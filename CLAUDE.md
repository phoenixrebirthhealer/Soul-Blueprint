# Phoenix Rebirth | soulReady | Claude Code Project Brief
**Owner:** Christina Stevens | Hobbs, NM
**GitHub Repo:** phoenixrebirthhealer/Soul-Blueprint
**GitHub Pages:** phoenixrebirthhealer.github.io/Soul-Blueprint/
**Last Updated:** May 2026

Read this file completely before doing anything in this repository.

---

## WHO CHRISTINA IS AND HOW SHE WORKS

- Founder of Phoenix Rebirth (parent brand), Awakening Catalyst and Soul Liberation Guide
- Neurodivergent with 23 confirmed wiring patterns
- Communicates directly with frequent profanity as part of authentic voice
- Works one topic at a time
- Ask ONE question at a time only — never back-to-back questions
- Does not do code — every single coding instruction must show EXACTLY what is currently in the file AND exactly what replaces it. No partial instructions. No "find this section." Show full before and full after every time, no exceptions.

---

## HARD RULES — APPLY TO ALL WORK ALWAYS

- NEVER use em dashes anywhere, ever, in any output
- NEVER use the word "medicine" — always say "Rebirth"
- Master numbers (11, 22, 33) are NEVER reduced under any circumstances
- Hebrew letter values and numerology values are completely separate systems — never mix them
- NOT NOW never becomes "No"
- NEVER use disorder, condition, or diagnosis — always use: wiring pattern, neurological architecture, soul chosen processing difference, nervous system design
- The Soul Blueprint system activates Rebirths — it does not give advice
- Profanity is expected when it serves truth
- NEVER assume data — always read exactly what is provided, never generate from memory or training
- Plain language always — write at a level accessible to someone who knows nothing about the system

---

## BRAND AND NAME RULES

- **Christina Stevens** = name for ALL Phoenix Rebirth, soulReady, and HarmonyHub work
- **Aurelia Reign** = name for Aurelia Alchemia products ONLY — never for any other brand
- Never swap these two names under any circumstances

| Brand | Purpose | Name |
|---|---|---|
| Phoenix Rebirth | Parent authority brand | Christina Stevens |
| soulReady | App and reading platform (Base44) | Christina Stevens |
| Aurelia Alchemia | Apothecary arm | Aurelia Reign only |
| HarmonyHub | Practitioner platform ($35/year) | Christina Stevens |

---

## READING DELIVERY FORMAT — NON-NEGOTIABLE

Every reading is delivered as a standalone interactive HTML file hosted on GitHub Pages. No AI generation on the delivery end. AI generates content. Content goes into a locked HTML template. Client sees a beautiful interactive page.

- Fonts: Cormorant Garamond (body) + Cinzel (headers/labels)
- HTML readings: dark gradient background `linear-gradient(135deg, #2D0A3E, #3D1155, #6B1E7A, #C2185B)`
- PDFs: WHITE background always — deep plum, magenta, gold accents only — never dark backgrounds on PDFs
- Each reading type has its own distinct template that never changes structurally
- Header: soulReady | Phoenix Rebirth
- Footer: Phoenix Rebirth • soulReady • [Reading Name] • Proprietary System • [Year]

### PDF Colors
- Deep plum: #1a0a2e or #2d1054
- Magenta: #c2185b
- Gold: #d4af37

### HTML Colors
- Gold: #D4AF37 | Gold-light: #F0D060 | Gold-pale: #FFF8DC
- Magenta: #C2185B | Pink-blush: #F8BBD0

---

## TCM ASTROLOGY CHAKRA WHEEL — TEMPLATE SPEC

### Locked Forever — Never Changes
- 12 house positions, house numbers 1-12, house chakra colors in outer band
- Ring geometry, borders, dividers, center circle
- SVG coordinate system: viewBox="0 0 640 640", center (320,320)
- Tooltip structure, tab structure (Harmonies / Tensions / Healing Paths), legend
- Header branding and footer

### Ring Boundaries
| Ring | Inner r | Outer r |
|---|---|---|
| House band | 257 | 287 |
| Zodiac band | 215 | 253 |
| Planet zone | 165 | 210 |

**Planet zone base radius: r=187. Planets NEVER enter zodiac band (r=215 to r=253). Ever.**

### Planet Placement Formula
```
svgAngle = (longitude - risingStart + 270) mod 360
x = 320 + r * cos(svgAngle * PI/180)
y = 320 + r * sin(svgAngle * PI/180)
```
risingStart = ecliptic start degree of Rising sign (Aries=0, Taurus=30, Gemini=60, Cancer=90, Leo=120, Virgo=150, Libra=180, Scorpio=210, Sagittarius=240, Capricorn=270, Aquarius=300, Pisces=330)

Dot sizes: major planets r=13 (font 11), minor planets r=11 (font 10), label planets r=10 (font 8)

### Zodiac Label Rotation
- Houses 1-3 (midAngles 15, 45, 75): rotate = midAngle + 360
- Houses 4-12 (midAngles 105-345): rotate = midAngle
- Label x,y at r=234 using midAngle - 90

### Dynamic Per Client
- Rising sign determines zodiac band rotation — Rising always sits at House 1 (top)
- All zodiac sign labels and colors in middle band
- All planet positions (x,y from ecliptic longitude)
- All planet tooltip data (sign, house, chakra layers, degree type, summary)
- Birth activation box, sidebar patterns, medical layer, aspect entries, client header

### House Chakra Colors — Locked
| House | Chakra | Color |
|---|---|---|
| 1 | Root | #CC2244 |
| 2 | Sacral | #FF6D00 |
| 3 | Solar Plexus | #DDC000 |
| 4 | Heart | #00C853 |
| 5 | Throat | #0091EA |
| 6 | Third Eye | #6200EA |
| 7 | Heart | #00C853 |
| 8 | Sacral | #FF6D00 |
| 9 | Third Eye | #6200EA |
| 10 | Throat | #0091EA |
| 11 | Heart | #00C853 |
| 12 | Crown | #AA00FF |

### Zodiac Chakra Colors — Locked
| Sign | Chakra | Color |
|---|---|---|
| Aries | Solar Plexus | #DDC000 |
| Taurus | Heart | #00C853 |
| Gemini | Throat | #0091EA |
| Cancer | Third Eye | #6200EA |
| Leo | Third Eye | #6200EA |
| Virgo | Throat | #0091EA |
| Libra | Heart | #00C853 |
| Scorpio | Solar Plexus | #DDC000 |
| Sagittarius | Sacral | #FF6D00 |
| Capricorn | Root | #CC2244 |
| Aquarius | Root | #CC2244 |
| Pisces | Sacral | #FF6D00 |

---

## CHAKRA DEGREE MAPPING — PROPRIETARY AND LOCKED

Use ONLY this mapping for ALL chart work including planets, angles, Lilith, nodes. Never use any other degree system.

| Degree | Chakra | Degree | Chakra |
|---|---|---|---|
| 0 | Crown | 15 | Throat |
| 1 | Solar Plexus | 16 | Third Eye |
| 2 | Heart | 17 | Third Eye |
| 3 | Throat | 18 | Throat |
| 4 | Third Eye | 19 | Heart |
| 5 | Third Eye | 20 | Solar Plexus |
| 6 | Throat | 21 | Sacral |
| 7 | Heart | 22 | Root |
| 8 | Solar Plexus | 23 | Root |
| 9 | Sacral | 24 | Sacral |
| 10 | Root | 25 | Solar Plexus |
| 11 | Root | 26 | Heart |
| 12 | Sacral | 27 | Throat |
| 13 | Solar Plexus | 28 | Third Eye |
| 14 | Heart | 29 | Crown |

### Degree Type Definitions — Locked
- Cardinal: 0 of cardinal signs ONLY (Aries, Cancer, Libra, Capricorn) — NOT degrees 1, 2, 3
- Fixed critical: 8, 9, 21, 22 in fixed signs (Taurus, Leo, Scorpio, Aquarius)
- Mutable critical: 4, 17 in mutable signs (Gemini, Virgo, Sagittarius, Pisces)
- Critical all signs: 0 and 15
- Karmic all signs: 25
- Anaretic all signs: 29

---

## SABIAN SYMBOLS — INTEGRATION LAYER

Full specification: `SABIAN_SYMBOLS_SPEC.md`

Sabian Symbols are an additional interpretive layer on top of the chakra degree system. They apply to ALL chart placements in every reading with astrological data.

### Rounding Rule — Confirmed and Locked
- Zero minutes exactly = use that degree symbol
- ANY minutes past the degree = round UP to the next symbol
- No 45-minute threshold. No exceptions.

**Examples:** 5°00' = Symbol 5 | 5°01' = Symbol 6 | 18°57' = Symbol 19 | 29°12' = Symbol 30

### Applies To
Every planet and point: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Chiron, Black Moon Lilith, North Node, South Node, Part of Fortune, Ascendant, Midheaven, Vertex.

### Nodal Axis
Always present North Node and South Node Sabian Symbols together as a paired story. Never in isolation.

### Integration Points
- Soul Blueprint Tier 1
- TCM Astrology Chakra Tier 1
- Raw Data Astrology tab (SoulBlueprintAdmin)
- All future readings with astrological data

### Technical Build
Static lookup table of all 360 symbols hardcoded in codebase. No external API. Pure lookup by sign and degree number after rounding. Wheeler/Jones originals are public domain. Do not reproduce Rudhyar's keynotes verbatim (copyright).

---

## HUMAN DESIGN SYSTEM RULES

### Christina's Chart — Locked Forever
- Type: Generator 5/1 — NEVER Manifesting Generator, NEVER any other type
- Authority: Emotional Authority — NEVER Sacral Authority
- Profile: 5/1
- Defined Centers: Spleen, Sacral, Solar Plexus, G-Center, Root
- Undefined Centers: Heart/Ego, Throat, Ajna, Head
- Active Gates: 61, 11, 62, 12, 8, 10, 51, 57, 34, 50, 27, 28, 9, 55, 30, 60, 52, 58, 41
- Incarnation Cross: Left Angle Cross of the Clarion (51/57 | 61/62)

### Authority Rules — All Charts
- Emotional Authority ALWAYS takes precedence over Sacral
- Any Generator or MG with a defined Solar Plexus = Emotional Authority — never Sacral

### Strategy Rules — All Charts
- Manifesting Generator: Wait to Respond AND Inform (two-part, both required)
- Generator: Wait to Respond only (one part only — never add Inform)
- Projector: Wait for the Invitation
- Manifestor: Inform before Acting
- Reflector: Wait a Lunar Cycle

### Variable System
- Digestion = Color + Tone of Design Sun
- Environment = Color + Tone of Design North Node
- Design Sense = Tone of Design Sun
- Tone 1-3 = left arrow | Tone 4-6 = right arrow

### Digestion Map
| Color | Left | Right |
|---|---|---|
| 1 | Consecutive | Alternating |
| 2 | Open | Closed |
| 3 | Hot | Cold |
| 4 | Calm | Nervous |
| 5 | High Sound | Low Sound |
| 6 | Direct Light | Indirect Light |

### Environment Map (Design North Node)
| Color | Left | Right |
|---|---|---|
| 1 | Selective Caves | Blending Caves |
| 2 | Internal Markets | External Markets |
| 3 | Wet Kitchens | Dry Kitchens |
| 4 | Active Mountains | Passive Mountains |
| 5 | Narrow Valleys | Wide Valleys |
| 6 | Natural Shores | Artificial Shores |

### Design Sense Map (Design Sun)
| Tone | Left | Right |
|---|---|---|
| 1 | Smell | Smell |
| 2 | Taste | Taste |
| 3 | Outer Vision | Outer Vision |
| 4 | Inner Vision | Inner Vision |
| 5 | Feeling | Feeling |
| 6 | Touch | Touch |

---

## REPOSITORY STRUCTURE

The repo runs on Railway as a Python Flask API. Base44 calls this API for all astrology and Human Design calculations.

### Key Technical Facts
- HD_GATE_OFFSET_DEGREES = 1.75 (verified and fixed — do not change)
- Design date = true 88-degree solar arc binary search (NOT flat 88 days)
- Variable system uses Color/Tone from Design Sun and Design North Node (NOT Jupiter)

### Fixes Already Completed — Do Not Revert
- Channel definitions corrected with accurate center assignments
- Type determination rebuilt to check motor-to-Throat through actual channels
- Gate offset corrected from 1.97 to 1.75
- Design date changed from flat 88 days to true 88-degree solar arc
- Digestion/Environment/Design Sense rebuilt using Color/Tone system
- Incarnation Cross lookup table added (192 crosses by profile type)

### Channel Center Corrections — Verified
| Channel | Correct Assignment |
|---|---|
| 6-59 | Solar Plexus to Sacral |
| 19-49 | Root to Solar Plexus |
| 26-44 | Heart/Ego to Spleen |
| 35-36 | Throat to Solar Plexus |
| 37-40 | Solar Plexus to Heart/Ego |
| 42-53 | Sacral to Root |
| 20-57 | Throat to Spleen (was missing, now added) |

### Base44 Architecture
- `soulBlueprintApi.js` — calls Railway API, adapts response for Base44
- `SoulBlueprintAdmin.jsx` — admin control center for Christina
- `humanDesignCalculator.js` — legacy JS (superseded by Railway API)
- Incarnation Cross: auto-calculated from repository — manual entry removed

---

## NUMEROLOGY SYSTEM — PHOENIX REBIRTH PROPRIETARY

- Letter values: A=1 through Z=26 — no reduction ever on letter values
- Double digits: first digit leads, second integrates
- Master numbers 11, 22, 33: NEVER reduced — named as double frequency
- Chakra Key: 0=Soul in Purest Form, 1=Root, 2=Sacral, 3=Solar Plexus, 4=Heart, 5=Throat, 6=Third Eye, 7=Crown, 8=Soul Star, 9=Earth Star

---

## HEBREW SYSTEM — PHOENIX REBIRTH PROPRIETARY

- 22 Hebrew letters mapped to Metatron's Cube
- Hebrew letter values and numerology values are COMPLETELY SEPARATE SYSTEMS — never mix them
- Each letter has: position number, Hebrew name, English sound, elemental wound, elemental gift

---

## SELF-LOVE SCORING TIERS

| Tier | Score Range |
|---|---|
| Thriving Self-Love Foundation | 68 to 85 |
| Developing Self-Love Foundation | 51 to 67 |
| Emerging Self-Love Foundation | 34 to 50 |
| Low Self-Love Foundation | 0 to 33 |

---

## OVERCOMING SURVIVAL MODE PDF — TRIGGER LOGIC

- NEVER assumes survival mode
- Triggers when: Self-Love score 67 or below AND attachment style is one of: Pure Avoidant, Pure Anxious, Pure Disorganized, Disorganized Anxious Leaning, Disorganized Avoidant Leaning, True Disorganized Equal Split
- Score 33 or below triggers regardless of attachment style
- Framing: "In case you have ever felt like you are running on survival mode, this was created specifically for you based on your data"
- Data points: HD type and authority, Moon sign and degree, North and South Node, attachment style, Self-Love score range, Life Path number
- PDF format: WHITE background, deep plum, magenta, gold — standard PDF spec

---

## DIVINE FEMININE RECEIVING READING

- Free checklist unlocked only by chart-based engagement thresholds — never generic metrics
- Thresholds by HD type:
  - Generator: response patterns to chart-suggested resources
  - Manifesting Generator: breadth of engagement across multiple tools
  - Projector: depth over volume
  - Manifestor: quality of burst engagements, not login frequency
  - Reflector: consistent returns over 29 days, not intensity
- Authority layer thresholds: TBD pending Base44 behavioral data storage confirmation
- Paid full reading is always the CTA after free checklist
- Pulls from: Venus sign/house, Moon sign/house, Rising sign, Black Moon Lilith sign/degree/aspects, Venus aspects, Self-Love Language results

---

## AWAKENING AND PATH ACTIVATION TRANSIT TRACKER

Full specification: `TRANSIT_TRACKER_SPEC.md`

A transit projection system identifying personal awakening and path activation windows. An approximation tool, not a prediction system. Every output carries a prominent disclaimer.

### Freemium Model
- Free tier: one calculation per profection year, resets on solar return date (NOT January 1)
- Premium tier: maximum two updates per calendar month (future build — architecture must support it now)

### Convergence Flagging
3 to 6 month window. Three or more transits converging = Significant Activation Threshold.
- 3 transits = Emerging Window
- 4 to 5 = Active Window
- 6 or more = Major Activation Window

### Profection Year Formula
House = (age mod 12) + 1. Activated sign = sign ruling that house in Whole Sign based on Rising sign.

### Key Rule
Do NOT hardcode approximate ages for Uranus opposition or Saturn return. Calculate precisely from actual ephemeris data using pyswisseph.

---

## PENDING ITEMS TO ADD TO RAW DATA IN APP

- Job Title field in Intake Form (displays in Astrology tab under Dominant Modality with career alignment assessment: DIRECT CONFLICT, DIRECT ALIGNMENT, or timing-based not yet aligned)
- Annual Profection Year table based on Rising sign and age
- Sabian Symbols as additional layer in all readings

---

## SOVEREIGN BOUNDARIES — HARDCODED, NON-NEGOTIABLE

Never include, reference, or activate in any reading:
- Womb Reading: declined permanently
- Birth Trauma: not permitted
- Conception: not permitted
- In Utero: not permitted
- Portal work: Soul Guardian function only
- Mirror Work after midnight: absolute boundary
- Frequency Matching: UP ONLY, never down

---

## READINGS PRIORITY LIST

In order:
1. TCM Astrology Chakra Tier 1 — interactive HTML wheel (template in tcm-system/)
2. Soul Blueprint Decoder Tier 1 — six-system reading
3. Name Frequency Reading — $10.99
4. Relational Name Frequency — Tiers 1, 2, 3
5. Self-Love Language Reading — $82 PDF
6. Soul's Journey Reading — $47 (gated)
7. TCM Astrology Chakra Tier 2 Deep Dive — $110
8. Soul Blueprint Decoder Tier 2 — $325 with session

---

## PRICING — LOCKED

| Product | Price | Gate |
|---|---|---|
| Name Frequency Reading | $10.99 | None |
| Relational Name Frequency Tier 1 | $10.99 | None |
| Relational Name Frequency Tier 2 standalone | $10.99 | None |
| Relational Name Frequency Tier 3 standalone | $10.99 | None |
| Relational Tiers 2+3 together | $18.99 | After Tier 1 |
| Relational Tiers 1+2+3 together | $26.99 | None |
| Self-Love Language Reading | $82 | None |
| Soul's Journey Reading | $47 | Self-Love Language + reassessment |
| TCM Astrology Chakra Tier 1 | $59 | None |
| TCM Astrology Chakra Tier 2 Deep Dive | $110 | None |
| Soul Blueprint Decoder Tier 1 | $77 | None |
| Soul Blueprint Decoder Tier 2 with session | $325 | None |
| Field Frequency Scan | $75 | Credited toward session |
| Rapid Relief Session | $225 | None |
| Mild Session | $275 | None |
| Chronic Session | $475 | None |
| Guidance Session | $450 | None |
| Oracle and Tarot Reading | $575 | None |
| HarmonyHub | $35/year | Practitioners only |

---

## CHRISTINA'S CALIBRATION DATA — FOR TESTING ONLY

- Name Number: 205
- Life Path: raw 34, reduced 7
- Birthday: 9
- Hebrew Position 21: Shin convergence power point
- Hebrew Position 9: Tet triple activation
- Elemental wound: Air
- Human Design: Generator 5/1, Emotional Authority, Left Angle Cross of the Clarion (51/57 | 61/62)
- Defined Centers: Spleen, Sacral, Solar Plexus, G-Center, Root
- Undefined Centers: Heart/Ego, Throat, Ajna, Head
- Rising sign: Aquarius
- Birth: April 9, 1983 | 2:17 AM | Hobbs, NM
- Specific birth degrees and full chart data are private and not listed here

---

*Phoenix Rebirth | Christina Stevens | Internal Reference | 2026*
*For Claude Code use only.*
