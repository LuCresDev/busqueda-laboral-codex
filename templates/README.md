# Plantillas de documentos y perfil

Las plantillas activas son JSON y generan PDF con Python, ReportLab y pypdf. La selección técnica vive en config/argentina.json:

| Documento | Esqueleto activo | Instrucciones | Límite |
|---|---|---|---|
| CV | cv/argentina-ats/template.json | cv/argentina-ats/TEMPLATE.md | 1–2 páginas |
| Carta | cover_letters/argentina-simple/template.json | cover_letters/argentina-simple/TEMPLATE.md | 1 página |

Las rutas de la tabla parten de esta carpeta. Los comandos se ejecutan desde la raíz del repositorio. No se necesita LaTeX para estas plantillas.

## Uso desde la conversación

Pedí «adaptá mi CV a esta oferta» o «prepará la postulación». Codex lee el perfil confirmado, el manifiesto y las guías compartidas; crea una fuente específica en cv/ o cover_letters/ y genera su PDF. Una plantilla con placeholders no es un documento personal ni una fuente de hechos.

Ejemplos de los comandos que usa el flujo sobre archivos ya completados con datos reales:

    .\herramientas.ps1 -Accion python -Argumentos @('tools/render_application.py', '--kind', 'cv', '--input', 'cv/main_<empresa>_<rol>.json', '--output', 'cv/main_<empresa>_<rol>.pdf')
    .\herramientas.ps1 -Accion python -Argumentos @('tools/render_application.py', '--kind', 'cover', '--input', 'cover_letters/cover_<empresa>_<rol>.json', '--output', 'cover_letters/cover_<empresa>_<rol>.pdf')

Reemplazar los marcadores de ruta antes de ejecutar. Las fuentes específicas y los PDF son privados; no se guardan datos personales en template.json. Inspeccionar visualmente todas las páginas y extraer texto para comprobar contacto, orden y palabras clave ATS. Un error de render no convierte un PDF anterior en resultado nuevo.

## Registrar o cambiar una plantilla

Pedí «mostrame las plantillas», «registrá esta plantilla de CV» o «usá la plantilla argentina-ats». El workflow .agents/skills/argentina-job-search/references/workflows/add-template.md describe registro, prueba y activación; son pedidos en lenguaje natural, no comandos slash.

Una plantilla registrada incluye:

    templates/
    ├── cv/<nombre>/
    │   ├── template.<ext>   # Esqueleto genérico sin biografía
    │   ├── TEMPLATE.md      # Contrato, renderer, fuentes y límites
    │   └── recursos/        # Solo si el formato los necesita
    ├── cover_letters/<nombre>/
    │   └── ...
    └── profile/             # Esqueletos personales genéricos para bootstrap

Antes de activar una plantilla nueva hay una prueba de render con datos explícitamente ficticios. Su manifiesto declara extensión, comando, directorio de ejecución, dependencias, fuentes y presupuesto de páginas. La selección en config y el bloque activo de las guías 05/06 deben coincidir. Pedir «volver a las predeterminadas» selecciona las plantillas JSON argentinas.

## Compatibilidad opcional

Los ejemplos cv/main_example.tex y cover_letters/cover_example.tex, junto con cover_letters/cover.cls, se conservan como referencias históricas y pruebas de compatibilidad. Esas rutas parten de la raíz. No son el formato predeterminado ni un CV del candidato.

Una plantilla LaTeX, Typst u otro formato solo se usa si fue seleccionada explícitamente y su manifiesto declara las herramientas disponibles. Los ejemplos antiguos no habilitan una instalación automática ni reemplazan el perfil.

## Esqueletos de perfil

templates/profile/ contiene candidate.md, behavioral.md, writing-style.md, evaluation.md e interview.md genéricos. El bootstrap copia únicamente los faltantes a profile/ y no sobrescribe datos existentes. La personalización ocurre en profile/, local y privado; las reglas de los skills y estos esqueletos públicos conservan sus placeholders o campos pendientes.
