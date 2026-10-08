# inventory-mock

API **simulada** del catálogo de vehículos nuevos en Lima para el proyecto *Agente de
Calificación de Leads* (curso Agentes de IA, UTEC). Se sirve gratis desde GitHub
(raw.githubusercontent.com), igual que `credit-bureau-mock`.

> ⚠️ Es un **catálogo de modelos**, no stock real: `inventario_verificado`,
> `activo_para_oferta` y `equipamiento_verificado` son `false` en todos los registros, y
> `tipo_disponibilidad` es `SIN_VERIFICAR`. Los precios son referenciales de web
> (`WEB_REFERENCIAL_NO_COTIZACION`), no cotizaciones. El agente no debe confirmar stock ni
> precios finales.

## Endpoints

| GET | URL | Respuesta |
|---|---|---|
| Total | `https://raw.githubusercontent.com/<usuario>/inventory-mock/main/inventory.json` | `{"total": 220, "vehicles": [...]}` |
| Por ID | `https://raw.githubusercontent.com/<usuario>/inventory-mock/main/vehicles/{id_modelo}.json` | Un vehículo. Si el ID no existe, devuelve **404**. |

Formato del ID: `PE-LIM-{MARCA}-{NNN}`, por ejemplo `PE-LIM-TOYOTA-002`.

GitHub cachea los archivos unos minutos, así que un cambio puede tardar en verse.

Ejemplo (`vehicles/PE-LIM-TOYOTA-002.json`):

```json
{
  "id_modelo": "PE-LIM-TOYOTA-002",
  "marca": "Toyota",
  "modelo": "Raize",
  "segmento": "SUV / crossover",
  "propulsion": "Gasolina",
  "precio_web_usd_desde": 16830,
  "moneda_precio_web": "USD",
  "tipo_precio": "WEB_REFERENCIAL_NO_COTIZACION",
  "url_fuente": "https://e.toyotaperu.com.pe/inventory?locale=es-pe",
  "fuente_id": "C01",
  "fecha_revision": "2026-10-08",
  "marca_autorizada_concesionaria": false,
  "inventario_verificado": false,
  "activo_para_oferta": false,
  "tipo_disponibilidad": "SIN_VERIFICAR",
  "version_exacta": null,
  "vin": null,
  "equipamiento_verificado": false,
  "precio_final_cotizado_pen": null
}
```

## Datos

- 220 modelos de 19 marcas, revisados el 2026-10-08.
- 47 modelos no tienen precio web: `precio_web_usd_desde` y `moneda_precio_web` van en `null`.
- `version_exacta`, `vin` y `precio_final_cotizado_pen` están en `null` en todos los
  registros. Se mantienen porque son los campos que llenaría una verificación humana.

Conversión del CSV al JSON:

| En el CSV | En el JSON |
|---|---|
| Celda vacía | `null` |
| `True` / `False` | `true` / `false` |
| Precios | Número (`16830`), no texto |
| BOM al inicio del archivo | Se lee con `utf-8-sig`; la primera columna queda como `id_modelo` |

## Regenerar

Edita `raw/catalogo_vehiculos_lima_2026.csv` y ejecuta:

```bash
python3 build_inventory.py
```

El script valida que estén las columnas, que los booleanos y precios sean válidos y que los
`id_modelo` sean únicos y aptos para URL. Luego regenera `inventory.json` y `vehicles/`.
No edites los JSON a mano: se sobrescriben.
