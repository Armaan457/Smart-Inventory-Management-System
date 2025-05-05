import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

def update_product(product_id, name=None, category=None, price=None, quantity=None, sales=None, rating=None, supplier_id=None):
    try:
        conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = conn.cursor()

        fields = []
        values = []

        if name:
            fields.append("name = :{}".format(len(values) + 1))
            values.append(name)
        if category:
            fields.append("category = :{}".format(len(values) + 1))
            values.append(category)
        if price is not None:
            fields.append("price = :{}".format(len(values) + 1))
            values.append(price)
        if quantity is not None:
            fields.append("quantity = :{}".format(len(values) + 1))
            values.append(quantity)
        if sales is not None:
            fields.append("sales = :{}".format(len(values) + 1))
            values.append(sales)
        if rating is not None:
            fields.append("rating = :{}".format(len(values) + 1))
            values.append(rating)
        if supplier_id is not None:
            fields.append("supplier_id = :{}".format(len(values) + 1))
            values.append(supplier_id)


        if not fields:
            return {"error": "No fields to update."}

        query = f"UPDATE products SET {', '.join(fields)} WHERE product_id = :{len(values) + 1}"
        values.append(product_id)

        cursor.execute(query, tuple(values))
        conn.commit()
        return {"success": f"Product ID {product_id} updated."}
    except Exception as e:
        return {"error": str(e)}


