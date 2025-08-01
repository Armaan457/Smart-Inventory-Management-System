import cx_Oracle
import os
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

# Load credentials
load_dotenv()
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("db_username")
password = os.getenv("db_password")

def create_connection():
    return cx_Oracle.connect(user=username, password=password, dsn=dsn)

def fetch_non_admin_users():
    """Fetch all non-admin users from the database."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, role FROM User_Data WHERE LOWER(role) != 'admin' ORDER BY name")
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=["User ID", "Name", "Role"])
    except cx_Oracle.DatabaseError as e:
        st.error(f"❌ Error fetching users: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

def delete_user(user_id):
    """Delete a non-admin user by their user ID."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM User_Data WHERE user_id = :user_id", {'user_id': user_id})
        conn.commit()
        return f"✅ User ID {user_id} deleted successfully."
    except cx_Oracle.DatabaseError as e:
        return f"❌ Failed to delete user: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()