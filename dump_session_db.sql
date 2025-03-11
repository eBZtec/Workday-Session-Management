--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

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
-- Name: certificate_authority; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.certificate_authority (
    id integer NOT NULL,
    fqdn character varying(100) NOT NULL,
    certificate text NOT NULL,
    validity timestamp with time zone NOT NULL
);


ALTER TABLE public.certificate_authority OWNER TO wsm;

--
-- Name: certificate_authority_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.certificate_authority_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.certificate_authority_id_seq OWNER TO wsm;

--
-- Name: certificate_authority_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.certificate_authority_id_seq OWNED BY public.certificate_authority.id;


--
-- Name: client; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.client (
    hostname character varying(100) NOT NULL,
    ip_address character varying(100) NOT NULL,
    client_version character varying(50) NOT NULL,
    os_name character varying(50),
    os_version character varying(50) NOT NULL,
    uptime character varying(50),
    agent_info character varying(50),
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone,
    certificate_authority_id integer
);


ALTER TABLE public.client OWNER TO wsm;

--
-- Name: events; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.events (
    id integer NOT NULL,
    event_type character varying(50) NOT NULL,
    description character varying(255) NOT NULL,
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone
);


ALTER TABLE public.events OWNER TO wsm;

--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.events_id_seq OWNER TO wsm;

--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;


--
-- Name: exceptions; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.exceptions (
    id integer NOT NULL,
    type character varying(50),
    ip_address character varying(50),
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone NOT NULL
);


ALTER TABLE public.exceptions OWNER TO wsm;

--
-- Name: exceptions_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.exceptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exceptions_id_seq OWNER TO wsm;

--
-- Name: exceptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.exceptions_id_seq OWNED BY public.exceptions.id;


--
-- Name: extended_workhours; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.extended_workhours (
    id integer NOT NULL,
    std_wrk_id integer NOT NULL,
    uid character varying,
    extension_start_time timestamp without time zone NOT NULL,
    extension_end_time timestamp without time zone NOT NULL,
    extended_workhours_type character varying(2) NOT NULL,
    uf character varying(2) NOT NULL,
    c character varying(100) NOT NULL,
    week_days_count character varying(7) NOT NULL,
    extension_active integer NOT NULL,
    ou integer,
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone NOT NULL
);


ALTER TABLE public.extended_workhours OWNER TO wsm;

--
-- Name: extended_workhours_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.extended_workhours_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.extended_workhours_id_seq OWNER TO wsm;

--
-- Name: extended_workhours_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.extended_workhours_id_seq OWNED BY public.extended_workhours.id;


--
-- Name: holidays; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.holidays (
    id integer NOT NULL,
    name character varying(20) NOT NULL,
    day integer NOT NULL,
    month integer NOT NULL,
    city integer NOT NULL,
    holiday_type character varying(2) NOT NULL,
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone NOT NULL
);


ALTER TABLE public.holidays OWNER TO wsm;

--
-- Name: holidays_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.holidays_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holidays_id_seq OWNER TO wsm;

--
-- Name: holidays_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.holidays_id_seq OWNED BY public.holidays.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    std_wrk_id integer,
    uid character varying(50) NOT NULL,
    message character varying(200) NOT NULL,
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone NOT NULL
);


ALTER TABLE public.messages OWNER TO wsm;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.messages_id_seq OWNER TO wsm;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.sessions (
    hostname character varying(100) NOT NULL,
    event_type character varying(50) NOT NULL,
    "user" character varying(100) NOT NULL,
    status character varying(50),
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone
);


ALTER TABLE public.sessions OWNER TO wsm;

--
-- Name: standard_workhours; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.standard_workhours (
    id integer NOT NULL,
    uid character varying(50) NOT NULL,
    start_time character varying(5) NOT NULL,
    end_time character varying(5) NOT NULL,
    allowed_work_hours text,
    uf character varying(2) NOT NULL,
    st character varying(35) NOT NULL,
    c character varying(100) NOT NULL,
    weekdays character varying(7) NOT NULL,
    session_termination_action character varying(15),
    cn character varying(240) NOT NULL,
    l character varying(240),
    unrestricted boolean,
    enable boolean NOT NULL,
    deactivation_date timestamp with time zone,
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone NOT NULL
);


ALTER TABLE public.standard_workhours OWNER TO wsm;

--
-- Name: standard_workhours_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.standard_workhours_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.standard_workhours_id_seq OWNER TO wsm;

--
-- Name: standard_workhours_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.standard_workhours_id_seq OWNED BY public.standard_workhours.id;


--
-- Name: target; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.target (
    id integer NOT NULL,
    target character varying(100) NOT NULL,
    service character varying(100) NOT NULL,
    enabled integer NOT NULL,
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone NOT NULL
);


ALTER TABLE public.target OWNER TO wsm;

--
-- Name: target_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.target_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.target_id_seq OWNER TO wsm;

--
-- Name: target_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.target_id_seq OWNED BY public.target.id;


--
-- Name: target_status; Type: TABLE; Schema: public; Owner: wsm
--

CREATE TABLE public.target_status (
    id integer NOT NULL,
    std_wrk_id integer,
    id_target integer NOT NULL,
    uuid character varying(37),
    create_timestamp timestamp with time zone NOT NULL,
    update_timestamp timestamp with time zone NOT NULL
);


ALTER TABLE public.target_status OWNER TO wsm;

--
-- Name: target_status_id_seq; Type: SEQUENCE; Schema: public; Owner: wsm
--

CREATE SEQUENCE public.target_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.target_status_id_seq OWNER TO wsm;

--
-- Name: target_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wsm
--

ALTER SEQUENCE public.target_status_id_seq OWNED BY public.target_status.id;


--
-- Name: certificate_authority id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.certificate_authority ALTER COLUMN id SET DEFAULT nextval('public.certificate_authority_id_seq'::regclass);


--
-- Name: events id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- Name: exceptions id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.exceptions ALTER COLUMN id SET DEFAULT nextval('public.exceptions_id_seq'::regclass);


--
-- Name: extended_workhours id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.extended_workhours ALTER COLUMN id SET DEFAULT nextval('public.extended_workhours_id_seq'::regclass);


--
-- Name: holidays id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.holidays ALTER COLUMN id SET DEFAULT nextval('public.holidays_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: standard_workhours id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.standard_workhours ALTER COLUMN id SET DEFAULT nextval('public.standard_workhours_id_seq'::regclass);


--
-- Name: target id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.target ALTER COLUMN id SET DEFAULT nextval('public.target_id_seq'::regclass);


--
-- Name: target_status id; Type: DEFAULT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.target_status ALTER COLUMN id SET DEFAULT nextval('public.target_status_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: certificate_authority certificate_authority_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.certificate_authority
    ADD CONSTRAINT certificate_authority_pkey PRIMARY KEY (id);


--
-- Name: client client_certificate_authority_id_key; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_certificate_authority_id_key UNIQUE (certificate_authority_id);


--
-- Name: client client_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_pkey PRIMARY KEY (hostname);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: exceptions exceptions_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.exceptions
    ADD CONSTRAINT exceptions_pkey PRIMARY KEY (id);


--
-- Name: extended_workhours extended_workhours_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.extended_workhours
    ADD CONSTRAINT extended_workhours_pkey PRIMARY KEY (id);


--
-- Name: holidays holidays_name_key; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.holidays
    ADD CONSTRAINT holidays_name_key UNIQUE (name);


--
-- Name: holidays holidays_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.holidays
    ADD CONSTRAINT holidays_pkey PRIMARY KEY (id, day, month);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY ("user", hostname);


--
-- Name: standard_workhours standard_workhours_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.standard_workhours
    ADD CONSTRAINT standard_workhours_pkey PRIMARY KEY (id);


--
-- Name: standard_workhours standard_workhours_uid_key; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.standard_workhours
    ADD CONSTRAINT standard_workhours_uid_key UNIQUE (uid);


--
-- Name: target target_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.target
    ADD CONSTRAINT target_pkey PRIMARY KEY (id);


--
-- Name: target_status target_status_pkey; Type: CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.target_status
    ADD CONSTRAINT target_status_pkey PRIMARY KEY (id);


--
-- Name: client client_certificate_authority_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_certificate_authority_id_fkey FOREIGN KEY (certificate_authority_id) REFERENCES public.certificate_authority(id);


--
-- Name: extended_workhours extended_workhours_std_wrk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.extended_workhours
    ADD CONSTRAINT extended_workhours_std_wrk_id_fkey FOREIGN KEY (std_wrk_id) REFERENCES public.standard_workhours(id);


--
-- Name: messages messages_std_wrk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_std_wrk_id_fkey FOREIGN KEY (std_wrk_id) REFERENCES public.standard_workhours(id);


--
-- Name: sessions sessions_hostname_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_hostname_fkey FOREIGN KEY (hostname) REFERENCES public.client(hostname);


--
-- Name: target_status target_status_id_target_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.target_status
    ADD CONSTRAINT target_status_id_target_fkey FOREIGN KEY (id_target) REFERENCES public.target(id);


--
-- Name: target_status target_status_std_wrk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wsm
--

ALTER TABLE ONLY public.target_status
    ADD CONSTRAINT target_status_std_wrk_id_fkey FOREIGN KEY (std_wrk_id) REFERENCES public.standard_workhours(id);


--
-- PostgreSQL database dump complete
--

