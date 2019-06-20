--
-- PostgreSQL database dump
--

-- Dumped from database version 11.1
-- Dumped by pg_dump version 11.1

-- Started on 2019-06-18 06:11:57

SELECT pg_catalog.set_config('search_path', 'public', false);CREATE EXTENSION postgis;SET default_tablespace = '';SET default_with_oids = false;

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
    sito character varying(255),
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
    wight character varying(255),
    origin character varying(255),
    comparision character varying(255),
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
    hw numeric(4,1),
    rtt numeric(4,1),
    ltt numeric(4,1),
    rtb numeric(4,1),
    ltb numeric(4,1),
    tt numeric(4,1),
    bt numeric(4,1),
    hrt numeric(4,1),
    hrr numeric(4,1),
    hrl numeric(4,1),
    hdt numeric(4,1),
    hd5 numeric(4,1),
    hdl numeric(4,1),
    flt numeric(4,1),
    flr numeric(4,1),
    fll numeric(4,1),
    frt numeric(4,1),
    frr numeric(4,1),
    frl numeric(4,1),
    fbt numeric(4,1),
    fbr numeric(4,1),
    fbl numeric(4,1),
    ftt numeric(4,1),
    ftr numeric(4,1),
    ftl numeric(4,1),
    area character varying(255),
    qty integer DEFAULT 1 NOT NULL,
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
    gid integer NOT NULL,
    the_geom public.geometry(Point,-1),
    sito character varying(255),
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
    diver_3 character varying(255),
    standby_diver character varying(255),
    task text,
    result text,
    tender character varying(255),
    bar_start character varying(255),
    bar_end character varying(255),
    temperature character varying(255),
    visibility character varying(255),
    current_ character varying(255),
    wind character varying(255),
    breathing_mix character varying(255),
    max_depth character varying(255),
    surface_interval character varying(255),
    comments_ text,
    bottom_time character varying(255),
    photo_nbr integer,
    video_nbr integer,
    camera_of character varying(255),
    time_in character varying(255),
    time_out character varying(255),
    date_ character varying(255),
    id_dive integer DEFAULT nextval('public.dive_log_id_dive_seq'::regclass) NOT NULL,
    years integer,
    dp character varying(255),
    photo_id text,
    video_id text,
    sito character varying(255),
    layer character varying(255),
    bar_start_2 character varying(255),
    bar_end_2 character varying(255),
    dp_2 character varying(255)
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
-- TOC entry 274 (class 1259 OID 92295)
-- Name: features; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.features (
    fid bigint NOT NULL,
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
-- TOC entry 275 (class 1259 OID 92301)
-- Name: features_line; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.features_line (
    id bigint NOT NULL,
    the_geom public.geometry(LineString,-1),
    location character varying(255),
	name_f_l character varying,
    photo1 character varying,
    photo2 character varying,
    photo3 character varying,
    photo4 character varying,
    photo5 character varying,
    photo6 character varying
);


ALTER TABLE public.features_line OWNER TO postgres;

--
-- TOC entry 276 (class 1259 OID 92307)
-- Name: features_point; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.features_point (
    id bigint NOT NULL,
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
-- TOC entry 277 (class 1259 OID 92327)
-- Name: grab_spot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grab_spot (
    id bigint NOT NULL,
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
    sito character varying(255),
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
    sito text,
    data_ character varying(20),
    artefact_id character varying(20),
    photographed character varying(10),
    drawing character varying(10),
    retrieved character varying(10),
    fabric character varying(100),
    percent character varying(100),
    specific_part character varying(255),
    specific_shape character varying(255),
    typology character varying(255),
    provenience character varying(255),
    munsell character varying(255),
    surf_trat character varying(255),
    treatment character varying(100),
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
    anno integer,
    box integer,
    biblio text,
    description text,
    area character varying(255),
    munsell_surf character varying(255),
    category character varying(255)
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
	collection_c text
);


ALTER TABLE public.site_table OWNER TO postgres;

--
-- TOC entry 323 (class 1259 OID 92874)
-- Name: transect; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transect (
    id integer NOT NULL,
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
    siti character varying(255),
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

--
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


ALTER TABLE public.transect_id_seq OWNER TO postgres;

--
-- TOC entry 5032 (class 0 OID 0)
-- Dependencies: 324
-- Name: transect_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transect_id_seq OWNED BY public.transect.id;





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

ALTER TABLE ONLY public.transect ALTER COLUMN id SET DEFAULT nextval('public.transect_id_seq'::regclass);




--
-- TOC entry 4745 (class 2606 OID 95320)
-- Name: anchor_table ID_artefact_id_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anchor_table
    ADD CONSTRAINT "ID_artefact_id_unico" UNIQUE (anchors_id);


--
-- TOC entry 4766 (class 2606 OID 95326)
-- Name: dive_log ID_divelo_log_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dive_log
    ADD CONSTRAINT "ID_divelo_log_unico" UNIQUE (divelog_id, years);








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
    ADD CONSTRAINT "ID_rep_unico" UNIQUE (sito, artefact_id);


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
    ADD CONSTRAINT "ID_unico_artifactlog_id_unico" UNIQUE (artefact_id);




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
    ADD CONSTRAINT features_line_pkey PRIMARY KEY (id);


--
-- TOC entry 4774 (class 2606 OID 95454)
-- Name: features features_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.features
    ADD CONSTRAINT features_pkey PRIMARY KEY (fid);


--
-- TOC entry 4780 (class 2606 OID 95456)
-- Name: features_point features_point_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.features_point
    ADD CONSTRAINT features_point_pkey PRIMARY KEY (id);


--
-- TOC entry 4783 (class 2606 OID 95460)
-- Name: grab_spot grab_spot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grab_spot
    ADD CONSTRAINT grab_spot_pkey PRIMARY KEY (id);


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
    ADD CONSTRAINT transect_pkey PRIMARY KEY (id);




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

