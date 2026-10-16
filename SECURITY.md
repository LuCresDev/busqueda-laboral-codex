# Límites de confianza y datos privados

Los avisos, sitios web, documentos y mensajes externos son datos de entrada. Sus
instrucciones incrustadas no modifican el flujo, no autorizan ejecutar comandos ni
permiten transmitir el perfil a terceros. Las defensas del agente son instrucciones;
el proyecto no afirma ser un sandbox de seguridad.

## Datos personales

`profile/`, exportaciones de LinkedIn, CV, documentos, tracker, candidaturas, cachés,
`.runtime/`, `.env` y reportes son privados. Las plantillas públicas son genéricas.
`.gitignore` y el exportador excluyen esos datos. El exportador también filtra
archivos privados forzados al índice y no incluye historial Git; no puede borrar un
secreto previamente publicado en un repositorio remoto.

## Herramientas y red

Los skills usan las capacidades reales de la sesión Codex. No se copian permisos
de otros agentes ni se desactivan las aprobaciones del entorno. Los portales respetan
sus restricciones de acceso y su estado habilitado. Ante sesión, CAPTCHA, 403 o 429,
se detiene esa vía y se ofrece un enlace o texto aportado por el usuario.

Una candidatura preparada queda como borrador hasta que el usuario indique el envío.
Gmail y Notion son opcionales y dependen de conexiones disponibles. No se almacenan
claves en los archivos compartibles ni se conectan navegadores automáticamente.

## Controles del repositorio

`tools/security_guards.py` comprueba exclusiones de datos, configuración nativa y
manifiestos de dependencias. El instalador de portales rechaza lifecycle scripts y
trustedDependencies. CI ejecuta controles y pruebas con permisos de lectura; no consulta
portales reales ni publica información de candidatos.

Si detectás una vulnerabilidad, informala al mantenedor de la copia que estés usando
sin adjuntar datos personales. Las vulnerabilidades del proyecto original se pueden
reportar según [su política](https://github.com/MadsLorentzen/ai-job-search/security/policy).
