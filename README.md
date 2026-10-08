# inventory-mock

API **simulada** del inventario de vehículos nuevos en Lima para el proyecto *Agente de
Calificación de Leads* (curso Agentes de IA, UTEC). Se sirve gratis desde GitHub
(raw.githubusercontent.com), igual que `credit-bureau-mock`.

> ⚠️ **Cómo deben usarse estos datos:**
> - El stock es una **foto al `fecha_revision`** (2026-10-08). El agente no debe confirmarlo
>   como verdad definitiva: debe decir "figura disponible en inventario, sujeto a
>   confirmación del asesor".
> - `precio_referencial_pen` es el precio web × 3.75. **No es una cotización** y no debe
>   presentarse como precio final.
> - Si `tipo_precio` es `ESTIMADO_PROMEDIO_SEGMENTO`, el precio es una estimación por
>   segmento, no el precio publicado por la marca.

## Endpoints

| GET | URL | Respuesta |
|---|---|---|
| Total | `https://raw.githubusercontent.com/beltocas/inventory-mock/main/inventory.json` | `{"total": 220, "total_unidades": 842, "vehicles": [...]}` |
| Por ID | `https://raw.githubusercontent.com/beltocas/inventory-mock/main/vehicles/{id_modelo}.json` | Un vehículo. Si el ID no existe, devuelve **404**. |

Formato del ID: `PE-LIM-{MARCA}-{NNN}`, por ejemplo `PE-LIM-TOYOTA-002`.

GitHub cachea los archivos unos minutos, así que un cambio puede tardar en verse.

Ejemplo (`vehicles/PE-LIM-NISSAN-001.json`):

```json
{
  "id_modelo": "PE-LIM-NISSAN-001",
  "marca": "Nissan",
  "modelo": "Versa",
  "segmento": "Sedan",
  "propulsion": "Gasolina",
  "precio_web_usd_desde": 15990,
  "moneda_precio_web": "USD",
  "tipo_precio": "ESTIMADO_PROMEDIO_SEGMENTO",
  "url_fuente": "https://www.nissan.pe/",
  "fuente_id": "C05",
  "fecha_revision": "2026-10-08",
  "marca_autorizada_concesionaria": true,
  "inventario_verificado": true,
  "activo_para_oferta": true,
  "tipo_disponibilidad": "EN_STOCK",
  "version_exacta": "Base",
  "vin": null,
  "equipamiento_verificado": true,
  "stock_unidades": 7,
  "precio_referencial_pen": 59960
}
```

## Campos

| Campo | Tipo | Significado |
|---|---|---|
| `id_modelo` | texto | ID único del modelo |
| `marca`, `modelo` | texto | 19 marcas y 220 modelos (nombres únicos) |
| `segmento` | texto | 10 valores, sin tildes: `Comercial liviano`, `Coupe / deportivo`, `Hatchback`, `Monovolumen / MPV`, `Pickup`, `SUV / 4x4`, `SUV / crossover`, `SUV / familiar`, `Sedan`, `Van / transporte` |
| `propulsion` | texto | 7 valores, sin tildes: `Gasolina`, `Electrico BEV`, `Hibrido HEV`, `Hibrido e-POWER`, `Hibrido enchufable PHEV`, `Microhibrido MHEV`, `Segun version` |
| `precio_web_usd_desde` | entero | Precio desde, en USD |
| `moneda_precio_web` | texto | `USD` |
| `tipo_precio` | texto | `WEB_REFERENCIAL_NO_COTIZACION` (173 modelos, precio publicado) o `ESTIMADO_PROMEDIO_SEGMENTO` (47 modelos, precio estimado) |
| `url_fuente`, `fuente_id` | texto | De dónde se tomó el dato |
| `fecha_revision` | fecha | Fecha de la foto del inventario |
| `marca_autorizada_concesionaria`, `inventario_verificado`, `activo_para_oferta`, `equipamiento_verificado` | booleano | `true` en todos los registros |
| `tipo_disponibilidad` | texto | `EN_STOCK` (190 modelos, stock ≥ 1) o `A_PEDIDO` (30 modelos, stock 0) |
| `version_exacta` | texto | `Base` (137) o `Full` (83). Cada fila es una sola versión. |
| `vin` | `null` | Vacío: el inventario es por modelo, no por unidad física |
| `stock_unidades` | entero | Unidades disponibles, de 0 a 8 (842 en total) |
| `precio_referencial_pen` | entero | `precio_web_usd_desde` × 3.75. Referencial, **no es una cotización**. |

## Conversión del CSV al JSON

| En el CSV | En el JSON |
|---|---|
| Celda vacía | `null` |
| `True` / `False` | `true` / `false` |
| Precios y stock | Números (`15990`, `7`), no texto |
| `precio_final_cotizado_pen` | Se publica como **`precio_referencial_pen`**: el valor es una conversión, no una cotización |
| BOM al inicio del archivo | Se lee con `utf-8-sig`; la primera columna queda como `id_modelo` |

## Regenerar

Edita `raw/catalogo_vehiculos_lima_2026_completo.csv` y ejecuta:

```bash
python3 build_inventory.py
```

El script se detiene con un error si:
- falta una columna;
- un booleano, un precio o `stock_unidades` no es válido (el stock debe ser un entero ≥ 0);
- `EN_STOCK` tiene stock 0, o `A_PEDIDO` tiene stock mayor a 0;
- un `id_modelo` está duplicado o no sirve para una URL.

Si todo está bien, regenera `inventory.json` y `vehicles/`. No edites los JSON a mano: se
sobrescriben.

## Historial de versiones del CSV

| Versión | Cambios |
|---|---|
| `catalogo_vehiculos_lima_2026.csv` | Catálogo sin verificar: todo `SIN_VERIFICAR`, 47 modelos sin precio y sin precio en PEN |
| `catalogo_vehiculos_lima_2026_completo.csv` | Columna nueva `stock_unidades`, inventario verificado (`EN_STOCK` / `A_PEDIDO`), versión `Base`/`Full`, precio estimado para los 47 modelos sin precio, y precio en PEN (publicado como `precio_referencial_pen`) |
