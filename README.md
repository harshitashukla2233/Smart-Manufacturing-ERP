# Smart Manufacturing ERP & Production Planning System

**Apex Auto Components | SAP-inspired discrete manufacturing prototype**

## Project summary
A Python/Streamlit prototype that models a fictional automotive engine-component manufacturer. It demonstrates manufacturing master data, multi-level BOM relationships, inventory-aware material planning, routing-based capacity review and a simplified engineering-change impact workflow.

> **Scope and honesty statement:** This is an independent educational prototype inspired by common ERP/SAP manufacturing concepts. It is not an SAP S/4HANA implementation, does not connect to SAP, and does not reproduce proprietary SAP functionality. All company and operational data are synthetic.

## Business problem
The fictional manufacturer needs a consistent way to understand product structures, manufacturing steps, inventory availability, production demand and the impact of engineering changes.

## Features
1. Product and material master data.
2. Multi-level Bill of Materials (BOM), including illustrative scrap factors.
3. Routing operations assigned to work centres.
4. Inventory snapshot with on-hand, reserved and safety-stock quantities.
5. Basic MRP: planned demand, stock netting and recursive BOM explosion.
6. Work-centre routing load estimate and capacity comparison.
7. Simplified engineering change request (ECR) demo with direct parent-BOM impact lookup.
8. Master-data validation checks and downloadable MRP results.

## Technology
- Python and Pandas – business logic and data processing
- Streamlit – interactive application
- CSV – starter master data
- SQL (PostgreSQL-compatible schema) – relational data model
- Power BI – optional future reporting extension

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\\Scripts\\activate

pip install -r requirements.txt
streamlit run app.py
```

## Repository structure
```text
app.py
modules/planning.py
data/
  products.csv
  bom.csv
  routing.csv
  work_centres.csv
  inventory.csv
  production_orders.csv
database/schema.sql
documentation/
tests/
requirements.txt
```

## Key business definitions
- **Product master:** core record describing a product or material.
- **BOM:** components and quantities required to make a parent product.
- **Routing:** ordered operations used to manufacture a product.
- **Work centre:** a production resource or group of similar resources.
- **MRP:** calculation of material requirements against stock and planned supply.
- **Available stock in this prototype:** on-hand less reserved stock and safety stock.
- **Engineering change:** controlled proposal to revise product definition or manufacturing data.

## Model assumptions and limitations
- Discrete manufacturing of a fictional engine assembly.
- One active illustrative BOM revision is supplied per parent/component relationship.
- MRP nets each item against the inventory snapshot and explodes make requirements through the BOM. This is a teaching-level lot-for-lot model; it does not implement full SAP planning logic, scheduled receipts, lot sizing, calendars, alternate BOM selection or pegging.
- The capacity page estimates aggregate routing load for a selected quantity. It is not a finite-capacity scheduler and does not schedule orders across shifts or dates.
- The engineering-change page demonstrates a proposed revision and direct parent-BOM lookup; it does not implement formal approval persistence, effectivity dates or production-order release blocking.
- No live ERP, CAD, supplier or shop-floor system integration is implemented.

## Validation
Run:
```bash
python -m unittest discover -s tests -v
```

## Future enhancements
- Persist transactions in PostgreSQL.
- Add procurement proposals and planned production orders.
- Add operation-level finite scheduling and shift calendars.
- Add engineering revision history, approvals and effectivity dates.
- Add role-based access and audit log.
- Connect Power BI to a persistent database.
- Explore SAP Learning Journeys and an SAP sandbox for genuine SAP configuration experience.
