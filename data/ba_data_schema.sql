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

CREATE SEQUENCE public.flow_cell_metadata_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

CREATE SEQUENCE public.flow_cycle_metadata_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

CREATE SEQUENCE public.flow_cycle_stats_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

CREATE SEQUENCE public.flow_cycle_timeseries_buffer_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

CREATE SEQUENCE public.flow_cycle_timeseries_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

CREATE SEQUENCE public.module_metadata_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

CREATE SEQUENCE public.stack_metadata_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Drop table

-- DROP TABLE public.abuse_metadata;

CREATE TABLE IF NOT EXISTS public.abuse_metadata (
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

CREATE TABLE IF NOT EXISTS public.abuse_timeseries (
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

CREATE TABLE IF NOT EXISTS public.cell_metadata (
	"index" serial4 NOT NULL,
	cell_id text NOT NULL,
	parent_id text NULL,
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

CREATE TABLE IF NOT EXISTS public.cycle_metadata (
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

CREATE TABLE IF NOT EXISTS public.cycle_stats (
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
	component_level text NULL,
	CONSTRAINT cycle_stats_pkey PRIMARY KEY (index)
);


-- public.cycle_timeseries definition

-- Drop table

-- DROP TABLE public.cycle_timeseries;

CREATE TABLE IF NOT EXISTS public.cycle_timeseries (
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
	is_load_balanced boolean NULL,
	component_level text NULL,
	CONSTRAINT cycle_timeseries_pkey PRIMARY KEY (index)
);


-- public.cycle_timeseries_buffer definition

-- Drop table

-- DROP TABLE public.cycle_timeseries_buffer;

CREATE TABLE IF NOT EXISTS public.cycle_timeseries_buffer (
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
	is_load_balanced boolean NULL,
	component_level text NULL,
	CONSTRAINT cycle_timeseries_buffer_pkey PRIMARY KEY (index)
);



CREATE TABLE IF NOT EXISTS public.flow_cell_metadata (
	"index" serial4 NOT NULL,
	cell_id text UNIQUE NOT NULL,
	parent_id text UNIQUE NULL,
	flow_pattern text NULL, 
	NE_material text NULL, 
	PE_material text NULL, 
	membrane text NULL, 
	membrane_size float(4) NULL,
	NE_active text NULL, 
	initial_NE_active float(4) NULL,
	PE_active text NULL, 
	initial_PE_active float(4) NULL,
	NE_volume float(4) NULL, 
	PE_volume float(4) NULL, 
	flow_rate float(4) NULL,
	test_type text NULL,
	tester text NULL,
	test text NOT NULL,
	status text NULL,
	CONSTRAINT flow_cell_metadata_pkey PRIMARY KEY (index)
);

CREATE TABLE IF NOT EXISTS public.flow_cycle_metadata (
	"index" serial4 NOT NULL,
	cell_id text UNIQUE NOT NULL,
	soc_max float8 NULL,
	soc_min float8 NULL,
	crate_c float8 NULL,
	crate_d float8 NULL, 
	CONSTRAINT flow_cycle_metadata_pkey PRIMARY KEY (index)
);

CREATE TABLE IF NOT EXISTS public.flow_cycle_stats(
	"index" serial4 NOT NULL,
	v_max float8 NULL,
	v_min float8 NULL,
	ah_c float8 NULL,
	ah_d float8 NULL,
	e_c float8 NULL,
	e_c_cmltv float8 NULL,
	e_d float8 NULL,
	e_d_cmltv float8 NULL,
	i_max float8 NULL,
	i_min float8 NULL,
	v_c_mean float8 NULL,
	v_d_mean float8 NULL,
	e_eff float8 NULL,
	ah_eff float8 NULL,
	e_eff_cmltv float8 NULL,
	cycle_index int4 NULL,
	test_time float8 NOT NULL,
	cell_id text NOT NULL,
	component_level text NULL,
	CONSTRAINT flow_cycle_stats_pkey PRIMARY KEY (index)
);

CREATE TABLE IF NOT EXISTS public.flow_cycle_timeseries(
	"index" serial4 NOT NULL,
	i float8 NULL,
	v float8 NULL,
	w float8 NULL,
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
	component_level text NULL,
	CONSTRAINT flow_cycle_timeseries_pkey PRIMARY KEY (index)
);

CREATE TABLE IF NOT EXISTS public.flow_cycle_timeseries_buffer (
	"index" serial4 NOT NULL,
	i float8 NULL,
	v float8 NULL,
	w float8 NULL,
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
	component_level text NULL,
	CONSTRAINT flow_cycle_timeseries_buffer_pkey PRIMARY KEY (index)
);

CREATE TABLE IF NOT EXISTS public.stack_metadata (
	"index" serial4 NOT NULL,
	stack_id text NOT NULL,
	num_series int4 NOT NULL,
	status text NULL
);

CREATE TABLE IF NOT EXISTS module_metadata (
    index integer NOT NULL,
    module_id text NOT NULL,
    configuration text,
    num_parallel integer,
    num_series integer,
    status text
);

ALTER TABLE ONLY module_metadata ALTER COLUMN index SET DEFAULT nextval('module_metadata_index_seq'::regclass);

ALTER TABLE ONLY module_metadata
    ADD CONSTRAINT module_metadata_pkey PRIMARY KEY (index);

CREATE VIEW IF NOT EXISTS cell_cycle_stats AS
SELECT
  v_max,
  v_min,
  ah_c,
  ah_d,
  e_c,
  e_d,
  i_max,
  i_min,
  v_c_mean,
  v_d_mean,
  e_eff,
  ah_eff,
  cycle_index,
  test_time,
  cell_id
FROM cycle_stats
WHERE component_level='cell';

CREATE VIEW IF NOT EXISTS module_cycle_stats AS
SELECT
  v_max,
  v_min,
  ah_c,
  ah_d,
  e_c,
  e_d,
  i_max,
  i_min,
  v_c_mean,
  v_d_mean,
  e_eff,
  ah_eff,
  cycle_index,
  test_time,
  cell_id “module_id”
FROM cycle_stats
WHERE component_level='module';

CREATE VIEW IF NOT EXISTS cell_timeseries AS
SELECT
  i,
  v,
  ah_c,
  ah_d,
  e_c,
  e_d,
  env_temperature,
  cell_temperature,
  cycle_time,
  date_time,
  cycle_index,
  test_time,
  cell_id "cell_id"
FROM cycle_timeseries
WHERE component_level='cell';

CREATE VIEW IF NOT EXISTS module_timeseries AS
SELECT
  i,
  v,
  ah_c,
  ah_d,
  e_c,
  e_d,
  env_temperature,
  cell_temperature,
  cycle_time,
  date_time,
  cycle_index,
  test_time,
  cell_id "module_id"
FROM cycle_timeseries
WHERE component_level='module';