--
-- PostgreSQL database dump
--

-- Dumped from database version 13.20
-- Dumped by pg_dump version 13.20

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: session_audit; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.session_audit (
    id integer NOT NULL,
    hostname character varying(100) NOT NULL,
    event_type character varying(50) NOT NULL,
    login character varying(100) NOT NULL,
    status character varying(50),
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone,
    os_version character varying(50) NOT NULL,
    os_name character varying(50),
    ip_address character varying(100) NOT NULL,
    client_version character varying(50) NOT NULL,
    agent_info character varying(50),
    audit_source text
);


ALTER TABLE public.session_audit OWNER TO wsm;

--
-- Name: session_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.session_audit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.session_audit_id_seq OWNER TO wsm;

--
-- Name: session_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.session_audit_id_seq OWNED BY public.session_audit.id;


--
-- Name: session_audit id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.session_audit ALTER COLUMN id SET DEFAULT nextval('public.session_audit_id_seq'::regclass);


--
-- Name: session_audit session_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.session_audit
    ADD CONSTRAINT session_audit_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

