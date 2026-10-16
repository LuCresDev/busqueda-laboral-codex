# Consulta salarial con datos propios

Esta herramienta opcional busca empresas **solo en el dataset que vos aportes**.
No consulta una base de salarios de mercado, no recomienda cuánto cobrar y no
actualiza importes por inflación o tipo de cambio. Si no tenés datos comparables,
el asistente omite este paso sin impedir la búsqueda laboral.

El archivo local `salary_data.json` está ignorado por Git. No incluyas datos de
personas identificables ni publiques encuestas o información confidencial.
Los nombres e importes siguientes son **ficticios para mostrar el formato**.

## Importes absolutos: moneda, bruto/neto, período y fecha

Para un sueldo usá `amount`, nunca un índice sin unidades:

```json
{
  "metadata": {
    "source": "Ejemplo ficticio aportado por el usuario",
    "as_of": "2026-10-01",
    "currency": "ARS",
    "pay_basis": "gross",
    "period": "month"
  },
  "companies": [
    {
      "company": "Ñandú Ficticia S.R.L.",
      "city": "Córdoba",
      "categories": {
        "desarrollo": {"amount": 123456.78, "count": 12}
      }
    },
    {
      "company": "Otra Ficticia S.A.S.",
      "city": "Neuquén",
      "categories": {
        "desarrollo": {
          "amount": 1234.56,
          "currency": "USD",
          "pay_basis": "net",
          "period": "year"
        }
      }
    }
  ]
}
```

Los campos de cada categoría prevalecen sobre los de `metadata`. Cada importe
requiere moneda explícita de tres letras, `gross`/`net` (bruto/neto), período
`month`/`year`/`hour`/`week`/`day`, fuente y fecha real del dato `YYYY-MM-DD`.
`as_of` es la fecha de los datos, no la fecha en que ejecutaste el comando.
La herramienta muestra esa fecha; comprobar vigencia y comparabilidad queda a cargo
del usuario. No transforma valores de una fecha a otra.

La salida `--json` conserva el formato histórico de lista de empresas y materializa
las unidades/fuente/fecha heredadas en cada categoría con `amount`. No mezcla ARS
con USD, mensual con anual ni bruto con neto. Tampoco calcula un porcentaje frente
a una base de índice para un `amount` ni convierte dólares automáticamente.
La coincidencia de nombre es aproximada: revisá razón social, ciudad y fuente antes
de atribuir un dato a una empresa. Reconoce SA, SRL, SAS y variantes con puntos,
tildes, ñ y ciudades como Córdoba/Neuquén sin exigir que tipees las tildes.

## Índices y cantidades

Para una serie de índices aportada por vos, conservá el contrato `index`:

```json
{
  "metadata": {
    "source": "Encuesta ficticia, no datos de mercado",
    "index_baseline": 100,
    "index_label": "Índice",
    "baseline_description": "Base definida por esta encuesta ficticia"
  },
  "companies": [
    {
      "company": "Empresa de Prueba SA",
      "city": "Rosario",
      "categories": {"desarrollo": {"count": 12, "index": 108.5}}
    }
  ]
}
```

`count` es cantidad de observaciones/personas, no salario ni identificador.
Una categoría puede contener un índice con cantidad o solo cantidad. La ausencia
de `index` no permite afirmar que hubo supresión por privacidad. El `index: null`
explícito conserva la presentación histórica de dato suprimido.
El porcentaje contra la base describe únicamente la serie de índices provista;
no significa estar por encima del mercado argentino. No combines `index` y
`amount` en la misma categoría.

Los archivos históricos que guardaban importes en `index` con base cero siguen
siendo legibles. No se reinterpretan ni se convierten automáticamente. Para datos
nuevos, migrá manualmente a `amount` cuando puedas confirmar todas las unidades.

## Convertir un Excel propio

Necesitás la dependencia opcional `openpyxl` en tu Python:

```powershell
python -m pip install openpyxl
python tools/convert_salary_excel.py "datos-propios.xlsx" --source "Fuente aportada" --currency ARS --basis bruto --period mensual --as-of 2026-10-01
python salary_lookup.py --validate
python salary_lookup.py "Nandu Ficticia" --city "Cordoba"
python salary_lookup.py "Nandu Ficticia" --json
```

Desde el montaje de Windows también podés invocar Python con
`.\herramientas.ps1 -Accion python -Argumentos @(...)`.

El conversor reconoce:

- Empresa, Compañía o Razón social; Ciudad, Localidad o Ubicación.
- Cantidad e Índice, con categorías iguales para emparejar, por ejemplo
  `Cantidad desarrollo` + `Índice desarrollo`.
- Sueldo, Salario o Remuneración como **importe absoluto**.
- Columnas explícitas Moneda, Bruto/Neto, Período, Fuente y Fecha por fila;
  permiten datasets mixtos ARS/USD sin asumir una unidad global. Si contradicen
  un flag global, el conversor falla para que aclares el archivo.
- Omite DNI, CUIT, CUIL, legajo, identificadores y porcentajes de aumento;
  no los convierte en salarios, índices ni cantidades.

Para datos con columnas antiguas en inglés, se conserva la interpretación
histórica de `Salary` como índice. Si ese Excel contiene importes, agregá
`--value-kind amount` y las unidades explícitas. Una columna que diga `Index` o
`Índice` sigue siendo un índice. Las categorías numéricas sin tipo conservan el
comportamiento histórico; revisalas antes de usar su resultado.

Preferí celdas numéricas reales de Excel. Se aceptan textos como `123.456,78` o
`123,456.78`; un separador ambiguo como `1.234` o `1,234` se omite, sin adivinar
una cantidad mil veces mayor o menor. Las cantidades fraccionarias se rechazan,
no se truncan. Los campos inválidos y las unidades incompletas impiden escribir
el resultado, conservando el archivo de salida anterior. Revisá siempre el JSON
convertido antes de incorporarlo a una evaluación.

## Alcance y límites

- Sin `salary_data.json`, se omite la comparación salarial.
- Sin moneda, base bruto/neto, período, fuente y fecha, no se admite un nuevo importe absoluto.
- Un valor viejo, de muestra pequeña o de otra modalidad contractual no demuestra
  cuál sería una oferta actual. La herramienta no corrige esas diferencias.
- La búsqueda no certifica identidad corporativa ni calidad estadística del dataset.
- No se extraen datos salariales ni credenciales de portales y no se envía información.
