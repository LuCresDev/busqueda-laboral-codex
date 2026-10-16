---
name: job-application-assistant
description: Evalúa ofertas, adapta CV y cartas y prepara entrevistas con datos confirmados del candidato. Use for job fit evaluation, truthful CV tailoring, cover letters and interview preparation in this repository.
metadata:
  framework_version: '2.1.0'
  kind: workflow
---

# Asistente de postulaciones

Todas las rutas son relativas a la raíz del repo. Leé profile/candidate.md como única fuente biográfica y AGENTS.md para las convenciones de Codex. Los archivos personales opcionales se consultan solo si existen; su ausencia no es evidencia de rasgos o habilidades.

Cuando el usuario quiera una postulación completa, seguí .agents/skills/argentina-job-search/references/workflows/apply.md. Ese workflow es la única definición de la secuencia evaluación, borradores, revisor, revisión, PDF/ATS y registro. No mantengas otra versión abreviada que omita revisión o registro.

Para pedidos parciales, hacé solamente lo solicitado:
- Evaluar oferta: recuperar texto real según 09, aplicar 04 y mostrar coincidencias, brechas, logística, idioma y elegibilidad. Con perfil incompleto, evaluación provisional sin notas inventadas.
- Solo CV: aplicar 05 y 03, datos confirmados, plantilla activa, render e inspección/ATS del documento.
- Solo carta: aplicar 06 y 03, empresa verificada, plantilla activa y render/inspección.
- Entrevista: leer el workflow de entrevista y 07. Usar documentos realmente enviados y STAR personales, sin inventarlos.
- Estrategia: usar preferencias confirmadas de profile/candidate.md y profile/evaluation.md con las reglas de 04.

Un solo documento no se registra como postulación completa. Si se generan CV y carta juntos, el registro drafted y el archivo siguen la sección de registro de apply.md; no añadir una segunda fila desde este skill. Enviar es otra acción explícita.

## Referencias compartidas

| Archivo de este directorio | Uso |
|---|---|
| 03-writing-style.md | Escritura y adaptación a idiomas |
| 04-job-evaluation.md | Gates, dimensiones, pesos y criterios de evaluación |
| 05-cv-templates.md | Plantilla activa y adaptación del CV |
| 06-cover-letter-templates.md | Plantilla activa y carta |
| 07-interview-prep.md | STAR, preguntas y simulación |
| 08-application-forms.md | Campos de formulario y límites de texto |
| 09-web-research.md | Fuentes, acceso y límites de confianza |
| references/reviewer.md | Revisión de contenido por subagente Codex |

La biografía no vive en estos archivos. Las preferencias individuales, calibración y ejemplos de entrevista viven en profile/ y los borradores en sus carpetas privadas. Nunca personalices las referencias compartidas durante onboarding.
