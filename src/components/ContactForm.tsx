'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, User, Building2, Mail, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export const ContactForm: React.FC = () => {
  const [formData, setFormData] = useState({
    nombre: '',
    empresa: '',
    correo: '',
  });

  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    setErrorMessage('');

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStatus('success');
        setFormData({ nombre: '', empresa: '', correo: '' });
      } else {
        setStatus('error');
        setErrorMessage(data.error || 'Ocurrió un error al enviar el formulario.');
      }
    } catch (err) {
      console.error('Error de red:', err);
      setStatus('error');
      setErrorMessage('No se pudo conectar con el servidor. Inténtalo de nuevo.');
    }
  };

  return (
    <section id="contacto" className="py-24 bg-white /60 relative overflow-hidden border-t border-slate-200 transition-colors duration-300">
      {/* Ambient background glow */}
      <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-96 h-96 bg-blue-600/10 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-emerald-600/10 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        <div className="grid lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Info Column */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="lg:col-span-5 space-y-6 text-center lg:text-left"
          >
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-uni-600 text-xs font-semibold uppercase tracking-wider">
              <Mail className="w-4 h-4 text-uni-600" />
              <span>Contacto Académico</span>
            </div>

            <h2 className="text-3xl sm:text-4xl font-extrabold text-uni-900 tracking-tight leading-tight">
              Escríbele al Semillero de Investigación
            </h2>

            <p className="text-base text-slate-600 font-light leading-relaxed">
              Escríbele al Semillero de Investigación GEOPAV de la Universidad de Ibagué. Este es un trabajo académico del Semestre Paz y Región 2026B: recibimos observaciones sobre el análisis, aportes de transportadores y habitantes del corredor, y correcciones a los datos publicados.
            </p>

            <div className="space-y-3 pt-2 text-xs font-mono text-slate-500">
              <div className="flex items-center gap-3 justify-center lg:justify-start">
                <div className="w-2 h-2 rounded-full bg-gmae-500 animate-pulse"></div>
                <span>Universidad de Ibagué · Programa de Ingeniería Civil</span>
              </div>
              <div className="flex items-center gap-3 justify-center lg:justify-start">
                <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                <span>Tiempo de respuesta estimado: &lt; 24 horas hábiles</span>
              </div>
            </div>
          </motion.div>

          {/* Right Form Card Column */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="lg:col-span-7"
          >
            <div className="rounded-3xl bg-slate-50/90 border border-slate-200 p-8 sm:p-10 shadow-2xl relative">
              
              {status === 'success' ? (
                <div className="py-12 text-center space-y-4">
                  <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-gmae-600 flex items-center justify-center mx-auto">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <h3 className="text-2xl font-bold text-uni-900">¡Mensaje Enviado!</h3>
                  <p className="text-sm text-slate-600 max-w-md mx-auto">
                    Hemos recibido tu mensaje. El equipo del Semillero GEOPAV lo revisará a la brevedad.
                  </p>
                  <button
                    onClick={() => setStatus('idle')}
                    className="mt-4 px-6 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-700 text-uni-900 font-semibold text-xs transition-colors"
                  >
                    Enviar otra consulta
                  </button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  
                  {/* Nombre */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-600 flex items-center gap-2">
                      <User className="w-3.5 h-3.5 text-uni-600" />
                      <span>Nombre Completo *</span>
                    </label>
                    <input
                      type="text"
                      name="nombre"
                      required
                      value={formData.nombre}
                      onChange={handleChange}
                      placeholder="Ej. Ing. Carlos Mendoza"
                      className="w-full px-4 py-3 rounded-xl bg-white border border-slate-200 text-uni-900 text-sm placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                    />
                  </div>

                  {/* Empresa */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-600 flex items-center gap-2">
                      <Building2 className="w-3.5 h-3.5 text-gmae-600" />
                      <span>Empresa o Institución</span>
                    </label>
                    <input
                      type="text"
                      name="empresa"
                      value={formData.empresa}
                      onChange={handleChange}
                      placeholder="Ej. Logística de Colombia S.A."
                      className="w-full px-4 py-3 rounded-xl bg-white border border-slate-200 text-uni-900 text-sm placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
                    />
                  </div>

                  {/* Correo Electrónico */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-600 flex items-center gap-2">
                      <Mail className="w-3.5 h-3.5 text-uni-500" />
                      <span>Correo Electrónico *</span>
                    </label>
                    <input
                      type="email"
                      name="correo"
                      required
                      value={formData.correo}
                      onChange={handleChange}
                      placeholder="carlos.mendoza@empresa.com"
                      className="w-full px-4 py-3 rounded-xl bg-white border border-slate-200 text-uni-900 text-sm placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-colors"
                    />
                  </div>

                  {/* Error Message */}
                  {status === 'error' && (
                    <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-700 text-xs flex items-center gap-3">
                      <AlertCircle className="w-4 h-4 shrink-0" />
                      <span>{errorMessage}</span>
                    </div>
                  )}

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={status === 'loading'}
                    className="w-full py-4 rounded-xl bg-uni-700 hover:bg-uni-600 text-white font-bold text-sm shadow-xl shadow-engineering-900/20 transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 border border-uni-500"
                  >
                    {status === 'loading' ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin text-uni-900" />
                        <span>Enviando solicitud...</span>
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        <span>Enviar Solicitud de Información</span>
                      </>
                    )}
                  </button>

                  <p className="text-[11px] text-slate-500 text-center font-mono">
                    Sus datos se usan únicamente con fines académicos dentro del Semestre Paz y Región de la Universidad de Ibagué y no se comparten con terceros.
                  </p>
                </form>
              )}

            </div>
          </motion.div>

        </div>

      </div>
    </section>
  );
};
