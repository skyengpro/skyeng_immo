# Sky Immo frontend

React + Vite + Tailwind app served by the Frappe site at `/sky-immo`. Adapted from the
prototype in `doc/mon-immo`, connected to the real backend (`skyeng_immo/sky_immo/api.py`).

- `src/data/api.ts` is the only door to the server; `src/data/types.ts` mirrors its answers.
- `src/features/owner` are the landlord screens (also used by staff), `src/features/tenant` the tenant ones.
- Readability first: 17 px body text on phones, 48 px buttons, text under every tab icon,
  AA contrast, one main action per screen.

See the app README for build, dev server and tests.
