-- =====================================================================
-- Taksoandmed: tähtskeemi loomine PostgreSQL-is
-- Käivitamine DBeaveris: Alt+X (Execute SQL Script), kogu fail korraga.
-- Skripti võib käivitada mitu korda, sest iga käivitus alustab puhtalt.
-- Eeldus: tabel takso_andmed_clean on andmebaasis olemas.
-- Reegel: lause sees ei ole tühje ridu, tühi rida on ainult lausete vahel.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. PUHASTUS
-- Kustutan kõik skripti loodud tabelid. Algandmeid ei puututa.
-- CASCADE eemaldab ka tabelitevahelised FK-seosed.
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS fact_tickets CASCADE;

DROP TABLE IF EXISTS fact_rides CASCADE;

DROP TABLE IF EXISTS dim_order CASCADE;

DROP TABLE IF EXISTS dim_date CASCADE;

DROP TABLE IF EXISTS dim_device CASCADE;

DROP TABLE IF EXISTS dim_app_version CASCADE;

DROP TABLE IF EXISTS dim_pricing_context CASCADE;

DROP TABLE IF EXISTS dim_app_device CASCADE;

-- ---------------------------------------------------------------------
-- 1. ALGANDMETE KONTROLL (grain'i valik)
-- Oodatav tulemus:
-- source_rows = 4943, unique_orders = 4166, unique_tickets = 4943,
-- orders_with_multiple_tries = 0, orders_with_changing_ride_data = 0.
-- Järeldus: sõidu andmed on orderi piires samad, seega
-- fact_rides grain = üks order ja fact_tickets grain = üks ticket.
-- ---------------------------------------------------------------------

SELECT
    (SELECT COUNT(*) FROM takso_andmed_clean) AS source_rows,
    (SELECT COUNT(DISTINCT order_id_new) FROM takso_andmed_clean) AS unique_orders,
    (SELECT COUNT(DISTINCT ticket_id_new) FROM takso_andmed_clean) AS unique_tickets,
    (SELECT COUNT(*) FROM (
        SELECT order_id_new
        FROM takso_andmed_clean
        GROUP BY order_id_new
        HAVING COUNT(DISTINCT order_try_id_new) > 1
    ) x) AS orders_with_multiple_tries,
    (SELECT COUNT(*) FROM (
        SELECT order_id_new
        FROM takso_andmed_clean
        GROUP BY order_id_new
        HAVING COUNT(DISTINCT metered_price) > 1
            OR COUNT(DISTINCT upfront_price) > 1
            OR COUNT(DISTINCT distance) > 1
            OR COUNT(DISTINCT duration) > 1
            OR COUNT(DISTINCT predicted_distance) > 1
            OR COUNT(DISTINCT predicted_duration) > 1
            OR COUNT(DISTINCT fraud_score) > 1
    ) y) AS orders_with_changing_ride_data;

-- ---------------------------------------------------------------------
-- 2. DIMENSIOONID
-- ---------------------------------------------------------------------

-- dim_date: üks rida = üks kalendripäev.
CREATE TABLE dim_date (
    date_key SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    day_of_week VARCHAR(20),
    day_of_week_nr INTEGER,
    month INTEGER,
    year INTEGER
);

INSERT INTO dim_date (date, day_of_week, day_of_week_nr, month, year)
SELECT DISTINCT
    date::date,
    day_of_week,
    day_of_week_nr,
    month,
    year
FROM takso_andmed_clean
ORDER BY date::date;

-- dim_order: üks rida = üks unikaalne order.
-- had_overpaid_ride_ticket täidetakse punktis 5.
CREATE TABLE dim_order (
    order_key SERIAL PRIMARY KEY,
    order_id_new INTEGER NOT NULL,
    had_overpaid_ride_ticket INTEGER,
    CONSTRAINT dim_order_order_id_unique UNIQUE (order_id_new)
);

INSERT INTO dim_order (order_id_new)
SELECT DISTINCT order_id_new
FROM takso_andmed_clean
ORDER BY order_id_new;

-- dim_device: üks rida = üks unikaalne driver device + device name kombinatsioon.
CREATE TABLE dim_device (
    device_key SERIAL PRIMARY KEY,
    driver_device_uid_new INTEGER,
    device_name VARCHAR(100)
);

INSERT INTO dim_device (driver_device_uid_new, device_name)
SELECT DISTINCT
    driver_device_uid_new,
    device_name
FROM takso_andmed_clean;

-- dim_app_version: üks rida = üks unikaalne rider + driver app-versiooni kombinatsioon.
CREATE TABLE dim_app_version (
    app_version_key SERIAL PRIMARY KEY,
    rider_app_version VARCHAR(50),
    driver_app_version VARCHAR(50)
);

INSERT INTO dim_app_version (rider_app_version, driver_app_version)
SELECT DISTINCT
    rider_app_version,
    driver_app_version
FROM takso_andmed_clean;

-- dim_pricing_context: üks rida = üks unikaalne
-- prediction_price_type + change_reason_pricing + entered_by kombinatsioon.
CREATE TABLE dim_pricing_context (
    pricing_context_key SERIAL PRIMARY KEY,
    prediction_price_type VARCHAR(50),
    change_reason_pricing VARCHAR(50),
    entered_by VARCHAR(50)
);

INSERT INTO dim_pricing_context (prediction_price_type, change_reason_pricing, entered_by)
SELECT DISTINCT
    prediction_price_type,
    change_reason_pricing,
    entered_by
FROM takso_andmed_clean;

-- ---------------------------------------------------------------------
-- 3. FAKTITABEL fact_rides
-- Üks rida = üks unikaalne order (sõit).
-- ---------------------------------------------------------------------

CREATE TABLE fact_rides (
    ride_key SERIAL PRIMARY KEY,
    order_id_new INTEGER NOT NULL,
    order_try_id_new INTEGER,
    calc_created VARCHAR(50),
    time VARCHAR(50),
    metered_price REAL,
    upfront_price REAL,
    distance INTEGER,
    duration INTEGER,
    dest_change_number INTEGER,
    predicted_distance REAL,
    predicted_duration REAL,
    fraud_score REAL,
    gps_confidence INTEGER,
    b_state VARCHAR(50),
    order_state VARCHAR(50),
    order_try_state VARCHAR(50),
    eu_indicator INTEGER,
    is_invalid_ride BOOLEAN,
    fraud_score_status VARCHAR(50),
    date_key INTEGER REFERENCES dim_date(date_key),
    order_key INTEGER REFERENCES dim_order(order_key),
    device_key INTEGER REFERENCES dim_device(device_key),
    app_version_key INTEGER REFERENCES dim_app_version(app_version_key),
    pricing_context_key INTEGER REFERENCES dim_pricing_context(pricing_context_key),
    CONSTRAINT fact_rides_order_try_unique UNIQUE (order_id_new, order_try_id_new)
);

-- DISTINCT ON jätab iga order_id_new kohta ühe rea.
-- IS NOT DISTINCT FROM võrdleb korrektselt ka NULL väärtusi.
INSERT INTO fact_rides (
    order_id_new,
    order_try_id_new,
    calc_created,
    time,
    metered_price,
    upfront_price,
    distance,
    duration,
    dest_change_number,
    predicted_distance,
    predicted_duration,
    fraud_score,
    gps_confidence,
    b_state,
    order_state,
    order_try_state,
    eu_indicator,
    is_invalid_ride,
    fraud_score_status,
    date_key,
    order_key,
    device_key,
    app_version_key,
    pricing_context_key
)
SELECT DISTINCT ON (t.order_id_new)
    t.order_id_new,
    t.order_try_id_new,
    t.calc_created,
    t.time,
    t.metered_price,
    t.upfront_price,
    t.distance,
    t.duration,
    t.dest_change_number,
    t.predicted_distance,
    t.predicted_duration,
    t.fraud_score,
    t.gps_confidence,
    t.b_state,
    t.order_state,
    t.order_try_state,
    t.eu_indicator,
    t.is_invalid_ride::boolean,
    t.fraud_score_status,
    dd.date_key,
    o.order_key,
    dv.device_key,
    av.app_version_key,
    pc.pricing_context_key
FROM takso_andmed_clean t
LEFT JOIN dim_date dd
    ON dd.date = t.date::date
LEFT JOIN dim_order o
    ON o.order_id_new = t.order_id_new
LEFT JOIN dim_device dv
    ON dv.driver_device_uid_new IS NOT DISTINCT FROM t.driver_device_uid_new
    AND dv.device_name IS NOT DISTINCT FROM t.device_name
LEFT JOIN dim_app_version av
    ON av.rider_app_version IS NOT DISTINCT FROM t.rider_app_version
    AND av.driver_app_version IS NOT DISTINCT FROM t.driver_app_version
LEFT JOIN dim_pricing_context pc
    ON pc.prediction_price_type IS NOT DISTINCT FROM t.prediction_price_type
    AND pc.change_reason_pricing IS NOT DISTINCT FROM t.change_reason_pricing
    AND pc.entered_by IS NOT DISTINCT FROM t.entered_by
ORDER BY t.order_id_new, t.ticket_id_new;

-- ---------------------------------------------------------------------
-- 4. FAKTITABEL fact_tickets
-- Üks rida = üks unikaalne ticket.
-- Ühel orderil võib olla mitu ticketit, seos käib dim_order kaudu.
-- ---------------------------------------------------------------------

CREATE TABLE fact_tickets (
    ticket_id_new INTEGER PRIMARY KEY,
    order_id_new INTEGER NOT NULL,
    overpaid_ride_ticket INTEGER,
    order_key INTEGER REFERENCES dim_order(order_key)
);

INSERT INTO fact_tickets (ticket_id_new, order_id_new, overpaid_ride_ticket, order_key)
SELECT
    t.ticket_id_new,
    t.order_id_new,
    t.overpaid_ride_ticket,
    o.order_key
FROM takso_andmed_clean t
LEFT JOIN dim_order o
    ON o.order_id_new = t.order_id_new;

-- ---------------------------------------------------------------------
-- 5. RIKASTAMINE
-- had_overpaid_ride_ticket = 1, kui orderil oli vähemalt üks
-- overpaid_ride_ticket = 1. Muidu 0.
-- ---------------------------------------------------------------------

UPDATE dim_order d
SET had_overpaid_ride_ticket = x.had_overpaid
FROM (
    SELECT
        order_key,
        MAX(overpaid_ride_ticket) AS had_overpaid
    FROM fact_tickets
    GROUP BY order_key
) x
WHERE d.order_key = x.order_key;

-- ---------------------------------------------------------------------
-- 6. LÕPPKONTROLL
-- Oodatav tulemus:
-- fact_rides_rows = 4166, fact_tickets_rows = 4943, dim_order_rows = 4166,
-- kõik missing_* ja mismatch veerud = 0.
-- ---------------------------------------------------------------------

SELECT
    (SELECT COUNT(*) FROM fact_rides) AS fact_rides_rows,
    (SELECT COUNT(*) FROM fact_tickets) AS fact_tickets_rows,
    (SELECT COUNT(*) FROM dim_order) AS dim_order_rows,
    (SELECT COUNT(*) FROM dim_date) AS dim_date_rows,
    (SELECT COUNT(*) FROM dim_device) AS dim_device_rows,
    (SELECT COUNT(*) FROM dim_app_version) AS dim_app_version_rows,
    (SELECT COUNT(*) FROM dim_pricing_context) AS dim_pricing_context_rows,
    (SELECT COUNT(*) FROM fact_rides WHERE date_key IS NULL) AS missing_date,
    (SELECT COUNT(*) FROM fact_rides WHERE order_key IS NULL) AS missing_order,
    (SELECT COUNT(*) FROM fact_rides WHERE device_key IS NULL) AS missing_device,
    (SELECT COUNT(*) FROM fact_rides WHERE app_version_key IS NULL) AS missing_app_version,
    (SELECT COUNT(*) FROM fact_rides WHERE pricing_context_key IS NULL) AS missing_pricing_context,
    (SELECT COUNT(*) FROM fact_tickets WHERE order_key IS NULL) AS missing_ticket_order,
    (SELECT COUNT(*) FROM dim_order WHERE had_overpaid_ride_ticket IS NULL) AS missing_overpaid_flag;

-- had_overpaid_ride_ticket jaotus. Oodatud väärtused: ainult 0 ja 1.
SELECT
    had_overpaid_ride_ticket,
    COUNT(*) AS orders
FROM dim_order
GROUP BY had_overpaid_ride_ticket
ORDER BY had_overpaid_ride_ticket;

-- Kõik FK-seosed. Oodatud: 5 fact_rides tabelil, 1 fact_tickets tabelil.
SELECT
    conrelid::regclass AS table_name,
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid IN ('fact_rides'::regclass, 'fact_tickets'::regclass)
  AND contype = 'f'
ORDER BY table_name, constraint_name;
