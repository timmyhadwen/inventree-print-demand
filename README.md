# InvenTree 3D Print Demand Plugin

Dashboard plugin for InvenTree that shows aggregated demand for 3D printed parts across all open build orders and sales orders.

## Features

- Dashboard panel showing all parts from a configured category
- Aggregates stock, allocations, and demand from build and sales orders
- Colour-coded deficit column (red = shortage, green = surplus)
- Configurable part category with optional subcategory inclusion

## Installation

```bash
cd Projects/02-engineering/inventree/inventree-print-demand
pip install -e .
```

Then restart InvenTree and enable the plugin in **Admin > Plugins**.

## Configuration

In plugin settings, set:

- **Part Category** - select the category containing your 3D printed parts
- **Include Subcategories** - whether to include parts from subcategories (default: true)

## API

`GET /plugin/print-demand/api/demand/` returns a JSON array of parts sorted by deficit:

```json
[
  {
    "pk": 123,
    "name": "Housing Top",
    "IPN": "MP-001",
    "in_stock": 50,
    "allocated_build": 30,
    "allocated_sales": 10,
    "available": 10,
    "required_build": 45,
    "required_sales": 15,
    "deficit": -10
  }
]
```
