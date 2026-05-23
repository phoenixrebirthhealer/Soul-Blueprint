/**
 * Phoenix Rebirth | soulReady
 * MASTER CONSTANTS — All lookup tables from MASTER_NON_NEGOTIABLES.md
 * Import from this file in all reading generation scripts.
 * Never hardcode these values anywhere else.
 */

// ─────────────────────────────────────────────
// CHAKRA COLORS — canonical hex values
// ─────────────────────────────────────────────
export const CHAKRA_COLORS = {
  'Root':        '#CC2244',
  'Sacral':      '#FF6D00',
  'Solar Plexus':'#DDC000',
  'Heart':       '#00C853',
  'Throat':      '#0091EA',
  'Third Eye':   '#6200EA',
  'Crown':       '#AA00FF',
};

// ─────────────────────────────────────────────
// SECTION 6 — DEGREE CHAKRA MAP (0-29)
// Proprietary. Never replace with any other system.
// ─────────────────────────────────────────────
export const DEGREE_CHAKRA = {
  0:  'Crown',
  1:  'Solar Plexus',
  2:  'Heart',
  3:  'Throat',
  4:  'Third Eye',
  5:  'Third Eye',
  6:  'Throat',
  7:  'Heart',
  8:  'Solar Plexus',
  9:  'Sacral',
  10: 'Root',
  11: 'Root',
  12: 'Sacral',
  13: 'Solar Plexus',
  14: 'Heart',
  15: 'Throat',
  16: 'Third Eye',
  17: 'Third Eye',
  18: 'Throat',
  19: 'Heart',
  20: 'Solar Plexus',
  21: 'Sacral',
  22: 'Root',
  23: 'Root',
  24: 'Sacral',
  25: 'Solar Plexus',
  26: 'Heart',
  27: 'Throat',
  28: 'Third Eye',
  29: 'Crown',
};

// Returns chakra name for a given degree integer
export function getDegreeChakra(degree) {
  const d = Math.floor(degree);
  return DEGREE_CHAKRA[d] ?? null;
}

// ─────────────────────────────────────────────
// DEGREE TYPE RULES — Section 6
// ─────────────────────────────────────────────
const CARDINAL_SIGNS  = ['Aries', 'Cancer', 'Libra', 'Capricorn'];
const FIXED_SIGNS     = ['Taurus', 'Leo', 'Scorpio', 'Aquarius'];
const MUTABLE_SIGNS   = ['Gemini', 'Virgo', 'Sagittarius', 'Pisces'];

export function getDegreeType(degree, sign) {
  const d = Math.floor(degree);
  const types = [];
  if (d === 0 && CARDINAL_SIGNS.includes(sign)) types.push('Cardinal');
  if ([8, 9, 21, 22].includes(d) && FIXED_SIGNS.includes(sign)) types.push('Fixed Critical');
  if ([4, 17].includes(d) && MUTABLE_SIGNS.includes(sign)) types.push('Mutable Critical');
  if ([0, 15].includes(d)) types.push('Critical');
  if (d === 25) types.push('Karmic');
  if (d === 29) types.push('Anaretic');
  return types.length > 0 ? types.join(', ') : 'Standard';
}

// ─────────────────────────────────────────────
// SECTION 7 — ZODIAC CHAKRA MAP
// Locked. Never changes.
// ─────────────────────────────────────────────
export const ZODIAC_CHAKRA = {
  'Aries':       { chakra: 'Solar Plexus', color: '#DDC000' },
  'Taurus':      { chakra: 'Heart',        color: '#00C853' },
  'Gemini':      { chakra: 'Throat',       color: '#0091EA' },
  'Cancer':      { chakra: 'Third Eye',    color: '#6200EA' },
  'Leo':         { chakra: 'Third Eye',    color: '#6200EA' },
  'Virgo':       { chakra: 'Throat',       color: '#0091EA' },
  'Libra':       { chakra: 'Heart',        color: '#00C853' },
  'Scorpio':     { chakra: 'Solar Plexus', color: '#DDC000' },
  'Sagittarius': { chakra: 'Sacral',       color: '#FF6D00' },
  'Capricorn':   { chakra: 'Root',         color: '#CC2244' },
  'Aquarius':    { chakra: 'Root',         color: '#CC2244' },
  'Pisces':      { chakra: 'Sacral',       color: '#FF6D00' },
};

// ─────────────────────────────────────────────
// SECTION 8 — HOUSE CHAKRA MAP
// Locked. Never changes for any client.
// ─────────────────────────────────────────────
export const HOUSE_CHAKRA = {
  1:  { chakra: 'Root',        color: '#CC2244' },
  2:  { chakra: 'Sacral',      color: '#FF6D00' },
  3:  { chakra: 'Solar Plexus',color: '#DDC000' },
  4:  { chakra: 'Heart',       color: '#00C853' },
  5:  { chakra: 'Throat',      color: '#0091EA' },
  6:  { chakra: 'Third Eye',   color: '#6200EA' },
  7:  { chakra: 'Heart',       color: '#00C853' },
  8:  { chakra: 'Sacral',      color: '#FF6D00' },
  9:  { chakra: 'Third Eye',   color: '#6200EA' },
  10: { chakra: 'Throat',      color: '#0091EA' },
  11: { chakra: 'Heart',       color: '#00C853' },
  12: { chakra: 'Crown',       color: '#AA00FF' },
};

// ─────────────────────────────────────────────
// SECTION 9 — TCM WHEEL GEOMETRY
// Planet zone: r=165 to r=210. Base r=187.
// Zodiac band: r=215 to r=253. Planets NEVER enter here.
// ─────────────────────────────────────────────
export const TCM_WHEEL = {
  center: { x: 320, y: 320 },
  planetZone: { inner: 165, outer: 210, base: 187 },
  zodiacBand: { inner: 215, outer: 253 },
  houseBand:  { inner: 257, outer: 287 },
};

/**
 * Calculate SVG x,y for a planet given its ecliptic longitude and the
 * rising sign's start degree.
 * @param {number} longitude   - planet ecliptic longitude in degrees
 * @param {number} risingStart - ecliptic start degree of Rising sign
 * @param {number} r           - placement radius (default: TCM_WHEEL.planetZone.base)
 */
export function planetXY(longitude, risingStart, r = TCM_WHEEL.planetZone.base) {
  const svgAngle = ((longitude - risingStart + 270) % 360 + 360) % 360;
  const rad = svgAngle * Math.PI / 180;
  return {
    x: +(TCM_WHEEL.center.x + r * Math.cos(rad)).toFixed(1),
    y: +(TCM_WHEEL.center.y + r * Math.sin(rad)).toFixed(1),
    svgAngle,
  };
}

// ─────────────────────────────────────────────
// SECTION 10 — NUMEROLOGY CHAKRA KEY
// Proprietary Phoenix Rebirth system.
// ─────────────────────────────────────────────
export const NUMEROLOGY_CHAKRA_KEY = {
  0: 'Soul in Purest Form',
  1: 'Root',
  2: 'Sacral',
  3: 'Solar Plexus',
  4: 'Heart',
  5: 'Throat',
  6: 'Third Eye',
  7: 'Crown',
  8: 'Soul Star',
  9: 'Earth Star',
};

// Letter values A=1 through Z=26. Master numbers 11, 22, 33 never reduced.
export const LETTER_VALUES = {
  A:1,  B:2,  C:3,  D:4,  E:5,  F:6,  G:7,  H:8,  I:9,
  J:10, K:11, L:12, M:13, N:14, O:15, P:16, Q:17, R:18,
  S:19, T:20, U:21, V:22, W:23, X:24, Y:25, Z:26,
};

export const MASTER_NUMBERS = new Set([11, 22, 33]);

// ─────────────────────────────────────────────
// SECTION 5 — HUMAN DESIGN MAPS
// ─────────────────────────────────────────────
export const HD_DIGESTION = {
  1: { left: 'Consecutive',  right: 'Alternating'  },
  2: { left: 'Open',         right: 'Closed'        },
  3: { left: 'Hot',          right: 'Cold'          },
  4: { left: 'Calm',         right: 'Nervous'       },
  5: { left: 'High Sound',   right: 'Low Sound'     },
  6: { left: 'Direct Light', right: 'Indirect Light'},
};

export const HD_ENVIRONMENT = {
  1: { left: 'Selective Caves',  right: 'Blending Caves'    },
  2: { left: 'Internal Markets', right: 'External Markets'  },
  3: { left: 'Wet Kitchens',     right: 'Dry Kitchens'      },
  4: { left: 'Active Mountains', right: 'Passive Mountains' },
  5: { left: 'Narrow Valleys',   right: 'Wide Valleys'      },
  6: { left: 'Natural Shores',   right: 'Artificial Shores' },
};

export const HD_SENSE = {
  1: { left: 'Smell',       right: 'Smell'       },
  2: { left: 'Taste',       right: 'Taste'       },
  3: { left: 'Outer Vision',right: 'Outer Vision'},
  4: { left: 'Inner Vision',right: 'Inner Vision'},
  5: { left: 'Feeling',     right: 'Feeling'     },
  6: { left: 'Touch',       right: 'Touch'       },
};

export const HD_STRATEGY = {
  'Generator':           'Wait to Respond',
  'Manifesting Generator': 'Wait to Respond and Inform',
  'Projector':           'Wait for the Invitation',
  'Manifestor':          'Inform before Acting',
  'Reflector':           'Wait a Lunar Cycle',
};

// Tone 1-3 = left arrow, Tone 4-6 = right arrow
export function hdArrow(tone) {
  return tone >= 1 && tone <= 3 ? 'left' : 'right';
}

// Authority: anyone with defined Solar Plexus = Emotional, never Sacral
export function hdAuthority(type, definedCenters) {
  if (['Generator', 'Manifesting Generator'].includes(type) &&
      definedCenters.includes('Solar Plexus')) {
    return 'Emotional Authority';
  }
  return null; // caller must determine from full chart data
}

// ─────────────────────────────────────────────
// SECTION 17 — PRICING (locked)
// ─────────────────────────────────────────────
export const PRICING = {
  'Name Frequency Reading':                  { price: 9.99,  gate: null },
  'Relational Name Frequency Tier 1':        { price: 9.99,  gate: null },
  'Relational Name Frequency Tier 2':        { price: 9.99,  gate: null },
  'Relational Name Frequency Tier 3':        { price: 9.99,  gate: null },
  'Relational Tiers 2+3':                    { price: 16.99, gate: 'After Tier 1' },
  'Relational Tiers 1+2+3':                  { price: 24.99, gate: null },
  'Self-Love Language Reading':              { price: 77,    gate: null },
  "Soul's Journey Reading":                  { price: 47,    gate: 'Self-Love Language + reassessment' },
  'TCM Astrology Chakra Tier 1':             { price: 55,    gate: null },
  'TCM Astrology Chakra Tier 2 Deep Dive':   { price: 110,   gate: null },
  'Soul Blueprint Decoder Tier 1':           { price: 77,    gate: null },
  'Soul Blueprint Decoder Tier 2':           { price: 325,   gate: null },
  'Field Frequency Scan':                    { price: 75,    gate: 'Credited toward session' },
  'Rapid Relief Session':                    { price: 225,   gate: null },
  'Mild Session':                            { price: 275,   gate: null },
  'Chronic Session':                         { price: 475,   gate: null },
  'Guidance Session':                        { price: 450,   gate: null },
  'Oracle and Tarot Reading':                { price: 575,   gate: null },
  'HarmonyHub':                              { price: 35,    gate: 'Practitioners only', per: 'year' },
};

// ─────────────────────────────────────────────
// HTML VISUAL IDENTITY TOKENS — Section 4
// Use these CSS values in every HTML reading template.
// ─────────────────────────────────────────────
export const HTML_TOKENS = {
  backgroundGradient: 'linear-gradient(135deg, #2D0A3E, #3D1155, #6B1E7A, #C2185B)',
  gold:        '#D4AF37',
  goldLight:   '#F0D060',
  goldPale:    '#FFF8DC',
  magenta:     '#C2185B',
  pinkBlush:   '#F8BBD0',
  plumDeep:    '#2D0A3E',
  plumMid:     '#4A0E5E',
  fontBody:    "'Cormorant Garamond', serif",
  fontHeaders: "'Cinzel', serif",
};

// ─────────────────────────────────────────────
// PDF VISUAL IDENTITY TOKENS — Section 3
// White background always on PDFs.
// ─────────────────────────────────────────────
export const PDF_TOKENS = {
  background: '#FFFFFF',
  plumDeep:   '#1a0a2e',
  plumMid:    '#2d1054',
  magenta:    '#c2185b',
  gold:       '#d4af37',
  fontBody:   'Lora',
  fontHeaders:'Cinzel',
};

// ─────────────────────────────────────────────
// SOVEREIGN BOUNDARIES — Section 14
// Never include any of these in any reading.
// ─────────────────────────────────────────────
export const SOVEREIGN_BOUNDARIES = [
  'Womb Reading',
  'Birth Trauma',
  'Conception',
  'In Utero',
  'Portal work (except Soul Guardian)',
  'Mirror Work after midnight',
  'Frequency Matching down',
];

// ─────────────────────────────────────────────
// FORBIDDEN LANGUAGE — Section 1
// Replace any use of these terms immediately.
// ─────────────────────────────────────────────
export const FORBIDDEN_TERMS = {
  'medicine':   'Rebirth',
  'disorder':   'wiring pattern',
  'condition':  'wiring pattern',
  'diagnosis':  'wiring pattern',
};
