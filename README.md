# Archivo Vivo — Banco de semillas ancestrales

Aplicación de escritorio en Python para administrar un catálogo de semillas nativas y visualizar un **árbol binario de búsqueda**. La interfaz está en español; los nombres de clases, métodos y variables del código están en inglés. No requiere instalar paquetes externos: utiliza únicamente la biblioteca estándar de Python y Tkinter.

## Caso de estudio

Un pequeño centro de conservación de semillas ancestrales necesita catalogar variedades agrícolas locales, identificar su región de origen y registrar su viabilidad. Cada muestra tiene un código de acceso único. El árbol binario organiza los registros por ese código, lo que permite buscar, insertar y eliminar muestras siguiendo comparaciones por clave. El catálogo también permite agrupar visualmente los registros por región.

## Funcionalidades

- Interfaz de escritorio en español con panel de métricas y visualización gráfica del árbol.
- Estructura `TreeNode` y árbol binario de búsqueda `SeedTree` implementados manualmente.
- Crear y actualizar muestras, eliminar registros y buscar por código.
- Recorridos inorden, preorden y postorden.
- Filtro de catálogo por región de origen.
- Indicadores de peso (cantidad de nodos), altura, nodos hoja y viabilidad promedio.
- Persistencia local en `data/seed_records.json`.
- Datos iniciales para probar el sistema desde el primer inicio.
- Pruebas automatizadas con `unittest`.

## Requisitos

- Python 3.10 o superior recomendado.
- Tkinter instalado. En Windows normalmente viene con Python.
- No requiere `pip install` ni conexión a internet.

## Ejecutar en Visual Studio Code

1. Descomprime el ZIP.
2. Abre la carpeta `ArchivoVivo_Arboles` en Visual Studio Code.
3. Abre **Terminal → Nueva terminal**.
4. Ejecuta:

   ```powershell
   python main.py
   ```

   Si Windows no reconoce `python`, prueba:

   ```powershell
   py main.py
   ```

5. La ventana **ARCHIVO VIVO | Banco de semillas** debe abrirse con registros de ejemplo.

## Ejecutar pruebas

En la terminal, desde la carpeta del proyecto:

```powershell
python -m unittest discover -s tests -v
```

También puedes usar `py -m unittest discover -s tests -v`.

## Publicar en GitHub desde la terminal

Crea primero un repositorio vacío en GitHub con el nombre `ArchivoVivo-Arboles` (sin README, licencia ni `.gitignore` inicial). Después, desde esta carpeta ejecuta, reemplazando la URL por la URL real de tu repositorio:

```powershell
git init
git add .
git commit -m "Initial commit: Archivo Vivo tree application"
git branch -M main
git remote add origin https://github.com/USUARIO/ArchivoVivo-Arboles.git
git push -u origin main
```

Si el repositorio ya existe y tiene un remoto configurado, consulta primero `git remote -v` para evitar duplicarlo.

## Cómo se usa el árbol

El campo **Código de acceso** es la clave del árbol. Si el código nuevo es menor que el código de un nodo, se explora la rama izquierda; si es mayor, la derecha. Los códigos duplicados se rechazan. El recorrido inorden muestra las claves de menor a mayor. La altura se cuenta en niveles, con árbol vacío de altura 0 y raíz en nivel 1.

## Estructura de archivos

```text
ArchivoVivo_Arboles/
├── main.py
├── README.md
├── data/
│   └── seed_records.json
└── tests/
    └── test_tree.py
```
