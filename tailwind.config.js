/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        /* Azul institucional Universidad de Ibague. Base #193F77 tomada del logotipo. */
        uni: {
          50:  '#eef3fa',
          100: '#d8e3f2',
          200: '#b3c7e3',
          300: '#8aa7d1',
          400: '#5f83ba',
          500: '#3d63a0',
          600: '#2a4f87',
          700: '#193F77',
          800: '#143163',
          900: '#0f2449',
          950: '#0a1830',
        },
        /* Verde del Semillero GMAE */
        gmae: {
          50:  '#eaf6f1',
          100: '#cdeadd',
          200: '#9dd5bf',
          300: '#66bd9d',
          400: '#33a17c',
          500: '#158a63',
          600: '#0F7B55',
          700: '#0c6446',
          800: '#0a4f38',
          900: '#083c2b',
        },
        /* Dorado del sello de acreditacion, solo para detalles */
        acred: {
          400: '#F3B70D',
          500: '#CF9013',
          600: '#a97210',
        },
        /* Alias heredados: apuntan al azul institucional para no romper clases existentes */
        engineering: {
          50:  '#eef3fa',
          100: '#d8e3f2',
          200: '#b3c7e3',
          300: '#8aa7d1',
          400: '#5f83ba',
          500: '#3d63a0',
          600: '#2a4f87',
          700: '#193F77',
          800: '#143163',
          900: '#0f2449',
          950: '#0a1830',
        },
        steel: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        emerald: {
          50:  '#eaf6f1',
          100: '#cdeadd',
          200: '#9dd5bf',
          300: '#66bd9d',
          400: '#33a17c',
          500: '#158a63',
          600: '#0F7B55',
          700: '#0c6446',
          800: '#0a4f38',
          900: '#083c2b',
        },
        unibague: {
          50:  '#eef3fa',
          100: '#d8e3f2',
          200: '#b3c7e3',
          300: '#8aa7d1',
          400: '#5f83ba',
          500: '#3d63a0',
          600: '#2a4f87',
          700: '#193F77',
          800: '#143163',
          900: '#0f2449',
        }
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
};
