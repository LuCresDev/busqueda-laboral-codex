# Estrategia de búsqueda: Argentina

El mercado predeterminado es Argentina (`AR`), con fechas en
`America/Argentina/Buenos_Aires`. Esto no confirma residencia del candidato.
El único perfil canónico es profile/candidate.md. Tomá de allí profesión, roles, tecnologías, seniority, lugar, modalidad e idiomas confirmados; lo pendiente es desconocido. La URL de un perfil público por sí sola no acredita experiencia ni habilidades inaccesibles. No ejecutes consultas con placeholders. Español de conversación no demuestra español laboral ni inglés.

## Fuentes

Consultá `config/portales-argentina.json` y
`.agents/skills/argentina-job-search/references/portales.md` para dominios, alcance,
limitaciones y acceso guiado. Fuentes locales contempladas: Bumeran, ZonaJobs,
Computrabajo Argentina, Get on Board, Servicio de Empleo AMIA y páginas de empleo de
las empresas. LinkedIn se descubre mediante buscador y apertura manual del usuario;
su CLI está deshabilitada. freehire complementa puestos de tecnología.

Las CLI instaladas y habilitadas son el mecanismo primario cuando sirven para el
puesto y el mercado. Descubrí solo skills de portal con CLI real bajo `.agents/skills/`;
`argentina-job-search` es un adaptador de flujo, no un portal. Usá los flags documentados
por cada CLI. La instalación activa solo incluye portales y fuentes pertinentes al mercado configurado.

Las consultas `site:` sirven para fuentes sin CLI y para cubrir fallas o huecos de
cobertura. No tienen garantía de frescura: verificá el aviso antes de presentarlo como
vacante abierta. Si un portal exige login, CAPTCHA o devuelve 403/429, registrá la
limitación y seguí la referencia de acceso guiado; no eludas controles.

## Generar consultas desde el perfil

Si el perfil confirma programación y modalidad remota, una búsqueda amplia puede usar variantes «programador», «desarrollador», «software developer» y «software engineer» con «remoto» o «remote». Son ejemplos de títulos, no hechos del candidato ni evidencia lingüística. Si el perfil pide remoto exclusivo, excluir presencial e híbrido. No bloquear remoto por ciudad desconocida; tecnología, experiencia e idiomas pendientes impiden un ajuste personalizado definitivo.

Ejemplos solo para ese alcance confirmado:

    site:bumeran.com.ar programador remoto
    site:zonajobs.com.ar desarrollador remoto
    site:ar.computrabajo.com programador remoto
    site:getonbrd.com.ar "software developer" Argentina remoto
    site:linkedin.com/jobs "software engineer" remote Argentina

Agrupá por función y usá variantes de títulos que realmente encajen con las competencias
y objetivos confirmados. No establezcas tecnología, seniority, sector o consultoría como
prioridad del candidato por venir incluidos en ejemplos del repositorio.

| Prioridad | Criterio |
|---|---|
| 1 | Función y puestos objetivo confirmados |
| 2 | Función compatible con experiencia o dominio probado |
| 3 | Función adyacente que el usuario acepte explorar |
| 4, solo búsqueda amplia | Otros títulos que usen habilidades confirmadas |

Adaptá estos patrones con valores reales antes de ejecutarlos:

```text
site:bumeran.com.ar "<puesto confirmado>" "<ciudad confirmada>"
site:zonajobs.com.ar "<función confirmada>" "<ciudad confirmada>"
site:ar.computrabajo.com "<puesto confirmado>" "<área aceptable confirmada>"
site:linkedin.com/jobs "<puesto confirmado>" Argentina
"<empresa objetivo confirmada>" empleo "<puesto confirmado>"
```

Tomá la modalidad del perfil confirmado. Si exige remoto exclusivo, agregá híbrido o presencial solo cuando el usuario cambie expresamente ese alcance. Usá términos en los idiomas laborales
que declare el perfil, con variantes de títulos habituales; no hagas pasar la lengua
del aviso por un requisito laboral si el texto no lo exige.

## Lugar y trabajo remoto

- Para presencial o híbrido, comprobá ciudad, dirección/área informada y frecuencia de
  asistencia contra el radio de traslado confirmado. No asumas CABA, Buenos Aires ni
  disponibilidad de mudanza.
- Para remoto, comprobá que permita trabajar desde Argentina. «LATAM», «Américas»
  o «global» no confirma por sí solo elegibilidad: verificá los países permitidos, la
  entidad/forma de contratación y la franja horaria pedida. Lo ausente queda pendiente.
- No deduzcas permiso de trabajo, residencia fiscal ni capacidad de facturación del
  idioma o del país elegido como mercado.

## Idiomas y frescura

Aplicá el Language Gate de `04-job-evaluation.md` después de confirmar los idiomas y
niveles del perfil. Durante onboarding incompleto marcá «idiomas laborales pendientes»;
no descartes por una tabla que todavía contiene ejemplos ni la trates como perfil vacío
definitivo. Para idiomas declarados, distinguí requisito ausente de nivel insuficiente
como establece el marco canónico.

Buscá por defecto publicaciones de los últimos 14 días o avisos con fecha de cierre
futura. La fecha del buscador no reemplaza la fecha del aviso. Sin fecha comprobable,
marcá «fecha desconocida». Cerrados o vencidos se archivan con el estado canónico,
sin presentarlos como vacantes abiertas. Conservá URL, fuente, fecha de consulta y
deduplicación mediante `job_scraper/seen_jobs.json` y `job_search_tracker.csv`, ambos
relativos a la raíz del repo, igual que los comandos de herramientas.
