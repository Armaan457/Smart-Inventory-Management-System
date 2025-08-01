import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

# Oracle DB setup
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("db_username")
password = os.getenv("db_password")

def create_supplier(supplier_id, name, location, contact_info):
    try:
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()

        insert_query = """
        INSERT INTO Suppliers (supplier_id, name, location, contact_info)
        VALUES (:1, :2, :3, :4)
        """
        cursor.execute(insert_query, (supplier_id, name, location, contact_info))
        connection.commit()

        return {"success": f"✅ Supplier '{name}' created successfully."}
    
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return {"error": f"❌ Oracle Error: {error.message}"}
    
    finally:
        if 'connection' in locals():
            connection.close()

def update_supplier(supplier_id, name=None, location=None, contact_info=None):
    try:
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()

        update_fields = []
        params = []

        if name:
            update_fields.append("name = :name")
            params.append(name)
        if location:
            update_fields.append("location = :location")
            params.append(location)
        if contact_info:
            update_fields.append("contact_info = :contact_info")
            params.append(contact_info)

        if not update_fields:
            return {"error": "⚠️ No fields to update."}

        query = f"""
        UPDATE Suppliers
        SET {', '.join(update_fields)}
        WHERE supplier_id = :supplier_id
        """

        # Build a dictionary for bind variables
        bind_vars = {
            'supplier_id': supplier_id
        }

        # Map dynamic bind names correctly
        for i, field in enumerate(update_fields):
            field_name = field.split(" = ")[0].strip()
            bind_vars[field_name] = params[i]

        cursor.execute(query, bind_vars)
        connection.commit()

        return {"success": f"✅ Supplier {supplier_id} updated successfully."}
    
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return {"error": f"❌ Oracle Error: {error.message}"}
    
    finally:
        if 'connection' in locals():
            connection.close()

def delete_supplier(supplier_id):
    try:
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()

        delete_query = "DELETE FROM Suppliers WHERE supplier_id = :1"
        cursor.execute(delete_query, (supplier_id,))
        connection.commit()

        return {"success": f"✅ Supplier {supplier_id} deleted successfully."}
    
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return {"error": f"❌ Oracle Error: {error.message}"}
    
    finally:
        if 'connection' in locals():
            connection.close()
