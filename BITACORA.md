# BITACORA.md — Diario del Proyecto Mundial Predictor

> Registro cronológico de todo lo que se construye, aprende y decide.
> Actualizar al final de cada sesión de trabajo.
> Este archivo es tu memoria del proyecto.

---

## ¿Para qué sirve esta bitácora?

1. **Recordar qué hiciste** cuando vuelves después de días sin tocar el proyecto
2. **Aprender de los errores** — los problemas resueltos aquí no se repiten
3. **Ver el progreso** — motiva ver cuánto has avanzado
4. **Documentar decisiones** — por qué se hizo algo de cierta manera

---

## SESIÓN 001 — Junio 2026
**Estado:** Conceptualización y planificación
**Duración:** ~2 horas de conversación con Claude

### ¿Qué hicimos?
- Exploramos la viabilidad de crear un sistema de análisis de apuestas deportivas
- Investigamos el modelo de Joachim Klement (matemático alemán que predijo los últimos 3 mundiales)
- Estudiamos el modelo Dixon-Coles y cómo funciona matemáticamente
- Investigamos las APIs disponibles para datos del Mundial 2026
- Conocimos Claude Fable 5 y Opus 4.8 (modelos nuevos de Anthropic)
- Creamos la estructura de documentación del proyecto

### ¿Qué aprendimos?

**Sobre el modelo Klement:**
- Usa variables macro: ranking FIFA, PIB per cápita, población, cultura futbolística
- Predijo correctamente: Alemania 2014, Francia 2018, Argentina 2022
- Para 2026 predice que ganará Países Bajos
- Él mismo advierte que NO se use para apostar (ironía: nosotros igual lo vamos a usar como base)
- Su utilidad para nosotros: establecer el "peso base" de cada selección

**Sobre Dixon-Coles:**
- Es el modelo estándar de la industria para predicción de fútbol
- Basado en distribución de Poisson (modela eventos raros = goles)
- Mejora sobre Poisson simple: corrige subestimación de empates
- Agrega peso temporal: partidos recientes pesan más que viejos

**Sobre value betting:**
- No se trata de predecir quién gana — se trata de encontrar cuotas mal puestas
- Si el modelo dice 40% de probabilidad pero la cuota implica 33%, ahí hay valor
- A largo plazo, apostar sistemáticamente con edge positivo = rentabilidad

**Sobre las APIs:**
- football-data.org: gratis, bueno para empezar
- The Odds API: 500 requests gratis/mes, perfecta para cuotas
- TheStatsAPI: $50/mes, tiene xG en tiempo real (para fase avanzada)

**Sobre Claude Code:**
- Es una herramienta de terminal que ejecuta Claude directamente en el proyecto
- Ve todos los archivos, ejecuta código, hace cambios en múltiples archivos
- Ventaja enorme vs chat: no hay que copiar y pegar código
- Comando para instalar: `npm install -g @anthropic-ai/claude-code`

**Sobre los modelos de Claude:**
- Opus 4.8: lanzado 28 mayo 2026, mejoras en razonamiento y tareas agénticas
- Fable 5: lanzado 9 junio 2026, el más potente disponible al público
- Para este proyecto: Sonnet 4.6 es suficiente para el día a día, Opus para análisis complejos

### ¿Qué decidimos?
- Arquitectura: terminal primero → Telegram después → Dashboard web
- Modelos a implementar: Dixon-Coles + ELO + variables Klement + detector de value
- Lenguaje: Python (más librerías estadísticas, más tutoriales disponibles)
- Empezar con APIs gratuitas, escalar a de pago cuando haya ingresos
- Documentar TODO para aprender mientras se construye

### ¿Qué falta por hacer?
- [ ] Instalar Python y dependencias
- [ ] Crear cuenta en football-data.org y obtener API key
- [ ] Crear cuenta en The Odds API y obtener API key
- [ ] Implementar el fetcher de datos básico
- [ ] Implementar Dixon-Coles v1
- [ ] Hacer primera prueba con partidos reales del Mundial 2026

### Errores y problemas encontrados
*Ninguno aún — proyecto en fase de planificación*

### Notas personales
> El proyecto tiene potencial real. La clave está en la disciplina:
> - Apostar solo cuando hay edge real (>3%)
> - No dejarse llevar por "corazonadas"
> - Mantener registro de todos los picks para medir el rendimiento
> El sueño: un domingo, correr el programa, analizar los partidos del día,
> apostar $20.000 COP estratégicamente y ganar $60.000-$100.000 COP.
> A escala: con bankroll de $2.000.000 COP y disciplina, posible sustento mensual.

---

## SESIÓN 002 — 16 de junio 2026
**Estado:** Completada
**Duración:** ~1.5 horas
**Objetivo de la sesión:** Instalar entorno virtual, crear config/settings.py y data/fetcher.py, y hacer el primer llamado real a la API de football-data.org.

### Commits realizados hoy
- `chore(deps): crear entorno virtual e instalar dependencias base` — venv + 6 librerías
- `feat(config): agregar settings.py que carga API keys desde .env` — configuración global
- `feat(fetcher): conectar football-data.org y obtener partidos del Mundial 2026` — primer dato real
- `docs(bitacora): documentar sesión 002 - entorno y primera conexión a API`

### ¿Qué hicimos?
- Creamos el entorno virtual (`venv`) — la "caja aislada" donde viven las librerías del proyecto
- Instalamos las 6 librerías base: `requests`, `scipy`, `numpy`, `pandas`, `python-dotenv`, `colorama`
- Creamos `requirements.txt` para que cualquiera pueda reinstalar todo con un comando
- Creamos todas las carpetas del proyecto: `config/`, `data/cache/`, `data/historico/`, `modelos/`, `analisis/`, `tests/`
- Escribimos `config/settings.py`: carga las API keys del `.env`, define rutas del proyecto, incluye función `verificar_configuracion()` y parámetros del sistema (EDGE_MINIMO, KELLY_FRACCION, etc.)
- Escribimos `data/fetcher.py`: se conecta a football-data.org, descarga partidos del Mundial 2026, convierte horas de UTC a hora colombiana (COT = UTC-5), ordena por hora y guarda caché en disco
- Hicimos la primera prueba real con datos del Mundial 2026 del día de hoy (2026-06-16):
  ```
  14:00 COT → France vs Senegal   [IN_PLAY]
  17:00 COT → Iraq vs Norway      [TIMED]
  20:00 COT → Iran vs New Zealand [FINISHED]
  ```
- Verificamos que `.env`, `venv/` y `data/cache/` están correctamente ignorados por Git

### ¿Qué aprendimos?

**Sobre Python:**
- **Entorno virtual**: `python -m venv venv` crea una carpeta donde se instalan librerías solo para este proyecto, sin tocar el Python del sistema. Así dos proyectos distintos pueden tener versiones distintas de la misma librería sin conflictos.
- **`sys.path`**: Python busca módulos solo en ciertas carpetas. Cuando un script está en `data/` no ve los módulos de `config/`. Se soluciona agregando la raíz al path: `sys.path.insert(0, str(BASE_DIR))`.
- **`python-dotenv`**: la librería `load_dotenv()` lee el archivo `.env` y mete sus variables en la memoria del programa. Después `os.getenv("NOMBRE")` las lee. El archivo `.env` nunca se sube a Git.
- **Caché con JSON**: guardar la respuesta de la API en un archivo `.json` local permite que la segunda ejecución sea instantánea y no gaste cuota. Si el archivo existe → leerlo; si no → llamar a la API y guardarlo.
- **`raise_for_status()`**: con `requests`, una respuesta HTTP 403 o 429 no lanza error automáticamente — hay que llamar este método para que se convierta en una excepción capturablee con `try/except`.

**Sobre Git:**
- `git check-ignore ARCHIVO` muestra si un archivo está siendo ignorado por `.gitignore`. Muy útil para verificar que los secretos y la caché nunca se suban accidentalmente.

**Sobre Python en Windows:**
- La terminal de Windows usa codificación `cp1252` por defecto y no puede mostrar emojis ni algunos caracteres (✅, ⚽). Se soluciona con `sys.stdout.reconfigure(encoding="utf-8")` al inicio del programa.

### Errores encontrados y cómo se resolvieron

| Error | Causa | Solución |
|-------|-------|----------|
| `UnicodeEncodeError: 'charmap' codec can't encode character '✅'` | La consola de Windows usa `cp1252` que no soporta emojis | Se agregó `sys.stdout.reconfigure(encoding="utf-8")` en `settings.py`, que todos los módulos importan |
| El `.env` no existía en la ruta esperada | Yo intenté crearlo en `config/.env` pero el usuario ya lo tenía en la raíz (`files/.env`) | Se ajustó `settings.py` para apuntar a `BASE_DIR / ".env"` en vez de `CONFIG_DIR / ".env"` |
| Partidos aparecían desordenados en consola (20:00, 14:00, 17:00) | La API no garantiza orden cronológico | Se agregó `sorted(partidos, key=lambda p: p["hora_cot"])` en `mostrar_partidos()` |

### ¿Qué falta para la próxima sesión?
- [ ] Paso 1.3: implementar `modelos/elo.py` con los ratings iniciales de las 48 selecciones y la fórmula de actualización
- [ ] Paso 1.3: probar predicción ELO para un partido: España vs Alemania → ¿quién tiene más probabilidad?
- [ ] Complementar `fetcher.py` con la función de cuotas (The Odds API) — quedó pendiente del Paso 1.2

### Picks analizados hoy
*Ninguno — el sistema aún no tiene modelo de predicción implementado*

---

## 📋 Template para nuevas sesiones
*(Copia esto cada vez que empieces a trabajar)*

```markdown
## SESIÓN 00X — Fecha
**Estado:** En progreso / Completada
**Duración:** X horas
**Objetivo de la sesión:** ...

### Commits realizados hoy
- `tipo(scope): descripción` — qué se logró

### ¿Qué hicimos?
- 

### ¿Qué aprendimos?
**Sobre Python:**
- 

**Sobre el modelo / estadística:**
- 

**Sobre Git:**
- 

**Sobre apuestas:**
- 

### Errores encontrados y cómo se resolvieron
| Error | Causa | Solución |
|-------|-------|----------|
| | | |

### ¿Qué falta para la próxima sesión?
- [ ] 

### Picks analizados hoy (si los hay)
| Partido | Mercado | Edge | Aposté | Resultado |
|---------|---------|------|--------|-----------|
| | | | | |
```

---

## Registro de picks realizados

> Una vez que el sistema esté funcionando, registrar TODOS los picks aquí.
> Esto es crucial para medir si el sistema realmente funciona.

| Fecha | Partido | Mercado | Cuota | Stake | Resultado | P/L |
|-------|---------|---------|-------|-------|-----------|-----|
| -     | -       | -       | -     | -     | -         | -   |

**Total invertido:** $0
**Total retornado:** $0
**ROI:** 0%
**Picks ganados:** 0/0

---

## Lecciones aprendidas (acumuladas)

### Sobre matemáticas y estadística
*(Se irá llenando)*

### Sobre programación en Python
*(Se irá llenando)*

### Sobre apuestas deportivas
- Las casas incluyen un margen (overround) de ~5-10% en sus cuotas
- Por eso apostar al azar siempre pierde a largo plazo
- La única forma de ganar es encontrar cuotas donde el margen está mal calculado
- Los mercados alternativos (corners, tarjetas, BTTS) son menos eficientes que 1X2

### Sobre Claude Code
*(Se irá llenando)*

---

*Bitácora iniciada: Junio 2026*
*Proyecto: Mundial Predictor → Sistema de Value Betting*
*Ubicación: Medellín, Colombia*
