import preset, { content } from 'frappe-ui/tailwind'

// Sky-immo tokens. Every colour is a CSS variable (see src/style.css) so light and dark themes share
// one set of class names. Warm paper, deep ink, one sky blue; amber and red only for what needs action.
const v = (name) => `rgb(var(--si-${name}) / <alpha-value>)`

export default {
  presets: [preset],
  content: [...content, './index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Newsreader Variable"', 'Georgia', 'serif'],
        body: ['"Figtree Variable"', 'system-ui', 'sans-serif'],
      },
      colors: {
        paper: { DEFAULT: v('paper'), deep: v('paper-deep') },
        card: v('card'),
        ink: { DEFAULT: v('ink'), soft: v('ink-soft'), mute: v('ink-mute'), faint: v('ink-faint') },
        'on-ink': v('on-ink'),
        'on-sky': v('on-sky'),
        line: { DEFAULT: v('line'), strong: v('line-strong') },
        sky: { DEFAULT: v('sky'), deep: v('sky-deep'), mid: v('sky-mid'), soft: v('sky-soft'), mist: v('sky-mist') },
        ok: { DEFAULT: v('ok'), soft: v('ok-soft') },
        warn: { DEFAULT: v('warn'), mid: v('warn-mid'), soft: v('warn-soft') },
        alert: { DEFAULT: v('alert'), soft: v('alert-soft') },
        info: { DEFAULT: v('info'), soft: v('info-soft') },
      },
      // every rounded corner of the app, one value: --si-radius in src/style.css
      borderRadius: { app: 'var(--si-radius)' },
      boxShadow: {
        card: '0 1px 2px rgb(var(--si-shadow) / .05), 0 1px 1px rgb(var(--si-shadow) / .03)',
        lift: '0 14px 34px -14px rgb(var(--si-shadow) / .28), 0 2px 6px rgb(var(--si-shadow) / .06)',
      },
    },
  },
}
