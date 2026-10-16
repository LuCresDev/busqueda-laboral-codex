# Instalación de la edición Codex

## 1. Obtener el código

Usá un fork o una copia del repositorio. Esta edición conserva el código compartible
separado del perfil personal: un clon nuevo no debe contener experiencia de su autor.
Git es necesario para las herramientas de actualización y exportación pública.

## 2. Preparar Python

Necesitás Python 3.10 o superior. Se recomienda un entorno virtual:

```sh
python -m venv .venv
```

Activá `.venv` según tu sistema (`.venv\Scripts\Activate.ps1` en PowerShell,
`source .venv/bin/activate` en Linux/macOS) y ejecutá:

```sh
python -m pip install -r requirements.txt
python tools/bootstrap.py
python tools/doctor.py
```

`bootstrap.py` crea los archivos faltantes en `profile/` y configura rutas locales
en `.runtime/runtime.local.json`. Es idempotente: no sobrescribe perfiles ni runtime
existentes. No instala software, no inicia sesión y no pide claves API.

`doctor.py` identifica dependencias necesarias y capacidades opcionales. Bun, la CLI
de Codex y Poppler pueden faltar si usás el flujo correspondiente desde la aplicación.
La generación de PDF sí requiere las dependencias declaradas en requirements.txt.

## 3. Abrir en Codex

Abrí la carpeta como proyecto en Codex. La entrada es `AGENTS.md`; los skills viven
en `.agents/skills/`. Pedí «Cargá mi CV y ayudame a configurar mi búsqueda».

Con Codex CLI instalado y autenticado:

```sh
python tools/run.py start
```

Windows incluye `ABRIR-ASISTENTE.cmd` y `iniciar.ps1`. El diagnóstico se puede ejecutar
con `powershell -NoProfile -File iniciar.ps1 -Diagnostico`. Si la política local de
PowerShell impide abrirlos, podés usar los comandos Python equivalentes o la app.

## 4. Completar el perfil

Adjuntá un CV o aportá experiencia, tecnologías, proyectos, formación e idiomas.
El sistema distingue datos desconocidos de competencias ausentes. LinkedIn puede
exigir sesión: un enlace no garantiza acceso a toda la experiencia. Un PDF exportado
o texto aportado por vos permite continuar sin compartir credenciales.

El perfil canónico es `profile/candidate.md`; evaluaciones personales, estilo y
ejemplos STAR se guardan en los demás archivos de `profile/`. La metodología y los
esqueletos `templates/profile/` son compartibles y nunca se personalizan.

## 5. Búsqueda automática opcional

Instalá Bun desde [su fuente oficial](https://bun.sh/docs/installation) si querés
usar los portales CLI. La CLI de LinkedIn está deshabilitada para el flujo predeterminado;
se usa búsqueda guiada. Los portales exclusivos de Dinamarca no se incluyen. freehire funciona sin dependencias de ejecución:

```sh
python tools/run.py search --query "backend developer" --mode remote --limit 5
```

`python tools/install_portal_clis.py --dry-run` muestra las dependencias de desarrollo
de los portales disponibles. El instalador rechaza lifecycle scripts y
trustedDependencies sin revisión. El modo web guiado no requiere Bun.

## 6. PDF

Las plantillas activas usan JSON y `tools/render_application.py`. El manifiesto de
cada plantilla documenta su esquema y comando. Nunca uses datos ficticios en un CV
personal. Los ejemplos de tests/demo no son información del candidato.

Poppler `pdftoppm` permite revisar las páginas renderizadas. `verify_pdf.py` usa pypdf
para extraer texto y revisar contactos, fechas y palabras clave. `verify_layout.py`
necesita el ejecutable opcional `pdftotext`; si devuelve `skipped` y código 2, registrá
la omisión y mantené la revisión visual. No rellenes un CV breve para ocupar dos páginas.

## 7. Integraciones y actualizaciones

Gmail y Notion se usan solo si pedís esa función y la sesión expone una conexión
adecuada. El proyecto no configura MCPs de otro agente ni conecta tu navegador.

La relación con el proyecto original está en `UPSTREAM.md`. Las actualizaciones son
revisión de diferencias metodológicas; nunca reemplazan automáticamente `profile/`.
Antes de publicar una adaptación, corré controles y exportá el paquete público.
