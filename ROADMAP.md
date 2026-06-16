# ROADMAP.md — Hoja de Ruta: Mundial Predictor

> Tu mapa completo desde cero hasta un sistema que genere ingresos reales.
> Marca cada tarea con ✅ cuando la termines.

---

## Vista general

```
FASE 1 → Terminal (semanas 1-2)
   ↓
FASE 2 → Telegram Bot (semanas 3-4)
   ↓
FASE 3 → Dashboard + Escala (mes 2+)
   ↓
FASE 4 → Ligas del mundo (mes 3+)
```

**Dónde estamos ahora:** Inicio de Fase 1 ← AQUÍ

---

## ═══════════════════════════════════
## FASE 1 — Sistema en Terminal
## Objetivo: Primera predicción real en pantalla
## Tiempo estimado: 1-2 semanas
## ═══════════════════════════════════

### 🗂️ Paso 1.0 — Configurar Git y GitHub
*Lo que aprenderás: control de versiones, repositorios remotos, flujo profesional*

- [ ] Verificar que Git está instalado
  ```bash
  git --version
  # Si no está: https://git-scm.com/downloads
  ```

- [ ] Configurar tu identidad en Git (solo se hace una vez)
  ```bash
  git config --global user.name "Tu Nombre"
  git config --global user.email "tu@email.com"
  ```

- [ ] Crear repositorio en GitHub
  - Entrar a github.com → New repository
  - Nombre: `mundial-predictor`
  - Descripción: "Sistema de análisis estadístico para value betting - Mundial 2026"
  - Visibilidad: **Privado** (tiene tus estrategias, no las compartas aún)
  - NO inicializar con README (lo haremos nosotros)

- [ ] Inicializar Git en la carpeta del proyecto
  ```bash
  cd mundial-predictor
  git init
  git branch -M main
  ```

- [ ] Crear `.gitignore` antes del primer commit
  ```bash
  # Claude Code crea este archivo automáticamente desde CLAUDE.md
  # Verificar que .env está incluido — CRÍTICO
  cat .gitignore | grep .env
  ```

- [ ] Primer commit — los archivos de documentación
  ```bash
  git add CLAUDE.md BITACORA.md ROADMAP.md .gitignore
  git commit -m "docs: inicializar proyecto con documentación base"
  git remote add origin https://github.com/TU_USUARIO/mundial-predictor.git
  git push -u origin main
  ```

**¿Cómo saber que funcionó?**
Entras a `github.com/TU_USUARIO/mundial-predictor` y ves los tres archivos .md.

---

### 🔧 Paso 1.1 — Preparar el entorno
*Lo que aprenderás: cómo funciona Python, entornos virtuales, pip*

- [x] Instalar Python 3.11+ en tu computador
  ```bash
  # Verificar si ya lo tienes:
  python --version
  ```
- [x] Crear carpeta del proyecto
  ```bash
  mkdir mundial-predictor
  cd mundial-predictor
  ```
- [x] Crear entorno virtual (caja aislada para el proyecto)
  ```bash
  python -m venv venv
  source venv/bin/activate  # Mac/Linux
  venv\Scripts\activate     # Windows
  ```
- [x] Instalar dependencias base
  ```bash
  pip install requests scipy numpy pandas python-dotenv colorama
  ```
- [x] Instalar Claude Code
  ```bash
  npm install -g @anthropic-ai/claude-code
  ```
- [x] Crear archivo `.env` con tus API keys
  ```
  FOOTBALL_DATA_KEY=tu_key_aqui
  ODDS_API_KEY=tu_key_aqui
  ```

**¿Cómo saber que funcionó?**
```bash
python -c "import numpy; print('✅ Python listo')"
claude --version  # Debe mostrar versión de Claude Code
```

---

### 🌐 Paso 1.2 — Conectar a las APIs
*Lo que aprenderás: qué es una API, cómo hacer requests HTTP, JSON*

- [x] Crear cuenta en football-data.org (gratis)
  - URL: https://www.football-data.org/client/register
  - Copiar el API key al archivo `.env`

- [x] Crear cuenta en The Odds API (gratis, 500 requests/mes)
  - URL: https://the-odds-api.com/
  - Copiar el API key al archivo `.env`

- [x] Escribir `data/fetcher.py` — el módulo que descarga datos
  - Función: obtener partidos del día ✅
  - Función: obtener cuotas de un partido *(pendiente — Paso 1.5)*
  - Función: obtener resultados históricos *(pendiente — Paso 1.4)*

- [x] Probar que los datos llegan correctamente
  ```bash
  python data/fetcher.py
  # Debe mostrar los partidos del Mundial de hoy
  ```

**¿Cómo saber que funcionó?**
```
Partidos encontrados hoy (Mundial 2026):
  España vs Alemania — 18:00 COT
  Brasil vs Argentina — 21:00 COT
```

---

### 📐 Paso 1.3 — Implementar el modelo ELO
*Lo que aprenderás: sistemas de rating, álgebra básica, lógica condicional*

*Empezamos por ELO porque es más simple que Dixon-Coles y da buenos resultados rápido*

- [x] Escribir `modelos/elo.py`
  - Cargar ratings iniciales de todas las selecciones (basado en ranking FIFA)
  - Función: calcular probabilidad de victoria dado ELO de ambos equipos
  - Función: actualizar ELO después de cada resultado real

- [x] Crear base de datos de ratings iniciales para las 48 selecciones del Mundial
  - Derivada de la POSICIÓN en el ranking FIFA (verificada), no de puntos inventados
  - Campo de 48 + grupos verificados contra el sorteo oficial (5 dic 2025)
  - Persistencia en `data/ratings_elo.json` vía `modelos/almacen.py`

- [x] Probar con un partido real
  ```bash
  python modelos/elo.py "Argentina" "Francia"
  # Argentina: 42.4% | Empate: 23.8% | Francia: 33.8%
  ```

- [x] EXTRA (no estaba en el plan): tests automáticos (`tests/test_elo.py`, 7/7 ✅)
- [x] EXTRA: persistencia de ratings con escritura segura (`modelos/almacen.py`)

---

### 📊 Paso 1.4 — Implementar Dixon-Coles
*Lo que aprenderás: distribución de Poisson, optimización matemática, scipy*

*Este es el corazón del sistema. Más complejo pero más preciso.*

- [ ] Escribir `modelos/dixon_coles.py`
  - Función: calcular `lambda` (goles esperados) para cada equipo
  - Función: distribución de Poisson bivariada
  - Función: corrección Dixon-Coles para marcadores bajos
  - Función: factor de decaimiento temporal

- [ ] Ajustar el modelo con datos históricos de mundiales
  - Usar datos de los últimos 3 mundiales (2014, 2018, 2022)
  - Optimizar parámetros con scipy.optimize

- [ ] Combinar con ELO
  - ELO da la probabilidad base
  - Dixon-Coles refina con estadísticas de goles

- [ ] Probar predicción completa
  ```bash
  python modelos/dixon_coles.py "España" "Alemania"
  # Output esperado:
  # Goles esperados: España 1.62 — Alemania 1.18
  # Marcador más probable: 1-1 (12.3%)
  # España gana: 51.2% | Empate: 25.8% | Alemania: 23.0%
  ```

---

### 💰 Paso 1.5 — Implementar detector de value
*Lo que aprenderás: probabilidad implícita, cálculo de edge, gestión de riesgo*

- [ ] Escribir `modelos/value_bet.py`
  - Función: convertir cuota decimal a probabilidad implícita
  - Función: calcular edge (diferencia entre modelo y mercado)
  - Función: calcular Kelly Criterion (tamaño óptimo de apuesta)
  - Función: filtrar solo picks con edge > 3%

- [ ] Integrar cuotas reales de The Odds API

- [ ] Definir umbrales de confianza
  ```python
  EDGE_MINIMO = 0.03        # 3% mínimo
  CONFIANZA_MINIMA = 0.55   # Modelo debe dar 55%+ de probabilidad
  KELLY_FRACCION = 0.25     # Usar solo 25% del Kelly completo (conservador)
  ```

---

### 🖥️ Paso 1.6 — Output bonito en terminal
*Lo que aprenderás: formateo de texto, librería colorama, diseño de CLI*

- [ ] Escribir `analisis/reporte.py`
  - Output con colores (verde = value, rojo = no apostar)
  - Tabla clara con probabilidades y cuotas
  - Resumen de picks del día

- [ ] Escribir `main.py` — el archivo que ejecutas cada día
  ```bash
  python main.py              # Analiza todos los partidos del día
  python main.py "España"     # Analiza solo partidos de España
  python main.py --fecha 2026-06-20  # Analiza una fecha específica
  ```

**🎯 HITO FASE 1 COMPLETADO cuando:**
```
$ python main.py

╔══════════════════════════════════════════════════╗
║     MUNDIAL PREDICTOR — Análisis del día        ║
║     Sábado 20 de junio, 2026                    ║
╚══════════════════════════════════════════════════╝

📊 PARTIDO: España vs Alemania (18:00 COT)
   Probabilidades modelo:
   España:   51.2%  │ Cuota justa: 1.95
   Empate:   25.8%  │ Cuota justa: 3.88
   Alemania: 23.0%  │ Cuota justa: 4.35

   Cuotas Bet365:
   España:   1.75   │ Prob. implícita: 57.1%  ❌ Sin valor
   Empate:   3.60   │ Prob. implícita: 27.8%  ❌ Sin valor
   Alemania: 4.75   │ Prob. implícita: 21.1%  ✅ VALOR +1.9%

   Mercados alternativos:
   ✅ Más de 2.5 goles: Edge +4.2% → APOSTAR
      Cuota: 2.10 | Kelly sugerido: 2.1% del bankroll

═══════════════════════════════════════════════════
📌 PICKS DEL DÍA:
   1. España-Alemania: Más de 2.5 goles @ 2.10
      Stake sugerido: $2.000 COP (2% de $100k bankroll)
═══════════════════════════════════════════════════
```

---

## ═══════════════════════════════════
## FASE 2 — Bot de Telegram
## Objetivo: Recibir alertas en el celular automáticamente
## Tiempo estimado: 1 semana
## ═══════════════════════════════════

### 📱 Paso 2.1 — Crear el bot de Telegram
*Lo que aprenderás: Telegram Bot API, python-telegram-bot, webhooks*

- [ ] Crear bot en Telegram con @BotFather
  - Comando: `/newbot`
  - Guardar el token en `.env`
- [ ] Instalar librería: `pip install python-telegram-bot`
- [ ] Escribir `telegram/bot.py` con comandos básicos:
  - `/analisis` → Muestra partidos del día
  - `/picks` → Solo los value bets de hoy
  - `/bankroll 50000` → Registra tu bankroll actual
  - `/historial` → Tus últimos 10 picks y resultados

### ⏰ Paso 2.2 — Automatizar alertas
*Lo que aprenderás: cron jobs, scheduling, automatización*

- [ ] Configurar análisis automático 3 horas antes de cada partido
- [ ] Alerta cuando se detecta value bet nuevo
- [ ] Resumen diario cada noche con resultados

**🎯 HITO FASE 2 COMPLETADO cuando:**
Tu celular recibe esto automáticamente a las 15:00 sin que hagas nada:

```
🤖 MUNDIAL PREDICTOR

⚽ España vs Alemania — HOY 18:00

✅ VALUE BET DETECTADO
Mercado: Más de 2.5 goles
Cuota: 2.10 (Bet365)
Edge: +4.2%
Stake: 2% bankroll

Probabilidades modelo:
🟦 España: 51.2%
⬜ Empate: 25.8%
🟥 Alemania: 23.0%
```

---

## ═══════════════════════════════════
## FASE 3 — Dashboard Web + Escala
## Objetivo: Interfaz visual y sistema profesional
## Tiempo estimado: 2-3 semanas
## ═══════════════════════════════════

### 🌐 Paso 3.1 — Dashboard web local
*Lo que aprenderás: Flask/Streamlit, HTML básico, visualización de datos*

- [ ] Instalar Streamlit: `pip install streamlit`
- [ ] Escribir `dashboard/app.py`
  - Página de análisis del día
  - Gráficas de rendimiento histórico
  - Curva de bankroll en el tiempo
  - Tabla de picks con filtros

- [ ] Correr localmente:
  ```bash
  streamlit run dashboard/app.py
  # Abre automáticamente en http://localhost:8501
  ```

### 📈 Paso 3.2 — Mejorar el modelo
- [ ] Integrar xG real (TheStatsAPI $50/mes) cuando haya ingresos
- [ ] Agregar análisis de alineaciones confirmadas
- [ ] Implementar modelo de corners y tarjetas
- [ ] Backtesting completo con datos de mundiales anteriores

### 💼 Paso 3.3 — Escalar a otras ligas
- [ ] Premier League inglesa (más datos = modelo más preciso)
- [ ] Champions League
- [ ] Liga Betplay Colombia (conoces el contexto local)
- [ ] Cualquier liga con datos disponibles

**🎯 HITO FASE 3 COMPLETADO cuando:**
Un domingo cualquiera puedes:
1. Abrir la terminal: `streamlit run dashboard/app.py`
2. Ver todos los partidos del día con análisis completo
3. Seleccionar 3-5 picks con value real
4. Apostar $20.000-$50.000 COP estratégicamente
5. Cerrar el computador y esperar resultados

---

## ═══════════════════════════════════
## FASE 4 — Sistema profesional
## Objetivo: Sustento real en Colombia
## Tiempo estimado: mes 3+
## ═══════════════════════════════════

### 💰 Números reales para Colombia

```
ESCENARIO CONSERVADOR (bankroll $500.000 COP):
- Picks por semana: 10-15
- Acierto esperado: 55-58%
- Stake promedio: 2% = $10.000 COP
- ROI esperado: 8-12% mensual
- Ganancia mensual: $40.000 - $60.000 COP
→ Complemento de ingresos, no sustento aún

ESCENARIO MEDIO (bankroll $2.000.000 COP):
- Picks por semana: 10-15
- Stake promedio: 2% = $40.000 COP
- ROI esperado: 8-12% mensual
- Ganancia mensual: $160.000 - $240.000 COP
→ Ayuda significativa

ESCENARIO ÓPTIMO (bankroll $5.000.000 COP):
- Picks por semana: 15-20
- Stake promedio: 2% = $100.000 COP
- ROI esperado: 8-12% mensual
- Ganancia mensual: $400.000 - $600.000 COP
→ Sustento real en Colombia

CLAVE: Los números escalan con disciplina, no con suerte.
La disciplina es no salirse del sistema aunque se pierdan 3 seguidas.
```

### 📋 Posibles fuentes de ingreso adicionales
- [ ] Canal de Telegram con picks (cobrar suscripción $20.000-$50.000 COP/mes)
- [ ] Afiliados de casas de apuestas (Codere, Betplay, Wplay pagan por usuario referido)
- [ ] Vender el servicio de análisis a otros apostadores

---

## Progreso actual

```
FASE 1: ████░░░░░░ 40%  ← Aquí estamos (Pasos 1.1, 1.2 y 1.3 completados)
FASE 2: ░░░░░░░░░░ 0%
FASE 3: ░░░░░░░░░░ 0%
FASE 4: ░░░░░░░░░░ 0%
```

---

## Checklist de conocimientos adquiridos

### Python
- [ ] Variables, tipos de datos, funciones
- [ ] Condicionales y bucles
- [ ] Manejo de archivos
- [ ] Llamadas a APIs (requests)
- [ ] Librerías científicas (numpy, scipy, pandas)
- [ ] Programación orientada a objetos

### Estadística y matemáticas
- [ ] Distribución de Poisson
- [ ] Probabilidad básica
- [ ] Optimización de funciones
- [ ] Interpretación de datos

### Apuestas deportivas
- [ ] Tipos de cuotas (decimal, americana, fraccional)
- [ ] Cálculo de probabilidad implícita
- [ ] Concepto de value betting
- [ ] Kelly Criterion
- [ ] Gestión de bankroll
- [ ] Tipos de mercados (1X2, Over/Under, BTTS, Handicap)

### Herramientas
- [ ] Terminal/línea de comandos
- [ ] Git (control de versiones)
- [ ] Claude Code
- [ ] APIs REST
- [ ] Telegram Bot API

---

*Roadmap creado: Junio 2026*
*Actualizar el % de progreso en cada sesión*
