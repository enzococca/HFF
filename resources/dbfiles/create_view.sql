--
-- TOC entry 298 (class 1259 OID 92603)
-- Name: hff_system__anchor_view; Type: VIEW; Schema: public; Owner: postgres
--
CREATE VIEW public.hff_system__anchor_view AS
 SELECT anchor_point.gid,
    --anchor_point.site,
    anchor_point.code,
    anchor_point.link,
    anchor_point.the_geom,
    anchor_point.type,
    anchor_point.obj,
    anchor_table.id_anc,
    anchor_table.site,
    anchor_table.divelog_id,
    anchor_table.anchors_id,
    anchor_table.stone_type,
    anchor_table.anchor_type,
    anchor_table.anchor_shape,
    anchor_table.type_hole,
    anchor_table.inscription,
    anchor_table.petrography,
    anchor_table.weight,
    anchor_table.origin,
    anchor_table.comparison,
    anchor_table.typology,
    anchor_table.recovered,
    anchor_table.photographed,
    anchor_table.conservation_completed,
    anchor_table.years,
    anchor_table.date_,
    anchor_table.depth,
    anchor_table.tool_markings,
    anchor_table.description_i,
    anchor_table.petrography_r,
    anchor_table.area
   FROM (public.anchor_point
     JOIN public.anchor_table ON (((anchor_point.code)::text = (anchor_table.anchors_id)::text)));
ALTER TABLE public.hff_system__anchor_view OWNER TO postgres;
--
-- TOC entry 299 (class 1259 OID 92608)
-- Name: hff_system__art_view; Type: VIEW; Schema: public; Owner: postgres
--
CREATE VIEW public.hff_system__art_view AS
 SELECT artefact_log.divelog_id,
    artefact_log.artefact_id,
    artefact_log.material,
    artefact_log.treatment,
    artefact_log.description,
    artefact_log.recovered,
    artefact_log.list,
    artefact_log.photographed,
    artefact_log.conservation_completed,
    artefact_log.years AS anno,
    artefact_log.date_,
    artefact_log.id_art,
    artefact_log.obj,
    artefact_log.shape,
    artefact_log.depth,
    artefact_log.tool_markings,
    artefact_log.lmin,
    artefact_log.lmax,
    artefact_log.wmin,
    artefact_log.wmax,
    artefact_log.tmin,
    artefact_log.tmax,
    artefact_log.biblio,
    artefact_log.storage_,
    artefact_log.box,
    artefact_log.washed,
    artefact_log.site,
    artefact_log.area,
    artefact_point.gid,
    --artefact_point.site,
    artefact_point.code,
    artefact_point.years,
    artefact_point.link,
    artefact_point.the_geom
   FROM (public.artefact_point
     JOIN public.artefact_log ON (((artefact_point.code)::text = (artefact_log.artefact_id)::text)));
ALTER TABLE public.hff_system__art_view OWNER TO postgres;
--
-- TOC entry 329 (class 1259 OID 106144)
-- Name: hff_system__pot_view; Type: VIEW; Schema: public; Owner: postgres
--
CREATE VIEW public.hff_system__pot_view AS
 SELECT pottery_table.id_rep,
    pottery_table.divelog_id,
    pottery_table.site,
    pottery_table.date_,
    pottery_table.artefact_id,
    pottery_table.photographed,
    pottery_table.drawing,
    pottery_table.retrieved,
    pottery_table.inclusions,
    pottery_table.percent_inclusion,
    pottery_table.specific_part,
    pottery_table.form,
    pottery_table.typology,
    pottery_table.provenance,
    pottery_table.munsell_clay,
    pottery_table.surf_treatment,
    pottery_table.conservation,
    pottery_table.depth,
    pottery_table.storage_,
    pottery_table.period,
    pottery_table.state,
    pottery_table.samples,
    pottery_table.washed,
    pottery_table.dm,
    pottery_table.dr,
    pottery_table.db,
    pottery_table.th,
    pottery_table.ph,
    pottery_table.bh,
    pottery_table.thickmin,
    pottery_table.thickmax,
    pottery_table.years,
    pottery_table.box,
    pottery_table.biblio,
    pottery_table.description,
    pottery_table.area,
    pottery_table.munsell_surf,
    pottery_table.category,
    pottery_point.gid,
    pottery_point.the_geom,
    --pottery_point.site,
    pottery_point.code
   FROM (public.pottery_point
     JOIN public.pottery_table ON (((pottery_point.code)::text = (pottery_table.artefact_id)::text)))
  ORDER BY pottery_table.artefact_id DESC, pottery_point.gid;
ALTER TABLE public.hff_system__pot_view OWNER TO postgres;
--
-- TOC entry 327 (class 1259 OID 97896)
-- Name: hff_system__site_view; Type: VIEW; Schema: public; Owner: postgres
--
CREATE VIEW public.hff_system__grabspot_view AS
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
ALTER TABLE public.hff_system__grabspot_view OWNER TO postgres;
CREATE VIEW public.hff_system__feature_p_view AS
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
ALTER TABLE public.hff_system__feature_p_view OWNER TO postgres;
CREATE VIEW public.hff_system__feature_point_view AS
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
ALTER TABLE public.hff_system__feature_point_view OWNER TO postgres;
CREATE VIEW public.hff_system__feature_l_view AS
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
ALTER TABLE public.hff_system__feature_l_view OWNER TO postgres;
CREATE VIEW public.hff_system__transect_view AS
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
ALTER TABLE public.hff_system__transect_view OWNER TO postgres;
-- TOC entry 328 (class 1259 OID 97938)
-- Name: mediaentity_view; Type: VIEW; Schema: public; Owner: postgres
--
CREATE VIEW public.mediaentity_view AS
 SELECT media_thumb_table.id_media_thumb,
    media_thumb_table.id_media,
    media_thumb_table.filepath,
    media_thumb_table.path_resize,
    media_to_entity_table.entity_type,
    media_to_entity_table.id_media AS id_media_m,
    media_to_entity_table.id_entity
   FROM (public.media_thumb_table
     JOIN public.media_to_entity_table ON ((media_thumb_table.id_media = media_to_entity_table.id_media)))
  ORDER BY media_to_entity_table.id_entity;
ALTER TABLE public.mediaentity_view OWNER TO postgres;

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
ALTER TABLE public.eamena_poligon_view OWNER TO postgres

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
	a.depth_quality as depth_quality, a.coordinates as coordinates, a.acquired_coordinates as acquired_coordinates,	a.position_quality_1 as position_quality_1, a.position_quality_2 as position_quality_2,
	a.l AS l, a.w AS w, a.d AS d, a.t AS t,
	a.cl AS cl, a.cw AS cw, a.cd AS cd,
	a.nickname AS nickname, a.date_built AS date_built,
	a.date_lost AS date_lost, a.description AS description,
	a.history AS history, a.list AS list, a.name as name,
	b.gid AS gid, b.the_geom AS the_geom,
	b.code AS code, b.nationality AS nationality_1,
	b.name_vessel AS name_vessel_1
FROM (public.shipwreck_table AS a
JOIN shipwreck_location AS b ON (((a.code_id)::text = (b.code)::text)));
ALTER TABLE public.shipwreck_view OWNER TO postgres