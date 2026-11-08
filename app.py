from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from modules.planning import validate_master_data, calculate_mrp, capacity_load

st.set_page_config(page_title="Apex Manufacturing ERP", page_icon="🏭", layout="wide")
st.title("🏭 Apex Auto Components | Smart Manufacturing ERP")
st.caption("SAP-inspired manufacturing planning prototype · Synthetic demonstration data")
st.info("Learning prototype only: this is not an SAP S/4HANA implementation and is not connected to a live ERP.")

data_dir = ROOT / "data"
pages = ["Overview", "Master Data", "Material Requirements Planning", "Capacity Planning", "Engineering Change Demo"]
page = st.sidebar.radio("Navigate", pages)

products = pd.read_csv(data_dir/"products.csv")
orders = pd.read_csv(data_dir/"production_orders.csv")
inventory = pd.read_csv(data_dir/"inventory.csv")
bom = pd.read_csv(data_dir/"bom.csv")
routing = pd.read_csv(data_dir/"routing.csv")
centres = pd.read_csv(data_dir/"work_centres.csv")

if page == "Overview":
    st.subheader("Manufacturing operations overview")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Products / materials", len(products))
    c2.metric("BOM relationships", len(bom))
    c3.metric("Production orders", len(orders))
    c4.metric("Work centres", len(centres))
    st.markdown("### Production demand")
    st.dataframe(orders, use_container_width=True, hide_index=True)
    st.markdown("### Inventory snapshot")
    inv = inventory.copy()
    inv["available_qty"] = inv.on_hand_qty - inv.reserved_qty - inv.safety_stock_qty
    st.dataframe(inv, use_container_width=True, hide_index=True)
    st.markdown("### Business process")
    st.write("Demand → BOM explosion → net material requirements → inventory check → make/buy proposal → capacity review → production execution.")

elif page == "Master Data":
    st.subheader("Manufacturing master data")
    tab1,tab2,tab3,tab4,tab5 = st.tabs(["Products","BOM","Routing","Work centres","Inventory"])
    with tab1: st.dataframe(products, use_container_width=True, hide_index=True)
    with tab2: st.dataframe(bom, use_container_width=True, hide_index=True)
    with tab3: st.dataframe(routing, use_container_width=True, hide_index=True)
    with tab4: st.dataframe(centres, use_container_width=True, hide_index=True)
    with tab5: st.dataframe(inventory, use_container_width=True, hide_index=True)
    st.markdown("### Master-data validation")
    checks = validate_master_data(data_dir)
    st.dataframe(checks, use_container_width=True, hide_index=True)
    if (checks.status == "PASS").all():
        st.success("All master-data validation checks passed.")
    else:
        st.error("One or more master-data checks failed. Review the table.")

elif page == "Material Requirements Planning":
    st.subheader("Material Requirements Planning (MRP)")
    st.write("Calculates demand from planned production orders, offsets available stock (on-hand less reservations and safety stock), and explodes the remaining make requirements through the BOM.")
    order_qty = st.number_input("Additional engine assembly demand", min_value=0, max_value=5000, value=0, step=10)
    if order_qty:
        extra = pd.DataFrame([{"production_order_id":"SIMULATION","product_id":"ENG-100","order_qty":order_qty,"due_date":"2026-11-30","priority":"MEDIUM","status":"PLANNED"}])
        combined = pd.concat([orders, extra], ignore_index=True)
    else:
        combined = orders
    mrp = calculate_mrp(data_dir, combined)
    st.dataframe(mrp, use_container_width=True, hide_index=True)
    buy = mrp[mrp.action == "BUY"]
    make = mrp[mrp.action == "MAKE"]
    a,b = st.columns(2)
    a.metric("Items requiring manufacture", len(make))
    b.metric("Items requiring purchase", len(buy))
    st.download_button("Download MRP results CSV", mrp.to_csv(index=False), "mrp_results.csv", "text/csv")

elif page == "Capacity Planning":
    st.subheader("Work-centre capacity review")
    qty = st.number_input("Production quantity for routing load simulation", min_value=1, max_value=10000, value=100, step=10)
    load = capacity_load(data_dir, qty)
    st.dataframe(load, use_container_width=True, hide_index=True)
    st.bar_chart(load.set_index("work_centre_name")[["required_hours","effective_daily_capacity_hours"]])
    st.caption("Illustrative aggregate routing-load estimate. A full finite scheduler would sequence orders by date, shift calendars, queue time and machine availability.")

elif page == "Engineering Change Demo":
    st.subheader("Engineering change request (ECR) – demonstration")
    st.write("Demonstrates a controlled revision proposal. This is a simplified PLM concept workflow, not a live SAP PLM transaction.")
    with st.form("ecr"):
        component = st.selectbox("Affected component", products[products.product_type.isin(["COMPONENT","SEMI_FINISHED"])].product_id.tolist())
        old_revision = st.text_input("Current revision", "A")
        new_revision = st.text_input("Proposed revision", "B")
        reason = st.text_area("Reason for change", "Improve component performance / reduce weight.")
        submitted = st.form_submit_button("Submit change request")
    if submitted:
        st.success(f"ECR created for {component}: revision {old_revision} → {new_revision}.")
        affected = bom[bom.component_product_id == component]
        st.markdown("**Direct parent products potentially affected by this component change:**")
        if affected.empty:
            st.write("No direct parent BOM records found.")
        else:
            st.dataframe(affected[["parent_product_id","component_product_id","quantity_per","revision"]], use_container_width=True, hide_index=True)
        st.warning("Before release, a real engineering change process would require impact assessment, approvals, effectivity control, stock disposition and production-order checks.")
