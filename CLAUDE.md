# CLAUDE.md — Guía Maestra del Proyecto Mundial Predictor

> Este archivo le dice a Claude Code exactamente qué es este proyecto, cómo está estructurado,
> y cómo debe comportarse al ayudar. Léelo antes de tocar cualquier archivo.

---

## ¿Qué es este proyecto?

Un sistema de análisis estadístico de fútbol para detectar apuestas de valor ("value bets").
Empezó con el Mundial 2026 y está diseñado para escalar a cualquier liga del mundo.

**No es un bot de apuestas automático.** Es una herramienta de análisis que recomienda
oportunidades donde la probabilidad real supera la probabilidad implícita en la cuota.
El humano siempre decide si apuesta o no.

**Dueño del proyecto:** Usuario en Medellín, Colombia.
**Nivel técnico del usuario:** Principiante aprendiendo. Explicar siempre el "por qué".
**Idioma:** Español en todo momento, incluyendo comentarios en el código.

---

## Arquitectura del sistema

```
mundial-predictor/
│
├── CLAUDE.md           ← Este archivo. Leerlo siempre primero.
├── BITACORA.md         ← Diario del proyecto. Actualizar después de cada sesión.
├── ROADMAP.md          ← Fases del proyecto y progreso actual.
├── README.md           ← Instrucciones de instalación y uso rápido.
│
├── config/
│   ├── settings.py     ← Variables de entorno, API keys, configuración global.
│   └── .env            ← Secretos (NO subir a git nunca).
│
├── data/
│   ├── fetcher.py      ← Descarga datos de APIs externas.
│   ├── cache/          ← JSONs guardados localmente para no repetir llamadas.
│   └── historico/      ← Datos históricos de partidos y resultados.
│
├── modelos/
│   ├── dixon_coles.py  ← Modelo matemático principal de predicción de goles.
│   ├── elo.py          ← Sistema de rating dinámico por selección.
│   ├── klement.py      ← Variables macro (PIB, población, cultura fútbol, ranking FIFA).
│   └── value_bet.py    ← Detecta dónde el modelo supera la cuota del mercado.
│
├── analisis/
│   ├── partido.py      ← Analiza un partido específico.
│   ├── jornada.py      ← Analiza todos los partidos del día.
│   └── reporte.py      ← Genera el output final legible en terminal.
│
├── telegram/           ← (Fase 2) Bot de alertas automáticas.
│   └── bot.py
│
├── dashboard/          ← (Fase 3) Interfaz web local.
│   └── app.py
│
└── tests/
    └── test_modelos.py ← Pruebas para verificar que los modelos funcionan.
```

---

## Modelos matemáticos implementados

### 1. Dixon-Coles (núcleo principal)
Predice la distribución de goles de cada equipo usando distribución de Poisson bivariada.
Corrige la subestimación de empates y pondera más los partidos recientes.

**Variables clave:**
- `alpha` = capacidad ofensiva del equipo
- `beta` = capacidad defensiva del equipo
- `gamma` = ventaja de local
- `rho` = corrección para resultados de bajo marcador (0-0, 1-0, 0-1, 1-1)
- `xi` = factor de decaimiento temporal (partidos recientes pesan más)

### 2. Rating ELO adaptado al fútbol
Sistema de rating dinámico que actualiza la "fuerza" de cada selección después de cada partido.
Útil porque hay pocos enfrentamientos históricos entre selecciones nacionales.

**Fórmula:**
```
nuevo_elo = elo_actual + K × (resultado_real - resultado_esperado)
K = 60 para Mundial, 40 para amistosos, 50 para clasificatorias
```

### 3. Variables Klement (contexto macro)
Peso relativo inicial de cada selección basado en:
- Ranking FIFA actual
- PIB per cápita (infraestructura deportiva)
- Población
- Importancia cultural del fútbol en el país
- Factor "sorpresa" matemático

### 4. Detector de Value Bet
```
probabilidad_modelo > probabilidad_implicita_cuota + margen_minimo

probabilidad_implicita = 1 / cuota_decimal
margen_minimo = 0.03  # 3% de edge mínimo para considerar una apuesta
```

---

## APIs y fuentes de datos

### Datos de partidos (gratuito para empezar)
- **football-data.org** → Fixtures, resultados, standings
  - Free tier: 10 llamadas/minuto, datos básicos
  - URL: https://api.football-data.org/v4/
  - Header: `X-Auth-Token: TU_KEY`

### Cuotas de apuestas
- **The Odds API** → Cuotas de múltiples casas
  - Free tier: 500 requests/mes
  - URL: https://api.the-odds-api.com/v4/
  - Casas disponibles: Bet365, Betway, 1xBet, Codere

### Datos avanzados (opcional, de pago)
- **TheStatsAPI** → xG, lineups, cuotas en vivo ($50/mes)
- **Sportmonks** → Todo incluido + IA propia (desde $30/mes)

---

## Protocolo obligatorio de cierre de sesión

**Esto no es opcional. Al final de CADA sesión de trabajo, sin que el usuario
tenga que pedirlo, Claude Code debe ejecutar estos 3 procesos en orden:**

### 1. Documentar en BITACORA.md
Agregar una nueva entrada de sesión usando el template que ya existe al final
del archivo. Debe incluir:
- Qué se construyó (en lenguaje simple, el usuario es principiante)
- Qué conceptos nuevos se tocaron (Python, Git, estadística, apuestas)
- Errores que aparecieron y cómo se resolvieron — esto es lo más valioso,
  nunca omitir un error solo porque ya se arregló
- Checklist de qué falta para la próxima sesión

### 2. Actualizar ROADMAP.md
Marcar con ✅ los checkboxes de las tareas completadas en esta sesión.
Actualizar la barra de progreso de la fase correspondiente.

### 3. Git add, commit y push
Seguir el formato de commits ya definido en este archivo (sección Workflow con Git).
Nunca dejar trabajo funcional sin commitear al cerrar sesión.
Hacer push siempre, no dejar commits solo locales.

**Regla de oro:** si el usuario dice "vamos a cerrar" o "eso es todo por hoy"
o similar, estos 3 pasos se ejecutan automáticamente sin que tenga que pedir
cada uno por separado. Mostrar al usuario un resumen breve de qué se documentó
y qué se commiteó al final.

**Excepción:** si el usuario dice explícitamente "no hagas commit todavía" o
"espera para documentar", respetar eso y solo ejecutarlo cuando lo confirme.

---

## Workflow con Git — Reglas obligatorias

### Filosofía
Cada vez que algo funciona → se commitea. Cada sesión de trabajo → termina con push.
El historial de Git es también un historial de aprendizaje.

### Estructura de commits
Usar siempre este formato para que el historial sea legible:

```
tipo(scope): descripción corta en español

Ejemplos reales del proyecto:
feat(fetcher): conectar API football-data.org para partidos del Mundial
fix(dixon_coles): corregir cálculo de lambda cuando hay pocos datos
docs(bitacora): documentar sesión 003 - implementación ELO completa
test(value_bet): agregar pruebas para detector de edge mínimo
refactor(reporte): mejorar output de terminal con colores
chore(deps): agregar scipy y pandas al requirements.txt
```

Tipos permitidos:
- `feat` → nueva funcionalidad
- `fix` → corrección de error
- `docs` → cambio en documentación (.md files)
- `test` → pruebas
- `refactor` → mejora de código sin cambiar funcionalidad
- `chore` → tareas de mantenimiento (dependencias, configuración)

### Flujo por sesión — Claude Code lo ejecuta automáticamente

```bash
# Al INICIO de cada sesión:
git status                    # Ver qué hay pendiente
git pull origin main          # Traer cambios si los hay

# Durante el trabajo — después de cada hito:
git add .
git commit -m "feat(modelos): implementar Dixon-Coles v1 básico"

# Al FINAL de cada sesión (obligatorio):
git add .
git commit -m "docs(bitacora): actualizar sesión XXX con aprendizajes"
git push origin main
```

### Archivos que NUNCA van a Git

Claude Code debe verificar que `.gitignore` contenga siempre:

```gitignore
# Secretos - NUNCA subir
.env
config/secrets.py

# Python
__pycache__/
*.pyc
*.pyo
venv/
.venv/
*.egg-info/

# Datos cacheados (pueden ser grandes)
data/cache/
data/historico/*.json

# VSCode personal
.vscode/settings.json

# Sistema operativo
.DS_Store
Thumbs.db
```

### Cuándo hacer commit
- ✅ Terminaste una función y funciona
- ✅ Corregiste un error
- ✅ Actualizaste BITACORA.md o ROADMAP.md
- ✅ Agregaste comentarios explicativos
- ❌ NO commitear código roto que no ejecuta
- ❌ NO commitear con API keys hardcodeadas

### Mensaje especial para hitos importantes
```bash
# Cuando completes un paso completo del ROADMAP:
git tag -a v0.1-fase1-terminal -m "Fase 1 completada: primer análisis en terminal"
git push origin --tags
```

---

## Reglas de desarrollo

### Para Claude Code:
1. **Siempre explicar el código** con comentarios en español que enseñen al usuario
2. **Nunca borrar** archivos sin confirmación explícita del usuario
3. **Actualizar BITACORA.md** al final de cada sesión de trabajo
4. **Primero hacer funcionar, luego optimizar** — no sobre-ingeniería al inicio
5. **Manejo de errores siempre** — las APIs fallan, los datos llegan sucios
6. **Guardar datos en cache** — no hacer llamadas innecesarias a APIs
7. **Variables de entorno para secretos** — nunca hardcodear API keys

### Estilo de código:
```python
# ✅ Correcto — comentarios que enseñan
def calcular_probabilidad_poisson(lambda_local, lambda_visitante, max_goles=10):
    """
    Calcula la probabilidad de cada marcador posible usando distribución de Poisson.
    
    lambda_local: goles esperados del equipo local (ej: 1.8)
    lambda_visitante: goles esperados del visitante (ej: 1.2)
    max_goles: máximo de goles a considerar por equipo (10 es suficiente)
    """
    ...
```

### Orden de prioridad al resolver problemas:
1. ¿Funciona? → Si no, arreglarlo primero
2. ¿Es entendible? → Si no, agregar comentarios
3. ¿Es eficiente? → Optimizar solo si hay un problema real de velocidad

---

## Gestión del bankroll (para el usuario)

El sistema recomienda apuestas, pero el usuario debe seguir estas reglas:

```
REGLA DE ORO: Nunca apostar más del 2-5% del bankroll en un pick.

Ejemplo con bankroll de $50.000 COP (~$12 USD):
- Por pick: $1.000 - $2.500 COP
- Si el sistema da 10 picks al mes con 60% de acierto:
  - Ganancia esperada: ~$5.000 - $15.000 COP/mes
  - Con bankroll de $500.000 COP → ~$50.000 - $150.000 COP/mes

Escala con disciplina, no con emoción.
```

### Mercados recomendados para empezar:
1. **Más/Menos goles (Over/Under)** — más predecible que el resultado
2. **Ambos marcan (BTTS)** — menos eficiente en las casas
3. **Handicap asiático** — elimina el empate, más opciones de valor
4. **Resultado al descanso** — ventana de análisis más pequeña

---

## Cómo usar Claude Code en este proyecto

Claude Code es una herramienta de terminal que ejecuta Claude directamente en tu computador.
Puede leer, escribir y ejecutar código sin que tengas que copiar y pegar nada.

### Instalación (cuando llegues a la Fase 1):
```bash
npm install -g @anthropic-ai/claude-code
cd mundial-predictor
claude  # Esto abre Claude Code en el proyecto
```

### Comandos útiles en Claude Code:
```bash
# Pedirle que cree un archivo nuevo
"crea el archivo modelos/dixon_coles.py con la implementación completa"

# Pedirle que explique código existente
"explícame línea por línea qué hace la función en fetcher.py"

# Pedirle que encuentre y corrija errores
"el script da este error: [pegar error], arréglalo"

# Pedirle análisis
"analiza el partido de hoy Colombia vs Argentina"
```

### La ventaja de Claude Code vs el chat:
- **Ve todos tus archivos** sin que tengas que copiarlos
- **Ejecuta el código** y ve si funciona o da error
- **Hace cambios en múltiples archivos** a la vez
- **Recuerda el contexto** del proyecto entre preguntas
- **Guarda el progreso** en la BITACORA automáticamente

---

## Glosario para el usuario

| Término | Definición simple |
|---------|------------------|
| **Value bet** | Apuesta donde TU probabilidad calculada > probabilidad que asigna la casa |
| **Cuota decimal** | Número que multiplica tu apuesta (cuota 2.50 → apuestas $10, ganas $25) |
| **Probabilidad implícita** | Lo que la casa cree que va a pasar (1 / cuota) |
| **Edge** | Tu ventaja sobre la casa en puntos porcentuales |
| **Bankroll** | Tu capital total para apuestas |
| **xG (Expected Goals)** | Goles que estadísticamente debería haber marcado un equipo |
| **Dixon-Coles** | Modelo matemático que predice cuántos goles marcará cada equipo |
| **ELO** | Sistema de puntuación que mide la fuerza actual de cada selección |
| **Poisson** | Distribución matemática que modela eventos raros (como los goles) |
| **Over/Under** | Apuesta a si habrá más o menos goles de un número dado |
| **BTTS** | "Both Teams To Score" — ambos equipos marcan al menos un gol |
| **Handicap asiático** | Cuota que da ventaja de goles a uno de los equipos |

---

*Última actualización: Junio 2026 | Proyecto iniciado durante el Mundial 2026*