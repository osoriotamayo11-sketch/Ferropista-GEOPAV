import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from '@/components/ThemeProvider';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'Ferropista Cordillera Central | Análisis del Semillero GEOPAV',
  description: 'Análisis académico de la propuesta de túnel de base ferroviario Ferropista en el tramo Ibagué – Armenia. Semillero de Investigación GEOPAV, Universidad de Ibagué, Semestre Paz y Región 2026B. Basado en la ponencia de ARCS / UC Consult (2025).',
  keywords: [
    'Ferropista',
    'Cordillera Central',
    'Proyecto Intermodal',
    'Ibagué',
    'Armenia',
    'Túnel de base',
    'Alto de La Línea',
    'Ingeniería Colombia',
    'Semillero GEOPAV',
    'Universidad de Ibagué'
  ],
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL
      ?? (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000')
  ),
  authors: [{ name: 'Semillero de Investigación GEOPAV — Universidad de Ibagué' }],
  openGraph: {
    title: 'Ferropista Cordillera Central | Análisis del Semillero GEOPAV',
    description: 'Trabajo académico del Semillero GEOPAV (Universidad de Ibagué) sobre la propuesta de túnel de base ferroviario entre Ibagué y Armenia. Las cifras provienen de la ponencia de ARCS / UC Consult (2025) y están en verificación.',
    url: undefined,
    siteName: 'Ferropista — Análisis Semillero GEOPAV',
    locale: 'es_CO',
    type: 'website',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Ferropista Cordillera Central - Proyecto Intermodal Ibagué Armenia',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Ferropista Cordillera Central | Análisis del Semillero GEOPAV',
    description: 'Transformación del transporte de carga en la Cordillera Central de Colombia.',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning className={`${inter.variable} scroll-smooth`}>
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-800 antialiased selection:bg-uni-700 selection:text-white">
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
