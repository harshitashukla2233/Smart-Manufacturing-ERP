# Business Process Overview

## Scenario
Apex Auto Components is a fictional discrete manufacturer producing engine assemblies and components.

## End-to-end process
1. Maintain product/material master records.
2. Define the product structure using BOM records.
3. Define the manufacturing sequence using routing operations.
4. Record available inventory, reservations and safety stock.
5. Enter planned production demand.
6. Calculate gross component demand through BOM explosion.
7. Offset demand against available inventory.
8. Classify net requirements as MAKE or BUY using procurement type.
9. Review routing load against work-centre capacity.
10. Assess engineering-change impact before revising a product definition.

## Simplified data relationships
- `products` is the master entity.
- `bom.parent_product_id` and `bom.component_product_id` both reference products.
- `routing.product_id` references products.
- `routing.work_centre_id` references work centres.
- `inventory.product_id` references products.
- `production_orders.product_id` references products.

## SAP concept mapping (conceptual, not exact configuration)
| Prototype feature | Related SAP manufacturing concept |
|---|---|
| Product/material records | Material master |
| BOM structure | Bill of Material |
| Routing operations | Routing / task list |
| Work centres | Work centre master |
| Planned production demand | Planned/production order concepts |
| Stock netting and BOM explosion | MRP |
| Engineering revision impact | PLM / engineering change management |
| Capacity estimate | Capacity planning |

Actual SAP object names, configuration, transactions and process behaviour depend on SAP product/version and implementation design.
