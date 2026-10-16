# Validación de la edición Codex

Validación local realizada el 15/10/2026 en Windows y Python 3.12.

- 620 pruebas Python aprobadas con un entorno virtual aislado y las dependencias
  de `requirements-dev.txt`. La publicación se comprobó además en un clon público nuevo.
- 128 pruebas Bun aprobadas (57 freehire y 71 LinkedIn), más comprobación de tipos
  en ambas CLI. Las pruebas usan respuestas simuladas y servidores locales; los
  subprocesos de prueba también bloquean las consultas externas reales.
- 6 de 6 skills aprobados por el validador oficial de Skill Creator.
- Linter nativo: 6 skills y 12 referencias de workflows. El instalador descubre
  únicamente las 2 CLI conservadas; LinkedIn sigue deshabilitado para uso automático.
- Regresiones argentinas: SA/SRL/SAS, tildes y ñ, ciudades, encabezados Excel en
  español y recorrido Excel → JSON → consulta con importes ficticios ARS/USD.
  Moneda, bruto/neto, período, fuente y fecha se conservan sin conversión automática.
- Controles de datos privados, manifiestos y versión aprobados.
- Bootstrap desde cero y diagnóstico técnico aprobados. Los avisos de perfil incompleto
  y capacidades opcionales ausentes se conservan como tales.
- Consulta real y puntual de programación remota para Argentina ejecutada con el runner.
- Prueba conductual aislada: CV ficticio importado, postulación preparada, dos JSON,
  CV de una página, carta de una página y registro `drafted`. Aviso archivado literalmente.
- PDF revisados visualmente y por texto: contactos, tildes, palabras clave y fechas.
- Las plantillas y la metodología compartidas conservaron sus hashes al personalizar
  la candidatura ficticia; no hubo envíos externos.
- Exportación pública revisada sin perfil personal, documentos, credenciales, runtime
  local, historial Git ni rutas privadas del equipo.
- El ZIP y un clon Git con `.gitattributes` conservan las sumas de verificación
  del manifiesto: texto LF, lanzador `.cmd` CRLF y binarios sin modificaciones.
- La comprobación de enlaces omite únicamente los marcadores literales `...` y `…`;
  sigue detectando rutas reales inexistentes en todas las plataformas. Las pruebas
  de exportación resuelven los alias de rutas temporales de Windows.

La prueba de candidatura utilizó datos ficticios. No certifica afinidad de ofertas
con un candidato real ni garantiza compatibilidad con todos los sistemas ATS.
El flujo requiere las capacidades que efectivamente ofrezca cada sesión de Codex;
las integraciones opcionales no se simulan como conectadas.

CI queda configurado para ejecutar controles y generar PDF sin LaTeX en GitHub.
Esa ejecución remota no se realizó durante esta validación local.
