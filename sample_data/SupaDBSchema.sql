'''
-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.Fan list (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  series text,
  product_type character varying,
  innerouter character varying,
  diameter bigint,
  fanID uuid NOT NULL DEFAULT gen_random_uuid() UNIQUE,
  year bigint,
  fan_type text,
  CONSTRAINT Fan list_pkey PRIMARY KEY (fanID),
  CONSTRAINT Fan list_fan_type_fkey FOREIGN KEY (fan_type) REFERENCES public.fan_type(fan_type)
);
CREATE TABLE public.FanTestData (
  fantestdataID uuid NOT NULL DEFAULT gen_random_uuid(),
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  fanID uuid NOT NULL,
  FanName text,
  created_at timestamp with time zone DEFAULT now(),
  TestDate date NOT NULL,
  tested_at text,
  test_facillity jsonb,
  comment text,
  SingleFanTest boolean NOT NULL,
  bellmouth text NOT NULL,
  Unit bigint,
  Hako uuid,
  Hex character varying,
  temp_o_[degC] real NOT NULL,
  temp_c_[defC] real NOT NULL,
  Ps_[Pa] jsonb NOT NULL,
  Q_[m3min] jsonb NOT NULL,
  Torque_[mNm] jsonb,
  Power_[W] jsonb,
  SPL_[dbA] jsonb,
  CONSTRAINT FanTestData_pkey PRIMARY KEY (fantestdataID),
  CONSTRAINT FanTestData_fanID_fkey FOREIGN KEY (fanID) REFERENCES public.Fan list(fanID),
  CONSTRAINT FanTestData_Hako_fkey FOREIGN KEY (Hako) REFERENCES public.Hako list(hakoID),
  CONSTRAINT FanTestData_Hex_fkey FOREIGN KEY (Hex) REFERENCES public.heat_exchanger(熱交_id),
  CONSTRAINT FanTestData_Unit_fkey FOREIGN KEY (Unit) REFERENCES public.Unit list(id)
);
CREATE TABLE public.Hako list (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  hakoID uuid NOT NULL DEFAULT gen_random_uuid() UNIQUE,
  series character varying,
  subseries character varying,
  CONSTRAINT Hako list_pkey PRIMARY KEY (id, hakoID)
);
CREATE TABLE public.Unit list (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  product_type text NOT NULL,
  innerouter text,
  hakoID uuid UNIQUE,
  fanID uuid,
  HexID character varying,
  compID character varying,
  refID character varying,
  CONSTRAINT Unit list_pkey PRIMARY KEY (id),
  CONSTRAINT Unit list_fanID_fkey FOREIGN KEY (fanID) REFERENCES public.Fan list(fanID),
  CONSTRAINT Unit list_hakoID_fkey FOREIGN KEY (hakoID) REFERENCES public.Hako list(hakoID)
);
CREATE TABLE public.bellmouth_casing (
  bc_id character varying NOT NULL,
  番号 integer NOT NULL DEFAULT nextval('"bellmouth_casing_番号_seq"'::regclass) UNIQUE,
  作成日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  製品種別 character varying,
  ファンシリーズ character varying,
  内径 numeric,
  備考 text,
  ステータス character varying DEFAULT 'active'::character varying CHECK ("ステータス"::text = ANY (ARRAY['active'::character varying, 'inactive'::character varying, 'obsolete'::character varying]::text[])),
  更新日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT bellmouth_casing_pkey PRIMARY KEY (bc_id)
);
CREATE TABLE public.casing (
  筐体_id character varying NOT NULL,
  番号 integer NOT NULL DEFAULT nextval('"casing_番号_seq"'::regclass) UNIQUE,
  作成日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  筐体名 character varying,
  寸法_幅 numeric,
  寸法_奥行 numeric,
  寸法_高さ numeric,
  材質 character varying,
  備考 text,
  ステータス character varying DEFAULT 'active'::character varying,
  更新日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT casing_pkey PRIMARY KEY (筐体_id)
);
CREATE TABLE public.compressor (
  圧縮機_id character varying NOT NULL,
  番号 integer NOT NULL DEFAULT nextval('"compressor_番号_seq"'::regclass) UNIQUE,
  作成日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  メーカー character varying,
  型式 character varying,
  容量 numeric,
  ストロークボリューム numeric,
  圧縮機効率 numeric CHECK ("圧縮機効率" >= 0::numeric AND "圧縮機効率" <= 100::numeric),
  冷媒種類 character varying,
  運転周波数範囲_下限 integer,
  運転周波数範囲_上限 integer,
  備考 text,
  ステータス character varying DEFAULT 'active'::character varying,
  更新日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT compressor_pkey PRIMARY KEY (圧縮機_id)
);
CREATE TABLE public.fan (
  ファン_id character varying NOT NULL,
  番号 integer NOT NULL DEFAULT nextval('"fan_番号_seq"'::regclass) UNIQUE,
  作成日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  ファン名 character varying,
  ファン種別 character varying,
  直径 numeric,
  枚数 integer,
  定格風量 numeric,
  定格回転数 integer,
  備考 text,
  ステータス character varying DEFAULT 'active'::character varying,
  更新日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fan_pkey PRIMARY KEY (ファン_id)
);
CREATE TABLE public.fan_type (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  fan_type text NOT NULL UNIQUE,
  CONSTRAINT fan_type_pkey PRIMARY KEY (id, fan_type)
);
CREATE TABLE public.heat_exchanger (
  熱交_id character varying NOT NULL,
  番号 integer NOT NULL DEFAULT nextval('"heat_exchanger_番号_seq"'::regclass) UNIQUE,
  作成日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  フィンシリーズ character varying,
  列数 integer CHECK ("列数" > 0),
  段数 integer CHECK ("段数" > 0),
  伝熱面積 numeric,
  フィンピッチ numeric,
  チューブ外径 numeric,
  備考 text,
  ステータス character varying DEFAULT 'active'::character varying,
  更新日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT heat_exchanger_pkey PRIMARY KEY (熱交_id)
);
CREATE TABLE public.refrigerant (
  冷媒_id character varying NOT NULL,
  番号 integer NOT NULL DEFAULT nextval('"refrigerant_番号_seq"'::regclass) UNIQUE,
  作成日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  冷媒名 character varying NOT NULL,
  ph線図_id character varying,
  分子量 numeric,
  沸点 numeric,
  臨界温度 numeric,
  臨界圧力 numeric,
  gwp integer,
  odp numeric,
  安全性分類 character varying,
  備考 text,
  ステータス character varying DEFAULT 'active'::character varying,
  更新日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT refrigerant_pkey PRIMARY KEY (冷媒_id)
);
CREATE TABLE public.test_data (
  データ_id character varying NOT NULL,
  番号 integer NOT NULL DEFAULT nextval('"test_data_番号_seq"'::regclass) UNIQUE,
  作成日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  試験日 date NOT NULL,
  試験者 character varying,
  ユニット_id character varying,
  筐体_id character varying,
  ファン_id character varying,
  bc_id character varying,
  熱交_id character varying,
  圧縮機_id character varying,
  冷媒_id character varying,
  運転モード character varying,
  室内温度 numeric,
  室内湿度 numeric,
  室外温度 numeric,
  室外湿度 numeric,
  圧縮機周波数 integer,
  ファン回転数 integer,
  冷房能力 numeric,
  暖房能力 numeric,
  消費電力 numeric CHECK ("消費電力" >= 0::numeric),
  cop numeric CHECK (cop >= 0::numeric),
  吸込圧力 numeric,
  吐出圧力 numeric,
  吸込温度 numeric,
  吐出温度 numeric,
  過冷却度 numeric,
  過熱度 numeric,
  合否判定 character varying,
  判定理由 text,
  データファイルパス character varying,
  備考 text,
  更新日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  Ps ARRAY,
  CONSTRAINT test_data_pkey PRIMARY KEY (データ_id),
  CONSTRAINT test_data_ユニット_id_fkey FOREIGN KEY (ユニット_id) REFERENCES public.unit(ユニット_id),
  CONSTRAINT test_data_筐体_id_fkey FOREIGN KEY (筐体_id) REFERENCES public.casing(筐体_id),
  CONSTRAINT test_data_ファン_id_fkey FOREIGN KEY (ファン_id) REFERENCES public.fan(ファン_id),
  CONSTRAINT test_data_bc_id_fkey FOREIGN KEY (bc_id) REFERENCES public.bellmouth_casing(bc_id),
  CONSTRAINT test_data_熱交_id_fkey FOREIGN KEY (熱交_id) REFERENCES public.heat_exchanger(熱交_id),
  CONSTRAINT test_data_圧縮機_id_fkey FOREIGN KEY (圧縮機_id) REFERENCES public.compressor(圧縮機_id),
  CONSTRAINT test_data_冷媒_id_fkey FOREIGN KEY (冷媒_id) REFERENCES public.refrigerant(冷媒_id)
);
CREATE TABLE public.unit (
  ユニット_id character varying NOT NULL,
  番号 integer NOT NULL DEFAULT nextval('"unit_番号_seq"'::regclass) UNIQUE,
  作成日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  ユニット名 character varying,
  製品シリーズ character varying,
  定格能力 numeric,
  備考 text,
  ステータス character varying DEFAULT 'active'::character varying,
  更新日時 timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT unit_pkey PRIMARY KEY (ユニット_id)
);
'''
