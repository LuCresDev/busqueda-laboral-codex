# Búsqueda Laboral con Codex

Un asistente de búsqueda laboral que funciona dentro de Codex. Evalúa ofertas,
prepara CV y cartas, ayuda con entrevistas y mantiene el seguimiento en archivos
locales. Esta edición incluye fuentes para Argentina y oportunidades remotas LATAM.

Nombre del repositorio de esta edición: `busqueda-laboral-codex`.

Adaptación independiente de [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search),
distribuida bajo su licencia MIT. Conserva la metodología de evaluación y revisión,
y usa instrucciones `AGENTS.md` y skills nativos en `.agents/skills/`.
Las fuentes incluidas conservan sus licencias y avisos en
[atribuciones de terceros](THIRD_PARTY_NOTICES.md).

## Inicio rápido

Requisitos: Codex (aplicación o CLI), Python 3.10 o superior y Git. Bun es opcional
para la consulta automática de portales; la búsqueda web guiada también funciona.

```sh
python -m pip install -r requirements.txt
python tools/bootstrap.py
python tools/doctor.py
```

Abrí esta carpeta en Codex y pedí: **«Quiero completar mi perfil y buscar trabajo
remoto para Argentina»**. Si usás la CLI:

```sh
codex --cd . --search
```

En Windows también podés usar `ABRIR-ASISTENTE.cmd` después del bootstrap.
La documentación oficial describe [skills](https://learn.chatgpt.com/docs/build-skills)
y [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Cómo se usa

| Pedido a Codex | Resultado |
|---|---|
| «Cargá mi CV» | Perfil verificable, con preguntas sobre lo que falte |
| «Buscame trabajo remoto» | Ofertas con fuente, fecha y elegibilidad por verificar |
| «Ordená estas ofertas» | Evaluación de afinidad basada en tu experiencia real |
| «Prepará una postulación» | CV y carta revisados, PDF y registro como borrador |
| «Tengo entrevista» | Preparación por etapa y simulación con ejemplos reales |
| «Ya postulé / me llamaron / me rechazaron» | Actualización del seguimiento |
| «Qué me falta aprender» | Brechas y plan de aprendizaje con fuentes |
| «Mostrame el estado» | Panel HTML local del seguimiento |

Los workflows son recursos internos del skill; no requieren comandos slash de otro
agente. Las integraciones Gmail y Notion son opcionales y dependen de herramientas
conectadas disponibles. El proyecto no conecta una sesión de Chrome por sí mismo.

## Qué incluye

- Perfil privado separado del código y de las plantillas compartibles.
- Fuentes y ejemplos orientados a Argentina y trabajo remoto; no se incluyen portales exclusivos de Dinamarca.
- Evaluación previa y revisión independiente al preparar candidaturas cuando la
  sesión dispone de subagentes. La ausencia de esa capacidad se informa.
- Plantillas JSON con PDF de una o dos páginas para CV y una para carta, fuentes
  Unicode, capa de texto y comprobación de contactos y palabras clave. No requiere LaTeX.
- Consulta tecnológica en freehire y búsqueda guiada en Bumeran, ZonaJobs,
  Computrabajo, Get on Board, LinkedIn y AMIA. No se prometen scrapers propios de
  todos esos sitios; cada aviso requiere verificar vigencia y acceso.
- Registro CSV, archivo de materiales, deduplicación, entrevistas, seguimiento,
  análisis de brechas y herramientas de actualización de metodología.

Consulta automática de ejemplo, sin puntuar afinidad personal:

```sh
python tools/run.py search --query "software engineer" --mode remote --limit 5
```

freehire cubre principalmente tecnología. Los filtros LATAM/remoto no garantizan
que una empresa contrate desde Argentina; Codex debe comprobar el aviso real.

## Compartir el proyecto

`profile/`, documentos personales, candidaturas, tracker, cachés, `.runtime/` y
credenciales quedan fuera del código compartible. El bootstrap crea tu perfil local
desde `templates/profile/` y preserva los archivos existentes. No incluyas un CV real
en un fork público. Para generar un paquete de código revisable:

```sh
python tools/export_public.py --output ../busqueda-laboral-codex.zip
```

El exportador filtra archivos privados incluso si fueron añadidos al índice Git,
genera un manifiesto SHA-256 y no incluye historial Git. Un fork de GitHub conserva
su propio historial; revisá los cambios antes de publicar.

## Estructura

```text
AGENTS.md                 Instrucciones para Codex
.agents/skills/           Skills, metodología y workflows nativos
templates/profile/        Esqueletos genéricos de perfil
profile/                  Datos personales locales (ignorado por Git)
templates/                Plantillas de documentos
tools/                    Inicio, diagnóstico, búsqueda, PDF y controles
config/                   Mercado y fuentes de empleo
documents/                Materiales personales y archivo de postulaciones
tests/                    Pruebas de herramientas y contratos
```

Guías: [instalación](SETUP.md), [uso en Argentina](README-ARGENTINA.md),
[contribuciones](CONTRIBUTING.md), [límites de confianza](SECURITY.md),
[atribución y migración](UPSTREAM.md).

## Validación

```sh
python -m pip install -r requirements-dev.txt
python tools/lint_skills.py
python tools/security_guards.py
python -m unittest discover -s tests -t .
```

Las pruebas de CLI usan respuestas simuladas; las consultas reales son puntuales y
se realizan localmente. Los PDF se verifican por páginas, extracción de texto y
revisión visual. El resultado de cada ejecución debe describir lo que efectivamente
se comprobó, incluidas capacidades opcionales ausentes.

Este proyecto es independiente y no está afiliado a OpenAI ni al mantenedor original.
