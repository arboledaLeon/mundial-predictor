"""
settings.py — Configuración global del proyecto Mundial Predictor.

¿Qué hace este archivo?
Lee las "variables de entorno" (las API keys secretas) desde el archivo .env
y las deja disponibles para todo el proyecto.

¿Por qué hacerlo así y no escribir las keys directamente en el código?
Porque si subes el código a GitHub, las keys quedarían expuestas y cualquiera
podría usarlas (y gastarte tu cuota gratuita o cobrarte). El archivo .env NUNCA
se sube a Git (está en .gitignore), así que tus secretos quedan solo en tu PC.
"""

import os                          # Para leer variables de entorno y rutas
import sys                         # Para ajustar la codificación de la salida
from pathlib import Path           # Para construir rutas de archivos sin errores
from dotenv import load_dotenv     # Librería que lee el archivo .env

# ─────────────────────────────────────────────────────────────
# 0. CODIFICACIÓN UTF-8 EN LA CONSOLA (importante en Windows)
# ─────────────────────────────────────────────────────────────
# La consola de Windows usa "cp1252" por defecto y NO puede mostrar emojis
# (✅, ⚽, 📊) ni acentos en algunos casos, lo que rompe el programa.
# Forzamos UTF-8 en la salida para que los reportes con colores y emojis
# funcionen siempre. try/except por si la salida no admite reconfigurar.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ─────────────────────────────────────────────────────────────
# 1. RUTAS DEL PROYECTO
# ─────────────────────────────────────────────────────────────
# BASE_DIR = la carpeta raíz del proyecto (donde están CLAUDE.md, README.md...).
# __file__ es la ruta de ESTE archivo (config/settings.py).
# .parent.parent sube dos niveles: de settings.py -> config/ -> raíz del proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent

# Rutas útiles que otros módulos pueden importar en vez de escribirlas a mano.
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
HISTORICO_DIR = DATA_DIR / "historico"

# ─────────────────────────────────────────────────────────────
# 2. CARGAR EL ARCHIVO .env
# ─────────────────────────────────────────────────────────────
# El .env está en la RAÍZ del proyecto (junto a CLAUDE.md), no dentro de config/.
# load_dotenv lee ese archivo y carga sus variables a la memoria para poder
# leerlas con os.getenv(). Si el archivo no existe, no falla: solo no carga nada.
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# ─────────────────────────────────────────────────────────────
# 3. LEER LAS API KEYS
# ─────────────────────────────────────────────────────────────
# os.getenv("NOMBRE") devuelve el valor de la variable, o None si no existe.
FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

# ─────────────────────────────────────────────────────────────
# 4. URLs BASE DE LAS APIs
# ─────────────────────────────────────────────────────────────
# Las dejamos aquí centralizadas para no repetirlas en cada archivo.
FOOTBALL_DATA_URL = "https://api.football-data.org/v4"
ODDS_API_URL = "https://api.the-odds-api.com/v4"

# ─────────────────────────────────────────────────────────────
# 5. PARÁMETROS DEL SISTEMA DE VALUE BETTING
# ─────────────────────────────────────────────────────────────
# Centralizados aquí para ajustarlos fácil sin tocar la lógica de los modelos.
EDGE_MINIMO = 0.03          # 3% de ventaja mínima sobre la casa para considerar un pick
CONFIANZA_MINIMA = 0.55     # El modelo debe dar al menos 55% de probabilidad
KELLY_FRACCION = 0.25       # Usar solo 25% del Kelly completo (más conservador/seguro)


def verificar_configuracion():
    """
    Revisa que las API keys estén cargadas y avisa cuáles faltan.

    Devuelve True si ambas keys están presentes, False si falta alguna.
    Sirve para que el fetcher avise con claridad en vez de fallar con un
    error confuso a mitad de una llamada a la API.
    """
    problemas = []

    if not ENV_PATH.exists():
        problemas.append(f"No se encontró el archivo .env en: {ENV_PATH}")

    if not FOOTBALL_DATA_KEY:
        problemas.append("Falta FOOTBALL_DATA_KEY en el .env")

    if not ODDS_API_KEY:
        problemas.append("Falta ODDS_API_KEY en el .env")

    if problemas:
        print("⚠️  Problemas de configuración:")
        for p in problemas:
            print(f"   - {p}")
        return False

    print("✅ Configuración correcta: ambas API keys cargadas.")
    return True


# Si ejecutas este archivo directamente (python config/settings.py),
# corre la verificación. Si solo se importa desde otro módulo, no hace nada.
if __name__ == "__main__":
    verificar_configuracion()
