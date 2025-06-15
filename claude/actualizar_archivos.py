import os
import shutil
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'archivos')
SCRIPT_PATH = os.path.relpath(os.path.abspath(__file__), ROOT_DIR)

EXCLUDE_DIRS = {'tests', 'deprec', 'claude', '.git', '__pycache__'}


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
    """Copia los archivos .py del proyecto aplicando los filtros."""
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
            if not archivo.endswith('.py'):
                continue
            ruta_rel = os.path.normpath(os.path.join(rel_raiz, archivo))
            if ruta_rel == SCRIPT_PATH:
                continue
            origen = os.path.join(raiz, archivo)
            destino = os.path.join(ARCHIVOS_DIR, ruta_rel)
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            shutil.copy2(origen, destino)


def generar_tree():
    """Genera un archivo txt con la estructura de la carpeta de destino."""
    salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arbol_archivos.txt')
    with open(salida, 'w', encoding='utf-8') as f:
        subprocess.run(['tree', '-f', 'archivos'], cwd=os.path.dirname(os.path.abspath(__file__)), stdout=f, check=False)


def main():
    limpiar_destino()
    copiar_archivos()
    generar_tree()


if __name__ == '__main__':
    main()
