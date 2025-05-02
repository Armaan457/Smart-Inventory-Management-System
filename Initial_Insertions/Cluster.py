import cx_Oracle
import pandas as pd
import json
from dotenv import load_dotenv
import os
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

csv_file_path = r"Clustering\dataset_dbms.csv" 
df = pd.read_csv(csv_file_path)

required_columns = ['cluster', 'quantity', 'price', 'sales', 'popularity_score', 'category']
df = df[required_columns].dropna()

cluster_group = df.groupby('cluster').agg({
    'quantity': 'mean',
    'price': 'mean',
    'sales': 'mean',
    'popularity_score': 'mean'
}).reset_index()

category_counts = df.groupby('cluster')['category'] \
                    .value_counts() \
                    .unstack(fill_value=0)

json_list = []
for cl in cluster_group['cluster']:
    raw = category_counts.loc[cl].to_dict()               
    non_zero = {cat: cnt for cat, cnt in raw.items() if cnt > 0}
    js = json.dumps(non_zero)                              
    json_list.append(js)

cluster_group['category_distribution'] = json_list

print("\n🔍 Cluster 105 debug:")
rc = category_counts.loc[105].to_dict()
print("  raw counts:", rc)
print("  json string:", cluster_group.loc[cluster_group['cluster']==105, 'category_distribution'].iloc[0])

try:
    # Connect to DB
    connection = cx_Oracle.connect(
        user=username,
        password=password,
        dsn=dsn,
    )
    print("✅ Connected to Oracle Database.")
    cursor = connection.cursor()

    for _, row in cluster_group.iterrows():
        cluster_id = int(row['cluster'])
        avg_quantity = round(row['quantity'], 2)
        avg_price = round(row['price'], 2)
        avg_sales = round(row['sales'], 2)
        avg_popularity_score = round(row['popularity_score'], 2)
        category_distribution_clob = cursor.var(cx_Oracle.CLOB)
        category_distribution_clob.setvalue(0, str(row['category_distribution']))


        cursor.execute("""
            INSERT INTO Clusters (
                cluster_id, avg_quantity, avg_price, avg_sales,
                avg_popularity_score, category_distribution
            )
            VALUES (:1, :2, :3, :4, :5, :6)
        """, (
            cluster_id,
            avg_quantity,
            avg_price,
            avg_sales,
            avg_popularity_score,
            category_distribution_clob
        ))

        print(f"Inserted cluster: {cluster_id}")


    # Commit the changes
    connection.commit()
    print("\n✅ Changes committed to the database.")

    # Verify inserted data
    cursor.execute("SELECT * FROM Clusters")
    rows = cursor.fetchall()
    for row in rows:
        cluster_id, avg_qty, avg_price, avg_sales, avg_pop_score, cat_dist_lob = row
        cat_dist_str = cat_dist_lob.read() if cat_dist_lob else None
        print(f"Cluster ID: {cluster_id}, Avg Qty: {avg_qty}, Avg Price: {avg_price}, "
            f"Avg Sales: {avg_sales}, Popularity: {avg_pop_score}, "
            f"Category Distribution: {cat_dist_str}")

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"❌ Database error: {error.message}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 Connection closed.")
