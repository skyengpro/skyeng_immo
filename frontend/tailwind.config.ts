import type { Config } from 'tailwindcss';

// Jetons frappe-ui 1.0.2, repris du prototype, avec deux ajustements pour un public âgé :
// - textes plus grands (base 17 px sur mobile, 16 px sur le web) ;
// - lien et badge bleu assombris pour atteindre le contraste AA (4,5:1), écart signalé par le prototype.
// La palette par défaut de Tailwind est remplacée, pas étendue : aucune couleur hors charte n'est disponible.
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    screens: {
      lg: '1024px',
    },
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      white: '#FFFFFF',
      surface: {
        base: '#FFFFFF',
        sidebar: '#F8F8F8',
        'gray-2': '#F3F3F3',
        'gray-3': '#EDEDED',
      },
      outline: {
        'gray-2': '#E2E2E2',
        'gray-3': '#C7C7C7',
      },
      ink: {
        'gray-9': '#0F0F0F',
        'gray-8': '#171717',
        'gray-6': '#525252',
        'gray-5': '#7C7C7C',
      },
      primary: {
        DEFAULT: '#171717',
        hover: '#383838',
        active: '#525252',
        text: '#FFFFFF',
      },
      link: '#0060B8',
      green: { bg: '#E4FAEB', ink: '#14804D' },
      orange: { bg: '#FFEFE4', ink: '#BD3E0C' },
      red: { bg: '#FFE7E7', ink: '#B41D1D' },
      yellow: { bg: '#FFF7D3', ink: '#9A6304' },
      blue: { bg: '#E6F4FF', ink: '#005AA8' },
      gray: { bg: '#F3F3F3', ink: '#525252' },
      overlay: 'rgb(15 15 15 / 0.4)',
    },
    fontFamily: {
      sans: ['"Inter Variable"', 'system-ui', 'sans-serif'],
    },
    fontSize: {
      xs: ['13px', '1.4'],
      sm: ['15px', '1.4'],
      base: ['16px', '1.45'],
      body: ['17px', '1.45'],
      lg: ['18px', '1.4'],
      xl: ['20px', '1.35'],
      '2xl': ['22px', '1.3'],
      '3xl': ['26px', '1.25'],
      '4xl': ['32px', '1.2'],
    },
    fontWeight: {
      normal: '420',
      medium: '500',
      semibold: '600',
    },
    borderRadius: {
      none: '0',
      DEFAULT: '8px',
      xl: '12px',
      full: '9999px',
    },
    boxShadow: {
      none: 'none',
      float: '0px 0px 1px rgba(0, 0, 0, 0.19), 0px 1px 2px rgba(0, 0, 0, 0.07), 0px 6px 15px -5px rgba(0, 0, 0, 0.11)',
      dialog: '0px 0px 1px rgba(0, 0, 0, 0.19), 0px 4px 8px rgba(0, 0, 0, 0.06), 0px 16px 32px -8px rgba(0, 0, 0, 0.16)',
    },
    extend: {
      maxWidth: {
        content: '1120px',
      },
      width: {
        sidebar: '256px',
      },
      spacing: {
        sidebar: '256px',
        tabbar: '68px',
        topbar: '56px',
      },
    },
  },
  plugins: [],
} satisfies Config;
