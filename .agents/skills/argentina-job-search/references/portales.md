# Portales de empleo para Argentina

Verificación: **15 de octubre de 2026**. Configuración legible por herramientas: `config/portales-argentina.json`.

Este skill es un **workflow de búsqueda guiada**, sin CLI de portal. No implementa un scraper ni expone comandos `search`/`fetch`. No registrarlo como scraper ejecutable en el descubrimiento de portales. Los CLIs originales del repositorio conservan sus mercados originales; este catálogo no los convierte en conectores argentinos.

## Selección inicial

| Fuente | Para qué usarla | Entrada pública | Acceso comprobado y límite |
|---|---|---|---|
| Bumeran Argentina | Búsqueda general por puesto y ubicación | [Listado](https://www.bumeran.com.ar/empleos.html) | Avisos actuales indexados. Fetch web: 429. HTTP puntual: 200, sin validar renderizado. |
| ZonaJobs | Búsqueda general, provincias y modalidades | [Listado](https://www.zonajobs.com.ar/empleos.html) | Inicio indexado con filtros. Fetch web: 429. HTTP puntual: 200, sin validar renderizado. |
| Computrabajo Argentina | Puestos generales, operativos y profesionales | [Ofertas](https://ar.computrabajo.com/ofertas-de-trabajo/) | Inicio web pidió JS/verificación antirobot. Listado puntual HTTP 200. |
| LinkedIn | Puestos profesionales y remotos | [Argentina](https://ar.linkedin.com/jobs/search?location=Argentina) | Resultados públicos indexados. Usar descubrimiento en buscador y apertura manual por el usuario. |
| Get on Board | Tecnología y puestos relacionados | [Argentina y remotos](https://www.getonbrd.com.ar/) | Inicio y categoría leídos con herramienta web. Revisar admisión desde Argentina en cada remoto. |
| Servicio de Empleo AMIA | Empleos locales y apoyo a la búsqueda | [Buscá empleo](https://empleos.amia.org.ar/busco-empleo/empleos/) | Inicio y enlace comprobados; listado HTTP 200 y un timeout de fetch web. Registro de CV para postular. |

Son seis opciones disponibles, sin asumir el oficio, experiencia o ciudad del candidato. Elegir las relevantes al completar el perfil; no ejecutar seis búsquedas para todos los puestos por defecto. No conservar cantidades de vacantes como garantía de cobertura: cambian a diario.

## Método de búsqueda

1. Tomar puesto, experiencia, ciudad/provincia, radio y modalidad del perfil confirmado. Sin perfil, preparar consultas o pedir esos datos; no inventarlos.
2. Generar variantes en español e inglés cuando el rubro lo requiera. Ejemplos: `"analista de datos"`, `"data analyst"`, `"administrativo"`, `"administrative assistant"`.
3. Usar las consultas `site:` del JSON en una herramienta de búsqueda web disponible. Reemplazar `{role}` y `{location}` con texto; no enviar nombre, teléfono, DNI, correo ni CV al buscador. Si ubicación no aplica, omitir ese término en lugar de dejar el placeholder.
4. Abrir el aviso público para confirmar datos cuando el sitio y su política lo permitan. Para LinkedIn, entregar el enlace para apertura manual o analizar el texto que aporte el usuario. Ante login, CAPTCHA, 403, 429 o barrera equivalente, detener ese acceso y registrar la limitación.
5. Guardar URL original, título, empresa, ubicación, modalidad, fecha de publicación si aparece y fecha de consulta. No inventar sueldo ni fecha. Un snippet o un HTTP 200 por sí solos no prueban que la vacante siga abierta.
6. Deduplicar por URL canónica y por empresa + puesto + ubicación. Un aviso en Bumeran y ZonaJobs puede ser el mismo. Priorizar, si existe, la página de empleo de la propia empresa para confirmar vigencia.
7. Para remoto internacional, comprobar que acepte trabajar desde Argentina; distinguir relación de dependencia de contractor/monotributo, moneda ARS/USD, bruto/neto, período y huso horario. No inferir elegibilidad por la palabra «remoto».

Las consultas son plantillas de descubrimiento, no una API ni una promesa de resultados completos. La postulación y los inicios de sesión son acciones del usuario. Este workflow no envía CVs ni mensajes automáticamente.

## Robots y restricciones observadas

Los siguientes `robots.txt` se revisaron mediante una petición HTTP puntual, excepto LinkedIn, leído con la herramienta web. La ausencia de una restricción no otorga permiso general para scraping. Volver a comprobar las reglas antes de crear cualquier integración futura.

- [Bumeran robots.txt](https://www.bumeran.com.ar/robots.txt) y [ZonaJobs robots.txt](https://www.zonajobs.com.ar/robots.txt): HTTP 200; restringen variantes `recientes=true`, `relevantes=true`, parámetros `localidades` y algunas rutas de listados. No usar rutas internas ni intentar evadir el rate limit observado.
- [Computrabajo robots.txt](https://ar.computrabajo.com/robots.txt): HTTP 200; restringe hojas de vida, currículums, `/Ajax/`, `/_services/` y diversas variantes de filtros. No usar endpoints internos ni sortear la verificación antirobot.
- [LinkedIn robots.txt](https://www.linkedin.com/robots.txt): indica que el acceso automatizado requiere permiso expreso y remite a sus [condiciones de uso](https://www.linkedin.com/legal/user-agreement). No crear ni ejecutar extracción de páginas, navegación automática o llamadas `jobs-guest`/`voyager`. Utilizar el buscador para descubrir enlaces y pedir el texto del aviso si hace falta analizarlo.
- [Get on Board robots.txt](https://www.getonbrd.com.ar/robots.txt): HTTP 200; la respuesta comprobada contenía un comentario, sin reglas `Disallow`. Se mantiene búsqueda guiada sin extracción masiva.
- [AMIA robots.txt](https://empleos.amia.org.ar/robots.txt): HTTP 200; grupo `User-agent: *` con `Disallow` vacío y sitemap. El sitio no se integra como API.

## Recurso oficial complementario

[Portal Empleo](https://www.portalempleo.gob.ar/) sirve también para empleo y capacitación. El [instructivo oficial de registro](https://www.argentina.gob.ar/sites/default/files/intructivo_ciudadanos_portal_empleo_julio_2025.pdf) explica que «Buscá Empleo» está dentro del perfil registrado. El usuario realiza personalmente el registro y el ingreso con DNI/contraseña en el sitio oficial; no hacen falta esos datos en este repositorio.

Prueba: inicio HTTP 200 por PowerShell, con título de Portal Empleo; la herramienta web devolvió 502. `robots.txt` devolvió 404. No confundir el fallo de un cliente con cierre del servicio ni asumir permiso de automatización. Es un recurso manual complementario, sin scraper instalado.

## Fuentes primarias de actividad

- [Bumeran: listado público de ejemplo](https://www.bumeran.com.ar/empleos-area-recursos-humanos-y-capacitacion-busqueda-recursos-humanos.html).
- [ZonaJobs: inicio con búsqueda por puesto, ubicación y modalidad](https://www.zonajobs.com.ar/).
- [Computrabajo: listado público indexado](https://ar.computrabajo.com/offersgrid/search).
- [LinkedIn: búsqueda argentina indexada](https://ar.linkedin.com/jobs/search).
- [Get on Board: inicio argentino](https://www.getonbrd.com.ar/) y [categoría Programación](https://www.getonbrd.com.ar/jobs/programacion).
- [Servicio de Empleo AMIA: inicio y herramientas para postulantes](https://empleos.amia.org.ar/).

La verificación fue de acceso y funcionamiento público básico; no se ejecutó una postulación ni se probó una extracción automatizada. No hay API de estos portales configurada en esta adaptación.
