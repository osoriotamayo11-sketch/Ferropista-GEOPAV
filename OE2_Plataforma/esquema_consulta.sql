-- Consulta ciudadana del objetivo específico 2 — Semillero GEOPAV
-- Percepción de riesgo vial en el paso del Alto de La Línea.
--
-- VIGENTE desde el 15 sep 2026. Se ejecuta en el editor SQL del proyecto de Supabase.
--
-- La consulta se abre con el instrumento propio del semillero, ANTES de que llegue
-- el oficial avalado por la interlocutora. Por eso la tabla lleva `instrumento_version`:
-- cada respuesta queda marcada con la versión que la produjo, de modo que las dos
-- tandas se puedan separar o juntar pregunta por pregunta cuando se sustituya.
-- Sin esa columna, mezclarlas sería indistinguible de falsear la muestra.
--
-- Tres reglas fijas, acordadas antes de escribir esto:
--   1. No se almacena dirección IP ni identificador de dispositivo.
--   2. RLS activa: el rol anónimo puede insertar, nunca leer.
--   3. La service role key vive solo en el servidor, jamás en el cliente.
--
-- No hay ninguna columna que identifique a la persona: ni nombre, ni documento,
-- ni contacto. El municipio es de residencia o base de operación, no de ubicación.

create table if not exists public.consulta_oe2 (
  id                uuid primary key default gen_random_uuid(),
  creado_en         timestamptz not null default now(),

  consentimiento    boolean     not null check (consentimiento = true),

  -- Qué versión del cuestionario produjo esta respuesta. Ver el encabezado.
  instrumento_version text    not null default 'borrador-geopav-2026-09',

  -- A · relación con el paso
  perfil            text        not null,
  municipio         text        not null,
  frecuencia        text        not null,
  franja            text,

  -- B · percepción de riesgo
  riesgo_1a5        smallint    not null check (riesgo_1a5 between 1 and 5),
  sectores          text[],
  causas            text[],
  accidente         boolean,
  cambio_5a         text,

  -- C · operación y vida diaria
  tiempo_cruce      text,
  impredecible_1a5  smallint    check (impredecible_1a5 between 1 and 5),
  afectacion        text[],

  -- D · sobre la propuesta de túnel
  conocia           boolean,
  efecto_esperado   text,
  preocupacion      text,

  -- E · abierta
  comentario        text        check (char_length(comentario) <= 300)
);

comment on table public.consulta_oe2 is
  'Respuestas anónimas de la consulta ciudadana del OE 2. Sin datos identificables.';

-- Índice para los cortes que va a usar el análisis
create index if not exists consulta_oe2_perfil_idx    on public.consulta_oe2 (perfil);
create index if not exists consulta_oe2_municipio_idx on public.consulta_oe2 (municipio);
create index if not exists consulta_oe2_creado_idx    on public.consulta_oe2 (creado_en);
create index if not exists consulta_oe2_version_idx   on public.consulta_oe2 (instrumento_version);

-- Seguridad a nivel de fila
alter table public.consulta_oe2 enable row level security;

-- El visitante puede depositar una respuesta…
create policy "anon puede insertar"
  on public.consulta_oe2
  for insert
  to anon
  with check (consentimiento = true);

-- …y no puede leer ninguna, ni la suya. La lectura se hace desde el servidor
-- con la service role key, que omite RLS. No se crea ninguna policy de select.
