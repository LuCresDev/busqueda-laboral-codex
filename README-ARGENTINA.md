# Uso para Argentina y trabajo remoto

Esta edición funciona desde Codex mediante `AGENTS.md` y `.agents/skills/`.
Los datos personales viven en `profile/`; el código compartible no depende de otros
agentes ni de sus archivos de configuración.

Para empezar en un clon nuevo:

```sh
python -m pip install -r requirements.txt
python tools/bootstrap.py
python tools/doctor.py
```

Abrí esta carpeta en Codex o usá `ABRIR-ASISTENTE.cmd` en Windows. Podés seguir
en el chat donde se preparó la instalación. Ejemplos:

- «Cargá mi CV y confirmá lo que falta».
- «Buscame trabajo remoto de programación compatible con mi experiencia».
- «Evaluá esta oferta».
- «Prepará mi postulación y dejala como borrador».
- «Tengo entrevista para este puesto».
- «Ya envié la postulación; registrala».

El mercado predeterminado es Argentina y el idioma de conversación es español.
Eso no demuestra residencia, autorización laboral, idiomas profesionales ni experiencia.
Las preferencias reales de cada persona se completan en el perfil privado.

Bumeran, ZonaJobs, Computrabajo, Get on Board, LinkedIn y AMIA están documentados
para búsqueda guiada. freehire aporta consultas automáticas de tecnología. Algunos
portales exigen sesión o bloquean acceso automático; se conserva el enlace y se puede
usar el texto que aportes. No hay un scraper argentino universal.

Los remotos LATAM, globales o para Américas requieren verificar países aceptados,
contratación y franja horaria. Los requisitos no confirmados quedan pendientes.

En esta instalación Windows también podés ejecutar:

```powershell
.\herramientas.ps1 -Accion doctor
.\herramientas.ps1 -Accion buscar -Consulta "software engineer" -Modalidad remoto -Limite 5
```

Un resultado de búsqueda no es una recomendación personalizada hasta completar el
perfil. La preparación de documentos no los envía a empresas. Las plantillas generan
CV de una o dos páginas y carta de una, con texto extraíble y revisión visual.

Para compartir únicamente el código, usá `tools/export_public.py`. El perfil, el
LinkedIn personal, las postulaciones, los PDF y el runtime quedan fuera del paquete.
