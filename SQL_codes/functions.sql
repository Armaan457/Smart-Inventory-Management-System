CREATE OR REPLACE FUNCTION GetCategoryFromName (
    p_name IN VARCHAR2
) RETURN VARCHAR2
IS
    v_category VARCHAR2(50);
BEGIN
    SELECT category INTO v_category
    FROM Products
    WHERE LOWER(name) = LOWER(p_name)
    FETCH FIRST 1 ROWS ONLY; -- In case multiple matches

    RETURN v_category;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
END;
/