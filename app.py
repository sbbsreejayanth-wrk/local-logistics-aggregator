import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION & DATABASE SETUP ---
st.set_page_config(page_title="NEO-CHENNAI | Autonomous Supply Chain Engine", layout="wide")
DB_FILE = "logistics_db.json"

# --- INITIALIZE STATE ENGINE FOR PORTAL ROUTING ---
if "current_view" not in st.session_state:
    st.session_state["current_view"] = "SPLASH"

# --- THE PREMIUM ENTERPRISE GLASSMORPHISM CSS ENGINE ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

        /* Global Theme Overrides - Forcing transparency across structural containers */
        .stApp, .main, .block-container, [data-testid="stAppViewContainer"] {
            background: transparent !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Force highly visible typography colors over the dark background */
        .stApp, .stMarkdown, p, span, div, .stText, label {
            color: #f3f4f6 !important;
        }
        
        /* Premium Glow Section Headers */
        h1 {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
            color: #00FFCC !important;
            letter-spacing: -1px;
            text-transform: uppercase;
            text-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
            margin-bottom: 25px !important;
        }
        h2, h3 {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 600 !important;
            color: #ffffff !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 8px;
            margin-top: 20px !important;
        }

        /* Glassmorphic Data Cards & Widgets */
        div[data-testid="stMetricBlock"], .streamlit-expanderHeader, div.stForm, .premium-card {
            background: rgba(11, 15, 23, 0.8) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(0, 255, 204, 0.15) !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6) !important;
            padding: 24px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        div[data-testid="stMetricBlock"]:hover, .premium-card:hover {
            border-color: rgba(0, 255, 204, 0.4) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 255, 204, 0.2) !important;
            transform: translateY(-3px);
        }

        /* Metric Alignments */
        div[data-testid="stMetricBlock"] [data-testid="stMetricLabel"] p {
            color: #9ca3af !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }
        div[data-testid="stMetricBlock"] [data-testid="stMetricValue"] div {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }

        /* Form Controls */
        label, [data-testid="stWidgetLabel"] p {
            color: #9ca3af !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
        }
        
        input, select, textarea, div[data-baseweb="select"] {
            background-color: #0b0f17 !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
        }

        /* Tables */
        .stDataFrame div, table, th, td, [data-testid="stTable"] {
            color: #e5e7eb !important;
            background-color: #111827 !important;
            border-collapse: collapse;
        }
        th {
            background-color: #1f2937 !important;
            font-family: 'JetBrains Mono', monospace !important;
            color: #00FFCC !important;
            text-transform: uppercase;
            font-size: 0.8rem;
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #1f2937 0%, #111827 100%) !important;
            color: #00FFCC !important;
            border: 1px solid #00FFCC !important;
            border-radius: 8px !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 600 !important;
            padding: 12px 28px !important;
            letter-spacing: 0.5px;
            transition: all 0.4s ease-in-out !important;
            width: 100%;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #00FFCC 0%, #00E6B8 100%) !important;
            color: #0b0f17 !important;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.4) !important;
            border-color: #00FFCC !important;
        }

        div[data-testid="stTabBar"] button {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.9rem !important;
            color: #9ca3af !important;
            background: transparent !important;
            border: none !important;
        }
        div[data-testid="stTabBar"] button[aria-selected="true"] {
            color: #00FFCC !important;
            border-bottom: 2px solid #00FFCC !important;
        }

        section[data-testid="stSidebar"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT GLOBAL BACKGROUND ANIMATION CANVAS ---
st.components.v1.html("""
    <canvas id="networkCanvas" style="position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:-1; background:#0b0f17;"></canvas>
    <script>
        const canvas = document.getElementById('networkCanvas');
        const ctx = canvas.getContext('2d');
        let particles = [];
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.radius = Math.random() * 2 + 1.5;
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0, 255, 204, 0.6)';
                ctx.fill();
            }
        }

        for (let i = 0; i < 100; i++) {
            particles.push(new Particle());
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Core space depth gradient
            let gradient = ctx.createRadialGradient(canvas.width/2, canvas.height/2, 10, canvas.width/2, canvas.height/2, canvas.width);
            gradient.addColorStop(0, '#111827');
            gradient.addColorStop(1, '#070a10');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();
                
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    
                    if (dist < 150) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(0, 255, 204, ${1 - (dist / 150) * 0.25})`;
                        ctx.lineWidth = 0.6;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animate);
        }
        animate();
    </script>
""", height=0, width=0)

# --- SYSTEM ECOSYSTEM DATABASE LAYER ---
default_operators = [
    {"id": 1, "name": "Muthu Chennai Fast Freight", "vehicle": "Tata Ace (Van)", "capacity": 1000, "status": "Available", "rate_per_km": 30, "wallet_balance": 4500},
    {"id": 2, "name": "Annamalai Local Couriers", "vehicle": "Two-Wheeler", "capacity": 100, "status": "Available", "rate_per_km": 12, "wallet_balance": 1200},
    {"id": 3, "name": "Koyambedu Market Bulk Transport", "vehicle": "Eicher Pro (Truck)", "capacity": 5000, "status": "Available", "rate_per_km": 65, "wallet_balance": 18200}
]

if not os.path.exists(DB_FILE):
    initial_data = {
        "producer_wallet": 75000,
        "supplier_wallet": 150000,
        "market_wallet": 90000,
        "customer_wallet": 35000,
        "farm_harvest_piles": [
            {"id": "HVST-001", "crop": "Raw Tomatoes", "qty": 2000, "status": "Unsold"}
        ],
        "supplier_raw_stock": 0,
        "supplier_refined_inventory": [
            {"id": "REFN-001", "product": "Tomato Purée Cases", "qty": 50, "status": "In Warehouse Storage"}
        ],
        "warehouses": {
            "Madhavaram Hub": {"capacity": 5000, "current_stock": 500},
            "Tambaram Hub": {"capacity": 3000, "current_stock": 200}
        },
        "market_inventory": {
            "Koyambedu Wholesale Stall": 120,
            "T. Nagar Supermarket Outpost": 40
        },
        "operators": default_operators,
        "shipments": [],
        "tickets": []
    }
    with open(DB_FILE, "w") as f:
        json.dump(initial_data, f, indent=4)

def load_data():
    with open(DB_FILE, "r") as f: return json.load(f)
def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

data = load_data()

HUB_COORDINATES = {
    "koyambedu": [13.0692, 80.1948], "tambaram": [12.9229, 80.1275], "madhavaram": [13.1068, 80.2184],
    "guindy": [13.0067, 80.2206], "sriperumbudur": [12.9724, 79.9515], "t. nagar (alley 1)": [13.0324, 80.2337],
    "sowcarpet (alley 2)": [13.0978, 80.2792], "parrys (alley 3)": [13.0945, 80.2891]
}

def create_satellite_map(center_coords, zoom=11):
    sat_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    labels_url = "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}"
    m = folium.Map(location=center_coords, zoom_start=zoom, tiles=sat_url, attr="Esri Maxar")
    folium.TileLayer(tiles=labels_url, attr="Esri Labels", overlay=True, control=False).add_to(m)
    folium.Circle(location=[13.04, 80.22], radius=12000, color="#00FFCC", fill=True, fill_color="#00FFCC", fill_opacity=0.04).add_to(m)
    return m

def render_navigation_header(title, return_target="HOME"):
    c_b1, c_b2 = st.columns([8, 2])
    with c_b1:
        st.markdown(f"<p style='font-family:\"JetBrains Mono\"; color:#00FFCC; margin:0;'>NETWORK NODE // {title.upper()}</p>", unsafe_allow_html=True)
    with c_b2:
        button_label = "◀ Control Matrix Home" if return_target == "HOME" else "◀ Corporate Overview"
        if st.button(button_label):
            st.session_state["current_view"] = return_target
            st.rerun()
    st.markdown("---")

# ==========================================
# 🌌 CORPORATE SPLASH DECK
# ==========================================
if st.session_state["current_view"] == "SPLASH":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:3.5rem; margin-bottom:10px;'>⚡ NEO-CHENNAI OPERATIONS LABS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00FFCC; font-family:\"JetBrains Mono\"; font-size:1.1rem; letter-spacing: 2px; margin-bottom:50px;'>Next-Gen Autonomous Supply Chain Infrastructure</p>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.markdown("""
            <div class='premium-card' style='margin-bottom:20px;'>
                <h2 style='color:#ffffff; margin-top:0;'>Corporate Profile</h2>
                <p style='color:#d1d5db; line-height:1.7;'>
                    Neo-Chennai Operations Labs builds resilient digital networks to orchestrate complex logistics workflows. 
                    By replacing fragmented intermediaries with unified tokenized escrow pools, autonomous routing rules, and multi-modal transit layers, 
                    we seamlessly bridge physical production pipelines with retail marketplaces.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🛠️ Core Infrastructure Superpowers")
        f_c1, f_c2 = st.columns(2)
        with f_c1:
            st.markdown("""
                <div class='premium-card' style='padding:15px !important;'>
                    <h4 style='color:#00FFCC; margin:0;'>🔗 Smart Escrow Clearing</h4>
                    <p style='color:#9ca3af; font-size:0.8rem; margin:5px 0 0 0;'>Frictionless capital locks released instantly upon geolocation drop verification.</p>
                </div>
            """, unsafe_allow_html=True)
        with f_c2:
            st.markdown("""
                <div class='premium-card' style='padding:15px !important;'>
                    <h4 style='color:#00FFCC; margin:0;'>⚡ Multi-Modal Splitting</h4>
                    <p style='color:#9ca3af; font-size:0.8rem; margin:5px 0 0 0;'>Dynamically splits freight cargo onto inner-city micromobility units when gridlock points form.</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Initialize Core Platform Matrix 🚀", key="enter_platform"):
            st.session_state["current_view"] = "HOME"
            st.rerun()

    with col_right:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>🌐 Live Telemetry Footprint</h3>", unsafe_allow_html=True)
        st.caption("Active logistical node points tracking across the metropolitan territory map.")
        m_splash = create_satellite_map([13.04, 80.22], zoom=10)
        for name, coord in HUB_COORDINATES.items():
            folium.CircleMarker(
                location=coord, radius=6, color="#00FFCC", fill=True, fill_color="#00FFCC", fill_opacity=0.7, popup=name.upper()
            ).add_to(m_splash)
        st_folium(m_splash, width="100%", height=350, key="splash_map", returned_objects=[])
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 🏠 CENTRAL INTERFACE MATRIX GRID (HOME)
# ==========================================
elif st.session_state["current_view"] == "HOME":
    render_navigation_header("Control Matrix Mainframe", return_target="SPLASH")
    st.markdown("<h1 style='text-align:center; font-size:2.8rem;'>⚡ SYSTEM PORTAL REGISTRY</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#9ca3af; font-family:\"JetBrains Mono\"; margin-bottom:50px;'>Orchestrate, verify, and pass inventory tracking updates downstream through all 6 echelons</p>", unsafe_allow_html=True)
    
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    row2_c1, row2_c2, row2_c3 = st.columns(3)
    
    with row1_c1:
        st.markdown("<div class='premium-card'><h3>🌾 1. PRODUCER</h3><p style='color:#9ca3af; font-size:0.85rem;'>Manage farmgate crop harvests and execute raw sales orders with downstream processors.</p></div>", unsafe_allow_html=True)
        if st.button("Access Producer Node"): st.session_state["current_view"] = "PRODUCER"; st.rerun()
            
    with row1_c2:
        st.markdown("<div class='premium-card'><h3>🧪 2. SUPPLIER</h3><p style='color:#9ca3af; font-size:0.85rem;'>Procure raw farm loads, run packaging refinery lines, and dispatch stock to warehouses.</p></div>", unsafe_allow_html=True)
        if st.button("Access Supplier Processing"): st.session_state["current_view"] = "SUPPLIER"; st.rerun()
            
    with row1_c3:
        st.markdown("<div class='premium-card'><h3>🏬 3. WAREHOUSE</h3><p style='color:#9ca3af; font-size:0.85rem;'>Audit dynamic space storage capacity constraints and authorize regional cross-dock dispatches.</p></div>", unsafe_allow_html=True)
        if st.button("Access Micro-Hub Network"): st.session_state["current_view"] = "WAREHOUSE"; st.rerun()
            
    with row2_c1:
        st.markdown("<div class='premium-card'><h3>🚛 4. TRANSPORT / OPERATOR</h3><p style='color:#9ca3af; font-size:0.85rem;'>Manage core fleet carrier routes, map dynamic highway telemetry, and engage multi-modal runs.</p></div>", unsafe_allow_html=True)
        if st.button("Access Carrier Rails"): st.session_state["current_view"] = "OPERATOR"; st.rerun()
            
    with row2_c2:
        st.markdown("<div class='premium-card'><h3>🏪 5. MARKET / SELLER</h3><p style='color:#9ca3af; font-size:0.85rem;'>Monitor wholesale/retail shelf stocks and initialize automated stock replacement requests.</p></div>", unsafe_allow_html=True)
        if st.button("Access Storefront Engine"): st.session_state["current_view"] = "MARKET"; st.rerun()
            
    with row2_c3:
        st.markdown("<div class='premium-card'><h3>📦 6. CUSTOMER GATEWAY</h3><p style='color:#9ca3af; font-size:0.85rem;'>Top up unified wallets, complete checkouts, file service tickets, and map real-time cargo radar lines.</p></div>", unsafe_allow_html=True)
        if st.button("Access Customer Portal"): st.session_state["current_view"] = "CUSTOMER"; st.rerun()

# ==========================================
# 🌾 ECHELON 1: PRODUCER NODE
# ==========================================
elif st.session_state["current_view"] == "PRODUCER":
    render_navigation_header("Producer Core Farm Gate")
    st.metric(label="🛡️ Farm Enterprise Financial Reserve", value=f"₹{data['producer_wallet']:,}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🪵 Record Daily Crop Yield Harvest")
        with st.form("harvest_form", clear_on_submit=True):
            crop_name = st.selectbox("Select Crop Variant", ["Raw Tomatoes", "Organic Paddy", "Premium Jasmine Flora"])
            qty_kg = st.number_input("Harvest Net Mass Weight (kg)", min_value=100, max_value=20000, value=1000, step=500)
            if st.form_submit_button("Log Into Farm Ledger"):
                h_id = f"HVST-{random.randint(100, 999)}"
                data["farm_harvest_piles"].append({"id": h_id, "crop": crop_name, "qty": int(qty_kg), "status": "Unsold"})
                save_data(data)
                st.toast("Harvest recorded in farm inventory.", icon="🌾")
                st.rerun()
                
    with col2:
        st.markdown("### 🌾 Active Farm Inventory Piles")
        if not data["farm_harvest_piles"]: st.info("No raw harvest clusters resting at farm nodes.")
        else:
            for hp in data["farm_harvest_piles"]:
                st.markdown(f"**ID:** `{hp['id']}` | **Crop:** `{hp['crop']}` | **Weight:** `{hp['qty']} kg` -> Status: `{hp['status']}`")

# ==========================================
# 🧪 ECHELON 2: SUPPLIER NODE
# ==========================================
elif st.session_state["current_view"] == "SUPPLIER":
    render_navigation_header("Supplier & Refinery Engine")
    st.metric(label="🧪 Branded Supplier Business Capital", value=f"₹{data['supplier_wallet']:,}")
    
    tab_buy, tab_refine, tab_ship = st.tabs(["🌾 Farm Procurement", "⚙️ Factory Packaging Lines", "🚚 Logistics Fulfillment Setup"])
    
    with tab_buy:
        st.markdown("### Buy Raw Yield From Local Producers")
        unsold_harvests = [h for h in data["farm_harvest_piles"] if h["status"] == "Unsold"]
        if not unsold_harvests: st.info("No farm gate harvest piles available to acquire right now.")
        else:
            for uh in unsold_harvests:
                cost = uh["qty"] * 15
                st.markdown(f"📦 **Ref:** `{uh['id']}` | **Produce:** {uh['crop']} ({uh['qty']} kg) | **Purchase Cost:** `₹{cost:,}`")
                if st.button(f"Purchase and Intake ({uh['id']})", key=f"buy_{uh['id']}"):
                    if data["supplier_wallet"] >= cost:
                        data["supplier_wallet"] -= cost
                        data["producer_wallet"] += cost
                        uh["status"] = "Purchased by Supplier"
                        data["supplier_raw_stock"] += uh["qty"]
                        save_data(data)
                        st.toast("Procurement funds distributed. Raw stock transferred.", icon="✅")
                        st.rerun()
                    else: st.error("Insufficient supplier business capital.")
                    
    with tab_refine:
        st.markdown("### Process and Package Retail Goods")
        st.metric("Stored Raw Supply Pool Balance", value=f"{data['supplier_raw_stock']} kg")
        with st.form("refine_form"):
            st.caption("Converts 500 kg raw farm inputs into 20 commercial product boxes.")
            product_type = st.selectbox("Output Product Unit", ["Tomato Purée Cases", "Premium Rice Packages", "Essential Oils"])
            if st.form_submit_button("Initiate Factory Assembly Line"):
                if data["supplier_raw_stock"] >= 500:
                    data["supplier_raw_stock"] -= 500
                    r_id = f"REFN-{random.randint(100, 999)}"
                    data["supplier_refined_inventory"].append({"id": r_id, "product": product_type, "qty": 20, "status": "Ready at Factory Side"})
                    save_data(data)
                    st.toast("Refining cycle completed.", icon="⚙️")
                    st.rerun()
                else: st.error("Insufficient raw stock reserves to fuel automated production loops.")
                
    with tab_ship:
        st.markdown("### Dispatch Processed Inventory to Regional Warehouse Clusters")
        ready_stock = [r for r in data["supplier_refined_inventory"] if r["status"] == "Ready at Factory Side"]
        if not ready_stock: st.info("No finished product stocks currently waiting at the factory site.")
        else:
            for rs in ready_stock:
                st.markdown(f"📦 **Ref:** `{rs['id']}` | **Product Stack:** {rs['product']} ({rs['qty']} units)")
                target_wh = st.selectbox("Select Target Micro-Warehouse Hub:", list(data["warehouses"].keys()), key=f"wh_sel_{rs['id']}")
                target_carrier = st.selectbox("Assign Fleet Transit Carrier Line:", [op["name"] for op in data["operators"] if op["status"] == "Available"], key=f"op_sel_{rs['id']}")
                
                if st.button(f"Book Freight Routing ({rs['id']})", key=f"bk_{rs['id']}"):
                    mock_dist = random.randint(15, 45)
                    op_rate = next(o["rate_per_km"] for o in data["operators"] if o["name"] == target_carrier)
                    fare = mock_dist * op_rate
                    
                    if data["supplier_wallet"] >= fare:
                        data["supplier_wallet"] -= fare
                        s_id = f"TRK-{int(datetime.now().timestamp())}"
                        data["shipments"].append({
                            "id": s_id, "cargo": rs["product"], "weight": rs["qty"] * 10,
                            "pickup": "Factory Refinery Node", "destination": target_wh,
                            "operator": target_carrier, "status": "Assigned", "distance": mock_dist, "fare": fare,
                            "gate_queue": 0, "is_split": False, "child_trips": [], "payment_status": "Paid (In Escrow)",
                            "linked_refined_id": rs["id"]
                        })
                        rs["status"] = "In Transit to Warehouse Hub"
                        for o in data["operators"]:
                            if o["name"] == target_carrier: o["status"] = "Busy"
                        save_data(data)
                        st.toast("Fulfillment run assigned. Funds locked in transport escrow.", icon="🔒")
                        st.rerun()
                    else: st.error("Insufficient capital to cover freight charges.")

# ==========================================
# 🏬 ECHELON 3: WAREHOUSE NODE
# ==========================================
elif st.session_state["current_view"] == "WAREHOUSE":
    render_navigation_header("Regional Warehouse Footprint")
    st.markdown("### 🏬 Cross-Dock Warehouse Micro-Hub Footprint Utilization")
    wh_cols = st.columns(len(data["warehouses"]))
    idx = 0
    for w_name, w_info in data["warehouses"].items():
        with wh_cols[idx]:
            st.metric(label=f"🏢 {w_name}", value=f"{w_info['current_stock']} / {w_info['capacity']} Units Stored")
            st.progress(w_info["current_stock"] / w_info["capacity"])
        idx += 1
        
    st.markdown("<br>### 📦 Internal Inventory Item Ledger Tracking Sheets", unsafe_allow_html=True)
    wh_items = [r for r in data["supplier_refined_inventory"] if r["status"] == "In Warehouse Storage"]
    if not wh_items: st.info("No active commercial products sitting inside micro-hub inventory zones.")
    else:
        for wi in wh_items:
            st.markdown(f"🗳️ **Batch Target ID:** `{wi['id']}` | **Product Variant:** {wi['product']} | **In Stock Volume:** `{wi['qty']} Units`")

# ==========================================
# 🚛 ECHELON 4: TRANSPORT / OPERATOR ENGINE
# ==========================================
elif st.session_state["current_view"] == "OPERATOR":
    render_navigation_header("Transporter Fleet Controller")
    st.title("🚛 CARRIER DISPATCH DECK")
    col1, col2, col3 = st.columns([1.2, 1.4, 1.5])
    
    with col1:
        st.markdown("### DISPATCH MANAGEMENT METRICS")
        st.dataframe(pd.DataFrame(data["operators"])[["name", "vehicle", "wallet_balance", "status"]], use_container_width=True, hide_index=True)
        
        st.markdown("### COMPLIANCE TICKETS")
        if not data.get("tickets"): st.info("Zero active system compliance disputes.")
        for tk in data["tickets"]:
            with st.expander(f"🎫 [{tk['type']}] Ref: {tk['shipment_id']}"):
                st.caption(f"Status: {tk['status']} | Log: {tk['issue_text']}")
                if tk["status"] == "Open" and st.button("Flag as Settled", key=f"res_{tk['timestamp']}"):
                    tk["status"] = "Resolved"
                    save_data(data)
                    st.toast("Support conflict set to resolved.", icon="✅")
                    st.rerun()

    with col2:
        st.markdown("### TELEMETRY STATE MACHINE CARDS")
        active_jobs = [s for s in data["shipments"] if s["status"] != "Delivered"]
        if not active_jobs: st.info("No cargo routing contracts actively queued across network channels.")
        for s in active_jobs:
            st.markdown(f"⚙️ **{s['cargo']}** Asset Carrier: `{s['operator']}`")
            c_state = s["status"]
            if not s.get("is_split"):
                if c_state == "Assigned" and st.button(f"Confirm Intake (ID: {s['id']})", key=f"pk_{s['id']}"):
                    s["status"] = "Picked Up"; save_data(data); st.rerun()
                elif c_state == "Picked Up" and st.button(f"Inject into Highway (ID: {s['id']})", key=f"it_{s['id']}"):
                    s["status"] = "In Transit"; save_data(data); st.rerun()
                elif c_state == "In Transit":
                    if st.button(f"⚠️ Flag Gate Queue Hold (ID: {s['id']})", key=f"stk_{s['id']}"):
                        s["status"] = "Stuck at Gate Queue"; s["gate_queue"] = random.randint(5, 18); save_data(data); st.rerun()
                    if st.button(f"⚡ Deploy Multi-Modal Split", key=f"splt_{s['id']}"):
                        s["is_split"] = True; s["status"] = "Split Delivery Last-Mile"
                        loc = "T. Nagar (Alley 1)" if "nagar" in s["destination"].lower() else "Sowcarpet (Alley 2)"
                        s["child_trips"] = [{"runner": f"Runner-Asset {i}", "status": "Out bound", "loc": loc} for i in ["A", "B", "C"]]
                        save_data(data); st.rerun()
                    if st.button(f"✅ Safe Handoff & Release Escrow (ID: {s['id']})", key=f"dc_{s['id']}"):
                        s["status"] = "Delivered"; s["payment_status"] = "Released to Operator"
                        if s["destination"] in data["warehouses"]:
                            data["warehouses"][s["destination"]]["current_stock"] += int(s["weight"] / 10)
                        
                        if "linked_refined_id" in s:
                            for idx_item in data["supplier_refined_inventory"]:
                                if idx_item["id"] == s["linked_refined_id"]: idx_item["status"] = "In Warehouse Storage"
                                
                        for o in data["operators"]:
                            if o["name"] == s["operator"]: o["wallet_balance"] += s.get("fare", 0); o["status"] = "Available"
                        save_data(data); st.toast("Cargo delivery verified. Funds transferred to wallet.", icon="💸"); st.rerun()
            else:
                if st.button(f"🏁 Complete Multi-trip Route Chain (ID: {s['id']})", key=f"fnbk_{s['id']}"):
                    s["status"] = "Delivered"; s["payment_status"] = "Released to Operator"
                    if s["destination"] in data["warehouses"]:
                        data["warehouses"][s["destination"]]["current_stock"] += int(s["weight"] / 10)
                    for o in data["operators"]:
                        if o["name"] == s["operator"]: o["wallet_balance"] += s.get("fare", 0); o["status"] = "Available"
                    save_data(data); st.toast("Multi-trip flow settled.", icon="🏁"); st.rerun()

    with col3:
        st.markdown("### LINE DISPATCH TELEMETRY")
        m_op = create_satellite_map([13.0827, 80.2707], zoom=11)
        for job in active_jobs:
            coords = HUB_COORDINATES["koyambedu"]
            for k in HUB_COORDINATES:
                if k in job["pickup"].lower() or k in job["destination"].lower(): coords = HUB_COORDINATES[k]
            folium.Marker(coords, popup=f"{job['cargo']}: {job['status']}", icon=folium.Icon(color='red')).add_to(m_op)
        st_folium(m_op, width="100%", height=500, key="op_map", returned_objects=[])

# ==========================================
# 🏪 ECHELON 5: MARKET / SELLER NODE
# ==========================================
elif st.session_state["current_view"] == "MARKET":
    render_navigation_header("Market Storefront Outlet")
    c_m1, c_m2 = st.columns(2)
    with c_m1: st.metric(label="🏪 Market Merchant Cash Vault Balance", value=f"₹{data['market_wallet']:,}")
    
    st.markdown("<br>### 🏪 Local Storefront Shelf Allocations Inventory", unsafe_allow_html=True)
    m_col1, m_col2 = st.columns(2)
    with m_col1: st.metric("Koyambedu Wholesale Stall Stock", value=f"{data['market_inventory']['Koyambedu Wholesale Stall']} Units")
    with m_col2: st.metric("T. Nagar Supermarket Outpost Stock", value=f"{data['market_inventory']['T. Nagar Supermarket Outpost']} Units")
        
    st.markdown("<br>### ⚡ Run Supply Chain Replenishment Flow", unsafe_allow_html=True)
    with st.form("replenish_form"):
        from_wh = st.selectbox("Pull From Warehouse Hub Source:", list(data["warehouses"].keys()))
        to_market = st.selectbox("Inject Target Storefront Node Location:", list(data["market_inventory"].keys()))
        pull_qty = st.number_input("Replenish Allocation Units Quantity", min_value=10, max_value=500, value=50, step=10)
        
        if st.form_submit_button("Trigger Stock Pipeline Transport Request"):
            if data["warehouses"][from_wh]["current_stock"] >= pull_qty:
                data["warehouses"][from_wh]["current_stock"] -= int(pull_qty)
                mock_dist = random.randint(10, 30)
                fare = mock_dist * 30
                
                s_id = f"TRK-RPL-{int(datetime.now().timestamp())}"
                data["shipments"].append({
                    "id": s_id, "cargo": "Refined Bulk Store Replenishment", "weight": int(pull_qty * 10),
                    "pickup": from_wh, "destination": to_market,
                    "operator": "Muthu Chennai Fast Freight", "status": "Assigned", "distance": mock_dist, "fare": fare,
                    "gate_queue": 0, "is_split": False, "child_trips": [], "payment_status": "Paid (In Escrow)"
                })
                data["market_inventory"][to_market] += int(pull_qty)
                save_data(data)
                st.toast("Store replenishment transport request sent. Freight routed.", icon="🏪")
                st.rerun()
            else: st.error("Target warehouse lacks sufficient stock allocations.")

# ==========================================
# 📦 ECHELON 6: CUSTOMER GATEWAY
# ==========================================
elif st.session_state["current_view"] == "CUSTOMER":
    render_navigation_header("Consumer Gateway Interface")
    c_pay1, c_pay2 = st.columns(2)
    with c_pay1: st.metric(label="💳 UNIFIED PREPAID CUSTOMER WALLET BALANCE", value=f"₹{data['customer_wallet']:,}")
    with c_pay2: st.metric(label="📈 TOTAL CARGO RUNS VERIFIED", value=len(data["shipments"]))
        
    st.markdown("<br>", unsafe_allow_html=True)
    tab_checkout, tab_billing, tab_radar, tab_disputes = st.tabs([
        "🛒 Retail Direct Checkout", "💳 Top-Up Terminal Engine", "📦 Cargo Live Radar", "🎫 Service Escalation Desk"
    ])
    
    with tab_checkout:
        st.markdown("### Buy Packaged Finished Goods Directly")
        target_store = st.selectbox("Select Storefront Terminal Target Area:", list(data["market_inventory"].keys()))
        current_store_stock = data["market_inventory"][target_store]
        st.write(f"Available Shelf Inventory at Node: `{current_store_stock} Units`")
        
        with st.form("purchase_goods_form"):
            buy_units = st.number_input("Purchase Volume Units", min_value=1, max_value=20, value=2)
            cost_total = buy_units * 120
            st.markdown(f"**Gross Total Invoiced Price:** `₹{cost_total:,}`")
            
            if st.form_submit_button("Authorize Payment & Checkout Order"):
                if data["customer_wallet"] >= cost_total:
                    if data["market_inventory"][target_store] >= buy_units:
                        data["customer_wallet"] -= cost_total
                        data["market_wallet"] += cost_total
                        data["market_inventory"][target_store] -= int(buy_units)
                        save_data(data)
                        st.toast("Purchase verified! Inventory deducted from retail node.", icon="🛍️")
                        st.rerun()
                    else: st.error("Insufficient storefront shelf stocks.")
                else: st.error("Insufficient personal consumer wallet cash reserves.")
                
    with tab_billing:
        cx_col1, cx_col2 = st.columns([1.1, 0.9])
        with cx_col1:
            st.markdown("### Secure Digital Wallet Top-Up Portal")
            with st.form("wallet_topup_form", clear_on_submit=True):
                topup_amount = st.number_input("Top-up Amount (INR)", min_value=100, max_value=100000, value=5000, step=500)
                pay_c1, pay_c2 = st.columns(2)
                with pay_c1: card_num = st.text_input("Debit / Corporate Card Number", value="•••• •••• •••• 4242")
                with pay_c2: card_expiry = st.text_input("Expiry Date / CVV", value="12/29 | •••")
                    
                if st.form_submit_button("Authorize Digital Fund Transfer"):
                    data["customer_wallet"] += int(topup_amount)
                    save_data(data)
                    st.toast(f"Wallet successfully charged with ₹{topup_amount:,}", icon="💳")
                    st.rerun()
                    
        with cx_col2:
            st.markdown("### Active System Invoices")
            if not data["shipments"]: st.info("No active billing chains detected.")
            else:
                for s in reversed(data["shipments"]):
                    inv_status = "🟢 SETTLED" if s["status"] == "Delivered" else "🔒 ESCROW HOLD"
                    with st.expander(f"🧾 INV-{s['id']} [{inv_status}]"):
                        base_fare = s.get("fare", 0)
                        st.markdown(f"**Gross Value:** `₹{base_fare:,}`")

    with tab_radar:
        st.markdown("### Live Pathway Telemetry Vector")
        search_id = st.text_input("INPUT SYSTEM ENCRYPTED TRACKING ID", placeholder="e.g., TRK-CH101")
        if search_id:
            match_found = next((s for s in data["shipments"] if s["id"] == search_id), None)
            if match_found:
                st.success(f"Security Clearance Verified | Manifest: **{match_found['cargo']}**")
                st.markdown(f"💰 **Freight Cost:** `₹{match_found.get('fare', 0)}` | **Escrow State:** `{match_found.get('payment_status')}`")
                if match_found.get("is_split"):
                    for rn in match_found["child_trips"]: st.markdown(f"* `[ASSET]` **{rn['runner']}** -> State: `{rn['status']}` ({rn['loc']})")
                else: st.metric("CURRENT FREIGHT STATE TIMELINE STATUS", value=match_found["status"])
            else: st.error("Tracking reference sequence unrecognized in database cluster.")
            
        m_cust = create_satellite_map([13.0827, 80.2707], zoom=11)
        st_folium(m_cust, width="100%", height=400, key="cust_map", returned_objects=[])

    with tab_disputes:
        st.markdown("### System Compliance Escalations")
        with st.form("ticket_form", clear_on_submit=True):
            t_id = st.text_input("Linked Manifest Reference Target ID", placeholder="e.g., TRK-CH101")
            i_type = st.selectbox("Dispute Class Vector", ["Delayed Delivery Network State", "Damaged Physical Cargo", "Operator Ledger Inconsistency"])
            i_desc = st.text_area("Provide Comprehensive Incident Logs")
            if st.form_submit_button("Transmit Ticket to Dispatch Desk") and t_id and i_desc:
                data["tickets"].append({"shipment_id": t_id, "type": i_type, "issue_text": i_desc, "status": "Open", "timestamp": int(datetime.now().timestamp())})
                save_data(data)
                st.toast("Dispute logged. Operators flagged.", icon="🎫")
                st.rerun()
