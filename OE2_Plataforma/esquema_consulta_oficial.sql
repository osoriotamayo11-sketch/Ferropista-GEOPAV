-- Consulta ciudadana del OE 2 — instrumento OFICIAL avalado (versión 'oficial-2026-09').
-- Semillero GEOPAV.
--
-- Tabla nueva. La tabla public.consulta_oe2 (borrador 'borrador-geopav-2026-09') NO se
-- toca: sus filas se conservan tal cual y nunca se mezclan en silencio con estas.
--
-- Reglas fijas heredadas del esquema anterior:
--   1. No se almacena dirección IP ni identificador de dispositivo.
--   2. RLS activa: el rol anónimo puede insertar, nunca leer.
--   3. La clave secreta vive solo en el servidor.
-- Ninguna columna identifica a la persona.
--
-- Preguntas: OE2_Plataforma/Act3_Instrumento/instrumento_oficial_2026-09.json
-- p14 y p15 dependen de la relación (pregunta 1); su texto cambia por perfil.
-- 'trabajador' y 'otro' no tienen bloque 14–15 en el instrumento: van en nulo.

create table if not exists public.consulta_oe2_oficial (
  id                  uuid primary key default gen_random_uuid(),
  creado_en           timestamptz not null default now(),
  consentimiento      boolean     not null check (consentimiento = true),
  instrumento_version text        not null default 'oficial-2026-09',

  relacion      text not null check (relacion in
                  ('carga','particular','comerciante','residente','trabajador','otro')),
  relacion_otro text check (char_length(relacion_otro) <= 100),
  frecuencia    text not null check (frecuencia in
                  ('diario','varias_semana','una_semana','algunas_mes','ocasional','nunca')),

  p03 smallint not null check (p03 between 1 and 5),
  p04 smallint not null check (p04 between 1 and 5),
  p05 smallint not null check (p05 between 1 and 5),
  p06 smallint not null check (p06 between 1 and 5),
  p07 smallint not null check (p07 between 1 and 5),
  p08 smallint not null check (p08 between 1 and 5),
  p09 smallint not null check (p09 between 1 and 5),
  p10 smallint not null check (p10 between 1 and 5),
  p11 smallint not null check (p11 between 1 and 5),
  p12 smallint not null check (p12 between 1 and 5),
  p13 smallint not null check (p13 between 1 and 5),
  p14 smallint check (p14 between 1 and 5),
  p15 smallint check (p15 between 1 and 5),

  p16_beneficio text check (char_length(p16_beneficio) <= 500),
  p17_impacto   text check (char_length(p17_impacto)   <= 500),

  constraint bloque_por_perfil check (
    (relacion in ('carga','particular','comerciante','residente') and p14 is not null and p15 is not null)
    or
    (relacion in ('trabajador','otro') and p14 is null and p15 is null)
  ),
  constraint otro_solo_si_otro check (relacion = 'otro' or relacion_otro is null)
);

comment on table public.consulta_oe2_oficial is
  'Respuestas anónimas de la consulta del OE 2 con el instrumento oficial avalado. Sin datos identificables.';

create index if not exists consulta_oe2_oficial_relacion_idx on public.consulta_oe2_oficial (relacion);
create index if not exists consulta_oe2_oficial_creado_idx   on public.consulta_oe2_oficial (creado_en);

alter table public.consulta_oe2_oficial enable row level security;

create policy "anon puede insertar (oficial)"
  on public.consulta_oe2_oficial
  for insert
  to anon
  with check (consentimiento = true);
-- Sin policy de select: la lectura se hace desde el servidor con la clave secreta.
