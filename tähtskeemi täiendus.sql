SELECT
    order_key,
    COUNT(DISTINCT order_state) AS order_state_count,
    COUNT(DISTINCT order_try_state) AS order_try_state_count
FROM fact_rides
GROUP BY order_key
HAVING
    COUNT(DISTINCT order_state) > 1
    OR COUNT(DISTINCT order_try_state) > 1;

ALTER TABLE dim_order
ADD COLUMN order_state varchar(50),
ADD COLUMN order_try_state varchar(50);

UPDATE dim_order d
SET
    order_state = f.order_state,
    order_try_state = f.order_try_state
FROM fact_rides f
WHERE d.order_key = f.order_key;

-- Kontrollin, kas order_state ja order_try_state
-- kopeerusid fact_rides tabelist dim_order tabelisse õigesti.
-- Tulemus peaks olema 0 ehk ühtegi erinevust ei ole.

SELECT COUNT(*) AS mismatches
FROM dim_order d
JOIN fact_rides f
    ON d.order_key = f.order_key
WHERE d.order_state IS DISTINCT FROM f.order_state
   OR d.order_try_state IS DISTINCT FROM f.order_try_state;

-- Kontrollin, mitu NULL-väärtust on dim_order tabelis
-- pärast order_state ja order_try_state lisamist.

SELECT
    COUNT(*) FILTER (WHERE order_state IS NULL) AS order_state_nulls,
    COUNT(*) FILTER (WHERE order_try_state IS NULL) AS order_try_state_nulls
FROM dim_order;

-- Eemaldan fact_rides tabelist orderiga seotud kirjeldavad väljad,
-- sest need asuvad nüüd dim_order tabelis.
-- Väärtuste korrektne ülekandmine on eelnevalt kontrollitud.

ALTER TABLE fact_rides
DROP COLUMN order_state,
DROP COLUMN order_try_state;

-- Vaatan üle fact_rides tabeli praegused veerud ja nende andmetüübid,
-- et otsustada, millised väljad kuuluvad fact-tabelisse
-- ja millised võiksid kuuluda olemasolevatesse dimensioonidesse.

SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'fact_rides'
ORDER BY ordinal_position;

-- Lisan order_state ja order_try_state veerud
-- fact_rides tabelisse tagasi.

ALTER TABLE fact_rides
ADD COLUMN order_state varchar(50),
ADD COLUMN order_try_state varchar(50);

-- Taastan order_state ja order_try_state väärtused
-- dim_order tabelist fact_rides tabelisse order_key järgi.

UPDATE fact_rides f
SET
    order_state = d.order_state,
    order_try_state = d.order_try_state
FROM dim_order d
WHERE f.order_key = d.order_key;

-- Kontrollin, kas taastatud väärtused fact_rides tabelis
-- vastavad dim_order tabelis olevatele väärtustele.
-- Oodatav tulemus: 0.

SELECT COUNT(*) AS mismatches
FROM fact_rides f
JOIN dim_order d
    ON f.order_key = d.order_key
WHERE f.order_state IS DISTINCT FROM d.order_state
   OR f.order_try_state IS DISTINCT FROM d.order_try_state;

-- Kontrollin, kas ühe order_key kohta on alati ainult üks
-- order_try_id_new väärtus.
-- Kui tulemus on 0 rida, sobib order_try_id_new dim_order tabelisse.

SELECT
    order_key,
    COUNT(DISTINCT order_try_id_new) AS order_try_id_count
FROM fact_rides
GROUP BY order_key
HAVING COUNT(DISTINCT order_try_id_new) > 1;

-- Lisan order_try_id_new veeru dim_order tabelisse,
-- sest iga order_key kohta on ainult üks order_try_id_new väärtus.

ALTER TABLE dim_order
ADD COLUMN order_try_id_new integer;

-- Toon order_try_id_new väärtuse fact_rides tabelist
-- dim_order tabelisse order_key alusel.

UPDATE dim_order d
SET order_try_id_new = f.order_try_id_new
FROM fact_rides f
WHERE d.order_key = f.order_key;

-- Kontrollin, kas order_try_id_new kopeerus dim_order tabelisse õigesti.
-- Oodatav tulemus: 0.

SELECT COUNT(*) AS mismatches
FROM dim_order d
JOIN fact_rides f
    ON d.order_key = f.order_key
WHERE d.order_try_id_new IS DISTINCT FROM f.order_try_id_new;

-- Kontrollin, kas ühe order_key kohta on alati ainult üks
-- orderi loomise aeg (calc_created).
-- Oodatav tulemus: 0 rida.

SELECT
    order_key,
    COUNT(DISTINCT calc_created) AS created_at_count
FROM fact_rides
GROUP BY order_key
HAVING COUNT(DISTINCT calc_created) > 1;

-- Lisan orderi loomise aja dim_order tabelisse,
-- sest iga order_key kohta on ainult üks calc_created väärtus.

ALTER TABLE dim_order
ADD COLUMN calc_created varchar;

-- Toon orderi loomise aja fact_rides tabelist
-- dim_order tabelisse order_key alusel.

UPDATE dim_order d
SET calc_created = f.calc_created
FROM fact_rides f
WHERE d.order_key = f.order_key;

-- Kontrollin, kas calc_created kopeerus dim_order tabelisse õigesti.
-- Oodatav tulemus: 0.

SELECT COUNT(*) AS mismatches
FROM dim_order d
JOIN fact_rides f
    ON d.order_key = f.order_key
WHERE d.calc_created IS DISTINCT FROM f.calc_created;
