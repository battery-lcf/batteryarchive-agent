-- DROP SCHEMA public;

-- CREATE SCHEMA public AUTHORIZATION postgres;

-- DROP SEQUENCE public.abuse_metadata_index_seq;

CREATE SEQUENCE public.abuse_metadata_index_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.abuse_timeseries_index_seq;

CREATE SEQUENCE public.abuse_timeseries_index_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.cell_metadata_index_seq;

CREATE SEQUENCE public.cell_metadata_index_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.cycle_metadata_index_seq;

CREATE SEQUENCE public.cycle_metadata_index_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.cycle_stats_index_seq;

CREATE SEQUENCE public.cycle_stats_index_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.cycle_timeseries_buffer_index_seq;

CREATE SEQUENCE public.cycle_timeseries_buffer_index_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.cycle_timeseries_index_seq;

CREATE SEQUENCE public.cycle_timeseries_index_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;-- public.abuse_metadata definition

-- Drop table

-- DROP TABLE public.abuse_metadata;

CREATE TABLE public.abuse_metadata (
	"index" serial4 NOT NULL,
	cell_id text NOT NULL,
	temperature float8 NULL,
	thickness float8 NULL,
	v_init float8 NULL,
	indentor float8 NULL,
	nail_speed float8 NULL,
	soc float8 NULL,
	CONSTRAINT abuse_metadata_pkey PRIMARY KEY (index)
);


-- public.abuse_timeseries definition

-- Drop table

-- DROP TABLE public.abuse_timeseries;

CREATE TABLE public.abuse_timeseries (
	"index" serial4 NOT NULL,
	axial_d float8 NULL,
	axial_f float8 NULL,
	v float8 NULL,
	norm_d float8 NULL,
	strain float8 NULL,
	top_indent_temperature float8 NULL,
	top_back_temperature float8 NULL,
	left_bottom_temperature float8 NULL,
	right_bottom_temperature float8 NULL,
	above_punch_temperature float8 NULL,
	below_punch_temperature float8 NULL,
	test_time float8 NULL,
	cell_id text NOT NULL,
	ambient_temperature float8 NULL,
	"load" float8 NULL,
	CONSTRAINT abuse_timeseries_pkey PRIMARY KEY (index)
);


-- public.cell_metadata definition

-- Drop table

-- DROP TABLE public.cell_metadata;

CREATE TABLE public.cell_metadata (
	"index" serial4 NOT NULL,
	cell_id text NOT NULL,
	anode text NULL,
	cathode text NULL,
	"source" text NULL,
	ah int4 NULL,
	form_factor text NULL,
	test text NOT NULL,
	tester text NULL,
	status text NULL,
	weight text NULL,
	dimensions text NULL,
	CONSTRAINT cell_metadata_pkey PRIMARY KEY (index)
);


-- public.cycle_metadata definition

-- Drop table

-- DROP TABLE public.cycle_metadata;

CREATE TABLE public.cycle_metadata (
	"index" serial4 NOT NULL,
	temperature float8 NULL,
	soc_max float8 NULL,
	soc_min float8 NULL,
	v_max float8 NULL,
	v_min float8 NULL,
	crate_c float8 NULL,
	crate_d float8 NULL,
	cell_id text NOT NULL,
	step int4 NULL,
	CONSTRAINT cycle_metadata_pkey PRIMARY KEY (index)
);


-- public.cycle_stats definition

-- Drop table

-- DROP TABLE public.cycle_stats;

CREATE TABLE public.cycle_stats (
	"index" serial4 NOT NULL,
	v_max float8 NULL,
	v_min float8 NULL,
	ah_c float8 NULL,
	ah_d float8 NULL,
	e_c float8 NULL,
	e_d float8 NULL,
	i_max float8 NULL,
	i_min float8 NULL,
	v_c_mean float8 NULL,
	v_d_mean float8 NULL,
	e_eff float8 NULL,
	ah_eff float8 NULL,
	cycle_index int4 NULL,
	test_time float8 NOT NULL,
	cell_id text NOT NULL,
	CONSTRAINT cycle_stats_pkey PRIMARY KEY (index)
);


-- public.cycle_timeseries definition

-- Drop table

-- DROP TABLE public.cycle_timeseries;

CREATE TABLE public.cycle_timeseries (
	"index" serial4 NOT NULL,
	i float8 NULL,
	v float8 NULL,
	ah_c float8 NULL,
	ah_d float8 NULL,
	e_c float8 NULL,
	e_d float8 NULL,
	env_temperature float8 NULL,
	cell_temperature float8 NULL,
	cycle_time float8 NULL,
	date_time timestamp NULL,
	cycle_index int4 NOT NULL,
	test_time float8 NULL,
	cell_id text NOT NULL,
	CONSTRAINT cycle_timeseries_pkey PRIMARY KEY (index)
);


-- public.cycle_timeseries_buffer definition

-- Drop table

-- DROP TABLE public.cycle_timeseries_buffer;

CREATE TABLE public.cycle_timeseries_buffer (
	"index" serial4 NOT NULL,
	i float8 NULL,
	v float8 NULL,
	ah_c float8 NULL,
	ah_d float8 NULL,
	e_c float8 NULL,
	e_d float8 NULL,
	env_temperature float8 NULL,
	cell_temperature float8 NULL,
	cycle_time float8 NULL,
	date_time timestamp NULL,
	cycle_index int4 NOT NULL,
	test_time float8 NULL,
	cell_id text NOT NULL,
	sheetname text NULL,
	CONSTRAINT cycle_timeseries_buffer_pkey PRIMARY KEY (index)
);
