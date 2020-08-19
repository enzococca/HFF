 /* alter table dive_log add column bar_start_2 character varying(255);
 alter table dive_log add column bar_end_2 character varying(255);
 alter table dive_log add column dp_2 character varying(255); */
 /* alter table site_table add column ets character varying(255);
 alter table site_table add column material_c text;
 alter table site_table add column morphology_c text;
 alter table site_table add column collection_c text; */
/*  alter table grab_spot RENAME COLUMN id to gid; */
drop view pyarchinit_grabspot_view;
drop view pyarchinit_feature_p_view;
drop view pyarchinit_feature_point_view;
drop view pyarchinit_feature_l_view;
drop view pyarchinit_transect_view ;
CREATE SEQUENCE IF NOT EXISTS public.shipwreck_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.shipwreck_id_seq OWNER TO postgres;
--

CREATE TABLE IF NOT EXISTS public.shipwreck_table (
    id_shipwreck integer DEFAULT nextval('public.shipwreck_id_seq'::regclass) NOT NULL,
    code_id character varying(255),
    name_vessel character varying(255),
    yard character varying(255),
    area character varying(255),
    category character varying(255),
    confidence character varying(255),
    propulsion character varying(255),
    material character varying(255),
    nationality character varying(255),
    type character varying(255),
    owner character varying(255),
    purpose character varying(255),
    builder character varying(255),
    cause character varying(255),
    divers character varying(255),
    wreck character varying(255),
	composition character varying(255),
	inclination character varying(255),
    depth_max_min character varying(255),
	depth_quality character varying(255),
	coordinates character varying(255),
	position_quality_1 character varying(255),
	acquired_coordinates character varying(255),
	position_quality_2 character varying(255),
    l numeric(5,2),
    w numeric(5,2),
    d numeric(5,2),
    t numeric(5,2),
    cl numeric(5,2),
    cw numeric(5,2),
    cd numeric(5,2),
    nickname character varying(255),
    date_built character varying(255),
	date_lost character varying(255),
	description text,
	history text,
	list text,
	name text character varying(10),
	status character varying(255)
);
ALTER TABLE public.shipwreck_table OWNER TO postgres;

CREATE SEQUENCE IF NOT EXISTS public.shipwreck_id_p_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE  public.shipwreck_id_p_seq
    OWNER TO postgres;
CREATE TABLE  IF NOT EXISTS public.shipwreck_location
(
    gid integer NOT NULL DEFAULT nextval('shipwreck_id_p_seq'::regclass),
    the_geom geometry(Point,32636),
    code character varying COLLATE pg_catalog."default",
    nationality character varying COLLATE pg_catalog."default",
    name_vessel character varying COLLATE pg_catalog."default",
    
    CONSTRAINT shipwreck_pkey PRIMARY KEY (gid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.shipwreck_location
    OWNER to postgres;

-- Index: sidx_site_poligon_the_geom

-- DROP INDEX public.sidx_site_poligon_the_geom;

CREATE INDEX sidx_shipwreck_the_geom
    ON public.shipwreck_location USING gist
    (the_geom)
    TABLESPACE pg_default;	
--
-- TOC entry 5011 (class 0 OID 0)
-- Dependencies: 20
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--
SET standard_conforming_strings = OFF;
---CREATE SCHEMA "public";
CREATE or replace VIEW public.shipwreck_view AS
SELECT id_shipwreck AS id_shipwreck,
    a.code_id AS code_id, a.name_vessel AS name_vessel,
    a.yard AS yard, a.area AS area, a.category AS category,
    a.confidence AS confidence, a.propulsion AS propulsion,
    a.material AS material, a.nationality AS nationality,
    a.type AS type, a.owner AS owner, a.purpose AS purpose,
    a.builder AS builder, a.cause AS cause,
    a.divers AS divers,
    a.wreck AS wreck, a.composition AS composition,
    a.inclination AS inclination, a.depth_max_min AS depth_max_min, 
	a.depth_quality as depth_quality, a.coordinates as coordinates, a.acquired_coordinates as acquired_coordinates,
	a.position_quality_1 as position_quality_1, a.position_quality_2 as position_quality_2
    a.l AS l, a.w AS w, a.d AS d, a.t AS t,
    a.cl AS cl, a.cw AS cw, a.cd AS cd,
    a.nickname AS nickname, a.date_built AS date_built,
    a.date_lost AS date_lost, a.description AS description,
    a.history AS history, a.list AS list, a.name as name, a.status as status,
    b.gid AS gid, b.the_geom AS the_geom,
    b.code AS code, b.nationality AS nationality_1,
    b.name_vessel AS name_vessel_1
FROM (public.shipwreck_table AS a
JOIN shipwreck_location AS b ON (((a.code_id)::text = (b.code)::text)));
ALTER TABLE public.shipwreck_view OWNER TO postgres
CREATE or replace VIEW public.pyarchinit_grabspot_view AS
	SELECT site_table.id_sito,
    site_table.location_,
    site_table.mouhafasat,
    site_table.casa,
    site_table.village,
    site_table.antique_name,
    site_table.definition,
    site_table.find_check,
    site_table.sito_path,
    site_table.proj_name,
    site_table.proj_code,
    site_table.geometry_collection,
    site_table.name_site,
    site_table.area,
    site_table.date_start,
    site_table.type_class,
    site_table.grab,
    site_table.survey_type,
    site_table.certainties,
    site_table.supervisor,
    site_table.date_fill,
    site_table.soil_type,
    site_table.topographic_setting,
    site_table.visibility,
    site_table.condition_state,
    site_table.features,
    site_table.disturbance,
    site_table.orientation,
    site_table.length_,
    site_table.width_,
    site_table.depth_,
    site_table.height_,
    site_table.material,
    site_table.finish_stone,
    site_table.coursing,
    site_table.direction_face,
    site_table.bonding_material,
    site_table.dating,
    site_table.documentation,
    site_table.biblio,
    site_table.description,
    site_table.interpretation,
    grab_spot.gid,
	grab_spot.name_grab,
    grab_spot.the_geom
    FROM (public.site_table
	JOIN public.grab_spot ON (((grab_spot.name_grab)::text = (site_table.name_site)::text)));
ALTER TABLE public.pyarchinit_grabspot_view OWNER TO postgres;
CREATE or replace VIEW public.pyarchinit_feature_p_view AS
	SELECT site_table.id_sito,
    site_table.location_,
    site_table.mouhafasat,
    site_table.casa,
    site_table.village,
    site_table.antique_name,
    site_table.definition,
    site_table.find_check,
    site_table.sito_path,
    site_table.proj_name,
    site_table.proj_code,
    site_table.geometry_collection,
    site_table.name_site,
    site_table.area,
    site_table.date_start,
    site_table.type_class,
    site_table.grab,
    site_table.survey_type,
    site_table.certainties,
    site_table.supervisor,
    site_table.date_fill,
    site_table.soil_type,
    site_table.topographic_setting,
    site_table.visibility,
    site_table.condition_state,
    site_table.features,
    site_table.disturbance,
    site_table.orientation,
    site_table.length_,
    site_table.width_,
    site_table.depth_,
    site_table.height_,
    site_table.material,
    site_table.finish_stone,
    site_table.coursing,
    site_table.direction_face,
    site_table.bonding_material,
    site_table.dating,
    site_table.documentation,
    site_table.biblio,
    site_table.description,
    site_table.interpretation,
    features.gid,
	features.name_feat,
    features.the_geom
	 FROM (public.site_table
     JOIN public.features ON (((features.name_feat)::text = (site_table.name_site)::text)));
ALTER TABLE public.pyarchinit_feature_p_view OWNER TO postgres;
CREATE or replace view  public.pyarchinit_feature_point_view AS
	SELECT site_table.id_sito,
    site_table.location_,
    site_table.mouhafasat,
    site_table.casa,
    site_table.village,
    site_table.antique_name,
    site_table.definition,
    site_table.find_check,
    site_table.sito_path,
    site_table.proj_name,
    site_table.proj_code,
    site_table.geometry_collection,
    site_table.name_site,
    site_table.area,
    site_table.date_start,
    site_table.type_class,
    site_table.grab,
    site_table.survey_type,
    site_table.certainties,
    site_table.supervisor,
    site_table.date_fill,
    site_table.soil_type,
    site_table.topographic_setting,
    site_table.visibility,
    site_table.condition_state,
    site_table.features,
    site_table.disturbance,
    site_table.orientation,
    site_table.length_,
    site_table.width_,
    site_table.depth_,
    site_table.height_,
    site_table.material,
    site_table.finish_stone,
    site_table.coursing,
    site_table.direction_face,
    site_table.bonding_material,
    site_table.dating,
    site_table.documentation,
    site_table.biblio,
    site_table.description,
    site_table.interpretation,
    features_point.gid,
	features_point.name_f_p,
    features_point.the_geom 
	FROM (public.site_table
	JOIN public.features_point ON (((features_point.name_f_p)::text = (site_table.name_site)::text)));
ALTER TABLE public.pyarchinit_feature_point_view OWNER TO postgres;
CREATE or replace view public.pyarchinit_feature_l_view AS
 SELECT site_table.id_sito,
    site_table.location_,
    site_table.mouhafasat,
    site_table.casa,
    site_table.village,
    site_table.antique_name,
    site_table.definition,
    site_table.find_check,
    site_table.sito_path,
    site_table.proj_name,
    site_table.proj_code,
    site_table.geometry_collection,
    site_table.name_site,
    site_table.area,
    site_table.date_start,
    site_table.type_class,
    site_table.grab,
    site_table.survey_type,
    site_table.certainties,
    site_table.supervisor,
    site_table.date_fill,
    site_table.soil_type,
    site_table.topographic_setting,
    site_table.visibility,
    site_table.condition_state,
    site_table.features,
    site_table.disturbance,
    site_table.orientation,
    site_table.length_,
    site_table.width_,
    site_table.depth_,
    site_table.height_,
    site_table.material,
    site_table.finish_stone,
    site_table.coursing,
    site_table.direction_face,
    site_table.bonding_material,
    site_table.dating,
    site_table.documentation,
    site_table.biblio,
    site_table.description,
    site_table.interpretation,
    features_line.gid,
	features_line.name_f_l,
    features_line.the_geom
FROM (public.site_table
	JOIN public.features_line ON (((features_line.name_f_l)::text = (site_table.name_site)::text)));
ALTER TABLE public.pyarchinit_feature_l_view OWNER TO postgres;
CREATE or replace view  public.pyarchinit_transect_view AS
 SELECT site_table.id_sito,
    site_table.location_,
    site_table.mouhafasat,
    site_table.casa,
    site_table.village,
    site_table.antique_name,
    site_table.definition,
    site_table.find_check,
    site_table.sito_path,
    site_table.proj_name,
    site_table.proj_code,
    site_table.geometry_collection,
    site_table.name_site,
    site_table.area,
    site_table.date_start,
    site_table.type_class,
    site_table.grab,
    site_table.survey_type,
    site_table.certainties,
    site_table.supervisor,
    site_table.date_fill,
    site_table.soil_type,
    site_table.topographic_setting,
    site_table.visibility,
    site_table.condition_state,
    site_table.features,
    site_table.disturbance,
    site_table.orientation,
    site_table.length_,
    site_table.width_,
    site_table.depth_,
    site_table.height_,
    site_table.material,
    site_table.finish_stone,
    site_table.coursing,
    site_table.direction_face,
    site_table.bonding_material,
    site_table.dating,
    site_table.documentation,
    site_table.biblio,
    site_table.description,
    site_table.interpretation,
    transect.gid,
	transect.name_tr,
    transect.the_geom
FROM (public.site_table
     JOIN public.transect ON (((transect.name_tr)::text = (site_table.name_site)::text)));
ALTER TABLE public.pyarchinit_transect_view OWNER TO postgres;

CREATE TABLE IF NOT EXISTS public.eamena_table
(
    id_eamena integer NOT NULL,
    location character varying(200) COLLATE pg_catalog."default",
    name_site character varying(200) COLLATE pg_catalog."default",
    grid text COLLATE pg_catalog."default",
    hp text COLLATE pg_catalog."default",
    d_activity text COLLATE pg_catalog."default",
    role text COLLATE pg_catalog."default",
    activity text COLLATE pg_catalog."default",
    name text COLLATE pg_catalog."default",
    name_type text COLLATE pg_catalog."default",
    d_type text COLLATE pg_catalog."default",
    dfd text COLLATE pg_catalog."default",
    dft text COLLATE pg_catalog."default",
    lc text COLLATE pg_catalog."default",
    mn text COLLATE pg_catalog."default",
    mt text COLLATE pg_catalog."default",
    mu text COLLATE pg_catalog."default",
    ms text COLLATE pg_catalog."default",
    desc_type text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    cd text COLLATE pg_catalog."default",
    pd text COLLATE pg_catalog."default",
    pc text COLLATE pg_catalog."default",
    di text COLLATE pg_catalog."default",
    fft text COLLATE pg_catalog."default",
    ffc text COLLATE pg_catalog."default",
    fs text COLLATE pg_catalog."default",
    fat text COLLATE pg_catalog."default",
    fn text COLLATE pg_catalog."default",
    fai text COLLATE pg_catalog."default",
    it text COLLATE pg_catalog."default",
    ic text COLLATE pg_catalog."default",
    intern text COLLATE pg_catalog."default",
    fi text COLLATE pg_catalog."default",
    sf text COLLATE pg_catalog."default",
    sfc text COLLATE pg_catalog."default",
    tc text COLLATE pg_catalog."default",
    tt text COLLATE pg_catalog."default",
    tp text COLLATE pg_catalog."default",
    ti text COLLATE pg_catalog."default",
    dcc text COLLATE pg_catalog."default",
    dct text COLLATE pg_catalog."default",
    dcert text COLLATE pg_catalog."default",
    et1 text COLLATE pg_catalog."default",
    ec1 text COLLATE pg_catalog."default",
    et2 text COLLATE pg_catalog."default",
    ec2 text COLLATE pg_catalog."default",
    et3 text COLLATE pg_catalog."default",
    ec3 text COLLATE pg_catalog."default",
    et4 text COLLATE pg_catalog."default",
    ec4 text COLLATE pg_catalog."default",
    et5 text COLLATE pg_catalog."default",
    ec5 text COLLATE pg_catalog."default",
    ddf text COLLATE pg_catalog."default",
    ddt text COLLATE pg_catalog."default",
    dob text COLLATE pg_catalog."default",
    doo text COLLATE pg_catalog."default",
    dan text COLLATE pg_catalog."default",
    investigator text COLLATE pg_catalog."default",
    CONSTRAINT eamena_table_pkey PRIMARY KEY (id_eamena),
    CONSTRAINT "ID_eamena_unico" UNIQUE (name_site)

)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE SEQUENCE IF NOT EXISTS public.eamena_table_id_eamena_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.eamena_table_id_eamena_seq OWNER TO postgres;
	
----------------------------------------------------------------------------------------


CREATE SEQUENCE IF NOT EXISTS public.site_line_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.site_line_id_seq
    OWNER TO postgres;

CREATE SEQUENCE IF NOT EXISTS public.site_point_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.site_point_id_seq
    OWNER TO postgres;	

CREATE SEQUENCE IF NOT EXISTS public.site_poligon_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.site_poligon_id_seq
    OWNER TO postgres;	
	
	
	
CREATE TABLE IF NOT EXISTS public.site_line
(
    id integer NOT NULL DEFAULT nextval('site_line_id_seq'::regclass),
    the_geom geometry(LineString,32636),
    gid bigint,
    location character varying COLLATE pg_catalog."default",
    name_f_l character varying COLLATE pg_catalog."default",
    photo1 character varying COLLATE pg_catalog."default",
    photo2 character varying COLLATE pg_catalog."default",
    photo3 character varying COLLATE pg_catalog."default",
    photo4 character varying COLLATE pg_catalog."default",
    photo5 character varying COLLATE pg_catalog."default",
    photo6 character varying COLLATE pg_catalog."default",
    CONSTRAINT site_line_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.site_line
    OWNER to postgres;

-- Index: sidx_site_line_the_geom

-- DROP INDEX public.sidx_site_line_the_geom;

CREATE INDEX IF NOT EXISTS sidx_site_line_the_geom
    ON public.site_line USING gist
    (the_geom)
    TABLESPACE pg_default;
CREATE TABLE IF NOT EXISTS public.site_point
(
    id integer NOT NULL DEFAULT nextval('site_point_id_seq'::regclass),
    the_geom geometry(Point,32636),
    gid bigint,
    location character varying COLLATE pg_catalog."default",
    name_f_p character varying COLLATE pg_catalog."default",
    photo character varying COLLATE pg_catalog."default",
    photo2 character varying COLLATE pg_catalog."default",
    photo3 character varying COLLATE pg_catalog."default",
    photo4 character varying COLLATE pg_catalog."default",
    photo5 character varying COLLATE pg_catalog."default",
    photo6 character varying COLLATE pg_catalog."default",
    CONSTRAINT site_point_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.site_point
    OWNER to postgres;

-- Index: sidx_site_point_the_geom

-- DROP INDEX public.sidx_site_point_the_geom;

CREATE INDEX IF NOT EXISTS sidx_site_point_the_geom
    ON public.site_point USING gist
    (the_geom)
    TABLESPACE pg_default;
CREATE TABLE IF NOT EXISTS public.site_poligon
(
    id integer NOT NULL DEFAULT nextval('site_poligon_id_seq'::regclass),
    the_geom geometry(MultiPolygon,32636),
    name_feat character varying COLLATE pg_catalog."default",
    photo character varying COLLATE pg_catalog."default",
    photo2 character varying COLLATE pg_catalog."default",
    photo3 character varying COLLATE pg_catalog."default",
    photo4 character varying COLLATE pg_catalog."default",
    photo5 character varying COLLATE pg_catalog."default",
    photo6 character varying COLLATE pg_catalog."default",
    location character varying COLLATE pg_catalog."default",
    CONSTRAINT site_poligon_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.site_poligon
    OWNER to postgres;

-- Index: sidx_site_poligon_the_geom

-- DROP INDEX public.sidx_site_poligon_the_geom;

CREATE INDEX IF NOT EXISTS sidx_site_poligon_the_geom
    ON public.site_poligon USING gist
    (the_geom)
    TABLESPACE pg_default;	
--
-- TOC entry 5011 (class 0 OID 0)
-- Dependencies: 20
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

CREATE or replace VIEW public.eamena_line_view AS
	SELECT	eamena_table.id_eamena,
		eamena_table.location ,
        eamena_table.name_site ,
        eamena_table.grid ,
        eamena_table.hp ,
        eamena_table.d_activity ,
        eamena_table.role ,
        eamena_table.activity ,
        eamena_table.name ,
        eamena_table.name_type ,
        eamena_table.d_type ,
        eamena_table.dfd ,
        eamena_table.dft ,
        eamena_table.lc ,
        eamena_table.mn ,
        eamena_table.mt ,
        eamena_table.mu ,
        eamena_table.ms ,
        eamena_table.desc_type, 
        eamena_table.description ,
        eamena_table.cd ,
        eamena_table.pd, 
        eamena_table.pc, 
        eamena_table.di ,
        eamena_table.fft, 
        eamena_table.ffc ,
        eamena_table.fs ,
        eamena_table.fat ,
        eamena_table.fn ,
        eamena_table.fai ,
        eamena_table.it ,
        eamena_table.ic ,
        eamena_table.intern ,
        eamena_table.fi, 
        eamena_table.sf ,
        eamena_table.sfc ,
        eamena_table.tc ,
        eamena_table.tt ,
        eamena_table.tp ,
        eamena_table.ti ,
        eamena_table.dcc ,
        eamena_table.dct ,
        eamena_table.dcert,
        eamena_table.et1 ,
        eamena_table.ec1, 
        eamena_table.et2 ,
        eamena_table.ec2 ,
        eamena_table.et3 ,
        eamena_table.ec3 ,
        eamena_table.et4 ,
        eamena_table.ec4 ,
        eamena_table.et5 ,
        eamena_table.ec5 ,
        eamena_table.ddf ,
        eamena_table.ddt ,
        eamena_table.dob ,
        eamena_table.doo ,
        eamena_table.dan,
        eamena_table.investigator,
		site_line.location as location_1,
		site_line.name_f_l,
		site_line.the_geom
		FROM (public.eamena_table
     JOIN public.site_line ON (((site_line.name_f_l)::text = (eamena_table.name_site)::text)));
ALTER TABLE public.eamena_line_view OWNER TO postgres;

CREATE or replace VIEW public.eamena_point_view AS
	SELECT	eamena_table.id_eamena,
		eamena_table.location ,
        eamena_table.name_site ,
        eamena_table.grid ,
        eamena_table.hp ,
        eamena_table.d_activity ,
        eamena_table.role ,
        eamena_table.activity ,
        eamena_table.name ,
        eamena_table.name_type ,
        eamena_table.d_type ,
        eamena_table.dfd ,
        eamena_table.dft ,
        eamena_table.lc ,
        eamena_table.mn ,
        eamena_table.mt ,
        eamena_table.mu ,
        eamena_table.ms ,
        eamena_table.desc_type, 
        eamena_table.description ,
        eamena_table.cd ,
        eamena_table.pd, 
        eamena_table.pc, 
        eamena_table.di ,
        eamena_table.fft, 
        eamena_table.ffc ,
        eamena_table.fs ,
        eamena_table.fat ,
        eamena_table.fn ,
        eamena_table.fai ,
        eamena_table.it ,
        eamena_table.ic ,
        eamena_table.intern ,
        eamena_table.fi, 
        eamena_table.sf ,
        eamena_table.sfc ,
        eamena_table.tc ,
        eamena_table.tt ,
        eamena_table.tp ,
        eamena_table.ti ,
        eamena_table.dcc ,
        eamena_table.dct ,
        eamena_table.dcert,
        eamena_table.et1 ,
        eamena_table.ec1, 
        eamena_table.et2 ,
        eamena_table.ec2 ,
        eamena_table.et3 ,
        eamena_table.ec3 ,
        eamena_table.et4 ,
        eamena_table.ec4 ,
        eamena_table.et5 ,
        eamena_table.ec5 ,
        eamena_table.ddf ,
        eamena_table.ddt ,
        eamena_table.dob ,
        eamena_table.doo ,
        eamena_table.dan,
        eamena_table.investigator,
		site_point.location as location_1,
		site_point.name_f_p,
		site_point.the_geom
		FROM (public.eamena_table
     JOIN public.site_point ON (((site_point.name_f_p)::text = (eamena_table.name_site)::text)));
ALTER TABLE public.eamena_point_view OWNER TO postgres;

CREATE or replace VIEW public.eamena_poligon_view AS
	SELECT	eamena_table.id_eamena,
		eamena_table.location ,
        eamena_table.name_site ,
        eamena_table.grid ,
        eamena_table.hp ,
        eamena_table.d_activity ,
        eamena_table.role ,
        eamena_table.activity ,
        eamena_table.name ,
        eamena_table.name_type ,
        eamena_table.d_type ,
        eamena_table.dfd ,
        eamena_table.dft ,
        eamena_table.lc ,
        eamena_table.mn ,
        eamena_table.mt ,
        eamena_table.mu ,
        eamena_table.ms ,
        eamena_table.desc_type, 
        eamena_table.description ,
        eamena_table.cd ,
        eamena_table.pd, 
        eamena_table.pc, 
        eamena_table.di ,
        eamena_table.fft, 
        eamena_table.ffc ,
        eamena_table.fs ,
        eamena_table.fat ,
        eamena_table.fn ,
        eamena_table.fai ,
        eamena_table.it ,
        eamena_table.ic ,
        eamena_table.intern ,
        eamena_table.fi, 
        eamena_table.sf ,
        eamena_table.sfc ,
        eamena_table.tc ,
        eamena_table.tt ,
        eamena_table.tp ,
        eamena_table.ti ,
        eamena_table.dcc ,
        eamena_table.dct ,
        eamena_table.dcert,
        eamena_table.et1 ,
        eamena_table.ec1, 
        eamena_table.et2 ,
        eamena_table.ec2 ,
        eamena_table.et3 ,
        eamena_table.ec3 ,
        eamena_table.et4 ,
        eamena_table.ec4 ,
        eamena_table.et5 ,
        eamena_table.ec5 ,
        eamena_table.ddf ,
        eamena_table.ddt ,
        eamena_table.dob ,
        eamena_table.doo ,
        eamena_table.dan,
        eamena_table.investigator,
		site_poligon.location as location_1,
		site_poligon.name_feat,
		site_poligon.the_geom
		FROM (public.eamena_table
     JOIN public.site_poligon ON (((site_poligon.name_feat)::text = (eamena_table.name_site)::text)));
ALTER TABLE public.eamena_poligon_view OWNER TO postgres;

