CREATE OR REPLACE PROCEDURE GetSuppliersByLocation (
    p_city IN VARCHAR2 DEFAULT NULL,
    p_country IN VARCHAR2 DEFAULT NULL
)
IS
    CURSOR supplier_cursor IS
        SELECT *
        FROM Suppliers
        WHERE (p_city IS NULL OR UPPER(location) LIKE UPPER(p_city) || '%')
          AND (p_country IS NULL OR UPPER(location) LIKE '%' || UPPER(p_country));
    supplier_rec supplier_cursor%ROWTYPE;
BEGIN
    OPEN supplier_cursor;
    LOOP
        FETCH supplier_cursor INTO supplier_rec;
        EXIT WHEN supplier_cursor%NOTFOUND;

        DBMS_OUTPUT.PUT_LINE('Supplier ID: ' || supplier_rec.supplier_id);
        DBMS_OUTPUT.PUT_LINE('Name: ' || supplier_rec.name);
        DBMS_OUTPUT.PUT_LINE('Location: ' || supplier_rec.location);
        DBMS_OUTPUT.PUT_LINE('Contact Info: ' || supplier_rec.contact_info);
        DBMS_OUTPUT.PUT_LINE('-----------------------------');
    END LOOP;
    CLOSE supplier_cursor;
END;
/

CREATE OR REPLACE PROCEDURE RecommendItemsByCategory (
    p_category IN VARCHAR2
)
IS
    CURSOR cluster_cursor IS
        SELECT cluster_id, category_distribution
        FROM Clusters
        WHERE REGEXP_LIKE(category_distribution, LOWER(p_category), 'i')
          AND cluster_id != -1
        FETCH FIRST 3 ROWS ONLY;

    CURSOR product_cursor (cluster_id NUMBER) IS
        SELECT name, price, rating
        FROM Products
        WHERE cluster_id = cluster_id
          AND LOWER(category) = LOWER(p_category);

    cluster_rec cluster_cursor%ROWTYPE;
    prod_rec product_cursor%ROWTYPE;
    v_found_count NUMBER := 0;
BEGIN
    OPEN cluster_cursor;
    LOOP
        FETCH cluster_cursor INTO cluster_rec;
        EXIT WHEN cluster_cursor%NOTFOUND;

        v_found_count := v_found_count + 1;
        DBMS_OUTPUT.PUT_LINE('Cluster ID: ' || cluster_rec.cluster_id);

        OPEN product_cursor(cluster_rec.cluster_id);
        LOOP
            FETCH product_cursor INTO prod_rec;
            EXIT WHEN product_cursor%NOTFOUND;

            DBMS_OUTPUT.PUT_LINE(' - ' || prod_rec.name || ' | ₹' || prod_rec.price || prod_rec.rating);
        END LOOP;
        CLOSE product_cursor;

        DBMS_OUTPUT.PUT_LINE('-----------------------------');
    END LOOP;
    CLOSE cluster_cursor;

    IF v_found_count = 0 THEN
        DBMS_OUTPUT.PUT_LINE('No clusters found for category "' || p_category || '". Using fallback cluster -1.');
        DBMS_OUTPUT.PUT_LINE('Identical items in fallback cluster:');

        FOR fallback_prod IN (
            SELECT name, price, rating
            FROM Products
            WHERE cluster_id = -1
              AND LOWER(category) = LOWER(p_category)
        ) LOOP
            DBMS_OUTPUT.PUT_LINE(' - ' || fallback_prod.name || ' | ₹' || fallback_prod.price || fallback_prod.rating * 100);
        END LOOP;
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
END;
/

CREATE OR REPLACE PROCEDURE FilterClustersByStats (
    p_min_quantity        IN NUMBER DEFAULT NULL,
    p_min_price           IN NUMBER DEFAULT NULL,
    p_min_sales           IN NUMBER DEFAULT NULL,
    p_min_popularity      IN NUMBER DEFAULT NULL
)
IS
BEGIN
    DBMS_OUTPUT.PUT_LINE('📊 Matching Clusters:');

    FOR rec IN (
        SELECT cluster_id, avg_quantity, avg_price, avg_sales, avg_popularity_score
        FROM Clusters
        WHERE (p_min_quantity IS NULL OR avg_quantity >= p_min_quantity)
          AND (p_min_price IS NULL OR avg_price >= p_min_price)
          AND (p_min_sales IS NULL OR avg_sales >= p_min_sales)
          AND (p_min_popularity IS NULL OR avg_popularity_score >= p_min_popularity)
        ORDER BY cluster_id
    ) LOOP
        DBMS_OUTPUT.PUT_LINE('Cluster ID: ' || rec.cluster_id);
        DBMS_OUTPUT.PUT_LINE(' - Avg Quantity: ' || rec.avg_quantity);
        DBMS_OUTPUT.PUT_LINE(' - Avg Price: ₹' || rec.avg_price);
        DBMS_OUTPUT.PUT_LINE(' - Avg Sales: ' || rec.avg_sales);
        DBMS_OUTPUT.PUT_LINE(' - Popularity Score: ' || rec.avg_popularity_score);
        DBMS_OUTPUT.PUT_LINE('----------------------------');
    END LOOP;

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('❌ Error: ' || SQLERRM);
END;
/

CREATE OR REPLACE PROCEDURE PrintSupplierInfo (
    p_supplier_name IN VARCHAR2
)
IS
    v_supplier_id   Suppliers.supplier_id%TYPE;
    v_location      Suppliers.location%TYPE;
    v_contact_info  Suppliers.contact_info%TYPE;
BEGIN
    SELECT supplier_id, location, contact_info
    INTO v_supplier_id, v_location, v_contact_info
    FROM Suppliers
    WHERE UPPER(name) = UPPER(p_supplier_name);

    DBMS_OUTPUT.PUT_LINE('Supplier ID: ' || v_supplier_id);
    DBMS_OUTPUT.PUT_LINE('Name: ' || p_supplier_name);

    IF v_location IS NULL THEN
        DBMS_OUTPUT.PUT_LINE('Location: No location specified');
    ELSE
        DBMS_OUTPUT.PUT_LINE('Location: ' || v_location);
    END IF;

    IF v_contact_info IS NULL THEN
        DBMS_OUTPUT.PUT_LINE('Contact Info: No phone number available');
    ELSE
        DBMS_OUTPUT.PUT_LINE('Contact Info: ' || v_contact_info);
    END IF;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('❌ Supplier "' || p_supplier_name || '" not found.');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('❌ Error: ' || SQLERRM);
END;
/