"""
fetcher.py — El módulo que DESCARGA datos de las APIs externas.

¿Qué hace este archivo?
Se conecta a football-data.org y trae los partidos del Mundial 2026.
Por ahora solo los partidos (las cuotas vendrán de The Odds API más adelante).

Ideas clave que aplica:
  - Manejo de errores: las APIs fallan (sin internet, key vencida, límite excedido).
  - Caché: guarda la respuesta en disco para no repetir llamadas y gastar tu cuota.
  - Horas en Colombia: la API da horas en UTC; las pasamos a hora colombiana (COT).
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

import requests

# ─────────────────────────────────────────────────────────────
# IMPORTAR LA CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
# Como este archivo se ejecuta con "python data/fetcher.py", Python solo conoce
# la carpeta data/. Agregamos la raíz del proyecto al "camino de búsqueda"
# (sys.path) para poder importar config/settings.py sin problemas.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import settings  # noqa: E402  (se importa después de ajustar sys.path)


# ─────────────────────────────────────────────────────────────
# CONSTANTES DE ESTE MÓDULO
# ─────────────────────────────────────────────────────────────
# "WC" es el código del Mundial (World Cup) en football-data.org.
COMPETICION_MUNDIAL = "WC"

# Colombia está en UTC-5 (no usa horario de verano). Lo definimos una vez.
ZONA_COLOMBIA = timezone(timedelta(hours=-5))


# ─────────────────────────────────────────────────────────────
# FUNCIÓN AUXILIAR: hacer una petición a football-data.org
# ─────────────────────────────────────────────────────────────
def _pedir_a_football_data(endpoint, parametros=None):
    """
    Hace una petición GET a football-data.org y devuelve el JSON ya convertido
    a diccionario de Python. Si algo falla, devuelve None y explica el error.

    endpoint: la parte final de la URL, ej "competitions/WC/matches"
    parametros: diccionario opcional con filtros, ej {"dateFrom": "2026-06-16"}

    El guion bajo al inicio del nombre (_pedir...) es una convención en Python
    que significa "función interna, de uso solo dentro de este archivo".
    """
    # 1. Validar que tenemos la API key antes de intentar nada.
    if not settings.FOOTBALL_DATA_KEY:
        print("⚠️  No hay FOOTBALL_DATA_KEY configurada. Revisa tu archivo .env")
        return None

    url = f"{settings.FOOTBALL_DATA_URL}/{endpoint}"

    # football-data.org pide la key en un header (cabecera) llamado X-Auth-Token.
    headers = {"X-Auth-Token": settings.FOOTBALL_DATA_KEY}

    try:
        # timeout=15 -> si la API no responde en 15 segundos, no esperamos para siempre.
        respuesta = requests.get(url, headers=headers, params=parametros, timeout=15)

        # raise_for_status lanza un error si el código HTTP es 4xx o 5xx
        # (ej: 403 key inválida, 429 demasiadas peticiones, 500 error del servidor).
        respuesta.raise_for_status()

        return respuesta.json()

    except requests.exceptions.HTTPError as e:
        codigo = e.response.status_code if e.response is not None else "?"
        if codigo == 403:
            print("❌ Error 403: API key inválida o sin permiso para este recurso.")
        elif codigo == 429:
            print("❌ Error 429: superaste el límite de llamadas (10/min en el free tier).")
        else:
            print(f"❌ Error HTTP {codigo} al consultar football-data.org.")
        return None

    except requests.exceptions.ConnectionError:
        print("❌ Sin conexión a internet o el servidor no responde.")
        return None

    except requests.exceptions.Timeout:
        print("❌ La API tardó demasiado en responder (timeout).")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error inesperado al consultar la API: {e}")
        return None


# ─────────────────────────────────────────────────────────────
# CACHÉ: guardar y leer respuestas en disco
# ─────────────────────────────────────────────────────────────
def _ruta_cache(nombre):
    """Construye la ruta de un archivo de caché dentro de data/cache/."""
    settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)  # crea la carpeta si no existe
    return settings.CACHE_DIR / nombre


def _guardar_en_cache(nombre, datos):
    """Guarda un diccionario como archivo JSON en la caché."""
    ruta = _ruta_cache(nombre)
    with open(ruta, "w", encoding="utf-8") as archivo:
        # ensure_ascii=False -> conserva acentos y ñ; indent=2 -> legible para humanos.
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def _leer_de_cache(nombre):
    """Lee un JSON de la caché. Devuelve None si no existe."""
    ruta = _ruta_cache(nombre)
    if not ruta.exists():
        return None
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL: obtener los partidos de un día
# ─────────────────────────────────────────────────────────────
def obtener_partidos_del_dia(fecha=None, usar_cache=True):
    """
    Trae los partidos del Mundial 2026 de una fecha dada.

    fecha: texto "YYYY-MM-DD". Si es None, usa la fecha de HOY.
    usar_cache: si True, usa la respuesta guardada en disco si ya existe
                (ahorra llamadas a la API). Pon False para forzar datos frescos.

    Devuelve una lista de diccionarios "limpios", cada uno con los datos de un
    partido (equipos, hora en Colombia, estado). Lista vacía si no hay partidos.
    """
    # Si no nos dan fecha, usamos la de hoy en Colombia.
    if fecha is None:
        fecha = datetime.now(ZONA_COLOMBIA).strftime("%Y-%m-%d")

    nombre_cache = f"partidos_mundial_{fecha}.json"

    # 1. Intentar leer de la caché primero.
    datos = None
    if usar_cache:
        datos = _leer_de_cache(nombre_cache)
        if datos is not None:
            print(f"📁 Usando datos guardados en caché para {fecha}.")

    # 2. Si no había caché, llamar a la API.
    if datos is None:
        print(f"🌐 Consultando football-data.org para los partidos del {fecha}...")
        # La API filtra por rango de fechas. Para "un solo día" usamos
        # dateFrom = dateTo = la fecha pedida.
        parametros = {"dateFrom": fecha, "dateTo": fecha}
        datos = _pedir_a_football_data(
            f"competitions/{COMPETICION_MUNDIAL}/matches", parametros
        )

        if datos is None:
            # Hubo un error de red/API; ya se imprimió el motivo.
            return []

        # Guardamos en caché para la próxima vez.
        _guardar_en_cache(nombre_cache, datos)

    # 3. "Limpiar" los datos: la API devuelve mucha información; nos quedamos
    #    solo con lo que necesitamos, en un formato sencillo.
    partidos_limpios = []
    for partido in datos.get("matches", []):
        partidos_limpios.append(_limpiar_partido(partido))

    return partidos_limpios


def _limpiar_partido(partido):
    """
    Toma un partido crudo de la API y devuelve un diccionario sencillo
    con solo los campos que nos interesan.
    """
    # Los nombres de equipo a veces vienen como None si el partido es futuro
    # y aún no se conocen los rivales (ej: "Ganador grupo A"). Usamos "Por definir".
    local = partido.get("homeTeam", {}).get("name") or "Por definir"
    visitante = partido.get("awayTeam", {}).get("name") or "Por definir"

    # utcDate viene como "2026-06-16T18:00:00Z" (hora UTC). La convertimos a COT.
    hora_cot = _utc_a_hora_colombia(partido.get("utcDate"))

    return {
        "id": partido.get("id"),
        "local": local,
        "visitante": visitante,
        "hora_cot": hora_cot,
        "estado": partido.get("status"),  # SCHEDULED, FINISHED, IN_PLAY, etc.
    }


def _utc_a_hora_colombia(fecha_utc_texto):
    """
    Convierte una fecha UTC en texto (ej "2026-06-16T18:00:00Z") a la hora
    de Colombia en formato "HH:MM". Devuelve "??:??" si el dato falta o falla.
    """
    if not fecha_utc_texto:
        return "??:??"
    try:
        # Reemplazamos la "Z" final (que significa UTC) por "+00:00", formato
        # que Python entiende de forma nativa.
        momento_utc = datetime.fromisoformat(fecha_utc_texto.replace("Z", "+00:00"))
        momento_colombia = momento_utc.astimezone(ZONA_COLOMBIA)
        return momento_colombia.strftime("%H:%M")
    except (ValueError, AttributeError):
        return "??:??"


# ─────────────────────────────────────────────────────────────
# MOSTRAR LOS PARTIDOS EN CONSOLA
# ─────────────────────────────────────────────────────────────
def mostrar_partidos(fecha=None):
    """
    Obtiene los partidos del día y los imprime de forma legible en la terminal.
    Es la función que se ejecuta cuando corres este archivo directamente.
    """
    if fecha is None:
        fecha = datetime.now(ZONA_COLOMBIA).strftime("%Y-%m-%d")

    print("=" * 55)
    print(f"  PARTIDOS DEL MUNDIAL 2026 — {fecha}")
    print("=" * 55)

    partidos = obtener_partidos_del_dia(fecha)

    if not partidos:
        print("\nNo se encontraron partidos para esta fecha.")
        print("(Puede que no haya jornada hoy, o que el free tier no incluya")
        print(" el Mundial. Probaremos con otra fecha si hace falta.)")
        return

    print(f"\nPartidos encontrados hoy: {len(partidos)}\n")
    # Ordenamos por hora para que se lean de la mañana a la noche.
    # Como hora_cot es texto "HH:MM", ordenarlo alfabéticamente ya da el orden correcto.
    partidos = sorted(partidos, key=lambda p: p["hora_cot"])
    for p in partidos:
        # Ej:  18:00 COT  →  España vs Alemania   [SCHEDULED]
        print(f"  {p['hora_cot']} COT  →  {p['local']} vs {p['visitante']}   [{p['estado']}]")

    print("\n" + "=" * 55)


# Si ejecutas "python data/fetcher.py", se muestran los partidos de hoy.
if __name__ == "__main__":
    # Permite probar otra fecha así:  python data/fetcher.py 2026-06-20
    fecha_pedida = sys.argv[1] if len(sys.argv) > 1 else None
    mostrar_partidos(fecha_pedida)
