"""Archivo Vivo: an educational seed-bank catalog powered by a binary search tree."""
from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Iterable

APP_TITLE = "ARCHIVO VIVO | Banco de semillas"
DATA_FILE = Path(__file__).resolve().parent / "data" / "seed_records.json"


@dataclass
class SeedRecord:
    accession: int
    species: str
    region: str
    status: str
    viability: int
    notes: str = ""


class TreeNode:
    """A node in the binary search tree; keyed by accession number."""
    def __init__(self, record: SeedRecord):
        self.record = record
        self.left: Optional[TreeNode] = None
        self.right: Optional[TreeNode] = None


class SeedTree:
    """Binary search tree supporting insertion, lookup, deletion and traversals."""
    def __init__(self):
        self.root: Optional[TreeNode] = None
        self.size = 0

    def insert(self, record: SeedRecord) -> bool:
        if self.root is None:
            self.root = TreeNode(record)
            self.size = 1
            return True
        current = self.root
        while True:
            if record.accession == current.record.accession:
                return False
            if record.accession < current.record.accession:
                if current.left is None:
                    current.left = TreeNode(record)
                    self.size += 1
                    return True
                current = current.left
            else:
                if current.right is None:
                    current.right = TreeNode(record)
                    self.size += 1
                    return True
                current = current.right

    def find_node(self, accession: int) -> Optional[TreeNode]:
        current = self.root
        while current is not None:
            if accession == current.record.accession:
                return current
            current = current.left if accession < current.record.accession else current.right
        return None

    def search(self, accession: int) -> Optional[SeedRecord]:
        node = self.find_node(accession)
        return node.record if node else None

    def delete(self, accession: int) -> bool:
        found = self.search(accession)
        if found is None:
            return False
        self.root = self._delete_node(self.root, accession)
        self.size -= 1
        return True

    def _delete_node(self, node: Optional[TreeNode], accession: int) -> Optional[TreeNode]:
        if node is None:
            return None
        if accession < node.record.accession:
            node.left = self._delete_node(node.left, accession)
        elif accession > node.record.accession:
            node.right = self._delete_node(node.right, accession)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = node.right
            while successor.left is not None:
                successor = successor.left
            node.record = successor.record
            node.right = self._delete_node(node.right, successor.record.accession)
        return node

    def traverse(self, order: str = "inorder") -> list[SeedRecord]:
        result: list[SeedRecord] = []
        def visit(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            if order == "preorder":
                result.append(node.record)
            visit(node.left)
            if order == "inorder":
                result.append(node.record)
            visit(node.right)
            if order == "postorder":
                result.append(node.record)
        visit(self.root)
        return result

    def height(self) -> int:
        def measure(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            return 1 + max(measure(node.left), measure(node.right))
        return measure(self.root)

    def leaves(self) -> int:
        def count(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            if node.left is None and node.right is None:
                return 1
            return count(node.left) + count(node.right)
        return count(self.root)

    def load_records(self, records: Iterable[SeedRecord]) -> None:
        self.root = None
        self.size = 0
        for record in records:
            self.insert(record)


SAMPLE_RECORDS = [
    SeedRecord(410, "Quinua negra", "Altiplano", "En observación", 82, "Variedad resistente al frío."),
    SeedRecord(230, "Maíz capio", "Andes", "Prioritaria", 91, "Semilla tradicional de altura."),
    SeedRecord(610, "Fríjol cacha", "Andes", "Estable", 96, "Buena adaptación a suelos volcánicos."),
    SeedRecord(150, "Papa criolla silvestre", "Páramo", "Prioritaria", 73, "Requiere nueva prueba de germinación."),
    SeedRecord(320, "Amaranto rojo", "Altiplano", "Estable", 88, "Registro recuperado de una huerta comunitaria."),
    SeedRecord(520, "Chachafruto", "Bosque andino", "En observación", 67, "Especie útil para sistemas agroforestales."),
    SeedRecord(720, "Lulo de monte", "Bosque andino", "Prioritaria", 79, "Muestra recolectada en zona de transición."),
]


class ArchivoVivoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1280x820")
        self.minsize(1080, 720)
        self.configure(bg="#101923")
        self.tree = SeedTree()
        self.selected_accession: Optional[int] = None
        self._configure_styles()
        self._load_data()
        self._build_layout()
        self.refresh_all()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background="#182633", foreground="#e8f1f2", fieldbackground="#182633", rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", background="#263b49", foreground="#d8f5e8", font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#237b70")], foreground=[("selected", "#ffffff")])
        style.configure("TCombobox", fieldbackground="#182633", background="#263b49", foreground="#ffffff")

    def _load_data(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        records = []
        if DATA_FILE.exists():
            try:
                records = [SeedRecord(**item) for item in json.loads(DATA_FILE.read_text(encoding="utf-8"))]
            except (OSError, ValueError, TypeError):
                records = []
        if not records:
            records = SAMPLE_RECORDS[:]
            self._save_records(records)
        self.tree.load_records(records)

    def _save_records(self, records: Optional[list[SeedRecord]] = None):
        payload = [asdict(record) for record in (records if records is not None else self.tree.traverse())]
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _panel(self, parent, title: str, subtitle: str = "") -> tk.Frame:
        frame = tk.Frame(parent, bg="#182633", highlightbackground="#2b414e", highlightthickness=1)
        heading = tk.Frame(frame, bg="#182633")
        heading.pack(fill="x", padx=18, pady=(15, 8))
        tk.Label(heading, text=title, bg="#182633", fg="#e9fff5", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(heading, text=subtitle, bg="#182633", fg="#91a9b5", font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))
        return frame

    def _button(self, parent, text, command, primary=False):
        color = "#3bd6a2" if primary else "#263b49"
        fg = "#09221d" if primary else "#dce9ed"
        button = tk.Button(parent, text=text, command=command, bg=color, fg=fg, activebackground="#66e8bd", activeforeground="#09221d", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 9, "bold"), padx=13, pady=9)
        return button

    def _build_layout(self):
        header = tk.Frame(self, bg="#101923")
        header.pack(fill="x", padx=26, pady=(20, 14))
        tk.Label(header, text="◈  ARCHIVO VIVO", bg="#101923", fg="#3bd6a2", font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(header, text="BANCO DE SEMILLAS ANCESTRALES  /  LABORATORIO DE CONSERVACIÓN", bg="#101923", fg="#91a9b5", font=("Segoe UI", 9, "bold")).pack(side="left", padx=18, pady=(9, 0))
        self.status_label = tk.Label(header, text="● SISTEMA LOCAL", bg="#101923", fg="#3bd6a2", font=("Segoe UI", 9, "bold"))
        self.status_label.pack(side="right", pady=(8, 0))

        stats = tk.Frame(self, bg="#101923")
        stats.pack(fill="x", padx=26, pady=(0, 14))
        self.stat_values = {}
        for key, label in [("total", "MUESTRAS REGISTRADAS"), ("height", "ALTURA DEL ÁRBOL"), ("leaves", "NODOS HOJA"), ("viability", "VIABILIDAD PROMEDIO")]:
            card = tk.Frame(stats, bg="#182633", highlightbackground="#2b414e", highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            tk.Label(card, text=label, bg="#182633", fg="#91a9b5", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(12, 3))
            value = tk.Label(card, text="—", bg="#182633", fg="#3bd6a2", font=("Segoe UI", 22, "bold"))
            value.pack(anchor="w", padx=15, pady=(0, 12))
            self.stat_values[key] = value

        content = tk.Frame(self, bg="#101923")
        content.pack(fill="both", expand=True, padx=26, pady=(0, 22))
        left = tk.Frame(content, bg="#101923", width=355)
        left.pack(side="left", fill="y", padx=(0, 14))
        left.pack_propagate(False)
        form = self._panel(left, "Ficha de conservación", "Crea, actualiza o retira una muestra del catálogo.")
        form.pack(fill="x", pady=(0, 14))
        self.form_vars = {name: tk.StringVar() for name in ("accession", "species", "region", "status", "viability", "notes")}
        fields = [("accession", "Código de acceso"), ("species", "Especie / variedad"), ("region", "Región de origen"), ("viability", "Viabilidad (%)")]
        for name, label in fields:
            row = tk.Frame(form, bg="#182633")
            row.pack(fill="x", padx=18, pady=5)
            tk.Label(row, text=label, bg="#182633", fg="#b9cbd1", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
            entry = tk.Entry(row, textvariable=self.form_vars[name], bg="#101923", fg="#f0f7f7", insertbackground="#3bd6a2", relief="flat", font=("Segoe UI", 10))
            entry.pack(fill="x", ipady=7)
        row = tk.Frame(form, bg="#182633")
        row.pack(fill="x", padx=18, pady=5)
        tk.Label(row, text="Estado de conservación", bg="#182633", fg="#b9cbd1", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        status_box = ttk.Combobox(row, textvariable=self.form_vars["status"], values=["Estable", "En observación", "Prioritaria", "Crítica"], state="readonly")
        status_box.pack(fill="x", ipady=4)
        row = tk.Frame(form, bg="#182633")
        row.pack(fill="x", padx=18, pady=5)
        tk.Label(row, text="Notas de campo", bg="#182633", fg="#b9cbd1", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        tk.Entry(row, textvariable=self.form_vars["notes"], bg="#101923", fg="#f0f7f7", insertbackground="#3bd6a2", relief="flat", font=("Segoe UI", 10)).pack(fill="x", ipady=7)
        buttons = tk.Frame(form, bg="#182633")
        buttons.pack(fill="x", padx=18, pady=(12, 18))
        self._button(buttons, "＋ Guardar muestra", self.save_record, True).pack(fill="x", pady=(0, 7))
        actions = tk.Frame(buttons, bg="#182633")
        actions.pack(fill="x")
        self._button(actions, "Limpiar", self.clear_form).pack(side="left", fill="x", expand=True, padx=(0, 5))
        self._button(actions, "Eliminar", self.delete_selected).pack(side="left", fill="x", expand=True, padx=(5, 0))

        tools = self._panel(left, "Explorador del árbol", "Recorridos clásicos de una estructura binaria.")
        tools.pack(fill="x")
        self._button(tools, "Inorden · ordenar por código", lambda: self.apply_traversal("inorder"), True).pack(fill="x", padx=18, pady=(3, 6))
        self._button(tools, "Preorden · raíz primero", lambda: self.apply_traversal("preorder")).pack(fill="x", padx=18, pady=3)
        self._button(tools, "Postorden · raíz al final", lambda: self.apply_traversal("postorder")).pack(fill="x", padx=18, pady=3)
        tk.Label(tools, text="Buscar por código", bg="#182633", fg="#b9cbd1", font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(12, 4))
        search_row = tk.Frame(tools, bg="#182633")
        search_row.pack(fill="x", padx=18, pady=(0, 18))
        self.search_var = tk.StringVar()
        tk.Entry(search_row, textvariable=self.search_var, bg="#101923", fg="#f0f7f7", insertbackground="#3bd6a2", relief="flat").pack(side="left", fill="x", expand=True, ipady=8)
        self._button(search_row, "Buscar", self.search_record, True).pack(side="left", padx=(7, 0))

        right = tk.Frame(content, bg="#101923")
        right.pack(side="left", fill="both", expand=True)
        tree_panel = self._panel(right, "Mapa de nodos", "Cada nodo representa una muestra; las ramas reflejan el orden por código de acceso.")
        tree_panel.pack(fill="both", expand=True, pady=(0, 14))
        self.tree_canvas = tk.Canvas(tree_panel, bg="#111e28", highlightthickness=0, height=280)
        self.tree_canvas.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        list_panel = self._panel(right, "Catálogo de muestras", "Selecciona una fila para cargar sus datos en la ficha.")
        list_panel.pack(fill="both", expand=True)
        filter_row = tk.Frame(list_panel, bg="#182633")
        filter_row.pack(fill="x", padx=18, pady=(0, 8))
        tk.Label(filter_row, text="Filtrar por región:", bg="#182633", fg="#b9cbd1", font=("Segoe UI", 9)).pack(side="left")
        self.region_filter = tk.StringVar(value="Todas")
        self.region_box = ttk.Combobox(filter_row, textvariable=self.region_filter, state="readonly", width=22)
        self.region_box.pack(side="left", padx=8)
        self.region_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_table())
        self._button(filter_row, "Exportar JSON", self.export_data).pack(side="right")
        columns = ("accession", "species", "region", "status", "viability")
        self.table = ttk.Treeview(list_panel, columns=columns, show="headings", selectmode="browse")
        labels = {"accession": "Código", "species": "Especie / variedad", "region": "Región", "status": "Estado", "viability": "Viabilidad"}
        widths = {"accession": 80, "species": 210, "region": 130, "status": 140, "viability": 90}
        for col in columns:
            self.table.heading(col, text=labels[col])
            self.table.column(col, width=widths[col], anchor="w")
        self.table.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        self.table.bind("<<TreeviewSelect>>", self.on_table_select)
        footer = tk.Label(self, text="ESTRUCTURAS DE DATOS  •  ÁRBOLES BINARIOS DE BÚSQUEDA  •  DATOS LOCALES EN JSON", bg="#101923", fg="#58717e", font=("Segoe UI", 8, "bold"))
        footer.pack(side="bottom", pady=(0, 8))
        self.tree_canvas.bind("<Configure>", lambda _event: self.draw_tree())

    def save_record(self):
        try:
            accession = int(self.form_vars["accession"].get().strip())
            viability = int(self.form_vars["viability"].get().strip())
        except ValueError:
            messagebox.showerror("Datos inválidos", "El código y la viabilidad deben ser números enteros.")
            return
        species = self.form_vars["species"].get().strip()
        region = self.form_vars["region"].get().strip()
        status = self.form_vars["status"].get().strip()
        notes = self.form_vars["notes"].get().strip()
        if accession <= 0 or not species or not region or not status:
            messagebox.showwarning("Faltan datos", "Completa el código, especie, región y estado de conservación.")
            return
        if not 0 <= viability <= 100:
            messagebox.showwarning("Viabilidad inválida", "La viabilidad debe estar entre 0 y 100.")
            return
        existing = self.tree.search(accession)
        record = SeedRecord(accession, species, region, status, viability, notes)
        if existing and self.selected_accession != accession:
            messagebox.showerror("Código duplicado", "Ya existe una muestra con ese código de acceso.")
            return
        if self.selected_accession is not None and self.selected_accession != accession:
            self.tree.delete(self.selected_accession)
        if existing and self.selected_accession == accession:
            self.tree.delete(accession)
        if not self.tree.insert(record):
            messagebox.showerror("No se pudo guardar", "No fue posible insertar la muestra en el árbol.")
            return
        self._save_records()
        self.clear_form()
        self.refresh_all()
        self.status_label.config(text="● CAMBIOS GUARDADOS", fg="#3bd6a2")

    def delete_selected(self):
        accession = self.selected_accession
        if accession is None:
            try:
                accession = int(self.form_vars["accession"].get().strip())
            except ValueError:
                accession = None
        if accession is None or self.tree.search(accession) is None:
            messagebox.showinfo("Sin selección", "Selecciona una muestra de la tabla o escribe un código existente.")
            return
        if messagebox.askyesno("Confirmar eliminación", f"¿Retirar la muestra {accession} del catálogo?"):
            self.tree.delete(accession)
            self._save_records()
            self.clear_form()
            self.refresh_all()

    def search_record(self):
        try:
            accession = int(self.search_var.get().strip())
        except ValueError:
            messagebox.showwarning("Búsqueda", "Escribe un código numérico de acceso.")
            return
        record = self.tree.search(accession)
        if record is None:
            messagebox.showinfo("Sin resultados", f"No se encontró una muestra con el código {accession}.")
            return
        self.fill_form(record)
        self.region_filter.set("Todas")
        self.refresh_table()
        for item in self.table.get_children():
            if int(self.table.item(item, "values")[0]) == accession:
                self.table.selection_set(item)
                self.table.see(item)
                break

    def fill_form(self, record: SeedRecord):
        self.selected_accession = record.accession
        for key, value in asdict(record).items():
            self.form_vars[key].set(str(value))

    def clear_form(self):
        self.selected_accession = None
        for variable in self.form_vars.values():
            variable.set("")
        self.form_vars["status"].set("Estable")
        self.table.selection_remove(self.table.selection())

    def on_table_select(self, _event=None):
        selection = self.table.selection()
        if not selection:
            return
        values = self.table.item(selection[0], "values")
        record = self.tree.search(int(values[0]))
        if record:
            self.fill_form(record)

    def apply_traversal(self, order: str):
        records = self.tree.traverse(order)
        names = {"inorder": "Inorden", "preorder": "Preorden", "postorder": "Postorden"}
        messagebox.showinfo(f"Recorrido {names[order]}", " → ".join(str(record.accession) for record in records) if records else "El árbol está vacío.")
        self.refresh_table(records)

    def refresh_all(self):
        records = self.tree.traverse("inorder")
        self.stat_values["total"].config(text=str(self.tree.size))
        self.stat_values["height"].config(text=str(self.tree.height()))
        self.stat_values["leaves"].config(text=str(self.tree.leaves()))
        average = round(sum(record.viability for record in records) / len(records)) if records else 0
        self.stat_values["viability"].config(text=f"{average}%")
        regions = ["Todas"] + sorted({record.region for record in records})
        self.region_box["values"] = regions
        if self.region_filter.get() not in regions:
            self.region_filter.set("Todas")
        self.refresh_table()
        self.draw_tree()

    def refresh_table(self, records: Optional[list[SeedRecord]] = None):
        for item in self.table.get_children():
            self.table.delete(item)
        source = records if records is not None else self.tree.traverse("inorder")
        selected_region = self.region_filter.get()
        for record in source:
            if selected_region != "Todas" and record.region != selected_region:
                continue
            self.table.insert("", "end", values=(record.accession, record.species, record.region, record.status, f"{record.viability}%"))

    def draw_tree(self):
        canvas = self.tree_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 400)
        height = max(canvas.winfo_height(), 220)
        if self.tree.root is None:
            canvas.create_text(width / 2, height / 2, text="El árbol está vacío\nAgrega una muestra para comenzar", fill="#91a9b5", font=("Segoe UI", 12), justify="center")
            return
        positions = {}
        def assign(node: Optional[TreeNode], depth: int, low: float, high: float):
            if node is None:
                return
            x = (low + high) / 2
            y = 35 + depth * max(62, (height - 70) / max(self.tree.height(), 1))
            positions[node.record.accession] = (x, y, node)
            assign(node.left, depth + 1, low, x)
            assign(node.right, depth + 1, x, high)
        assign(self.tree.root, 0, 35, width - 35)
        for accession, (x, y, node) in positions.items():
            for child in (node.left, node.right):
                if child and child.record.accession in positions:
                    cx, cy, _ = positions[child.record.accession]
                    canvas.create_line(x, y + 17, cx, cy - 17, fill="#456575", width=2)
        for accession, (x, y, node) in positions.items():
            canvas.create_oval(x - 27, y - 18, x + 27, y + 18, fill="#1f6e61", outline="#3bd6a2", width=2)
            canvas.create_text(x, y, text=str(accession), fill="#ffffff", font=("Segoe UI", 9, "bold"))
            canvas.create_text(x, y + 28, text=node.record.species[:16], fill="#b9cbd1", font=("Segoe UI", 8))

    def export_data(self):
        try:
            self._save_records()
            messagebox.showinfo("Exportación lista", f"Catálogo guardado en:\n{DATA_FILE}")
        except OSError as error:
            messagebox.showerror("Error de exportación", f"No se pudo guardar el catálogo.\n{error}")


if __name__ == "__main__":
    app = ArchivoVivoApp()
    app.mainloop()
