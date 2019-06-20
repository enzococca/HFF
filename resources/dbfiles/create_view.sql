--
-- TOC entry 298 (class 1259 OID 92603)
-- Name: pyarchinit_anchor_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.pyarchinit_anchor_view AS
 SELECT anchor_point.gid,
    anchor_point.sito,
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
    anchor_table.wight,
    anchor_table.origin,
    anchor_table.comparision,
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


ALTER TABLE public.pyarchinit_anchor_view OWNER TO postgres;

--
-- TOC entry 299 (class 1259 OID 92608)
-- Name: pyarchinit_art_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.pyarchinit_art_view AS
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
    artefact_point.sito,
    artefact_point.code,
    artefact_point.years,
    artefact_point.link,
    artefact_point.the_geom
   FROM (public.artefact_point
     JOIN public.artefact_log ON (((artefact_point.code)::text = (artefact_log.artefact_id)::text)));


ALTER TABLE public.pyarchinit_art_view OWNER TO postgres;






--
-- TOC entry 329 (class 1259 OID 106144)
-- Name: pyarchinit_pot_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.pyarchinit_pot_view AS
 SELECT pottery_table.id_rep,
    pottery_table.divelog_id,
    pottery_table.sito AS site,
    pottery_table.data_,
    pottery_table.artefact_id,
    pottery_table.photographed,
    pottery_table.drawing,
    pottery_table.retrieved,
    pottery_table.fabric,
    pottery_table.percent,
    pottery_table.specific_part,
    pottery_table.specific_shape,
    pottery_table.typology,
    pottery_table.provenience,
    pottery_table.munsell,
    pottery_table.surf_trat,
    pottery_table.treatment,
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
    pottery_table.anno,
    pottery_table.box,
    pottery_table.biblio,
    pottery_table.description,
    pottery_table.area,
    pottery_table.munsell_surf,
    pottery_table.category,
    pottery_point.gid,
    pottery_point.the_geom,
    pottery_point.sito,
    pottery_point.code
   FROM (public.pottery_point
     JOIN public.pottery_table ON (((pottery_point.code)::text = (pottery_table.artefact_id)::text)))
  ORDER BY pottery_table.artefact_id DESC, pottery_point.gid;


ALTER TABLE public.pyarchinit_pot_view OWNER TO postgres;

--
-- TOC entry 327 (class 1259 OID 97896)
-- Name: pyarchinit_site_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.pyarchinit_grabspot_view AS
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
    grab_spot.name_grab,
    grab_spot.the_geom AS aa
   FROM (public.site_table
     JOIN public.grab_spot ON (((grab_spot.name_grab)::text = (site_table.name_site)::text)));
     


ALTER TABLE public.pyarchinit_grabspot_view OWNER TO postgres;

CREATE VIEW public.pyarchinit_feature_p_view AS
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
   
    
    features.name_feat,
    features.the_geom AS dd

	 FROM (public.site_table
     JOIN public.features ON (((features.name_feat)::text = (site_table.name_site)::text)));
     
ALTER TABLE public.pyarchinit_feature_p_view OWNER TO postgres;

CREATE VIEW public.pyarchinit_feature_point_view AS
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
    
    features_point.name_f_p,
    features_point.the_geom AS bb
FROM (public.site_table
JOIN public.features_point ON (((features_point.name_f_p)::text = (site_table.name_site)::text)));
     
ALTER TABLE public.pyarchinit_feature_point_view OWNER TO postgres;


CREATE VIEW public.pyarchinit_feature_l_view AS
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
    
    features_line.name_f_l,
    features_line.the_geom AS cc

FROM (public.site_table
JOIN public.features_line ON (((features_line.name_f_l)::text = (site_table.name_site)::text)));
     
ALTER TABLE public.pyarchinit_feature_l_view OWNER TO postgres;


CREATE VIEW public.pyarchinit_transect_view AS
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
    
    
    transect.name_tr,
    transect.the_geom AS ff

FROM (public.site_table
     JOIN public.transect ON (((transect.name_tr)::text = (site_table.name_site)::text)));
ALTER TABLE public.pyarchinit_transect_view OWNER TO postgres;







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