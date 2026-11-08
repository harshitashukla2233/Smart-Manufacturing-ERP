import pandas as pd
from collections import defaultdict

def validate_master_data(data_dir):
    p = pd.read_csv(f"{data_dir}/products.csv")
    b = pd.read_csv(f"{data_dir}/bom.csv")
    r = pd.read_csv(f"{data_dir}/routing.csv")
    w = pd.read_csv(f"{data_dir}/work_centres.csv")
    i = pd.read_csv(f"{data_dir}/inventory.csv")
    o = pd.read_csv(f"{data_dir}/production_orders.csv")
    checks = []
    def add(name, passed, detail):
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})
    add("Unique product IDs", p.product_id.is_unique, "Product master IDs must be unique.")
    pids = set(p.product_id)
    add("BOM references valid products",
        set(b.parent_product_id).issubset(pids) and set(b.component_product_id).issubset(pids),
        "Every BOM parent and component must exist in products.")
    add("Routing references valid products and work centres",
        set(r.product_id).issubset(pids) and set(r.work_centre_id).issubset(set(w.work_centre_id)),
        "Routing product and work-centre IDs must exist.")
    add("Inventory references valid products", set(i.product_id).issubset(pids),
        "Every inventory row must reference a known product.")
    add("Production orders reference valid products", set(o.product_id).issubset(pids),
        "Every production order must reference a known product.")
    units = p.set_index("product_id").base_uom.to_dict()
    unit_ok = all(str(row.uom) == str(units[row.component_product_id]) for row in b.itertuples())
    add("BOM units match component base units", unit_ok,
        "BOM line UOM must match the component product base UOM.")
    inv_ok = (i.on_hand_qty.ge(0).all() and i.reserved_qty.ge(0).all()
              and i.safety_stock_qty.ge(0).all() and i.reserved_qty.le(i.on_hand_qty).all())
    add("Inventory quantities are valid", inv_ok,
        "Quantities must be non-negative and reserved stock cannot exceed on-hand stock.")
    add("Unique routing operation numbers",
        not r.duplicated(["product_id","operation_no"]).any(),
        "A product cannot repeat the same operation number.")
    add("No self-referencing BOM lines",
        not (b.parent_product_id == b.component_product_id).any(),
        "A product cannot be its own direct BOM component.")
    return pd.DataFrame(checks)

def calculate_mrp(data_dir, orders=None):
    products = pd.read_csv(f"{data_dir}/products.csv").set_index("product_id")
    bom = pd.read_csv(f"{data_dir}/bom.csv")
    inventory = pd.read_csv(f"{data_dir}/inventory.csv")
    order_df = orders if orders is not None else pd.read_csv(f"{data_dir}/production_orders.csv")
    stock = inventory.groupby("product_id").agg(
        on_hand=("on_hand_qty","sum"),
        reserved=("reserved_qty","sum"),
        safety=("safety_stock_qty","sum")
    )
    available = {}
    for pid in products.index:
        if pid in stock.index:
            row = stock.loc[pid]
            available[pid] = max(0.0, float(row.on_hand-row.reserved-row.safety))
        else:
            available[pid] = 0.0
    gross = defaultdict(float)
    for row in order_df.itertuples():
        gross[row.product_id] += float(row.order_qty)

    rows = []
    visited_path = set()
    def explode(pid, gross_qty, path=()):
        if pid in path:
            raise ValueError(f"Circular BOM detected: {' -> '.join(path + (pid,))}")
        net = max(0.0, gross_qty - available.get(pid, 0.0))
        rows.append({
            "product_id": pid,
            "product_name": products.loc[pid, "product_name"],
            "product_type": products.loc[pid, "product_type"],
            "gross_requirement": round(gross_qty, 3),
            "available_after_reservations_and_safety": round(available.get(pid, 0.0), 3),
            "net_requirement": round(net, 3),
            "procurement_type": products.loc[pid, "procurement_type"],
            "action": "MAKE" if net > 0 and products.loc[pid, "procurement_type"] == "MAKE"
                      else ("BUY" if net > 0 else "NO ACTION")
        })
        if net <= 0:
            return
        children = bom[bom.parent_product_id == pid]
        for child in children.itertuples():
            qty = net * float(child.quantity_per) * (1 + float(child.scrap_factor_pct)/100)
            explode(child.component_product_id, qty, path + (pid,))
    for pid, qty in gross.items():
        explode(pid, qty)
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    # Aggregate repeated demand for the same item across multiple parent paths.
    agg = result.groupby(["product_id","product_name","product_type","procurement_type","action"], as_index=False).agg(
        gross_requirement=("gross_requirement","sum"),
        available_after_reservations_and_safety=("available_after_reservations_and_safety","max"),
        net_requirement=("net_requirement","sum")
    )
    agg["net_requirement"] = (agg["gross_requirement"] - agg["available_after_reservations_and_safety"]).clip(lower=0).round(3)
    agg["action"] = agg.apply(lambda x: "NO ACTION" if x.net_requirement <= 0 else x.procurement_type, axis=1)
    return agg.sort_values(["action","product_id"]).reset_index(drop=True)

def capacity_load(data_dir, production_qty=100):
    routing = pd.read_csv(f"{data_dir}/routing.csv")
    centres = pd.read_csv(f"{data_dir}/work_centres.csv").set_index("work_centre_id")
    rows = []
    for work_centre_id, group in routing.groupby("work_centre_id"):
        required = (group.setup_time_min.sum() +
                    group.processing_time_min_per_unit.sum() * production_qty) / 60
        rows.append({"work_centre_id": work_centre_id, "required_hours": required})
    grouped = pd.DataFrame(rows)
    grouped["work_centre_name"] = grouped.work_centre_id.map(centres.work_centre_name)
    grouped["effective_daily_capacity_hours"] = grouped.work_centre_id.map(
        centres.available_hours_per_day * centres.efficiency_pct / 100
    )
    grouped["utilisation_pct"] = (
        grouped.required_hours / grouped.effective_daily_capacity_hours * 100
    ).round(1)
    grouped["status"] = grouped.utilisation_pct.apply(lambda x: "OVER CAPACITY" if x > 100 else "WITHIN CAPACITY")
    return grouped.sort_values("utilisation_pct", ascending=False)
