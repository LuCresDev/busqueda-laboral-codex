# Contribuir a Búsqueda Laboral con Codex

Esta edición mantiene el flujo completo como skills e instrucciones de Codex.
Una contribución debe conservar la separación entre metodología pública y perfil
privado, la honestidad de las candidaturas y la verificación de documentos.

## Antes de cambiar el código

Leé `AGENTS.md` y el skill relevante. Usá fixtures genéricos o datos ficticios
claramente marcados; no incluyas CV reales, contactos, tokens ni datos de tu búsqueda.
Las plantillas compartibles viven en `templates/`; tus datos van en `profile/`.

## Validación

```sh
python -m pip install -r requirements-dev.txt
python tools/lint_skills.py
python tools/security_guards.py
python -m unittest discover -s tests -t .
```

Para una CLI de portal, corré su suite `bun test` y el typecheck correspondiente.
Las pruebas automatizadas deben usar fixtures/mocks. Las consultas reales son
puntuales y deben informar barreras de acceso sin eludirlas. Los cambios de PDF
requieren renderizado e inspección visual además de extracción de texto.

Si cambiás metodología, actualizá `framework_version` y explicá el cambio de
comportamiento. Los mapas de actualización deben comparar contra la ruta original
correcta y nunca sobrescribir perfiles. No se aceptan permisos ficticios de otro agente,
ejecución automática de scripts de dependencias ni envíos externos no solicitados.

En el PR describí el problema, el comportamiento resultante y qué verificaste.
Mantené la licencia MIT y la atribución del proyecto original.
