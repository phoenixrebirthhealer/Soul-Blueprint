bash

cat /home/claude/timing_layer.js
Output

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, PageBreak
} = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const hBorder = { style: BorderStyle.SINGLE, size: 1, color: "2D0A3E" };
const hBorders = { top: hBorder, bottom: hBorder, left: hBorder, right: hBorder };
const aBorder = { style: BorderStyle.SINGLE, size: 1, color: "C2185B" };
const aBorders = { top: aBorder, bottom: aBorder, left: aBorder, right: aBorder };

function h1(text) {
  return new Paragraph({ spacing: { before: 400, after: 200 },
    children: [new TextRun({ text, bold: true, size: 36, color: "2D0A3E", font: "Arial" })] });
}
function h2(text) {
  return new Paragraph({ spacing: { before: 300, after: 150 },
    children: [new TextRun({ text, bold: true, size: 28, color: "6B1E7A", font: "Arial" })] });
}
function h3(text) {
  return new Paragraph({ spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, size: 24, color: "C2185B", font: "Arial" })] });
}
function body(text) {
  return new Paragraph({ spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, size: 22, font: "Arial" })] });
}
function note(text) {
  return new Paragraph({ spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, size: 20, italics: true, color: "555555", font: "Arial" })] });
}
function rule(text) {
  return new Paragraph({ spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, size: 20, bold: true, color: "C2185B", font: "Arial" })] });
}
function divider() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "6B1E7A", space: 1 } },
    children: [new TextRun("")] });
}
function spacer() {
  return new Paragraph({ spacing: { before: 80, after: 80 }, children: [new TextRun("")] });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function hRow(cells, cols, accent) {
  return new TableRow({ tableHeader: true, children: cells.map((text, i) => new TableCell({
    borders: accent ? aBorders : hBorders,
    width: { size: cols[i], type: WidthType.DXA },
    shading: { fill: accent ? "C2185B" : "2D0A3E", type: ShadingType.CLEAR },
    margins: { top: 100, bottom: 100, left: 150, right: 150 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, size: 19, color: "FFFFFF", font: "Arial" })] })]
  }))});
}
function dRow(cells, cols, shade) {
  return new TableRow({ children: cells.map((text, i) => new TableCell({
    borders,
    width: { size: cols[i], type: WidthType.DXA },
    shading: { fill: shade || "FFFFFF", type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 150, right: 150 },
    children: [new Paragraph({ children: [new TextRun({ text, size: 19, font: "Arial" })] })]
  }))});
}

const CW = 15120; // landscape content width

// ============================================================
// TABLE 1: ANNUAL PROFECTIONS — HOUSE TO AGE MAPPING
// ============================================================
const profCols = [800, 1200, 1400, 1600, 9120];
const profTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: profCols, rows: [
  hRow(["House", "Ages (repeating)", "Chakra", "Time Lord (sign ruler)", "Health and Life Theme for That Year"], profCols),
  dRow(["1st", "0,12,24,36,48,60,72,84", "Root", "Ruler of Rising sign", "Physical body, identity, and vitality are the year's primary theme. Health events in a 1st house profection year directly involve the physical constitution. The Rising sign's body areas are most activated. Time Lord governs the year's health curriculum."], profCols, "FFF8F0"),
  dRow(["2nd", "1,13,25,37,49,61,73,85", "Sacral", "Ruler of 2nd house sign", "Resources, metabolism, throat and thyroid health, and self-worth are the year's focus. Financial stress manifests physically in the 2nd house body areas. Time Lord governs resource and metabolic patterns."], profCols, "FFFFFF"),
  dRow(["3rd", "2,14,26,38,50,62,74,86", "Solar Plexus", "Ruler of 3rd house sign", "Nervous system, respiratory health, communication patterns, and sibling relationships are activated. Time Lord governs nervous system and respiratory curriculum for the year."], profCols, "FFF8F0"),
  dRow(["4th", "3,15,27,39,51,63,75,87", "Heart", "Ruler of 4th house sign", "Home, roots, stomach health, and emotional foundation are the year's primary theme. Family health events and emotional body patterns are most active. Time Lord governs domestic and foundational health."], profCols, "FFFFFF"),
  dRow(["5th", "4,16,28,40,52,64,76,88", "Throat", "Ruler of 5th house sign", "Creativity, heart health, spine, and joy are activated. Children's health may become relevant. Suppressed creativity creates physical patterns in the 5th house body areas. Time Lord governs cardiac and creative health."], profCols, "FFF8F0"),
  dRow(["6th", "5,17,29,41,53,65,77,89", "Third Eye", "Ruler of 6th house sign", "PRIMARY HEALTH YEAR. The 6th house profection year is the most significant health year in the cycle. Chronic health patterns surface. Daily routines and digestion are the year's focus. Time Lord is the primary health Time Lord for the year."], profCols, "FFFFFF"),
  dRow(["7th", "6,18,30,42,54,66,78,90", "Heart", "Ruler of 7th house sign", "Partnership, kidney health, skin, and lower back are the year's theme. Relationship stress manifests physically in 7th house body areas. Legal and contract matters may have health implications. Time Lord governs partnership and kidney health."], profCols, "FFF8F0"),
  dRow(["8th", "7,19,31,43,55,67,79,91", "Sacral", "Ruler of 8th house sign", "Transformation, reproductive health, elimination, and shared resources are activated. Surgery, inheritance, and deep health transformations are most likely in 8th house years. Time Lord governs reproductive and eliminative health."], profCols, "FFFFFF"),
  dRow(["9th", "8,20,32,44,56,68,80,92", "Third Eye", "Ruler of 9th house sign", "Philosophy, belief systems, hip and liver health, and long-distance travel are the year's theme. Belief system disruptions create physical patterns in 9th house body areas. Time Lord governs hip and liver health."], profCols, "FFF8F0"),
  dRow(["10th", "9,21,33,45,57,69,81,93", "Throat", "Ruler of 10th house sign", "Career, reputation, skeletal health, and public authority are activated. Career pressure manifests physically in 10th house body areas. Time Lord governs structural and career health."], profCols, "FFFFFF"),
  dRow(["11th", "10,22,34,46,58,70,82,94", "Heart", "Ruler of 11th house sign", "Community, circulation, ankle health, and collective belonging are the year's theme. Community belonging (or its absence) affects cardiovascular health. Time Lord governs circulatory and community health."], profCols, "FFF8F0"),
  dRow(["12th", "11,23,35,47,59,71,83,95", "Crown", "Ruler of 12th house sign", "Hidden health patterns, immune function, lymphatic health, and subconscious patterns are activated. The 12th house profection year often surfaces conditions that have been building below conscious awareness. Time Lord governs immune and hidden health patterns."], profCols, "FFFFFF"),
]});

// ============================================================
// TABLE 2: TIME LORD HEALTH IMPLICATIONS
// ============================================================
const tlCols = [1200, 1200, 1200, 11520];
const tlTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: tlCols, rows: [
  hRow(["Planet Time Lord", "Chakra", "Classification", "Health Implications When Active as Time Lord"], tlCols),
  dRow(["Sun", "Third Eye", "Benefic", "A Sun Time Lord year supports vitality, cardiovascular health, and physical identity. The body's vital force is the year's primary theme. When Sun is afflicted in the natal chart, its Time Lord year may surface those afflictions more acutely."], tlCols, "FFF8F0"),
  dRow(["Moon", "Third Eye", "Benefic/Variable", "A Moon Time Lord year activates emotional digestion, fluid regulation, and hormonal patterns. The emotional body and physical health are most directly connected this year. Lunar cycles carry heightened physical significance."], tlCols, "FFFFFF"),
  dRow(["Mercury", "Throat", "Neutral", "A Mercury Time Lord year activates the nervous system, respiratory health, and the communication-body interface. Nervous system patterns and respiratory health are the year's primary physical focus."], tlCols, "FFF8F0"),
  dRow(["Venus", "Heart", "Lesser Benefic", "A Venus Time Lord year supports kidney function, hormonal balance, and skin health. Self-love practices have direct physical health implications this year. When Venus is afflicted natally, kidney and hormonal patterns may surface."], tlCols, "FFFFFF"),
  dRow(["Mars", "Solar Plexus", "Lesser Malefic", "A Mars Time Lord year activates inflammatory patterns, adrenal function, and physical drive. Accidents, acute inflammatory events, and surgical interventions are most likely in Mars Time Lord years. Physical output capacity is highest and most vulnerable simultaneously."], tlCols, "FFF8F0"),
  dRow(["Jupiter", "Sacral", "Greater Benefic", "A Jupiter Time Lord year expands the liver, hip, and metabolic systems. Health generally improves but overconsumption and over-expansion are the primary risks. The body's healing capacity is at its highest in Jupiter Time Lord years."], tlCols, "FFFFFF"),
  dRow(["Saturn", "Root", "Greater Malefic", "A Saturn Time Lord year is the most significant health year in any profection cycle. Chronic conditions surface, structural restrictions become visible, and karmic health patterns demand attention. Saturn Time Lord years require the most proactive health management. They are not punishment. They are the curriculum becoming visible."], tlCols, "FFF8F0"),
  dRow(["Uranus", "Third Eye", "Disruptive", "A Uranus Time Lord year brings sudden and unexpected health events. Neurological patterns and erratic physical experiences are characteristic. Conventional health approaches may be less effective. Innovative and unconventional interventions respond better."], tlCols, "FFFFFF"),
  dRow(["Neptune", "Crown", "Dissolving", "A Neptune Time Lord year activates immune vulnerability, mystery health patterns, and lymphatic health. Misdiagnosis is more likely. Spiritual alignment is the most effective health support. Substance sensitivity increases."], tlCols, "FFF8F0"),
  dRow(["Pluto", "Crown", "Transforming", "A Pluto Time Lord year activates deep cellular transformation, elimination organ health, and inherited health patterns. Profound health transformations, including conditions that permanently change how the person lives, are most likely in Pluto Time Lord years. The transformation is the health event."], tlCols, "FFFFFF"),
]});

// ============================================================
// TABLE 3: TRANSIT TIMING INDICATORS
// ============================================================
const transCols = [1800, 1800, 11520];
const transTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: transCols, rows: [
  hRow(["Transiting Planet", "Aspect to Natal Point", "Health Timing Implications"], transCols),
  dRow(["Saturn", "Conjunct natal Sun or Ascendant", "Classic indicator of lowered vitality, chronic health surfacing, or structural health challenge. Duration: 1-2 years as Saturn moves through. The body's structural systems are under maximum pressure. Skeletal, dental, and joint health are primary focus areas."], transCols, "FFF8F0"),
  dRow(["Saturn", "Conjunct, square, or oppose natal Moon", "Emotional suppression creating physical restriction. Fluid imbalances, digestive patterns, and lymphatic congestion are characteristic. Duration: months to a year. The emotional body's restriction becomes a physical health event."], transCols, "FFFFFF"),
  dRow(["Saturn", "Conjunct, square, or oppose 6th house ruler", "The health house ruler under Saturn's restriction. Chronic health patterns in the 6th house body areas surface for long-term management. Duration: 1-2 years. The health curriculum of the natal 6th house becomes visible and unavoidable."], transCols, "FFF8F0"),
  dRow(["Jupiter", "Conjunct natal Ascendant or 6th house ruler", "Recovery indicator. The body's healing capacity expands. Health improves. Overconsumption is the primary risk. Duration: months. The most favorable transit for recovery from illness or surgery."], transCols, "FFFFFF"),
  dRow(["Mars", "Conjunct natal Mars, Ascendant, or 6th house planets", "Acute inflammatory trigger. Accidents, surgery timing, and sudden onset conditions are most likely when Mars transits these points. Duration: days to weeks. The most precise short-term timing indicator for acute health events."], transCols, "FFF8F0"),
  dRow(["Mars", "Stationing retrograde near natal health points", "Maximum pressure point. A stationing Mars is at its slowest and most concentrated. When it stations near natal planets in health houses or near health-relevant natal points, the inflammatory force sits rather than moves through. Duration: weeks at the station point. The 2007 accident example: Mars stationing Rx in Gemini on November 15th, four days after the event, at maximum pressure on the natal North Node-Mars-Midheaven-Chiron configuration."], transCols, "FFFFFF"),
  dRow(["Uranus", "Conjunct natal Ascendant, Sun, or health planets", "Sudden onset health events. Unpredictable and neurologically-involved conditions. Duration: 1-2 years as Uranus moves through. The health event often arrives without conventional warning signs."], transCols, "FFF8F0"),
  dRow(["Neptune", "Conjunct natal Ascendant or 12th house ruler", "Immune vulnerability period. Mystery conditions and misdiagnosis are most likely. Duration: 1-3 years. Spiritual alignment is the most effective health support during Neptune transits."], transCols, "FFFFFF"),
  dRow(["Pluto", "Conjunct natal Ascendant, Sun, or health planets", "Deep cellular health transformation. Profound health events that permanently change the person's relationship to their body. Duration: 1-5 years. The transformation IS the health event, not an interruption to health."], transCols, "FFF8F0"),
  dRow(["Transiting Moon", "Conjunct natal 6th house planets or ruler", "Short-term health trigger. Duration: hours to a day. Most relevant for pinpointing the exact timing of acute events within a larger transit window. The Moon's sign at the time of a health event indicates which body areas are activated at that precise moment."], transCols, "FFFFFF"),
]});

// ============================================================
// TABLE 4: SURGERY AND PROCEDURE TIMING
// ============================================================
const surgCols = [2000, 13120];
const surgTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: surgCols, rows: [
  hRow(["Timing Factor", "Application for Surgery and Medical Procedure Timing"], surgCols),
  dRow(["Moon Phase — FAVOR", "Waning Moon (last quarter to new moon) is the most favorable window for surgery. Research confirms reduced bleeding and faster recovery during waning lunar phases. The body's fluid and inflammatory systems are in a releasing and reducing mode rather than a building and expanding mode."], surgCols, "FFF8F0"),
  dRow(["Moon Phase — AVOID", "Full Moon increases blood flow and inflammatory response. Surgery during a full moon carries higher risk of complications and slower recovery. Eclipses represent maximum energetic disruption and are to be avoided for any elective procedure. New Moon is the most neutral point if waning window is not available."], surgCols, "FFFFFF"),
  dRow(["Moon Void of Course — AVOID", "A void of course Moon (after its last major aspect before changing signs) means the energy of any action taken does not complete as intended. Elective surgery during Moon VOC carries risk of unexpected complications or outcomes that do not match the intended result."], surgCols, "FFF8F0"),
  dRow(["Moon Sign — AVOID", "Do not schedule surgery on the body part ruled by the sign the transiting Moon currently occupies. Moon in Aries: avoid head and facial surgery. Moon in Taurus: avoid throat and thyroid surgery. Moon in Gemini: avoid lung and shoulder surgery. Moon in Cancer: avoid stomach and breast surgery. Moon in Leo: avoid heart and spine surgery. Moon in Virgo: avoid abdominal and intestinal surgery. Moon in Libra: avoid kidney and lower back surgery. Moon in Scorpio: avoid reproductive and elimination surgery. Moon in Sagittarius: avoid hip and liver surgery. Moon in Capricorn: avoid knee and joint surgery. Moon in Aquarius: avoid ankle and circulatory surgery. Moon in Pisces: avoid foot and lymphatic surgery."], surgCols, "FFFFFF"),
  dRow(["Day of Week", "Tuesday (Mars-ruled) is traditionally favored for surgery because Mars governs cutting and precision intervention. Saturday (Saturn-ruled) is favored for procedures addressing chronic structural conditions. Sunday (Sun-ruled) supports vitality and recovery initiation. These are traditional preferences, not absolute rules."], surgCols, "FFF8F0"),
  dRow(["Mars Transit — FAVOR", "Mars aspecting the angles (Ascendant, Midheaven, Descendant, IC) supports surgical intervention. Mars trine or sextile natal Sun or Ascendant supports the body's capacity to handle physical intervention and recover."], surgCols, "FFFFFF"),
  dRow(["Mars Transit — AVOID", "Mars square or opposite natal Sun, Moon, or Ascendant increases surgical risk through elevated inflammatory response and reduced recovery capacity. Mars Rx periods are generally unfavorable for elective surgery as the energy is internalized rather than forward-moving."], surgCols, "FFF8F0"),
  dRow(["Jupiter Transit — FAVOR", "Jupiter transiting the 1st or 6th house supports recovery. The body's healing capacity is expanded. The most favorable recovery window available in any transit cycle."], surgCols, "FFFFFF"),
  dRow(["Saturn Transit — AVOID for Elective", "Saturn transiting the natal Sun, Moon, or Ascendant reduces vitality and slows recovery. Elective procedures during Saturn transits to these points carry higher risk of prolonged recovery and complications. Emergency procedures are not governed by electional timing."], surgCols, "FFF8F0"),
  dRow(["Eclipse Windows — AVOID", "Solar and Lunar eclipses represent maximum energetic disruption. Avoid elective surgery within two weeks of any eclipse. If emergency surgery occurs during an eclipse window, additional recovery support is warranted."], surgCols, "FFFFFF"),
]});

// ============================================================
// TABLE 5: SECONDARY PROGRESSIONS HEALTH INDICATORS
// ============================================================
const progCols = [2400, 12720];
const progTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: progCols, rows: [
  hRow(["Progression Indicator", "Health Timing Implications"], progCols),
  dRow(["Progressed Moon changing signs", "Every 2.5 years the Progressed Moon moves into a new sign. Each sign change shifts the emotional body's primary needs and physical focus areas. The sign the Progressed Moon enters governs the body areas most activated for the next 2.5 years."], progCols, "FFF8F0"),
  dRow(["Progressed Moon entering 6th house", "The most significant Progressed Moon health indicator. When the Progressed Moon enters the natal 6th house, health becomes a primary life focus for approximately 2.5 years. Chronic health patterns surface. Daily routines and digestion require conscious attention."], progCols, "FFFFFF"),
  dRow(["Progressed Moon entering 8th house", "Transformation and deep health events are the theme for 2.5 years. Reproductive and elimination health patterns surface. Surgery or significant medical interventions are most likely during this progression."], progCols, "FFF8F0"),
  dRow(["Progressed Moon entering 12th house", "Hidden health patterns and immune function are the theme for 2.5 years. Conditions that have been building below conscious awareness surface. Rest, retreat, and inner healing work are physiologically required during this progression."], progCols, "FFFFFF"),
  dRow(["Progressed New Moon", "A Progressed New Moon (Progressed Sun conjunct Progressed Moon) initiates a new 30-year cycle. The health implications depend on the sign and house of the Progressed New Moon. New health patterns, both challenges and improvements, are seeded at this point."], progCols, "FFF8F0"),
  dRow(["Progressed Full Moon", "A Progressed Full Moon (Progressed Sun opposite Progressed Moon) represents the culmination and peak of the current 30-year cycle. Health patterns that were seeded at the Progressed New Moon reach their maximum expression. Resolution or crisis is most likely at this point."], progCols, "FFFFFF"),
  dRow(["Progressed Moon harmonious to natal Sun or Ascendant", "Recovery indicator. The body's vitality and identity are supported by the emotional body's progression. The most favorable internal timing for healing and health improvement."], progCols, "FFF8F0"),
  dRow(["Progressed Moon square or oppose natal Sun or Ascendant", "Internal tension between the emotional body and physical vitality. Health challenges that have an internal, emotionally-driven quality. The body is processing something the emotions have not yet completed."], progCols, "FFFFFF"),
]});

// ============================================================
// TABLE 6: ANNUAL PROFECTION EXAMPLE — CHRISTINA STEVENS 2007
// ============================================================
const exCols = [2400, 12720];
const exTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: exCols, rows: [
  hRow(["Layer", "Christina Stevens — November 11, 2007 Car Accident Analysis"], exCols, true),
  dRow(["Age and Profection Year", "Age 24. 1st House Annual Profection Year (ages 0, 12, 24, 36, 48, 60). The 1st house is the physical body, identity, and personal reinvention. Theme for the year: new beginnings, personal reinvention, physical identity, and self-focus."], exCols, "FFF0F5"),
  dRow(["Rising Sign and Time Lords", "Aquarius Rising. Traditional Time Lord: Saturn Rx (traditional Aquarius ruler). Modern Time Lord: Uranus Rx (modern Aquarius ruler). Both retrograde. Both internalizing their force in the body areas they govern for the entire year."], exCols, "FFFFFF"),
  dRow(["Saturn Rx as Time Lord", "Saturn Rx in Scorpio in the 10th house. The Greater Malefic governing the structural and eliminative body system, retrograde, operating internally and privately. As Time Lord for a 1st house (physical body) profection year, Saturn Rx was the planetary authority over Christina's physical body and health for all of 2007."], exCols, "FFF0F5"),
  dRow(["Uranus Rx as Co-Time Lord", "Uranus Rx at Fixed critical 8°49' in Sagittarius in the 11th house. Governing the hip-sciatic-neurological system. Retrograde, building internal pressure at a Fixed critical degree. As co-Time Lord, Uranus Rx was building pressure in the hip and nervous system throughout 2007 before the November event."], exCols, "FFFFFF"),
  dRow(["Soul Misalignment Decision", "Friday November 9, 2007: Christina left massage therapy school (her soul-aligned holistic path) and decided not to return. This decision occurred two days before the accident. The soul misalignment decision preceded the physical event by 48 hours."], exCols, "FFF0F5"),
  dRow(["Transiting Mars Station", "Mars was transiting Gemini and stationed retrograde on November 15, 2007, four days after the accident. A stationing planet is at its slowest and most concentrated. Mars was at maximum pressure on the natal chart in the days immediately surrounding the accident."], exCols, "FFFFFF"),
  dRow(["Natal Aspects Activated", "Mars Sextile North Node natally. Transiting Mars in Gemini was moving through the natal North Node's sign, activating the natal Mars-North Node sextile. North Node Quincunx Midheaven natally: soul direction and career in awkward constant adjustment. Chiron Opposition Midheaven at 0°33': the Planetary Bridge directly opposing the career pinnacle. Venus Opposition Midheaven at 0°21': love values and career power in tightest opposition."], exCols, "FFF0F5"),
  dRow(["Transiting Moon at Event Time", "Moon in Sagittarius on November 11, 2007 at 7 PM PST. Sagittarius governs hips, thighs, sacrum, and sciatic nerve. The Moon was transiting directly through the primary body area of the most severe injury (right pelvis sheared) at the exact time of the accident. The Moon moved into Capricorn (knees, joints) on November 14, right as Mars stationed retrograde on November 15."], exCols, "FFFFFF"),
  dRow(["Lunar Phase", "Waxing Crescent at 2% illumination. One day into the new lunar cycle. The most initiatory point of the lunar cycle. New beginnings at the lunar level corresponded with new beginnings (forced) at the life level."], exCols, "FFF0F5"),
  dRow(["Injury Pattern and Body Map", "Right pelvis sheared, right knee shattered, right shin compound fracture, right ankle fractured. Right side = masculine/giving side in the Christina Stevens Body Map. Sagittarius (hips/sacrum, Jupiter Rx and Uranus Rx natal placements), Capricorn (knees, Saturn Rx natal placement), Aquarius (ankles, natal Rising sign) — three consecutive signs, all with natal planets or angles, all injured in sequence from hip to ankle."], exCols, "FFFFFF"),
  dRow(["System Confirmation", "This event is the primary calibration example for the medical astrology timing query tool. All layers confirmed simultaneously: 1st house profection year (physical body theme), Saturn Rx and Uranus Rx as Time Lords (structural and neurological body governors), Mars stationing Rx in North Node's sign (soul direction activation), Moon in the injury site sign at exact event time, 48-hour gap between soul misalignment decision and physical cost event. Physical cost of career misalignment confirmed as a chart-level pattern."], exCols, "FFF0F5"),
]});

// ============================================================
// TABLE 7: MEDICAL ASTROLOGY TIMING QUERY TOOL SPEC
// ============================================================
const specCols = [2400, 12720];
const specTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: specCols, rows: [
  hRow(["Query Component", "Specification for Build"], specCols),
  dRow(["User Inputs Required", "1. Birth date, time, and location (for natal chart generation via PySwisseph API). 2. Event date and time (for transit chart generation at event moment). 3. Body parts or regions involved (for body area to sign/house/planet mapping lookup). 4. Optional: nature of event (accident, illness onset, surgery, recovery)."], specCols, "FFF8F0"),
  dRow(["Step 1: Generate Natal Chart", "Use PySwisseph API to generate full natal chart from birth data. Extract: all planetary positions, house cusps, Ascendant, Midheaven, aspects. Run through the existing TCM Astrology Chakra System 5-layer framework to establish baseline health activation map."], specCols, "FFFFFF"),
  dRow(["Step 2: Calculate Profection Year", "Calculate age at time of event. Assign profection house (age mod 12, starting from 1st house at age 0). Identify the sign occupying that house in the natal chart. Identify the traditional and modern ruler of that sign as the Time Lord(s). Cross-reference Time Lord natal placement, aspects, and dignity."], specCols, "FFF8F0"),
  dRow(["Step 3: Generate Transit Chart", "Use PySwisseph API to generate planetary positions at the event date and time. Identify: which transiting planets are within 3° of natal planets in health houses (6th, 8th, 12th). Which transiting planets are within 3° of natal Ascendant, Sun, Moon, or Midheaven. Whether any transiting planet is stationing (within 2 weeks of station) near natal health points."], specCols, "FFFFFF"),
  dRow(["Step 4: Map Body Parts to Astrology", "Cross-reference the body parts or regions provided by the user against the sign body part mapping table (Section 4 of Tier 2 Backend Reference). Identify which natal planets occupy the signs governing those body areas. Identify which houses govern those body areas and whether they were activated by the profection year or transits."], specCols, "FFF8F0"),
  dRow(["Step 5: Cross-Reference Logic", "Run the following checks: Was the profection house a health house (6th, 8th, or 12th)? Was the Time Lord afflicted natally or by transit? Was transiting Mars within 3° of natal health points at the event time? Was transiting Mars stationing near natal health points? Was the natal Ascendant, Sun, or chart ruler under transit pressure? Did the transiting Moon occupy the sign governing the injured/ill body area at event time? Were the body areas involved governed by the natal sign or house of the activated profection year?"], specCols, "FFFFFF"),
  dRow(["Step 6: Generate Reading Output", "Produce a narrative reading that: names the profection year and its theme, identifies the Time Lord and its natal condition, identifies the key transits active at the event time, connects the body areas involved to their natal chart activations, states whether the event was written in the chart, identifies the decision or soul alignment factor if relevant, and provides the healing pathway based on the TCM body clock windows most relevant to the body areas involved."], specCols, "FFF8F0"),
  dRow(["Language Standards", "Never diagnose. Never predict future health events with certainty. Frame all findings as: this is what the chart indicates was active at this time. Use the same language standards as the Tier 2 Deep Dive reading: patterns, activations, curriculum, physical expression. The query tool illuminates what was written. It does not determine fate."], specCols, "FFFFFF"),
  dRow(["Pricing", "$97 standalone query. Available as add-on to existing Soul Blueprint or TCM reading holders at $47. One query per purchase. Results delivered as a formatted HTML reading in the same visual style as the TCM Tier 2 Deep Dive."], specCols, "FFF8F0"),
]});

// ============================================================
// TABLE 8: QUICK TIMING SUMMARY
// ============================================================
const qtCols = [2400, 4560, 8160];
const qtTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: qtCols, rows: [
  hRow(["Event Type", "Key Timing Indicators", "Primary Chart Factors to Check"], qtCols),
  dRow(["Acute Illness or Accident", "Transiting Mars or Moon hitting 6th or 8th house planets or natal Ascendant. Mars stationing near natal health points.", "Natal planets in 6th, 8th, 12th. Ascendant and its ruler. Mars natal placement and aspects. Annual Profection year and Time Lord."], qtCols, "FFF8F0"),
  dRow(["Chronic Illness Onset", "Transiting Saturn or outer planets hitting natal health points. 6th house profection year. Saturn as Time Lord.", "Saturn natal condition and aspects. Neptune natal condition. 6th house ruler and its transits. Profection year (ages 5, 17, 29, 41, 53, 65)."], qtCols, "FFFFFF"),
  dRow(["Surgery Timing (Elective)", "Waning Moon, Mars aspecting angles favorably, Jupiter transiting 1st or 6th house. Avoid Moon VOC, eclipses, Mars Rx.", "Moon phase and sign at proposed date. Mars transit condition. Jupiter transit condition. Natal 8th house ruler condition."], qtCols, "FFF8F0"),
  dRow(["Recovery Trajectory", "Jupiter or Venus transiting 1st or 6th house. Progressed Moon in harmonious aspect to natal Sun or Ascendant. Waxing Moon.", "Jupiter and Venus natal condition and current transits. Progressed Moon position and aspects. Annual Profection year Time Lord condition."], qtCols, "FFFFFF"),
  dRow(["Major Health Transformation", "Pluto or Uranus transiting natal Ascendant, Sun, or 6th house ruler. Progressed New or Full Moon. 8th house profection year.", "Pluto and Uranus natal condition and current transits. Progressed Moon phase. Annual Profection year (ages 7, 19, 31, 43, 55, 67 for 8th house)."], qtCols, "FFF8F0"),
  dRow(["Soul Misalignment Physical Cost", "Mars stationing near natal North Node, Midheaven, or Chiron. Venus Opposition Midheaven activation. 1st house profection year with Saturn or Mars as Time Lord.", "North Node natal aspects to Midheaven and Chiron. Venus Opposition Midheaven orb. Annual Profection year theme. Time Lord natal condition. Decision timing relative to event timing."], qtCols, "FFFFFF"),
]});

const doc = new Document({
  numbering: { config: [] },
  styles: { default: { document: { run: { font: "Arial", size: 22 } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 20160, height: 12240 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
        orientation: "landscape"
      }
    },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "MEDICAL ASTROLOGY TIMING LAYER", bold: true, size: 48, color: "2D0A3E", font: "Arial" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "Annual Profections, Transits, Progressions, and Electional Timing", bold: true, size: 32, color: "6B1E7A", font: "Arial" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "Backend Reference System | Practitioner and AI Reading Generation Use Only", italics: true, size: 24, color: "C2185B", font: "Arial" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 300 },
        children: [new TextRun({ text: "Phoenix Rebirth | Christina Stevens | April 2026 | Version 1.0 | PROPRIETARY", size: 20, color: "999999", font: "Arial" })] }),
      divider(),
      note("This document is the timing layer backend for the TCM Astrology Chakra System and the Medical Astrology Timing Query Tool. It provides the Annual Profection framework, Time Lord health implications, transit timing indicators, surgery electional timing, secondary progression health indicators, the calibration example from Christina Stevens' chart, and the full specification for the Medical Astrology Timing Query Tool build."),
      spacer(),

      h1("SECTION 1: Annual Profections — House to Age and Health Theme Mapping"),
      note("Annual Profections assign a specific house to each year of life, beginning with the 1st house at age 0 and cycling through all 12 houses every 12 years. The ruler of the sign occupying that house becomes the Time Lord for the year. The 6th, 8th, and 12th house profection years carry the most significant health implications."),
      spacer(),
      profTable,
      pageBreak(),

      h1("SECTION 2: Time Lord Health Implications"),
      note("The Time Lord is the planetary ruler of the sign occupying the profected house for that year. The Time Lord's natal condition (sign, house, aspects, dignity, and whether retrograde) governs the quality of its year as Time Lord. A well-placed Time Lord supports the year's themes. An afflicted Time Lord brings the natal challenges into the year's foreground."),
      spacer(),
      tlTable,
      pageBreak(),

      h1("SECTION 3: Transit Timing Indicators"),
      note("Transits are the primary external timing mechanism. Slower planets (Saturn, Uranus, Neptune, Pluto) indicate long-term health periods. Faster planets (Mars, Sun, Moon) pinpoint acute timing within longer windows. The most precise acute health event timing comes from Mars transits and the transiting Moon's sign at the moment of the event."),
      spacer(),
      transTable,
      pageBreak(),

      h1("SECTION 4: Surgery and Medical Procedure Timing"),
      note("Electional astrology for medical procedures selects the most favorable timing for surgical intervention and recovery. These guidelines apply to elective procedures only. Emergency procedures are not governed by electional timing. These are traditional frameworks with some modern research support, particularly around lunar phase and surgical outcomes."),
      spacer(),
      surgTable,
      pageBreak(),

      h1("SECTION 5: Secondary Progressions Health Indicators"),
      note("Secondary Progressions represent internal developmental timing. One day after birth equals one year of life. Progressions show internal shifts that may not have external triggers. The Progressed Moon is the most actively used progression for health timing, moving approximately one sign every 2.5 years."),
      spacer(),
      progTable,
      pageBreak(),

      h1("SECTION 6: Calibration Example — Christina Stevens November 2007"),
      note("This is the primary calibration example for the Medical Astrology Timing Query Tool. All timing layers confirmed simultaneously in a single event. Use this example to verify the query tool's output accuracy and as the demonstration case for client education materials."),
      spacer(),
      exTable,
      pageBreak(),

      h1("SECTION 7: Medical Astrology Timing Query Tool — Build Specification"),
      note("This section specifies the full build requirements for the Medical Astrology Timing Query Tool. Scheduled for the May 25th build session. Requires the PySwisseph API (already built), the Tier 2 Backend Reference body part mapping tables, and the Annual Profection calculation logic documented in this section."),
      spacer(),
      specTable,
      pageBreak(),

      h1("SECTION 8: Quick Timing Reference Summary"),
      note("This table provides the fast-lookup version of the timing framework for use during reading generation. For each event type, check the key timing indicators and cross-reference the primary natal chart factors listed."),
      spacer(),
      qtTable,
      spacer(),
      divider(),

      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 100 },
        children: [new TextRun({ text: "Medical Astrology Timing Layer | TCM Astrology Chakra System", italics: true, size: 20, color: "2D0A3E", font: "Arial" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "Proprietary system created by Christina Stevens. Phoenix Rebirth. April 2026. All rights reserved.", italics: true, size: 18, color: "999999", font: "Arial" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0 },
        children: [new TextRun({ text: "Backend reference document for practitioner and AI reading generation use only. Not for client distribution.", italics: true, size: 18, color: "C2185B", font: "Arial" })] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/mnt/user-data/outputs/Medical_Astrology_Timing_Layer.docx", buffer);
  console.log("Done");
});
