"""
Genera la API simulada del catalogo de vehiculos.

Fuente:
  - raw/catalogo_vehiculos_lima_2026_completo.csv

Salidas:
  - inventory.json            : GET total (todos los modelos + resumen).
  - vehicles/{id_modelo}.json : GET por ID (lo sirve GitHub raw).

Uso:
  python3 build_inventory.py
"""

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).parent

RAW_CSV = ROOT / "raw" / "catalogo_vehiculos_lima_2026_completo.csv"
VEHICLES_DIR = ROOT / "vehicles"
INVENTORY_JSON = ROOT / "inventory.json"

ID_PATTERN = re.compile(r"^[A-Z0-9-]+$")

BOOLEAN_COLUMNS = {
    "marca_autorizada_concesionaria",
    "inventario_verificado",
    "activo_para_oferta",
    "equipamiento_verificado",
}

NUMBER_COLUMNS = {
    "precio_web_usd_desde",
    "precio_final_cotizado_pen",
}

INTEGER_COLUMNS = {
    "stock_unidades",
}

# El CSV lo llama "cotizado", pero es precio_web_usd_desde x 3.75:
# no es una cotizacion. En el JSON se publica con un nombre honesto.
RENAMED_COLUMNS = {
    "precio_final_cotizado_pen": "precio_referencial_pen",
}

AVAILABILITY_WITH_STOCK = "EN_STOCK"
AVAILABILITY_ON_ORDER = "A_PEDIDO"

REQUIRED_COLUMNS = {
    "id_modelo",
    "marca",
    "modelo",
    "segmento",
    "propulsion",
    "precio_web_usd_desde",
    "moneda_precio_web",
    "tipo_precio",
    "url_fuente",
    "fuente_id",
    "fecha_revision",
    "tipo_disponibilidad",
} | BOOLEAN_COLUMNS | INTEGER_COLUMNS


def parse_boolean(value: str, *, column: str, row_id: str) -> bool:
    normalized = value.strip().lower()

    if normalized == "true":
        return True

    if normalized == "false":
        return False

    raise SystemExit(
        f"{row_id}: valor no booleano en {column}: {value!r}"
    )


def parse_number(value: str, *, column: str, row_id: str) -> int | float:
    try:
        number = float(value)

    except ValueError:
        raise SystemExit(
            f"{row_id}: valor no numerico en {column}: {value!r}"
        ) from None

    return int(number) if number.is_integer() else number


def parse_integer(value: str, *, column: str, row_id: str) -> int:
    number = parse_number(value, column=column, row_id=row_id)

    if not isinstance(number, int) or number < 0:
        raise SystemExit(
            f"{row_id}: {column} debe ser entero >= 0: {value!r}"
        )

    return number


def validate_availability(vehicle: dict) -> None:
    row_id = vehicle["id_modelo"]
    stock = vehicle["stock_unidades"]
    availability = vehicle["tipo_disponibilidad"]

    if stock is None:
        raise SystemExit(f"{row_id}: stock_unidades vacio")

    if availability == AVAILABILITY_WITH_STOCK and stock == 0:
        raise SystemExit(
            f"{row_id}: {AVAILABILITY_WITH_STOCK} con stock 0"
        )

    if availability == AVAILABILITY_ON_ORDER and stock > 0:
        raise SystemExit(
            f"{row_id}: {AVAILABILITY_ON_ORDER} con stock {stock}"
        )


def to_vehicle(row: dict) -> dict:
    row_id = row["id_modelo"].strip()
    vehicle = {}

    for column, raw_value in row.items():
        value = raw_value.strip()

        # Vacio = dato no disponible, no texto vacio.
        if value == "":
            vehicle[column] = None

        elif column in BOOLEAN_COLUMNS:
            vehicle[column] = parse_boolean(
                value, column=column, row_id=row_id
            )

        elif column in NUMBER_COLUMNS:
            vehicle[column] = parse_number(
                value, column=column, row_id=row_id
            )

        elif column in INTEGER_COLUMNS:
            vehicle[column] = parse_integer(
                value, column=column, row_id=row_id
            )

        else:
            vehicle[column] = value

    for old_name, new_name in RENAMED_COLUMNS.items():
        if old_name in vehicle:
            vehicle[new_name] = vehicle.pop(old_name)

    validate_availability(vehicle)

    return vehicle


def load_vehicles() -> list[dict]:
    if not RAW_CSV.exists():
        raise SystemExit(f"No existe {RAW_CSV}.")

    # utf-8-sig: el CSV trae BOM al inicio.
    with RAW_CSV.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])

        if missing:
            raise SystemExit(
                f"Faltan columnas en el CSV: {sorted(missing)}"
            )

        vehicles = [to_vehicle(row) for row in reader]

    seen: set[str] = set()

    for vehicle in vehicles:
        vehicle_id = vehicle["id_modelo"]

        if not vehicle_id or not ID_PATTERN.match(vehicle_id):
            raise SystemExit(f"id_modelo invalido: {vehicle_id!r}")

        if vehicle_id in seen:
            raise SystemExit(f"id_modelo duplicado: {vehicle_id}")

        seen.add(vehicle_id)

    return vehicles


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def main() -> None:
    vehicles = load_vehicles()

    # Regenera vehicles/ desde cero para no dejar archivos huerfanos.
    for old_file in VEHICLES_DIR.glob("*.json"):
        old_file.unlink()

    for vehicle in vehicles:
        write_json(
            VEHICLES_DIR / f"{vehicle['id_modelo']}.json",
            vehicle,
        )

    total_units = sum(
        vehicle["stock_unidades"] for vehicle in vehicles
    )

    write_json(
        INVENTORY_JSON,
        {
            "total": len(vehicles),
            "total_unidades": total_units,
            "vehicles": vehicles,
        },
    )

    brands = {vehicle["marca"] for vehicle in vehicles}
    without_price = sum(
        1 for vehicle in vehicles
        if vehicle["precio_web_usd_desde"] is None
    )
    estimated_price = sum(
        1 for vehicle in vehicles
        if vehicle["tipo_precio"] == "ESTIMADO_PROMEDIO_SEGMENTO"
    )
    on_order = sum(
        1 for vehicle in vehicles
        if vehicle["tipo_disponibilidad"] == AVAILABILITY_ON_ORDER
    )

    print(f"{len(vehicles)} vehiculos de {len(brands)} marcas")
    print(f"Unidades en stock: {total_units}")
    print(f"A pedido (stock 0): {on_order}")
    print(f"Precio estimado por segmento: {estimated_price}")
    print(f"Sin precio web: {without_price}")


if __name__ == "__main__":
    main()
