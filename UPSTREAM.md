# Origen y edición Codex

Esta edición deriva de [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search),
revisión base `407dc34`, consultada el 15 de octubre de 2026. La licencia MIT original
se conserva íntegra en `LICENSE`, incluido el copyright de Mads Lorentzen.

## Cambios de esta edición

- Runtime y descubrimiento mediante Codex, `AGENTS.md` y `.agents/skills/`.
- Flujos de perfil, búsqueda, ranking, postulación, entrevistas, seguimiento,
  aprendizaje e integraciones opcionales adaptados a capacidades reales de Codex.
- Perfil privado en `profile/`, separado de metodología y plantillas compartibles.
- Fuentes argentinas y remoto LATAM, con comprobación de elegibilidad.
- PDF a partir de JSON con ReportLab, Unicode, extracción y revisión visual.
- Bootstrap portable, diagnóstico, runner, controles, pruebas y exportación pública.

El original utiliza Claude Code. La historia de `CHANGELOG.md` y el mapa de revisión
upstream conservan nombres/rutas históricas para atribución y comparación; no son
dependencias de ejecución de esta edición. No se conserva una configuración de
permisos de ese runtime.

## Revisar actualizaciones

`tools/check_upstream_updates.py` compara diferencias mediante un mapa explícito de
rutas nativas a rutas históricas. Su función es informar cambios para revisión. No
aplica merges ni reemplaza perfiles, documentos o candidaturas. Si una ruta local
esperada falta, debe reportarlo en vez de declarar la comparación aprobada.

No se promete soporte del mantenedor original para esta adaptación. Las decisiones
y problemas de esta edición corresponden al repositorio que la publique.

## Ajustes de mercado de esta edición

El producto se llama Búsqueda Laboral con Codex (`busqueda-laboral-codex`). Se retiraron
los cuatro portales exclusivos de Dinamarca. Los ejemplos de uso, datos salariales y
pautas culturales se adaptan a Argentina y remoto; las pruebas Unicode conservan
casos internacionales para comprobar compatibilidad, sin convertirlos en preferencias
del candidato. La licencia y la atribución originales permanecen intactas.
