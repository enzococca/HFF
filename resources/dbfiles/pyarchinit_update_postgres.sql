 /* alter table dive_log add column bar_start_2 character varying(255);
 alter table dive_log add column bar_end_2 character varying(255);
 alter table dive_log add column dp_2 character varying(255); */
 alter table site_table add column ets character varying(255);
 alter table site_table add column material_c text;
 alter table site_table add column morphology_c text;
 alter table site_table add column collection_c text;


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
    grab_spot.name_grab,
    grab_spot.the_geom AS aa
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
   
    
    features.name_feat,
    features.the_geom AS dd

	 FROM (public.site_table
     JOIN public.features ON (((features.name_feat)::text = (site_table.name_site)::text)));
     
ALTER TABLE public.pyarchinit_feature_p_view OWNER TO postgres;

CREATE or replace public.pyarchinit_feature_point_view AS
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


CREATE or replace public.pyarchinit_feature_l_view AS
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


CREATE or replace public.pyarchinit_transect_view AS
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




