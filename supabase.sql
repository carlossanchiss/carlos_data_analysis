-- Tabla atletas
create table if not exists public.athletes (
  id uuid primary key default gen_random_uuid(),
  strava_id bigint unique,
  firstname text,
  lastname text,
  access_token text,
  refresh_token text,
  expires_at bigint,
  coach_email text
);

-- Tabla bruta (JSON)
create table if not exists public.activities_raw (
  id bigint primary key,
  strava_id bigint,
  raw_json jsonb,
  start_date timestamptz
);

-- Tabla métricas procesadas
create table if not exists public.activities_metrics (
  id uuid primary key default gen_random_uuid(),
  strava_id bigint,
  activity_id bigint,
  date date,
  distance_km numeric,
  moving_time_min numeric,
  np numeric,
  tss numeric,
  ctl numeric,
  atl numeric,
  pd_curve jsonb,
  best_5 numeric,
  best_60 numeric,
  best_300 numeric,
  best_1200 numeric
);

-- Tabla IA
create table if not exists public.ai_insights (
  strava_id bigint,
  week date,
  weekly_summary text,
  workout_plan text,
  primary key (strava_id, week)
);

-- ———  Row-Level Security ———
alter table athletes            enable row level security;
alter table activities_raw      enable row level security;
alter table activities_metrics  enable row level security;
alter table ai_insights         enable row level security;

-- Atleta ve solo lo suyo
create policy athlete_ath
  on athletes for select
  using ( strava_id::text = auth.jwt()::json->>'strava_id');

create policy athlete_raw
  on activities_raw for select
  using ( strava_id::text = auth.jwt()::json->>'strava_id');

create policy athlete_met
  on activities_metrics for select
  using ( strava_id::text = auth.jwt()::json->>'strava_id');

create policy athlete_ai
  on ai_insights for select
  using ( strava_id::text = auth.jwt()::json->>'strava_id');

-- Coach (correo en athletes.coach_email) ve todo mediante sub-query
create policy coach_raw
  on activities_raw for all
  using (
    exists(select 1 from athletes a
           where a.strava_id = activities_raw.strava_id
             and a.coach_email = auth.jwt()::json->>'email')
  );

create policy coach_met
  on activities_metrics for all
  using (exists(select 1 from athletes a
                where a.strava_id = activities_metrics.strava_id
