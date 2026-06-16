"""
almacen.py — Persistencia de los ratings ELO entre ejecuciones.

¿Qué problema resuelve?
El diccionario RATINGS de elo.py vive en memoria: se reinicia cada vez que
corres el programa. Para que el modelo MEJORE partido a partido durante el
Mundial, los ELOs actualizados tienen que GUARDARSE en disco y volver a
CARGARSE la próxima vez. Eso hace este módulo.

¿Por qué un módulo aparte (y no guardar dentro de elo.py)?
Para esconder el "cómo se guarda" detrás de dos funciones: cargar_ratings() y
guardar_ratings(). Hoy por debajo hay un archivo JSON; si en el futuro (Fase 3/4)
necesitamos SQLite para backtesting o muchas ligas, cambiamos SOLO este módulo
y el resto del proyecto ni se entera.

Formato del archivo (data/ratings_elo.json), con 3 secciones:
    meta      -> info del archivo (cuándo se actualizó, versión inicial)
    ratings   -> { selección: ELO actual }
    historial -> lista de partidos registrados (para auditar y backtesting)

Nota: este archivo SÍ va a Git (a diferencia de data/cache/). Así el historial
de commits muestra cómo evolucionan los ratings durante el Mundial.
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Importamos el modelo ELO para los ratings iniciales y la actualización.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from config import settings  # noqa: E402  (UTF-8 + rutas del proyecto)
from modelos import elo      # noqa: E402


# ─────────────────────────────────────────────────────────────
# RUTA DEL ARCHIVO Y CONSTANTES
# ─────────────────────────────────────────────────────────────
# El archivo vive en data/ratings_elo.json (NO en cache, porque sí se versiona).
RUTA_RATINGS = settings.DATA_DIR / "ratings_elo.json"

# Etiqueta de la versión inicial de los ratings: de dónde salieron los ELOs base.
VERSION_INICIAL = "posicion_fifa_11jun2026"

# Colombia (UTC-5) para poner fechas legibles en el archivo.
ZONA_COLOMBIA = timezone(timedelta(hours=-5))


def _hoy():
    """Devuelve la fecha de hoy en Colombia como texto 'YYYY-MM-DD'."""
    return datetime.now(ZONA_COLOMBIA).strftime("%Y-%m-%d")


# ─────────────────────────────────────────────────────────────
# INICIALIZAR: construir el estado base con los 48 ELOs de elo.py
# ─────────────────────────────────────────────────────────────
def inicializar_ratings():
    """
    Crea el diccionario base con los 48 ELOs iniciales del modelo, sin partidos
    registrados todavía. NO lo guarda en disco (de eso se encarga guardar_ratings).

    Los ELOs se redondean a 2 decimales para que el archivo sea legible y los
    diffs de Git muestren cambios claros.
    """
    ratings = {equipo: round(valor, 2) for equipo, valor in elo.RATINGS.items()}
    return {
        "meta": {
            "actualizado": _hoy(),
            "version_inicial": VERSION_INICIAL,
            "n_partidos_registrados": 0,
            "descripcion": "Ratings ELO del Mundial 2026. Se actualizan tras cada partido.",
        },
        "ratings": ratings,
        "historial": [],
    }


# ─────────────────────────────────────────────────────────────
# GUARDAR: escritura SEGURA (archivo temporal + rename atómico)
# ─────────────────────────────────────────────────────────────
def guardar_ratings(datos):
    """
    Guarda el diccionario de ratings en disco de forma SEGURA.

    ¿Por qué "archivo temporal + rename" y no escribir directo?
    Si el programa se interrumpe a la mitad de escribir el archivo final, el
    archivo quedaría corrupto (a medias) y perderías todos los ratings. En vez
    de eso:
        1) Escribimos en un archivo temporal (ratings_elo.json.tmp).
        2) Cuando terminó BIEN, renombramos el temporal sobre el final.
    El rename (os.replace) es atómico: o pasa completo, o no pasa. Así el archivo
    real nunca queda a medias.
    """
    # Aseguramos que la carpeta data/ exista.
    RUTA_RATINGS.parent.mkdir(parents=True, exist_ok=True)

    ruta_temporal = RUTA_RATINGS.with_suffix(".json.tmp")
    with open(ruta_temporal, "w", encoding="utf-8") as archivo:
        # ensure_ascii=False -> conserva acentos y ñ; indent=2 -> legible y con
        # buenos diffs en Git. sort_keys en ratings lo hacemos aparte si hace falta.
        json.dump(datos, archivo, ensure_ascii=False, indent=2)

    # Reemplazo atómico: el archivo final nunca queda a medio escribir.
    os.replace(ruta_temporal, RUTA_RATINGS)


# ─────────────────────────────────────────────────────────────
# CARGAR: leer del disco (y crear el archivo la primera vez)
# ─────────────────────────────────────────────────────────────
def cargar_ratings():
    """
    Carga el diccionario de ratings desde disco.

    Si el archivo no existe (primera vez), lo crea con los 48 ELOs base y lo
    guarda, para que siempre haya algo con qué trabajar.
    """
    if not RUTA_RATINGS.exists():
        print("📄 No existía data/ratings_elo.json. Creándolo con los 48 ELOs base...")
        datos = inicializar_ratings()
        guardar_ratings(datos)
        return datos

    with open(RUTA_RATINGS, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


# ─────────────────────────────────────────────────────────────
# CONSULTAR un rating actual
# ─────────────────────────────────────────────────────────────
def obtener_elo_actual(equipo, datos=None):
    """
    Devuelve el ELO ACTUAL (persistido) de una selección, que puede diferir del
    inicial si ya jugó partidos. Acepta nombres en español o inglés.

    datos: si ya cargaste el estado, pásalo para no leer el disco otra vez.
    """
    if datos is None:
        datos = cargar_ratings()
    clave = elo.nombre_canonico(equipo)
    if clave not in datos["ratings"]:
        raise ValueError(f"No hay rating guardado para '{equipo}' (canónico: '{clave}').")
    return datos["ratings"][clave]


# ─────────────────────────────────────────────────────────────
# REGISTRAR un partido: actualiza ratings + guarda historial
# ─────────────────────────────────────────────────────────────
def registrar_resultado(local, visitante, goles_local, goles_visitante,
                        tipo_partido, datos=None, guardar=True):
    """
    Registra el resultado de un partido real: actualiza los ELOs de ambos
    equipos y deja constancia en el historial.

    tipo_partido: OBLIGATORIO a propósito (sin valor por defecto). Esto evita el
    riesgo que anotamos en el punto 4 de la auditoría: que un partido se trate
    como "mundial" (K=60) por accidente. Quien registra DEBE decir qué tipo es.
    Valores válidos: "mundial", "clasificatoria", "amistoso".

    datos: estado ya cargado (opcional, para no releer disco).
    guardar: si True, persiste el cambio en disco al terminar.

    Devuelve el estado actualizado (dict).
    """
    if tipo_partido not in elo.K_FACTOR:
        raise ValueError(
            f"tipo_partido '{tipo_partido}' inválido. "
            f"Usa uno de: {list(elo.K_FACTOR.keys())}."
        )

    if datos is None:
        datos = cargar_ratings()

    local = elo.nombre_canonico(local)
    visitante = elo.nombre_canonico(visitante)

    elo_local_antes = datos["ratings"][local]
    elo_visitante_antes = datos["ratings"][visitante]

    # Calculamos los nuevos ratings usando el modelo (no duplicamos la fórmula).
    elo_local_despues, elo_visitante_despues = elo.actualizar_elo(
        elo_local_antes, elo_visitante_antes,
        goles_local, goles_visitante, tipo_partido=tipo_partido
    )

    # Guardamos los nuevos ratings (redondeados para legibilidad del archivo).
    datos["ratings"][local] = round(elo_local_despues, 2)
    datos["ratings"][visitante] = round(elo_visitante_despues, 2)

    # Dejamos constancia en el historial (sirve para auditar y para backtesting).
    datos["historial"].append({
        "fecha": _hoy(),
        "local": local,
        "visitante": visitante,
        "goles": [goles_local, goles_visitante],
        "tipo": tipo_partido,
        "elo_antes": [round(elo_local_antes, 2), round(elo_visitante_antes, 2)],
        "elo_despues": [round(elo_local_despues, 2), round(elo_visitante_despues, 2)],
    })

    # Actualizamos la metadata.
    datos["meta"]["actualizado"] = _hoy()
    datos["meta"]["n_partidos_registrados"] = len(datos["historial"])

    if guardar:
        guardar_ratings(datos)

    return datos


# ─────────────────────────────────────────────────────────────
# RESUMEN EN CONSOLA
# ─────────────────────────────────────────────────────────────
def mostrar_resumen():
    """Carga el estado y muestra un resumen legible del archivo de ratings."""
    datos = cargar_ratings()
    meta = datos["meta"]

    print("=" * 56)
    print("  ALMACÉN DE RATINGS ELO — MUNDIAL 2026")
    print("=" * 56)
    print(f"  Archivo: {RUTA_RATINGS}")
    print(f"  Actualizado: {meta['actualizado']}")
    print(f"  Versión inicial: {meta['version_inicial']}")
    print(f"  Selecciones guardadas: {len(datos['ratings'])}")
    print(f"  Partidos registrados: {meta['n_partidos_registrados']}")
    print("\n  Top 5 por ELO actual:")
    # Ordenamos por ELO de mayor a menor y mostramos los 5 primeros.
    top = sorted(datos["ratings"].items(), key=lambda par: par[1], reverse=True)[:5]
    for i, (equipo, valor) in enumerate(top, start=1):
        print(f"    {i}. {equipo:<16} {valor:.0f}")
    print("=" * 56)


# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Ejecutar "python modelos/almacen.py" crea el archivo si no existe y
    # muestra un resumen. No registra partidos (eso lo hará el fetcher después).
    mostrar_resumen()
