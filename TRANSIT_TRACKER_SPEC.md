# Awakening and Path Activation Transit Tracker
Phoenix Rebirth | soulReady | Claude Code Build Specification
Add to Railway Flask codebase

---

## WHAT THIS IS

A transit projection system that identifies personal awakening and path activation windows for each client by comparing major planetary transits against their natal chart.

This is NOT a prediction system. It is an approximation tool. Every output must carry a prominent disclaimer that these are estimated windows, not exact dates, and that individual response to transits varies significantly.

---

## FREEMIUM MODEL — NON-NEGOTIABLE

**Free Tier**
- One transit window calculation per profection year
- Resets on the client's solar return date (when Sun returns to exact natal position)
- NOT a calendar year reset. A profection year reset.

**Premium Tier**
- Maximum two updates per calendar month
- Same calculation, more frequent refresh for greater accuracy as planets move
- Premium is a future build — architecture must support it from the start

---

## TRANSITS TO TRACK

The following transits are flagged when they fall within a 3 to 6 month window of each other. When THREE OR MORE converge within that window it is flagged as a significant activation threshold.

**Major Personal Transits**
- Saturn crossing natal Ascendant
- Saturn crossing natal Sun
- Saturn crossing natal Moon
- Saturn crossing natal Midheaven
- Saturn crossing natal North Node
- Saturn Return (transiting Saturn conjunct natal Saturn) — approximately age 29 and 58
- Uranus opposition natal Uranus — approximately age 38 to 42 but varies by birth year
- Uranus square natal Uranus — approximately age 21 and 63 but varies by birth year
- Jupiter conjunct natal Neptune
- Jupiter conjunct natal Chiron
- Jupiter conjunct natal North Node
- Pluto conjunct natal Sun
- Pluto conjunct natal Moon
- Pluto conjunct natal Ascendant
- Pluto square natal Sun
- Pluto square natal Moon
- Nodal Return (transiting North Node conjunct natal North Node) — approximately every 18 to 19 years
- Solar Return proximity — the 7 days immediately before the solar return date

**Profection Year Activation**
- Current profection year house and ruling sign (calculated from Rising sign and current age)
- When the profection year lord (ruling planet of the activated sign) receives a major transit simultaneously

---

## CONVERGENCE FLAGGING LOGIC

If 3 or more tracked transits fall within a 3 to 6 month window of each other, flag the window as a Significant Activation Threshold.

| Transits Converging | Flag Level |
|---|---|
| 3 | Emerging Window |
| 4 to 5 | Active Window |
| 6 or more | Major Activation Window |

The 3 to 6 month convergence window is non-negotiable. Do not narrow it to exact dates.

---

## PROFECTION YEAR CALCULATION

Profection years cycle through the 12 houses starting from House 1 at birth.

- Age 0 = House 1 (Rising sign)
- Age 1 = House 2
- Age 2 = House 3
- Continuing through 12 houses then repeating

**Formula:** House = (age mod 12) + 1

The activated sign = the sign that rules that house in Whole Sign based on their Rising sign.
The activated planet = the ruling planet of that sign.

**Example:** Aquarius Rising, age 37
- 37 mod 12 = 1, so House 2 is activated
- House 2 in Whole Sign Aquarius Rising = Pisces
- Pisces ruler = Jupiter and Neptune
- Any major transit to Jupiter or Neptune that year is amplified

---

## EPHEMERIS SOURCE

Use the Swiss Ephemeris Python library (pyswisseph) for planetary position calculations. This is the same library used by professional astrology software. It is accurate, open source, and well documented.

Install: `pip install pyswisseph`

The library provides precise planetary positions for any date past, present, or future. Use it to calculate where transiting planets will be month by month over the next 3 years from the current date for each client.

**Do NOT hardcode approximate ages for Uranus opposition or Saturn return.** Calculate them precisely from each client's natal chart using actual ephemeris data. Christina's awakening at 36 proves that approximate ages are not accurate enough.

---

## DATA INPUTS REQUIRED

All of these already exist in the client record from intake:

- Date of birth (day, month, year)
- Time of birth
- Place of birth
- Natal chart data already calculated by Railway (use existing astrology output)
- Current age (calculated from DOB)
- Rising sign (already calculated)

---

## OUTPUT FORMAT

For each client the system returns:

**Current profection year details**
- Age, activated house, activated sign, activated planet(s)
- How long remaining in current profection year

**Transit window list for next 36 months**
- Each tracked transit with estimated date range
- Orb: flag when transiting planet is within 5 degrees of natal point

**Convergence windows flagged**
- Date range of convergence
- Which transits are overlapping
- Flag level (Emerging, Active, or Major)

**Prominent disclaimer on every output**

> "These are estimated activation windows based on planetary movement patterns. They are approximations, not predictions. Individual response to planetary transits varies significantly. This information is for self-awareness purposes only and is not a guarantee of any specific experience or timeline."

---

## DISPLAY IN APP

This feature lives in soulReady under a new section called: **Activation Window** or **Soul Path Timeline** (name TBD)

- Free tier clients see their current profection year details and one snapshot of the next convergence window
- Premium clients see the full 36 month transit map with all flagged convergence windows

---

## IMPORTANT NOTES FOR CLAUDE CODE

- Do NOT hardcode approximate ages for Uranus opposition or Saturn return. Calculate precisely from actual ephemeris data.
- The 3 to 6 month convergence window is non-negotiable. Do not narrow it to exact dates.
- The profection year reset for the free tier must be calculated from the exact solar return date, not January 1.
- Every output carries the disclaimer. No exceptions.
- This is a future premium feature. Build the architecture to support the freemium model from the start even if premium tier is not activated yet.

---

*Phoenix Rebirth | soulReady | Internal Build Specification | 2026*
