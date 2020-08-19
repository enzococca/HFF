--
-- PostgreSQL database dump
--
-- Dumped from database version 11.1
-- Dumped by pg_dump version 11.1
-- Started on 2019-06-18 06:11:57
SELECT pg_catalog.set_config('search_path', 'public', false);
CREATE EXTENSION postgis;
SET default_tablespace = '';
SET default_with_oids = false;
--
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--
--
-- TOC entry 1646 (class 1255 OID 91711)
-- Name: delete_media_table(); Type: FUNCTION; Schema: public; Owner: postgres
--
CREATE FUNCTION public.delete_media_table() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
--BEGIN
--      DELETE from fauna_azioni WHERE sito=OLD.sito and code=OLD.code;
--RETURN OLD;
--END;
BEGIN
IF OLD.id_media!=OLD.id_media THEN
update media_table set id_media=OLD.id_media;
else 
DELETE from media_table 
where id_media = OLD.id_media ;
end if;
RETURN OLD;
END;
$$;
ALTER FUNCTION public.delete_media_table() OWNER TO postgres;
--
-- TOC entry 1647 (class 1255 OID 91712)
-- Name: delete_media_to_entity_table(); Type: FUNCTION; Schema: public; Owner: postgres
--
CREATE FUNCTION public.delete_media_to_entity_table() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
--BEGIN
--      DELETE from fauna_azioni WHERE sito=OLD.sito and code=OLD.code;
--RETURN OLD;
--END;
BEGIN
IF OLD.id_media!=OLD.id_media THEN
update media_to_entity_table set id_media=OLD.id_media;
else 
DELETE from media_to_entity_table 
where id_media = OLD.id_media ;
end if;
RETURN OLD;
END;
$$;
ALTER FUNCTION public.delete_media_to_entity_table() OWNER TO postgres;
--
-- TOC entry 1648 (class 1255 OID 91713)
-- Name: update_sk_1(); Type: FUNCTION; Schema: public; Owner: postgres
--
CREATE FUNCTION public.update_sk_1() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
myRec RECORD;
BEGIN
if NEW.anatomysk is null then
update sk_1 set
anatomysk = NEW.anatomysk
where codesk = NEW.codesk and site = NEW.site and anatomysk = NEW.anatomysk and
position_sk=NEW.position_sk
and
individuo=NEW.individuo
and
area=NEW.area
and
color=NEW.color;
ELSE
INSERT INTO
sk_1
(
codesk, site,area,individuo,color,position_sk,anatomysk)
select distinct
codesk, site,area,individuo,color,position_sk,
unnest(string_to_array(anatomysk, ',')) AS anatomysk
from sk_table where codesk = NEW.codesk and site = NEW.site and anatomysk = NEW.anatomysk and
position_sk=NEW.position_sk
and
individuo=NEW.individuo
and
area=NEW.area
and
color=NEW.color;
--USING NEW.code, NEW.sito, NEW.azione;
END IF;
RETURN NEW;
END;
$$;
ALTER FUNCTION public.update_sk_1() OWNER TO postgres;
SET default_tablespace = '';
SET default_with_oids = false;
--
-- TOC entry 254 (class 1259 OID 91948)
-- Name: anchor_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.anchor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.anchor_id_seq OWNER TO postgres;
--
-- TOC entry 255 (class 1259 OID 91950)
-- Name: anchor_p_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

-- TOC entry 255 (class 1259 OID 91950)
-- Name: anchor_p_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.anchor_p_gid_seq
    START WITH 3
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.anchor_p_gid_seq OWNER TO postgres;
--
-- TOC entry 256 (class 1259 OID 91952)
-- Name: anchor_point; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.anchor_point (
    gid integer DEFAULT nextval('public.anchor_p_gid_seq'::regclass) NOT NULL,
    site character varying(255),
    code character varying(255),
    years integer,
    link character varying(255),
    the_geom public.geometry(Point,-1),
    type character varying(255),
    obj character varying(255)
);
ALTER TABLE public.anchor_point OWNER TO postgres;
--
-- TOC entry 257 (class 1259 OID 91959)
-- Name: anchor_table; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.anchor_table (
    id_anc integer DEFAULT nextval('public.anchor_id_seq'::regclass) NOT NULL,
    site text,
    divelog_id integer,
    anchors_id character varying(255),
    stone_type character varying(255),
    anchor_type character varying(255),
    anchor_shape character varying(255),
    type_hole character varying(255),
    inscription character varying(255),
    petrography character varying(255),
    weight character varying(255),
    origin character varying(255),
    comparison character varying(255),
    typology character varying(255),
    recovered character varying(255),
    photographed character varying(10),
    conservation_completed character varying(10),
    years integer,
    date_ character varying(255),
    depth numeric(5,2),
    tool_markings character varying(255),
    description_i text,
    petrography_r text,
    ll numeric(4,1),
    rl numeric(4,1),
    ml numeric(4,1),
    tw numeric(4,1),
    bw numeric(4,1),
    mw numeric(4,1),
    rtt numeric(4,1),
    ltt numeric(4,1),
    rtb numeric(4,1),
    ltb numeric(4,1),
    tt numeric(4,1),
    bt numeric(4,1),
    td numeric(4,1),
    rd numeric(4,1),
    ld numeric(4,1),
    tde numeric(4,1),
    rde numeric(4,1),
    lde numeric(4,1),
    tfl numeric(4,1),
    rfl numeric(4,1),
    lfl numeric(4,1),
    tfr numeric(4,1),
    rfr numeric(4,1),
    lfr numeric(4,1),
    tfb numeric(4,1),
    rfb numeric(4,1),
    lfb numeric(4,1),
    tft numeric(4,1),
    rft numeric(4,1),
    lft numeric(4,1),
    area character varying(255),
    bd numeric(4,1),
    bde numeric(4,1),
    bfl numeric(4,1),
    bfr numeric(4,1),
    bfb numeric(4,1),
    bft numeric(4,1)
);
ALTER TABLE public.anchor_table OWNER TO postgres;
--
-- TOC entry 258 (class 1259 OID 91981)
-- Name: art_log_id_art; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.shipwreck_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.shipwreck_id_seq OWNER TO postgres;
--

CREATE TABLE public.shipwreck_table (
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
	name character varying(10),
	status character varying(255)
	
);
ALTER TABLE public.shipwreck_table OWNER TO postgres;
--
-- TOC entry 258 (class 1259 OID 91981)
-- Name: art_log_id_art; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.art_log_id_art
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.art_log_id_art OWNER TO postgres;
--
-- TOC entry 259 (class 1259 OID 91983)
-- Name: artefact_log; Type: TABLE; Schema: public; Owner: postgres
--


CREATE TABLE public.artefact_log (
    divelog_id integer,
    artefact_id character varying(255),
    material character varying(255),
    treatment character varying(255),
    description character varying(2555),
    recovered character varying(10),
    list integer DEFAULT 1 NOT NULL,
    photographed character varying(10),
    conservation_completed character varying(10),
    years integer,
    date_ character varying(255),
    id_art integer DEFAULT nextval('public.art_log_id_art'::regclass) NOT NULL,
    obj character varying(255),
    shape character varying(255),
    depth numeric(5,2),
    tool_markings character varying(255),
    lmin numeric(4,1),
    lmax numeric(4,1),
    wmin numeric(4,1),
    wmax numeric(4,1),
    tmin numeric(4,1),
    tmax numeric(4,1),
    biblio text,
    storage_ character varying(255),
    box integer,
    washed character varying(3),
    site character varying(255),
    area character varying(255)
);
ALTER TABLE public.artefact_log OWNER TO postgres;
--
-- TOC entry 260 (class 1259 OID 91991)
-- Name: artefact_log_id_art_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.artefact_log_id_art_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.artefact_log_id_art_seq OWNER TO postgres;
--
-- TOC entry 261 (class 1259 OID 91993)
-- Name: artefact_p_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.artefact_p_gid_seq
    START WITH 3
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.artefact_p_gid_seq OWNER TO postgres;
--
-- TOC entry 262 (class 1259 OID 91995)
-- Name: artefact_point; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.artefact_point (
    gid integer DEFAULT nextval('public.artefact_p_gid_seq'::regclass) NOT NULL,
    the_geom public.geometry(Point,-1),
    site character varying(255),
    code character varying(255),
    years integer,
    link character varying(255),
    type character varying(255),
    obj character varying(255),
    "X" double precision,
    "Y" double precision,
    rotation double precision,
    "Layer" integer
);
ALTER TABLE public.artefact_point OWNER TO postgres;


--
-- TOC entry 271 (class 1259 OID 152736)
-- Name: coastline_kcs19; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coastline(
    id int NOT NULL,
    the_geom public.geometry(MultiLineString,32636),
    "name_site" character(255)
);


ALTER TABLE public.coastline OWNER TO postgres;


--
-- TOC entry 269 (class 1259 OID 92254)
-- Name: dive_log_id_dive_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.dive_log_id_dive_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.dive_log_id_dive_seq OWNER TO postgres;
--
-- TOC entry 270 (class 1259 OID 92256)
-- Name: dive_log; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.dive_log (
    divelog_id integer,
    area_id character varying(255),
    diver_1 character varying(255),
    diver_2 character varying(255),
    additional_diver character varying(255),
    standby_diver character varying(255),
    task text,
    result text,
    dive_supervisor character varying(255),
    bar_start_diver1 character varying(255),
    bar_end_diver1 character varying(255),
    uw_temperature character varying(255),
    uw_visibility character varying(255),
    uw_current_ character varying(255),
    wind character varying(255),
    breathing_mix character varying(255),
    max_depth character varying(255),
    surface_interval character varying(255),
    comments_ text,
    bottom_time character varying(255),
    photo_nbr integer,
    video_nbr integer,
    camera character varying(255),
    time_in character varying(255),
    time_out character varying(255),
    date_ character varying(255),
    id_dive integer DEFAULT nextval('public.dive_log_id_dive_seq'::regclass) NOT NULL,
    years integer,
    dp_diver1 character varying(255),
    photo_id text,
    video_id text,
    site character varying(255),
    layer character varying(255),
    bar_start_diver2 character varying(255),
    bar_end_diver2 character varying(255),
    dp_diver2 character varying(255)
);
ALTER TABLE public.dive_log OWNER TO postgres;
--
-- TOC entry 271 (class 1259 OID 92263)
-- Name: divle_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.divle_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.divle_log_id_seq OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 92263)
-- Name: divle_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.features_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.features_gid_seq OWNER TO postgres;

--
-- TOC entry 274 (class 1259 OID 92295)
-- Name: features; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.features (
    gid integer DEFAULT nextval('public.features_gid_seq'::regclass) NOT NULL,
    the_geom public.geometry(MultiPolygon,-1),
    id bigint,
    name_feat character varying(200),
    photo character varying(200),
    photo2 character varying(200),
    photo3 character varying(200),
    photo4 character varying(200),
    photo5 character varying(200),
    photo6 character varying(200)
);
ALTER TABLE public.features OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 92263)
-- Name: divle_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.features_l_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.features_l_gid_seq OWNER TO postgres;


--
-- TOC entry 275 (class 1259 OID 92301)
-- Name: features_line; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.features_line (
    gid integer DEFAULT nextval('public.features_l_gid_seq'::regclass) NOT NULL,
    the_geom public.geometry(LineString,-1),
    location character varying(255),
	name_f_l character varying(255),
    photo1 character varying(255),
    photo2 character varying(255),
    photo3 character varying(255),
    photo4 character varying(255),
    photo5 character varying(255),
    photo6 character varying(255)
);
ALTER TABLE public.features_line OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 92263)
-- Name: divle_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.features_p_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.features_p_gid_seq OWNER TO postgres;

--
-- TOC entry 276 (class 1259 OID 92307)
-- Name: features_point; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.features_point (
    gid integer DEFAULT nextval('public.features_p_gid_seq'::regclass) NOT NULL,
    the_geom public.geometry(Point,-1),
    location character varying(255),
	name_f_p character varying(200),
    photo character varying(200),
    photo2 character varying(200),
    photo3 character varying(200),
    photo4 character varying(200),
    photo5 character varying(200),
    photo6 character varying(200)
);
ALTER TABLE public.features_point OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 92263)
-- Name: divle_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.grabspot_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.grabspot_gid_seq OWNER TO postgres;




--
-- TOC entry 277 (class 1259 OID 92327)
-- Name: grab_spot; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.grab_spot (
    gid integer DEFAULT nextval('public.grabspot_gid_seq'::regclass) NOT NULL,
    the_geom public.geometry(Point,-1),
    location character varying(255),
	name_grab character varying(200),
    photo character varying(200),
    photo2 character varying(200),
    photo3 character varying(200),
    photo4 character varying(200),
    photo5 character varying(200),
    photo6 character varying(200)
);
ALTER TABLE public.grab_spot OWNER TO postgres;
--
-- TOC entry 278 (class 1259 OID 92461)
-- Name: media_table; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.media_table (
    id_media integer NOT NULL,
    mediatype text,
    filename text,
    filetype character varying(10),
    filepath text,
    descrizione text,
    tags text
);
ALTER TABLE public.media_table OWNER TO postgres;
--
-- TOC entry 279 (class 1259 OID 92467)
-- Name: media_table_id_media_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.media_table_id_media_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.media_table_id_media_seq OWNER TO postgres;
--
-- TOC entry 5004 (class 0 OID 0)
-- Dependencies: 279
-- Name: media_table_id_media_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.media_table_id_media_seq OWNED BY public.media_table.id_media;
--
-- TOC entry 280 (class 1259 OID 92469)
-- Name: media_thumb_table; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.media_thumb_table (
    id_media_thumb integer NOT NULL,
    id_media integer,
    mediatype text,
    media_filename text,
    media_thumb_filename text,
    filetype character varying(10),
    filepath text,
    path_resize text
);
ALTER TABLE public.media_thumb_table OWNER TO postgres;
--
-- TOC entry 281 (class 1259 OID 92475)
-- Name: media_thumb_table_id_media_thumb_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.media_thumb_table_id_media_thumb_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.media_thumb_table_id_media_thumb_seq OWNER TO postgres;
--
-- TOC entry 5005 (class 0 OID 0)
-- Dependencies: 281
-- Name: media_thumb_table_id_media_thumb_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.media_thumb_table_id_media_thumb_seq OWNED BY public.media_thumb_table.id_media_thumb;
--
-- TOC entry 282 (class 1259 OID 92477)
-- Name: media_to_entity_table; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.media_to_entity_table (
    "id_mediaToEntity" integer NOT NULL,
    id_entity integer,
    entity_type text,
    table_name text,
    id_media integer,
    filepath text,
    media_name text
);
ALTER TABLE public.media_to_entity_table OWNER TO postgres;
--
-- TOC entry 283 (class 1259 OID 92483)
-- Name: media_to_entity_table_id_mediaToEntity_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public."media_to_entity_table_id_mediaToEntity_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public."media_to_entity_table_id_mediaToEntity_seq" OWNER TO postgres;
--
-- TOC entry 5006 (class 0 OID 0)
-- Dependencies: 283
-- Name: media_to_entity_table_id_mediaToEntity_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public."media_to_entity_table_id_mediaToEntity_seq" OWNED BY public.media_to_entity_table."id_mediaToEntity";
--
-- TOC entry 284 (class 1259 OID 92489)
-- Name: mediaentity_view_; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.mediaentity_view_ (
    id_media_thumb integer NOT NULL,
    id_media integer,
    filepath text,
    entity_type text,
    id_media_m integer,
    id_entity integer
);
ALTER TABLE public.mediaentity_view_ OWNER TO postgres;
--
-- TOC entry 285 (class 1259 OID 92495)
-- Name: mediaentity_view_id_media_thumb_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.mediaentity_view_id_media_thumb_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.mediaentity_view_id_media_thumb_seq OWNER TO postgres;
--
-- TOC entry 5008 (class 0 OID 0)
-- Dependencies: 285
-- Name: mediaentity_view_id_media_thumb_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.mediaentity_view_id_media_thumb_seq OWNED BY public.mediaentity_view_.id_media_thumb;
--
-- TOC entry 286 (class 1259 OID 92497)
-- Name: mediaentity_view2; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.mediaentity_view2 (
    id_media_thumb integer DEFAULT nextval('public.mediaentity_view_id_media_thumb_seq'::regclass) NOT NULL,
    id_media integer,
    filepath text,
    entity_type text,
    id_media_m integer,
    id_entity integer
);
ALTER TABLE public.mediaentity_view2 OWNER TO postgres;
--
-- TOC entry 287 (class 1259 OID 92516)
-- Name: obj; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.obj (
    id integer NOT NULL,
    the_geom public.geometry(MultiPoint,-1),
    fid bigint,
    photo character varying(200),
    name_obj character varying(200)
);
ALTER TABLE public.obj OWNER TO postgres;
--
-- TOC entry 288 (class 1259 OID 92522)
-- Name: obj_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.obj_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.obj_id_seq OWNER TO postgres;
--
-- TOC entry 5010 (class 0 OID 0)
-- Dependencies: 288
-- Name: obj_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.obj_id_seq OWNED BY public.obj.id;
--
-- TOC entry 289 (class 1259 OID 92532)
-- Name: pdf_administrator_table; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.pdf_administrator_table (
    id_pdf_administrator integer NOT NULL,
    table_name text,
    schema_griglia text,
    schema_fusione_celle text,
    modello text
);
ALTER TABLE public.pdf_administrator_table OWNER TO postgres;
--
-- TOC entry 290 (class 1259 OID 92538)
-- Name: pdf_administrator_table_id_pdf_administrator_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.pdf_administrator_table_id_pdf_administrator_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.pdf_administrator_table_id_pdf_administrator_seq OWNER TO postgres;
--
-- TOC entry 5011 (class 0 OID 0)
-- Dependencies: 290
-- Name: pdf_administrator_table_id_pdf_administrator_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.pdf_administrator_table_id_pdf_administrator_seq OWNED BY public.pdf_administrator_table.id_pdf_administrator;
--
-- TOC entry 294 (class 1259 OID 92586)
-- Name: pottery_p_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.pottery_p_gid_seq
    START WITH 3
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.pottery_p_gid_seq OWNER TO postgres;
--
-- TOC entry 295 (class 1259 OID 92588)
-- Name: pottery_point; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.pottery_point (
    gid integer NOT NULL,
    the_geom public.geometry(Point,-1),
    site character varying(255),
    code character varying(255),
    years integer,
    link character varying(255),
    type character varying(255),
    "X" numeric,
    "Y" numeric,
    rotation numeric,
    "Layer" integer
);
ALTER TABLE public.pottery_point OWNER TO postgres;
--
-- TOC entry 296 (class 1259 OID 92594)
-- Name: pottery_table_id_rep_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.pottery_table_id_rep_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.pottery_table_id_rep_seq OWNER TO postgres;
--
-- TOC entry 297 (class 1259 OID 92596)
-- Name: pottery_table; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.pottery_table (
    id_rep integer DEFAULT nextval('public.pottery_table_id_rep_seq'::regclass) NOT NULL,
    divelog_id integer,
    site text,
    date_ character varying(20),
    artefact_id character varying(20),
    photographed character varying(10),
    drawing character varying(10),
    retrieved character varying(10),
    inclusions character varying(100),
    percent_inclusion character varying(100),
    specific_part character varying(255),
    form character varying(255),
    typology character varying(255),
    provenance character varying(255),
    munsell_clay character varying(255),
    surf_treatment character varying(255),
    conservation character varying(100),
    depth character varying(10),
    storage_ character varying(255),
    period character varying(50),
    state character varying(50),
    samples character varying(250),
    washed character varying(50),
    dm character varying(255),
    dr character varying(255),
    db character varying(255),
    th character varying(255),
    ph character varying(255),
    bh character varying(255),
    thickmin character varying(255),
    thickmax character varying(255),
    years integer,
    box integer,
    biblio text,
    description text,
    area character varying(255),
    munsell_surf character varying(255),
    category character varying(255),
	wheel_made character varying(10)
);
ALTER TABLE public.pottery_table OWNER TO postgres;
--
-- TOC entry 321 (class 1259 OID 92772)
-- Name: site_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.site_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.site_seq OWNER TO postgres;
--
-- TOC entry 326 (class 1259 OID 97888)
-- Name: site_table; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.site_table (
    id_sito integer DEFAULT nextval('public.site_seq'::regclass) NOT NULL,
    location_ text,
    mouhafasat character varying(255),
    casa character varying(255),
    village character varying(255),
    antique_name character varying(255),
    definition character varying(255),
    find_check integer,
    sito_path character varying DEFAULT 'inserisci path'::character varying,
    proj_name character varying(100),
    proj_code character varying(100),
    geometry_collection character varying(100),
    name_site character varying(100),
    area character varying(100),
    date_start character varying(255),
    date_finish character varying(255),
    type_class character varying(100),
    grab character varying(255),
    survey_type character varying(100),
    certainties character varying(100),
    supervisor character varying(255),
    date_fill character varying(255),
    soil_type character varying(255),
    topographic_setting character varying(255),
    visibility character varying(255),
    condition_state character varying(255),
    features text,
    disturbance text,
    orientation character varying(100),
    length_ numeric(4,2),
    width_ numeric(4,2),
    depth_ numeric(4,2),
    height_ numeric(4,2),
    material character varying(255),
    finish_stone character varying(100),
    coursing character varying(100),
    direction_face character varying(100),
    bonding_material character varying(255),
    dating character varying(255),
    documentation text,
    biblio text,
    description text,
    interpretation text,
    photolog text,
	est character varying(255),
	material_c text,
	morphology_c text,
	collection_c text,
	damage character varying(255),
	country character varying(255)
);
ALTER TABLE public.site_table OWNER TO postgres;
--
-- TOC entry 270 (class 1259 OID 152727)
-- Name: sites_grid; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grid (
    id bigint NOT NULL,
    the_geom public.geometry(MultiPolygon,32636),
    "left" numeric,
    top numeric,
    "right" numeric,
    bottom numeric,
    name character varying(254),
    name_site character varying(254)
);


ALTER TABLE public.grid OWNER TO postgres;



--
-- TOC entry 275 (class 1259 OID 152767)
-- Name: track; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.track (
    id integer NOT NULL,
    the_geom public.geometry(MultiPoint,-1),
    y_proj numeric,
    x_proj numeric,
    ltime character varying(254),
    divelog bigint,
    divers character varying(254),
    obj character varying(254),
    name_site character(255),
    day smallint,
    month smallint
);


ALTER TABLE public.track OWNER TO postgres;


--
-- TOC entry 274 (class 1259 OID 152765)
-- Name: track_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.track_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.track_id_seq OWNER TO postgres;
--
-- TOC entry 321 (class 1259 OID 92772)
-- Name: site_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.transect_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.transect_seq OWNER TO postgres;




--
-- TOC entry 323 (class 1259 OID 92874)
-- Name: transect; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.transect (
    gid integer DEFAULT nextval('public.transect_seq'::regclass) NOT NULL,
    the_geom public.geometry(MultiPolygonZ,-1),
    fid bigint,
    name_tr character varying(80),
	location character varying(255),
    area character varying(200),
    photo character varying(254),
    photo2 character varying(200),
    photo3 character varying(200),
    photo4 character varying(200),
    photo5 character varying(200),
    photo6 character varying(200)
);
ALTER TABLE public.transect OWNER TO postgres;




--
-- TOC entry 308 (class 1259 OID 92704)
-- Name: pyarchinit_siti; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.pyarchinit_siti (
    gid integer NOT NULL,
    id integer,
    site character varying(255),
    link character varying(255),
    the_geom public.geometry(Point,-1)
);
ALTER TABLE public.pyarchinit_siti OWNER TO postgres;
--
-- TOC entry 309 (class 1259 OID 92710)
-- Name: pyarchinit_siti_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.pyarchinit_siti_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.pyarchinit_siti_gid_seq OWNER TO postgres;
--
-- TOC entry 5024 (class 0 OID 0)
-- Dependencies: 309
-- Name: pyarchinit_siti_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.pyarchinit_siti_gid_seq OWNED BY public.pyarchinit_siti.gid;
--
-- TOC entry 310 (class 1259 OID 92712)
-- Name: pyarchinit_thesaurus_sigle; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.pyarchinit_thesaurus_sigle (
    id integer NOT NULL,
    id_thesaurus_sigle bigint,
    nome_tabella character varying,
    sigla character varying,
    sigla_estesa character varying,
    descrizione character varying,
    tipologia_sigla character varying,
    lingua text DEFAULT ''::text
);
ALTER TABLE public.pyarchinit_thesaurus_sigle OWNER TO postgres;
--
-- TOC entry 311 (class 1259 OID 92719)
-- Name: pyarchinit_thesaurus_sigle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.pyarchinit_thesaurus_sigle_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.pyarchinit_thesaurus_sigle_id_seq OWNER TO postgres;
--
-- TOC entry 5026 (class 0 OID 0)
-- Dependencies: 311
-- Name: pyarchinit_thesaurus_sigle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.pyarchinit_thesaurus_sigle_id_seq OWNED BY public.pyarchinit_thesaurus_sigle.id;
--
-- TOC entry 319 (class 1259 OID 92750)
-- Name: qgis_projects; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE public.qgis_projects (
    name text NOT NULL,
    metadata jsonb,
    content bytea
);
ALTER TABLE public.qgis_projects OWNER TO postgres;
--
-- TOC entry 320 (class 1259 OID 92762)
-- Name: ref_id_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.ref_id_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.ref_id_gid_seq OWNER TO postgres;
--
-- TOC entry 322 (class 1259 OID 92782)
-- Name: sk_1_id_1_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.sk_1_id_1_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.sk_1_id_1_seq OWNER TO postgres;
/* --
-- TOC entry 324 (class 1259 OID 92880)
-- Name: transect_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE public.transect_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.transect_id_seq OWNER TO postgres; */
--
-- TOC entry 5032 (class 0 OID 0)
-- Dependencies: 324
-- Name: transect_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.transect_seq OWNED BY public.transect.gid;
--
-- TOC entry 4667 (class 2604 OID 97904)
-- Name: media_table id_media; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.media_table ALTER COLUMN id_media SET DEFAULT nextval('public.media_table_id_media_seq'::regclass);
--
-- TOC entry 4668 (class 2604 OID 97905)
-- Name: media_thumb_table id_media_thumb; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.media_thumb_table ALTER COLUMN id_media_thumb SET DEFAULT nextval('public.media_thumb_table_id_media_thumb_seq'::regclass);
--
-- TOC entry 4669 (class 2604 OID 97906)
-- Name: media_to_entity_table id_mediaToEntity; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.media_to_entity_table ALTER COLUMN "id_mediaToEntity" SET DEFAULT nextval('public."media_to_entity_table_id_mediaToEntity_seq"'::regclass);
--
-- TOC entry 4670 (class 2604 OID 97908)
-- Name: mediaentity_view_ id_media_thumb; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.mediaentity_view_ ALTER COLUMN id_media_thumb SET DEFAULT nextval('public.mediaentity_view_id_media_thumb_seq'::regclass);
--
-- TOC entry 4672 (class 2604 OID 97909)
-- Name: obj id; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.obj ALTER COLUMN id SET DEFAULT nextval('public.obj_id_seq'::regclass);
--
-- TOC entry 4673 (class 2604 OID 97910)
-- Name: pdf_administrator_table id_pdf_administrator; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pdf_administrator_table ALTER COLUMN id_pdf_administrator SET DEFAULT nextval('public.pdf_administrator_table_id_pdf_administrator_seq'::regclass);
--
-- TOC entry 4731 (class 2604 OID 97912)
-- Name: pyarchinit_siti gid; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pyarchinit_siti ALTER COLUMN gid SET DEFAULT nextval('public.pyarchinit_siti_gid_seq'::regclass);
--
-- TOC entry 4733 (class 2604 OID 97913)
-- Name: pyarchinit_thesaurus_sigle id; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pyarchinit_thesaurus_sigle ALTER COLUMN id SET DEFAULT nextval('public.pyarchinit_thesaurus_sigle_id_seq'::regclass);
--
-- TOC entry 4736 (class 2604 OID 97915)
-- Name: transect id; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.transect ALTER COLUMN gid SET DEFAULT nextval('public.transect_seq'::regclass);
ALTER TABLE ONLY public.grab_spot ALTER COLUMN gid SET DEFAULT nextval('public.grabspot_gid_seq'::regclass);
ALTER TABLE ONLY public.features ALTER COLUMN gid SET DEFAULT nextval('public.features_gid_seq'::regclass);
ALTER TABLE ONLY public.features_line ALTER COLUMN gid SET DEFAULT nextval('public.features_l_gid_seq'::regclass);
ALTER TABLE ONLY public.features_point ALTER COLUMN gid SET DEFAULT nextval('public.features_p_gid_seq'::regclass);
--
-- TOC entry 4745 (class 2606 OID 95320)
-- Name: anchor_table ID_artefact_id_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.anchor_table
    ADD CONSTRAINT "ID_artefact_id_unico" UNIQUE (site, anchors_id);
--
-- TOC entry 4766 (class 2606 OID 95326)
-- Name: dive_log ID_divelo_log_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.shipwreck_table
    ADD CONSTRAINT "ID_code_id_unico" UNIQUE (code_id);
--
-- TOC entry 4766 (class 2606 OID 95326)
-- Name: dive_log ID_divelo_log_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dive_log
    ADD CONSTRAINT "ID_divelo_log_unico" UNIQUE (divelog_id, years, site);
--
-- TOC entry 4794 (class 2606 OID 95342)
-- Name: media_to_entity_table ID_mediaToEntity_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.media_to_entity_table
    ADD CONSTRAINT "ID_mediaToEntity_unico" UNIQUE (id_entity, entity_type, id_media);
--
-- TOC entry 4790 (class 2606 OID 95344)
-- Name: media_thumb_table ID_media_thumb_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.media_thumb_table
    ADD CONSTRAINT "ID_media_thumb_unico" UNIQUE (media_thumb_filename);
--
-- TOC entry 4786 (class 2606 OID 95346)
-- Name: media_table ID_media_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.media_table
    ADD CONSTRAINT "ID_media_unico" UNIQUE (filepath);
--
-- TOC entry 4803 (class 2606 OID 95348)
-- Name: pdf_administrator_table ID_pdf_administrator_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pdf_administrator_table
    ADD CONSTRAINT "ID_pdf_administrator_unico" UNIQUE (table_name, modello);
--
-- TOC entry 4816 (class 2606 OID 95352)
-- Name: pottery_table ID_rep_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pottery_table
    ADD CONSTRAINT "ID_rep_unico" UNIQUE (site, artefact_id);
--
-- TOC entry 4844 (class 2606 OID 97922)
-- Name: site_table ID_sito_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.site_table
    ADD CONSTRAINT "ID_sito_unico" UNIQUE (name_site);
--
-- TOC entry 4749 (class 2606 OID 95360)
-- Name: artefact_log ID_unico_artifactlog_id_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.artefact_log
    ADD CONSTRAINT "ID_unico_artifactlog_id_unico" UNIQUE (site, artefact_id);
--
-- TOC entry 4741 (class 2606 OID 95370)
-- Name: anchor_point anchor_point_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.anchor_point
    ADD CONSTRAINT anchor_point_pkey PRIMARY KEY (gid);
--
-- TOC entry 4754 (class 2606 OID 95374)
-- Name: artefact_point artefact_point_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.artefact_point
    ADD CONSTRAINT artefact_point_pkey PRIMARY KEY (gid);
--
-- TOC entry 4777 (class 2606 OID 95452)
-- Name: features_line features_line_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.features_line
    ADD CONSTRAINT features_line_pkey PRIMARY KEY (gid);
--
-- TOC entry 4774 (class 2606 OID 95454)
-- Name: features features_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.features
    ADD CONSTRAINT features_pkey PRIMARY KEY (gid);
--
-- TOC entry 4780 (class 2606 OID 95456)
-- Name: features_point features_point_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.features_point
    ADD CONSTRAINT features_point_pkey PRIMARY KEY (gid);
--
-- TOC entry 4783 (class 2606 OID 95460)
-- Name: grab_spot grab_spot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.grab_spot
    ADD CONSTRAINT grab_spot_pkey PRIMARY KEY (gid);
--
-- TOC entry 4788 (class 2606 OID 95494)
-- Name: media_table media_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.media_table
    ADD CONSTRAINT media_table_pkey PRIMARY KEY (id_media);
--
-- TOC entry 4792 (class 2606 OID 95496)
-- Name: media_thumb_table media_thumb_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.media_thumb_table
    ADD CONSTRAINT media_thumb_table_pkey PRIMARY KEY (id_media_thumb);
--
-- TOC entry 4796 (class 2606 OID 95498)
-- Name: media_to_entity_table media_to_entity_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.media_to_entity_table
    ADD CONSTRAINT media_to_entity_table_pkey PRIMARY KEY ("id_mediaToEntity");
--
-- TOC entry 4798 (class 2606 OID 95500)
-- Name: mediaentity_view_ mediaentity_view_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.mediaentity_view_
    ADD CONSTRAINT mediaentity_view_pkey PRIMARY KEY (id_media_thumb);
--
-- TOC entry 4800 (class 2606 OID 95502)
-- Name: obj obj_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.obj
    ADD CONSTRAINT obj_pkey PRIMARY KEY (id);
--
-- TOC entry 4805 (class 2606 OID 95506)
-- Name: pdf_administrator_table pdf_administrator_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pdf_administrator_table
    ADD CONSTRAINT pdf_administrator_table_pkey PRIMARY KEY (id_pdf_administrator);
--
-- TOC entry 4747 (class 2606 OID 95512)
-- Name: anchor_table pk_id_anc; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.anchor_table
    ADD CONSTRAINT pk_id_anc PRIMARY KEY (id_anc);
--
-- TOC entry 4752 (class 2606 OID 95514)
-- Name: artefact_log pk_id_art; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipwreck_table
    ADD CONSTRAINT pk_id_shipwreck PRIMARY KEY (id_shipwreck);
--
-- TOC entry 4752 (class 2606 OID 95514)
-- Name: artefact_log pk_id_art; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefact_log
    ADD CONSTRAINT pk_id_art PRIMARY KEY (id_art);
--
-- TOC entry 4768 (class 2606 OID 95516)
-- Name: dive_log pk_id_dive; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.dive_log
    ADD CONSTRAINT pk_id_dive PRIMARY KEY (id_dive);
--
-- TOC entry 4814 (class 2606 OID 95528)
-- Name: pottery_point pottery_point_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pottery_point
    ADD CONSTRAINT pottery_point_pkey PRIMARY KEY (gid);
--
-- TOC entry 4818 (class 2606 OID 95530)
-- Name: pottery_table pottery_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pottery_table
    ADD CONSTRAINT pottery_table_pkey PRIMARY KEY (id_rep);
--
-- TOC entry 4828 (class 2606 OID 95534)
-- Name: pyarchinit_siti pyarchinit_siti_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pyarchinit_siti
    ADD CONSTRAINT pyarchinit_siti_pkey PRIMARY KEY (gid);
--
-- TOC entry 4831 (class 2606 OID 95536)
-- Name: pyarchinit_thesaurus_sigle pyarchinit_thesaurus_sigle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pyarchinit_thesaurus_sigle
    ADD CONSTRAINT pyarchinit_thesaurus_sigle_pkey PRIMARY KEY (id);
--
-- TOC entry 4839 (class 2606 OID 95542)
-- Name: qgis_projects qgis_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.qgis_projects
    ADD CONSTRAINT qgis_projects_pkey PRIMARY KEY (name);


--
-- TOC entry 4435 (class 2604 OID 152770)
-- Name: track id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.track ALTER COLUMN id SET DEFAULT nextval('public.track_id_seq'::regclass);

--
-- TOC entry 4513 (class 2606 OID 152740)
-- Name: coastline_kcs19 coastline_kcs19_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coastline
    ADD CONSTRAINT coastline_pkey PRIMARY KEY (id);


--
-- TOC entry 4511 (class 2606 OID 152731)
-- Name: sites_grid sites_grid_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grid
    ADD CONSTRAINT grid_pkey PRIMARY KEY (id);


--
-- TOC entry 4519 (class 2606 OID 152772)
-- Name: track track_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.track
    ADD CONSTRAINT track_pkey PRIMARY KEY (id);










--
-- TOC entry 4846 (class 2606 OID 97924)
-- Name: site_table site_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.site_table
    ADD CONSTRAINT site_table_pkey PRIMARY KEY (id_sito);
--
-- TOC entry 4842 (class 2606 OID 95570)
-- Name: transect transect_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.transect
    ADD CONSTRAINT transect_pkey PRIMARY KEY (gid);
--
-- TOC entry 4750 (class 1259 OID 95577)
-- Name: dive_logartefact_log; Type: INDEX; Schema: public; Owner: postgres
--
CREATE INDEX dive_logartefact_log ON public.artefact_log USING btree (divelog_id);
--
-- TOC entry 4742 (class 1259 OID 95584)
-- Name: sidx_anchor_point_a_the_geom; Type: INDEX; Schema: public; Owner: postgres
--
CREATE INDEX sidx_anchor_point_a_the_geom ON public.anchor_point USING gist (the_geom);
--
-- TOC entry 4743 (class 1259 OID 95585)
-- Name: sidx_anchor_point_the_geom; Type: INDEX; Schema: public; Owner: postgres
--
CREATE INDEX sidx_anchor_point_the_geom ON public.anchor_point USING gist (the_geom);
--
-- TOC entry 4778 (class 1259 OID 95605)
-- Name: sidx_features_line_the_geom; Type: INDEX; Schema: public; Owner: postgres
--
CREATE INDEX sidx_features_line_the_geom ON public.features_line USING gist (the_geom);
--
-- TOC entry 4781 (class 1259 OID 95606)
-- Name: sidx_features_point_the_geom; Type: INDEX; Schema: public; Owner: postgres
--
CREATE INDEX sidx_features_point_the_geom ON public.features_point USING gist (the_geom);
--
-- TOC entry 4775 (class 1259 OID 95607)
-- Name: sidx_features_the_geom; Type: INDEX; Schema: public; Owner: postgres
--
CREATE INDEX sidx_features_the_geom ON public.features USING gist (the_geom);
--
-- TOC entry 4784 (class 1259 OID 95609)
-- Name: sidx_grab_spot_the_geom; Type: INDEX; Schema: public; Owner: postgres
--
CREATE INDEX sidx_grab_spot_the_geom ON public.grab_spot USING gist (the_geom);
--
-- TOC entry 4801 (class 1259 OID 95615)
-- Name: sidx_obj_the_geom; Type: INDEX; Schema: public; Owner: postgres
--
CREATE INDEX sidx_obj_the_geom ON public.obj USING gist (the_geom);
--
-- TOC entry 4840 (class 1259 OID 95630)
-- Name: sidx_transect_geom; Type: INDEX; Schema: public; Owner: postgres
--
CREATE INDEX sidx_transect_geom ON public.transect USING gist (the_geom);
--
-- TOC entry 4847 (class 2620 OID 95631)
-- Name: media_thumb_table delete_media_table; Type: TRIGGER; Schema: public; Owner: postgres
--
CREATE TRIGGER delete_media_table AFTER DELETE OR UPDATE ON public.media_thumb_table FOR EACH ROW EXECUTE PROCEDURE public.delete_media_table();
--
-- TOC entry 4848 (class 2620 OID 95632)
-- Name: media_thumb_table delete_media_to_entity_table; Type: TRIGGER; Schema: public; Owner: postgres
--
CREATE TRIGGER delete_media_to_entity_table AFTER DELETE OR UPDATE ON public.media_thumb_table FOR EACH ROW EXECUTE PROCEDURE public.delete_media_to_entity_table();

------------------------------------------------------------------------------------------------------
CREATE TABLE public.eamena_table
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


CREATE SEQUENCE public.eamena_table_id_eamena_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.eamena_table_id_eamena_seq OWNER TO postgres;
	
----------------------------------------------------------------------------------------


CREATE SEQUENCE public.site_line_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.site_line_id_seq
    OWNER TO postgres;

CREATE SEQUENCE public.site_point_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.site_point_id_seq
    OWNER TO postgres;	

CREATE SEQUENCE public.site_poligon_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.site_poligon_id_seq
    OWNER TO postgres;	
	
CREATE SEQUENCE public.shipwreck_id_p_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.shipwreck_id_p_seq
    OWNER TO postgres;		
	
CREATE TABLE public.site_line
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

CREATE INDEX sidx_site_line_the_geom
    ON public.site_line USING gist
    (the_geom)
    TABLESPACE pg_default;
CREATE TABLE public.site_point
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

CREATE INDEX sidx_site_point_the_geom
    ON public.site_point USING gist
    (the_geom)
    TABLESPACE pg_default;
CREATE TABLE public.site_poligon
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

CREATE INDEX sidx_site_poligon_the_geom
    ON public.site_poligon USING gist
    (the_geom)
    TABLESPACE pg_default;	
--
-- TOC entry 5011 (class 0 OID 0)
-- Dependencies: 20
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--
SET standard_conforming_strings = OFF;
---CREATE SCHEMA "public";
CREATE TABLE public.shipwreck_location
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

DROP TABLE IF EXISTS "public"."grid_eamena_lebanon" CASCADE;
DELETE FROM geometry_columns WHERE f_table_name = 'grid_eamena_lebanon' AND f_table_schema = 'public';
BEGIN;
CREATE TABLE "public"."grid_eamena_lebanon" ( "ogc_fid" SERIAL, CONSTRAINT "grid_eamena_lebanon_pk" PRIMARY KEY ("ogc_fid") );
SELECT AddGeometryColumn('public','grid_eamena_lebanon','the_geom',32636,'MULTIPOLYGON',2);
CREATE INDEX "grid_eamena_lebanon_the_geom_geom_idx" ON "public"."grid_eamena_lebanon" USING GIST ("the_geom");
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "name" VARCHAR(254);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "descriptio" VARCHAR(254);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "timestamp" VARCHAR(24);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "begin" VARCHAR(24);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "end" VARCHAR(24);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "altitudemo" VARCHAR(254);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "tessellate" NUMERIC(10,0);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "extrude" NUMERIC(10,0);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "visibility" NUMERIC(10,0);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "draworder" NUMERIC(10,0);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "icon" VARCHAR(254);
ALTER TABLE "public"."grid_eamena_lebanon" ADD COLUMN "snippet" VARCHAR(254);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F0000010000000103000000010000000500000064EB1072FEF524419DA28CC0E3DE4B412CC85762DCF124415B062FF808154C41F745E704D9A72541D0A86CEDF5154C41D736D38B7FAC25417FE8D5CCCFDF4B4164EB1072FEF524419DA28CC0E3DE4B41', 'E35N33-11', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000002CC85762DCF124415B062FF808154C4184E35238B3ED244187E44BAD2E4B4C41B6E571802AA3254181ABE0861C4C4C41F745E704D9A72541D0A86CEDF5154C412CC85762DCF124415B062FF808154C41', 'E35N33-13', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F0000010000000103000000010000000500000084E35238B3ED244187E44BAD2E4B4C41E41509F982E92441792C5EE054814C4171CB1C04749E25419666A89943824C41B6E571802AA3254181ABE0861C4C4C4184E35238B3ED244187E44BAD2E4B4C41', 'E35N33-31', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000E41509F982E92441792C5EE054814C41B2268AA94BE524416C5FDE917BB74C4122B89B95B5992541FCF837266BB84C4171CB1C04749E25419666A89943824C41E41509F982E92441792C5EE054814C41', 'E35N33-33', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000B2268AA94BE524416C5FDE917BB74C41CDC7EE4E0DE124410B8E42C2A2ED4C414873AC3AEF9425411828012D93EE4C4122B89B95B5992541FCF837266BB84C41B2268AA94BE524416C5FDE917BB74C41', 'E35N34-11', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000CDC7EE4E0DE124410B8E42C2A2ED4C41039158EEC7DC24410956FE71CA234D41BCC516F920902541985D73AEBB244D414873AC3AEF9425411828012D93EE4C41CDC7EE4E0DE124410B8E42C2A2ED4C41', 'E35N34-13', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000039158EEC7DC24410956FE71CA234D4181FBF18C7BD82441C2DF82A1F2594D416E74ACD64A8B25410CA5FBAAE45A4D41BCC516F920902541985D73AEBB244D41039158EEC7DC24410956FE71CA234D41', 'E35N34-31', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000D736D38B7FAC25417FE8D5CCCFDF4B41F745E704D9A72541D0A86CEDF5154C41DA462FDCD85D2641FB7FC6CFFE164C41160D1BED036326413118DFAAD7E04B41D736D38B7FAC25417FE8D5CCCFDF4B41', 'E35N33-12', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000F745E704D9A72541D0A86CEDF5154C41B6E571802AA3254181ABE0861C4C4C416E9B80EAA45826415C766268264D4C41DA462FDCD85D2641FB7FC6CFFE164C41F745E704D9A72541D0A86CEDF5154C41', 'E35N33-14', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000B6E571802AA3254181ABE0861C4C4C4171CB1C04749E25419666A89943824C4192525C1E68532641A27224754E834C416E9B80EAA45826415C766268264D4C41B6E571802AA3254181ABE0861C4C4C41', 'E35N33-32', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F0000010000000103000000010000000500000071CB1C04749E25419666A89943824C4122B89B95B5992541FCF837266BB84C41F4DB1A7E224E2641D0AE7BF676B94C4192525C1E68532641A27224754E834C4171CB1C04749E25419666A89943824C41', 'E35N33-34', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F0000010000000103000000010000000500000022B89B95B5992541FCF837266BB84C414873AC3AEF9425411828012D93EE4C415EC91F10D44826413925D5EC9FEF4C41F4DB1A7E224E2641D0AE7BF676B94C4122B89B95B5992541FCF837266BB84C41', 'E35N34-12', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000004873AC3AEF9425411828012D93EE4C41BCC516F920902541985D73AEBB244D41D8C8D9DA7C432641628E9B58C9254D415EC91F10D44826413925D5EC9FEF4C414873AC3AEF9425411828012D93EE4C41', 'E35N34-14', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000BCC516F920902541985D73AEBB244D416E74ACD64A8B25410CA5FBAAE45A4D41C69EC2E41C3E2641B85E373AF35B4D41D8C8D9DA7C432641628E9B58C9254D41BCC516F920902541985D73AEBB244D41', 'E35N34-32', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000160D1BED036326413118DFAAD7E04B41DA462FDCD85D2641FB7FC6CFFE164C41DEDD3343DC132741557667A323184C41E21905F38B192741070BD75EFBE14B41160D1BED036326413118DFAAD7E04B41', 'E35N33-21', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000DA462FDCD85D2641FB7FC6CFFE164C416E9B80EAA45826415C766268264D4C413AFF6ACF220E27418E14F8554C4E4C41DEDD3343DC132741557667A323184C41DA462FDCD85D2641FB7FC6CFFE164C41', 'E35N33-23', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000006E9B80EAA45826415C766268264D4C4192525C1E68532641A27224754E834C41F1219C9E5F08274179D9F47675844C413AFF6ACF220E27418E14F8554C4E4C416E9B80EAA45826415C766268264D4C41', 'E35N33-41', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F0000010000000103000000010000000500000092525C1E68532641A27224754E834C41F4DB1A7E224E2641D0AE7BF676B94C41B02DC5B7920227410A98C7069FBA4C41F1219C9E5F08274179D9F47675844C4192525C1E68532641A27224754E834C41', 'E35N33-43', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000F4DB1A7E224E2641D0AE7BF676B94C415EC91F10D44826413925D5EC9FEF4C415947F021BCFC26412200D805C9F04C41B02DC5B7920227410A98C7069FBA4C41F4DB1A7E224E2641D0AE7BF676B94C41', 'E35N34-21', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000005EC91F10D44826413925D5EC9FEF4C41D8C8D9DA7C432641628E9B58C9254D4174CA33E4DBF62641839C8B74F3264D415947F021BCFC26412200D805C9F04C415EC91F10D44826413925D5EC9FEF4C41', 'E35N34-23', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000D8C8D9DA7C432641628E9B58C9254D41C69EC2E41C3E2641B85E373AF35B4D418542B205F2F02641B1D045531E5D4D4174CA33E4DBF62641839C8B74F3264D41D8C8D9DA7C432641628E9B58C9254D41', 'E35N34-41', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000DEDD3343DC132741557667A323184C413AFF6ACF220E27418E14F8554C4E4C416E3F0E88A4C327413F9E38548E4F4C41FAE1EA94E3C92741D92FEB6C64194C41DEDD3343DC132741557667A323184C41', 'E35N33-24', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000003AFF6ACF220E27418E14F8554C4E4C41F1219C9E5F08274179D9F47675844C416656A1DB5ABD27412CF7ABA3B8854C416E3F0E88A4C327413F9E38548E4F4C413AFF6ACF220E27418E14F8554C4E4C41', 'E35N33-42', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000F1219C9E5F08274179D9F47675844C41B02DC5B7920227410A98C7069FBA4C412264489706B72741F224A95BE3BB4C416656A1DB5ABD27412CF7ABA3B8854C41F1219C9E5F08274179D9F47675844C41', 'E35N33-44', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000B02DC5B7920227410A98C7069FBA4C415947F021BCFC26412200D805C9F04C41A5FDB4C2A7B027412A0E927C0EF24C412264489706B72741F224A95BE3BB4C41B02DC5B7920227410A98C7069FBA4C41', 'E35N34-22', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000005947F021BCFC26412200D805C9F04C4174CA33E4DBF62641839C8B74F3264D415808A6653EAA2741D293C6063A284D41A5FDB4C2A7B027412A0E927C0EF24C415947F021BCFC26412200D805C9F04C41', 'E35N34-24', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F0000010000000103000000010000000500000074CA33E4DBF62641839C8B74F3264D418542B205F2F02641B1D045531E5D4D41AAB2E787CAA32741348FA4FA655E4D415808A6653EAA2741D293C6063A284D4174CA33E4DBF62641839C8B74F3264D41', 'E35N34-42', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000006E3F0E88A4C327413F9E38548E4F4C416656A1DB5ABD27412CF7ABA3B8854C41DA21202C5A722841C0194C0018874C41253B376D2A792841AB932B68EC504C416E3F0E88A4C327413F9E38548E4F4C41', 'E36N33-31', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000006656A1DB5ABD27412CF7ABA3B8854C412264489706B72741F224A95BE3BB4C4168B240717E6B28410F3D1DFA43BD4C41DA21202C5A722841C0194C0018874C416656A1DB5ABD27412CF7ABA3B8854C41', 'E36N33-33', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000002264489706B72741F224A95BE3BB4C41A5FDB4C2A7B027412A0E927C0EF24C412CE3F24497642841B79CFA5570F34C4168B240717E6B28410F3D1DFA43BD4C412264489706B72741F224A95BE3BB4C41', 'E36N34-11', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000A5FDB4C2A7B027412A0E927C0EF24C415808A6653EAA2741D293C6063A284D4102149FAFA45D284178F43D149D294D412CE3F24497642841B79CFA5570F34C41A5FDB4C2A7B027412A0E927C0EF24C41', 'E36N34-13', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000005808A6653EAA2741D293C6063A284D41AAB2E787CAA32741348FA4FA655E4D412806BCB9A6562841CF1A3F35CA5F4D4102149FAFA45D284178F43D149D294D415808A6653EAA2741D293C6063A284D41', 'E36N34-31', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000DA21202C5A722841C0194C0018874C4168B240717E6B28410F3D1DFA43BD4C412E26379AFA1F2941156090E7C0BE4C417837BAE65D272941D7A2479293884C41DA21202C5A722841C0194C0018874C41', 'E36N33-34', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F0000010000000103000000010000000500000068B240717E6B28410F3D1DFA43BD4C412CE3F24497642841B79CFA5570F34C41FA251BFB8A1829415D117897EEF44C412E26379AFA1F2941156090E7C0BE4C4168B240717E6B28410F3D1DFA43BD4C41', 'E36N34-12', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000002CE3F24497642841B79CFA5570F34C4102149FAFA45D284178F43D149D294D41F31579120F11294174D251A21C2B4D41FA251BFB8A1829415D117897EEF44C412CE3F24497642841B79CFA5570F34C41', 'E36N34-14', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F0000010000000103000000010000000500000002149FAFA45D284178F43D149D294D412806BCB9A6562841CF1A3F35CA5F4D41244E73E9860929410CFF6E084B614D41F31579120F11294174D251A21C2B4D4102149FAFA45D284178F43D149D294D41', 'E36N34-32', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000007837BAE65D272941D7A2479293884C412E26379AFA1F2941156090E7C0BE4C41B603A0667BD42941B3C9DE295AC04C419E35FD6166DC2941502C815F2B8A4C417837BAE65D272941D7A2479293884C41', 'E36N33-43', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F000001000000010300000001000000050000002E26379AFA1F2941156090E7C0BE4C41FA251BFB8A1829415D117897EEF44C419F79893783CC2941EE0CE04689F64C41B603A0667BD42941B3C9DE295AC04C412E26379AFA1F2941156090E7C0BE4C41', 'E36N34-21', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000FA251BFB8A1829415D117897EEF44C41F31579120F11294174D251A21C2B4D41B20E78DE7DC42941BFF7D0B6B82C4D419F79893783CC2941EE0CE04689F64C41FA251BFB8A1829415D117897EEF44C41', 'E36N34-23', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
INSERT INTO "public"."grid_eamena_lebanon" ("the_geom" , "name", "descriptio", "timestamp", "begin", "end", "altitudemo", "tessellate", "extrude", "visibility", "draworder", "icon", "snippet") VALUES ('01060000207C7F00000100000001030000000100000005000000F31579120F11294174D251A21C2B4D41244E73E9860929410CFF6E084B614D41EBC93A656BBC2941D3F3FB79E8624D41B20E78DE7DC42941BFF7D0B6B82C4D41F31579120F11294174D251A21C2B4D41', 'E36N34-41', '<html xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:msxsl="urn:schemas-microsoft-com:xslt">

<head>

<META http-equiv="Content-Type" content="text/html">

<meta http-equiv="content-type" content="text/html; charset=UTF-8">

</head>

<body style="mar', NULL, NULL, NULL, NULL, -1, 0, 0, NULL, NULL, NULL);
COMMIT;

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2018-10-02 21:35:07

--
-- PostgreSQL database dump complete
--
;
