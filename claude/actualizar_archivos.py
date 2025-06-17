import os
import shutil
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'archivos')
SCRIPT_PATH = os.path.relpath(os.path.abspath(__file__), ROOT_DIR)

EXCLUDE_DIRS = {'tests', 'deprec', 'claude', '.git', '__pycache__', '.pytest_cache', '.idea'}
EXCLUDE_FILES = {'__init__.py'}  # Archivos específicos a excluir


def limpiar_destino():
    """Elimina todo el contenido de la carpeta de destino."""
    if os.path.exists(ARCHIVOS_DIR):
        for nombre in os.listdir(ARCHIVOS_DIR):
            ruta = os.path.join(ARCHIVOS_DIR, nombre)
            if os.path.isdir(ruta):
                shutil.rmtree(ruta)
            else:
                os.remove(ruta)
    else:
        os.makedirs(ARCHIVOS_DIR, exist_ok=True)


def copiar_archivos():
    """Copia los archivos del proyecto aplicando los filtros.

    - Archivos ``.py`` y ``.json`` se copian siempre.
    - Archivos ``.txt`` solo se copian si provienen de la carpeta
      ``documentacion``.
    """
    for raiz, dirs, files in os.walk(ROOT_DIR):
        rel_raiz = os.path.relpath(raiz, ROOT_DIR)
        if rel_raiz == '.':
            primer = ''
        else:
            primer = rel_raiz.split(os.sep)[0]
        if primer in EXCLUDE_DIRS:
            dirs[:] = []
            continue
        # Filtrar subdirectorios excluidos
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for archivo in files:
            # Filtrar extensiones permitidas
            ext = os.path.splitext(archivo)[1]
            permitido = False

            if ext in {'.py', '.json'}:
                permitido = True
            elif ext == '.txt' and rel_raiz.startswith('documentacion'):
                permitido = True

            if not permitido or archivo in EXCLUDE_FILES:
                continue

            ruta_rel = os.path.normpath(os.path.join(rel_raiz, archivo))
            if ruta_rel == SCRIPT_PATH:
                continue

            origen = os.path.join(raiz, archivo)

            # CAMBIO: Todos los archivos van directo a la carpeta archivos/ sin subcarpetas
            destino = os.path.join(ARCHIVOS_DIR, archivo)

            # Si ya existe un archivo con el mismo nombre, renombrarlo
            contador = 1
            nombre_base, extension = os.path.splitext(archivo)
            while os.path.exists(destino):
                nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                destino = os.path.join(ARCHIVOS_DIR, nuevo_nombre)
                contador += 1

            shutil.copy2(origen, destino)
            print(f"Copiado: {ruta_rel} -> {os.path.basename(destino)}")


def generar_tree_python(directorio, archivo_salida, prefijo="", nivel=0, max_nivel=10):
    """Genera un árbol de directorios usando Python."""
    if not os.path.exists(directorio) or nivel > max_nivel:
        return

    elementos = []
    try:
        for elemento in os.listdir(directorio):
            # Saltar archivos/carpetas excluidos
            if elemento in EXCLUDE_DIRS or elemento.startswith('.'):
                continue

            ruta_completa = os.path.join(directorio, elemento)
            if os.path.isdir(ruta_completa):
                elementos.append((elemento, True, ruta_completa))
            else:
                # Solo mostrar archivos .py y algunos otros relevantes (no __init__.py)
                if (elemento.endswith('.py') and elemento not in EXCLUDE_FILES) or \
                        elemento.endswith(('.json', '.md', '.txt', '.gitignore', '.yml', '.yaml')):
                    elementos.append((elemento, False, ruta_completa))
    except PermissionError:
        return

    elementos.sort(key=lambda x: (not x[1], x[0]))  # Directorios primero, luego archivos

    for i, (nombre, es_directorio, ruta_completa) in enumerate(elementos):
        es_ultimo_elemento = i == len(elementos) - 1

        if es_ultimo_elemento:
            simbolo = "└── "
            nuevo_prefijo = prefijo + "    "
        else:
            simbolo = "├── "
            nuevo_prefijo = prefijo + "│   "

        archivo_salida.write(f"{prefijo}{simbolo}{nombre}\n")

        if es_directorio:
            generar_tree_python(ruta_completa, archivo_salida, nuevo_prefijo, nivel + 1, max_nivel)


def generar_tree():
    """Genera un archivo txt con la estructura del proyecto completo (excluyendo carpetas no deseadas)."""
    # CAMBIO: Guardar el archivo dentro de la carpeta archivos/
    salida = os.path.join(ARCHIVOS_DIR, 'arbol_archivos.txt')

    try:
        # Intentar usar tree de Windows si está disponible
        with open(salida, 'w', encoding='utf-8') as f:
            # Usar tree de Windows con exclusiones
            resultado = subprocess.run([
                'tree', '/F', ROOT_DIR,
                # No hay una forma fácil de excluir con tree de Windows
            ], stdout=f, stderr=subprocess.DEVNULL, check=False, cwd=ROOT_DIR)

        # Si tree funcionó, filtrar el archivo manualmente
        if os.path.exists(salida):
            with open(salida, 'r', encoding='utf-8') as f:
                lineas = f.readlines()

            # Filtrar líneas que contengan carpetas/archivos excluidos
            lineas_filtradas = []
            for linea in lineas:
                excluir_linea = False
                for excluido in EXCLUDE_DIRS:
                    if f"├───{excluido}" in linea or f"└───{excluido}" in linea or f"│   {excluido}" in linea:
                        excluir_linea = True
                        break
                if "__init__.py" in linea:
                    excluir_linea = True

                if not excluir_linea:
                    lineas_filtradas.append(linea)

            with open(salida, 'w', encoding='utf-8') as f:
                f.writelines(lineas_filtradas)

        print("Árbol generado usando tree de Windows (filtrado)")

    except (FileNotFoundError, subprocess.SubprocessError):
        # Si tree no está disponible, usar implementación en Python
        with open(salida, 'w', encoding='utf-8') as f:
            nombre_proyecto = os.path.basename(ROOT_DIR)
            f.write(f"{nombre_proyecto}/\n")
            generar_tree_python(ROOT_DIR, f)
        print("Árbol generado usando implementación Python")


def main():
    print("Iniciando actualización de archivos...")
    limpiar_destino()
    print("Destino limpiado.")

    copiar_archivos()
    print("Archivos copiados.")

    generar_tree()
    print("Árbol de archivos generado.")

    print(f"\nProceso completado.")
    print(f"Archivos Python disponibles en: {ARCHIVOS_DIR}")
    print(f"Estructura del proyecto en: {ARCHIVOS_DIR}/arbol_archivos.txt")


if __name__ == '__main__':
    main()
