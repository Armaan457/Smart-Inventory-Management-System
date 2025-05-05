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

        IF supplier_rec.location IS NULL THEN
            DBMS_OUTPUT.PUT_LINE('Location: No location specified');
        ELSE
            DBMS_OUTPUT.PUT_LINE('Location: ' || supplier_rec.location);
        END IF;

        IF supplier_rec.contact_info IS NULL THEN
            DBMS_OUTPUT.PUT_LINE('Contact Info: No phone number available');
        ELSE
            DBMS_OUTPUT.PUT_LINE('Contact Info: ' || supplier_rec.contact_info);
        END IF;

        DBMS_OUTPUT.PUT_LINE('----------------------------------------------------------------------------');
    END LOOP;
    CLOSE supplier_cursor;
END;
/


CREATE OR REPLACE PROCEDURE RecommendItemsByCategory (
    p_category_or_name IN VARCHAR2
)
IS
    v_category VARCHAR2(100);
    v_item_cluster_id NUMBER;
    v_previous_cluster_id NUMBER := NULL; 
    CURSOR cluster_cursor IS
        SELECT cluster_id, category_distribution
        FROM Clusters
        WHERE REGEXP_LIKE(category_distribution, LOWER(v_category), 'i')
          AND cluster_id != -1
        FETCH FIRST 3 ROWS ONLY;

    CURSOR product_cursor (p_cluster_id NUMBER) IS
        SELECT name, price, rating
        FROM Products
        WHERE cluster_id = p_cluster_id
          AND LOWER(category) = LOWER(v_category);

    cluster_rec cluster_cursor%ROWTYPE;
    prod_rec product_cursor%ROWTYPE;
    v_found_count NUMBER := 0;
BEGIN
    v_category := GetCategoryFromName(p_category_or_name);
    IF v_category IS NULL THEN
        v_category := p_category_or_name; 
    ELSE
        BEGIN
            SELECT cluster_id
            INTO v_item_cluster_id
            FROM Products
            WHERE UPPER(name) = UPPER(p_category_or_name)
            FETCH FIRST 1 ROWS ONLY;

            DBMS_OUTPUT.PUT_LINE('Cluster containing the item: ' || v_item_cluster_id);

            -- Display products in the item's cluster
            OPEN product_cursor(v_item_cluster_id);
            LOOP
                FETCH product_cursor INTO prod_rec;
                EXIT WHEN product_cursor%NOTFOUND;

                DBMS_OUTPUT.PUT_LINE(' - ' || prod_rec.name || ' | ₹' || prod_rec.price || ' | Rating ' || prod_rec.rating * 100 || '%');
            END LOOP;
            CLOSE product_cursor;

            v_previous_cluster_id := v_item_cluster_id;

            DBMS_OUTPUT.PUT_LINE('----------------------------------------------------------------------------');
            DBMS_OUTPUT.PUT_LINE('Similar items in the other clusters:');
            DBMS_OUTPUT.PUT_LINE('----------------------------------------------------------------------------');

        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                DBMS_OUTPUT.PUT_LINE('Item "' || p_category_or_name || '" not found in any cluster.');
        END;
    END IF;

    OPEN cluster_cursor;
    LOOP
        FETCH cluster_cursor INTO cluster_rec;
        EXIT WHEN cluster_cursor%NOTFOUND;

        IF cluster_rec.cluster_id = v_previous_cluster_id THEN
            CONTINUE;
        END IF;

        v_found_count := v_found_count + 1;
        DBMS_OUTPUT.PUT_LINE('Cluster: ' || cluster_rec.cluster_id);

        OPEN product_cursor(cluster_rec.cluster_id);
        LOOP
            FETCH product_cursor INTO prod_rec;
            EXIT WHEN product_cursor%NOTFOUND;

            DBMS_OUTPUT.PUT_LINE(' - ' || prod_rec.name || ' | ₹' || prod_rec.price || ' | Rating ' || prod_rec.rating * 100 || '%');
        END LOOP;
        CLOSE product_cursor;

        DBMS_OUTPUT.PUT_LINE('----------------------------------------------------------------------------');
    END LOOP;
    CLOSE cluster_cursor;

    IF v_found_count = 0 THEN
        DBMS_OUTPUT.PUT_LINE('No clusters found for category "' || v_category || '". Using fallback cluster -1.');

        FOR fallback_prod IN (
            SELECT name, price, rating
            FROM Products
            WHERE cluster_id = -1
              AND LOWER(category) = LOWER(v_category)
        ) LOOP
            DBMS_OUTPUT.PUT_LINE(' - ' || fallback_prod.name || ' | ₹' || fallback_prod.price || ' | Rating ' || fallback_prod.rating * 100 || '%');
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
    p_min_popularity      IN NUMBER DEFAULT NULL,
    p_num_clusters        IN NUMBER DEFAULT NULL -- New parameter for limiting clusters
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
        FETCH FIRST p_num_clusters ROWS ONLY -- Limit the number of clusters
    ) LOOP
        DBMS_OUTPUT.PUT_LINE('Cluster ID: ' || rec.cluster_id);
        DBMS_OUTPUT.PUT_LINE(' - Avg Quantity: ' || rec.avg_quantity);
        DBMS_OUTPUT.PUT_LINE(' - Avg Price: ₹' || rec.avg_price);
        DBMS_OUTPUT.PUT_LINE(' - Avg Sales: ' || rec.avg_sales);
        DBMS_OUTPUT.PUT_LINE(' - Popularity Score: ' || rec.avg_popularity_score*100 || '%');
        DBMS_OUTPUT.PUT_LINE('----------------------------------------------------------------------------');
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


CREATE OR REPLACE PROCEDURE ConductTransaction (
    p_product_name      IN VARCHAR2,
    p_quantity_change   IN NUMBER,
    p_user_id           IN NUMBER
)
IS
    v_product_id        NUMBER;
    v_current_quantity  NUMBER;
BEGIN
    -- Get product ID and current quantity
    SELECT product_id, quantity
    INTO v_product_id, v_current_quantity
    FROM Products
    WHERE LOWER(name) = LOWER(p_product_name);

    IF v_current_quantity + p_quantity_change < 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Not enough stock for transaction.');
    END IF;

    -- Update Products table
    UPDATE Products
    SET quantity = quantity + p_quantity_change
    WHERE product_id = v_product_id;

    -- Insert into Transactions table
    INSERT INTO Transactions (
        transaction_id,
        transaction_type,
        quantity_change,
        transaction_date,
        product_id,
        user_id
    ) VALUES (
        TRANSACTIONS_SEQ.NEXTVAL,
        CASE WHEN p_quantity_change > 0 THEN 'Stock In' ELSE 'Stock Out' END,
        p_quantity_change,
        SYSDATE,
        v_product_id,
        p_user_id
    );

    COMMIT;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20002, 'Product not found.');
END;
/