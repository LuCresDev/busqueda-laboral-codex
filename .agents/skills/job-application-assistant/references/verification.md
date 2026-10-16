# Verificación final de documentos

El agente principal ejecuta esta lista una vez, después de aplicar cambios del revisor y terminar el render. Es metodología compartida, no parte del perfil personal.

## Hechos y enfoque

- Todas las afirmaciones, cargos, fechas, métricas, responsabilidades y tecnologías coinciden con profile/candidate.md. Las fuentes nuevas fueron confirmadas y registradas allí.
- Nombre y contacto son reales y autorizados para el documento. No hay placeholders, datos ficticios ni experiencias tomadas de un ejemplo público.
- Empresa, rol y requisitos corresponden al aviso real; cada requisito está cubierto o reconocido honestamente como brecha. No se insertan palabras clave sin sustento.
- Afirmaciones específicas de empresa verificadas por el principal contra páginas leídas, localizadas independientemente. Registrar fuentes y limitaciones.
- Voz y estilo coherentes entre documentos, con guías compartidas y preferencias personales opcionales. Sin clichés, exageración ni atribución de herramientas no confirmadas.
- Logística, idioma documental y elegibilidad tratados según hechos confirmados. El idioma del CV no prueba dominio laboral.

## Render e inspección

Leer manifiesto y contrato de la plantilla activa. En Argentina, JSON a PDF mediante tools/render_application.py, CV de 1–2 páginas y carta exactamente 1. No rellenar una página con contenido inventado. Cada render debe terminar con código 0 y corresponder a las fuentes actuales; un error nunca habilita presentar el PDF anterior como nuevo.

Inspeccionar visualmente todas las páginas con el visor o imágenes disponibles: títulos acompañados de contenido, sin huérfanos, solapamientos, recortes, bloques excesivos, contacto oculto o firmas fuera de página. Fechas y fuentes consistentes, acentos legibles, encabezados en idioma documental. Si no se puede inspeccionar, decirlo y no marcar ese ítem aprobado.

## Texto ATS

Ejecutar tools/verify_pdf.py con dump-text sobre el PDF nuevo. Para CV argentino, --ascii-dates verifica guiones de fechas; para carta, --pages 1. El renderer valida máximo 2 del CV, por lo que no exigir --pages 2 a un CV de 1 página.

Verificar:
- ausencia de caracteres de reemplazo, cid markers o texto visible ausente en extracción;
- correo y teléfono como texto literal, no solo iconos o hyperlinks;
- orden de lectura y secciones coherentes;
- términos del aviso presentes cuando el perfil los sostiene, con brechas reconocidas;
- fechas y datos de empresa, rol, candidato y documento correctos.

Si falta extractor o visor, conservar el resultado como pendiente con limitación concreta; nunca inventar una verificación aprobada. Reportar aprobado/falló/pendiente, archivos producidos, ajustes relevantes, brechas y fuentes. El registro drafted se realiza según apply.md, sin inferir envío.
