import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- CONFIGURATION & DATABASE SETUP ---
st.set_page_config(page_title="Chennai Logistics Aggregator", layout="wide")
DB_FILE = "logistics_db.json"

# Initialize a database customized for the Chennai market if it doesn't exist
if not os.path.exists(DB_FILE):
    initial_data = {
        "operators": [
            {"id": 1, "name": "Muthu Chennai Fast Freight", "vehicle": "Tata Ace (Van)", "capacity": 850, "status": "Available"},
            {"id": 2, "name": "Annamalai Local Couriers", "vehicle": "Two-Wheeler", "capacity": 30, "status": "Available"},
            {"id": 3, "name": "Koyambedu Market Bulk Transport", "vehicle": "Eicher Pro (Truck)", "capacity": 4000, "status": "Busy"}
        ],
        "shipments": [
            {
                "id": "TRK-CH101",
                "cargo": "Fresh Tomatoes",
                "weight": 500,
                "pickup": "Koyambedu Wholesale Market",
                "destination": "Tambaram Delivery Hub",
                "operator": "Muthu Chennai Fast Freight",
                "status": "In Transit"
            }
        ]
    }
    with open(DB_FILE, "w") as f:
        json.dump(initial_data, f, indent=4)

def load_data():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚚 Chennai Logistics Hub")
st.sidebar.markdown("Select your portal view below:")
user_role = st.sidebar.radio("Go To View:", ["🌾 Producer Portal", "🚛 Operator Portal", "📦 Consumer Tracking"])

# --- 1. PRODUCER PORTAL ---
if user_role == "🌾 Producer Portal":
    st.title("🌾 Producer / Trader Dashboard")
    st.subheader("Book Shipments across Chennai & TN Hubs")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Request New Transport Match")
        with st.form("delivery_form", clear_on_submit=True):
            cargo = st.text_input("Goods / Produce Type", placeholder="e.g., Mangoes, Rice bags, Vegetables")
            weight = st.number_input("Total Load Weight (kg)", min_value=1, value=100)
            pickup = st.text_input("Pickup Location in Chennai", placeholder="e.g., Koyambedu, Madhavaram")
            destination = st.text_input("Drop Destination", placeholder="e.g., Guindy, Sriperumbudur, Tambaram")
           submit = st.form_submit_button("Match with Local Operator")
            
            if submit and cargo and pickup and destination:
                available_ops = [op for op in data["operators"] if op["status"] == "Available" and op["capacity"] >= weight]
                
                if available_ops:
                    best_op = min(available_ops, key=lambda x: x["capacity"])
                    shipment_id = f"TRK-{int(datetime.now().timestamp())}"
                    new_shipment = {
                        "id": shipment_id,
                        "cargo": cargo,
                        "weight": weight,
                        "pickup": pickup,
                        "destination": destination,
                        "operator": best_op["name"],
                        "status": "Assigned"
                    }
                    data["shipments"].append(new_shipment)
                    for op in data["operators"]:
                        if op["name"] == best_op["name"]:
                            op["status"] = "Busy"
                    save_data(data)
                    st.success(f"🎉 Matched with {best_op['name']} ({best_op['vehicle']})! Tracking ID: {shipment_id}")
                    st.rerun()
                else:
                    st.error("❌ No local vehicles with enough open capacity match this load size right now.")

    with col2:
        st.markdown("### Active Consignment Tracker")
        if not data["shipments"]:
            st.info("No active shipments on the log right now.")
        else:
            for s in reversed(data["shipments"]):
                with st.expander(f"📦 {s['cargo']} ({s['weight']}kg) -> ID: {s['id']}"):
                    st.write(f"**Route:** {s['pickup']} ➡️ {s['destination']}")
                    st.write(f"**Assigned Driver:** {s['operator']}")
                    
                    status = s["status"]
                    st.markdown(f"**Current Milestone:** `{status}`")
                    if status == "Assigned":
                        st.progress(25, text="Step 1/4: Driver Booked")
                    elif status == "Picked Up":
                        st.progress(50, text="Step 2/4: Loading Completed")
                    elif status == "In Transit":
                        st.progress(75, text="Step 3/4: On the Road / In Transit")
                    elif status == "Delivered":
                        st.progress(100, text="Step 4/4: Dispatched & Delivered Safely 🎉")

# --- 2. OPER
