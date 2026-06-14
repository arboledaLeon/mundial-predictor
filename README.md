# ⚽ Mundial Predictor

> Sistema de análisis estadístico para detección de value bets en fútbol.
> Iniciado durante el Mundial 2026. Construido en Medellín, Colombia.

---

## ¿Qué hace este sistema?

Analiza partidos de fútbol cruzando tres fuentes de datos:
- **Estadísticas** → modelo Dixon-Coles + ELO para predecir probabilidades reales
- **Variables macro** → método Klement (ranking FIFA, PIB, población, cultura fútbol)  
- **Cuotas del mercado** → detecta dónde la casa de apuestas está "equivocada"

Cuando la probabilidad del modelo supera la probabilidad implícita en la cuota + un margen mínimo, el sistema alerta: **value bet detectado**.

---

## Estado del proyecto

```
FASE 1 — Terminal:     ░░░░░░░░░░ 0%   ← Aquí estamos
FASE 2 — Telegram Bot: ░░░░░░░░░░ 0%
FASE 3 — Dashboard:    ░░░░░░░░░░ 0%
FASE 4 — Escalar:      ░░░░░░░░░░ 0%
```

Ver [ROADMAP.md](./ROADMAP.md) para el plan detallado.

---

## Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/mundial-predictor.git
cd mundial-predictor

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 5. Ejecutar
python main.py
```

---

## Uso básico

```bash
# Analizar todos los partidos del día
python main.py

# Analizar un partido específico
python main.py --partido "España vs Alemania"

# Ver historial de picks
python main.py --historial
```

---

## Modelos matemáticos

| Modelo | Función | Estado |
|--------|---------|--------|
| Dixon-Coles | Predicción de goles por Poisson bivariada | 🔲 Pendiente |
| ELO adaptado | Rating dinámico por selección | 🔲 Pendiente |
| Variables Klement | Peso macro por país | 🔲 Pendiente |
| Value Detector | Comparación modelo vs cuota | 🔲 Pendiente |

---

## APIs utilizadas

| API | Datos | Plan |
|-----|-------|------|
| [football-data.org](https://football-data.org) | Fixtures, resultados | Gratuito |
| [The Odds API](https://the-odds-api.com) | Cuotas en tiempo real | Gratuito (500 req/mes) |

---

## Documentación del proyecto

- 📋 [ROADMAP.md](./ROADMAP.md) — Fases y pasos detallados
- 📓 [BITACORA.md](./BITACORA.md) — Diario de sesiones y aprendizajes
- 🤖 [CLAUDE.md](./CLAUDE.md) — Guía para Claude Code

---

## Disclaimer

Este sistema es una **herramienta de análisis estadístico educativo**.
No garantiza ganancias. Las apuestas deportivas implican riesgo de pérdida.
Apostar responsablemente: nunca más del 2-5% del bankroll por pick.

---

*Proyecto iniciado: Junio 2026 | Medellín, Colombia*
