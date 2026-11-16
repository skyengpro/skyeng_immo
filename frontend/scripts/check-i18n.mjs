// Vérifie que fr.json et en.json ont exactement les mêmes clés et les mêmes variables {{…}},
// et que chaque valeur d'énumération affichée (statuts, types, catégories…) a sa traduction.
// Le typage TypeScript couvre les clés écrites en dur ; ce script couvre les clés construites.
import { readFileSync } from 'node:fs';

const load = (lang) => JSON.parse(readFileSync(new URL(`../src/i18n/${lang}.json`, import.meta.url), 'utf8'));
const dictionaries = { fr: load('fr'), en: load('en') };

function flatten(node, prefix = '', out = new Map()) {
  for (const [key, value] of Object.entries(node)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (value && typeof value === 'object') flatten(value, path, out);
    else out.set(path, String(value));
  }
  return out;
}

const flat = Object.fromEntries(Object.entries(dictionaries).map(([lang, dict]) => [lang, flatten(dict)]));
const errors = [];
const variables = (text) => [...text.matchAll(/{{\s*(\w+)\s*}}/g)].map((match) => match[1]).sort().join(',');

for (const [lang, other] of [['fr', 'en'], ['en', 'fr']]) {
  for (const key of flat[lang].keys()) {
    if (!flat[other].has(key)) errors.push(`${key} : présente en ${lang}, absente en ${other}`);
  }
}
for (const [key, text] of flat.fr) {
  const translated = flat.en.get(key);
  if (translated === undefined) continue;
  if (!text.trim() || !translated.trim()) errors.push(`${key} : texte vide`);
  if (variables(text) !== variables(translated)) errors.push(`${key} : variables différentes entre fr et en`);
}

// Clés au pluriel : chaque _one a son _other.
for (const key of flat.fr.keys()) {
  if (key.endsWith('_one') && !flat.fr.has(key.replace(/_one$/, '_other'))) errors.push(`${key} : forme _other manquante`);
}

// Clés construites dans le code (t(`status.${kind}.${value}`), etc.) : valeurs reprises de src/data/types.ts et de skyeng_immo/sky_immo/data.py.
const ENUMS = {
  'status.invoice': ['paid', 'due', 'overdue', 'partly_paid'],
  'status.schedule': ['paid', 'due', 'overdue', 'partly_paid', 'upcoming'],
  'status.lease': ['active', 'upcoming', 'notice_given', 'expired'],
  'status.property': ['let', 'available', 'ending_soon', 'renovation'],
  'status.issue': ['open', 'in_progress', 'on_hold', 'resolved', 'closed'],
  'status.deposit': ['received', 'partly_received', 'returned', 'requested', 'unknown'],
  'issue.statusHelp': ['open', 'in_progress', 'on_hold', 'resolved', 'closed'],
  frequency: ['monthly', 'bimonthly', 'quarterly', 'semiannual', 'annual'],
  per: ['monthly', 'bimonthly', 'quarterly', 'semiannual', 'annual'],
  issueCategory: ['plumbing', 'electricity', 'locksmith', 'painting', 'air_conditioning', 'other'],
  'language.short': ['fr', 'en'],
  roles: ['manager', 'owner', 'tenant'],
  errors: ['network', 'notFound', 'unauthorized', 'noAccess'].flatMap((kind) => [`${kind}.title`, `${kind}.body`]),
};
for (const [prefix, values] of Object.entries(ENUMS)) {
  for (const value of values) {
    const key = `${prefix}.${value}`;
    if (!flat.fr.has(key)) errors.push(`${key} : clé construite dans le code mais absente`);
  }
}

if (errors.length) {
  console.error(`Traductions incomplètes (${errors.length}) :\n- ${errors.join('\n- ')}`);
  process.exit(1);
}
console.log(`Traductions OK : ${flat.fr.size} clés en fr et en en.`);
