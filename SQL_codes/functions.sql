CREATE OR REPLACE FUNCTION GetCategoryFromName (
    p_name IN VARCHAR2
) RETURN VARCHAR2
IS
    v_category VARCHAR2(50);
BEGIN
    SELECT category INTO v_category
    FROM Products
    WHERE LOWER(name) = LOWER(p_name)
    FETCH FIRST 1 ROWS ONLY; 
    
    RETURN v_category;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
END;
/

CREATE OR REPLACE FUNCTION GetInventoryAlerts
RETURN SYS_REFCURSOR
IS
    alert_cursor SYS_REFCURSOR;
BEGIN
    OPEN alert_cursor FOR
        SELECT 
            IA.product_id,
            P.name AS product_name,
            IA.alert_date,
            IA.alert_type,
            IA.message,
            IA.is_processed
        FROM 
            Inventory_Alerts IA
            JOIN Products P ON IA.product_id = P.product_id
        ORDER BY 
            IA.alert_date DESC;

    RETURN alert_cursor;
END;
/

