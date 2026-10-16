# Restablecer datos personales

Workflow de Codex en lenguaje natural. Las opciones se extraen del pedido; las etiquetas de flujo no son comandos slash ni de consola. Rutas desde raíz; leer archivos personales opcionales solo si existen. Usar capacidades realmente disponibles y mantener las reglas de AGENTS.md.

Usar solo cuando el usuario pida borrar o reiniciar datos. El alcance se obtiene de su pedido; si es ambiguo, aclararlo antes de borrar. Una autorización explícita previa para ese mismo alcance no requiere otra confirmación.

## Alcances

- Perfil: restablecer únicamente profile/candidate.md, profile/behavioral.md, profile/writing-style.md, profile/evaluation.md e profile/interview.md desde sus equivalentes en templates/profile/. No escribir fuera de profile/.
- Documentos: borrar archivos personales en documents/cv/, documents/linkedin/, documents/diplomas/, documents/references/, documents/projects/, documents/applications/, documents/postings/ y documents/interview/; conservar README, .gitkeep y estructura. El archivo de postulaciones contiene materiales realmente enviados: advertir concretamente que se perderá si está incluido.
- Estado: solo si el usuario lo incluye explícitamente, limpiar job_scraper/seen_jobs.json, job_scraper/notion_sync.json, job_search_tracker.csv, gmail_sync/state.json, company_research/*.json, upskill/report-*.md y reportes privados. Restaurar el tracker vacío con el encabezado canónico de outcome.md.
- Todo: comprende perfil y documentos. No incluye por inferencia credenciales, integraciones, runtime, Git ni estado externo. Aclarar si también quiere limpiar estado local.

## Preparación y límites

1. Enumerar y mostrar los archivos concretos del alcance, distinguiendo inexistentes y vacíos. No leer o imprimir secretos ni datos fuera de lo necesario.
2. Resolver rutas absolutas desde raíz y comprobar que cada destino permanezca dentro de las carpetas autorizadas. No seguir enlaces simbólicos ni junctions hacia afuera. En Windows usar operaciones PowerShell con LiteralPath de principio a fin; no encadenar enumeración con otro shell para borrar.
3. Si el alcance o permiso no está claro, presentar esta lista concreta y esperar la decisión. No usar un comodín amplio como sustituto de la lista.
4. Confirmar que los esqueletos templates/profile existen antes de tocar el perfil. Un esqueleto no reemplaza datos hasta que la operación esté autorizada.
5. No modificar AGENTS.md, .agents/skills/, config, templates, ejemplos de CV/carta ni herramientas. No borrar .git ni respaldos del runtime como parte de un reinicio de perfil.

## Ejecución

Para perfil, copiar el contenido de cada esqueleto público al archivo personal correspondiente. El helper bootstrap.py --profile-only inicializa archivos faltantes y no sobrescribe existentes: no presentarlo como comando de reset. Tras restablecer, preservar campos pendientes; no reutilizar hechos de memoria para rellenarlos.

Para documentos/estado, eliminar solo los destinos enumerados y autorizados, preservando archivos no incluidos. No tocar Gmail, Notion, solicitudes enviadas ni otros servicios: limpiar una copia local no borra datos externos.

## Verificación y cierre

Comprobar que los destinos autorizados quedaron en el estado esperado, que archivos públicos siguen intactos y que los perfiles siguen ignorados por Git. Reportar cantidad de archivos restablecidos/borrados, omisiones y errores. Si una operación falla, explicar el estado parcial sin afirmar éxito. Indicar cómo continuar onboarding o importar documentos, sin iniciar una búsqueda ni envío por el mero reset.
