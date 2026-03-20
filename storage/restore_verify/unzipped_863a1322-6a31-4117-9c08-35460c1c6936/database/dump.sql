--
-- PostgreSQL database dump
--

\restrict Ur7Yy377c6gXTJKBxXmBFzbQDahJXsf297pCACBgKeUON4GaAx2rbzfgB4fdscg

-- Dumped from database version 16.13
-- Dumped by pg_dump version 17.9 (Debian 17.9-0+deb13u1)

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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: app_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.app_settings (
    key character varying(120) NOT NULL,
    value text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_logs (
    actor_user_id character varying(36),
    action character varying(120) NOT NULL,
    target_type character varying(80) NOT NULL,
    target_id character varying(64),
    summary text NOT NULL,
    diff_json text,
    id character varying(36) NOT NULL
);


--
-- Name: backup_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backup_records (
    created_by_user_id character varying(36),
    filename character varying(255) NOT NULL,
    file_path character varying(500) NOT NULL,
    status character varying(30) NOT NULL,
    size_bytes integer DEFAULT 0 NOT NULL,
    notes text,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: booking_lines; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.booking_lines (
    booking_id character varying(36) NOT NULL,
    department_id character varying(36) NOT NULL,
    service_id character varying(36) NOT NULL,
    dress_id character varying(36),
    revenue_journal_entry_id character varying(36),
    line_number integer NOT NULL,
    service_date date NOT NULL,
    suggested_price numeric(12,2) NOT NULL,
    line_price numeric(12,2) NOT NULL,
    status character varying(40) NOT NULL,
    revenue_recognized_at timestamp with time zone,
    notes text,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: bookings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bookings (
    company_id character varying(36) NOT NULL,
    booking_number character varying(40) NOT NULL,
    customer_id character varying(36) NOT NULL,
    service_id character varying(36),
    dress_id character varying(36),
    booking_date date NOT NULL,
    event_date date,
    quoted_price numeric(12,2),
    status character varying(40) NOT NULL,
    notes text,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    branch_id character varying(36) NOT NULL,
    revenue_journal_entry_id character varying(36),
    revenue_recognized_at timestamp with time zone
);


--
-- Name: branches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.branches (
    company_id character varying(36) NOT NULL,
    code character varying(40) NOT NULL,
    name character varying(120) NOT NULL,
    is_default boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: chart_of_accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chart_of_accounts (
    company_id character varying(36) NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(160) NOT NULL,
    account_type character varying(20) NOT NULL,
    parent_account_id character varying(36),
    allows_posting boolean DEFAULT true NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: companies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.companies (
    name character varying(120) NOT NULL,
    legal_name character varying(180),
    default_currency character varying(3) DEFAULT 'EGP'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: customers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customers (
    company_id character varying(36) NOT NULL,
    full_name character varying(160) NOT NULL,
    phone character varying(30) NOT NULL,
    email character varying(160),
    address character varying(255),
    notes text,
    is_active boolean DEFAULT true NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: departments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.departments (
    company_id character varying(36) NOT NULL,
    code character varying(40) NOT NULL,
    name character varying(120) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: document_sequences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.document_sequences (
    company_id character varying(36) NOT NULL,
    key character varying(80) NOT NULL,
    prefix character varying(30) NOT NULL,
    next_number integer DEFAULT 1 NOT NULL,
    padding integer DEFAULT 6 NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: dress_resources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dress_resources (
    company_id character varying(36) NOT NULL,
    code character varying(60) NOT NULL,
    dress_type character varying(80) NOT NULL,
    purchase_date date,
    status character varying(40) NOT NULL,
    description text NOT NULL,
    image_path character varying(255),
    is_active boolean DEFAULT true NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: export_schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.export_schedules (
    company_id character varying(36) NOT NULL,
    branch_id character varying(36),
    name character varying(120) NOT NULL,
    export_type character varying(40) NOT NULL,
    cadence character varying(20) NOT NULL,
    next_run_on date NOT NULL,
    last_run_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: fiscal_periods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fiscal_periods (
    company_id character varying(36) NOT NULL,
    name character varying(120) NOT NULL,
    starts_on date NOT NULL,
    ends_on date NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_locked boolean DEFAULT false NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: journal_entries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.journal_entries (
    company_id character varying(36) NOT NULL,
    fiscal_period_id character varying(36) NOT NULL,
    entry_number character varying(40) NOT NULL,
    entry_date date NOT NULL,
    status character varying(20) DEFAULT 'draft'::character varying NOT NULL,
    reference character varying(120),
    notes text,
    posted_at timestamp with time zone,
    posted_by_user_id character varying(36),
    reversed_at timestamp with time zone,
    reversed_by_user_id character varying(36),
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: journal_entry_lines; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.journal_entry_lines (
    journal_entry_id character varying(36) NOT NULL,
    account_id character varying(36) NOT NULL,
    line_number integer NOT NULL,
    description character varying(255),
    debit_amount numeric(14,2) DEFAULT '0'::numeric NOT NULL,
    credit_amount numeric(14,2) DEFAULT '0'::numeric NOT NULL,
    id character varying(36) NOT NULL,
    CONSTRAINT ck_journal_entry_lines_ck_journal_entry_lines_credit_no_e7c1 CHECK ((credit_amount >= (0)::numeric)),
    CONSTRAINT ck_journal_entry_lines_ck_journal_entry_lines_debit_non_0d6c CHECK ((debit_amount >= (0)::numeric)),
    CONSTRAINT ck_journal_entry_lines_ck_journal_entry_lines_not_zero CHECK ((NOT ((debit_amount = (0)::numeric) AND (credit_amount = (0)::numeric)))),
    CONSTRAINT ck_journal_entry_lines_ck_journal_entry_lines_single_side CHECK ((NOT ((debit_amount > (0)::numeric) AND (credit_amount > (0)::numeric))))
);


--
-- Name: payment_allocations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment_allocations (
    payment_document_id character varying(36) NOT NULL,
    booking_id character varying(36) NOT NULL,
    booking_line_id character varying(36) NOT NULL,
    line_number integer NOT NULL,
    allocated_amount numeric(12,2) NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: payment_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment_documents (
    company_id character varying(36) NOT NULL,
    branch_id character varying(36) NOT NULL,
    customer_id character varying(36) NOT NULL,
    payment_number character varying(40) NOT NULL,
    payment_date date NOT NULL,
    document_kind character varying(20) NOT NULL,
    status character varying(30) NOT NULL,
    journal_entry_id character varying(36),
    voided_at timestamp with time zone,
    voided_by_user_id character varying(36),
    void_reason text,
    notes text,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: payment_receipts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment_receipts (
    company_id character varying(36) NOT NULL,
    payment_number character varying(40) NOT NULL,
    booking_id character varying(36) NOT NULL,
    payment_date date NOT NULL,
    payment_type character varying(40) NOT NULL,
    amount numeric(12,2) NOT NULL,
    remaining_after numeric(12,2) NOT NULL,
    notes text,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    branch_id character varying(36) NOT NULL,
    journal_entry_id character varying(36),
    status character varying(30) NOT NULL,
    voided_at timestamp with time zone,
    voided_by_user_id character varying(36),
    void_reason text
);


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.permissions (
    key character varying(80) NOT NULL,
    description character varying(255),
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.role_permissions (
    role_id character varying(36) NOT NULL,
    permission_id character varying(36) NOT NULL
);


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    name character varying(40) NOT NULL,
    description character varying(255),
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: service_catalog_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.service_catalog_items (
    company_id character varying(36) NOT NULL,
    department_id character varying(36) NOT NULL,
    name character varying(120) NOT NULL,
    default_price numeric(12,2) NOT NULL,
    duration_minutes integer,
    notes text,
    is_active boolean DEFAULT true NOT NULL,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_roles (
    user_id character varying(36) NOT NULL,
    role_id character varying(36) NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    username character varying(60) NOT NULL,
    full_name character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    last_login_at timestamp with time zone,
    id character varying(36) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
20260317_000015
\.


--
-- Data for Name: app_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.app_settings (key, value, created_at, updated_at) FROM stdin;
auth.default_admin_seeded	1	2026-03-14 04:11:52.720884+00	2026-03-14 04:11:52.720884+00
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.audit_logs (actor_user_id, action, target_type, target_id, summary, diff_json, id) FROM stdin;
\N	auth.default_admin_seeded	user	6307835d-b313-404a-a23b-ab033854f2cb	Seeded default admin user admin	\N	098ac5b7-60be-482a-959c-f962b0d17ff1
\N	accounting.foundation_seeded	company	4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Seeded chart of accounts foundation	{"account_codes": ["1000", "1100", "1200", "2100", "3100", "4100", "5100"], "journal_sequence_created": true}	228b41b6-036a-4918-880b-021db6aee064
6307835d-b313-404a-a23b-ab033854f2cb	accounting.journal_draft_created	journal_entry	8e391c2b-adb8-40bb-aec2-85364b946f44	Created draft journal entry JV000001	{"line_count": 2}	97390a4e-6a33-4f16-89b9-f982f0cd096c
6307835d-b313-404a-a23b-ab033854f2cb	accounting.journal_posted	journal_entry	8e391c2b-adb8-40bb-aec2-85364b946f44	Posted journal entry JV000001	\N	83c0ddbf-e94d-43d8-9cc5-c32ee91bba56
6307835d-b313-404a-a23b-ab033854f2cb	accounting.journal_reversed	journal_entry	8e391c2b-adb8-40bb-aec2-85364b946f44	Reversed journal entry JV000001	{"reversal_entry_number": "JV000002"}	4f8e0ead-b92e-4b2a-bdd8-f452946781b3
6307835d-b313-404a-a23b-ab033854f2cb	branch.created	branch	1d285163-6a83-4e15-b89c-ecf3471ac272	Created branch ??? ?????? BR1773624501	{"code": "BR1773624501"}	4963a101-3b33-42a4-b7d4-acec56099713
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	460a28a5-7ea7-4a50-b382-ad358cd7e2e1	Created customer ????? 1773629173	{"phone": "01517736291"}	fba91296-5c94-4c00-a939-03d11c17ed87
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	15549c36-4470-4562-8755-e447e35c6a78	Created department ??? 1773629173	{"code": "DEP1773629173"}	4adec51c-41d4-4219-95d8-375c8ba2023a
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	4b70e297-f7db-46b8-ac49-31cb9ca8deec	Created service ???? 1773629173	{"department_id": "15549c36-4470-4562-8755-e447e35c6a78", "default_price": 1800.0}	3b7d8988-4aa8-42e7-9ff6-adffc4e3bc95
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	89dc7a50-be70-45e3-9640-bb95bd387fb4	Created dress DR1773629173	{"status": "available"}	422e6050-986e-4fae-b4c3-4d9eb8491be2
\N	booking.sequence_seeded	company	4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Seeded booking document sequence	\N	62e2b9f8-3804-46e3-92ef-27636c5629dc
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	cb7e1e39-0ecc-4b12-baa1-7a4a898c3d0a	Created booking BK000001	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "dress_id": "89dc7a50-be70-45e3-9640-bb95bd387fb4"}	b8294cd9-636a-4dee-9db3-7573ab62db50
\N	payment.sequence_seeded	company	4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Seeded payment document sequence	\N	a08b81d6-1dae-400b-b366-cade2d7986c8
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_auto_posted	journal_entry	548dde2a-f7ed-4b86-87ef-544f529d0912	Auto-posted payment PAY000001 to journal JV000003	{"payment_id": "ab646c6d-b70e-4ab8-a686-582c1a2234b0", "payment_type": "deposit", "amount": 1200.0}	c19562de-86ed-4bb8-8e10-dc40f4175be5
6307835d-b313-404a-a23b-ab033854f2cb	payment.created	payment	ab646c6d-b70e-4ab8-a686-582c1a2234b0	Created payment PAY000001	{"payment_type": "deposit", "amount": 1200.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "journal_entry_number": "JV000003"}	9a05089e-e1a0-4407-980f-c551b9a725b6
6307835d-b313-404a-a23b-ab033854f2cb	export.customers_csv_downloaded	export	\N	Downloaded customers export customers_20260316_030256.csv	{"row_count": 2}	570d0e45-2d82-4064-bf1f-aa4cac1f2308
6307835d-b313-404a-a23b-ab033854f2cb	export.bookings_csv_downloaded	export	\N	Downloaded bookings export bookings_main_20260316_030256.csv	{"branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "row_count": 2}	6e24d20c-30c2-480e-9dbb-e0a22a12eee8
6307835d-b313-404a-a23b-ab033854f2cb	export.payments_csv_downloaded	export	\N	Downloaded payments export payments_main_20260316_030256.csv	{"branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "row_count": 1}	31133ab1-b999-4d77-8869-3314e0f93410
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	79d051ec-dca1-4f38-9b11-ce0fa552f885	Created customer ????? ?????? 204059	{"phone": "01077204059"}	968455c0-00dc-4025-b048-b69b59451a27
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	e29df0af-a599-475a-b3ae-869f6aee8090	Created department ??? ?????? 204059	{"code": "REV204059"}	5afde229-ba9d-4f60-86e7-d04348590f7b
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	85b408d0-9ee2-416c-8c56-3825b1eb14d5	Created service ???? ?????? 204059	{"department_id": "e29df0af-a599-475a-b3ae-869f6aee8090", "default_price": 2500.0}	90a8516f-9389-4260-ae90-898f54a265b8
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	80384f11-9127-4c38-abae-1d991b12c7b1	Created booking BK000002	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "dress_id": null}	d1fde044-7337-4eaa-a491-5ac5fefeb4b5
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_auto_posted	journal_entry	36acb4c2-8d63-46c1-8ef2-4abae7112c63	Auto-posted payment PAY000002 to journal JV000004	{"payment_id": "99ae3b83-0d36-448f-bfb0-c310db5cb7c2", "payment_type": "deposit", "amount": 1000.0}	7db1b40b-89d2-414e-bc9e-36a9fb2721b5
6307835d-b313-404a-a23b-ab033854f2cb	payment.created	payment	99ae3b83-0d36-448f-bfb0-c310db5cb7c2	Created payment PAY000002	{"payment_type": "deposit", "amount": 1000.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "journal_entry_number": "JV000004"}	6918cbe5-0768-4764-b1f5-4761cac866cb
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	d10e110e-4042-4875-81aa-b7340d5aa196	Created customer ????? ?????? 204145	{"phone": "01077204145"}	a88b02c7-d037-4cbf-954e-26a816ff2ffb
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	15c625ee-454a-4b87-adcd-6a439a5f9566	Created department ??? ?????? 204145	{"code": "REV204145"}	9724ccd1-6469-40a5-9d35-0ede0f3881e3
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	120b20f9-f68a-4143-b6eb-bd6b241f6900	Created service ???? ?????? 204145	{"department_id": "15c625ee-454a-4b87-adcd-6a439a5f9566", "default_price": 2500.0}	e26ccf62-80d4-42ae-852b-c406daf51407
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	09fdb729-07b3-4454-ac97-a4da673096ca	Created booking BK000003	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "dress_id": null}	c5dc70a3-bf44-4e8f-a1cd-b51e55485682
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_auto_posted	journal_entry	5fef3233-2feb-4437-b745-f8dc8ecc45cd	Auto-posted payment PAY000003 to journal JV000005	{"payment_id": "b5b06b2e-1012-4442-8b4f-b5f3d581aa07", "payment_type": "deposit", "amount": 1000.0}	d24e7c85-3aab-4504-9368-c6065aa3fe7a
6307835d-b313-404a-a23b-ab033854f2cb	payment.created	payment	b5b06b2e-1012-4442-8b4f-b5f3d581aa07	Created payment PAY000003	{"payment_type": "deposit", "amount": 1000.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "journal_entry_number": "JV000005"}	da7b0463-3daa-46de-80fc-1c8a55bd877c
6307835d-b313-404a-a23b-ab033854f2cb	accounting.booking_revenue_recognized	journal_entry	9c202f55-df97-4cfe-b00b-30eb9cfaec8d	Recognized revenue for booking BK000003 in journal JV000006	{"booking_id": "09fdb729-07b3-4454-ac97-a4da673096ca", "quoted_price": 2500.0, "collected_amount": 1000.0, "receivable_amount": 1500.0}	30601ef0-4f4d-422b-aa7d-e17d3a5d347d
6307835d-b313-404a-a23b-ab033854f2cb	booking.completed	booking	09fdb729-07b3-4454-ac97-a4da673096ca	Completed booking BK000003 and recognized revenue	{"journal_entry_number": "JV000006", "quoted_price": 2500.0, "recognized_at": "2026-03-16T18:41:45.586976+00:00"}	a4a05726-9d50-4aa7-bec8-fe132de2d29e
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	c6d38262-d5f9-42d9-a7e9-c4ab6faa3e58	Created customer Customer 1773706106789	{"phone": "01706106789"}	d8fb6aa3-b436-4270-ba5b-69d7a36476ab
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	77138a2b-1407-4cf2-9d06-3b0690dae582	Created department Dress Dept 6789	{"code": "DRESS-106789"}	83a21836-7412-4293-9634-76ef5fae364e
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	b3639f58-1408-49ad-82ea-2f096a52774d	Created service Service 06789	{"department_id": "77138a2b-1407-4cf2-9d06-3b0690dae582", "default_price": 700.0}	5187e64f-7f3c-4779-8052-edc1e0fc8bf7
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	fc013cdf-a908-4a6c-a5cb-34bb0ca1ca12	Created dress DR-106789-1	{"status": "available"}	a7deef6a-4dfd-44b7-ae8e-6e9ab0bd53bf
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	a7b8f6b9-d43a-486c-8243-93406694934b	Created dress DR-106789-2	{"status": "available"}	69b3b9a4-d519-41df-b74a-8b68d7372150
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	a3f96c16-3e33-43da-a0d2-3ae2c98137dc	Created dress DR-106789-3	{"status": "available"}	cae5a31f-20cf-4d69-9829-8bd7fdcd5209
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	689b4cbd-8e3d-44b6-8c88-ca9bbb4d0879	Created customer Customer 1773706358582	{"phone": "01706358582"}	d29abc4c-48ca-4280-864a-bd964bf7e594
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	820bdc06-5317-459f-96b2-eb9d6946e39d	Created department Dress Dept 8582	{"code": "DRESS-358582"}	cce27933-0a81-49e8-95fb-27818005e146
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	2e3c9dc0-c96a-4753-b1b8-04c89d8b37a9	Created service Service 58582	{"department_id": "820bdc06-5317-459f-96b2-eb9d6946e39d", "default_price": 700.0}	e34a7ebd-dac0-411a-9783-0588d5fb02a9
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	f1b2b3b9-601d-45f1-a90a-af512a13a265	Created dress DR-358582-1	{"status": "available"}	eecf0863-0b63-4e79-8209-88b1c8c16b4e
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	ac03c578-dab4-422a-b624-01df1b5f4212	Created dress DR-358582-2	{"status": "available"}	4b3d526b-86f7-40e4-b053-6febdd7e078b
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	ada29466-b3b5-42ec-89cc-668ab4c3b4d8	Created dress DR-358582-3	{"status": "available"}	0752e129-4d57-48b5-8219-f0de2ce48ca7
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	f83a7e7f-8f9d-4b6f-b94a-927b0f31131d	Auto-posted payment document PAY000004 to journal JV000007	{"payment_document_id": "c906f93f-5510-44b8-aee5-9f3c6e055eb0", "total_amount": 250.0, "advances_amount": 250.0, "receivables_amount": 0.0}	7b4c1b4d-dbe4-4f9b-86cb-5594501ead7d
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created_from_booking	payment_document	c906f93f-5510-44b8-aee5-9f3c6e055eb0	Created payment document PAY000004 from booking BK000004	{"booking_id": "373e5fe4-1107-4328-8817-3e01050e7c60", "allocation_count": 2, "total_amount": 250.0}	7396ff91-edd0-47b6-8a26-8fbdf98a61a3
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	373e5fe4-1107-4328-8817-3e01050e7c60	Created booking BK000004	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 2}	e36b31d7-9a2d-4aaa-a67c-79af24b204ea
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	a7fae3d4-83de-4d73-b8f1-5e965f165c3a	Created booking BK000005	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 1}	bdf49b87-e0de-4318-9122-31683a279c33
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	8365d96f-b12d-4763-a7bd-a6df0f606e68	Auto-posted payment document PAY000005 to journal JV000008	{"payment_document_id": "8960e8b6-86a4-4f2a-b8c9-33f199efdfec", "total_amount": 500.0, "advances_amount": 500.0, "receivables_amount": 0.0}	dc754056-d7bd-46e6-a05a-d0fb6649b5a0
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created	payment_document	8960e8b6-86a4-4f2a-b8c9-33f199efdfec	Created payment document PAY000005	{"allocation_count": 2, "total_amount": 500.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322"}	f9241a5e-59bd-454a-812b-d3c41154dcd9
6307835d-b313-404a-a23b-ab033854f2cb	accounting.booking_line_revenue_recognized	journal_entry	146e33da-3a41-43ae-855b-ff0d1735734f	Recognized revenue for booking BK000004 line 1 in journal JV000009	{"booking_id": "373e5fe4-1107-4328-8817-3e01050e7c60", "line_id": "7c6c491f-a1c7-4cdd-97be-31b723468e2a", "line_price": 2500.0, "collected_amount": 300.0, "receivable_amount": 2200.0}	6ce0ef32-de70-4748-9a6d-8cf67f7596bf
6307835d-b313-404a-a23b-ab033854f2cb	booking.line_completed	booking_line	7c6c491f-a1c7-4cdd-97be-31b723468e2a	Completed booking line BK000004 / 1	{"journal_entry_number": "JV000009", "line_price": 2500.0, "recognized_at": "2026-03-17T00:12:40.052848+00:00"}	e18a100e-4d4f-48fa-a62a-038080b90ebd
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	b129410b-4c99-496b-afcb-c3e01c5ed0ab	Created customer Customer 1773706814824	{"phone": "01706814824"}	45a82429-006b-4d10-ac8a-6b072a7a7ce0
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	47c96b72-97d5-403e-945f-dac0b55229e9	Created department Dress Dept 4824	{"code": "DRESS-814824"}	c9ece62b-3644-40fe-9027-a319268f15ce
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	f1c8f9b3-d35c-4aba-8033-a44dbbe31db0	Created service Service 14824	{"department_id": "47c96b72-97d5-403e-945f-dac0b55229e9", "default_price": 700.0}	410f4169-87cd-40ee-8ab7-3eeb3abc07b8
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	6cff60e7-84c5-4072-ae5a-0b4caf4ace39	Created dress DR-814824-1	{"status": "available"}	18b9871d-d721-408c-8264-af9d87d1bd76
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	86676064-f96c-4f1b-ae77-7a8999f712a2	Created dress DR-814824-2	{"status": "available"}	33a9dda9-8199-4916-a0af-e723abf8a6d3
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	2ac7d6b7-7040-4fd6-ae37-3cfe2707baf9	Created dress DR-814824-3	{"status": "available"}	d33073c4-cae0-4d4a-a845-2c2757816d50
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	b94fb361-b1c0-4f4c-bd12-df21755b448c	Auto-posted payment document PAY000006 to journal JV000010	{"payment_document_id": "e3a574da-701f-4786-b108-f4cd84075892", "total_amount": 250.0, "advances_amount": 250.0, "receivables_amount": 0.0}	f271cb30-c1d0-4d19-b8ec-88c17d650951
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created_from_booking	payment_document	e3a574da-701f-4786-b108-f4cd84075892	Created payment document PAY000006 from booking BK000006	{"booking_id": "62fc5598-c3b0-4b85-9c2b-5b5c9fa3178d", "allocation_count": 2, "total_amount": 250.0}	7af929b0-2705-4ce0-b83f-7bb10e67b281
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	62fc5598-c3b0-4b85-9c2b-5b5c9fa3178d	Created booking BK000006	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 2}	fc326b82-ad34-41bc-b039-0e204452bbe1
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	88c7ccee-eaf0-4af0-9b46-631d9003ece0	Created department Dress Dept 2620	{"code": "DRESS-962620"}	7041ff33-2653-4ac0-81a8-d07199596095
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	edbabc2c-2e12-46e6-849b-c5190548315c	Auto-posted payment document PAY000008 to journal JV000013	{"payment_document_id": "3ca7e7b2-b7a9-4d13-a9b8-aaaa0182c7fd", "total_amount": 250.0, "advances_amount": 250.0, "receivables_amount": 0.0}	5c6df6e3-c638-4a25-a00a-5cd2d1efea4d
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created_from_booking	payment_document	3ca7e7b2-b7a9-4d13-a9b8-aaaa0182c7fd	Created payment document PAY000008 from booking BK000008	{"booking_id": "d9c97a83-7b0f-4665-8b13-c077bf053b5a", "allocation_count": 2, "total_amount": 250.0}	805a150b-2bb7-4805-9e0b-61fbe28e554d
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	d9c97a83-7b0f-4665-8b13-c077bf053b5a	Created booking BK000008	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 2}	e421a004-ad61-4461-9c56-f0dc15dcdac0
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	c1fc18e5-a7c1-499f-ae46-f44116fa56d4	Created department Dress Dept 0360	{"code": "DRESS-040360"}	366a599c-58e2-4c72-b88b-1dac9dd920df
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	289b0b29-2dbe-43b1-8fea-67e0333dcc16	Auto-posted payment document PAY000010 to journal JV000016	{"payment_document_id": "bb203f17-3346-4c92-9364-b22468baafc6", "total_amount": 250.0, "advances_amount": 250.0, "receivables_amount": 0.0}	e6f6f144-320f-4b81-91b4-7700f2b99175
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created_from_booking	payment_document	bb203f17-3346-4c92-9364-b22468baafc6	Created payment document PAY000010 from booking BK000010	{"booking_id": "8e2f01f5-dea0-43ab-97ab-775ab374e6cd", "allocation_count": 2, "total_amount": 250.0}	94285959-4177-40e8-8afa-478b9510883c
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	8e2f01f5-dea0-43ab-97ab-775ab374e6cd	Created booking BK000010	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 2}	e7bfc150-75c5-4f21-82a8-6b5e031516be
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	526e6e04-fd5a-42bf-9bdd-a8f0e919c51b	Created department Dress Dept 5589	{"code": "DRESS-645589"}	7b4ce9cb-98fc-42ee-9426-4040c30504bf
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	05cb0064-d7e0-4eeb-a5c5-c3b9157484cf	Created booking BK000013	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 1}	9277b5c6-0f44-4e86-b35d-f446c237c39d
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	4654a8bc-829b-4c34-8b76-4d6adf35a38f	Created booking BK000007	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 1}	e4d4b567-55c6-4904-b298-6ca763da8d96
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	228b8a64-44d0-47f8-ae8d-b72409d7c375	Created dress DR-962620-1	{"status": "available"}	46ebce0f-a09d-40a3-ab52-e9366d22bf4d
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	c7260264-8785-4f3c-abd0-06e573998cf9	Created booking BK000009	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 1}	7190524b-4411-43c6-9a4f-7da504484b98
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	cace4cf6-955e-485e-99f3-0deb5c276db9	Created dress DR-040360-2	{"status": "available"}	f6aafc9f-02e3-445b-8a8f-6dcf781fb444
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	4e2502c8-db11-43d7-9964-dcae237ffd86	Created dress DR-645589-1	{"status": "available"}	1f499704-f7de-4b9c-9e65-885fca48f8a2
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	125fb589-11d3-495d-b784-bb0b96feaf20	Auto-posted payment document PAY000013 to journal JV000020	{"payment_document_id": "11a8759d-8fe3-480c-9189-c26ac40a7de1", "total_amount": 500.0, "advances_amount": 500.0, "receivables_amount": 0.0}	9efb4f91-40fc-4c3a-b252-0b41363f56c3
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created	payment_document	11a8759d-8fe3-480c-9189-c26ac40a7de1	Created payment document PAY000013	{"allocation_count": 2, "total_amount": 500.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322"}	f386015d-c4c9-4768-9007-5ac70e872ac6
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	6b6f3333-4541-4ebd-963a-7a2b4171c868	Auto-posted payment document PAY000007 to journal JV000011	{"payment_document_id": "4e4ab113-0934-4c4f-aecc-31324eae7d87", "total_amount": 500.0, "advances_amount": 500.0, "receivables_amount": 0.0}	7dba8972-d86d-4323-bf05-9466df592a61
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created	payment_document	4e4ab113-0934-4c4f-aecc-31324eae7d87	Created payment document PAY000007	{"allocation_count": 2, "total_amount": 500.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322"}	1d931d88-cacc-4788-b076-720ff1463964
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	b640a678-296d-4066-a213-a69dc7a28848	Created customer Customer 1773706962620	{"phone": "01706962620"}	626b272b-f388-42f2-8d49-0cf194179d16
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	97c294cb-7f62-4356-ab79-53f1a03d7f9b	Created dress DR-962620-3	{"status": "available"}	1b3928af-4516-4375-8aec-a37772683ca3
6307835d-b313-404a-a23b-ab033854f2cb	accounting.booking_line_revenue_recognized	journal_entry	3929e44f-5af8-4727-b1e7-015667262f27	Recognized revenue for booking BK000008 line 1 in journal JV000015	{"booking_id": "d9c97a83-7b0f-4665-8b13-c077bf053b5a", "line_id": "1b84b3a8-c519-4869-b7bf-3e72a61423c6", "line_price": 2500.0, "collected_amount": 300.0, "receivable_amount": 2200.0}	f8336052-c563-48c3-983c-cd0ddc5fb49d
6307835d-b313-404a-a23b-ab033854f2cb	booking.line_completed	booking_line	1b84b3a8-c519-4869-b7bf-3e72a61423c6	Completed booking line BK000008 / 1	{"journal_entry_number": "JV000015", "line_price": 2500.0, "recognized_at": "2026-03-17T00:22:43.510137+00:00"}	ab01fda9-ae24-4b92-b16c-384e0b381a01
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	383e1b0b-f862-482d-83bb-538230c8b06b	Created service Service 40360	{"department_id": "c1fc18e5-a7c1-499f-ae46-f44116fa56d4", "default_price": 700.0}	d42ba874-76bf-4feb-b41d-d9cac3b812c7
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	06059536-188d-4377-ae32-c39134f1a3a3	Auto-posted payment document PAY000011 to journal JV000017	{"payment_document_id": "af5c3d7e-f057-4cfb-9ca0-0c587a8cbf70", "total_amount": 500.0, "advances_amount": 500.0, "receivables_amount": 0.0}	32480c0a-0c5b-41ea-b423-c52b561232ea
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created	payment_document	af5c3d7e-f057-4cfb-9ca0-0c587a8cbf70	Created payment document PAY000011	{"allocation_count": 2, "total_amount": 500.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322"}	3077dd8a-6fd5-4cad-92cb-8fb977d8e72f
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	dedd0d0e-9fb9-4ccc-b185-0f09ee423c06	Created service Service 45589	{"department_id": "526e6e04-fd5a-42bf-9bdd-a8f0e919c51b", "default_price": 700.0}	448e5764-4039-4e11-8cba-3fc8eb7ae1d5
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	c04b1cd3-3fd8-4b1c-9343-e7d011a77399	Auto-posted payment document PAY000012 to journal JV000019	{"payment_document_id": "e31adbec-74ee-42ad-bc49-55ca87c733e8", "total_amount": 250.0, "advances_amount": 250.0, "receivables_amount": 0.0}	ea93e14f-3f99-4ea4-a61b-e3fc46574397
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created_from_booking	payment_document	e31adbec-74ee-42ad-bc49-55ca87c733e8	Created payment document PAY000012 from booking BK000012	{"booking_id": "bf605211-dba4-432c-bb28-d6b8156c6d0e", "allocation_count": 2, "total_amount": 250.0}	7581368c-2b8f-4cca-958d-15234f304840
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	bf605211-dba4-432c-bb28-d6b8156c6d0e	Created booking BK000012	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 2}	454a453f-e01a-444d-8030-4b48f0c5bb86
6307835d-b313-404a-a23b-ab033854f2cb	accounting.booking_line_revenue_recognized	journal_entry	1b4afa61-9ba3-4a84-8b2b-86b943a2dc41	Recognized revenue for booking BK000006 line 1 in journal JV000012	{"booking_id": "62fc5598-c3b0-4b85-9c2b-5b5c9fa3178d", "line_id": "943e99ff-48de-4703-b5ae-a0e99dbd60c2", "line_price": 2500.0, "collected_amount": 300.0, "receivable_amount": 2200.0}	4b2b2072-1b0e-47a8-a042-4e5ee1aead3c
6307835d-b313-404a-a23b-ab033854f2cb	booking.line_completed	booking_line	943e99ff-48de-4703-b5ae-a0e99dbd60c2	Completed booking line BK000006 / 1	{"journal_entry_number": "JV000012", "line_price": 2500.0, "recognized_at": "2026-03-17T00:20:15.869459+00:00"}	cf07f00c-4c36-47d3-a5ee-bf880e04fbac
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	702f2ab2-d969-4fe1-b1eb-74b0fde637f3	Created service Service 62620	{"department_id": "88c7ccee-eaf0-4af0-9b46-631d9003ece0", "default_price": 700.0}	491edc29-50ec-4681-88f0-27a0e31422b4
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	bbe7b863-4b40-4d3a-be7b-bf968b8464b2	Created dress DR-962620-2	{"status": "available"}	2467d2c8-61d1-4942-b72f-83b93420bb1c
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	32defaff-4d2c-4518-b21a-8db3ca6067ba	Auto-posted payment document PAY000009 to journal JV000014	{"payment_document_id": "906e97d5-5c07-457e-abc9-3c7efac43ae9", "total_amount": 500.0, "advances_amount": 500.0, "receivables_amount": 0.0}	1c2ccd52-eab9-4cfc-b959-36fe4509b16d
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created	payment_document	906e97d5-5c07-457e-abc9-3c7efac43ae9	Created payment document PAY000009	{"allocation_count": 2, "total_amount": 500.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322"}	bb151cf6-5f90-4d91-a0cc-dcec808e0712
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	95099d1d-f29f-491a-b82e-a0cc4177a149	Created customer Customer 1773707040360	{"phone": "01707040360"}	262ab7ab-1c7b-4e4f-91ae-ab69eefd255f
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	5250fc3b-26f2-4e3c-bae0-9fb58b517fd0	Created dress DR-040360-1	{"status": "available"}	76d295a0-7600-419d-9ac5-a37dc91d162f
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	2fbf4c69-54bd-49f8-b6f0-1df518240f17	Created dress DR-040360-3	{"status": "available"}	4e9bb414-af70-448b-9f2a-1a9e608d61bf
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	1019bb9d-6fc7-4582-9462-89ce4fe8202a	Created booking BK000011	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 1}	ec3e2cfd-f233-4801-8536-90f1183143aa
6307835d-b313-404a-a23b-ab033854f2cb	accounting.booking_line_revenue_recognized	journal_entry	cadb9018-37a3-4e79-8140-fbfd055c863b	Recognized revenue for booking BK000010 line 1 in journal JV000018	{"booking_id": "8e2f01f5-dea0-43ab-97ab-775ab374e6cd", "line_id": "eade8dce-bfa2-4005-b1f2-31e46c2b3c27", "line_price": 2500.0, "collected_amount": 300.0, "receivable_amount": 2200.0}	09180d0e-d2fe-4450-b5cb-a89a9227fe67
6307835d-b313-404a-a23b-ab033854f2cb	booking.line_completed	booking_line	eade8dce-bfa2-4005-b1f2-31e46c2b3c27	Completed booking line BK000010 / 1	{"journal_entry_number": "JV000018", "line_price": 2500.0, "recognized_at": "2026-03-17T00:24:01.225818+00:00"}	3861b907-c236-46a8-b770-c4c8b490d45d
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	569b0220-d940-4f21-9890-50e05c5bcd7b	Created customer Customer 1773709645589	{"phone": "01709645589"}	956b836b-96a1-429d-bff1-2aef1dfc496e
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	afba0200-537d-4cf2-8bdc-880fa34e811d	Created dress DR-645589-2	{"status": "available"}	3f00227d-3e14-4b4e-9a48-a5505ad7c2d5
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	98cb0afb-136e-48ef-a289-39d1037eee04	Created dress DR-645589-3	{"status": "available"}	c09f4ad9-0e65-40ee-b4bd-ba03abca2e39
6307835d-b313-404a-a23b-ab033854f2cb	accounting.booking_line_revenue_recognized	journal_entry	9be81ea4-ebdf-4540-8030-94fcf8e81330	Recognized revenue for booking BK000012 line 1 in journal JV000021	{"booking_id": "bf605211-dba4-432c-bb28-d6b8156c6d0e", "line_id": "f824c54c-12a6-4cdc-86e6-6e24990ba1f5", "line_price": 2500.0, "collected_amount": 300.0, "receivable_amount": 2200.0}	2f11e31d-2b93-43fb-95dc-88f3c02ac1dc
6307835d-b313-404a-a23b-ab033854f2cb	booking.line_completed	booking_line	f824c54c-12a6-4cdc-86e6-6e24990ba1f5	Completed booking line BK000012 / 1	{"journal_entry_number": "JV000021", "line_price": 2500.0, "recognized_at": "2026-03-17T01:07:27.517144+00:00"}	48f51bfc-d5a1-4226-86e6-34f1d63ae1a7
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	e1990ef4-cba7-4c12-860a-7c0b9a5e771b	Created customer Customer 1773709730441	{"phone": "01709730441"}	560fa7ee-e28c-4d6d-80b7-9f65ff54a8c0
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	9199284d-b0a4-4c80-96ac-77d030300589	Created department Dress Dept 0441	{"code": "DRESS-730441"}	54fcb749-073d-496a-98fb-d4e0eaf78652
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	59938760-badc-42ce-9f51-f07380e0a547	Created service Service 30441	{"department_id": "9199284d-b0a4-4c80-96ac-77d030300589", "default_price": 700.0}	197bd7ad-f515-47e8-80e3-3691ead25b26
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	f325c746-a2f2-4f42-b374-e332b7b731cb	Created dress DR-730441-1	{"status": "available"}	bd8fb990-c171-4498-96f8-f023b24c458a
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	5beb06c2-92b9-45d3-9742-5b187696e1c6	Created dress DR-730441-2	{"status": "available"}	c62b4251-a609-437b-a5f0-725cc571e01e
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	e122737b-0e54-4aaf-9f0b-5fe23495df99	Created dress DR-730441-3	{"status": "available"}	76c9f2d1-8eb8-455f-b618-be995d560639
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	6f9fa24a-2793-4842-b400-9dc05a6e2653	Auto-posted payment document PAY000014 to journal JV000022	{"payment_document_id": "2235082e-7763-4562-bfef-16a5a4f39af3", "total_amount": 250.0, "advances_amount": 250.0, "receivables_amount": 0.0}	a1248155-5c3a-4f58-845b-9843d4742a38
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created_from_booking	payment_document	2235082e-7763-4562-bfef-16a5a4f39af3	Created payment document PAY000014 from booking BK000014	{"booking_id": "d6e795c9-26cf-4b7b-b0f4-7abd95dfd213", "allocation_count": 2, "total_amount": 250.0}	aa527a76-58b3-4029-a9d2-67d4c7300787
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	d6e795c9-26cf-4b7b-b0f4-7abd95dfd213	Created booking BK000014	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 2}	5d5b7ba1-f510-44d1-91dd-2653eae996ce
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	1d6982d3-5ba6-475f-bc4a-536c075ead59	Created booking BK000015	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 1}	d9260b30-cc34-414e-8a97-74e7af37c196
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	87557f7b-4350-4c47-8434-ea9bda30ff22	Created customer Customer 1773709813793	{"phone": "01709813793"}	1305c55e-ee2b-4ae0-a70f-ecfa11528455
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	781465cf-312a-40e9-aa2d-7d406519317f	Auto-posted payment document PAY000015 to journal JV000023	{"payment_document_id": "ba95e7a6-570d-4040-9831-c4de8dbad623", "total_amount": 500.0, "advances_amount": 500.0, "receivables_amount": 0.0}	fc467a54-0837-45d9-ae8c-7c33a865cc66
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created	payment_document	ba95e7a6-570d-4040-9831-c4de8dbad623	Created payment document PAY000015	{"allocation_count": 2, "total_amount": 500.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322"}	307a729d-698d-44a4-be5e-4fe9c303a3df
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	c651f7b2-a8ca-4943-a873-5b49151df1fe	Created dress DR-813793-1	{"status": "available"}	8b4b68f4-2e59-4072-a136-f56b4da7ccf5
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	fa33d012-3afc-4526-9596-86213e690c41	Created booking BK000017	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 1}	a09ebe85-a9e4-443f-a58e-0cd34eff5d08
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	12f9ae70-9c6d-4da7-b3d0-d280db9fffcb	Created dress DR-880588-1	{"status": "available"}	cee998eb-6a43-42fc-83f3-68124a1200b5
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	1870fb02-647b-4078-977f-5b240210f236	Auto-posted payment document PAY000019 to journal JV000029	{"payment_document_id": "d72b1004-173e-4f1a-a2a2-2e1084850975", "total_amount": 500.0, "advances_amount": 500.0, "receivables_amount": 0.0}	f34ac01c-f8fb-44a2-81b6-0b39f8eb6675
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created	payment_document	d72b1004-173e-4f1a-a2a2-2e1084850975	Created payment document PAY000019	{"allocation_count": 2, "total_amount": 500.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322"}	41fea8e2-fe12-4264-92e4-3790417aae22
6307835d-b313-404a-a23b-ab033854f2cb	accounting.booking_line_revenue_recognized	journal_entry	fc16ac63-de51-40cd-b7f8-53da6c108859	Recognized revenue for booking BK000014 line 1 in journal JV000024	{"booking_id": "d6e795c9-26cf-4b7b-b0f4-7abd95dfd213", "line_id": "0df44b2c-be7d-410d-bffe-a3ce3f66e717", "line_price": 2500.0, "collected_amount": 300.0, "receivable_amount": 2200.0}	b95f8a1f-c90c-4940-9b9b-169b4252d8db
6307835d-b313-404a-a23b-ab033854f2cb	booking.line_completed	booking_line	0df44b2c-be7d-410d-bffe-a3ce3f66e717	Completed booking line BK000014 / 1	{"journal_entry_number": "JV000024", "line_price": 2500.0, "recognized_at": "2026-03-17T01:08:51.304311+00:00"}	f408cc9f-a0f0-4abc-8bed-3dc669a31312
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	4ea778d8-e91b-4fa7-b69c-987c6c100639	Created service Service 13793	{"department_id": "acfaf8ef-e8cd-4a33-a89b-9c3d6ece3be2", "default_price": 700.0}	f44bc464-a3ca-4b93-af35-de0b96fbe792
6307835d-b313-404a-a23b-ab033854f2cb	service.created	service	8d4c7a82-3f78-438a-96c7-5ad8ac5af99f	Created service Service 80588	{"department_id": "3e4dbc64-7430-4493-bb76-49bf773fef7f", "default_price": 700.0}	8204d4d4-2f2c-4cfd-b8ff-b8c3d5d73130
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	91e036e4-dd8e-4959-98be-7790c7e72558	Auto-posted payment document PAY000018 to journal JV000028	{"payment_document_id": "a9f6b333-876b-44d4-854f-cbde3c5b1270", "total_amount": 250.0, "advances_amount": 250.0, "receivables_amount": 0.0}	f8546053-7808-42d0-ae8d-5de9f1426748
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created_from_booking	payment_document	a9f6b333-876b-44d4-854f-cbde3c5b1270	Created payment document PAY000018 from booking BK000018	{"booking_id": "b160fe73-c188-4dbc-9bc2-7fb407387d8f", "allocation_count": 2, "total_amount": 250.0}	5e7a6139-5445-4e91-8ec6-301fab819448
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	b160fe73-c188-4dbc-9bc2-7fb407387d8f	Created booking BK000018	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 2}	7665a935-15f0-4e16-97ab-831135cbf862
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	acfaf8ef-e8cd-4a33-a89b-9c3d6ece3be2	Created department Dress Dept 3793	{"code": "DRESS-813793"}	9355e8b3-ff74-4348-9154-4a4a352b58d3
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	adea8eb6-431c-421c-a1de-d79dfdf9e392	Auto-posted payment document PAY000016 to journal JV000025	{"payment_document_id": "d3e92c90-7a9c-44c1-a035-07e195d0dbe1", "total_amount": 250.0, "advances_amount": 250.0, "receivables_amount": 0.0}	87c0ab24-e1e2-41ef-8607-55e930d38af6
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created_from_booking	payment_document	d3e92c90-7a9c-44c1-a035-07e195d0dbe1	Created payment document PAY000016 from booking BK000016	{"booking_id": "d36a3991-7078-4471-a1f5-8b21b0ea713e", "allocation_count": 2, "total_amount": 250.0}	7b505ea5-0956-43e0-8e6e-f89c23c645f4
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	d36a3991-7078-4471-a1f5-8b21b0ea713e	Created booking BK000016	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 2}	e29fe9e2-dd10-457b-862b-c85d318411fb
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	3dd42f89-2194-4c0a-91eb-10a20c19fbfb	Created dress DR-813793-2	{"status": "available"}	9793a57d-a994-4686-a160-11933854d581
6307835d-b313-404a-a23b-ab033854f2cb	accounting.payment_document_auto_posted	journal_entry	3724ce70-9815-4497-927c-bdf5e750d596	Auto-posted payment document PAY000017 to journal JV000026	{"payment_document_id": "12f9bc55-3693-421c-8874-b6abafc4f180", "total_amount": 500.0, "advances_amount": 500.0, "receivables_amount": 0.0}	767c3227-2ee0-4507-b677-182a604fd43a
6307835d-b313-404a-a23b-ab033854f2cb	payment_document.created	payment_document	12f9bc55-3693-421c-8874-b6abafc4f180	Created payment document PAY000017	{"allocation_count": 2, "total_amount": 500.0, "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322"}	a7c6ac8e-96e3-4134-add1-65df2280d1a4
6307835d-b313-404a-a23b-ab033854f2cb	booking.created	booking	e26dafd1-e398-4f96-83e2-c3f5fc98fbfc	Created booking BK000019	{"status": "confirmed", "branch_id": "df7fc2ef-5359-4aeb-9183-aa1c37dda322", "line_count": 1}	a25c2599-e9b2-4ad0-b823-15a7e634bd4c
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	ad309071-0cf3-4e26-9cc4-f07ef07c710c	Created dress DR-813793-3	{"status": "available"}	448ed899-4703-4b5f-9f44-708c579641a5
6307835d-b313-404a-a23b-ab033854f2cb	accounting.booking_line_revenue_recognized	journal_entry	76e03013-b2ee-4d86-be41-1f2ecb0b3d74	Recognized revenue for booking BK000016 line 1 in journal JV000027	{"booking_id": "d36a3991-7078-4471-a1f5-8b21b0ea713e", "line_id": "7b91de29-d683-4753-a0b3-9662aa3e8395", "line_price": 2500.0, "collected_amount": 300.0, "receivable_amount": 2200.0}	f501e490-c874-4013-a48a-64dc3de205a3
6307835d-b313-404a-a23b-ab033854f2cb	booking.line_completed	booking_line	7b91de29-d683-4753-a0b3-9662aa3e8395	Completed booking line BK000016 / 1	{"journal_entry_number": "JV000027", "line_price": 2500.0, "recognized_at": "2026-03-17T01:10:14.789120+00:00"}	e298300b-bea0-419b-9b36-41df13ab16e8
6307835d-b313-404a-a23b-ab033854f2cb	customer.created	customer	975312e9-5b60-40ce-ae21-cf4ed1342061	Created customer Customer 1773709880588	{"phone": "01709880588"}	bc8bd5f9-d941-4326-ab46-547b0f9a4f28
6307835d-b313-404a-a23b-ab033854f2cb	department.created	department	3e4dbc64-7430-4493-bb76-49bf773fef7f	Created department Dress Dept 0588	{"code": "DRESS-880588"}	f4a7894f-62d5-4d91-9f10-8bb9f7361124
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	46dfbbbc-39a1-4315-afc7-4bc9c8dbba66	Created dress DR-880588-2	{"status": "available"}	67b1b841-5281-475b-bca5-cdc3b5fbe49d
6307835d-b313-404a-a23b-ab033854f2cb	dress.created	dress	f410e21b-65a8-4ef6-b6e2-cedef4de4132	Created dress DR-880588-3	{"status": "available"}	ded0891d-3a5a-4138-82fb-c436e65d4fb6
6307835d-b313-404a-a23b-ab033854f2cb	accounting.booking_line_revenue_recognized	journal_entry	317c2eb1-c67b-43df-a608-ae96046dc72e	Recognized revenue for booking BK000018 line 1 in journal JV000030	{"booking_id": "b160fe73-c188-4dbc-9bc2-7fb407387d8f", "line_id": "17f7e2f9-92a9-426e-9586-7599a193a77c", "line_price": 2500.0, "collected_amount": 300.0, "receivable_amount": 2200.0}	e7e2b4ad-84ac-47fa-a413-c10c59500c5d
6307835d-b313-404a-a23b-ab033854f2cb	booking.line_completed	booking_line	17f7e2f9-92a9-426e-9586-7599a193a77c	Completed booking line BK000018 / 1	{"journal_entry_number": "JV000030", "line_price": 2500.0, "recognized_at": "2026-03-17T01:11:21.651517+00:00"}	a30d1dd6-79ba-42e8-be6f-82dee35a1dc4
6307835d-b313-404a-a23b-ab033854f2cb	backup.created	backup_record	\N	Created backup backup_20260317_021138.zip	\N	25def4d5-9a1c-41d5-8d65-a92c63016141
6307835d-b313-404a-a23b-ab033854f2cb	backup.downloaded	backup_record	0866e393-7fc9-4505-9aea-4fd4112ab2bd	Downloaded backup backup_20260317_021138.zip	\N	01f8aca1-2d03-4657-88d5-c10c8777c1b7
6307835d-b313-404a-a23b-ab033854f2cb	backup.created	backup_record	\N	Created backup backup_20260317_021807.zip	\N	f5121a54-d3fe-43ac-bb40-9e2ee381e7fb
6307835d-b313-404a-a23b-ab033854f2cb	backup.downloaded	backup_record	058bb18f-003e-47c3-b52f-0171f80362fa	Downloaded backup backup_20260317_021807.zip	\N	06d45f84-6238-40c9-b059-478dfb3dcc1e
\.


--
-- Data for Name: backup_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backup_records (created_by_user_id, filename, file_path, status, size_bytes, notes, id, created_at, updated_at) FROM stdin;
6307835d-b313-404a-a23b-ab033854f2cb	backup_20260317_021138.zip	/app/storage/backups/backup_20260317_021138.zip	created	30073	Generated from settings backup panel	0866e393-7fc9-4505-9aea-4fd4112ab2bd	2026-03-17 02:11:38.558668+00	2026-03-17 02:11:38.558668+00
6307835d-b313-404a-a23b-ab033854f2cb	backup_20260317_021807.zip	/app/storage/backups/backup_20260317_021807.zip	created	30270	Generated from settings backup panel	058bb18f-003e-47c3-b52f-0171f80362fa	2026-03-17 02:18:07.139804+00	2026-03-17 02:18:07.139804+00
\.


--
-- Data for Name: booking_lines; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.booking_lines (booking_id, department_id, service_id, dress_id, revenue_journal_entry_id, line_number, service_date, suggested_price, line_price, status, revenue_recognized_at, notes, id, created_at, updated_at) FROM stdin;
24ebfd42-cced-470e-b09c-86697da4c205	e572c53b-86eb-44cd-8281-edb93c9e4530	26785f9f-204b-462e-a5e2-05d1348c5915	1c19ee33-8315-4dc1-85b4-d4c1eb4ef4f4	\N	1	2026-07-20	1800.00	3000.00	confirmed	\N	\N	6ff26eea-8f7f-4f6a-9f84-bff8a7225b5d	2026-03-16 02:43:58.882473+00	2026-03-16 02:43:58.882473+00
cb7e1e39-0ecc-4b12-baa1-7a4a898c3d0a	15549c36-4470-4562-8755-e447e35c6a78	4b70e297-f7db-46b8-ac49-31cb9ca8deec	89dc7a50-be70-45e3-9640-bb95bd387fb4	\N	1	2026-07-15	1800.00	3000.00	confirmed	\N	\N	4ec5b55c-4e39-4717-9d40-cb0f03148518	2026-03-16 02:46:14.158742+00	2026-03-16 02:46:14.158742+00
80384f11-9127-4c38-abae-1d991b12c7b1	e29df0af-a599-475a-b3ae-869f6aee8090	85b408d0-9ee2-416c-8c56-3825b1eb14d5	\N	\N	1	2026-12-01	2500.00	2500.00	confirmed	\N	\N	d6841418-8f29-49b9-815a-bfd76dcc1d08	2026-03-16 18:40:59.557272+00	2026-03-16 18:40:59.557272+00
09fdb729-07b3-4454-ac97-a4da673096ca	15c625ee-454a-4b87-adcd-6a439a5f9566	120b20f9-f68a-4143-b6eb-bd6b241f6900	\N	9c202f55-df97-4cfe-b00b-30eb9cfaec8d	1	2026-12-01	2500.00	2500.00	completed	2026-03-16 18:41:45.586976+00	\N	8b79e88b-dbf5-4f08-b245-025ebfa1ade3	2026-03-16 18:41:45.246333+00	2026-03-16 18:41:45.532709+00
373e5fe4-1107-4328-8817-3e01050e7c60	820bdc06-5317-459f-96b2-eb9d6946e39d	2e3c9dc0-c96a-4753-b1b8-04c89d8b37a9	ac03c578-dab4-422a-b624-01df1b5f4212	\N	2	2026-08-11	700.00	3000.00	confirmed	\N	\N	10cf35d4-9e86-4948-8c24-42cce7da259c	2026-03-17 00:12:39.148139+00	2026-03-17 00:12:39.148139+00
a7fae3d4-83de-4d73-b8f1-5e965f165c3a	820bdc06-5317-459f-96b2-eb9d6946e39d	2e3c9dc0-c96a-4753-b1b8-04c89d8b37a9	ada29466-b3b5-42ec-89cc-668ab4c3b4d8	\N	1	2026-08-12	700.00	1800.00	confirmed	\N	\N	51ee1db9-9440-4392-b7fc-c6b2dbd97758	2026-03-17 00:12:39.549989+00	2026-03-17 00:12:39.549989+00
373e5fe4-1107-4328-8817-3e01050e7c60	820bdc06-5317-459f-96b2-eb9d6946e39d	2e3c9dc0-c96a-4753-b1b8-04c89d8b37a9	f1b2b3b9-601d-45f1-a90a-af512a13a265	146e33da-3a41-43ae-855b-ff0d1735734f	1	2026-08-10	700.00	2500.00	completed	2026-03-17 00:12:40.052848+00	\N	7c6c491f-a1c7-4cdd-97be-31b723468e2a	2026-03-17 00:12:39.148139+00	2026-03-17 00:12:39.920606+00
62fc5598-c3b0-4b85-9c2b-5b5c9fa3178d	47c96b72-97d5-403e-945f-dac0b55229e9	f1c8f9b3-d35c-4aba-8033-a44dbbe31db0	86676064-f96c-4f1b-ae77-7a8999f712a2	\N	2	2026-08-11	700.00	3000.00	confirmed	\N	\N	9a65956f-6fdb-4f9e-8e53-a8f324ba8127	2026-03-17 00:20:15.230029+00	2026-03-17 00:20:15.230029+00
4654a8bc-829b-4c34-8b76-4d6adf35a38f	47c96b72-97d5-403e-945f-dac0b55229e9	f1c8f9b3-d35c-4aba-8033-a44dbbe31db0	2ac7d6b7-7040-4fd6-ae37-3cfe2707baf9	\N	1	2026-08-12	700.00	1800.00	confirmed	\N	\N	75a899ce-8072-4408-bf49-f075d0e81f5c	2026-03-17 00:20:15.571582+00	2026-03-17 00:20:15.571582+00
62fc5598-c3b0-4b85-9c2b-5b5c9fa3178d	47c96b72-97d5-403e-945f-dac0b55229e9	f1c8f9b3-d35c-4aba-8033-a44dbbe31db0	6cff60e7-84c5-4072-ae5a-0b4caf4ace39	1b4afa61-9ba3-4a84-8b2b-86b943a2dc41	1	2026-08-10	700.00	2500.00	completed	2026-03-17 00:20:15.869459+00	\N	943e99ff-48de-4703-b5ae-a0e99dbd60c2	2026-03-17 00:20:15.230029+00	2026-03-17 00:20:15.820115+00
d9c97a83-7b0f-4665-8b13-c077bf053b5a	88c7ccee-eaf0-4af0-9b46-631d9003ece0	702f2ab2-d969-4fe1-b1eb-74b0fde637f3	bbe7b863-4b40-4d3a-be7b-bf968b8464b2	\N	2	2026-08-11	700.00	3000.00	confirmed	\N	\N	2dfb0bc3-ec28-4200-be0a-f2de6d0b98c8	2026-03-17 00:22:43.010078+00	2026-03-17 00:22:43.010078+00
c7260264-8785-4f3c-abd0-06e573998cf9	88c7ccee-eaf0-4af0-9b46-631d9003ece0	702f2ab2-d969-4fe1-b1eb-74b0fde637f3	97c294cb-7f62-4356-ab79-53f1a03d7f9b	\N	1	2026-08-12	700.00	1800.00	confirmed	\N	\N	6a7a0ea8-5761-4ff4-b9b1-18fbfde32dc3	2026-03-17 00:22:43.232795+00	2026-03-17 00:22:43.232795+00
d9c97a83-7b0f-4665-8b13-c077bf053b5a	88c7ccee-eaf0-4af0-9b46-631d9003ece0	702f2ab2-d969-4fe1-b1eb-74b0fde637f3	228b8a64-44d0-47f8-ae8d-b72409d7c375	3929e44f-5af8-4727-b1e7-015667262f27	1	2026-08-10	700.00	2500.00	completed	2026-03-17 00:22:43.510137+00	\N	1b84b3a8-c519-4869-b7bf-3e72a61423c6	2026-03-17 00:22:43.010078+00	2026-03-17 00:22:43.460353+00
8e2f01f5-dea0-43ab-97ab-775ab374e6cd	c1fc18e5-a7c1-499f-ae46-f44116fa56d4	383e1b0b-f862-482d-83bb-538230c8b06b	cace4cf6-955e-485e-99f3-0deb5c276db9	\N	2	2026-08-11	700.00	3000.00	confirmed	\N	\N	eed631b5-d3b4-4c06-93a2-450ffb61b5a2	2026-03-17 00:24:00.775978+00	2026-03-17 00:24:00.775978+00
1019bb9d-6fc7-4582-9462-89ce4fe8202a	c1fc18e5-a7c1-499f-ae46-f44116fa56d4	383e1b0b-f862-482d-83bb-538230c8b06b	2fbf4c69-54bd-49f8-b6f0-1df518240f17	\N	1	2026-08-12	700.00	1800.00	confirmed	\N	\N	67059ea2-383b-4af2-b548-3f6347b43980	2026-03-17 00:24:00.968482+00	2026-03-17 00:24:00.968482+00
8e2f01f5-dea0-43ab-97ab-775ab374e6cd	c1fc18e5-a7c1-499f-ae46-f44116fa56d4	383e1b0b-f862-482d-83bb-538230c8b06b	5250fc3b-26f2-4e3c-bae0-9fb58b517fd0	cadb9018-37a3-4e79-8140-fbfd055c863b	1	2026-08-10	700.00	2500.00	completed	2026-03-17 00:24:01.225818+00	\N	eade8dce-bfa2-4005-b1f2-31e46c2b3c27	2026-03-17 00:24:00.775978+00	2026-03-17 00:24:01.170291+00
bf605211-dba4-432c-bb28-d6b8156c6d0e	526e6e04-fd5a-42bf-9bdd-a8f0e919c51b	dedd0d0e-9fb9-4ccc-b185-0f09ee423c06	afba0200-537d-4cf2-8bdc-880fa34e811d	\N	2	2026-08-11	700.00	3000.00	confirmed	\N	\N	7612320d-f0dd-4507-b167-4fe5095081f9	2026-03-17 01:07:26.98646+00	2026-03-17 01:07:26.98646+00
05cb0064-d7e0-4eeb-a5c5-c3b9157484cf	526e6e04-fd5a-42bf-9bdd-a8f0e919c51b	dedd0d0e-9fb9-4ccc-b185-0f09ee423c06	98cb0afb-136e-48ef-a289-39d1037eee04	\N	1	2026-08-12	700.00	1800.00	confirmed	\N	\N	60346925-6764-4a86-a398-5b6177112f9c	2026-03-17 01:07:27.242707+00	2026-03-17 01:07:27.242707+00
bf605211-dba4-432c-bb28-d6b8156c6d0e	526e6e04-fd5a-42bf-9bdd-a8f0e919c51b	dedd0d0e-9fb9-4ccc-b185-0f09ee423c06	4e2502c8-db11-43d7-9964-dcae237ffd86	9be81ea4-ebdf-4540-8030-94fcf8e81330	1	2026-08-10	700.00	2500.00	completed	2026-03-17 01:07:27.517144+00	\N	f824c54c-12a6-4cdc-86e6-6e24990ba1f5	2026-03-17 01:07:26.98646+00	2026-03-17 01:07:27.469059+00
d6e795c9-26cf-4b7b-b0f4-7abd95dfd213	9199284d-b0a4-4c80-96ac-77d030300589	59938760-badc-42ce-9f51-f07380e0a547	5beb06c2-92b9-45d3-9742-5b187696e1c6	\N	2	2026-08-11	700.00	3000.00	confirmed	\N	\N	15e4c5f6-8d82-47ad-a1f1-e8d3fdc37846	2026-03-17 01:08:50.820724+00	2026-03-17 01:08:50.820724+00
1d6982d3-5ba6-475f-bc4a-536c075ead59	9199284d-b0a4-4c80-96ac-77d030300589	59938760-badc-42ce-9f51-f07380e0a547	e122737b-0e54-4aaf-9f0b-5fe23495df99	\N	1	2026-08-12	700.00	1800.00	confirmed	\N	\N	c7d283a7-6ab6-4dd5-9576-26efc871cee6	2026-03-17 01:08:50.966546+00	2026-03-17 01:08:50.966546+00
d6e795c9-26cf-4b7b-b0f4-7abd95dfd213	9199284d-b0a4-4c80-96ac-77d030300589	59938760-badc-42ce-9f51-f07380e0a547	f325c746-a2f2-4f42-b374-e332b7b731cb	fc16ac63-de51-40cd-b7f8-53da6c108859	1	2026-08-10	700.00	2500.00	completed	2026-03-17 01:08:51.304311+00	\N	0df44b2c-be7d-410d-bffe-a3ce3f66e717	2026-03-17 01:08:50.820724+00	2026-03-17 01:08:51.240812+00
d36a3991-7078-4471-a1f5-8b21b0ea713e	acfaf8ef-e8cd-4a33-a89b-9c3d6ece3be2	4ea778d8-e91b-4fa7-b69c-987c6c100639	3dd42f89-2194-4c0a-91eb-10a20c19fbfb	\N	2	2026-08-11	700.00	3000.00	confirmed	\N	\N	5b2396d0-11c3-4343-b335-b96497553081	2026-03-17 01:10:14.228646+00	2026-03-17 01:10:14.228646+00
fa33d012-3afc-4526-9596-86213e690c41	acfaf8ef-e8cd-4a33-a89b-9c3d6ece3be2	4ea778d8-e91b-4fa7-b69c-987c6c100639	ad309071-0cf3-4e26-9cc4-f07ef07c710c	\N	1	2026-08-12	700.00	1800.00	confirmed	\N	\N	5328aab3-4b7e-4606-9d5c-901456d533c4	2026-03-17 01:10:14.363956+00	2026-03-17 01:10:14.363956+00
d36a3991-7078-4471-a1f5-8b21b0ea713e	acfaf8ef-e8cd-4a33-a89b-9c3d6ece3be2	4ea778d8-e91b-4fa7-b69c-987c6c100639	c651f7b2-a8ca-4943-a873-5b49151df1fe	76e03013-b2ee-4d86-be41-1f2ecb0b3d74	1	2026-08-10	700.00	2500.00	completed	2026-03-17 01:10:14.78912+00	\N	7b91de29-d683-4753-a0b3-9662aa3e8395	2026-03-17 01:10:14.228646+00	2026-03-17 01:10:14.738563+00
b160fe73-c188-4dbc-9bc2-7fb407387d8f	3e4dbc64-7430-4493-bb76-49bf773fef7f	8d4c7a82-3f78-438a-96c7-5ad8ac5af99f	46dfbbbc-39a1-4315-afc7-4bc9c8dbba66	\N	2	2026-08-11	700.00	3000.00	confirmed	\N	\N	c0518a66-b159-4c66-848d-4b17c00eea53	2026-03-17 01:11:21.128803+00	2026-03-17 01:11:21.128803+00
e26dafd1-e398-4f96-83e2-c3f5fc98fbfc	3e4dbc64-7430-4493-bb76-49bf773fef7f	8d4c7a82-3f78-438a-96c7-5ad8ac5af99f	f410e21b-65a8-4ef6-b6e2-cedef4de4132	\N	1	2026-08-12	700.00	1800.00	confirmed	\N	\N	64e74dd2-57f9-4e39-aedb-1cfe0793d3d2	2026-03-17 01:11:21.345525+00	2026-03-17 01:11:21.345525+00
b160fe73-c188-4dbc-9bc2-7fb407387d8f	3e4dbc64-7430-4493-bb76-49bf773fef7f	8d4c7a82-3f78-438a-96c7-5ad8ac5af99f	12f9ae70-9c6d-4da7-b3d0-d280db9fffcb	317c2eb1-c67b-43df-a608-ae96046dc72e	1	2026-08-10	700.00	2500.00	completed	2026-03-17 01:11:21.651517+00	\N	17f7e2f9-92a9-426e-9586-7599a193a77c	2026-03-17 01:11:21.128803+00	2026-03-17 01:11:21.595212+00
\.


--
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bookings (company_id, booking_number, customer_id, service_id, dress_id, booking_date, event_date, quoted_price, status, notes, id, created_at, updated_at, branch_id, revenue_journal_entry_id, revenue_recognized_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	LIVE-1773629038	cc444c7a-e21b-40c9-b6f8-2dd1cd960d75	26785f9f-204b-462e-a5e2-05d1348c5915	1c19ee33-8315-4dc1-85b4-d4c1eb4ef4f4	2026-03-16	2026-07-20	3000.00	confirmed	Seeded live verification booking	24ebfd42-cced-470e-b09c-86697da4c205	2026-03-16 02:43:58.882473+00	2026-03-16 02:43:58.882473+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000001	460a28a5-7ea7-4a50-b382-ad358cd7e2e1	4b70e297-f7db-46b8-ac49-31cb9ca8deec	89dc7a50-be70-45e3-9640-bb95bd387fb4	2026-03-16	2026-07-15	3000.00	confirmed	??? ???? ??	cb7e1e39-0ecc-4b12-baa1-7a4a898c3d0a	2026-03-16 02:46:14.158742+00	2026-03-16 02:46:14.158742+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000002	79d051ec-dca1-4f38-9b11-ce0fa552f885	85b408d0-9ee2-416c-8c56-3825b1eb14d5	\N	2026-03-16	2026-12-01	2500.00	confirmed	\N	80384f11-9127-4c38-abae-1d991b12c7b1	2026-03-16 18:40:59.557272+00	2026-03-16 18:40:59.557272+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000003	d10e110e-4042-4875-81aa-b7340d5aa196	120b20f9-f68a-4143-b6eb-bd6b241f6900	\N	2026-03-16	2026-12-01	2500.00	completed	\N	09fdb729-07b3-4454-ac97-a4da673096ca	2026-03-16 18:41:45.246333+00	2026-03-16 18:41:45.532709+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	9c202f55-df97-4cfe-b00b-30eb9cfaec8d	2026-03-16 18:41:45.586976+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000005	689b4cbd-8e3d-44b6-8c88-ca9bbb4d0879	\N	\N	2026-03-17	\N	\N	confirmed	Playwright smoke booking two	a7fae3d4-83de-4d73-b8f1-5e965f165c3a	2026-03-17 00:12:39.549989+00	2026-03-17 00:12:39.549989+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000004	689b4cbd-8e3d-44b6-8c88-ca9bbb4d0879	\N	\N	2026-03-17	\N	\N	partially_completed	Playwright smoke booking one	373e5fe4-1107-4328-8817-3e01050e7c60	2026-03-17 00:12:39.148139+00	2026-03-17 00:12:39.920606+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000007	b129410b-4c99-496b-afcb-c3e01c5ed0ab	\N	\N	2026-03-17	\N	\N	confirmed	Playwright smoke booking two	4654a8bc-829b-4c34-8b76-4d6adf35a38f	2026-03-17 00:20:15.571582+00	2026-03-17 00:20:15.571582+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000006	b129410b-4c99-496b-afcb-c3e01c5ed0ab	\N	\N	2026-03-17	\N	\N	partially_completed	Playwright smoke booking one	62fc5598-c3b0-4b85-9c2b-5b5c9fa3178d	2026-03-17 00:20:15.230029+00	2026-03-17 00:20:15.820115+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000009	b640a678-296d-4066-a213-a69dc7a28848	\N	\N	2026-03-17	\N	\N	confirmed	Playwright smoke booking two	c7260264-8785-4f3c-abd0-06e573998cf9	2026-03-17 00:22:43.232795+00	2026-03-17 00:22:43.232795+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000008	b640a678-296d-4066-a213-a69dc7a28848	\N	\N	2026-03-17	\N	\N	partially_completed	Playwright smoke booking one	d9c97a83-7b0f-4665-8b13-c077bf053b5a	2026-03-17 00:22:43.010078+00	2026-03-17 00:22:43.460353+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000011	95099d1d-f29f-491a-b82e-a0cc4177a149	\N	\N	2026-03-17	\N	\N	confirmed	Playwright smoke booking two	1019bb9d-6fc7-4582-9462-89ce4fe8202a	2026-03-17 00:24:00.968482+00	2026-03-17 00:24:00.968482+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000010	95099d1d-f29f-491a-b82e-a0cc4177a149	\N	\N	2026-03-17	\N	\N	partially_completed	Playwright smoke booking one	8e2f01f5-dea0-43ab-97ab-775ab374e6cd	2026-03-17 00:24:00.775978+00	2026-03-17 00:24:01.170291+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000013	569b0220-d940-4f21-9890-50e05c5bcd7b	\N	\N	2026-03-17	\N	\N	confirmed	Playwright smoke booking two	05cb0064-d7e0-4eeb-a5c5-c3b9157484cf	2026-03-17 01:07:27.242707+00	2026-03-17 01:07:27.242707+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000012	569b0220-d940-4f21-9890-50e05c5bcd7b	\N	\N	2026-03-17	\N	\N	partially_completed	Playwright smoke booking one	bf605211-dba4-432c-bb28-d6b8156c6d0e	2026-03-17 01:07:26.98646+00	2026-03-17 01:07:27.469059+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000015	e1990ef4-cba7-4c12-860a-7c0b9a5e771b	\N	\N	2026-03-17	\N	\N	confirmed	Playwright smoke booking two	1d6982d3-5ba6-475f-bc4a-536c075ead59	2026-03-17 01:08:50.966546+00	2026-03-17 01:08:50.966546+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000014	e1990ef4-cba7-4c12-860a-7c0b9a5e771b	\N	\N	2026-03-17	\N	\N	partially_completed	Playwright smoke booking one	d6e795c9-26cf-4b7b-b0f4-7abd95dfd213	2026-03-17 01:08:50.820724+00	2026-03-17 01:08:51.240812+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000017	87557f7b-4350-4c47-8434-ea9bda30ff22	\N	\N	2026-03-17	\N	\N	confirmed	Playwright smoke booking two	fa33d012-3afc-4526-9596-86213e690c41	2026-03-17 01:10:14.363956+00	2026-03-17 01:10:14.363956+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000016	87557f7b-4350-4c47-8434-ea9bda30ff22	\N	\N	2026-03-17	\N	\N	partially_completed	Playwright smoke booking one	d36a3991-7078-4471-a1f5-8b21b0ea713e	2026-03-17 01:10:14.228646+00	2026-03-17 01:10:14.738563+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000019	975312e9-5b60-40ce-ae21-cf4ed1342061	\N	\N	2026-03-17	\N	\N	confirmed	Playwright smoke booking two	e26dafd1-e398-4f96-83e2-c3f5fc98fbfc	2026-03-17 01:11:21.345525+00	2026-03-17 01:11:21.345525+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BK000018	975312e9-5b60-40ce-ae21-cf4ed1342061	\N	\N	2026-03-17	\N	\N	partially_completed	Playwright smoke booking one	b160fe73-c188-4dbc-9bc2-7fb407387d8f	2026-03-17 01:11:21.128803+00	2026-03-17 01:11:21.595212+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	\N	\N
\.


--
-- Data for Name: branches; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.branches (company_id, code, name, is_default, is_active, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	MAIN	Main Branch	t	t	df7fc2ef-5359-4aeb-9183-aa1c37dda322	2026-03-14 04:11:52.698524+00	2026-03-14 04:11:52.698524+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	BR1773624501	??? ?????? BR1773624501	f	t	1d285163-6a83-4e15-b89c-ecf3471ac272	2026-03-16 01:28:27.110461+00	2026-03-16 01:28:27.110461+00
\.


--
-- Data for Name: chart_of_accounts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chart_of_accounts (company_id, code, name, account_type, parent_account_id, allows_posting, is_active, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	1000	الصندوق	asset	\N	t	t	756f5f60-b7b9-48d6-baf8-4b7cdc451048	2026-03-15 21:30:30.32481+00	2026-03-15 21:30:30.32481+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	1100	البنك	asset	\N	t	t	7ff2d681-9340-488a-ab0e-8c59ddc6a57b	2026-03-15 21:30:30.32481+00	2026-03-15 21:30:30.32481+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	1200	ذمم العملاء	asset	\N	t	t	b2a1d538-6540-467f-91ed-f709e29c76d7	2026-03-15 21:30:30.32481+00	2026-03-15 21:30:30.32481+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	2100	عربون العملاء	liability	\N	t	t	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2026-03-15 21:30:30.32481+00	2026-03-15 21:30:30.32481+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	3100	حقوق الملكية	equity	\N	t	t	b52a7827-5a97-419d-bed0-9a8c18adc86f	2026-03-15 21:30:30.32481+00	2026-03-15 21:30:30.32481+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	4100	إيرادات الخدمات	revenue	\N	t	t	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	2026-03-15 21:30:30.32481+00	2026-03-15 21:30:30.32481+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	5100	مصروفات تشغيلية	expense	\N	t	t	e38dfbbe-d31b-48ee-b5d9-3add4d7d5ce7	2026-03-15 21:30:30.32481+00	2026-03-15 21:30:30.32481+00
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.companies (name, legal_name, default_currency, is_active, id, created_at, updated_at) FROM stdin;
MyAtelier Pro	MyAtelier Pro	EGP	t	4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	2026-03-14 04:11:52.698524+00	2026-03-14 04:11:52.698524+00
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customers (company_id, full_name, phone, email, address, notes, is_active, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	????? ???? 1773629038	01191773629038	\N	\N	\N	t	cc444c7a-e21b-40c9-b6f8-2dd1cd960d75	2026-03-16 02:43:58.882473+00	2026-03-16 02:43:58.882473+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	????? 1773629173	01517736291	\N	\N	\N	t	460a28a5-7ea7-4a50-b382-ad358cd7e2e1	2026-03-16 02:46:13.959809+00	2026-03-16 02:46:13.959809+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	????? ?????? 204059	01077204059	\N	\N	\N	t	79d051ec-dca1-4f38-9b11-ce0fa552f885	2026-03-16 18:40:59.191461+00	2026-03-16 18:40:59.191461+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	????? ?????? 204145	01077204145	\N	\N	\N	t	d10e110e-4042-4875-81aa-b7340d5aa196	2026-03-16 18:41:44.978194+00	2026-03-16 18:41:44.978194+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Customer 1773706106789	01706106789	\N	\N	\N	t	c6d38262-d5f9-42d9-a7e9-c4ab6faa3e58	2026-03-17 00:08:26.871204+00	2026-03-17 00:08:26.871204+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Customer 1773706358582	01706358582	\N	\N	\N	t	689b4cbd-8e3d-44b6-8c88-ca9bbb4d0879	2026-03-17 00:12:38.697514+00	2026-03-17 00:12:38.697514+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Customer 1773706814824	01706814824	\N	\N	\N	t	b129410b-4c99-496b-afcb-c3e01c5ed0ab	2026-03-17 00:20:14.915779+00	2026-03-17 00:20:14.915779+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Customer 1773706962620	01706962620	\N	\N	\N	t	b640a678-296d-4066-a213-a69dc7a28848	2026-03-17 00:22:42.771561+00	2026-03-17 00:22:42.771561+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Customer 1773707040360	01707040360	\N	\N	\N	t	95099d1d-f29f-491a-b82e-a0cc4177a149	2026-03-17 00:24:00.505198+00	2026-03-17 00:24:00.505198+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Customer 1773709645589	01709645589	\N	\N	\N	t	569b0220-d940-4f21-9890-50e05c5bcd7b	2026-03-17 01:07:26.535514+00	2026-03-17 01:07:26.535514+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Customer 1773709730441	01709730441	\N	\N	\N	t	e1990ef4-cba7-4c12-860a-7c0b9a5e771b	2026-03-17 01:08:50.520747+00	2026-03-17 01:08:50.520747+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Customer 1773709813793	01709813793	\N	\N	\N	t	87557f7b-4350-4c47-8434-ea9bda30ff22	2026-03-17 01:10:13.879963+00	2026-03-17 01:10:13.879963+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	Customer 1773709880588	01709880588	\N	\N	\N	t	975312e9-5b60-40ce-ae21-cf4ed1342061	2026-03-17 01:11:20.657707+00	2026-03-17 01:11:20.657707+00
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.departments (company_id, code, name, is_active, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	CHK1773629038	??? ???? 1773629038	t	e572c53b-86eb-44cd-8281-edb93c9e4530	2026-03-16 02:43:58.882473+00	2026-03-16 02:43:58.882473+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DEP1773629173	??? 1773629173	t	15549c36-4470-4562-8755-e447e35c6a78	2026-03-16 02:46:14.023311+00	2026-03-16 02:46:14.023311+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	REV204059	??? ?????? 204059	t	e29df0af-a599-475a-b3ae-869f6aee8090	2026-03-16 18:40:59.422405+00	2026-03-16 18:40:59.422405+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	REV204145	??? ?????? 204145	t	15c625ee-454a-4b87-adcd-6a439a5f9566	2026-03-16 18:41:45.111057+00	2026-03-16 18:41:45.111057+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DRESS-106789	Dress Dept 6789	t	77138a2b-1407-4cf2-9d06-3b0690dae582	2026-03-17 00:08:27.146575+00	2026-03-17 00:08:27.146575+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DRESS-358582	Dress Dept 8582	t	820bdc06-5317-459f-96b2-eb9d6946e39d	2026-03-17 00:12:38.773858+00	2026-03-17 00:12:38.773858+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DRESS-814824	Dress Dept 4824	t	47c96b72-97d5-403e-945f-dac0b55229e9	2026-03-17 00:20:14.9859+00	2026-03-17 00:20:14.9859+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DRESS-962620	Dress Dept 2620	t	88c7ccee-eaf0-4af0-9b46-631d9003ece0	2026-03-17 00:22:42.813987+00	2026-03-17 00:22:42.813987+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DRESS-040360	Dress Dept 0360	t	c1fc18e5-a7c1-499f-ae46-f44116fa56d4	2026-03-17 00:24:00.553504+00	2026-03-17 00:24:00.553504+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DRESS-645589	Dress Dept 5589	t	526e6e04-fd5a-42bf-9bdd-a8f0e919c51b	2026-03-17 01:07:26.690393+00	2026-03-17 01:07:26.690393+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DRESS-730441	Dress Dept 0441	t	9199284d-b0a4-4c80-96ac-77d030300589	2026-03-17 01:08:50.564865+00	2026-03-17 01:08:50.564865+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DRESS-813793	Dress Dept 3793	t	acfaf8ef-e8cd-4a33-a89b-9c3d6ece3be2	2026-03-17 01:10:14.050469+00	2026-03-17 01:10:14.050469+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DRESS-880588	Dress Dept 0588	t	3e4dbc64-7430-4493-bb76-49bf773fef7f	2026-03-17 01:11:20.730618+00	2026-03-17 01:11:20.730618+00
\.


--
-- Data for Name: document_sequences; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.document_sequences (company_id, key, prefix, next_number, padding, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	backup	BKP	1	6	0e26283d-deaf-4ae6-851b-77af765507b2	2026-03-14 04:11:52.698524+00	2026-03-14 04:11:52.698524+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	booking	BK	20	6	6d4fc8d0-9d5a-4b39-b553-6a21bf57bd98	2026-03-16 02:46:14.158742+00	2026-03-17 01:11:21.345525+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	payment	PAY	20	6	b0dfef79-c534-4584-988d-ad9565bc8479	2026-03-16 02:46:14.243758+00	2026-03-17 01:11:21.451039+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	journal_entry	JV	31	6	60cfdac9-78cf-4637-8c30-819702c9e082	2026-03-15 21:30:30.32481+00	2026-03-17 01:11:21.595212+00
\.


--
-- Data for Name: dress_resources; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dress_resources (company_id, code, dress_type, purchase_date, status, description, image_path, is_active, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	CHK-DR-1773629038	????	\N	available	????? ???? ??	\N	t	1c19ee33-8315-4dc1-85b4-d4c1eb4ef4f4	2026-03-16 02:43:58.882473+00	2026-03-16 02:43:58.882473+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR1773629173	????	\N	available	????? ???? ??	\N	t	89dc7a50-be70-45e3-9640-bb95bd387fb4	2026-03-16 02:46:14.127691+00	2026-03-16 02:46:14.127691+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-106789-1	Test	\N	available	Smoke one	\N	t	fc013cdf-a908-4a6c-a5cb-34bb0ca1ca12	2026-03-17 00:08:27.366481+00	2026-03-17 00:08:27.366481+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-106789-2	Test	\N	available	Smoke two	\N	t	a7b8f6b9-d43a-486c-8243-93406694934b	2026-03-17 00:08:27.90551+00	2026-03-17 00:08:27.90551+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-106789-3	Test	\N	available	Smoke three	\N	t	a3f96c16-3e33-43da-a0d2-3ae2c98137dc	2026-03-17 00:08:27.947648+00	2026-03-17 00:08:27.947648+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-358582-1	Test	\N	available	Smoke one	\N	t	f1b2b3b9-601d-45f1-a90a-af512a13a265	2026-03-17 00:12:38.977581+00	2026-03-17 00:12:38.977581+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-358582-2	Test	\N	available	Smoke two	\N	t	ac03c578-dab4-422a-b624-01df1b5f4212	2026-03-17 00:12:39.042069+00	2026-03-17 00:12:39.042069+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-358582-3	Test	\N	available	Smoke three	\N	t	ada29466-b3b5-42ec-89cc-668ab4c3b4d8	2026-03-17 00:12:39.103482+00	2026-03-17 00:12:39.103482+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-814824-1	Test	\N	available	Smoke one	\N	t	6cff60e7-84c5-4072-ae5a-0b4caf4ace39	2026-03-17 00:20:15.090366+00	2026-03-17 00:20:15.090366+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-814824-2	Test	\N	available	Smoke two	\N	t	86676064-f96c-4f1b-ae77-7a8999f712a2	2026-03-17 00:20:15.129693+00	2026-03-17 00:20:15.129693+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-814824-3	Test	\N	available	Smoke three	\N	t	2ac7d6b7-7040-4fd6-ae37-3cfe2707baf9	2026-03-17 00:20:15.193075+00	2026-03-17 00:20:15.193075+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-962620-1	Test	\N	available	Smoke one	\N	t	228b8a64-44d0-47f8-ae8d-b72409d7c375	2026-03-17 00:22:42.908226+00	2026-03-17 00:22:42.908226+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-962620-2	Test	\N	available	Smoke two	\N	t	bbe7b863-4b40-4d3a-be7b-bf968b8464b2	2026-03-17 00:22:42.947071+00	2026-03-17 00:22:42.947071+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-962620-3	Test	\N	available	Smoke three	\N	t	97c294cb-7f62-4356-ab79-53f1a03d7f9b	2026-03-17 00:22:42.979045+00	2026-03-17 00:22:42.979045+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-040360-1	Test	\N	available	Smoke one	\N	t	5250fc3b-26f2-4e3c-bae0-9fb58b517fd0	2026-03-17 00:24:00.653991+00	2026-03-17 00:24:00.653991+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-040360-2	Test	\N	available	Smoke two	\N	t	cace4cf6-955e-485e-99f3-0deb5c276db9	2026-03-17 00:24:00.699053+00	2026-03-17 00:24:00.699053+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-040360-3	Test	\N	available	Smoke three	\N	t	2fbf4c69-54bd-49f8-b6f0-1df518240f17	2026-03-17 00:24:00.737586+00	2026-03-17 00:24:00.737586+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-645589-1	Test	\N	available	Smoke one	\N	t	4e2502c8-db11-43d7-9964-dcae237ffd86	2026-03-17 01:07:26.856977+00	2026-03-17 01:07:26.856977+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-645589-2	Test	\N	available	Smoke two	\N	t	afba0200-537d-4cf2-8bdc-880fa34e811d	2026-03-17 01:07:26.906112+00	2026-03-17 01:07:26.906112+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-645589-3	Test	\N	available	Smoke three	\N	t	98cb0afb-136e-48ef-a289-39d1037eee04	2026-03-17 01:07:26.94623+00	2026-03-17 01:07:26.94623+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-730441-1	Test	\N	available	Smoke one	\N	t	f325c746-a2f2-4f42-b374-e332b7b731cb	2026-03-17 01:08:50.6999+00	2026-03-17 01:08:50.6999+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-730441-2	Test	\N	available	Smoke two	\N	t	5beb06c2-92b9-45d3-9742-5b187696e1c6	2026-03-17 01:08:50.735442+00	2026-03-17 01:08:50.735442+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-730441-3	Test	\N	available	Smoke three	\N	t	e122737b-0e54-4aaf-9f0b-5fe23495df99	2026-03-17 01:08:50.779017+00	2026-03-17 01:08:50.779017+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-813793-1	Test	\N	available	Smoke one	\N	t	c651f7b2-a8ca-4943-a873-5b49151df1fe	2026-03-17 01:10:14.124792+00	2026-03-17 01:10:14.124792+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-813793-2	Test	\N	available	Smoke two	\N	t	3dd42f89-2194-4c0a-91eb-10a20c19fbfb	2026-03-17 01:10:14.159327+00	2026-03-17 01:10:14.159327+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-813793-3	Test	\N	available	Smoke three	\N	t	ad309071-0cf3-4e26-9cc4-f07ef07c710c	2026-03-17 01:10:14.199538+00	2026-03-17 01:10:14.199538+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-880588-1	Test	\N	available	Smoke one	\N	t	12f9ae70-9c6d-4da7-b3d0-d280db9fffcb	2026-03-17 01:11:20.993233+00	2026-03-17 01:11:20.993233+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-880588-2	Test	\N	available	Smoke two	\N	t	46dfbbbc-39a1-4315-afc7-4bc9c8dbba66	2026-03-17 01:11:21.048559+00	2026-03-17 01:11:21.048559+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	DR-880588-3	Test	\N	available	Smoke three	\N	t	f410e21b-65a8-4ef6-b6e2-cedef4de4132	2026-03-17 01:11:21.087675+00	2026-03-17 01:11:21.087675+00
\.


--
-- Data for Name: export_schedules; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.export_schedules (company_id, branch_id, name, export_type, cadence, next_run_on, last_run_at, is_active, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: fiscal_periods; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fiscal_periods (company_id, name, starts_on, ends_on, is_active, is_locked, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	FY 2026	2026-01-01	2026-12-31	t	f	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	2026-03-14 04:11:52.698524+00	2026-03-14 04:11:52.698524+00
\.


--
-- Data for Name: journal_entries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.journal_entries (company_id, fiscal_period_id, entry_number, entry_date, status, reference, notes, posted_at, posted_by_user_id, reversed_at, reversed_by_user_id, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000025	2026-03-17	posted	PAY000016	Auto-posted from payment document PAY000016	2026-03-17 01:10:14.281389+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	adea8eb6-431c-421c-a1de-d79dfdf9e392	2026-03-17 01:10:14.228646+00	2026-03-17 01:10:14.228646+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000001	2026-03-15	reversed	LIVE-CHECK	Checkpoint 2C live verification	2026-03-15 21:41:46.801895+00	6307835d-b313-404a-a23b-ab033854f2cb	2026-03-15 21:41:46.856534+00	6307835d-b313-404a-a23b-ab033854f2cb	8e391c2b-adb8-40bb-aec2-85364b946f44	2026-03-15 21:41:46.594677+00	2026-03-15 21:41:46.843704+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000002	2026-03-15	posted	REV-JV000001	Live reverse	2026-03-15 21:41:46.855931+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	575a4f29-e617-4dc2-ac3b-998261bca564	2026-03-15 21:41:46.843704+00	2026-03-15 21:41:46.843704+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000003	2026-06-15	posted	PAY000001	Auto-posted from payment PAY000001 for booking BK000001	2026-03-16 02:46:14.337846+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	548dde2a-f7ed-4b86-87ef-544f529d0912	2026-03-16 02:46:14.243758+00	2026-03-16 02:46:14.243758+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000004	2026-03-16	posted	PAY000002	Auto-posted from payment PAY000002 for booking BK000002	2026-03-16 18:40:59.791869+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	36acb4c2-8d63-46c1-8ef2-4abae7112c63	2026-03-16 18:40:59.671978+00	2026-03-16 18:40:59.671978+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000005	2026-03-16	posted	PAY000003	Auto-posted from payment PAY000003 for booking BK000003	2026-03-16 18:41:45.463423+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	5fef3233-2feb-4437-b745-f8dc8ecc45cd	2026-03-16 18:41:45.345328+00	2026-03-16 18:41:45.345328+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000006	2026-03-16	posted	BK000003	Revenue recognition for booking BK000003	2026-03-16 18:41:45.582087+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	9c202f55-df97-4cfe-b00b-30eb9cfaec8d	2026-03-16 18:41:45.532709+00	2026-03-16 18:41:45.532709+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000007	2026-03-17	posted	PAY000004	Auto-posted from payment document PAY000004	2026-03-17 00:12:39.307898+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	f83a7e7f-8f9d-4b6f-b94a-927b0f31131d	2026-03-17 00:12:39.148139+00	2026-03-17 00:12:39.148139+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000008	2026-03-18	posted	PAY000005	Auto-posted from payment document PAY000005	2026-03-17 00:12:39.776772+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	8365d96f-b12d-4763-a7bd-a6df0f606e68	2026-03-17 00:12:39.65449+00	2026-03-17 00:12:39.65449+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000009	2026-03-17	posted	BK000004-L1	Revenue recognition for booking BK000004 line 1	2026-03-17 00:12:39.97187+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	146e33da-3a41-43ae-855b-ff0d1735734f	2026-03-17 00:12:39.920606+00	2026-03-17 00:12:39.920606+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000010	2026-03-17	posted	PAY000006	Auto-posted from payment document PAY000006	2026-03-17 00:20:15.452227+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	b94fb361-b1c0-4f4c-bd12-df21755b448c	2026-03-17 00:20:15.230029+00	2026-03-17 00:20:15.230029+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000011	2026-03-18	posted	PAY000007	Auto-posted from payment document PAY000007	2026-03-17 00:20:15.756215+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	6b6f3333-4541-4ebd-963a-7a2b4171c868	2026-03-17 00:20:15.662209+00	2026-03-17 00:20:15.662209+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000012	2026-03-17	posted	BK000006-L1	Revenue recognition for booking BK000006 line 1	2026-03-17 00:20:15.866002+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	1b4afa61-9ba3-4a84-8b2b-86b943a2dc41	2026-03-17 00:20:15.820115+00	2026-03-17 00:20:15.820115+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000013	2026-03-17	posted	PAY000008	Auto-posted from payment document PAY000008	2026-03-17 00:22:43.060145+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	edbabc2c-2e12-46e6-849b-c5190548315c	2026-03-17 00:22:43.010078+00	2026-03-17 00:22:43.010078+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000014	2026-03-18	posted	PAY000009	Auto-posted from payment document PAY000009	2026-03-17 00:22:43.407944+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	32defaff-4d2c-4518-b21a-8db3ca6067ba	2026-03-17 00:22:43.314169+00	2026-03-17 00:22:43.314169+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000015	2026-03-17	posted	BK000008-L1	Revenue recognition for booking BK000008 line 1	2026-03-17 00:22:43.506547+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	3929e44f-5af8-4727-b1e7-015667262f27	2026-03-17 00:22:43.460353+00	2026-03-17 00:22:43.460353+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000016	2026-03-17	posted	PAY000010	Auto-posted from payment document PAY000010	2026-03-17 00:24:00.887649+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	289b0b29-2dbe-43b1-8fea-67e0333dcc16	2026-03-17 00:24:00.775978+00	2026-03-17 00:24:00.775978+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000017	2026-03-18	posted	PAY000011	Auto-posted from payment document PAY000011	2026-03-17 00:24:01.114511+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	06059536-188d-4377-ae32-c39134f1a3a3	2026-03-17 00:24:01.049193+00	2026-03-17 00:24:01.049193+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000018	2026-03-17	posted	BK000010-L1	Revenue recognition for booking BK000010 line 1	2026-03-17 00:24:01.212604+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	cadb9018-37a3-4e79-8140-fbfd055c863b	2026-03-17 00:24:01.170291+00	2026-03-17 00:24:01.170291+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000019	2026-03-17	posted	PAY000012	Auto-posted from payment document PAY000012	2026-03-17 01:07:27.111462+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	c04b1cd3-3fd8-4b1c-9343-e7d011a77399	2026-03-17 01:07:26.98646+00	2026-03-17 01:07:26.98646+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000020	2026-03-18	posted	PAY000013	Auto-posted from payment document PAY000013	2026-03-17 01:07:27.392687+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	125fb589-11d3-495d-b784-bb0b96feaf20	2026-03-17 01:07:27.30599+00	2026-03-17 01:07:27.30599+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000021	2026-03-17	posted	BK000012-L1	Revenue recognition for booking BK000012 line 1	2026-03-17 01:07:27.512876+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	9be81ea4-ebdf-4540-8030-94fcf8e81330	2026-03-17 01:07:27.469059+00	2026-03-17 01:07:27.469059+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000022	2026-03-17	posted	PAY000014	Auto-posted from payment document PAY000014	2026-03-17 01:08:50.878471+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	6f9fa24a-2793-4842-b400-9dc05a6e2653	2026-03-17 01:08:50.820724+00	2026-03-17 01:08:50.820724+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000023	2026-03-18	posted	PAY000015	Auto-posted from payment document PAY000015	2026-03-17 01:08:51.145+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	781465cf-312a-40e9-aa2d-7d406519317f	2026-03-17 01:08:51.068593+00	2026-03-17 01:08:51.068593+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000024	2026-03-17	posted	BK000014-L1	Revenue recognition for booking BK000014 line 1	2026-03-17 01:08:51.30004+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	fc16ac63-de51-40cd-b7f8-53da6c108859	2026-03-17 01:08:51.240812+00	2026-03-17 01:08:51.240812+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000026	2026-03-18	posted	PAY000017	Auto-posted from payment document PAY000017	2026-03-17 01:10:14.679002+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	3724ce70-9815-4497-927c-bdf5e750d596	2026-03-17 01:10:14.602044+00	2026-03-17 01:10:14.602044+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000027	2026-03-17	posted	BK000016-L1	Revenue recognition for booking BK000016 line 1	2026-03-17 01:10:14.785378+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	76e03013-b2ee-4d86-be41-1f2ecb0b3d74	2026-03-17 01:10:14.738563+00	2026-03-17 01:10:14.738563+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000028	2026-03-17	posted	PAY000018	Auto-posted from payment document PAY000018	2026-03-17 01:11:21.258124+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	91e036e4-dd8e-4959-98be-7790c7e72558	2026-03-17 01:11:21.128803+00	2026-03-17 01:11:21.128803+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000029	2026-03-18	posted	PAY000019	Auto-posted from payment document PAY000019	2026-03-17 01:11:21.531145+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	1870fb02-647b-4078-977f-5b240210f236	2026-03-17 01:11:21.451039+00	2026-03-17 01:11:21.451039+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	7c1f2ab6-0230-47f1-b543-95d0f14f3fc9	JV000030	2026-03-17	posted	BK000018-L1	Revenue recognition for booking BK000018 line 1	2026-03-17 01:11:21.645984+00	6307835d-b313-404a-a23b-ab033854f2cb	\N	\N	317c2eb1-c67b-43df-a608-ae96046dc72e	2026-03-17 01:11:21.595212+00	2026-03-17 01:11:21.595212+00
\.


--
-- Data for Name: journal_entry_lines; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.journal_entry_lines (journal_entry_id, account_id, line_number, description, debit_amount, credit_amount, id) FROM stdin;
8e391c2b-adb8-40bb-aec2-85364b946f44	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Cash	250.00	0.00	44b23989-9560-440d-9096-057c9587576b
8e391c2b-adb8-40bb-aec2-85364b946f44	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	2	Revenue	0.00	250.00	64399836-3513-47e8-859b-cf0ded767931
575a4f29-e617-4dc2-ac3b-998261bca564	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Cash	0.00	250.00	bf7afb7f-7cfd-497d-92a7-1b3a1d70b1e5
575a4f29-e617-4dc2-ac3b-998261bca564	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	2	Revenue	250.00	0.00	fe9c928c-e040-4aa0-a0c8-37b2f0091556
548dde2a-f7ed-4b86-87ef-544f529d0912	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment PAY000001 on booking BK000001	1200.00	0.00	816badb9-8f96-4689-96a7-304a4342e8b3
548dde2a-f7ed-4b86-87ef-544f529d0912	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment PAY000001 on booking BK000001	0.00	1200.00	03268e0d-71c4-49dd-82da-fd4bcee3dc22
36acb4c2-8d63-46c1-8ef2-4abae7112c63	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment PAY000002 on booking BK000002	1000.00	0.00	53865850-82ee-4593-80a9-7de4caf2e263
36acb4c2-8d63-46c1-8ef2-4abae7112c63	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment PAY000002 on booking BK000002	0.00	1000.00	c3b80c3b-9b68-4a41-b91f-43216275ba93
5fef3233-2feb-4437-b745-f8dc8ecc45cd	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment PAY000003 on booking BK000003	1000.00	0.00	d5120aa8-fcc2-4ccc-8d37-da076ba89d8f
5fef3233-2feb-4437-b745-f8dc8ecc45cd	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment PAY000003 on booking BK000003	0.00	1000.00	0c145c80-6181-4e38-a142-a14fe0e41f67
9c202f55-df97-4cfe-b00b-30eb9cfaec8d	864cf71a-41a6-45ab-81d7-c51766ec8cfc	1	Booking completion BK000003	1000.00	0.00	496393ec-2de1-4399-979f-27362ca8abe8
9c202f55-df97-4cfe-b00b-30eb9cfaec8d	b2a1d538-6540-467f-91ed-f709e29c76d7	2	Booking completion BK000003	1500.00	0.00	28535ae1-44ff-4b75-a722-bb0108725510
9c202f55-df97-4cfe-b00b-30eb9cfaec8d	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	3	Booking completion BK000003	0.00	2500.00	29661b79-07d4-4a1e-a54e-9add899d7cab
f83a7e7f-8f9d-4b6f-b94a-927b0f31131d	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000004	250.00	0.00	b51f44fa-d342-4f7d-b2ca-5813605722be
f83a7e7f-8f9d-4b6f-b94a-927b0f31131d	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000004	0.00	250.00	d08fd105-c259-4e32-be50-6a0fb1ed2c73
8365d96f-b12d-4763-a7bd-a6df0f606e68	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000005	500.00	0.00	df6a8d46-fa58-499d-b25c-cf7826eb58cd
8365d96f-b12d-4763-a7bd-a6df0f606e68	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000005	0.00	500.00	2f688800-973c-41bf-a991-fb94cc938729
146e33da-3a41-43ae-855b-ff0d1735734f	864cf71a-41a6-45ab-81d7-c51766ec8cfc	1	Booking BK000004 line 1	300.00	0.00	f2ae13bc-e4bd-47e6-8a19-2837ac5fe141
146e33da-3a41-43ae-855b-ff0d1735734f	b2a1d538-6540-467f-91ed-f709e29c76d7	2	Booking BK000004 line 1	2200.00	0.00	056d9b0a-7a1f-4f50-91b0-47bacd914b2e
146e33da-3a41-43ae-855b-ff0d1735734f	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	3	Booking BK000004 line 1	0.00	2500.00	73f79e47-45b5-4465-83b3-efe9366e5a17
b94fb361-b1c0-4f4c-bd12-df21755b448c	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000006	250.00	0.00	bf8efa21-e034-4f40-a8ea-13065dc289f3
b94fb361-b1c0-4f4c-bd12-df21755b448c	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000006	0.00	250.00	d3c9b700-cbf9-4b0f-b34c-07e4aa4efb69
6b6f3333-4541-4ebd-963a-7a2b4171c868	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000007	500.00	0.00	e1bb42e8-7811-4215-9b56-78d7e6e5c059
6b6f3333-4541-4ebd-963a-7a2b4171c868	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000007	0.00	500.00	918b5156-9c24-4908-a8c1-5887ff064bd0
1b4afa61-9ba3-4a84-8b2b-86b943a2dc41	864cf71a-41a6-45ab-81d7-c51766ec8cfc	1	Booking BK000006 line 1	300.00	0.00	48e563b4-85d1-460e-980e-99d6abcc231e
1b4afa61-9ba3-4a84-8b2b-86b943a2dc41	b2a1d538-6540-467f-91ed-f709e29c76d7	2	Booking BK000006 line 1	2200.00	0.00	3f393754-bef7-45a4-8f83-d8fae65b9c04
1b4afa61-9ba3-4a84-8b2b-86b943a2dc41	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	3	Booking BK000006 line 1	0.00	2500.00	6f52561e-6eb5-4937-8c21-dedf14af6f3d
edbabc2c-2e12-46e6-849b-c5190548315c	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000008	250.00	0.00	0717aef7-8c5e-41a1-ac88-d6781faa5b38
edbabc2c-2e12-46e6-849b-c5190548315c	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000008	0.00	250.00	603a4318-843d-483f-9f84-cfede54d33a5
32defaff-4d2c-4518-b21a-8db3ca6067ba	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000009	500.00	0.00	c35590a6-a446-48aa-8aec-2663b8aa852d
32defaff-4d2c-4518-b21a-8db3ca6067ba	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000009	0.00	500.00	e2b45ea1-d387-4dd5-86c9-f49d34bfb003
3929e44f-5af8-4727-b1e7-015667262f27	864cf71a-41a6-45ab-81d7-c51766ec8cfc	1	Booking BK000008 line 1	300.00	0.00	ae4f630b-9000-4d96-adcb-852fe726e729
3929e44f-5af8-4727-b1e7-015667262f27	b2a1d538-6540-467f-91ed-f709e29c76d7	2	Booking BK000008 line 1	2200.00	0.00	3f8839d9-e12a-42be-8980-06de5ceb5a7e
3929e44f-5af8-4727-b1e7-015667262f27	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	3	Booking BK000008 line 1	0.00	2500.00	db29040e-6b98-4992-8f25-25e9fcf34c3e
289b0b29-2dbe-43b1-8fea-67e0333dcc16	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000010	250.00	0.00	ec023a30-eece-4e5d-b786-3a962dca1165
289b0b29-2dbe-43b1-8fea-67e0333dcc16	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000010	0.00	250.00	478f128d-f1f9-4c8c-a50c-ab562f8b9e82
06059536-188d-4377-ae32-c39134f1a3a3	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000011	500.00	0.00	cddb939e-cc3e-4592-a366-35758ccebe1f
06059536-188d-4377-ae32-c39134f1a3a3	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000011	0.00	500.00	f5b9226e-63b7-44b5-9200-95dc7944f788
cadb9018-37a3-4e79-8140-fbfd055c863b	864cf71a-41a6-45ab-81d7-c51766ec8cfc	1	Booking BK000010 line 1	300.00	0.00	91177556-90d4-4a97-865c-893f83306e0c
cadb9018-37a3-4e79-8140-fbfd055c863b	b2a1d538-6540-467f-91ed-f709e29c76d7	2	Booking BK000010 line 1	2200.00	0.00	9c3fb652-7573-4378-868b-f9669a0c260a
cadb9018-37a3-4e79-8140-fbfd055c863b	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	3	Booking BK000010 line 1	0.00	2500.00	c17b129a-6de9-4a42-b7a1-ab18502c65e7
c04b1cd3-3fd8-4b1c-9343-e7d011a77399	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000012	250.00	0.00	60d64a8a-f385-49b6-a0d1-2931e8be8849
c04b1cd3-3fd8-4b1c-9343-e7d011a77399	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000012	0.00	250.00	1711daf9-1edb-4827-9843-e6c00af93d20
125fb589-11d3-495d-b784-bb0b96feaf20	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000013	500.00	0.00	a608b1b2-e185-48ba-b410-00e12f31ccc3
125fb589-11d3-495d-b784-bb0b96feaf20	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000013	0.00	500.00	e0388eec-7b60-42cd-893c-882daf115b6c
9be81ea4-ebdf-4540-8030-94fcf8e81330	864cf71a-41a6-45ab-81d7-c51766ec8cfc	1	Booking BK000012 line 1	300.00	0.00	72dbdfa3-55a1-4fae-886c-125312b68b8b
9be81ea4-ebdf-4540-8030-94fcf8e81330	b2a1d538-6540-467f-91ed-f709e29c76d7	2	Booking BK000012 line 1	2200.00	0.00	afbe6fe8-30f6-4522-9c0f-997abf455f43
9be81ea4-ebdf-4540-8030-94fcf8e81330	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	3	Booking BK000012 line 1	0.00	2500.00	1a90fd37-1f6c-4753-95b1-69f05ecca1b5
6f9fa24a-2793-4842-b400-9dc05a6e2653	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000014	250.00	0.00	09da3393-64dc-42a8-a5f4-216eac296b7a
6f9fa24a-2793-4842-b400-9dc05a6e2653	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000014	0.00	250.00	b3a345b9-36fa-4a54-aeb7-1fb4d3229922
781465cf-312a-40e9-aa2d-7d406519317f	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000015	500.00	0.00	80b2fa66-09b9-443f-b2f2-cbe2b4aca8d6
781465cf-312a-40e9-aa2d-7d406519317f	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000015	0.00	500.00	50f09f1a-a5ae-476e-ae84-bdc01706d42d
fc16ac63-de51-40cd-b7f8-53da6c108859	864cf71a-41a6-45ab-81d7-c51766ec8cfc	1	Booking BK000014 line 1	300.00	0.00	dbe77f32-d4e6-4193-8427-ba1461b5a4e7
fc16ac63-de51-40cd-b7f8-53da6c108859	b2a1d538-6540-467f-91ed-f709e29c76d7	2	Booking BK000014 line 1	2200.00	0.00	0d698d32-271c-4d08-85f3-5efdfa916e7e
fc16ac63-de51-40cd-b7f8-53da6c108859	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	3	Booking BK000014 line 1	0.00	2500.00	b7f8ac1f-24fc-492f-acc0-a0bc6305292b
adea8eb6-431c-421c-a1de-d79dfdf9e392	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000016	250.00	0.00	14b4fe79-ffce-48a5-b479-1e8d95e659c0
adea8eb6-431c-421c-a1de-d79dfdf9e392	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000016	0.00	250.00	5213ff02-2368-4a3b-8664-bfab76a860be
3724ce70-9815-4497-927c-bdf5e750d596	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000017	500.00	0.00	ad6d885a-f6ec-486c-9677-4f27bd0c01dd
3724ce70-9815-4497-927c-bdf5e750d596	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000017	0.00	500.00	965d4852-4197-44cd-af4f-22e34ae59b66
76e03013-b2ee-4d86-be41-1f2ecb0b3d74	864cf71a-41a6-45ab-81d7-c51766ec8cfc	1	Booking BK000016 line 1	300.00	0.00	690285b0-b18f-44a7-a62d-7433c4c2ffce
76e03013-b2ee-4d86-be41-1f2ecb0b3d74	b2a1d538-6540-467f-91ed-f709e29c76d7	2	Booking BK000016 line 1	2200.00	0.00	f74ff36a-14f0-4b60-b053-76616f4dbced
76e03013-b2ee-4d86-be41-1f2ecb0b3d74	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	3	Booking BK000016 line 1	0.00	2500.00	3b708abb-0db8-4482-a47d-9827e1c0021b
91e036e4-dd8e-4959-98be-7790c7e72558	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000018	250.00	0.00	db005386-158e-468f-ad85-5be5e0ec4dfd
91e036e4-dd8e-4959-98be-7790c7e72558	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000018	0.00	250.00	c9f895e8-514d-423f-955d-9315b3dda07f
1870fb02-647b-4078-977f-5b240210f236	756f5f60-b7b9-48d6-baf8-4b7cdc451048	1	Payment document PAY000019	500.00	0.00	760e8335-92af-401b-9c35-de210e50919f
1870fb02-647b-4078-977f-5b240210f236	864cf71a-41a6-45ab-81d7-c51766ec8cfc	2	Payment document PAY000019	0.00	500.00	e16575fe-a9bd-4398-a115-d24eab7ff9ca
317c2eb1-c67b-43df-a608-ae96046dc72e	864cf71a-41a6-45ab-81d7-c51766ec8cfc	1	Booking BK000018 line 1	300.00	0.00	a370ba4a-936a-403b-b72f-c516ca3ec702
317c2eb1-c67b-43df-a608-ae96046dc72e	b2a1d538-6540-467f-91ed-f709e29c76d7	2	Booking BK000018 line 1	2200.00	0.00	07bd2dd9-7864-4de8-9451-9d0a802d453a
317c2eb1-c67b-43df-a608-ae96046dc72e	6d6db60d-92e4-4da1-a7e5-c0cf4de303ab	3	Booking BK000018 line 1	0.00	2500.00	fc12dc1a-ef70-4a33-b945-6d7198501e76
\.


--
-- Data for Name: payment_allocations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payment_allocations (payment_document_id, booking_id, booking_line_id, line_number, allocated_amount, id, created_at, updated_at) FROM stdin;
27508ca7-d38b-482a-a7a6-19034875725d	cb7e1e39-0ecc-4b12-baa1-7a4a898c3d0a	4ec5b55c-4e39-4717-9d40-cb0f03148518	1	1200.00	7f6dfcbb-80f8-4768-8af3-9922f63c16fa	2026-03-16 02:46:14.243758+00	2026-03-16 02:46:14.243758+00
a9d02e7b-5e7f-45e6-b163-a0a3b373365a	80384f11-9127-4c38-abae-1d991b12c7b1	d6841418-8f29-49b9-815a-bfd76dcc1d08	1	1000.00	70beab03-cac7-427b-9372-70c10d3b7a1d	2026-03-16 18:40:59.671978+00	2026-03-16 18:40:59.671978+00
848efb02-2059-4240-ad0a-99d48107764e	09fdb729-07b3-4454-ac97-a4da673096ca	8b79e88b-dbf5-4f08-b245-025ebfa1ade3	1	1000.00	3fa99a53-0811-4e45-8c96-57d746e0f5b6	2026-03-16 18:41:45.345328+00	2026-03-16 18:41:45.345328+00
c906f93f-5510-44b8-aee5-9f3c6e055eb0	373e5fe4-1107-4328-8817-3e01050e7c60	7c6c491f-a1c7-4cdd-97be-31b723468e2a	1	100.00	3504b745-cc43-4940-8b89-fc95901f1b58	2026-03-17 00:12:39.148139+00	2026-03-17 00:12:39.148139+00
c906f93f-5510-44b8-aee5-9f3c6e055eb0	373e5fe4-1107-4328-8817-3e01050e7c60	10cf35d4-9e86-4948-8c24-42cce7da259c	2	150.00	1334be4d-54f8-40fe-bd24-1670b2ddb321	2026-03-17 00:12:39.148139+00	2026-03-17 00:12:39.148139+00
8960e8b6-86a4-4f2a-b8c9-33f199efdfec	373e5fe4-1107-4328-8817-3e01050e7c60	7c6c491f-a1c7-4cdd-97be-31b723468e2a	1	200.00	1c7132b5-a8b3-4456-8e93-11b6fb3cf1ac	2026-03-17 00:12:39.65449+00	2026-03-17 00:12:39.65449+00
8960e8b6-86a4-4f2a-b8c9-33f199efdfec	a7fae3d4-83de-4d73-b8f1-5e965f165c3a	51ee1db9-9440-4392-b7fc-c6b2dbd97758	2	300.00	be21c3f4-f4a8-4f89-a4ef-5b59159a39bd	2026-03-17 00:12:39.65449+00	2026-03-17 00:12:39.65449+00
e3a574da-701f-4786-b108-f4cd84075892	62fc5598-c3b0-4b85-9c2b-5b5c9fa3178d	943e99ff-48de-4703-b5ae-a0e99dbd60c2	1	100.00	55f7eed1-200c-439d-913f-659514699973	2026-03-17 00:20:15.230029+00	2026-03-17 00:20:15.230029+00
e3a574da-701f-4786-b108-f4cd84075892	62fc5598-c3b0-4b85-9c2b-5b5c9fa3178d	9a65956f-6fdb-4f9e-8e53-a8f324ba8127	2	150.00	4b35356a-5240-430a-8737-a74c789dae0a	2026-03-17 00:20:15.230029+00	2026-03-17 00:20:15.230029+00
4e4ab113-0934-4c4f-aecc-31324eae7d87	62fc5598-c3b0-4b85-9c2b-5b5c9fa3178d	943e99ff-48de-4703-b5ae-a0e99dbd60c2	1	200.00	df53a287-feb6-4c9c-be21-38687f05aa5c	2026-03-17 00:20:15.662209+00	2026-03-17 00:20:15.662209+00
4e4ab113-0934-4c4f-aecc-31324eae7d87	4654a8bc-829b-4c34-8b76-4d6adf35a38f	75a899ce-8072-4408-bf49-f075d0e81f5c	2	300.00	3f7d49f0-64a9-46ab-abd1-4d119329012b	2026-03-17 00:20:15.662209+00	2026-03-17 00:20:15.662209+00
3ca7e7b2-b7a9-4d13-a9b8-aaaa0182c7fd	d9c97a83-7b0f-4665-8b13-c077bf053b5a	1b84b3a8-c519-4869-b7bf-3e72a61423c6	1	100.00	20f7cd0e-2146-46bc-be29-2d5596edef6e	2026-03-17 00:22:43.010078+00	2026-03-17 00:22:43.010078+00
3ca7e7b2-b7a9-4d13-a9b8-aaaa0182c7fd	d9c97a83-7b0f-4665-8b13-c077bf053b5a	2dfb0bc3-ec28-4200-be0a-f2de6d0b98c8	2	150.00	4876fbc2-7040-407f-b13e-a5bd8ac50378	2026-03-17 00:22:43.010078+00	2026-03-17 00:22:43.010078+00
906e97d5-5c07-457e-abc9-3c7efac43ae9	d9c97a83-7b0f-4665-8b13-c077bf053b5a	1b84b3a8-c519-4869-b7bf-3e72a61423c6	1	200.00	490236b3-9200-4a10-bdfb-862641bb25df	2026-03-17 00:22:43.314169+00	2026-03-17 00:22:43.314169+00
906e97d5-5c07-457e-abc9-3c7efac43ae9	c7260264-8785-4f3c-abd0-06e573998cf9	6a7a0ea8-5761-4ff4-b9b1-18fbfde32dc3	2	300.00	f839ca60-068a-4bae-9d45-6f16541a4f81	2026-03-17 00:22:43.314169+00	2026-03-17 00:22:43.314169+00
bb203f17-3346-4c92-9364-b22468baafc6	8e2f01f5-dea0-43ab-97ab-775ab374e6cd	eade8dce-bfa2-4005-b1f2-31e46c2b3c27	1	100.00	6ee6d690-c667-45b9-8524-8511f7d4c3e8	2026-03-17 00:24:00.775978+00	2026-03-17 00:24:00.775978+00
bb203f17-3346-4c92-9364-b22468baafc6	8e2f01f5-dea0-43ab-97ab-775ab374e6cd	eed631b5-d3b4-4c06-93a2-450ffb61b5a2	2	150.00	2021b468-c104-4ae4-9e47-1aec8503120b	2026-03-17 00:24:00.775978+00	2026-03-17 00:24:00.775978+00
af5c3d7e-f057-4cfb-9ca0-0c587a8cbf70	8e2f01f5-dea0-43ab-97ab-775ab374e6cd	eade8dce-bfa2-4005-b1f2-31e46c2b3c27	1	200.00	9e959fc2-b413-447f-a107-c761d0e2c5ac	2026-03-17 00:24:01.049193+00	2026-03-17 00:24:01.049193+00
af5c3d7e-f057-4cfb-9ca0-0c587a8cbf70	1019bb9d-6fc7-4582-9462-89ce4fe8202a	67059ea2-383b-4af2-b548-3f6347b43980	2	300.00	337f4584-9ede-454c-a1a0-f6c4f69fe66c	2026-03-17 00:24:01.049193+00	2026-03-17 00:24:01.049193+00
e31adbec-74ee-42ad-bc49-55ca87c733e8	bf605211-dba4-432c-bb28-d6b8156c6d0e	f824c54c-12a6-4cdc-86e6-6e24990ba1f5	1	100.00	6d7cd2c2-6e0e-4e37-8b00-79f8be40b9dd	2026-03-17 01:07:26.98646+00	2026-03-17 01:07:26.98646+00
e31adbec-74ee-42ad-bc49-55ca87c733e8	bf605211-dba4-432c-bb28-d6b8156c6d0e	7612320d-f0dd-4507-b167-4fe5095081f9	2	150.00	a2723c4e-0028-4c38-ae23-3853dc0a4e9c	2026-03-17 01:07:26.98646+00	2026-03-17 01:07:26.98646+00
11a8759d-8fe3-480c-9189-c26ac40a7de1	bf605211-dba4-432c-bb28-d6b8156c6d0e	f824c54c-12a6-4cdc-86e6-6e24990ba1f5	1	200.00	77f3a215-6afa-4a07-9564-b8956b92a726	2026-03-17 01:07:27.30599+00	2026-03-17 01:07:27.30599+00
11a8759d-8fe3-480c-9189-c26ac40a7de1	05cb0064-d7e0-4eeb-a5c5-c3b9157484cf	60346925-6764-4a86-a398-5b6177112f9c	2	300.00	7526e68b-2dbc-4696-9d94-c88c43d97d5a	2026-03-17 01:07:27.30599+00	2026-03-17 01:07:27.30599+00
2235082e-7763-4562-bfef-16a5a4f39af3	d6e795c9-26cf-4b7b-b0f4-7abd95dfd213	0df44b2c-be7d-410d-bffe-a3ce3f66e717	1	100.00	e57d87bc-41ea-4e4c-907c-01f9289bee38	2026-03-17 01:08:50.820724+00	2026-03-17 01:08:50.820724+00
2235082e-7763-4562-bfef-16a5a4f39af3	d6e795c9-26cf-4b7b-b0f4-7abd95dfd213	15e4c5f6-8d82-47ad-a1f1-e8d3fdc37846	2	150.00	c196dcc0-4b65-48e5-98d7-34d77b33930f	2026-03-17 01:08:50.820724+00	2026-03-17 01:08:50.820724+00
ba95e7a6-570d-4040-9831-c4de8dbad623	d6e795c9-26cf-4b7b-b0f4-7abd95dfd213	0df44b2c-be7d-410d-bffe-a3ce3f66e717	1	200.00	46c5a70b-eb65-47f1-b535-22f1f335dcd1	2026-03-17 01:08:51.068593+00	2026-03-17 01:08:51.068593+00
ba95e7a6-570d-4040-9831-c4de8dbad623	1d6982d3-5ba6-475f-bc4a-536c075ead59	c7d283a7-6ab6-4dd5-9576-26efc871cee6	2	300.00	1339109c-4026-4c44-b10a-4db64c38228b	2026-03-17 01:08:51.068593+00	2026-03-17 01:08:51.068593+00
d3e92c90-7a9c-44c1-a035-07e195d0dbe1	d36a3991-7078-4471-a1f5-8b21b0ea713e	7b91de29-d683-4753-a0b3-9662aa3e8395	1	100.00	94aa0962-4b30-433b-b00c-33b912a33522	2026-03-17 01:10:14.228646+00	2026-03-17 01:10:14.228646+00
d3e92c90-7a9c-44c1-a035-07e195d0dbe1	d36a3991-7078-4471-a1f5-8b21b0ea713e	5b2396d0-11c3-4343-b335-b96497553081	2	150.00	94f58731-4b47-42fc-9091-7060bd5f4cd9	2026-03-17 01:10:14.228646+00	2026-03-17 01:10:14.228646+00
12f9bc55-3693-421c-8874-b6abafc4f180	d36a3991-7078-4471-a1f5-8b21b0ea713e	7b91de29-d683-4753-a0b3-9662aa3e8395	1	200.00	fef5d04a-4345-4ce5-aeff-b752da59418f	2026-03-17 01:10:14.602044+00	2026-03-17 01:10:14.602044+00
12f9bc55-3693-421c-8874-b6abafc4f180	fa33d012-3afc-4526-9596-86213e690c41	5328aab3-4b7e-4606-9d5c-901456d533c4	2	300.00	f69a578c-dd9a-40ad-a72c-b4441387e961	2026-03-17 01:10:14.602044+00	2026-03-17 01:10:14.602044+00
a9f6b333-876b-44d4-854f-cbde3c5b1270	b160fe73-c188-4dbc-9bc2-7fb407387d8f	17f7e2f9-92a9-426e-9586-7599a193a77c	1	100.00	c83da47b-17dc-4f6e-85ce-8c3cdf20ef74	2026-03-17 01:11:21.128803+00	2026-03-17 01:11:21.128803+00
a9f6b333-876b-44d4-854f-cbde3c5b1270	b160fe73-c188-4dbc-9bc2-7fb407387d8f	c0518a66-b159-4c66-848d-4b17c00eea53	2	150.00	3eabed37-e279-4ed2-bfe8-2f87db27f571	2026-03-17 01:11:21.128803+00	2026-03-17 01:11:21.128803+00
d72b1004-173e-4f1a-a2a2-2e1084850975	b160fe73-c188-4dbc-9bc2-7fb407387d8f	17f7e2f9-92a9-426e-9586-7599a193a77c	1	200.00	39651355-7b39-470c-9d90-904246c154cb	2026-03-17 01:11:21.451039+00	2026-03-17 01:11:21.451039+00
d72b1004-173e-4f1a-a2a2-2e1084850975	e26dafd1-e398-4f96-83e2-c3f5fc98fbfc	64e74dd2-57f9-4e39-aedb-1cfe0793d3d2	2	300.00	08117dbb-4ca8-4e33-bf36-6a6080cbfff1	2026-03-17 01:11:21.451039+00	2026-03-17 01:11:21.451039+00
\.


--
-- Data for Name: payment_documents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payment_documents (company_id, branch_id, customer_id, payment_number, payment_date, document_kind, status, journal_entry_id, voided_at, voided_by_user_id, void_reason, notes, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	460a28a5-7ea7-4a50-b382-ad358cd7e2e1	PAY000001	2026-06-15	collection	active	548dde2a-f7ed-4b86-87ef-544f529d0912	\N	\N	\N	???? ???? ??	27508ca7-d38b-482a-a7a6-19034875725d	2026-03-16 02:46:14.243758+00	2026-03-16 02:46:14.243758+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	79d051ec-dca1-4f38-9b11-ce0fa552f885	PAY000002	2026-03-16	collection	active	36acb4c2-8d63-46c1-8ef2-4abae7112c63	\N	\N	\N	\N	a9d02e7b-5e7f-45e6-b163-a0a3b373365a	2026-03-16 18:40:59.671978+00	2026-03-16 18:40:59.671978+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	d10e110e-4042-4875-81aa-b7340d5aa196	PAY000003	2026-03-16	collection	active	5fef3233-2feb-4437-b745-f8dc8ecc45cd	\N	\N	\N	\N	848efb02-2059-4240-ad0a-99d48107764e	2026-03-16 18:41:45.345328+00	2026-03-16 18:41:45.345328+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	689b4cbd-8e3d-44b6-8c88-ca9bbb4d0879	PAY000004	2026-03-17	collection	active	f83a7e7f-8f9d-4b6f-b94a-927b0f31131d	\N	\N	\N	???? ????? ?? ????? ????? BK000004	c906f93f-5510-44b8-aee5-9f3c6e055eb0	2026-03-17 00:12:39.148139+00	2026-03-17 00:12:39.148139+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	689b4cbd-8e3d-44b6-8c88-ca9bbb4d0879	PAY000005	2026-03-18	collection	active	8365d96f-b12d-4763-a7bd-a6df0f606e68	\N	\N	\N	Playwright smoke allocation	8960e8b6-86a4-4f2a-b8c9-33f199efdfec	2026-03-17 00:12:39.65449+00	2026-03-17 00:12:39.65449+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	b129410b-4c99-496b-afcb-c3e01c5ed0ab	PAY000006	2026-03-17	collection	active	b94fb361-b1c0-4f4c-bd12-df21755b448c	\N	\N	\N	???? ????? ?? ????? ????? BK000006	e3a574da-701f-4786-b108-f4cd84075892	2026-03-17 00:20:15.230029+00	2026-03-17 00:20:15.230029+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	b129410b-4c99-496b-afcb-c3e01c5ed0ab	PAY000007	2026-03-18	collection	active	6b6f3333-4541-4ebd-963a-7a2b4171c868	\N	\N	\N	Playwright smoke allocation	4e4ab113-0934-4c4f-aecc-31324eae7d87	2026-03-17 00:20:15.662209+00	2026-03-17 00:20:15.662209+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	b640a678-296d-4066-a213-a69dc7a28848	PAY000008	2026-03-17	collection	active	edbabc2c-2e12-46e6-849b-c5190548315c	\N	\N	\N	???? ????? ?? ????? ????? BK000008	3ca7e7b2-b7a9-4d13-a9b8-aaaa0182c7fd	2026-03-17 00:22:43.010078+00	2026-03-17 00:22:43.010078+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	b640a678-296d-4066-a213-a69dc7a28848	PAY000009	2026-03-18	collection	active	32defaff-4d2c-4518-b21a-8db3ca6067ba	\N	\N	\N	Playwright smoke allocation	906e97d5-5c07-457e-abc9-3c7efac43ae9	2026-03-17 00:22:43.314169+00	2026-03-17 00:22:43.314169+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	95099d1d-f29f-491a-b82e-a0cc4177a149	PAY000010	2026-03-17	collection	active	289b0b29-2dbe-43b1-8fea-67e0333dcc16	\N	\N	\N	???? ????? ?? ????? ????? BK000010	bb203f17-3346-4c92-9364-b22468baafc6	2026-03-17 00:24:00.775978+00	2026-03-17 00:24:00.775978+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	95099d1d-f29f-491a-b82e-a0cc4177a149	PAY000011	2026-03-18	collection	active	06059536-188d-4377-ae32-c39134f1a3a3	\N	\N	\N	Playwright smoke allocation	af5c3d7e-f057-4cfb-9ca0-0c587a8cbf70	2026-03-17 00:24:01.049193+00	2026-03-17 00:24:01.049193+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	569b0220-d940-4f21-9890-50e05c5bcd7b	PAY000012	2026-03-17	collection	active	c04b1cd3-3fd8-4b1c-9343-e7d011a77399	\N	\N	\N	???? ????? ?? ????? ????? BK000012	e31adbec-74ee-42ad-bc49-55ca87c733e8	2026-03-17 01:07:26.98646+00	2026-03-17 01:07:26.98646+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	569b0220-d940-4f21-9890-50e05c5bcd7b	PAY000013	2026-03-18	collection	active	125fb589-11d3-495d-b784-bb0b96feaf20	\N	\N	\N	Playwright smoke allocation	11a8759d-8fe3-480c-9189-c26ac40a7de1	2026-03-17 01:07:27.30599+00	2026-03-17 01:07:27.30599+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	e1990ef4-cba7-4c12-860a-7c0b9a5e771b	PAY000014	2026-03-17	collection	active	6f9fa24a-2793-4842-b400-9dc05a6e2653	\N	\N	\N	???? ????? ?? ????? ????? BK000014	2235082e-7763-4562-bfef-16a5a4f39af3	2026-03-17 01:08:50.820724+00	2026-03-17 01:08:50.820724+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	e1990ef4-cba7-4c12-860a-7c0b9a5e771b	PAY000015	2026-03-18	collection	active	781465cf-312a-40e9-aa2d-7d406519317f	\N	\N	\N	Playwright smoke allocation	ba95e7a6-570d-4040-9831-c4de8dbad623	2026-03-17 01:08:51.068593+00	2026-03-17 01:08:51.068593+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	87557f7b-4350-4c47-8434-ea9bda30ff22	PAY000016	2026-03-17	collection	active	adea8eb6-431c-421c-a1de-d79dfdf9e392	\N	\N	\N	???? ????? ?? ????? ????? BK000016	d3e92c90-7a9c-44c1-a035-07e195d0dbe1	2026-03-17 01:10:14.228646+00	2026-03-17 01:10:14.228646+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	87557f7b-4350-4c47-8434-ea9bda30ff22	PAY000017	2026-03-18	collection	active	3724ce70-9815-4497-927c-bdf5e750d596	\N	\N	\N	Playwright smoke allocation	12f9bc55-3693-421c-8874-b6abafc4f180	2026-03-17 01:10:14.602044+00	2026-03-17 01:10:14.602044+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	975312e9-5b60-40ce-ae21-cf4ed1342061	PAY000018	2026-03-17	collection	active	91e036e4-dd8e-4959-98be-7790c7e72558	\N	\N	\N	???? ????? ?? ????? ????? BK000018	a9f6b333-876b-44d4-854f-cbde3c5b1270	2026-03-17 01:11:21.128803+00	2026-03-17 01:11:21.128803+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	df7fc2ef-5359-4aeb-9183-aa1c37dda322	975312e9-5b60-40ce-ae21-cf4ed1342061	PAY000019	2026-03-18	collection	active	1870fb02-647b-4078-977f-5b240210f236	\N	\N	\N	Playwright smoke allocation	d72b1004-173e-4f1a-a2a2-2e1084850975	2026-03-17 01:11:21.451039+00	2026-03-17 01:11:21.451039+00
\.


--
-- Data for Name: payment_receipts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payment_receipts (company_id, payment_number, booking_id, payment_date, payment_type, amount, remaining_after, notes, id, created_at, updated_at, branch_id, journal_entry_id, status, voided_at, voided_by_user_id, void_reason) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	PAY000001	cb7e1e39-0ecc-4b12-baa1-7a4a898c3d0a	2026-06-15	deposit	1200.00	1800.00	???? ???? ??	ab646c6d-b70e-4ab8-a686-582c1a2234b0	2026-03-16 02:46:14.243758+00	2026-03-16 02:46:14.243758+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	548dde2a-f7ed-4b86-87ef-544f529d0912	active	\N	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	PAY000002	80384f11-9127-4c38-abae-1d991b12c7b1	2026-03-16	deposit	1000.00	1500.00	\N	99ae3b83-0d36-448f-bfb0-c310db5cb7c2	2026-03-16 18:40:59.671978+00	2026-03-16 18:40:59.671978+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	36acb4c2-8d63-46c1-8ef2-4abae7112c63	active	\N	\N	\N
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	PAY000003	09fdb729-07b3-4454-ac97-a4da673096ca	2026-03-16	deposit	1000.00	1500.00	\N	b5b06b2e-1012-4442-8b4f-b5f3d581aa07	2026-03-16 18:41:45.345328+00	2026-03-16 18:41:45.345328+00	df7fc2ef-5359-4aeb-9183-aa1c37dda322	5fef3233-2feb-4437-b745-f8dc8ecc45cd	active	\N	\N	\N
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.permissions (key, description, id, created_at, updated_at) FROM stdin;
users.manage	Manage all users and roles	8c0885d1-6027-4c30-927f-df1b5860c34d	2026-03-14 04:11:52.720884+00	2026-03-14 04:11:52.720884+00
users.self_manage	Manage own profile	c64894bc-2efd-45cd-b1db-2d7572c04fe2	2026-03-14 04:11:52.720884+00	2026-03-14 04:11:52.720884+00
settings.manage	Manage settings and backups	d6c370b4-cd2f-426c-81a4-56d1a1a6b940	2026-03-14 04:11:52.720884+00	2026-03-14 04:11:52.720884+00
accounting.view	View accounting foundation data	17b2ee0e-a02e-4964-8c08-4e15d5c3b0f6	2026-03-15 21:30:30.211627+00	2026-03-15 21:30:30.211627+00
accounting.manage	Create, post, and reverse journal entries	9214fe36-d3e4-42a7-aa47-ac504229953b	2026-03-15 21:41:44.339685+00	2026-03-15 21:41:44.339685+00
customers.view	View customers list and details	ef2187d6-2052-4e85-89e0-3d49ec94d616	2026-03-15 22:29:26.52126+00	2026-03-15 22:29:26.52126+00
customers.manage	Create and update customers	b4ab7cda-a458-457f-9a0a-990e97a94dbb	2026-03-15 22:29:26.52126+00	2026-03-15 22:29:26.52126+00
catalog.view	View departments and services catalog	0380542f-3839-41de-94da-3a59b4dbd573	2026-03-15 22:51:45.055428+00	2026-03-15 22:51:45.055428+00
catalog.manage	Create and update departments and services	585b8013-43ea-49d1-a8c8-46c149088ddc	2026-03-15 22:51:45.055428+00	2026-03-15 22:51:45.055428+00
dresses.view	View dress resources	9635ba37-7ba5-4319-b95c-f25373899285	2026-03-15 23:06:19.615963+00	2026-03-15 23:06:19.615963+00
dresses.manage	Create and update dress resources	81e36137-d764-46bd-979e-099707a3b195	2026-03-15 23:06:19.615963+00	2026-03-15 23:06:19.615963+00
bookings.view	View bookings	38b4172e-916f-45b1-ab61-847d390664b2	2026-03-15 23:16:29.710726+00	2026-03-15 23:16:29.710726+00
bookings.manage	Create and update bookings	847fc347-42e7-4af7-bf91-48c939d369f4	2026-03-15 23:16:29.710726+00	2026-03-15 23:16:29.710726+00
payments.view	View payments	68b90156-348f-488d-838e-4fed9cc1f84e	2026-03-15 23:26:41.037582+00	2026-03-15 23:26:41.037582+00
payments.manage	Create and update payments	4eece6fa-9dda-4a98-a559-13b207aa0067	2026-03-15 23:26:41.037582+00	2026-03-15 23:26:41.037582+00
finance.view	View finance dashboard metrics	344531ef-8f8a-44ef-80d0-89181bf6a657	2026-03-15 23:57:04.707593+00	2026-03-15 23:57:04.707593+00
reports.view	View broader operational reports	637cadcd-9176-475b-aa9c-069497676429	2026-03-16 00:16:06.461939+00	2026-03-16 00:16:06.461939+00
exports.view	Download CSV exports	f822c2b9-0dee-4c01-98b9-db86b09fab6b	2026-03-16 03:02:31.297476+00	2026-03-16 03:02:31.297476+00
exports.manage	Manage saved export schedules	fb30ae97-404e-4978-9b15-158362b00be5	2026-03-16 18:21:08.93233+00	2026-03-16 18:21:08.93233+00
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.role_permissions (role_id, permission_id) FROM stdin;
dcc276f2-105b-437a-8491-a32138ccc29a	8c0885d1-6027-4c30-927f-df1b5860c34d
dcc276f2-105b-437a-8491-a32138ccc29a	c64894bc-2efd-45cd-b1db-2d7572c04fe2
dcc276f2-105b-437a-8491-a32138ccc29a	d6c370b4-cd2f-426c-81a4-56d1a1a6b940
524d765e-3c74-4d2f-9c55-7005cbb3de77	d6c370b4-cd2f-426c-81a4-56d1a1a6b940
524d765e-3c74-4d2f-9c55-7005cbb3de77	c64894bc-2efd-45cd-b1db-2d7572c04fe2
dcc276f2-105b-437a-8491-a32138ccc29a	17b2ee0e-a02e-4964-8c08-4e15d5c3b0f6
524d765e-3c74-4d2f-9c55-7005cbb3de77	17b2ee0e-a02e-4964-8c08-4e15d5c3b0f6
dcc276f2-105b-437a-8491-a32138ccc29a	9214fe36-d3e4-42a7-aa47-ac504229953b
dcc276f2-105b-437a-8491-a32138ccc29a	ef2187d6-2052-4e85-89e0-3d49ec94d616
524d765e-3c74-4d2f-9c55-7005cbb3de77	ef2187d6-2052-4e85-89e0-3d49ec94d616
dcc276f2-105b-437a-8491-a32138ccc29a	b4ab7cda-a458-457f-9a0a-990e97a94dbb
524d765e-3c74-4d2f-9c55-7005cbb3de77	b4ab7cda-a458-457f-9a0a-990e97a94dbb
dcc276f2-105b-437a-8491-a32138ccc29a	585b8013-43ea-49d1-a8c8-46c149088ddc
524d765e-3c74-4d2f-9c55-7005cbb3de77	585b8013-43ea-49d1-a8c8-46c149088ddc
dcc276f2-105b-437a-8491-a32138ccc29a	0380542f-3839-41de-94da-3a59b4dbd573
524d765e-3c74-4d2f-9c55-7005cbb3de77	0380542f-3839-41de-94da-3a59b4dbd573
dcc276f2-105b-437a-8491-a32138ccc29a	81e36137-d764-46bd-979e-099707a3b195
524d765e-3c74-4d2f-9c55-7005cbb3de77	81e36137-d764-46bd-979e-099707a3b195
dcc276f2-105b-437a-8491-a32138ccc29a	9635ba37-7ba5-4319-b95c-f25373899285
524d765e-3c74-4d2f-9c55-7005cbb3de77	9635ba37-7ba5-4319-b95c-f25373899285
dcc276f2-105b-437a-8491-a32138ccc29a	38b4172e-916f-45b1-ab61-847d390664b2
524d765e-3c74-4d2f-9c55-7005cbb3de77	38b4172e-916f-45b1-ab61-847d390664b2
dcc276f2-105b-437a-8491-a32138ccc29a	847fc347-42e7-4af7-bf91-48c939d369f4
524d765e-3c74-4d2f-9c55-7005cbb3de77	847fc347-42e7-4af7-bf91-48c939d369f4
dcc276f2-105b-437a-8491-a32138ccc29a	68b90156-348f-488d-838e-4fed9cc1f84e
524d765e-3c74-4d2f-9c55-7005cbb3de77	68b90156-348f-488d-838e-4fed9cc1f84e
dcc276f2-105b-437a-8491-a32138ccc29a	4eece6fa-9dda-4a98-a559-13b207aa0067
524d765e-3c74-4d2f-9c55-7005cbb3de77	4eece6fa-9dda-4a98-a559-13b207aa0067
dcc276f2-105b-437a-8491-a32138ccc29a	344531ef-8f8a-44ef-80d0-89181bf6a657
524d765e-3c74-4d2f-9c55-7005cbb3de77	344531ef-8f8a-44ef-80d0-89181bf6a657
dcc276f2-105b-437a-8491-a32138ccc29a	637cadcd-9176-475b-aa9c-069497676429
524d765e-3c74-4d2f-9c55-7005cbb3de77	637cadcd-9176-475b-aa9c-069497676429
dcc276f2-105b-437a-8491-a32138ccc29a	f822c2b9-0dee-4c01-98b9-db86b09fab6b
dcc276f2-105b-437a-8491-a32138ccc29a	fb30ae97-404e-4978-9b15-158362b00be5
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.roles (name, description, id, created_at, updated_at) FROM stdin;
admin	System role: admin	dcc276f2-105b-437a-8491-a32138ccc29a	2026-03-14 04:11:52.720884+00	2026-03-14 04:11:52.720884+00
user	System role: user	524d765e-3c74-4d2f-9c55-7005cbb3de77	2026-03-14 04:11:52.720884+00	2026-03-14 04:11:52.720884+00
\.


--
-- Data for Name: service_catalog_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.service_catalog_items (company_id, department_id, name, default_price, duration_minutes, notes, is_active, id, created_at, updated_at) FROM stdin;
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	e572c53b-86eb-44cd-8281-edb93c9e4530	???? ???? 1773629038	1800.00	90	\N	t	26785f9f-204b-462e-a5e2-05d1348c5915	2026-03-16 02:43:58.882473+00	2026-03-16 02:43:58.882473+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	15549c36-4470-4562-8755-e447e35c6a78	???? 1773629173	1800.00	90	\N	t	4b70e297-f7db-46b8-ac49-31cb9ca8deec	2026-03-16 02:46:14.084143+00	2026-03-16 02:46:14.084143+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	e29df0af-a599-475a-b3ae-869f6aee8090	???? ?????? 204059	2500.00	\N	\N	t	85b408d0-9ee2-416c-8c56-3825b1eb14d5	2026-03-16 18:40:59.476793+00	2026-03-16 18:40:59.476793+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	15c625ee-454a-4b87-adcd-6a439a5f9566	???? ?????? 204145	2500.00	\N	\N	t	120b20f9-f68a-4143-b6eb-bd6b241f6900	2026-03-16 18:41:45.174445+00	2026-03-16 18:41:45.174445+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	77138a2b-1407-4cf2-9d06-3b0690dae582	Service 06789	700.00	\N	\N	t	b3639f58-1408-49ad-82ea-2f096a52774d	2026-03-17 00:08:27.241938+00	2026-03-17 00:08:27.241938+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	820bdc06-5317-459f-96b2-eb9d6946e39d	Service 58582	700.00	\N	\N	t	2e3c9dc0-c96a-4753-b1b8-04c89d8b37a9	2026-03-17 00:12:38.868554+00	2026-03-17 00:12:38.868554+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	47c96b72-97d5-403e-945f-dac0b55229e9	Service 14824	700.00	\N	\N	t	f1c8f9b3-d35c-4aba-8033-a44dbbe31db0	2026-03-17 00:20:15.039225+00	2026-03-17 00:20:15.039225+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	88c7ccee-eaf0-4af0-9b46-631d9003ece0	Service 62620	700.00	\N	\N	t	702f2ab2-d969-4fe1-b1eb-74b0fde637f3	2026-03-17 00:22:42.853813+00	2026-03-17 00:22:42.853813+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	c1fc18e5-a7c1-499f-ae46-f44116fa56d4	Service 40360	700.00	\N	\N	t	383e1b0b-f862-482d-83bb-538230c8b06b	2026-03-17 00:24:00.604578+00	2026-03-17 00:24:00.604578+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	526e6e04-fd5a-42bf-9bdd-a8f0e919c51b	Service 45589	700.00	\N	\N	t	dedd0d0e-9fb9-4ccc-b185-0f09ee423c06	2026-03-17 01:07:26.781816+00	2026-03-17 01:07:26.781816+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	9199284d-b0a4-4c80-96ac-77d030300589	Service 30441	700.00	\N	\N	t	59938760-badc-42ce-9f51-f07380e0a547	2026-03-17 01:08:50.615332+00	2026-03-17 01:08:50.615332+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	acfaf8ef-e8cd-4a33-a89b-9c3d6ece3be2	Service 13793	700.00	\N	\N	t	4ea778d8-e91b-4fa7-b69c-987c6c100639	2026-03-17 01:10:14.082918+00	2026-03-17 01:10:14.082918+00
4802cb59-a0b4-4388-9edc-2fbcd1ec82ae	3e4dbc64-7430-4493-bb76-49bf773fef7f	Service 80588	700.00	\N	\N	t	8d4c7a82-3f78-438a-96c7-5ad8ac5af99f	2026-03-17 01:11:20.894393+00	2026-03-17 01:11:20.894393+00
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_roles (user_id, role_id) FROM stdin;
6307835d-b313-404a-a23b-ab033854f2cb	dcc276f2-105b-437a-8491-a32138ccc29a
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (username, full_name, password_hash, is_active, last_login_at, id, created_at, updated_at) FROM stdin;
admin	Administrator	pbkdf2_sha256$260000$Ye7bZCY7JIBynxkatMt2kw==$fc/4GPqiytI+magLNcbH7f/IJB4EJxHU5L2oJUl4eK4=	t	2026-03-17 02:19:57.477035+00	6307835d-b313-404a-a23b-ab033854f2cb	2026-03-14 04:11:52.720884+00	2026-03-17 02:19:57.339073+00
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: app_settings pk_app_settings; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_settings
    ADD CONSTRAINT pk_app_settings PRIMARY KEY (key);


--
-- Name: audit_logs pk_audit_logs; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT pk_audit_logs PRIMARY KEY (id);


--
-- Name: backup_records pk_backup_records; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backup_records
    ADD CONSTRAINT pk_backup_records PRIMARY KEY (id);


--
-- Name: booking_lines pk_booking_lines; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.booking_lines
    ADD CONSTRAINT pk_booking_lines PRIMARY KEY (id);


--
-- Name: bookings pk_bookings; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT pk_bookings PRIMARY KEY (id);


--
-- Name: branches pk_branches; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT pk_branches PRIMARY KEY (id);


--
-- Name: chart_of_accounts pk_chart_of_accounts; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT pk_chart_of_accounts PRIMARY KEY (id);


--
-- Name: companies pk_companies; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT pk_companies PRIMARY KEY (id);


--
-- Name: customers pk_customers; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT pk_customers PRIMARY KEY (id);


--
-- Name: departments pk_departments; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT pk_departments PRIMARY KEY (id);


--
-- Name: document_sequences pk_document_sequences; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_sequences
    ADD CONSTRAINT pk_document_sequences PRIMARY KEY (id);


--
-- Name: dress_resources pk_dress_resources; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dress_resources
    ADD CONSTRAINT pk_dress_resources PRIMARY KEY (id);


--
-- Name: export_schedules pk_export_schedules; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.export_schedules
    ADD CONSTRAINT pk_export_schedules PRIMARY KEY (id);


--
-- Name: fiscal_periods pk_fiscal_periods; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fiscal_periods
    ADD CONSTRAINT pk_fiscal_periods PRIMARY KEY (id);


--
-- Name: journal_entries pk_journal_entries; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT pk_journal_entries PRIMARY KEY (id);


--
-- Name: journal_entry_lines pk_journal_entry_lines; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entry_lines
    ADD CONSTRAINT pk_journal_entry_lines PRIMARY KEY (id);


--
-- Name: payment_allocations pk_payment_allocations; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_allocations
    ADD CONSTRAINT pk_payment_allocations PRIMARY KEY (id);


--
-- Name: payment_documents pk_payment_documents; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_documents
    ADD CONSTRAINT pk_payment_documents PRIMARY KEY (id);


--
-- Name: payment_receipts pk_payment_receipts; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_receipts
    ADD CONSTRAINT pk_payment_receipts PRIMARY KEY (id);


--
-- Name: permissions pk_permissions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT pk_permissions PRIMARY KEY (id);


--
-- Name: role_permissions pk_role_permissions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT pk_role_permissions PRIMARY KEY (role_id, permission_id);


--
-- Name: roles pk_roles; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT pk_roles PRIMARY KEY (id);


--
-- Name: service_catalog_items pk_service_catalog_items; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_catalog_items
    ADD CONSTRAINT pk_service_catalog_items PRIMARY KEY (id);


--
-- Name: user_roles pk_user_roles; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT pk_user_roles PRIMARY KEY (user_id, role_id);


--
-- Name: users pk_users; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT pk_users PRIMARY KEY (id);


--
-- Name: booking_lines uq_booking_lines_booking_line_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.booking_lines
    ADD CONSTRAINT uq_booking_lines_booking_line_number UNIQUE (booking_id, line_number);


--
-- Name: bookings uq_bookings_company_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT uq_bookings_company_number UNIQUE (company_id, booking_number);


--
-- Name: branches uq_branches_company_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT uq_branches_company_code UNIQUE (company_id, code);


--
-- Name: chart_of_accounts uq_chart_of_accounts_company_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT uq_chart_of_accounts_company_code UNIQUE (company_id, code);


--
-- Name: customers uq_customers_company_phone; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT uq_customers_company_phone UNIQUE (company_id, phone);


--
-- Name: departments uq_departments_company_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT uq_departments_company_code UNIQUE (company_id, code);


--
-- Name: document_sequences uq_document_sequences_company_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_sequences
    ADD CONSTRAINT uq_document_sequences_company_key UNIQUE (company_id, key);


--
-- Name: dress_resources uq_dress_resources_company_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dress_resources
    ADD CONSTRAINT uq_dress_resources_company_code UNIQUE (company_id, code);


--
-- Name: journal_entries uq_journal_entries_company_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT uq_journal_entries_company_number UNIQUE (company_id, entry_number);


--
-- Name: journal_entry_lines uq_journal_entry_lines_entry_line_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entry_lines
    ADD CONSTRAINT uq_journal_entry_lines_entry_line_number UNIQUE (journal_entry_id, line_number);


--
-- Name: payment_allocations uq_payment_allocations_document_line_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_allocations
    ADD CONSTRAINT uq_payment_allocations_document_line_number UNIQUE (payment_document_id, line_number);


--
-- Name: payment_documents uq_payment_documents_company_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_documents
    ADD CONSTRAINT uq_payment_documents_company_number UNIQUE (company_id, payment_number);


--
-- Name: payment_receipts uq_payment_receipts_company_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_receipts
    ADD CONSTRAINT uq_payment_receipts_company_number UNIQUE (company_id, payment_number);


--
-- Name: permissions uq_permissions_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT uq_permissions_key UNIQUE (key);


--
-- Name: roles uq_roles_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT uq_roles_name UNIQUE (name);


--
-- Name: service_catalog_items uq_service_catalog_company_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_catalog_items
    ADD CONSTRAINT uq_service_catalog_company_name UNIQUE (company_id, name);


--
-- Name: users uq_users_username; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uq_users_username UNIQUE (username);


--
-- Name: ix_booking_lines_booking_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_booking_lines_booking_id ON public.booking_lines USING btree (booking_id);


--
-- Name: ix_booking_lines_dress_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_booking_lines_dress_id ON public.booking_lines USING btree (dress_id);


--
-- Name: ix_booking_lines_service_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_booking_lines_service_date ON public.booking_lines USING btree (service_date);


--
-- Name: ix_bookings_branch_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bookings_branch_id ON public.bookings USING btree (branch_id);


--
-- Name: ix_bookings_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bookings_company_id ON public.bookings USING btree (company_id);


--
-- Name: ix_bookings_customer_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bookings_customer_id ON public.bookings USING btree (customer_id);


--
-- Name: ix_bookings_event_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bookings_event_date ON public.bookings USING btree (event_date);


--
-- Name: ix_bookings_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bookings_status ON public.bookings USING btree (status);


--
-- Name: ix_customers_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_customers_company_id ON public.customers USING btree (company_id);


--
-- Name: ix_customers_full_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_customers_full_name ON public.customers USING btree (full_name);


--
-- Name: ix_customers_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_customers_phone ON public.customers USING btree (phone);


--
-- Name: ix_departments_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_departments_company_id ON public.departments USING btree (company_id);


--
-- Name: ix_departments_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_departments_name ON public.departments USING btree (name);


--
-- Name: ix_dress_resources_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_dress_resources_code ON public.dress_resources USING btree (code);


--
-- Name: ix_dress_resources_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_dress_resources_company_id ON public.dress_resources USING btree (company_id);


--
-- Name: ix_dress_resources_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_dress_resources_status ON public.dress_resources USING btree (status);


--
-- Name: ix_export_schedules_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_export_schedules_company_id ON public.export_schedules USING btree (company_id);


--
-- Name: ix_export_schedules_next_run_on; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_export_schedules_next_run_on ON public.export_schedules USING btree (next_run_on);


--
-- Name: ix_payment_allocations_booking_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_allocations_booking_id ON public.payment_allocations USING btree (booking_id);


--
-- Name: ix_payment_allocations_booking_line_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_allocations_booking_line_id ON public.payment_allocations USING btree (booking_line_id);


--
-- Name: ix_payment_allocations_payment_document_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_allocations_payment_document_id ON public.payment_allocations USING btree (payment_document_id);


--
-- Name: ix_payment_documents_branch_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_documents_branch_id ON public.payment_documents USING btree (branch_id);


--
-- Name: ix_payment_documents_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_documents_company_id ON public.payment_documents USING btree (company_id);


--
-- Name: ix_payment_documents_customer_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_documents_customer_id ON public.payment_documents USING btree (customer_id);


--
-- Name: ix_payment_documents_payment_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_documents_payment_date ON public.payment_documents USING btree (payment_date);


--
-- Name: ix_payment_receipts_booking_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_receipts_booking_id ON public.payment_receipts USING btree (booking_id);


--
-- Name: ix_payment_receipts_branch_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_receipts_branch_id ON public.payment_receipts USING btree (branch_id);


--
-- Name: ix_payment_receipts_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_receipts_company_id ON public.payment_receipts USING btree (company_id);


--
-- Name: ix_payment_receipts_journal_entry_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_receipts_journal_entry_id ON public.payment_receipts USING btree (journal_entry_id);


--
-- Name: ix_payment_receipts_payment_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_receipts_payment_date ON public.payment_receipts USING btree (payment_date);


--
-- Name: ix_service_catalog_company_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_service_catalog_company_id ON public.service_catalog_items USING btree (company_id);


--
-- Name: ix_service_catalog_department_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_service_catalog_department_id ON public.service_catalog_items USING btree (department_id);


--
-- Name: ix_service_catalog_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_service_catalog_name ON public.service_catalog_items USING btree (name);


--
-- Name: audit_logs fk_audit_logs_actor_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT fk_audit_logs_actor_user_id_users FOREIGN KEY (actor_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: backup_records fk_backup_records_created_by_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backup_records
    ADD CONSTRAINT fk_backup_records_created_by_user_id_users FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: booking_lines fk_booking_lines_booking_id_bookings; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.booking_lines
    ADD CONSTRAINT fk_booking_lines_booking_id_bookings FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: booking_lines fk_booking_lines_department_id_departments; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.booking_lines
    ADD CONSTRAINT fk_booking_lines_department_id_departments FOREIGN KEY (department_id) REFERENCES public.departments(id) ON DELETE RESTRICT;


--
-- Name: booking_lines fk_booking_lines_dress_id_dress_resources; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.booking_lines
    ADD CONSTRAINT fk_booking_lines_dress_id_dress_resources FOREIGN KEY (dress_id) REFERENCES public.dress_resources(id) ON DELETE SET NULL;


--
-- Name: booking_lines fk_booking_lines_revenue_journal_entry_id_journal_entries; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.booking_lines
    ADD CONSTRAINT fk_booking_lines_revenue_journal_entry_id_journal_entries FOREIGN KEY (revenue_journal_entry_id) REFERENCES public.journal_entries(id) ON DELETE SET NULL;


--
-- Name: booking_lines fk_booking_lines_service_id_service_catalog_items; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.booking_lines
    ADD CONSTRAINT fk_booking_lines_service_id_service_catalog_items FOREIGN KEY (service_id) REFERENCES public.service_catalog_items(id) ON DELETE RESTRICT;


--
-- Name: bookings fk_bookings_branch_id_branches; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_branch_id_branches FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE RESTRICT;


--
-- Name: bookings fk_bookings_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: bookings fk_bookings_customer_id_customers; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_customer_id_customers FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE RESTRICT;


--
-- Name: bookings fk_bookings_dress_id_dress_resources; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_dress_id_dress_resources FOREIGN KEY (dress_id) REFERENCES public.dress_resources(id) ON DELETE SET NULL;


--
-- Name: bookings fk_bookings_revenue_journal_entry; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_revenue_journal_entry FOREIGN KEY (revenue_journal_entry_id) REFERENCES public.journal_entries(id) ON DELETE SET NULL;


--
-- Name: bookings fk_bookings_service_id_service_catalog_items; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_service_id_service_catalog_items FOREIGN KEY (service_id) REFERENCES public.service_catalog_items(id) ON DELETE RESTRICT;


--
-- Name: branches fk_branches_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT fk_branches_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: chart_of_accounts fk_chart_of_accounts_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT fk_chart_of_accounts_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: chart_of_accounts fk_chart_of_accounts_parent_account_id_chart_of_accounts; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT fk_chart_of_accounts_parent_account_id_chart_of_accounts FOREIGN KEY (parent_account_id) REFERENCES public.chart_of_accounts(id) ON DELETE SET NULL;


--
-- Name: customers fk_customers_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT fk_customers_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: departments fk_departments_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT fk_departments_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: document_sequences fk_document_sequences_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_sequences
    ADD CONSTRAINT fk_document_sequences_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: dress_resources fk_dress_resources_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dress_resources
    ADD CONSTRAINT fk_dress_resources_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: export_schedules fk_export_schedules_branch_id_branches; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.export_schedules
    ADD CONSTRAINT fk_export_schedules_branch_id_branches FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE SET NULL;


--
-- Name: export_schedules fk_export_schedules_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.export_schedules
    ADD CONSTRAINT fk_export_schedules_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: fiscal_periods fk_fiscal_periods_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fiscal_periods
    ADD CONSTRAINT fk_fiscal_periods_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: journal_entries fk_journal_entries_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT fk_journal_entries_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: journal_entries fk_journal_entries_fiscal_period_id_fiscal_periods; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT fk_journal_entries_fiscal_period_id_fiscal_periods FOREIGN KEY (fiscal_period_id) REFERENCES public.fiscal_periods(id) ON DELETE RESTRICT;


--
-- Name: journal_entries fk_journal_entries_posted_by_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT fk_journal_entries_posted_by_user_id_users FOREIGN KEY (posted_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: journal_entries fk_journal_entries_reversed_by_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT fk_journal_entries_reversed_by_user_id_users FOREIGN KEY (reversed_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: journal_entry_lines fk_journal_entry_lines_account_id_chart_of_accounts; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entry_lines
    ADD CONSTRAINT fk_journal_entry_lines_account_id_chart_of_accounts FOREIGN KEY (account_id) REFERENCES public.chart_of_accounts(id) ON DELETE RESTRICT;


--
-- Name: journal_entry_lines fk_journal_entry_lines_journal_entry_id_journal_entries; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.journal_entry_lines
    ADD CONSTRAINT fk_journal_entry_lines_journal_entry_id_journal_entries FOREIGN KEY (journal_entry_id) REFERENCES public.journal_entries(id) ON DELETE CASCADE;


--
-- Name: payment_allocations fk_payment_allocations_booking_id_bookings; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_allocations
    ADD CONSTRAINT fk_payment_allocations_booking_id_bookings FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE RESTRICT;


--
-- Name: payment_allocations fk_payment_allocations_booking_line_id_booking_lines; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_allocations
    ADD CONSTRAINT fk_payment_allocations_booking_line_id_booking_lines FOREIGN KEY (booking_line_id) REFERENCES public.booking_lines(id) ON DELETE RESTRICT;


--
-- Name: payment_allocations fk_payment_allocations_payment_document_id_payment_documents; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_allocations
    ADD CONSTRAINT fk_payment_allocations_payment_document_id_payment_documents FOREIGN KEY (payment_document_id) REFERENCES public.payment_documents(id) ON DELETE CASCADE;


--
-- Name: payment_documents fk_payment_documents_branch_id_branches; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_documents
    ADD CONSTRAINT fk_payment_documents_branch_id_branches FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE RESTRICT;


--
-- Name: payment_documents fk_payment_documents_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_documents
    ADD CONSTRAINT fk_payment_documents_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: payment_documents fk_payment_documents_customer_id_customers; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_documents
    ADD CONSTRAINT fk_payment_documents_customer_id_customers FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE RESTRICT;


--
-- Name: payment_documents fk_payment_documents_journal_entry_id_journal_entries; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_documents
    ADD CONSTRAINT fk_payment_documents_journal_entry_id_journal_entries FOREIGN KEY (journal_entry_id) REFERENCES public.journal_entries(id) ON DELETE SET NULL;


--
-- Name: payment_documents fk_payment_documents_voided_by_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_documents
    ADD CONSTRAINT fk_payment_documents_voided_by_user_id_users FOREIGN KEY (voided_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: payment_receipts fk_payment_receipts_booking_id_bookings; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_receipts
    ADD CONSTRAINT fk_payment_receipts_booking_id_bookings FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE RESTRICT;


--
-- Name: payment_receipts fk_payment_receipts_branch_id_branches; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_receipts
    ADD CONSTRAINT fk_payment_receipts_branch_id_branches FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE RESTRICT;


--
-- Name: payment_receipts fk_payment_receipts_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_receipts
    ADD CONSTRAINT fk_payment_receipts_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: payment_receipts fk_payment_receipts_journal_entry_id_journal_entries; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_receipts
    ADD CONSTRAINT fk_payment_receipts_journal_entry_id_journal_entries FOREIGN KEY (journal_entry_id) REFERENCES public.journal_entries(id) ON DELETE SET NULL;


--
-- Name: payment_receipts fk_payment_receipts_voided_by_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_receipts
    ADD CONSTRAINT fk_payment_receipts_voided_by_user_id_users FOREIGN KEY (voided_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: role_permissions fk_role_permissions_permission_id_permissions; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT fk_role_permissions_permission_id_permissions FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions fk_role_permissions_role_id_roles; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT fk_role_permissions_role_id_roles FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: service_catalog_items fk_service_catalog_items_company_id_companies; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_catalog_items
    ADD CONSTRAINT fk_service_catalog_items_company_id_companies FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: service_catalog_items fk_service_catalog_items_department_id_departments; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_catalog_items
    ADD CONSTRAINT fk_service_catalog_items_department_id_departments FOREIGN KEY (department_id) REFERENCES public.departments(id) ON DELETE RESTRICT;


--
-- Name: user_roles fk_user_roles_role_id_roles; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT fk_user_roles_role_id_roles FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles fk_user_roles_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT fk_user_roles_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict Ur7Yy377c6gXTJKBxXmBFzbQDahJXsf297pCACBgKeUON4GaAx2rbzfgB4fdscg

