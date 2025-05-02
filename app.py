import streamlit as st
import cx_Oracle
import bcrypt
import os
from dotenv import load_dotenv
from Admin.Suppliers.supplier_data import fetch_supplier_info
from Admin.Suppliers.supplier_groupby import fetch_supplier_groupby
from Admin.Suppliers.supplier_loc import fetch_suppliers_by_location
from Admin.Clusters.cluster_analysis import filter_clusters

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
if 'username' not in st.session_state:
    st.session_state.username = None

# Functions for authentication and database interaction
def create_connection():
    return cx_Oracle.connect(user=username, password=password, dsn=dsn)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def user_exists(cursor, name):
    cursor.execute("SELECT COUNT(*) FROM User_Data WHERE LOWER(name) = LOWER(:name)", {'name': name})
    return cursor.fetchone()[0] > 0

def get_user_credentials(cursor, name):
    cursor.execute("SELECT role, password FROM User_Data WHERE LOWER(name) = LOWER(:name)", {'name': name})
    result = cursor.fetchone()
    if result:
        role, password_lob = result
        return role, password_lob.read()
    return None

def add_user(cursor, name, role, hashed_pw):
    cursor.setinputsizes(password=cx_Oracle.BLOB)
    cursor.execute(""" 
        INSERT INTO User_Data (name, role, password) 
        VALUES (:name, :role, :password)
    """, {'name': name, 'role': role, 'password': hashed_pw})

# Main login/signup page
if not st.session_state['is_user'] or not st.session_state['is_admin']:
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
                    role, stored_pw = creds
                    if verify_password(password_input, stored_pw):
                        st.session_state['is_user'] = True
                        st.session_state['is_admin'] = (role.lower() == "admin")
                        st.session_state['username'] = name
                        st.session_state['role'] = role
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect password.")

# If the user is authenticated and is an admin
if st.session_state['is_admin']:
    st.success(f"Welcome, {st.session_state.role} {st.session_state.username}!")

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
                output = fetch_supplier_info(supplier_name)
                for line in output:
                    st.text(line)

        # Supplier Count Grouped by Location
        with supplier_tabs[1]:
            if st.button("Show Grouped Supplier Counts", key="btn_grouped"):
                grouped = fetch_supplier_groupby()
                for loc, count in grouped:
                    st.write(f"{loc}: {count} suppliers")

        # Filter Suppliers by Location (City, Country)
        with supplier_tabs[2]:
            city = st.text_input("City (optional)", key="city_input")
            country = st.text_input("Country (optional)", key="country_input")
            if st.button("Search by Location", key="btn_search_location"):
                data = fetch_suppliers_by_location(city if city else None, country if country else None)
                for line in data:
                    st.text(line)

    # Cluster Queries Section
    with st.expander("🔢 Cluster Data"):
        min_quantity = st.text_input("Minimum Avg Quantity", key="min_qty")
        min_price = st.text_input("Minimum Avg Price", key="min_price")
        min_sales = st.text_input("Minimum Avg Sales", key="min_sales")
        min_popularity = st.text_input("Minimum Popularity Score", key="min_pop")

        if st.button("Run Cluster Filter", key="btn_run_cluster_filter"):
            results = filter_clusters(
                float(min_quantity) if min_quantity else None,
                float(min_price) if min_price else None,
                float(min_sales) if min_sales else None,
                float(min_popularity)/100 if min_popularity else None
            )
            for line in results:
                st.text(line)

