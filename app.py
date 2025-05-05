import streamlit as st
import cx_Oracle
import bcrypt
import os
from dotenv import load_dotenv
from Admin.Suppliers import supplier_data, supplier_groupby, supplier_loc
from Admin.Clusters import cluster_analysis
from User.Products import prod_cluster
from Admin.Clusters import view_cluster_data
from Admin.Clusters import update_product_cluster
from Admin.Products import view_product_data
from User.Transactions import conduct

# Load environment variables
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")


# Streamlit session state for authentication
if 'is_user' not in st.session_state:
    st.session_state.is_user = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Functions for authentication and database interaction
def create_connection():
    return cx_Oracle.connect(user=username, password=password, dsn=dsn)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def user_exists(cursor, name):
    cursor.execute("SELECT COUNT(*) FROM User_Data WHERE name) = :name", {'name': name})
    return cursor.fetchone()[0] > 0

def get_user_credentials(cursor, name):
    cursor.execute("SELECT user_id, role, password FROM User_Data WHERE name = :name", {'name': name})
    result = cursor.fetchone()
    if result:
        user_id, role, password_lob = result
        return user_id, role, password_lob.read()
    return None

def add_user(cursor, name, role, hashed_pw):
    cursor.setinputsizes(password=cx_Oracle.BLOB)
    cursor.execute(""" 
        INSERT INTO User_Data (name, role, password) 
        VALUES (:name, :role, :password)
    """, {'name': name, 'role': role, 'password': hashed_pw})

if not st.session_state['is_user'] and not st.session_state['is_admin']:
    st.title("🔐 Smart Inventory Management System")
    mode = st.radio("Choose Mode:", ["Login", "Signup"])
    name = st.text_input("Username")
    password_input = st.text_input("Password", type="password")

    if mode == "Signup":
        if st.button("Sign Up"):
            with create_connection() as conn:
                cursor = conn.cursor()
                if user_exists(cursor, name):
                    st.warning("User already exists!")
                else:
                    hashed = hash_password(password_input)
                    add_user(cursor, name, "user", hashed)
                    conn.commit()
                    st.success("Signup successful! You can now log in.")

    elif mode == "Login":
        if st.button("Login"):
            with create_connection() as conn:
                cursor = conn.cursor()
                creds = get_user_credentials(cursor, name)
                if not creds:
                    st.error("User not found.")
                else:
                    user_id, role, stored_pw = creds
                    if verify_password(password_input, stored_pw):
                        st.session_state['is_admin'] = (role.lower() == "admin")
                        st.session_state['is_user'] = (role.lower() == "user")
                        st.session_state['user_id'] = user_id
                        st.session_state['role'] = role
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect password.")

def fetch_all_product_names():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Products")
        return [row[0] for row in cursor.fetchall()]
    
product_names = fetch_all_product_names()  

if st.session_state['is_admin']:
    st.title("🔐 Smart Inventory Management System")
    st.success(f"Welcome, {st.session_state.role}!")

    # Logout functionality
    if st.button("Logout"):
        for key in ["is_user", "is_admin", "username", "role", "supplier_output"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Admin Dashboard
    st.subheader("Admin Dashboard")

    # Accordion-style collapsible sections for queries
    with st.expander("📦 Supplier Data"):
        supplier_tabs = st.tabs(["🔍 By Name", "📊 Group by Location", "🌍 Filter by Location"])

        # Supplier Info by Name
        with supplier_tabs[0]:
            supplier_name = st.text_input("Enter Supplier Name", key="supplier_name2")
            if st.button("Get Supplier Info", key="btn_supplier_info"):
                output = supplier_data.fetch_supplier_info(supplier_name)
                for line in output:
                    st.text(line)

        # Supplier Count Grouped by Location
        with supplier_tabs[1]:
            if st.button("Show Grouped Supplier Counts", key="btn_grouped"):
                grouped = supplier_groupby.fetch_supplier_groupby()
                for loc, count in grouped:
                    st.write(f"{loc}: {count} suppliers")

        # Filter Suppliers by Location (City, Country)
        with supplier_tabs[2]:
            city = st.text_input("City (optional)", key="city_input")
            country = st.text_input("Country (optional)", key="country_input")
            if st.button("Search by Location", key="btn_search_location"):
                data = supplier_loc.fetch_suppliers_by_location(city if city else None, country if country else None)
                for line in data:
                    st.text(line)

    # Cluster Queries Section
    with st.expander("🔢 Cluster Data"):
        cluster_tabs = st.tabs(["Filter Clusters", "Get Cluster data", "Update Product Cluster"])

        with cluster_tabs[0]:
            min_quantity = st.text_input("Minimum Avg Quantity", key="min_qty")
            min_price = st.text_input("Minimum Avg Price", key="min_price")
            min_sales = st.text_input("Minimum Avg Sales", key="min_sales")
            min_popularity = st.text_input("Minimum Popularity Score", key="min_pop")
            min_clusters = st.text_input("Number of Clusters", key="num_clusters")

            if st.button("Run Cluster Filter", key="btn_run_cluster_filter"):
                results = cluster_analysis.filter_clusters(
                    float(min_quantity) if min_quantity else None,
                    float(min_price) if min_price else None,
                    float(min_sales) if min_sales else None,
                    float(min_popularity)/100 if min_popularity else None,
                    float(min_clusters) if min_clusters else None
                )
                for line in results:
                    st.text(line)

        with cluster_tabs[1]:
            cluster_id = st.text_input("Enter Cluster ID", key="cluster_id")
            if st.button("Get Cluster Data", key="btn_cluster_data"):
                cluster_details = view_cluster_data.fetch_cluster_details(cluster_id)
                
                if "error" in cluster_details:
                    st.error(cluster_details["error"])
                else:
                    st.subheader(f"📦 Cluster ID: {cluster_details['Cluster ID']}")
                    st.markdown(f"**Average Quantity:** {cluster_details['Average Quantity']}")
                    st.markdown(f"**Average Price:** ₹{cluster_details['Average Price']}")
                    st.markdown(f"**Average Sales:** {cluster_details['Average Sales']}")
                    st.markdown(f"**Popularity Score:** {cluster_details['Popularity Score']*100}%")

                    # Nicely format Category Distribution
                    st.markdown("**🗂 Category Distribution:**")
                    for category in cluster_details['Category Distribution']:
                        st.markdown(f"- {category}")
                        
       # Tab 3 - Update Product Cluster
        with cluster_tabs[2]:
            st.markdown("### 🔄 Reassign Product to Cluster")
            product_id = st.text_input("Product ID", key="cluster_update_product_id")
            new_cluster_id = st.text_input("New Cluster ID", key="cluster_update_new_id")

            if st.button("Update Product Cluster", key="btn_update_cluster"):
                if product_id and new_cluster_id:
                    # ✅ Call your function here
                    result = update_product_cluster.update_product_cluster(
                        int(product_id),
                        int(new_cluster_id)
                    )

                    # ✅ Handle the response
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(result["success"])
                else:
                    st.warning("Please enter both Product ID and New Cluster ID.")


    with st.expander("📦 Product Data"):
        product_tabs = st.tabs(["View Product Data", "Update Product Cluster", "Stock In/Out Product"])

        with product_tabs[0]:

            selected_product = st.selectbox("Select a product to view details", product_names, key="view_product_name")

            if st.button("Get Product Info", key="btn_product_info"):
                product_data = view_product_data.fetch_product_data_by_name(selected_product)
                if "error" in product_data:
                    st.error(product_data["error"])
                else:
                    st.markdown("**📦 Product Information:**")
                    for k, v in product_data.items():
                        st.write(f"**{k}**: {v}")
        
        with product_tabs[2]:
            st.markdown("### 🔄 Conduct Transaction")
            product_name = st.selectbox("Select Product", product_names, key="conduct_product_name")
            quantity = st.number_input("Quantity (positive for stock-in, negative for stock-out)", key="conduct_quantity")
            user_id = st.session_state["user_id"] 
            
            if st.button("Conduct Transaction", key="btn_conduct_transaction"):
                if product_name and user_id:
                    result = conduct.call_conduct_transaction(product_name, int(quantity), int(user_id))
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(result["success"])
                else:
                    st.warning("Please enter both Product Name and User ID.")


elif st.session_state['is_user']:
    st.title("🔐 Smart Inventory Management System")
    st.success(f"Welcome, {st.session_state.role} {st.session_state.username}!")

    # Logout functionality
    if st.button("Logout"):
        for key in ["is_user", "is_admin", "username", "role"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.subheader("🧑‍💼 User Dashboard")

    with st.expander("📦 Product Recommendations"):
        with st.form("recommendation_form"):
            category = st.text_input("Enter Product Name or Category", placeholder="e.g. Electronics", key="user_category")
            submitted = st.form_submit_button("Recommend Items")

            if submitted and category:
                results = prod_cluster.recommend_items_by_category(category)
                if results:
                    st.markdown("### 📋 Recommended Items:")
                    for line in results:
                        st.text(line)
                else:
                    st.info("No recommendations found for that category.")
