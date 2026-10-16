---
name: argentina-job-search
description: Gestiona la búsqueda laboral del candidato en Argentina desde lenguaje natural. Use for job search, profile onboarding, ranking, applications, CVs, cover letters, interviews and application tracking in this repository, not for implementing its software.
metadata:
  framework_version: '2.1.0'
  kind: workflow
  market: AR
---

# Búsqueda laboral con Codex

Leé AGENTS.md, config/argentina.json y profile/candidate.md cuando la tarea necesite el perfil. Esta es la entrada nativa del flujo. Las rutas del cuerpo se resuelven desde la raíz del repositorio; los enlaces Markdown de este archivo son relativos al skill. No mantiene biografía ni implementa una CLI de portal.

## Selección por intención

| Pedido | Recurso a leer |
|---|---|
| Cargar o actualizar perfil, importar CV, empezar | [onboarding](references/workflows/setup.md) |
| Buscar nuevas vacantes | .agents/skills/job-scraper/SKILL.md |
| Ordenar y priorizar vacantes | [ranking](references/workflows/rank.md) |
| Evaluar una oferta, adaptar solo CV o carta | .agents/skills/job-application-assistant/SKILL.md |
| Preparar una postulación completa | [postulación](references/workflows/apply.md) |
| Preparar entrevista o practicar | [entrevista](references/workflows/interview.md) |
| Registrar envío, entrevista, oferta, rechazo o seguimiento | [seguimiento](references/workflows/outcome.md) |
| Ver pipeline en un tablero offline | [informe HTML](references/workflows/html-report.md) |
| Plan de aprendizaje según brechas | .agents/skills/upskill/SKILL.md |
| Ampliar perfil con fuentes públicas propias | [ampliar perfil](references/workflows/expand.md) |
| Registrar o elegir plantilla | [plantillas](references/workflows/add-template.md) |
| Investigar o agregar portal | [portales](references/workflows/add-portal.md) |
| Leer señales de Gmail, pedido explícito | [Gmail opcional](references/workflows/gmail-sync.md) |
| Publicar seguimiento en Notion, pedido explícito | [Notion opcional](references/workflows/notion-sync.md) |
| Restablecer datos, alcance explícito | [restablecimiento](references/workflows/reset.md) |

Son intenciones expresadas en la conversación, no comandos de consola o slash. Los parámetros mencionados por un workflow se extraen del pedido; no se exige una sintaxis especial al usuario.

## Perfil y evidencia

La biografía y los datos de contacto provienen solo de profile/candidate.md. profile/behavioral.md, writing-style.md, evaluation.md e interview.md son recursos personales opcionales; las reglas y metodologías compartidas viven en los otros skills. Si falta un perfil, seguí onboarding o inicializá con tools/bootstrap.py --profile-only desde raíz. No edites plantillas públicas para personalizarlo.

Campos vacíos, pendientes y placeholders significan desconocido. Usá el alcance confirmado para una búsqueda amplia sin bloquearla por detalles irrelevantes como ciudad para remoto. Señalá tecnologías, seniority, experiencia e idiomas que falten antes de atribuir ajuste personal definitivo. No inferir español laboral ni inglés por el idioma de conversación. Ninguna oferta o perfil público confirma autorización laboral del candidato.

Los nuevos hechos confirmados se registran en profile/candidate.md con su fuente. Los conflictos entre fuentes se aclaran con el usuario. Las observaciones de estilo, calibración y STAR van a sus archivos personales, nunca a metodología o plantillas compartidas. Un CV anterior sirve de estructura; no prueba hechos nuevos.

## Mercado y capacidades reales

Conversación en español, documentos en español por defecto editable, fechas en America/Argentina/Buenos_Aires según config. Consultá [fuentes y límites](references/portales.md) y config/portales-argentina.json al buscar. Los portales CLI se descubren solo si tienen cli/src/cli.ts y están habilitados; este skill es de workflow y no se ejecuta como portal. No inventes flags.

Usá las herramientas realmente ofrecidas por la sesión de Codex: archivos y shell para operaciones locales, búsqueda web/lector para fuentes públicas, navegador solo si está conectado, subagentes si están disponibles. El repositorio no instala esas capacidades. Si falta alguna, explicá la limitación y conservá un resultado honesto; nunca afirmes haber navegado, revisado o verificado algo que no ejecutaste.

En Windows, desde raíz:

    .\herramientas.ps1 -Accion doctor
    .\herramientas.ps1 -Accion portales
    .\herramientas.ps1 -Accion buscar -Consulta "<puesto confirmado>" -Fuente freehire -Ubicacion Argentina -Modalidad remoto
    .\herramientas.ps1 -Accion python -Argumentos @('tools/verify_pdf.py', '<archivo.pdf>')

El ejemplo de modalidad se adapta al perfil confirmado. freehire cubre tecnología y filtra Argentina; las fuentes generales y los filtros de ciudad se cubren por búsqueda guiada. LinkedIn usa buscador y apertura manual. Un empleo LATAM/global necesita evidencia de admisión desde Argentina, contratación y horario. No dar por confirmado lo que el aviso omite.

## Documentos y cierre

Para postulación completa, mantené la evaluación y el flujo drafter/reviewer. El revisor es un subagente de Codex definido por .agents/skills/job-application-assistant/references/reviewer.md, sin otra CLI. Si no hay subagentes, identificá la revisión propia y la limitación antes de presentar el resultado; no la llames independiente. El ranking usa puntuadores cuando corresponde y no requiere revisor de documentos.

Seguí la plantilla activa de config y las guías 05/06; JSON se renderiza con tools/render_application.py, CV de 1–2 páginas y carta de 1. Inspeccioná todas las páginas y extraé texto ATS con tools/verify_pdf.py. No usar un PDF viejo tras error de render. Registros y archivo siguen el contrato del workflow: drafted significa borrador; applied requiere el envío real comunicado por el usuario.

No enviar solicitudes, mensajes o documentos al preparar materiales. Gmail y Notion requieren pedido explícito y capacidades conectadas; sin ellas, explicar la conexión faltante y ofrecer el flujo local, sin instalar o autenticar por cuenta propia.
