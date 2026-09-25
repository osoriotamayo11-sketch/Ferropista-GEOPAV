import { NextRequest, NextResponse } from 'next/server';

/**
 * Recepción de la consulta ciudadana del OE 2.
 *
 * ABIERTA desde el 15 sep 2026. Instrumento vigente: el OFICIAL, avalado por la
 * entidad receptora (versión 'oficial-2026-09'; preguntas en
 * OE2_Plataforma/Act3_Instrumento/instrumento_oficial_2026-09.json). Las respuestas
 * se guardan en la tabla consulta_oe2_oficial (OE2_Plataforma/esquema_consulta_oficial.sql),
 * separada de la tabla del instrumento borrador anterior (consulta_oe2), que se
 * conserva intacta y nunca se mezcla en silencio con esta.
 *
 * Si la inserción falla —el proyecto de Supabase del plan Free se pausa solo tras unos
 * días sin actividad— la ruta devuelve 500 y el formulario se lo dice al participante.
 * Lo que no hace nunca es responder «guardado» sin haber guardado.
 *
 * Regla fija: no se almacena dirección IP ni identificador de dispositivo. No se lee
 * ninguna cabecera de red en esta ruta y así debe quedarse.
 */

const ALMACENAMIENTO_ACTIVO = true;

/** Versión del cuestionario que produce las respuestas. Ver el encabezado. */
const INSTRUMENTO_VERSION = 'oficial-2026-09';

const RELACIONES = ['carga', 'particular', 'comerciante', 'residente', 'trabajador', 'otro'] as const;
const PERFILES_CON_BLOQUE = ['carga', 'particular', 'residente', 'comerciante'] as const;
const FRECUENCIAS = ['diario', 'varias_semana', 'una_semana', 'algunas_mes', 'ocasional', 'nunca'] as const;
const CLAVES_LIKERT_OBLIGATORIAS = ['p03', 'p04', 'p05', 'p06', 'p07', 'p08', 'p09', 'p10', 'p11', 'p12', 'p13'] as const;

const esLikertValido = (v: unknown): v is number => Number.isInteger(v) && (v as number) >= 1 && (v as number) <= 5;

export async function POST(req: NextRequest) {
  let body: Record<string, unknown>;

  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'Cuerpo inválido.' }, { status: 400 });
  }

  if (body.consentimiento !== true) {
    return NextResponse.json(
      { error: 'Sin consentimiento no se procesa la respuesta.' },
      { status: 400 }
    );
  }

  const relacion = body.relacion;
  if (typeof relacion !== 'string' || !RELACIONES.includes(relacion as (typeof RELACIONES)[number])) {
    return NextResponse.json({ error: 'La relación con el corredor no es válida.' }, { status: 400 });
  }

  const relacionOtro = body.relacion_otro;
  if (relacionOtro !== null && relacionOtro !== undefined) {
    if (typeof relacionOtro !== 'string' || relacionOtro.length > 100) {
      return NextResponse.json({ error: 'El detalle de "Otro" supera los 100 caracteres.' }, { status: 400 });
    }
    if (relacion !== 'otro') {
      return NextResponse.json({ error: 'El detalle de "Otro" solo aplica cuando la relación es "otro".' }, { status: 400 });
    }
  }

  const frecuencia = body.frecuencia;
  if (typeof frecuencia !== 'string' || !FRECUENCIAS.includes(frecuencia as (typeof FRECUENCIAS)[number])) {
    return NextResponse.json({ error: 'La frecuencia de uso no es válida.' }, { status: 400 });
  }

  for (const clave of CLAVES_LIKERT_OBLIGATORIAS) {
    if (!esLikertValido(body[clave])) {
      return NextResponse.json(
        { error: `La respuesta de la pregunta ${clave.slice(1)} debe estar entre 1 y 5.` },
        { status: 400 }
      );
    }
  }

  const requierePerfil = PERFILES_CON_BLOQUE.includes(relacion as (typeof PERFILES_CON_BLOQUE)[number]);
  const p14 = body.p14;
  const p15 = body.p15;

  if (requierePerfil) {
    if (!esLikertValido(p14) || !esLikertValido(p15)) {
      return NextResponse.json(
        { error: 'Faltan las preguntas 14 y 15, obligatorias para este perfil.' },
        { status: 400 }
      );
    }
  } else if ((p14 !== null && p14 !== undefined) || (p15 !== null && p15 !== undefined)) {
    return NextResponse.json(
      { error: 'Las preguntas 14 y 15 no aplican a este perfil.' },
      { status: 400 }
    );
  }

  const p16Beneficio = body.p16_beneficio;
  if (p16Beneficio !== null && p16Beneficio !== undefined) {
    if (typeof p16Beneficio !== 'string' || p16Beneficio.length > 500) {
      return NextResponse.json({ error: 'La respuesta 16 supera los 500 caracteres.' }, { status: 400 });
    }
  }

  const p17Impacto = body.p17_impacto;
  if (p17Impacto !== null && p17Impacto !== undefined) {
    if (typeof p17Impacto !== 'string' || p17Impacto.length > 500) {
      return NextResponse.json({ error: 'La respuesta 17 supera los 500 caracteres.' }, { status: 400 });
    }
  }

  if (!ALMACENAMIENTO_ACTIVO) {
    return NextResponse.json(
      {
        error: 'La consulta todavía no está abierta. Esta es una vista previa del instrumento.',
        almacenado: false,
      },
      { status: 501 }
    );
  }

  /*
   * SUPABASE_URL, no NEXT_PUBLIC_SUPABASE_URL. Dos motivos, y el primero costó
   * una tarde: la variable con prefijo público guardaba
   * `…supabase.co/rest/v1`, y el cliente añade `/rest/v1` por su cuenta, de modo
   * que cada inserción salía a `/rest/v1/rest/v1/consulta_oe2_oficial` y Supabase la
   * rechazaba con «Invalid path specified in request URL». El segundo: esta URL
   * solo se usa aquí, en el servidor, así que el prefijo NEXT_PUBLIC_ —que
   * expone el valor al navegador— nunca hizo falta.
   *
   * El valor correcto es la raíz del proyecto, sin ruta y sin barra final.
   */
  /*
   * SUPABASE_SECRET_KEY (formato `sb_secret_…`) desde el 16 sep 2026. Sustituye a la
   * `service_role` legacy, que Supabase retira a finales de 2026 y que ya no se
   * regenera cuando un proyecto pausado se restaura. Va sin respaldo a la clave vieja
   * a propósito: si falta, la ruta falla a la vista en vez de seguir dependiendo de
   * una clave en retirada. Solo servidor: Supabase rechaza esta clave desde un navegador.
   */
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SECRET_KEY;

  if (!url || !key) {
    console.error('Falta SUPABASE_URL o SUPABASE_SECRET_KEY en el entorno.');
    return NextResponse.json(
      { error: 'No se pudo guardar la respuesta. Inténtelo de nuevo más tarde.', almacenado: false },
      { status: 500 }
    );
  }

  const { createClient } = await import('@supabase/supabase-js');
  const supabase = createClient(url, key);

  const { error } = await supabase.from('consulta_oe2_oficial').insert([{
    consentimiento: true,
    instrumento_version: INSTRUMENTO_VERSION,
    relacion,
    relacion_otro: relacion === 'otro' ? relacionOtro ?? null : null,
    frecuencia,
    p03: body.p03, p04: body.p04, p05: body.p05, p06: body.p06, p07: body.p07,
    p08: body.p08, p09: body.p09, p10: body.p10, p11: body.p11, p12: body.p12, p13: body.p13,
    p14: requierePerfil ? p14 : null,
    p15: requierePerfil ? p15 : null,
    p16_beneficio: p16Beneficio ?? null,
    p17_impacto: p17Impacto ?? null,
  }]);

  if (error) {
    console.error('Error insertando la consulta del OE 2:', error.message);
    return NextResponse.json(
      { error: 'No se pudo guardar la respuesta. Inténtelo de nuevo más tarde.', almacenado: false },
      { status: 500 }
    );
  }

  return NextResponse.json({ almacenado: true }, { status: 200 });
}
