--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: applications; Type: TABLE; Schema: public; Owner: hr_bot_user1
--

CREATE TABLE public.applications (
    id integer NOT NULL,
    job_id integer NOT NULL,
    applicant_id integer NOT NULL,
    cover_letter text,
    resume_path character varying(255),
    portfolio_url character varying(255),
    expected_salary integer,
    available_from date,
    notice_period character varying(50),
    preferred_contact_method character varying(20),
    contact_time_preference character varying(50),
    status character varying(20),
    employer_notes text,
    applicant_notes text,
    interview_scheduled boolean,
    interview_date timestamp without time zone,
    interview_type character varying(20),
    interview_notes text,
    employer_rating integer,
    employer_feedback text,
    applicant_rating integer,
    applicant_feedback text,
    source character varying(50),
    ip_address character varying(45),
    user_agent character varying(255),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    reviewed_at timestamp without time zone,
    responded_at timestamp without time zone
);


ALTER TABLE public.applications OWNER TO hr_bot_user1;

--
-- Name: applications_id_seq; Type: SEQUENCE; Schema: public; Owner: hr_bot_user1
--

CREATE SEQUENCE public.applications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.applications_id_seq OWNER TO hr_bot_user1;

--
-- Name: applications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: hr_bot_user1
--

ALTER SEQUENCE public.applications_id_seq OWNED BY public.applications.id;


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: hr_bot_user1
--

CREATE TABLE public.jobs (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    company character varying(100) NOT NULL,
    location character varying(100),
    salary_min integer,
    salary_max integer,
    salary_currency character varying(10),
    salary_period character varying(20),
    employment_type character varying(50),
    experience_level character varying(50),
    education_level character varying(50),
    requirements text,
    responsibilities text,
    benefits text,
    skills_required text,
    contact_email character varying(120),
    contact_phone character varying(20),
    contact_person character varying(100),
    company_website character varying(255),
    application_url character varying(255),
    category character varying(50),
    tags text,
    priority integer,
    is_active boolean,
    is_featured boolean,
    is_remote boolean,
    is_urgent boolean,
    views_count integer,
    applications_count integer,
    expires_at timestamp without time zone,
    published_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    employer_id integer NOT NULL
);


ALTER TABLE public.jobs OWNER TO hr_bot_user1;

--
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: hr_bot_user1
--

CREATE SEQUENCE public.jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jobs_id_seq OWNER TO hr_bot_user1;

--
-- Name: jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: hr_bot_user1
--

ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: hr_bot_user1
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(100) NOT NULL,
    subscription_type character varying(50) NOT NULL,
    criteria text NOT NULL,
    frequency character varying(20) NOT NULL,
    notification_time time without time zone,
    notification_days character varying(20),
    min_salary integer,
    max_salary integer,
    employment_types text,
    experience_levels text,
    locations text,
    categories text,
    exclude_keywords text,
    company_blacklist text,
    only_remote boolean,
    only_featured boolean,
    last_notification_sent timestamp without time zone,
    last_job_id_sent integer,
    total_notifications_sent integer,
    total_jobs_found integer,
    is_active boolean,
    is_paused boolean,
    max_notifications_per_day integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    expires_at timestamp without time zone
);


ALTER TABLE public.subscriptions OWNER TO hr_bot_user1;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: hr_bot_user1
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO hr_bot_user1;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: hr_bot_user1
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: hr_bot_user1
--

CREATE TABLE public.users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    username character varying(50),
    first_name character varying(50),
    last_name character varying(50),
    email character varying(120),
    phone character varying(20),
    user_type character varying(20) NOT NULL,
    company character varying(100),
    "position" character varying(100),
    location character varying(100),
    bio text,
    skills text,
    experience_years integer,
    education text,
    resume_path character varying(255),
    portfolio_url character varying(255),
    notification_enabled boolean,
    language character varying(10),
    timezone character varying(50),
    is_active boolean,
    is_verified boolean,
    last_activity timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.users OWNER TO hr_bot_user1;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: hr_bot_user1
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO hr_bot_user1;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: hr_bot_user1
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: applications id; Type: DEFAULT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.applications ALTER COLUMN id SET DEFAULT nextval('public.applications_id_seq'::regclass);


--
-- Name: jobs id; Type: DEFAULT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: applications; Type: TABLE DATA; Schema: public; Owner: hr_bot_user1
--

COPY public.applications (id, job_id, applicant_id, cover_letter, resume_path, portfolio_url, expected_salary, available_from, notice_period, preferred_contact_method, contact_time_preference, status, employer_notes, applicant_notes, interview_scheduled, interview_date, interview_type, interview_notes, employer_rating, employer_feedback, applicant_rating, applicant_feedback, source, ip_address, user_agent, created_at, updated_at, reviewed_at, responded_at) FROM stdin;
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: hr_bot_user1
--

COPY public.jobs (id, title, description, company, location, salary_min, salary_max, salary_currency, salary_period, employment_type, experience_level, education_level, requirements, responsibilities, benefits, skills_required, contact_email, contact_phone, contact_person, company_website, application_url, category, tags, priority, is_active, is_featured, is_remote, is_urgent, views_count, applications_count, expires_at, published_at, created_at, updated_at, employer_id) FROM stdin;
2	Python разработчик	Требуется опытный Python разработчик для работы над интересными проектами.	ТестКомпания	Москва	100000	150000	RUB	month	full-time	middle	\N	\N	\N	\N	Python, Flask, PostgreSQL	\N	\N	\N	\N	\N	\N	\N	0	t	f	f	f	0	0	\N	2025-07-04 15:57:19.939384	2025-07-04 15:57:19.939386	2025-07-04 15:57:19.939387	3
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: hr_bot_user1
--

COPY public.subscriptions (id, user_id, name, subscription_type, criteria, frequency, notification_time, notification_days, min_salary, max_salary, employment_types, experience_levels, locations, categories, exclude_keywords, company_blacklist, only_remote, only_featured, last_notification_sent, last_job_id_sent, total_notifications_sent, total_jobs_found, is_active, is_paused, max_notifications_per_day, created_at, updated_at, expires_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: hr_bot_user1
--

COPY public.users (id, telegram_id, username, first_name, last_name, email, phone, user_type, company, "position", location, bio, skills, experience_years, education, resume_path, portfolio_url, notification_enabled, language, timezone, is_active, is_verified, last_activity, created_at, updated_at) FROM stdin;
3	123456789	test_employer	Тест	Работодатель	\N	\N	employer	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	ru	Europe/Moscow	t	f	2025-07-04 15:57:19.936587	2025-07-04 15:57:19.936589	2025-07-04 15:57:19.93659
4	987654321	test_candidate	Тест	Соискатель	\N	\N	jobseeker	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	ru	Europe/Moscow	t	f	2025-07-04 15:57:19.938174	2025-07-04 15:57:19.938175	2025-07-04 15:57:19.938176
\.


--
-- Name: applications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: hr_bot_user1
--

SELECT pg_catalog.setval('public.applications_id_seq', 1, false);


--
-- Name: jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: hr_bot_user1
--

SELECT pg_catalog.setval('public.jobs_id_seq', 2, true);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: hr_bot_user1
--

SELECT pg_catalog.setval('public.subscriptions_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: hr_bot_user1
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- Name: applications applications_pkey; Type: CONSTRAINT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_applications_applicant_id; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_applications_applicant_id ON public.applications USING btree (applicant_id);


--
-- Name: idx_applications_created_at; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_applications_created_at ON public.applications USING btree (created_at);


--
-- Name: idx_applications_job_id; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_applications_job_id ON public.applications USING btree (job_id);


--
-- Name: idx_applications_status; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_applications_status ON public.applications USING btree (status);


--
-- Name: idx_jobs_created_at; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_jobs_created_at ON public.jobs USING btree (created_at);


--
-- Name: idx_jobs_employment_type; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_jobs_employment_type ON public.jobs USING btree (employment_type);


--
-- Name: idx_jobs_experience_level; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_jobs_experience_level ON public.jobs USING btree (experience_level);


--
-- Name: idx_jobs_is_active; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_jobs_is_active ON public.jobs USING btree (is_active);


--
-- Name: idx_jobs_location; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_jobs_location ON public.jobs USING btree (location);


--
-- Name: idx_jobs_salary_range; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_jobs_salary_range ON public.jobs USING btree (salary_min, salary_max);


--
-- Name: idx_subscriptions_is_active; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_subscriptions_is_active ON public.subscriptions USING btree (is_active);


--
-- Name: idx_subscriptions_user_id; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_subscriptions_user_id ON public.subscriptions USING btree (user_id);


--
-- Name: idx_users_is_active; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_users_is_active ON public.users USING btree (is_active);


--
-- Name: idx_users_telegram_id; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_users_telegram_id ON public.users USING btree (telegram_id);


--
-- Name: idx_users_user_type; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX idx_users_user_type ON public.users USING btree (user_type);


--
-- Name: ix_applications_applicant_id; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_applications_applicant_id ON public.applications USING btree (applicant_id);


--
-- Name: ix_applications_created_at; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_applications_created_at ON public.applications USING btree (created_at);


--
-- Name: ix_applications_job_id; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_applications_job_id ON public.applications USING btree (job_id);


--
-- Name: ix_applications_status; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_applications_status ON public.applications USING btree (status);


--
-- Name: ix_jobs_category; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_category ON public.jobs USING btree (category);


--
-- Name: ix_jobs_company; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_company ON public.jobs USING btree (company);


--
-- Name: ix_jobs_created_at; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_created_at ON public.jobs USING btree (created_at);


--
-- Name: ix_jobs_employer_id; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_employer_id ON public.jobs USING btree (employer_id);


--
-- Name: ix_jobs_employment_type; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_employment_type ON public.jobs USING btree (employment_type);


--
-- Name: ix_jobs_experience_level; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_experience_level ON public.jobs USING btree (experience_level);


--
-- Name: ix_jobs_expires_at; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_expires_at ON public.jobs USING btree (expires_at);


--
-- Name: ix_jobs_is_active; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_is_active ON public.jobs USING btree (is_active);


--
-- Name: ix_jobs_is_remote; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_is_remote ON public.jobs USING btree (is_remote);


--
-- Name: ix_jobs_location; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_location ON public.jobs USING btree (location);


--
-- Name: ix_jobs_published_at; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_published_at ON public.jobs USING btree (published_at);


--
-- Name: ix_jobs_salary_max; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_salary_max ON public.jobs USING btree (salary_max);


--
-- Name: ix_jobs_salary_min; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_salary_min ON public.jobs USING btree (salary_min);


--
-- Name: ix_jobs_title; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_jobs_title ON public.jobs USING btree (title);


--
-- Name: ix_subscriptions_created_at; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_subscriptions_created_at ON public.subscriptions USING btree (created_at);


--
-- Name: ix_subscriptions_is_active; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_subscriptions_is_active ON public.subscriptions USING btree (is_active);


--
-- Name: ix_subscriptions_subscription_type; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_subscriptions_subscription_type ON public.subscriptions USING btree (subscription_type);


--
-- Name: ix_subscriptions_user_id; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_subscriptions_user_id ON public.subscriptions USING btree (user_id);


--
-- Name: ix_users_created_at; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_users_created_at ON public.users USING btree (created_at);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_is_active; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_users_is_active ON public.users USING btree (is_active);


--
-- Name: ix_users_telegram_id; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE UNIQUE INDEX ix_users_telegram_id ON public.users USING btree (telegram_id);


--
-- Name: ix_users_user_type; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_users_user_type ON public.users USING btree (user_type);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: hr_bot_user1
--

CREATE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: applications applications_applicant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_applicant_id_fkey FOREIGN KEY (applicant_id) REFERENCES public.users(id);


--
-- Name: applications applications_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: jobs jobs_employer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_employer_id_fkey FOREIGN KEY (employer_id) REFERENCES public.users(id);


--
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hr_bot_user1
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

