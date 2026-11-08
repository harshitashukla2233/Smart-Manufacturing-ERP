# Test Cases

| ID | Scenario | Expected result |
|---|---|---|
| TC-01 | Load product master | Product IDs are unique |
| TC-02 | Validate BOM references | Every parent/component exists |
| TC-03 | Validate routing references | Product and work-centre IDs exist |
| TC-04 | Validate inventory | No negative quantities; reserved <= on hand |
| TC-05 | Run MRP | Gross demand is exploded through the BOM |
| TC-06 | Stock netting | Available stock offsets gross requirement |
| TC-07 | Procurement classification | Net BUY item is marked BUY; MAKE item marked MAKE |
| TC-08 | Capacity estimate | Required hours and utilisation are calculated |
| TC-09 | ECR impact lookup | Direct parent BOM records are displayed |
