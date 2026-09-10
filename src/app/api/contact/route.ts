import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { nombre, empresa, correo } = body;

    // Validación básica de campos
    if (!nombre || !correo) {
      return NextResponse.json(
        { error: 'Los campos Nombre y Correo son obligatorios.' },
        { status: 400 }
      );
    }

    /*
     * =========================================================================
     * INSTRUCCIONES DE INTEGRACIÓN DE SUPABASE:
     * =========================================================================
     * 1. Instala el cliente de Supabase:
     *    npm install @supabase/supabase-js
     *
     * 2. Configura las variables de entorno en tu archivo .env.local:
     *    NEXT_PUBLIC_SUPABASE_URL=https://tu-proyecto.supabase.co
     *    SUPABASE_SERVICE_ROLE_KEY=tu-clave-service-role-o-anon-key
     *
     * 3. Descomenta e inserta el siguiente fragmento de código:
     *
     *    import { createClient } from '@supabase/supabase-js';
     *    const supabase = createClient(
     *      process.env.NEXT_PUBLIC_SUPABASE_URL!,
     *      process.env.SUPABASE_SERVICE_ROLE_KEY!
     *    );
     *
     *    const { data, error } = await supabase
     *      .from('contactos')
     *      .insert([{ nombre, empresa, correo, created_at: new Date().toISOString() }]);
     *
     *    if (error) {
     *      console.error('Error insertando en Supabase:', error);
     *      return NextResponse.json({ error: error.message }, { status: 500 });
     *    }
     * =========================================================================
     */

    // Log para depuración en entorno de desarrollo
    console.log('📬 Nuevo mensaje de contacto recibido:', {
      nombre,
      empresa: empresa || 'N/A',
      correo,
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json(
      {
        success: true,
        message: 'Solicitud enviada correctamente. Un consultor técnico se pondrá en contacto pronto.',
        receivedData: { nombre, empresa, correo },
      },
      { status: 200 }
    );
  } catch (error: any) {
    console.error('Error procesando formulario de contacto:', error);
    return NextResponse.json(
      { error: 'Error interno del servidor al procesar la solicitud.' },
      { status: 500 }
    );
  }
}
