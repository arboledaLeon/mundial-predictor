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

## SESIÓN 002 — (próxima sesión)
**Estado:** Pendiente
**Objetivo:** Instalar entorno y hacer primer llamado a API

*(Aquí documentarás lo que pase en la próxima sesión)*

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
