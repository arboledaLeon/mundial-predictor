"""
elo.py — Modelo de rating ELO adaptado al fútbol de selecciones (Mundial 2026).

¿Qué hace este archivo?
Le da a cada selección un número (su "ELO") que mide su fuerza actual.
Con ese número calcula la probabilidad de que un equipo le gane a otro,
y actualiza los ratings después de cada partido real.

¿Por qué ELO y no otra cosa primero?
Porque es simple, robusto y da buenos resultados rápido. Es el "esqueleto"
de probabilidad sobre el que luego Dixon-Coles pondrá la carne (los goles).

Decisiones de diseño (aprobadas en la sesión 003):
  - El ELO inicial NO arranca parejo: se deriva de la POSICIÓN en el ranking
    FIFA, no de puntos inventados (la posición sí es verificable; los puntos
    al entero, no). Argentina (#1) no empieza igual que Nueva Zelanda (#48).
  - Constante de sensibilidad = 400 (estándar universal heredado del ajedrez).
  - K-factor según importancia del partido (leídos de CLAUDE.md):
    Mundial=60, Clasificatoria=50, Amistoso=40.
  - Ventaja de sede: +50 ELO SOLO para los 3 anfitriones (México, USA, Canadá)
    cuando juegan en casa, y SOLO para el cálculo de probabilidad de ese
    partido (no modifica el rating permanente).
"""

import sys
import unicodedata
from pathlib import Path

# Importamos settings para reusar la corrección de codificación UTF-8 (para que
# los acentos y emojis se vean bien en la consola de Windows) y mantener todo
# consistente con el resto del proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from config import settings  # noqa: E402  (se importa tras ajustar sys.path)


# ═════════════════════════════════════════════════════════════
# 1. CONSTANTES DEL MODELO
# ═════════════════════════════════════════════════════════════
SENSIBILIDAD = 400        # Cuántos puntos ELO equivalen a "10 veces más probable de ganar"
ELO_MAX = 1900            # ELO de la selección #1 del ranking
ELO_MIN = 1200            # ELO de la selección #48 del ranking
BONO_SEDE = 50            # Puntos ELO extra para un anfitrión jugando en casa

# K-factor: cuánto se mueve el rating tras un partido. Más alto = más volátil.
# Valores leídos de CLAUDE.md (sección "Rating ELO adaptado al fútbol").
K_FACTOR = {
    "mundial": 60,         # El partido más importante: más peso
    "clasificatoria": 50,  # Partidos oficiales rumbo al Mundial
    "amistoso": 40,        # Resultados menos representativos: menos peso
}

# Modelo de empate: el ELO puro solo da "expectativa de victoria" (que reparte
# el empate por la mitad). Para dar un pronóstico 1X2 (gana local / empate /
# gana visitante) estimamos el empate aparte.
#
# DRAW_BASE = empate cuando los dos equipos están PERFECTAMENTE parejos (e=0.5),
# es decir, el MÁXIMO de la curva de empate, NO el promedio de todos los partidos.
#
# Calibración (verificada en sesión 003):
#   - Tasa histórica completa 1930-2022: 24.7% de empates en fase de grupos
#     (166/671, wfstats.co.uk). PERO incluye eras antiguas muy defensivas.
#   - Era moderna (2014-2022): la banda real es ~16-20%. Dato verificado:
#     2018 = 16.7% (8/48, footballhistory.org); 2014 con empates
#     "excepcionalmente raros" (el primero llegó hasta el partido 13).
#   Elegimos la era MODERNA porque 2026 es fútbol actual.
#
# Conversión de ese promedio (~16-20%) al pico DRAW_BASE: como el promedio
# incluye partidos desbalanceados (que casi no empatan) y el pico es de
# partidos parejos, el pico va por encima del promedio. Con un favorito típico
# de grupo (e≈0.62): media(1-|2e-1|)≈0.75, así que 0.26*0.75≈0.195 ≈ 19% de
# empates promedio en el modelo -> dentro de la banda moderna. Por eso 0.26.
DRAW_BASE = 0.26

# Los 3 países anfitriones del Mundial 2026 (nombres canónicos en español).
ANFITRIONES = {"México", "Estados Unidos", "Canadá"}


# ═════════════════════════════════════════════════════════════
# 2. LOS 48 CLASIFICADOS, EN ORDEN DE RANKING (fuente de la verdad)
# ═════════════════════════════════════════════════════════════
# ⚠️ ACTUALIZAR: ELO inicial derivado de la POSICIÓN en el ranking FIFA,
#    NO de puntos exactos (los puntos al entero no eran verificables).
#    - El CAMPO de 48 equipos y sus GRUPOS están verificados contra el sorteo
#      oficial del 5 de diciembre de 2025.
#    - El ORDEN del ranking se verificó el 11 de junio de 2026 (última
#      actualización FIFA antes del Mundial) SOLO para el top 6 y los
#      anfitriones (México #14, USA #17, Canadá #30). El orden de las demás
#      posiciones es una estimación por fuerza relativa.
#    Ranking oficial: https://www.fifa.com/fifa-world-ranking
#
#    Fórmula: ELO = 1900 - (posición - 1) * (700 / 47)
#    -> #1 = 1900, #48 = 1200, cada puesto vale ~14.9 ELO.
#    Limitación conocida: lineal-por-posición comprime las diferencias en el
#    top (los puntos FIFA reales no son lineales). Aceptable por ahora; si
#    conseguimos los puntos oficiales, volvemos al método por puntos.
#
# La lista está ordenada del #1 al #48. La posición = índice + 1.
# Cada elemento es (nombre_en_español, grupo_del_mundial).
SELECCIONES = [
    ("Argentina", "J"),           # 1
    ("España", "H"),              # 2
    ("Francia", "I"),             # 3
    ("Inglaterra", "L"),          # 4
    ("Portugal", "K"),            # 5
    ("Brasil", "C"),              # 6
    ("Países Bajos", "F"),        # 7
    ("Bélgica", "G"),             # 8
    ("Alemania", "E"),            # 9
    ("Croacia", "L"),             # 10
    ("Marruecos", "C"),           # 11
    ("Colombia", "K"),            # 12
    ("Uruguay", "H"),             # 13
    ("México", "A"),              # 14  (anfitrión)
    ("Japón", "F"),               # 15
    ("Suiza", "B"),               # 16
    ("Estados Unidos", "D"),      # 17  (anfitrión)
    ("Senegal", "I"),             # 18
    ("Irán", "G"),                # 19
    ("Ecuador", "E"),             # 20
    ("Corea del Sur", "A"),       # 21
    ("Austria", "J"),             # 22
    ("Australia", "D"),           # 23
    ("Noruega", "I"),             # 24
    ("Türkiye", "D"),             # 25
    ("Egipto", "G"),              # 26
    ("Costa de Marfil", "E"),     # 27
    ("Argelia", "J"),             # 28
    ("Paraguay", "D"),            # 29
    ("Canadá", "B"),              # 30  (anfitrión)
    ("Túnez", "F"),               # 31
    ("Escocia", "C"),             # 32
    ("Suecia", "F"),              # 33
    ("Catar", "B"),               # 34
    ("Arabia Saudita", "H"),      # 35
    ("Congo DR", "K"),            # 36
    ("Sudáfrica", "A"),           # 37
    ("Panamá", "L"),              # 38
    ("Uzbekistán", "K"),          # 39
    ("Bosnia-Herzegovina", "B"),  # 40
    ("Irak", "I"),                # 41
    ("Jordania", "J"),            # 42
    ("Ghana", "L"),               # 43
    ("Cabo Verde", "H"),          # 44
    ("Chequia", "A"),             # 45
    ("Haití", "C"),               # 46
    ("Curazao", "G"),             # 47
    ("Nueva Zelanda", "G"),       # 48
]

# Cuántas selecciones hay (48). Lo calculamos en vez de escribir "48" a mano,
# así si algún día cambia la lista, la fórmula se ajusta sola.
N_SELECCIONES = len(SELECCIONES)


# ═════════════════════════════════════════════════════════════
# 3. ALIAS: nombres en inglés (de la API) -> nombre canónico en español
# ═════════════════════════════════════════════════════════════
# football-data.org devuelve los nombres en inglés. Este diccionario los
# traduce a nuestros nombres en español para que todo cuadre.
ALIAS = {
    "argentina": "Argentina",
    "spain": "España",
    "france": "Francia",
    "england": "Inglaterra",
    "portugal": "Portugal",
    "brazil": "Brasil",
    "netherlands": "Países Bajos",
    "belgium": "Bélgica",
    "germany": "Alemania",
    "croatia": "Croacia",
    "morocco": "Marruecos",
    "colombia": "Colombia",
    "uruguay": "Uruguay",
    "mexico": "México",
    "japan": "Japón",
    "switzerland": "Suiza",
    "united states": "Estados Unidos",
    "usa": "Estados Unidos",
    "us": "Estados Unidos",
    "senegal": "Senegal",
    "iran": "Irán",
    "ir iran": "Irán",
    "ecuador": "Ecuador",
    "south korea": "Corea del Sur",
    "korea republic": "Corea del Sur",
    "austria": "Austria",
    "australia": "Australia",
    "norway": "Noruega",
    "turkey": "Türkiye",
    "turkiye": "Türkiye",
    "egypt": "Egipto",
    "ivory coast": "Costa de Marfil",
    "cote d'ivoire": "Costa de Marfil",
    "algeria": "Argelia",
    "paraguay": "Paraguay",
    "canada": "Canadá",
    "tunisia": "Túnez",
    "scotland": "Escocia",
    "sweden": "Suecia",
    "qatar": "Catar",
    "saudi arabia": "Arabia Saudita",
    "dr congo": "Congo DR",
    "congo dr": "Congo DR",
    "democratic republic of congo": "Congo DR",
    "south africa": "Sudáfrica",
    "panama": "Panamá",
    "uzbekistan": "Uzbekistán",
    "bosnia-herzegovina": "Bosnia-Herzegovina",
    "bosnia and herzegovina": "Bosnia-Herzegovina",
    "iraq": "Irak",
    "jordan": "Jordania",
    "ghana": "Ghana",
    "cape verde": "Cabo Verde",
    "cabo verde": "Cabo Verde",
    "czechia": "Chequia",
    "czech republic": "Chequia",
    "haiti": "Haití",
    "curacao": "Curazao",
    "new zealand": "Nueva Zelanda",
}


# ═════════════════════════════════════════════════════════════
# 4. CONVERSIÓN POSICIÓN -> ELO INICIAL
# ═════════════════════════════════════════════════════════════
def posicion_a_elo(posicion):
    """
    Convierte la posición en el ranking (1 a 48) al ELO inicial.

    Fórmula:
        ELO = 1900 - (posición - 1) * (700 / 47)

    El #1 recibe 1900, el #48 recibe 1200, y el resto baja en pasos iguales
    de ~14.9 puntos por cada puesto. Es una recta entre el mejor y el peor.
    """
    paso = (ELO_MAX - ELO_MIN) / (N_SELECCIONES - 1)  # 700 / 47 ≈ 14.894
    return ELO_MAX - (posicion - 1) * paso


# Construimos los diccionarios que se usan en todo el módulo, una sola vez:
#   RATINGS = {selección: ELO inicial}
#   GRUPOS  = {selección: letra de grupo}
RATINGS = {}
GRUPOS = {}
for _indice, (_equipo, _grupo) in enumerate(SELECCIONES):
    _posicion = _indice + 1
    RATINGS[_equipo] = posicion_a_elo(_posicion)
    GRUPOS[_equipo] = _grupo


# ═════════════════════════════════════════════════════════════
# 5. NORMALIZACIÓN DE NOMBRES Y BÚSQUEDA
# ═════════════════════════════════════════════════════════════
def _normalizar(texto):
    """
    Pasa un nombre a una forma estándar para compararlo sin importar mayúsculas
    ni acentos. Ej: "  Perú " -> "peru", "FRANCE" -> "france".
    """
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


# Índice de búsqueda: forma normalizada -> nombre canónico en español.
# Incluye los nombres oficiales de la tabla y los alias en inglés.
_INDICE = {}
for _equipo in RATINGS:
    _INDICE[_normalizar(_equipo)] = _equipo
for _alias, _canonico in ALIAS.items():
    _INDICE[_normalizar(_alias)] = _canonico


def nombre_canonico(equipo):
    """Devuelve el nombre oficial en español de una selección (o el original si no se halla)."""
    clave = _INDICE.get(_normalizar(equipo))
    return clave if clave else equipo


def obtener_elo(equipo):
    """
    Devuelve el ELO inicial de una selección a partir de su nombre.
    Acepta español o inglés, con o sin acentos/mayúsculas.

    Si el equipo no está en la tabla, lanza un error claro en vez de fallar
    de forma confusa más adelante.
    """
    clave = _INDICE.get(_normalizar(equipo))
    if clave is None:
        raise ValueError(
            f"No conozco la selección '{equipo}'. Revisa el nombre o "
            f"agrégala a la lista SELECCIONES en modelos/elo.py."
        )
    return RATINGS[clave]


# ═════════════════════════════════════════════════════════════
# 6. PROBABILIDAD DE VICTORIA (núcleo del ELO)
# ═════════════════════════════════════════════════════════════
def expectativa(elo_a, elo_b):
    """
    Calcula la "expectativa" del equipo A: un número entre 0 y 1 que mezcla
    victorias y empates (un empate cuenta como medio).

    Fórmula ELO estándar:
        E_A = 1 / (1 + 10^((elo_B - elo_A) / 400))

    Ejemplo: si A tiene 400 puntos más que B, E_A ≈ 0.91 (muy favorito).
    """
    return 1 / (1 + 10 ** ((elo_b - elo_a) / SENSIBILIDAD))


def _normalizar_probabilidades(p_local, p_empate, p_visitante):
    """
    Garantiza que las 3 probabilidades sean >= 0 y sumen exactamente 1.0.

    ¿Por qué existe esto si la fórmula actual no produce negativos?
    Es una DEFENSA explícita: si en el futuro se sube DRAW_BASE o se cambia la
    forma del empate, esta función evita que se escape una probabilidad negativa
    o que la suma no dé 1 por errores de redondeo. El invariante queda blindado
    aquí y verificado en tests/test_elo.py.

    Pasos:
      1) Recortar (clamp) cualquier valor negativo a 0.
      2) Renormalizar dividiendo por el total, para que sumen 1 exacto.
    """
    p_local = max(0.0, p_local)
    p_empate = max(0.0, p_empate)
    p_visitante = max(0.0, p_visitante)

    total = p_local + p_empate + p_visitante
    if total == 0:
        # Caso imposible en la práctica (siempre hay algo de probabilidad).
        # Repartimos uniforme para no dividir por cero.
        return 1 / 3, 1 / 3, 1 / 3

    return p_local / total, p_empate / total, p_visitante / total


def calcular_1x2(local, visitante, es_sede=False):
    """
    Calcula las probabilidades 1X2 (gana local / empate / gana visitante).

    local, visitante: nombres de las selecciones (español o inglés).
    es_sede: si True, suma BONO_SEDE (+50) al ELO del local SOLO para este
             cálculo (no cambia el rating permanente). Solo aplica si el local
             es uno de los 3 anfitriones reales (México, USA, Canadá).

    Cómo separamos el empate (modelo simple y consistente):
        1) Sacamos la expectativa E del local con la fórmula ELO.
        2) Estimamos el empate: máximo cuando los equipos están parejos,
           y baja a medida que uno domina:
               P(empate) = DRAW_BASE * (1 - |2*E - 1|)
        3) Repartimos el resto respetando la expectativa ELO:
               P(local) = E - P(empate)/2
               P(visit) = (1 - E) - P(empate)/2
        4) Pasamos por _normalizar_probabilidades() para blindar el invariante
           (>= 0 y suma 1).

    Devuelve un diccionario con probabilidades, ELOs y cuotas justas.
    """
    elo_local = obtener_elo(local)
    elo_visitante = obtener_elo(visitante)

    # Bono de sede: solo si se pide Y el local es anfitrión real.
    elo_local_ajustado = elo_local
    sede_aplicada = False
    if es_sede and nombre_canonico(local) in ANFITRIONES:
        elo_local_ajustado += BONO_SEDE
        sede_aplicada = True

    # 1) Expectativa del local (incluye empates a medias).
    e_local = expectativa(elo_local_ajustado, elo_visitante)

    # 2) Probabilidad de empate.
    p_empate = DRAW_BASE * (1 - abs(2 * e_local - 1))

    # 3) Victoria local y visitante.
    p_local = e_local - p_empate / 2
    p_visitante = (1 - e_local) - p_empate / 2

    # 4) Blindaje: nunca negativas, siempre suman 1.
    p_local, p_empate, p_visitante = _normalizar_probabilidades(
        p_local, p_empate, p_visitante
    )

    return {
        "local": nombre_canonico(local),
        "visitante": nombre_canonico(visitante),
        "elo_local": elo_local,
        "elo_visitante": elo_visitante,
        "elo_local_ajustado": elo_local_ajustado,
        "sede_aplicada": sede_aplicada,
        "prob_local": p_local,
        "prob_empate": p_empate,
        "prob_visitante": p_visitante,
        # Cuota "justa" = 1 / probabilidad (sin margen de la casa). Si la casa
        # ofrece MÁS que esto, puede haber valor.
        "cuota_justa_local": (1 / p_local) if p_local > 0 else None,
        "cuota_justa_empate": (1 / p_empate) if p_empate > 0 else None,
        "cuota_justa_visitante": (1 / p_visitante) if p_visitante > 0 else None,
    }


# ═════════════════════════════════════════════════════════════
# 7. ACTUALIZACIÓN DEL RATING TRAS UN PARTIDO REAL
# ═════════════════════════════════════════════════════════════
def actualizar_elo(elo_local, elo_visitante, goles_local, goles_visitante,
                   tipo_partido="mundial"):
    """
    Calcula los nuevos ELO de ambos equipos después de un partido real.

    elo_local, elo_visitante: ratings ANTES del partido.
    goles_local, goles_visitante: marcador final.
    tipo_partido: "mundial", "clasificatoria" o "amistoso" (define el K-factor).

    Fórmula:
        nuevo_ELO = ELO_viejo + K * (resultado_real - expectativa)
        resultado_real: 1 si ganó, 0.5 si empató, 0 si perdió.

    Importante: el bono de sede NO se aplica aquí. La ventaja de local sirve
    para predecir, pero el rating permanente refleja la fuerza "neutral" real.

    Devuelve (nuevo_elo_local, nuevo_elo_visitante).
    """
    k = K_FACTOR.get(tipo_partido, 60)

    # Resultado real desde el punto de vista del local.
    if goles_local > goles_visitante:
        resultado_local = 1.0
    elif goles_local < goles_visitante:
        resultado_local = 0.0
    else:
        resultado_local = 0.5

    # Expectativa del local (sin bono de sede: fuerza neutral).
    e_local = expectativa(elo_local, elo_visitante)

    # El local se mueve según qué tan lejos quedó su resultado de lo esperado.
    nuevo_local = elo_local + k * (resultado_local - e_local)
    # El visitante se mueve en sentido contrario (todo es complementario).
    nuevo_visitante = elo_visitante + k * ((1 - resultado_local) - (1 - e_local))

    return nuevo_local, nuevo_visitante


# ═════════════════════════════════════════════════════════════
# 8. MOSTRAR PREDICCIÓN EN CONSOLA
# ═════════════════════════════════════════════════════════════
def _porcentaje(p):
    """Convierte 0.583 en el texto '58.3%'."""
    return f"{p * 100:.1f}%"


def mostrar_prediccion(local, visitante, es_sede=False):
    """Imprime el pronóstico 1X2 de un partido de forma legible."""
    r = calcular_1x2(local, visitante, es_sede=es_sede)

    print("─" * 56)
    titulo = f"  {r['local']}  vs  {r['visitante']}"
    if r["sede_aplicada"]:
        titulo += "   (local con ventaja de sede +50)"
    print(titulo)
    print("─" * 56)
    linea_elo = f"  ELO {r['local']}: {r['elo_local']:.0f}"
    if r["sede_aplicada"]:
        linea_elo += f" (con sede: {r['elo_local_ajustado']:.0f})"
    linea_elo += f"   |   ELO {r['visitante']}: {r['elo_visitante']:.0f}"
    print(linea_elo)
    print()
    print(f"  Gana {r['local']:<18} {_porcentaje(r['prob_local']):>6}"
          f"   | cuota justa {r['cuota_justa_local']:.2f}")
    print(f"  Empate{'':<17} {_porcentaje(r['prob_empate']):>6}"
          f"   | cuota justa {r['cuota_justa_empate']:.2f}")
    print(f"  Gana {r['visitante']:<18} {_porcentaje(r['prob_visitante']):>6}"
          f"   | cuota justa {r['cuota_justa_visitante']:.2f}")
    print("─" * 56)


# ═════════════════════════════════════════════════════════════
# 9. DEMOSTRACIÓN (los 3 casos de prueba aprobados)
# ═════════════════════════════════════════════════════════════
def _demo():
    """Corre los 3 casos de prueba para verificar que el modelo tiene sentido."""
    print("=" * 56)
    print("  DEMO — MODELO ELO MUNDIAL 2026")
    print("=" * 56)

    print("\n[CASO 1] Dos potencias en terreno neutral:\n")
    mostrar_prediccion("Argentina", "Francia", es_sede=False)

    print("\n[CASO 2] Anfitrión en casa (bono de sede activo):\n")
    mostrar_prediccion("USA", "Portugal", es_sede=True)
    print("  Nota: sin el bono, la probabilidad de USA sería menor. El +50 ELO")
    print("  refleja jugar en su país, pero no le alcanza para ser favorito")
    print("  ante un top como Portugal.")

    print("\n[CASO 3] SORPRESA — verificar el ajuste post-partido:\n")
    print("  Antes del partido: Arabia Saudita (débil) vs Argentina (top)")
    mostrar_prediccion("Arabia Saudita", "Argentina", es_sede=False)

    elo_saudi = obtener_elo("Arabia Saudita")
    elo_arg = obtener_elo("Argentina")
    print("  Simulamos una SORPRESA: Arabia Saudita gana 2-1 (como en 2022).")
    nuevo_saudi, nuevo_arg = actualizar_elo(
        elo_saudi, elo_arg, goles_local=2, goles_visitante=1, tipo_partido="mundial"
    )
    print(f"    Arabia Saudita: {elo_saudi:.0f}  ->  {nuevo_saudi:.0f}  "
          f"(+{nuevo_saudi - elo_saudi:.1f})")
    print(f"    Argentina:      {elo_arg:.0f}  ->  {nuevo_arg:.0f}  "
          f"({nuevo_arg - elo_arg:.1f})")
    print("\n  ✓ Tiene sentido: ganar siendo MUY poco favorito sube mucho al")
    print("    débil y castiga al favorito. Si hubiera ganado Argentina (lo")
    print("    esperado), los ratings apenas se habrían movido.")
    print("=" * 56)


# ═════════════════════════════════════════════════════════════
# 10. PUNTO DE ENTRADA
# ═════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Sin argumentos (o "demo"): corre la demostración de los 3 casos.
    # Con dos nombres: python modelos/elo.py "Argentina" "Francia" [--sede]
    args = sys.argv[1:]

    if not args or args[0].lower() == "demo":
        _demo()
    elif len(args) >= 2:
        sede = "--sede" in args
        mostrar_prediccion(args[0], args[1], es_sede=sede)
    else:
        print("Uso:")
        print('  python modelos/elo.py                          -> demo de 3 casos')
        print('  python modelos/elo.py "Argentina" "Francia"      -> un partido')
        print('  python modelos/elo.py "USA" "Portugal" --sede    -> con ventaja de sede')
