--
-- PostgreSQL database dump
--

-- Dumped from database version 18.1 (Debian 18.1-1.pgdg13+2)
-- Dumped by pg_dump version 18.4 (Ubuntu 18.4-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: __diesel_schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.__diesel_schema_migrations (
    version character varying(50) NOT NULL,
    run_on timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: annotation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.annotation (
    annotation_id character varying NOT NULL,
    annotation_time timestamp without time zone,
    detection_id character varying,
    annotator_id character varying
);


--
-- Name: class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.class (
    class_id character varying NOT NULL,
    class_type character varying,
    common_name character varying,
    tax_kingdom character varying,
    tax_phylum character varying,
    tax_class character varying,
    tax_order character varying,
    tax_family character varying,
    tax_genus character varying,
    tax_species character varying
);


--
-- Name: deployment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.deployment (
    site_id character varying,
    device_id character varying,
    start_date date,
    end_date date,
    deployed_by character varying,
    note character varying,
    lat numeric(10,5),
    lon numeric(10,5),
    geog public.geography,
    deployment_id uuid DEFAULT gen_random_uuid() NOT NULL,
    elevation numeric
);


--
-- Name: device; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device (
    device_id character varying NOT NULL,
    device_name character varying,
    device_type_id character varying,
    serial_number character varying
);


--
-- Name: device_class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_class (
    device_class character varying,
    device_class_id character varying DEFAULT uuidv7() NOT NULL
);


--
-- Name: device_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_type (
    brand character varying,
    model character varying,
    code character varying,
    device_class_id character varying,
    device_type_id character varying DEFAULT uuidv7() NOT NULL
);


--
-- Name: event; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.event (
    event_id character varying NOT NULL,
    type character varying,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    duration numeric,
    event_timestamp timestamp without time zone,
    deployment_id uuid,
    media_id uuid
);



--
-- Name: media; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.media (
    media_id uuid DEFAULT uuidv7() NOT NULL,
    media_type character varying,
    bitrate integer,
    samplerate integer,
    uri character varying(500) NOT NULL
);


--
-- Name: model; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.model (
    model_id character varying NOT NULL,
    name character varying,
    type character varying,
    url character varying
);


--
-- Name: occurrence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.occurrence (
    event_id character varying NOT NULL,
    model_id character varying,
    class_id character varying,
    confidence numeric,
    validator_id character varying,
    annotation character varying,
    occurrence_id character varying NOT NULL,
    occurrence_timestamp timestamp without time zone,
    media_id uuid
);


--
-- Name: person; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.person (
    person_id character varying CONSTRAINT annotator_annotator_id_not_null NOT NULL,
    name character varying,
    email character varying
);


--
-- Name: sensor_measure; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sensor_measure (
    recorded_at timestamp without time zone NOT NULL,
    measure_name character varying NOT NULL,
    measure_value double precision NOT NULL,
    event_id character varying,
    measure_id uuid DEFAULT uuidv7() NOT NULL
);


--
-- Name: site; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site (
    site_code character varying,
    geom public.geometry,
    elevation numeric,
    site_id character varying DEFAULT uuidv7() CONSTRAINT site_site_uuid_not_null NOT NULL
);


--
-- Name: uom; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.uom (
    measure_name character varying NOT NULL,
    unit_of_measure character varying
);

--
-- Name: v_sensor_measure_air_lat_lon_90day; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_sensor_measure_air_lat_lon_90day AS
 WITH int_temp AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS int_temperature
           FROM ((public.sensor_measure sm
             JOIN public.event e_1 ON (((sm.event_id)::text = (e_1.event_id)::text)))
             JOIN public.deployment d_1 ON ((e_1.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'int_temperature'::text)
        ), bat_v AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS bat_v
           FROM ((public.sensor_measure sm
             JOIN public.event e_1 ON (((sm.event_id)::text = (e_1.event_id)::text)))
             JOIN public.deployment d_1 ON ((e_1.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'bat_v'::text)
        ), ext_temp AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS ext_temperature
           FROM ((public.sensor_measure sm
             JOIN public.event e_1 ON (((sm.event_id)::text = (e_1.event_id)::text)))
             JOIN public.deployment d_1 ON ((e_1.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'ext_temperature'::text)
        ), humid AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS humidity
           FROM ((public.sensor_measure sm
             JOIN public.event e_1 ON (((sm.event_id)::text = (e_1.event_id)::text)))
             JOIN public.deployment d_1 ON ((e_1.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'humidity'::text)
        )
 SELECT i.event_id,
    i.recorded_at,
    d.device_id,
    d.lat,
    d.lon,
    d.geog,
    b.bat_v,
    i.int_temperature,
    e.ext_temperature,
    h.humidity
   FROM (((((int_temp i
     JOIN bat_v b ON (((i.event_id)::text = (b.event_id)::text)))
     JOIN ext_temp e ON (((i.event_id)::text = (e.event_id)::text)))
     JOIN humid h ON (((i.event_id)::text = (h.event_id)::text)))
     JOIN public.event t ON (((i.event_id)::text = (t.event_id)::text)))
     JOIN public.deployment d ON ((t.deployment_id = d.deployment_id)))
  WHERE (i.recorded_at >= (now() - '90 days'::interval))
  ORDER BY i.recorded_at DESC;


--
-- Name: v_sensor_measure_soil_lat_lon_90day; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_sensor_measure_soil_lat_lon_90day AS
 WITH cond AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS soil_conductivity
           FROM ((public.sensor_measure sm
             JOIN public.event e_1 ON (((sm.event_id)::text = (e_1.event_id)::text)))
             JOIN public.deployment d_1 ON ((e_1.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'soil_conductivity'::text)
        ), bat_v AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS bat_v
           FROM ((public.sensor_measure sm
             JOIN public.event e_1 ON (((sm.event_id)::text = (e_1.event_id)::text)))
             JOIN public.deployment d_1 ON ((e_1.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'bat_v'::text)
        ), water AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS soil_water
           FROM ((public.sensor_measure sm
             JOIN public.event e_1 ON (((sm.event_id)::text = (e_1.event_id)::text)))
             JOIN public.deployment d_1 ON ((e_1.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'soil_water'::text)
        ), tem AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS soil_temperature
           FROM ((public.sensor_measure sm
             JOIN public.event e_1 ON (((sm.event_id)::text = (e_1.event_id)::text)))
             JOIN public.deployment d_1 ON ((e_1.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'soil_temperature'::text)
        )
 SELECT i.event_id,
    i.recorded_at,
    d.device_id,
    d.lat,
    d.lon,
    d.geog,
    b.bat_v,
    i.soil_conductivity,
    e.soil_temperature,
    w.soil_water
   FROM (((((cond i
     JOIN bat_v b ON (((i.event_id)::text = (b.event_id)::text)))
     JOIN tem e ON (((i.event_id)::text = (e.event_id)::text)))
     JOIN water w ON (((i.event_id)::text = (w.event_id)::text)))
     JOIN public.event t ON (((i.event_id)::text = (t.event_id)::text)))
     JOIN public.deployment d ON ((t.deployment_id = d.deployment_id)))
  WHERE (i.recorded_at >= (now() - '90 days'::interval))
  ORDER BY i.recorded_at DESC;


--
-- Name: v_sensor_measure_station_lat_lon_90day; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_sensor_measure_station_lat_lon_90day AS
 WITH wg AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS peak_wind_gust
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'peak_wind_gust'::text)
        ), li AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS light_intensity
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'light_intensity'::text)
        ), rf AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS rainfall_last_10_mins
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'rainfall_last_10_mins'::text)
        ), bp AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS barometric_pressure
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'barometric_pressure'::text)
        ), ui AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS uv_index
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'uv_index'::text)
        ), ah AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS air_humidity
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'air_humidity'::text)
        ), at AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS air_temperature
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'air_temperature'::text)
        ), ri AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS rainfall_intensity
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'rainfall_intensity'::text)
        ), ws AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS wind_speed
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'wind_speed'::text)
        ), wd AS (
         SELECT sm.event_id,
            sm.recorded_at,
            sm.measure_value AS wind_direction
           FROM ((public.sensor_measure sm
             JOIN public.event e ON (((sm.event_id)::text = (e.event_id)::text)))
             JOIN public.deployment d_1 ON ((e.deployment_id = d_1.deployment_id)))
          WHERE ((sm.measure_name)::text = 'wind_direction'::text)
        )
 SELECT i.event_id,
    i.recorded_at,
    d.device_id,
    d.lat,
    d.lon,
    d.geog,
    li.light_intensity,
    bp.barometric_pressure,
    ui.uv_index,
    ah.air_humidity,
    at.air_temperature,
    ri.rainfall_intensity,
    rf.rainfall_last_10_mins,
    i.peak_wind_gust,
    ws.wind_speed,
    wd.wind_direction
   FROM (((((((((((wg i
     JOIN li ON (((i.event_id)::text = (li.event_id)::text)))
     JOIN rf ON (((i.event_id)::text = (rf.event_id)::text)))
     JOIN bp ON (((i.event_id)::text = (bp.event_id)::text)))
     JOIN ui ON (((i.event_id)::text = (ui.event_id)::text)))
     JOIN ah ON (((i.event_id)::text = (ah.event_id)::text)))
     JOIN at ON (((i.event_id)::text = (at.event_id)::text)))
     JOIN ri ON (((i.event_id)::text = (ri.event_id)::text)))
     JOIN ws ON (((i.event_id)::text = (ws.event_id)::text)))
     JOIN wd ON (((i.event_id)::text = (wd.event_id)::text)))
     JOIN public.event t ON (((i.event_id)::text = (t.event_id)::text)))
     JOIN public.deployment d ON ((t.deployment_id = d.deployment_id)))
  WHERE (i.recorded_at >= (now() - '90 days'::interval))
  ORDER BY i.recorded_at DESC;


--
-- Name: __diesel_schema_migrations __diesel_schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.__diesel_schema_migrations
    ADD CONSTRAINT __diesel_schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: annotation annotation_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.annotation
    ADD CONSTRAINT annotation_pk PRIMARY KEY (annotation_id);


--
-- Name: deployment deployment_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deployment
    ADD CONSTRAINT deployment_pk PRIMARY KEY (deployment_id);


--
-- Name: occurrence detection_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.occurrence
    ADD CONSTRAINT detection_pk PRIMARY KEY (occurrence_id);


--
-- Name: device_class device_class_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_class
    ADD CONSTRAINT device_class_pk PRIMARY KEY (device_class_id);


--
-- Name: device_type device_type_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_type
    ADD CONSTRAINT device_type_pk PRIMARY KEY (device_type_id);


--
-- Name: event event_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pk PRIMARY KEY (event_id);


--
-- Name: media media_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media
    ADD CONSTRAINT media_pk PRIMARY KEY (media_id);


--
-- Name: model model_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.model
    ADD CONSTRAINT model_pk PRIMARY KEY (model_id);


--
-- Name: person person_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.person
    ADD CONSTRAINT person_pk PRIMARY KEY (person_id);


--
-- Name: device recorder_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT recorder_pk PRIMARY KEY (device_id);


--
-- Name: sensor_measure sensor_measure_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensor_measure
    ADD CONSTRAINT sensor_measure_pk PRIMARY KEY (measure_id);


--
-- Name: site site_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site
    ADD CONSTRAINT site_pk PRIMARY KEY (site_id);


--
-- Name: site site_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site
    ADD CONSTRAINT site_unique UNIQUE (site_code);


--
-- Name: class species_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class
    ADD CONSTRAINT species_pk PRIMARY KEY (class_id);


--
-- Name: uom uom_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uom
    ADD CONSTRAINT uom_pk PRIMARY KEY (measure_name);


--
-- Name: annotation annotation_annotator_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.annotation
    ADD CONSTRAINT annotation_annotator_fk FOREIGN KEY (annotator_id) REFERENCES public.person(person_id);


--
-- Name: annotation annotation_detection_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.annotation
    ADD CONSTRAINT annotation_detection_fk FOREIGN KEY (detection_id) REFERENCES public.occurrence(occurrence_id);


--
-- Name: deployment deployment_device_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deployment
    ADD CONSTRAINT deployment_device_fk FOREIGN KEY (device_id) REFERENCES public.device(device_id);


--
-- Name: deployment deployment_site_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deployment
    ADD CONSTRAINT deployment_site_fk FOREIGN KEY (site_id) REFERENCES public.site(site_id);


--
-- Name: occurrence detection_capture_event_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.occurrence
    ADD CONSTRAINT detection_capture_event_fk FOREIGN KEY (event_id) REFERENCES public.event(event_id);


--
-- Name: occurrence detection_model_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.occurrence
    ADD CONSTRAINT detection_model_fk FOREIGN KEY (model_id) REFERENCES public.model(model_id);


--
-- Name: occurrence detection_species_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.occurrence
    ADD CONSTRAINT detection_species_fk FOREIGN KEY (class_id) REFERENCES public.class(class_id);


--
-- Name: device_type device_class_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_type
    ADD CONSTRAINT device_class_fk FOREIGN KEY (device_class_id) REFERENCES public.device_class(device_class_id);


--
-- Name: device device_dtype_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_dtype_fk FOREIGN KEY (device_type_id) REFERENCES public.device_type(device_type_id);


--
-- Name: event event_deployment_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_deployment_id_fk FOREIGN KEY (deployment_id) REFERENCES public.deployment(deployment_id);


--
-- Name: event event_media_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_media_fk FOREIGN KEY (media_id) REFERENCES public.media(media_id);


--
-- Name: occurrence occurrence_media_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.occurrence
    ADD CONSTRAINT occurrence_media_fk FOREIGN KEY (media_id) REFERENCES public.media(media_id);


--
-- Name: occurrence occurrence_person_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.occurrence
    ADD CONSTRAINT occurrence_person_fk FOREIGN KEY (validator_id) REFERENCES public.person(person_id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: sensor_measure sensor_measure_event_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensor_measure
    ADD CONSTRAINT sensor_measure_event_fk FOREIGN KEY (event_id) REFERENCES public.event(event_id);

--
-- Name:  sensor_measure sensor_measure_uom_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensor_measure
    ADD CONSTRAINT sensor_measure_uom_fk FOREIGN KEY (measure_name) REFERENCES public.uom(measure_name);



--
-- PostgreSQL database dump complete
--


