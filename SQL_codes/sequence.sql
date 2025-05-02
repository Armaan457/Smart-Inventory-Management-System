DECLARE
    v_max_id NUMBER;
BEGIN
    SELECT NVL(MAX(user_id), 0) INTO v_max_id FROM User_Data;

    EXECUTE IMMEDIATE '
        CREATE SEQUENCE Users_seq
        START WITH ' || (v_max_id + 1) || '
        INCREMENT BY 1
        NOCACHE
        NOCYCLE
    ';
END;
/
