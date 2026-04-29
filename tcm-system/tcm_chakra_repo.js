bash

cat /home/claude/tcm_chakra_repo.js
Output

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageBreak
} = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const headerBorder = { style: BorderStyle.SINGLE, size: 1, color: "4A0E4E" };
const headerBorders = { top: headerBorder, bottom: headerBorder, left: headerBorder, right: headerBorder };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 },
    children: [new TextRun({ text, bold: true, size: 36, color: "4A0E4E", font: "Arial" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 150 },
    children: [new TextRun({ text, bold: true, size: 28, color: "8B1A8B", font: "Arial" })]
  });
}

function h3(text) {
  return new Paragraph({
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, size: 24, color: "C2185B", font: "Arial" })]
  });
}

function body(text) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, size: 22, font: "Arial" })]
  });
}

function bold(text) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, bold: true, size: 22, font: "Arial" })]
  });
}

function note(text) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, size: 20, italics: true, color: "666666", font: "Arial" })]
  });
}

function divider() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "8B1A8B", space: 1 } },
    children: [new TextRun("")]
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function headerRow(cells, colWidths) {
  return new TableRow({
    tableHeader: true,
    children: cells.map((text, i) => new TableCell({
      borders: headerBorders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: "4A0E4E", type: ShadingType.CLEAR },
      margins: { top: 100, bottom: 100, left: 150, right: 150 },
      children: [new Paragraph({ children: [new TextRun({ text, bold: true, size: 20, color: "FFFFFF", font: "Arial" })] })]
    }))
  });
}

function dataRow(cells, colWidths, shade) {
  return new TableRow({
    children: cells.map((text, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: shade || "FFFFFF", type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 150, right: 150 },
      children: [new Paragraph({ children: [new TextRun({ text, size: 20, font: "Arial" })] })]
    }))
  });
}

// CHAKRA BASELINE TABLE
const chakraColWidths = [1400, 1100, 1100, 1200, 1100, 1100, 1360];
const chakraTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: chakraColWidths,
  rows: [
    headerRow(["Chakra", "Element", "Yin Meridian", "Yang Meridian", "Body Area", "TCM Focus", "Details"], chakraColWidths),
    dataRow(["Root", "Water", "Kidney", "Bladder", "Feet, back-body, adrenals", "Fear, Survival, Security, Foundation", "Kidney/Bladder manage foundational energy flowing from feet and back-body"], chakraColWidths, "F9F0FF"),
    dataRow(["Sacral", "Wood", "Liver", "Gallbladder", "Liver, hips, reproductive", "Sexual/social fulfillment, emotional intelligence, creativity", "Liver/Gallbladder manage circulation of energy, menstruation, and digestion"], chakraColWidths, "FFFFFF"),
    dataRow(["Solar Plexus", "Earth", "Spleen", "Stomach", "Stomach, digestion, front/sides", "Career, self-esteem, personal power, digestion", "Spleen/Stomach manage digestion and decision-making"], chakraColWidths, "F9F0FF"),
    dataRow(["Heart", "Fire", "Heart", "Small Intestine", "Heart, spine, emotional center", "Romantic/universal love, compassion, joy", "Heart/Small Intestine manage emotional availability and heart health (Shen)"], chakraColWidths, "FFFFFF"),
    dataRow(["Throat", "Metal", "Lung", "Large Intestine", "Lungs, nerves, communication", "Personal expression, self-awareness, communication", "Lung/Large Intestine relate to purification, letting go (grief), and breath"], chakraColWidths, "F9F0FF"),
    dataRow(["Third Eye", "Fire", "Pericardium", "Triple Burner", "Head, brain, intuition", "Intuition, rational thought, insight", "Pericardium/Triple Burner manage heart regulation and wisdom"], chakraColWidths, "FFFFFF"),
    dataRow(["Crown", "All/Spirit", "Governing Vessel", "Governing Vessel", "Top of head, heavenly Qi", "Spiritual connection, intuition", "GV 20 (Baihui) is the main entry point of heavenly Qi"], chakraColWidths, "F9F0FF"),
  ]
});

// HOUSE CHAKRA MAP
const houseColWidths = [1200, 1560, 3200, 3400];
const houseTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: houseColWidths,
  rows: [
    headerRow(["House", "Chakra", "Focus", "Body Governance"], houseColWidths),
    dataRow(["1st", "Root", "Identity, self, appearance", "Physical body, head, beginnings"], houseColWidths, "F9F0FF"),
    dataRow(["2nd", "Sacral", "Values, resources, money", "Throat, neck, material security"], houseColWidths, "FFFFFF"),
    dataRow(["3rd", "Solar Plexus", "Communication, siblings, local travel", "Lungs, arms, nervous system"], houseColWidths, "F9F0FF"),
    dataRow(["4th", "Heart", "Home, roots, foundation, family", "Chest, breasts, stomach"], houseColWidths, "FFFFFF"),
    dataRow(["5th", "Throat", "Creativity, children, romance, play", "Heart, spine, upper back"], houseColWidths, "F9F0FF"),
    dataRow(["6th", "Third Eye", "Health, work, daily routines", "Digestive system, intestines"], houseColWidths, "FFFFFF"),
    dataRow(["7th", "Heart", "Partnerships, open enemies, contracts", "Kidneys, skin, lower back"], houseColWidths, "F9F0FF"),
    dataRow(["8th", "Sacral", "Transformation, death, shared resources", "Reproductive system, elimination"], houseColWidths, "FFFFFF"),
    dataRow(["9th", "Third Eye", "Philosophy, higher learning, travel", "Hips, liver, thighs"], houseColWidths, "F9F0FF"),
    dataRow(["10th", "Throat", "Career, public reputation, authority", "Knees, joints, bones"], houseColWidths, "FFFFFF"),
    dataRow(["11th", "Heart", "Community, friends, collective, hopes", "Ankles, calves, circulation"], houseColWidths, "F9F0FF"),
    dataRow(["12th", "Crown", "Hidden, spiritual, karma, isolation", "Feet, immune system, lymph"], houseColWidths, "FFFFFF"),
  ]
});

// ZODIAC CHAKRA MAP
const zodiacColWidths = [1400, 1400, 1560, 2400, 2600];
const zodiacTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: zodiacColWidths,
  rows: [
    headerRow(["Sign", "Chakra", "Modality", "Body Areas", "Health Focus"], zodiacColWidths),
    dataRow(["Aries", "Solar Plexus", "Cardinal", "Head, blood", "Inflammation, headaches, adrenal fatigue"], zodiacColWidths, "F9F0FF"),
    dataRow(["Taurus", "Heart", "Fixed", "Throat, thyroid", "Thyroid issues, throat inflammation, stubborn weight"], zodiacColWidths, "FFFFFF"),
    dataRow(["Gemini", "Throat", "Mutable", "Lungs, nerves", "Respiratory issues, nervous system sensitivity"], zodiacColWidths, "F9F0FF"),
    dataRow(["Cancer", "Third Eye", "Cardinal", "Stomach, breasts", "Digestive issues, fluid retention, emotional eating"], zodiacColWidths, "FFFFFF"),
    dataRow(["Leo", "Third Eye", "Fixed", "Heart, spine", "Heart issues, back pain, blood pressure"], zodiacColWidths, "F9F0FF"),
    dataRow(["Virgo", "Throat", "Mutable", "Digestive system", "Gut health, IBS, anxiety-digestion connection"], zodiacColWidths, "FFFFFF"),
    dataRow(["Libra", "Heart", "Cardinal", "Kidneys, skin", "Kidney function, skin conditions, hormonal balance"], zodiacColWidths, "F9F0FF"),
    dataRow(["Scorpio", "Solar Plexus", "Fixed", "Reproductive system", "Hormonal issues, elimination, deep cellular transformation"], zodiacColWidths, "FFFFFF"),
    dataRow(["Sagittarius", "Sacral", "Mutable", "Liver, hips", "Liver toxicity, hip issues, sciatic nerve"], zodiacColWidths, "F9F0FF"),
    dataRow(["Capricorn", "Root", "Cardinal", "Joints, bones", "Arthritis, skeletal issues, structural integrity"], zodiacColWidths, "FFFFFF"),
    dataRow(["Aquarius", "Root", "Fixed", "Circulation, calves", "Circulatory issues, nervous system, varicose veins"], zodiacColWidths, "F9F0FF"),
    dataRow(["Pisces", "Sacral", "Mutable", "Feet, immune system", "Immune dysregulation, lymphatic congestion, foot issues"], zodiacColWidths, "FFFFFF"),
  ]
});

// PLANET CHAKRA MAP
const planetColWidths = [1400, 1400, 2480, 2280, 1800];
const planetTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: planetColWidths,
  rows: [
    headerRow(["Planet", "Chakra", "Health Influence", "Body System", "TCM Connection"], planetColWidths),
    dataRow(["Sun", "Third Eye", "Heart vitality, life force", "Cardiovascular system", "Shen (spirit), heart fire"], planetColWidths, "F9F0FF"),
    dataRow(["Moon", "Third Eye", "Stomach, fluids, emotional tides", "Digestive/lymphatic system", "Yin fluids, emotional body"], planetColWidths, "FFFFFF"),
    dataRow(["Mercury", "Throat", "Nervous system, communication", "Central nervous system", "Lung/Large Intestine (breath and release)"], planetColWidths, "F9F0FF"),
    dataRow(["Venus", "Heart", "Kidneys, skin, hormonal balance", "Endocrine/renal system", "Pericardium (love, Shen protection)"], planetColWidths, "FFFFFF"),
    dataRow(["Mars", "Solar Plexus", "Inflammation, drive, heat", "Muscular/adrenal system", "Liver fire, aggressive Qi"], planetColWidths, "F9F0FF"),
    dataRow(["Jupiter", "Sacral", "Liver expansion, abundance", "Hepatic/lymphatic system", "Liver/Gallbladder (Wood element)"], planetColWidths, "FFFFFF"),
    dataRow(["Saturn", "Root", "Bones, structure, restriction", "Skeletal system", "Kidney Jing (essence, foundations)"], planetColWidths, "F9F0FF"),
    dataRow(["Uranus", "Third Eye", "Nervous system disruption, awakening", "Neurological system", "Triple Burner (unusual heat patterns)"], planetColWidths, "FFFFFF"),
    dataRow(["Neptune", "Crown", "Immunity, dissolution, sensitivity", "Immune/lymphatic system", "Governing Vessel (spiritual Qi)"], planetColWidths, "F9F0FF"),
    dataRow(["Pluto", "Crown", "Elimination, cellular transformation", "Elimination/reproductive system", "Deep Jing transformation"], planetColWidths, "FFFFFF"),
  ]
});

// DEGREE CHAKRA MAP
const degreeColWidths = [800, 1600, 2480, 4480];
const degreeTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: degreeColWidths,
  rows: [
    headerRow(["Degree", "Chakra", "Criticality", "Notes"], degreeColWidths),
    dataRow(["0", "Crown", "Cardinal Critical (Aries, Cancer, Libra, Capricorn)", "Pure energy. Most intense expression of the sign. Crown activation at entry point."], degreeColWidths, "F9F0FF"),
    dataRow(["1", "Solar Plexus", "None", "Early personal power activation"], degreeColWidths, "FFFFFF"),
    dataRow(["2", "Heart", "None", "Heart opening, early love frequency"], degreeColWidths, "F9F0FF"),
    dataRow(["3", "Throat", "None", "Early voice activation"], degreeColWidths, "FFFFFF"),
    dataRow(["4", "Third Eye", "Mutable Critical (Gemini, Virgo, Sagittarius, Pisces)", "High sensitivity degree. Intuition heightened."], degreeColWidths, "F9F0FF"),
    dataRow(["5", "Third Eye", "None", "Continued intuitive activation"], degreeColWidths, "FFFFFF"),
    dataRow(["6", "Throat", "None", "Voice and communication frequency"], degreeColWidths, "F9F0FF"),
    dataRow(["7", "Heart", "None", "Heart resonance, relational frequency"], degreeColWidths, "FFFFFF"),
    dataRow(["8", "Solar Plexus", "Fixed Critical (Taurus, Leo, Scorpio, Aquarius)", "Power activation. Fixed energy, prone to stubborn physical issues."], degreeColWidths, "F9F0FF"),
    dataRow(["9", "Sacral", "Fixed Critical (Taurus, Leo, Scorpio, Aquarius)", "Creative and emotional activation. Fixed energy."], degreeColWidths, "FFFFFF"),
    dataRow(["10", "Root", "None", "Grounding and foundation frequency"], degreeColWidths, "F9F0FF"),
    dataRow(["11", "Root", "None", "Continued grounding activation"], degreeColWidths, "FFFFFF"),
    dataRow(["12", "Sacral", "None", "Emotional and creative frequency"], degreeColWidths, "F9F0FF"),
    dataRow(["13", "Solar Plexus", "None", "Personal power mid-point"], degreeColWidths, "FFFFFF"),
    dataRow(["14", "Heart", "None", "Heart center activation"], degreeColWidths, "F9F0FF"),
    dataRow(["15", "Throat", "None", "Voice and expression mid-point"], degreeColWidths, "FFFFFF"),
    dataRow(["16", "Third Eye", "None", "Intuition and insight activation"], degreeColWidths, "F9F0FF"),
    dataRow(["17", "Third Eye", "Mutable Critical (Gemini, Virgo, Sagittarius, Pisces)", "High sensitivity degree. Third Eye intensified."], degreeColWidths, "FFFFFF"),
    dataRow(["18", "Throat", "None", "Communication and self-expression"], degreeColWidths, "F9F0FF"),
    dataRow(["19", "Heart", "None", "Heart frequency, late cycle opening"], degreeColWidths, "FFFFFF"),
    dataRow(["20", "Solar Plexus", "None", "Power and digestion activation"], degreeColWidths, "F9F0FF"),
    dataRow(["21", "Sacral", "Fixed Critical (Taurus, Leo, Scorpio, Aquarius)", "Creative activation. Fixed energy, stubborn physical patterns."], degreeColWidths, "FFFFFF"),
    dataRow(["22", "Root", "Fixed Critical (Taurus, Leo, Scorpio, Aquarius)", "Grounding activation. Fixed energy, structural physical issues."], degreeColWidths, "F9F0FF"),
    dataRow(["23", "Root", "None", "Foundation and security frequency"], degreeColWidths, "FFFFFF"),
    dataRow(["24", "Sacral", "None", "Emotional intelligence and creativity"], degreeColWidths, "F9F0FF"),
    dataRow(["25", "Solar Plexus", "None", "Personal power late activation"], degreeColWidths, "FFFFFF"),
    dataRow(["26", "Heart", "None", "Heart and love frequency"], degreeColWidths, "F9F0FF"),
    dataRow(["27", "Throat", "None", "Voice and communication late activation"], degreeColWidths, "FFFFFF"),
    dataRow(["28", "Third Eye", "None", "Intuition and vision late activation"], degreeColWidths, "F9F0FF"),
    dataRow(["29", "Crown", "Anaretic (ALL signs)", "Fated degree. Karmic completion. Crown activation at cycle end. Intensified health impact in any sign."], degreeColWidths, "FFFFFF"),
  ]
});

// ASPECT CHAKRA MAP
const aspectColWidths = [1400, 1400, 1560, 2400, 2600];
const aspectTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: aspectColWidths,
  rows: [
    headerRow(["Aspect", "Chakra", "Nature", "Body Tension/Harmony", "Axis Pairs"], aspectColWidths),
    dataRow(["Conjunction", "Solar Plexus / Heart", "Fusion (can be harmony or intensity)", "Merged organ systems, intensified activation of both planets' body areas", "N/A"], aspectColWidths, "F9F0FF"),
    dataRow(["Opposition", "Root", "Tension, balance required", "Opposing body systems pulled against each other. Key health balance axis.", "Aries/Libra (endocrine/vitality), Taurus/Scorpio (intake/elimination), Gemini/Sagittarius (lungs/liver), Cancer/Capricorn (stomach/joints), Leo/Aquarius (heart/circulation), Virgo/Pisces (digestion/detox)"], aspectColWidths, "FFFFFF"),
    dataRow(["Square", "Root / Solar Plexus", "Friction, blockage, drive", "Cross-system stress. Two chakra systems in conflict creating physical tension.", "N/A"], aspectColWidths, "F9F0FF"),
    dataRow(["Trine", "Heart", "Flow, ease, harmony", "Harmonious energy flow between organ systems. Natural healing pathway.", "N/A"], aspectColWidths, "FFFFFF"),
    dataRow(["Sextile", "Throat", "Opportunity, communication", "Cooperative relationship between systems. Opportunity for health when activated consciously.", "N/A"], aspectColWidths, "F9F0FF"),
    dataRow(["Quincunx", "Sacral / Third Eye", "Adjustment, tension without resolution", "Awkward misalignment between organ systems requiring conscious integration. Often shows as chronic low-level issues.", "N/A"], aspectColWidths, "FFFFFF"),
  ]
});

// TCM BODY CLOCK
const clockColWidths = [1200, 1560, 1200, 1200, 1200, 2000];
const clockTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: clockColWidths,
  rows: [
    headerRow(["Time Window", "Organ", "Yin/Yang", "Element", "Chakra", "TCM Focus"], clockColWidths),
    dataRow(["1am - 3am", "Liver", "Yin", "Wood", "Sacral", "Processing emotions, detoxification, blood cleansing"], clockColWidths, "F9F0FF"),
    dataRow(["3am - 5am", "Lung", "Yin", "Metal", "Throat", "Grief release, breath, oxygenation, letting go"], clockColWidths, "FFFFFF"),
    dataRow(["5am - 7am", "Large Intestine", "Yang", "Metal", "Throat", "Elimination, releasing what no longer serves"], clockColWidths, "F9F0FF"),
    dataRow(["7am - 9am", "Stomach", "Yang", "Earth", "Solar Plexus", "Digestion, nourishment, receiving"], clockColWidths, "FFFFFF"),
    dataRow(["9am - 11am", "Spleen", "Yin", "Earth", "Solar Plexus", "Transformation of food/thought, intellectual activity"], clockColWidths, "F9F0FF"),
    dataRow(["11am - 1pm", "Heart", "Yin", "Fire", "Heart", "Peak heart energy, circulation, joy, Shen"], clockColWidths, "FFFFFF"),
    dataRow(["1pm - 3pm", "Small Intestine", "Yang", "Fire", "Heart", "Sorting and assimilation, discernment"], clockColWidths, "F9F0FF"),
    dataRow(["3pm - 5pm", "Bladder", "Yang", "Water", "Root", "Fluid metabolism, purification, fear release"], clockColWidths, "FFFFFF"),
    dataRow(["5pm - 7pm", "Kidney", "Yin", "Water", "Root", "Vital essence, willpower, ancestral energy"], clockColWidths, "F9F0FF"),
    dataRow(["7pm - 9pm", "Pericardium", "Yin", "Fire", "Third Eye", "Heart protection, emotional boundaries, intimacy"], clockColWidths, "FFFFFF"),
    dataRow(["9pm - 11pm", "Triple Burner", "Yang", "Fire", "Third Eye", "Regulating body temperature, harmonizing organ systems"], clockColWidths, "F9F0FF"),
    dataRow(["11pm - 1am", "Gallbladder", "Yang", "Wood", "Sacral", "Decision-making, courage, bile production, deep rest"], clockColWidths, "FFFFFF"),
  ]
});

// CHRISTINA'S BIRTH TIME
const birthClockColWidths = [2000, 7360];
const birthClockTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: birthClockColWidths,
  rows: [
    headerRow(["Field", "Value"], birthClockColWidths),
    dataRow(["Birth Time", "2:17 AM"], birthClockColWidths, "F9F0FF"),
    dataRow(["Active Window", "1am - 3am (Liver Time)"], birthClockColWidths, "FFFFFF"),
    dataRow(["Organ", "Liver (Yin) / Gallbladder (Yang)"], birthClockColWidths, "F9F0FF"),
    dataRow(["Element", "Wood"], birthClockColWidths, "FFFFFF"),
    dataRow(["Chakra Activated at Birth", "Sacral"], birthClockColWidths, "F9F0FF"),
    dataRow(["TCM Focus", "Processing emotions, detoxification, blood cleansing, courage in the dark"], birthClockColWidths, "FFFFFF"),
    dataRow(["HD Confirmation", "Generator type - Sacral being confirmed by TCM body clock at birth"], birthClockColWidths, "F9F0FF"),
  ]
});

// CHRISTINA'S FULL 5-LAYER CHART
const chartColWidths = [1300, 900, 1100, 1100, 1000, 1100, 2860];
const chartTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: chartColWidths,
  rows: [
    headerRow(["Placement", "House (H)", "Zodiac (Z)", "Planet (P)", "Degree (D)", "Critical?", "Summary"], chartColWidths),
    dataRow(["Sun Aries 18° H3", "Solar Plexus", "Solar Plexus", "Third Eye", "Throat", "No", "Double Solar Plexus (H+Z). Power identity expressed through voice. Third Eye adds intuitive drive."], chartColWidths, "F9F0FF"),
    dataRow(["Moon Pisces 2° H2", "Sacral", "Sacral", "Third Eye", "Heart", "No", "Double Sacral (H+Z). Emotional body is deeply creative and intuitive. Heart degree softens through love."], chartColWidths, "FFFFFF"),
    dataRow(["Mercury Taurus 3° H4", "Heart", "Heart", "Throat", "Throat", "No", "Double Heart (H+Z). Double Throat (P+D). Mind lives in love and speaks through voice. Most harmonically aligned mental placement."], chartColWidths, "F9F0FF"),
    dataRow(["Venus Taurus 25° H4", "Heart", "Heart", "Heart", "Solar Plexus", "No", "TRIPLE HEART (H+Z+P). Love, values, and abundance are pure Heart activation. Solar Plexus degree activates power through love."], chartColWidths, "FFFFFF"),
    dataRow(["Mars Taurus 2° H4", "Heart", "Heart", "Solar Plexus", "Heart", "No", "TRIPLE HEART (H+Z+D). Drive and action are Heart activated. Solar Plexus planet means power moves through love."], chartColWidths, "F9F0FF"),
    dataRow(["Jupiter Sagittarius 10° H11", "Heart", "Sacral", "Sacral", "Root", "No", "Double Sacral (Z+P). Expansion flows through creativity in Heart house (community). Root degree grounds abundance physically."], chartColWidths, "FFFFFF"),
    dataRow(["Saturn Scorpio 2° H10", "Throat", "Solar Plexus", "Root", "Heart", "Watch Fixed transits", "Karma expressed publicly through Throat. Solar Plexus sign brings power lessons. Root planet restricts and structures. Heart degree softens."], chartColWidths, "F9F0FF"),
    dataRow(["Uranus Sagittarius 8° H11", "Heart", "Sacral", "Third Eye", "Solar Plexus", "No (Mutable critical is 4,17)", "Awakening in Heart house through Sacral creativity. Third Eye planet sees the revolution coming. Solar Plexus degree activates power."], chartColWidths, "FFFFFF"),
    dataRow(["Neptune Sagittarius 29° H11/12", "Heart/Crown", "Sacral", "Crown", "Crown", "YES - Anaretic 29 all signs", "Double Crown (P+D). ANARETIC. Fated spiritual dissolution. Sacral sign means divine accessed through feeling and creating."], chartColWidths, "F9F0FF"),
    dataRow(["Pluto Libra 28° H9", "Third Eye", "Heart", "Crown", "Third Eye", "No", "Double Third Eye (H+D). Transformation through love (Heart sign) at highest spiritual frequency (Crown planet). Vision-driven rebirth."], chartColWidths, "FFFFFF"),
    dataRow(["Chiron Taurus 24° H4", "Heart", "Heart", "Third Eye", "Sacral", "No", "Double Heart (H+Z). Wound and gift both live in Heart at foundation. Intuitive healing path (Third Eye). Sacral degree - emotional core of the wound."], chartColWidths, "F9F0FF"),
    dataRow(["BML Aquarius 2° H1", "Root", "Root", "Third Eye", "Heart", "No", "Double Root (H+Z). Sovereign wild self is primal and embodied. Third Eye planet sees through all illusion. Heart degree - even wildness loves."], chartColWidths, "FFFFFF"),
    dataRow(["North Node Gemini 27° H5", "Throat", "Throat", "Third Eye", "Throat", "No", "TRIPLE THROAT (H+Z+D). Soul destiny is pure voice activation across three layers. Third Eye guides the path. You are meant to see it and say it."], chartColWidths, "F9F0FF"),
    dataRow(["Part of Fortune Pisces 24° H2", "Sacral", "Sacral", "Third Eye", "Sacral", "No", "TRIPLE SACRAL (H+Z+D). Fortune and prosperity flow through creativity and emotional intelligence at three layers. Intuition (Third Eye) finds the luck."], chartColWidths, "FFFFFF"),
    dataRow(["Vertex Virgo 6° H8", "Sacral", "Throat", "Third Eye", "Throat", "No", "Double Throat (Z+D). Fated encounters happen through voice. Sacral house means those meetings transform emotionally and creatively."], chartColWidths, "F9F0FF"),
    dataRow(["Midheaven Scorpio 25° H10", "Throat", "Solar Plexus", "Solar Plexus", "Solar Plexus", "No", "TRIPLE SOLAR PLEXUS (Z+P+D). Public power is the career pinnacle. Throat house means all that power speaks publicly."], chartColWidths, "FFFFFF"),
  ]
});

const doc = new Document({
  numbering: { config: [] },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "4A0E4E" },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "8B1A8B" },
        paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 15840, height: 12240 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
        orientation: "landscape"
      }
    },
    children: [
      // TITLE
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "TCM ASTROLOGY CHAKRA SYSTEM", bold: true, size: 48, color: "4A0E4E", font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "System Baseline Repository", bold: true, size: 32, color: "8B1A8B", font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "Phoenix Rebirth | Aurelia Reign | Proprietary System", italics: true, size: 24, color: "C2185B", font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 300 },
        children: [new TextRun({ text: "Created: April 2026 | Version 1.0", size: 20, color: "999999", font: "Arial" })]
      }),
      divider(),

      // SECTION 1 - CHAKRA BASELINE
      h1("SECTION 1: Chakra Baseline Reference"),
      note("The seven-chakra framework mapped to TCM elements, meridian pairs, organ systems, and energetic focus areas. This is the foundational lookup table for all system layers."),
      new Paragraph({ spacing: { before: 100, after: 200 }, children: [new TextRun("")] }),
      chakraTable,
      pageBreak(),

      // SECTION 2 - HOUSE MAP
      h1("SECTION 2: House Chakra Mapping"),
      note("House assignments are fixed and stationary. The house number always carries the same chakra regardless of what sign occupies it. The zodiac layer rotates based on Rising sign."),
      new Paragraph({ spacing: { before: 100, after: 200 }, children: [new TextRun("")] }),
      houseTable,
      pageBreak(),

      // SECTION 3 - ZODIAC MAP
      h1("SECTION 3: Zodiac Sign Chakra Mapping"),
      note("Each zodiac sign carries its associated chakra, body areas, and health focus. The zodiac wheel rotates based on the Rising sign in the natal chart, placing signs in houses accordingly."),
      new Paragraph({ spacing: { before: 100, after: 200 }, children: [new TextRun("")] }),
      zodiacTable,
      pageBreak(),

      // SECTION 4 - PLANET MAP
      h1("SECTION 4: Planetary Chakra Mapping"),
      note("Each planet carries its own chakra, health influence, and TCM organ system connection. Planetary chakra activations are fixed regardless of sign or house placement."),
      new Paragraph({ spacing: { before: 100, after: 200 }, children: [new TextRun("")] }),
      planetTable,
      pageBreak(),

      // SECTION 5 - DEGREE MAP
      h1("SECTION 5: Degree Chakra Mapping"),
      note("Each degree 0-29 carries its own chakra activation. 0 is Pure (Crown) and 29 is Fated (Crown). Critical degrees intensify the Zodiac chakra of the sign the planet occupies. Tight orbs (0-2) are immediate and conscious. Wide orbs (5+) are subliminal and require conscious effort."),
      new Paragraph({ spacing: { before: 100, after: 200 }, children: [new TextRun("")] }),
      degreeTable,
      pageBreak(),

      // SECTION 6 - ASPECTS
      h1("SECTION 6: Aspect Chakra Mapping"),
      note("Each aspect type carries its own chakra activation and physical body tension or harmony signature. Orb intensity determines whether the activation is conscious and immediate (0-2 degrees) or subliminal and background (5+ degrees). The six Opposition axes define specific body system tension pairs requiring balance."),
      new Paragraph({ spacing: { before: 100, after: 200 }, children: [new TextRun("")] }),
      aspectTable,
      pageBreak(),

      // SECTION 7 - TCM BODY CLOCK
      h1("SECTION 7: TCM Body Clock Reference"),
      note("The TCM body clock assigns 2-hour windows to each organ system. Birth time determines which organ and meridian pair was active at the moment of entry into this life, creating a birth time chakra activation that runs as an undercurrent through the entire chart."),
      new Paragraph({ spacing: { before: 100, after: 200 }, children: [new TextRun("")] }),
      clockTable,
      pageBreak(),

      // SECTION 8 - CHRISTINA'S BIRTH TIME
      h1("SECTION 8: Birth Time Activation - Christina Stevens"),
      note("Birth data: April 9, 1983 at 2:17 AM | Hobbs, NM | UTC -7"),
      new Paragraph({ spacing: { before: 100, after: 200 }, children: [new TextRun("")] }),
      birthClockTable,
      new Paragraph({ spacing: { before: 200, after: 100 }, children: [new TextRun("")] }),
      body("Note: Liver time (1am-3am) governs processing of emotions, detoxification, blood cleansing, and courage in the dark. Born into Sacral chakra activation through the Wood element Liver meridian. This is confirmed independently by Human Design (Generator = Sacral being) and by natal chart (Moon, Mercury, Mars, Venus, Part of Fortune all heavily Sacral activated). Three completely separate systems pointing to the same truth."),
      pageBreak(),

      // SECTION 9 - FULL CHART MAP
      h1("SECTION 9: Full 5-Layer Chart Activation Map - Christina Stevens"),
      note("All 16 natal placements mapped through all 5 system layers: House (H), Zodiac Sign (Z), Planet (P), Degree Chakra (D), and Degree Criticality. Where multiple layers share the same chakra, activation intensity increases."),
      new Paragraph({ spacing: { before: 100, after: 200 }, children: [new TextRun("")] }),
      chartTable,
      new Paragraph({ spacing: { before: 300, after: 100 }, children: [new TextRun("")] }),

      h2("System-Wide Pattern Summary"),
      divider(),
      bold("Throat is the Destiny Chakra:"),
      body("North Node hits Throat at three layers (H+Z+D). Mercury hits Throat at two layers (P+D). Vertex hits Throat at two layers (Z+D). Midheaven sits in a Throat house. The soul's entire evolutionary trajectory points toward voice as the primary instrument of purpose."),
      new Paragraph({ spacing: { before: 80, after: 80 }, children: [new TextRun("")] }),
      bold("Heart is the Foundation Chakra:"),
      body("Venus hits Heart at three layers (H+Z+P). Mars hits Heart at three layers (H+Z+D). Mercury hits Heart at two layers (H+Z). Chiron hits Heart at two layers (H+Z). The roots, love, drive, and wound all live in Heart. Love is not a theme in this chart. Love IS the structure."),
      new Paragraph({ spacing: { before: 80, after: 80 }, children: [new TextRun("")] }),
      bold("Solar Plexus is the Public Power Chakra:"),
      body("Sun hits Solar Plexus at two layers (H+Z). Midheaven hits Solar Plexus at three layers (Z+P+D). Personal power and career pinnacle are both Solar Plexus dominant. The public face is power."),
      new Paragraph({ spacing: { before: 80, after: 80 }, children: [new TextRun("")] }),
      bold("Sacral is the Birth Time and Fortune Chakra:"),
      body("Birth time activates Sacral through Liver/Wood at 2:17 AM. Part of Fortune hits Sacral at three layers (H+Z+D). Moon and Jupiter also carry Sacral activation. Prosperity and emotional fulfillment flow through creative Sacral energy."),
      new Paragraph({ spacing: { before: 80, after: 80 }, children: [new TextRun("")] }),
      bold("Crown appears at Neptune and Pluto:"),
      body("Both generational planets carry Crown activation. Neptune is also at the anaretic 29th degree, a double Crown hit. Collective and spiritual purpose operate at the highest frequency in this chart."),
      new Paragraph({ spacing: { before: 80, after: 80 }, children: [new TextRun("")] }),
      bold("Root holds only Black Moon Lilith:"),
      body("Sovereign wildness is the only Root activation. Primal, embodied, unapologetic identity in House 1. The foundation is not fear or survival. It is Lilith."),

      divider(),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 0 },
        children: [new TextRun({ text: "Phoenix Rebirth | TCM Astrology Chakra System | Version 1.0 | April 2026", italics: true, size: 18, color: "999999", font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 80, after: 0 },
        children: [new TextRun({ text: "Proprietary system created by Christina Stevens / Aurelia Reign. All rights reserved.", italics: true, size: 18, color: "999999", font: "Arial" })]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/mnt/user-data/outputs/TCM_Astrology_Chakra_System_Baseline.docx", buffer);
  console.log("Done");
});