# Sabian Symbols — Integration Specification
Phoenix Rebirth | soulReady | Claude Code Build Reference
Additional layer for ALL astrological readings

---

## WHAT SABIAN SYMBOLS ARE

360 symbolic images, one for each degree of the zodiac from Aries 1 through Pisces 30. Channeled in 1925 by clairvoyant Elsie Wheeler and astrologer Marc Edmund Jones in San Diego. Systematized and interpreted by Dane Rudhyar in his 1973 book An Astrological Mandala.

They are not predictions. They are archetypal images that reveal the specific soul story operating through a particular degree. Where the chakra degree layer tells you WHICH energy center is activated, the Sabian Symbol tells you the specific narrative or quality of that activation for that person.

These are two completely complementary layers. Neither replaces the other.

---

## PRIMARY REFERENCE

Dane Rudhyar — An Astrological Mandala: The Cycle of Transformations and Its 360 Symbolic Phases (1973, Vintage Books / Random House)

Marc Edmund Jones — The Sabian Symbols in Astrology (1953, Sabian Publishing Society) is the original source.

---

## ROUNDING RULE — NON-NEGOTIABLE

This is the single most important technical rule for correct Sabian Symbol calculation.

**IF a planet sits at exactly zero minutes (e.g. 5 degrees 00 minutes exactly):** Use the symbol for that degree (symbol 5)

**IF a planet has ANY minutes past the degree (e.g. 5 degrees 01 minutes or more):** Round UP to the next symbol (symbol 6)

**Examples:**
- 5 degrees 00 minutes = Symbol 5
- 5 degrees 01 minutes = Symbol 6
- 5 degrees 03 minutes = Symbol 6
- 5 degrees 45 minutes = Symbol 6
- 18 degrees 57 minutes = Symbol 19
- 29 degrees 12 minutes = Symbol 30
- 0 degrees 01 minutes of any sign = Symbol 1 of that sign

There is NO 0 degree symbol. Symbols are numbered 1 through 30 for each sign. There IS a 30 degree symbol. Any placement at 29 degrees and any minutes rounds up to 30.

This rule applies to EVERY planet and point in the chart without exception: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Chiron, Black Moon Lilith, North Node, South Node, Part of Fortune, Ascendant, Midheaven, Vertex, and any other calculated point.

---

## HOW TO CALCULATE THE SYMBOL NUMBER

1. Get the planet's exact position in degrees and minutes within its sign
2. Apply the rounding rule above
3. The resulting number (1-30) is the Sabian Symbol number for that sign

**Example:** Sun at Aries 18 degrees 57 minutes
- Has minutes past the degree, round up
- Symbol 19 of Aries

**Example:** North Node at Gemini 27 degrees 51 minutes
- Has minutes past the degree, round up
- Symbol 28 of Gemini

**Example:** Moon at Pisces 2 degrees 55 minutes
- Has minutes past the degree, round up
- Symbol 3 of Pisces

---

## WHERE SABIAN SYMBOLS ARE USED

Sabian Symbols are an ADDITIONAL LAYER within existing readings. They do not replace any existing layer. They layer on top of:
- Chakra degree mapping (Christina's proprietary system)
- Sign chakra mapping (locked zodiac to chakra colors)
- House chakra mapping (locked house chakra assignments)

Apply to ALL chart placements in every reading that includes astrology data.

**Integration points:**
- Soul Blueprint Tier 1 (all major placements)
- TCM Astrology Chakra Tier 1 (all planets in the wheel)
- Astrology tab in Raw Data (SoulBlueprintAdmin) for Christina's reference
- Any future reading that includes astrological chart data

---

## NODAL AXIS — BOTH SYMBOLS TOGETHER

When reading the North Node and South Node, always present BOTH symbols together as a paired story.
- South Node symbol = the past pattern or comfort zone
- North Node symbol = the soul's evolutionary direction

Always read them as a pair, never in isolation. The power of the nodal Sabian Symbols is in how they speak to each other across the axis.

---

## WHAT THE SYMBOL TELLS YOU

Each symbol has three elements worth noting in a reading:

**The IMAGE** — the brief poetic scene or figure channeled by Elsie Wheeler

**The KEYNOTE** — Rudhyar's one-line interpretive summary of the symbol's essence (do not reproduce verbatim — copyright)

**The RESONANCE** — how the image speaks to this specific person's chart placement. This is where the interpretive work happens. The image is not literal. It is archetypal.

---

## DISPLAY FORMAT

```
MERCURY — Taurus 3°10'
Chakra Degree: Throat (3°)
Sabian Symbol: [Symbol 4 of Taurus image text]
[Interpretive note relevant to Mercury placement]
```

---

## TECHNICAL BUILD NOTES FOR CLAUDE CODE

- Build a complete static lookup table of all 360 symbols (12 signs x 30 symbols each)
- Structure: `{ "Aries": { 1: "symbol text", 2: "symbol text", ... 30: "symbol text" }, "Taurus": {...}, ... }`
- No external API needed. Pure lookup by sign and degree number after rounding is applied.
- The 360 Sabian Symbol images (Wheeler/Jones originals) are in the public domain — reference freely
- Rudhyar's interpretive keynotes from An Astrological Mandala are under copyright — do not reproduce verbatim
- The rounding rule must be applied consistently across every placement in every chart for every client. No exceptions.

---

*Phoenix Rebirth | soulReady | Sabian Symbols Integration Spec | 2026*
*Reference: An Astrological Mandala, Dane Rudhyar, 1973*
*Original source: Marc Edmund Jones and Elsie Wheeler, 1925*
