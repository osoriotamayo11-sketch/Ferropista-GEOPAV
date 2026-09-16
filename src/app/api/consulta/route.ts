import { NextRequest, NextResponse } from 'next/server';

/**
 * Recepción de la consulta ciudadana del OE 2.
 *
 * ABIERTA desde el 15 sep 2026, con el instrumento propio del semillero: el oficial,
 * avalado por la interlocutora, todavía no ha llegado. Por eso cada fila se marca con
 * INSTRUMENTO_VERSION. Cuando el oficial entre, se cambia esa constante y las dos
 * tandas quedan separables; nunca se reescribe la versión de las filas ya guardadas.
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
const INSTRUMENTO_VERSION = 'borrador-geopav-2026-09';

const OBLIGATORIOS = ['perfil', 'municipio', 'frecuencia', 'riesgo'] as const;

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

  const faltantes = OBLIGATORIOS.filter((k) => body[k] === undefined || body[k] === null);
  if (faltantes.length > 0) {
    return NextResponse.json(
      { error: `Faltan respuestas obligatorias: ${faltantes.join(', ')}.` },
      { status: 400 }
    );
  }

  const riesgo = Number(body.riesgo);
  if (!Number.isInteger(riesgo) || riesgo < 1 || riesgo > 5) {
    return NextResponse.json(
      { error: 'La valoración de riesgo debe estar entre 1 y 5.' },
      { status: 400 }
    );
  }

  const comentario = typeof body.comentario === 'string' ? body.comentario : null;
  if (comentario !== null && comentario.length > 300) {
    return NextResponse.json(
      { error: 'El comentario supera los 300 caracteres.' },
      { status: 400 }
    );
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
   * que cada inserción salía a `/rest/v1/rest/v1/consulta_oe2` y Supabase la
   * rechazaba con «Invalid path specified in request URL». El segundo: esta URL
   * solo se usa aquí, en el servidor, así que el prefijo NEXT_PUBLIC_ —que
   * expone el valor al navegador— nunca hizo falta.
   *
   * El valor correcto es la raíz del proyecto, sin ruta y sin barra final.
   */
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !key) {
    console.error('Falta SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en el entorno.');
    return NextResponse.json(
      { error: 'No se pudo guardar la respuesta. Inténtelo de nuevo más tarde.', almacenado: false },
      { status: 500 }
    );
  }

  const { createClient } = await import('@supabase/supabase-js');
  const supabase = createClient(url, key);

  const { error } = await supabase.from('consulta_oe2').insert([{
    consentimiento: true,
    instrumento_version: INSTRUMENTO_VERSION,
    perfil: body.perfil, municipio: body.municipio, frecuencia: body.frecuencia,
    franja: body.franja ?? null,
    riesgo_1a5: riesgo,
    sectores: body.sectores ?? null, causas: body.causas ?? null,
    accidente: body.accidente === 'si' ? true : body.accidente === 'no' ? false : null,
    cambio_5a: body.cambio ?? null,
    tiempo_cruce: body.tiempo ?? null,
    impredecible_1a5: body.impredecible ?? null,
    afectacion: body.afectacion ?? null,
    conocia: body.conocia === 'si' ? true : body.conocia === 'no' ? false : null,
    efecto_esperado: body.efecto ?? null,
    preocupacion: body.preocupacion ?? null,
    comentario,
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
