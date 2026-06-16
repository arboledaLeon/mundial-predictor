"""
test_elo.py — Pruebas automáticas del modelo ELO.

¿Para qué sirven los tests?
Para verificar SOLOS, sin que un humano mire, que el modelo cumple sus reglas
fundamentales. Si mañana alguien cambia una fórmula y rompe algo, estos tests
fallan y avisan. "Se ve bien en la demo" no basta: el test lo comprueba.

Cómo correrlos (dos formas, ambas funcionan):
    python tests/test_elo.py        -> corre todo y muestra un resumen
    pytest tests/test_elo.py        -> si tienes pytest instalado

Cubre los 4 casos acordados en la auditoría de la sesión 003:
    1. Las 3 probabilidades de calcular_1x2() siempre suman 1.0
    2. Las 3 probabilidades nunca son negativas (ni en el partido más desigual)
    3. actualizar_elo() no cambia el rating si el resultado es el esperado
    4. El bono de sede solo se aplica a los 3 anfitriones, nunca a otro equipo
"""

import sys
from pathlib import Path

# Agregamos la raíz del proyecto al path para poder importar el modelo,
# igual que hace fetcher.py (este test está en tests/, no en la raíz).
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modelos import elo  # noqa: E402

# Tolerancia para comparar números con decimales (los floats nunca son exactos).
TOLERANCIA = 1e-9


# ─────────────────────────────────────────────────────────────
# TEST 1 — Las 3 probabilidades siempre suman 1.0
# ─────────────────────────────────────────────────────────────
def test_probabilidades_suman_uno():
    """Para varios partidos (parejos y desiguales), P(local)+P(empate)+P(visit) = 1."""
    partidos = [
        ("Argentina", "Francia"),       # parejo arriba
        ("Argentina", "Nueva Zelanda"),  # el más desigual posible
        ("Nueva Zelanda", "Argentina"),  # el mismo, al revés
        ("México", "Estados Unidos"),    # dos anfitriones
        ("Catar", "Jordania"),           # parejo abajo
    ]
    for local, visitante in partidos:
        r = elo.calcular_1x2(local, visitante)
        suma = r["prob_local"] + r["prob_empate"] + r["prob_visitante"]
        assert abs(suma - 1.0) < TOLERANCIA, (
            f"{local} vs {visitante}: las probabilidades suman {suma}, no 1.0"
        )


# ─────────────────────────────────────────────────────────────
# TEST 2 — Las probabilidades nunca son negativas, ni en casos extremos
# ─────────────────────────────────────────────────────────────
def test_probabilidades_nunca_negativas():
    """
    Recorre TODOS los pares posibles de selecciones (el barrido más exigente,
    incluye el partido más desigual del campo) y verifica que ninguna de las
    3 probabilidades sea negativa.
    """
    equipos = list(elo.RATINGS.keys())
    for local in equipos:
        for visitante in equipos:
            if local == visitante:
                continue
            r = elo.calcular_1x2(local, visitante)
            assert r["prob_local"] >= 0, f"P(local) negativa en {local} vs {visitante}"
            assert r["prob_empate"] >= 0, f"P(empate) negativa en {local} vs {visitante}"
            assert r["prob_visitante"] >= 0, f"P(visit) negativa en {local} vs {visitante}"


def test_caso_extremo_argentina_vs_nueva_zelanda():
    """El partido más desigual del campo (#1 vs #48): debe seguir siendo válido."""
    r = elo.calcular_1x2("Argentina", "Nueva Zelanda")
    suma = r["prob_local"] + r["prob_empate"] + r["prob_visitante"]
    assert abs(suma - 1.0) < TOLERANCIA
    assert r["prob_local"] >= 0 and r["prob_empate"] >= 0 and r["prob_visitante"] >= 0
    # Sanidad: Argentina debe ser ampliamente favorita.
    assert r["prob_local"] > 0.90, "Argentina debería ser >90% ante Nueva Zelanda"


# ─────────────────────────────────────────────────────────────
# TEST 3 — actualizar_elo() no cambia nada si el resultado es el esperado
# ─────────────────────────────────────────────────────────────
def test_actualizar_elo_sin_cambio_si_resultado_esperado():
    """
    Sanity check: si dos equipos tienen el MISMO ELO, su expectativa es 0.5
    (es decir, lo "esperado" es un empate). Si efectivamente empatan, el
    resultado coincide exactamente con la expectativa y el rating NO debe moverse.
    """
    elo_igual = 1600.0
    nuevo_local, nuevo_visitante = elo.actualizar_elo(
        elo_igual, elo_igual, goles_local=1, goles_visitante=1, tipo_partido="mundial"
    )
    assert abs(nuevo_local - elo_igual) < TOLERANCIA, "El local no debería cambiar"
    assert abs(nuevo_visitante - elo_igual) < TOLERANCIA, "El visitante no debería cambiar"


def test_actualizar_elo_suma_cero():
    """
    Lo que un equipo gana, el otro lo pierde: el total de ELO se conserva.
    (Propiedad clave del sistema ELO.)
    """
    elo_a, elo_b = 1750.0, 1500.0
    nuevo_a, nuevo_b = elo.actualizar_elo(elo_a, elo_b, 2, 0, "mundial")
    suma_antes = elo_a + elo_b
    suma_despues = nuevo_a + nuevo_b
    assert abs(suma_antes - suma_despues) < TOLERANCIA, "El ELO total debe conservarse"


# ─────────────────────────────────────────────────────────────
# TEST 4 — El bono de sede solo aplica a los 3 anfitriones
# ─────────────────────────────────────────────────────────────
def test_bono_sede_solo_anfitriones():
    """México, USA y Canadá reciben el +50; cualquier otro NO, aunque se pida."""
    # Un anfitrión SÍ recibe el bono.
    r_mexico = elo.calcular_1x2("México", "Japón", es_sede=True)
    assert r_mexico["sede_aplicada"] is True
    assert abs(r_mexico["elo_local_ajustado"] - (r_mexico["elo_local"] + elo.BONO_SEDE)) < TOLERANCIA

    # Un NO anfitrión, aunque pida es_sede=True, NO recibe el bono.
    r_arg = elo.calcular_1x2("Argentina", "Francia", es_sede=True)
    assert r_arg["sede_aplicada"] is False
    assert abs(r_arg["elo_local_ajustado"] - r_arg["elo_local"]) < TOLERANCIA


def test_bono_sede_aumenta_probabilidad():
    """Con el bono, el anfitrión debe tener MÁS probabilidad que sin él."""
    sin_sede = elo.calcular_1x2("Estados Unidos", "Portugal", es_sede=False)
    con_sede = elo.calcular_1x2("Estados Unidos", "Portugal", es_sede=True)
    assert con_sede["prob_local"] > sin_sede["prob_local"], (
        "El bono de sede debería subir la probabilidad del anfitrión"
    )


# ─────────────────────────────────────────────────────────────
# CORREDOR MANUAL (para 'python tests/test_elo.py' sin pytest)
# ─────────────────────────────────────────────────────────────
def _correr_todos():
    """Ejecuta todas las funciones test_* de este archivo y reporta resultados."""
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    fallos = 0
    print("=" * 56)
    print("  TESTS DEL MODELO ELO")
    print("=" * 56)
    for funcion in tests:
        try:
            funcion()
            print(f"  ✓ {funcion.__name__}")
        except AssertionError as e:
            fallos += 1
            print(f"  ✗ {funcion.__name__}  ->  {e}")
        except Exception as e:
            fallos += 1
            print(f"  ✗ {funcion.__name__}  ->  ERROR: {e}")
    print("=" * 56)
    if fallos == 0:
        print(f"  TODOS LOS TESTS PASARON ({len(tests)}/{len(tests)}) ✅")
    else:
        print(f"  {fallos} de {len(tests)} tests FALLARON ❌")
    print("=" * 56)
    return fallos


if __name__ == "__main__":
    n_fallos = _correr_todos()
    # Salimos con código 1 si algo falló (útil para automatización futura).
    sys.exit(1 if n_fallos else 0)
