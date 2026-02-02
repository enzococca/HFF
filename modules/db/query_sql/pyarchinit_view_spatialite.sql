CREATE VIEW pyarchinit_quote_view AS
 SELECT pyarchinit_quote.sito_q, pyarchinit_quote.area_q, pyarchinit_quote.us_q, pyarchinit_quote.unita_misu, pyarchinit_quote.quota_q, pyarchinit_quote.geometry, us_table.id_us, us_table.sito, us_table.area, us_table.us, us_table.struttura, us_table.definizione_stratigrafica, us_table.definizione_interpretativa, us_table.descrizione, us_table.interpretazione, us_table.rapporti, us_table.periodo_iniziale, us_table.fase_iniziale, us_table.periodo_finale, us_table.fase_finale, us_table.anno_scavo
   FROM pyarchinit_quote
   JOIN us_table ON pyarchinit_quote.sito_q = us_table.sito AND pyarchinit_quote.area_q = us_table.area AND pyarchinit_quote.us_q = us_table.us;


CREATE VIEW pyarchinit_us_view AS SELECT pyunitastratigrafiche.PK_UID, pyunitastratigrafiche.geometry, pyunitastratigrafiche.tipo_us_s, pyunitastratigrafiche.scavo_s, pyunitastratigrafiche.area_s, pyunitastratigrafiche.us_s, us_table.id_us, us_table.sito, us_table.area, us_table.us, us_table.struttura, us_table.definizione_stratigrafica, us_table.definizione_interpretativa, us_table.descrizione, us_table.interpretazione, us_table.rapporti, us_table.periodo_iniziale, us_table.fase_iniziale, us_table.periodo_finale, us_table.fase_finale, us_table.anno_scavo
   FROM pyunitastratigrafiche
   JOIN us_table ON pyunitastratigrafiche.scavo_s = us_table.sito AND pyunitastratigrafiche.area_s = us_table.area AND pyunitastratigrafiche.us_s = us_table.us

CREATE VIEW pyarchinit_uscaratterizzazioni_view AS
 SELECT pyuscaratterizzazioni.geometry, pyuscaratterizzazioni.tipo_us_c, pyuscaratterizzazioni.scavo_c, pyuscaratterizzazioni.area_c, pyuscaratterizzazioni.us_c, us_table.sito, us_table.id_us, us_table.area, us_table.us, us_table.struttura, us_table.definizione_stratigrafica, us_table.definizione_interpretativa, us_table.descrizione, us_table.interpretazione, us_table.rapporti, us_table.periodo_iniziale, us_table.fase_iniziale, us_table.periodo_finale, us_table.fase_finale, us_table.anno_scavo
   FROM pyuscaratterizzazioni
   JOIN us_table ON pyuscaratterizzazioni.scavo_c = us_table.sito AND pyuscaratterizzazioni.area_c = us_table.area AND pyuscaratterizzazioni.us_c = us_table.us;

CREATE VIEW IF NOT EXISTS shipwreck_view AS
SELECT
    a.id_shipwreck AS id_shipwreck,
    a.code_id AS code_id,
    a.name_vessel AS name_vessel,
    a.yard AS yard,
    a.area AS area,
    a.category AS category,
    a.confidence AS confidence,
    a.propulsion AS propulsion,
    a.material AS material,
    a.nationality AS nationality,
    a.type AS type,
    a.owner AS owner,
    a.purpose AS purpose,
    a.builder AS builder,
    a.cause AS cause,
    a.divers AS divers,
    a.wreck AS wreck,
    a.composition AS composition,
    a.inclination AS inclination,
    a.depth_max_min AS depth_max_min,
    a.depth_quality AS depth_quality,
    a.latitude AS latitude,
    a.longitude AS longitude,
    a.position_quality_1 AS position_quality_1,
    a.consulties AS consulties,
    a.l AS l,
    a.w AS w,
    a.d AS d,
    a.t AS t,
    a.cl AS cl,
    a.cw AS cw,
    a.cd AS cd,
    a.nickname AS nickname,
    a.date_built AS date_built,
    a.date_lost AS date_lost,
    a.description AS description,
    a.history AS history,
    a.list AS list,
    a.name AS name,
    a.status AS status,
    b.gid AS gid,
    b.the_geom AS the_geom,
    b.code AS code,
    b.nationality AS nationality_1,
    b.name_vessel AS name_vessel_1
FROM shipwreck_table AS a
LEFT JOIN shipwreck_location AS b ON a.code_id = b.code;

/*
CREATE VIEW pyarchinit_us_view AS SELECT pyunitastratigrafiche.PK_UID, pyunitastratigrafiche.geometry, pyunitastratigrafiche.tipo_us_s, pyunitastratigrafiche.scavo_s, pyunitastratigrafiche.area_s, pyunitastratigrafiche.us_s, us_table.id_us, us_table.sito, us_table.area, us_table.us, us_table.struttura, us_table.definizione_stratigrafica, us_table.definizione_interpretativa, us_table.descrizione, us_table.interpretazione, us_table.rapporti, us_table.periodo_iniziale, us_table.fase_iniziale, us_table.periodo_finale, us_table.fase_finale, us_table.anno_scavo
   FROM pyunitastratigrafiche
   JOIN us_table ON pyunitastratigrafiche.scavo_s = us_table.sito AND pyunitastratigrafiche.area_s = us_table.area AND pyunitastratigrafiche.us_s = us_table.us
*/






