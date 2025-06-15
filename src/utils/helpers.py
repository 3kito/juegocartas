"""
Funciones de utilidad general
"""

import json
import datetime
import os


def cargar_json(ruta_archivo):
    """Carga un archivo JSON y retorna su contenido"""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {ruta_archivo}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON en {ruta_archivo}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado cargando {ruta_archivo}: {e}")
        return None


def guardar_json(datos, ruta_archivo):
    """Guarda datos en un archivo JSON"""
    try:
        # Crear directorio si no existe
        directorio = os.path.dirname(ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)

        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error guardando JSON en {ruta_archivo}: {e}")
        return False


def log_evento(mensaje, nivel="INFO"):
    """Registra un evento en consola y opcionalmente en archivo"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Formatear mensaje según nivel
    if nivel == "ERROR":
        prefijo = "❌"
    elif nivel == "WARNING":
        prefijo = "⚠️"
    elif nivel == "SUCCESS":
        prefijo = "✅"
    elif nivel == "DEBUG":
        prefijo = "🔍"
    else:  # INFO
        prefijo = "ℹ️"

    # Mensaje formateado
    mensaje_completo = f"[{timestamp}] {prefijo} {mensaje}"

    # Mostrar en consola
    print(mensaje_completo)

    # Opcionalmente guardar en archivo de log
    # (descomenta si quieres logs persistentes)
    # _guardar_log(mensaje_completo)


def _guardar_log(mensaje):
    """Guarda mensaje en archivo de log (función privada)"""
    try:
        fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        archivo_log = f"logs/game_{fecha_hoy}.log"

        # Crear directorio logs si no existe
        if not os.path.exists("logs"):
            os.makedirs("logs")

        with open(archivo_log, 'a', encoding='utf-8') as f:
            f.write(mensaje + "\n")
    except Exception:
        # Si no puede escribir logs, no es crítico
        pass


def formatear_tiempo(segundos):
    """Convierte segundos a formato legible"""
    if segundos < 60:
        return f"{segundos:.1f}s"
    elif segundos < 3600:
        minutos = segundos // 60
        segundos_restantes = segundos % 60
        return f"{int(minutos)}m {segundos_restantes:.1f}s"
    else:
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        return f"{int(horas)}h {int(minutos)}m"


def validar_rango(valor, minimo, maximo, nombre="valor"):
    """Valida que un valor esté en el rango especificado"""
    if not (minimo <= valor <= maximo):
        raise ValueError(f"{nombre} debe estar entre {minimo} y {maximo}, recibido: {valor}")
    return valor


def generar_id_unico():
    """Genera un ID único basado en timestamp"""
    import time
    return int(time.time() * 1000)  # Timestamp en milisegundos


def distancia_euclidiana(punto1, punto2):
    """Calcula distancia euclidiana entre dos puntos (x, y)"""
    import math
    return math.sqrt((punto1[0] - punto2[0]) ** 2 + (punto1[1] - punto2[1]) ** 2)


def porcentaje(parte, total):
    """Calcula porcentaje de forma segura"""
    if total == 0:
        return 0
    return (parte / total) * 100


def truncar_texto(texto, max_longitud=50):
    """Trunca texto si es muy largo"""
    if len(texto) <= max_longitud:
        return texto
    return texto[:max_longitud - 3] + "..."


# Constantes útiles
COLORES_CONSOLA = {
    'RESET': '\033[0m',
    'ROJO': '\033[91m',
    'VERDE': '\033[92m',
    'AMARILLO': '\033[93m',
    'AZUL': '\033[94m',
    'MAGENTA': '\033[95m',
    'CYAN': '\033[96m',
    'BLANCO': '\033[97m'
}


def colorear_texto(texto, color='BLANCO'):
    """Aplica color al texto en consola (si el terminal lo soporta)"""
    if color.upper() in COLORES_CONSOLA:
        return f"{COLORES_CONSOLA[color.upper()]}{texto}{COLORES_CONSOLA['RESET']}"
    return texto