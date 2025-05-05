CREATE OR REPLACE TRIGGER trg_users_id
BEFORE INSERT ON User_Data
FOR EACH ROW
BEGIN
    IF :NEW.user_id IS NULL THEN
        SELECT Users_seq.NEXTVAL INTO :NEW.user_id FROM dual;
    END IF;
END;
/


CREATE OR REPLACE TRIGGER trg_inventory_alert
AFTER UPDATE OF quantity ON Products
FOR EACH ROW
WHEN (NEW.quantity <= 50 AND NEW.quantity <> OLD.quantity)
DECLARE
    v_alert_type VARCHAR2(50);
    v_message VARCHAR2(255);
BEGIN
    -- Determine the type of alert
    IF :NEW.quantity = 0 THEN
        v_alert_type := 'Stock Finished';
        v_message := 'Product "' || :NEW.name || '" is out of stock!';
    ELSE
        v_alert_type := 'Low Stock';
        v_message := 'Product "' || :NEW.name || '" has low stock (Qty: ' || :NEW.quantity || ')';
    END IF;

    BEGIN
        INSERT INTO Inventory_Alerts (
            product_id, alert_date, alert_type, message, is_processed
        ) VALUES (
            :NEW.product_id, TRUNC(SYSDATE), v_alert_type, v_message, 0
        );
    EXCEPTION
        WHEN DUP_VAL_ON_INDEX THEN
            NULL; 
    END;
END;
/