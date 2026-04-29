bash

cat /home/claude/tcm_aspects.js
Output

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  PageBreak, PageOrientation
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
function spacer() {
  return new Paragraph({ spacing: { before: 100, after: 100 }, children: [new TextRun("")] });
}

function headerRow(cells, colWidths) {
  return new TableRow({
    tableHeader: true,
    children: cells.map((text, i) => new TableCell({
      borders: headerBorders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: "4A0E4E", type: ShadingType.CLEAR },
      margins: { top: 100, bottom: 100, left: 150, right: 150 },
      children: [new Paragraph({ children: [new TextRun({ text, bold: true, size: 19, color: "FFFFFF", font: "Arial" })] })]
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
      children: [new Paragraph({ children: [new TextRun({ text, size: 19, font: "Arial" })] })]
    }))
  });
}
function dataRowBold(cells, boldCols, colWidths, shade) {
  return new TableRow({
    children: cells.map((text, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: shade || "FFFFFF", type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 150, right: 150 },
      children: [new Paragraph({ children: [new TextRun({ text, size: 19, font: "Arial", bold: boldCols.includes(i) })] })]
    }))
  });
}

// CONTENT WIDTH: 15840 - 2160 (margins) = 13680 DXA in landscape
const CW = 13680;

// ASPECT TABLE COLUMNS
// Aspect | Orb | Intensity | Aspect Chakra | P1 Chakra+Body | P2 Chakra+Body | TCM Interaction | Body Tension/Harmony | Healing Pathway
const aCols = [1400, 600, 900, 1100, 1580, 1580, 1820, 2400, 2300];
// sum = 13680

function aspectTable(rows) {
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: aCols,
    rows: [
      headerRow(["Aspect", "Orb", "Intensity", "Aspect Chakra", "Planet 1: Chakra + Body", "Planet 2: Chakra + Body", "TCM Meridian Interaction", "Body Tension or Harmony", "Healing Pathway"], aCols),
      ...rows
    ]
  });
}

function aRow(aspect, orb, intensity, aspectChakra, p1, p2, tcm, bodyEffect, healing, shade) {
  return dataRow([aspect, orb, intensity, aspectChakra, p1, p2, tcm, bodyEffect, healing], aCols, shade);
}

// ORB INTENSITY HELPER
function orbLevel(orb) {
  const o = parseFloat(orb);
  if (o <= 2) return "TIGHT - Immediate, conscious, physically active";
  if (o <= 4) return "MODERATE - Actively felt, requires awareness";
  return "WIDE - Subliminal, background, requires conscious effort";
}

const moonAspects = aspectTable([
  aRow(
    "Moon Sextile Mercury", "0°15'", orbLevel("0.25"), "Throat",
    "Moon: Third Eye | Stomach, fluids, emotional tides",
    "Mercury: Throat | Nervous system, communication",
    "Yin fluid body (Moon) cooperates with Lung/Large Intestine (Mercury). Emotional fluids and breath communicate freely.",
    "TIGHT HARMONY. Emotions and nervous system speak the same language. Gut feelings translate directly into words. Digestive system and nervous system are cooperative partners.",
    "Journaling, spoken emotional processing, and breathwork are primary healing modalities. When emotionally activated, the body clears through voice and breath.",
    "F9F0FF"
  ),
  aRow(
    "Moon Sextile Mars", "0°6'", orbLevel("0.1"), "Throat",
    "Moon: Third Eye | Stomach, fluids, emotional tides",
    "Mars: Solar Plexus | Inflammation, drive, heat",
    "Yin fluid body (Moon) cooperates with Liver fire (Mars). Emotional tides and physical heat are in productive dialogue.",
    "EXTREMELY TIGHT HARMONY. Tightest orb in the chart. Emotional body and physical drive are almost perfectly synchronized. Stomach/fluid system and inflammatory/muscular system cooperate. When you feel it emotionally you move on it physically almost instantly.",
    "Physical movement as emotional processing is the primary healing pathway. Exercise, dance, physical expression of emotion prevents inflammation build-up from emotional suppression.",
    "FFFFFF"
  ),
  aRow(
    "Moon Trine Saturn", "0°52'", orbLevel("0.87"), "Heart",
    "Moon: Third Eye | Stomach, fluids, emotional tides",
    "Saturn: Root | Bones, structure, skeletal system",
    "Yin fluid body (Moon) flows harmoniously with Kidney Jing (Saturn). Emotional body and foundational physical structure are in ease.",
    "TIGHT HARMONY. Emotional stability supports physical structural integrity. Stomach and fluid systems flow well with skeletal and joint health. Emotional processing does not undermine physical foundations.",
    "Consistent emotional routines (structured self-care, regular meals, sleep hygiene) strengthen both emotional regulation and bone/joint health simultaneously.",
    "F9F0FF"
  ),
  aRow(
    "Moon Square Uranus", "5°54'", orbLevel("5.9"), "Root / Solar Plexus",
    "Moon: Third Eye | Stomach, fluids, emotional tides",
    "Uranus: Third Eye | Neurological disruption, awakening",
    "Yin fluid body (Moon) in friction with Triple Burner (Uranus). Emotional tides disrupted by sudden neurological activation.",
    "WIDE FRICTION. Both planets share Third Eye but the Square creates tension between emotional fluid rhythms and sudden nervous system disruptions. Stomach irregularities triggered by emotional shocks. Fluid retention or depletion linked to nervous system dysregulation.",
    "Nervous system regulation practices (vagal toning, cold/warm alternating, grounding) prevent emotional disruptions from destabilizing stomach and fluid systems.",
    "FFFFFF"
  ),
  aRow(
    "Moon Sextile Neptune", "3°42'", orbLevel("3.7"), "Throat",
    "Moon: Third Eye | Stomach, fluids, emotional tides",
    "Neptune: Crown | Immunity, dissolution, lymphatic",
    "Yin fluid body (Moon) cooperates with Governing Vessel (Neptune). Emotional fluids and immune/lymphatic systems support each other.",
    "MODERATE HARMONY. Emotional health directly supports immune function. When emotionally at peace, lymphatic flow is supported. Emotional turbulence creates immune vulnerability.",
    "Meditation, energy clearing, and emotional release practices maintain both emotional equilibrium and immune resilience. HSP sensitivity is a feature not a flaw here.",
    "F9F0FF"
  ),
  aRow(
    "Moon Trine Pluto", "4°31'", orbLevel("4.5"), "Heart",
    "Moon: Third Eye | Stomach, fluids, emotional tides",
    "Pluto: Crown | Elimination, cellular transformation",
    "Yin fluid body (Moon) flows harmoniously with deep Jing transformation (Pluto). Emotional body and cellular elimination are natural allies.",
    "MODERATE HARMONY. Emotional processing supports deep cellular detoxification. The stomach and fluid systems work with elimination and reproductive systems in a healing flow. Emotional releases create physical detox responses.",
    "Deep emotional work (therapy, shadow work, somatic release) triggers genuine cellular-level healing. Crying, sweating, and emotional purging are literal detox pathways.",
    "FFFFFF"
  ),
  aRow(
    "Moon Trine North Node", "5°4'", orbLevel("5.1"), "Heart",
    "Moon: Third Eye | Stomach, fluids, emotional tides",
    "North Node: Third Eye | Soul destiny, karmic direction",
    "Yin fluid body (Moon) flows harmoniously with soul evolutionary path (North Node). Emotional intelligence IS the destiny path.",
    "WIDE HARMONY. Emotional body and soul mission are naturally aligned. Following emotional truth leads toward destiny. Stomach and fluid health are supported when living in alignment with soul purpose.",
    "Trust emotional guidance as soul navigation. Gut feelings about direction are accurate. Emotional health and soul alignment are the same practice.",
    "F9F0FF"
  ),
  aRow(
    "Moon Opposition Vertex", "3°12'", orbLevel("3.2"), "Root",
    "Moon: Third Eye | Stomach, fluids, emotional tides",
    "Vertex: Third Eye | Fated encounters, destined meetings",
    "AXIS: Cancer/Virgo adjacent axis. Yin fluid body in tension with fated relational encounters. Emotional body pulled against destiny contact points.",
    "MODERATE TENSION. Fated encounters trigger emotional body disruptions. Stomach upset, fluid irregularities, and emotional flooding around destined meetings. Tension between emotional security needs and fated relational transformation.",
    "Grounding practices before and after significant encounters. Recognize stomach responses as intuitive data about fated connections. Body is the oracle.",
    "FFFFFF"
  ),
]);

const mercuryAspects = aspectTable([
  aRow(
    "Mercury Conjunction Mars", "0°21'", orbLevel("0.35"), "Solar Plexus / Heart",
    "Mercury: Throat | Nervous system, communication",
    "Mars: Solar Plexus | Inflammation, muscular, adrenal",
    "Lung/Large Intestine (Mercury) fused with Liver fire (Mars). Thought and action are the same system. Mind and inflammation share a channel.",
    "TIGHT FUSION. Thinking triggers immediate physical action. Nervous system and inflammatory system are merged. Mental overload creates physical inflammation. Racing thoughts create muscular tension. Communication and drive cannot be separated.",
    "Physical movement clears mental overload. Anti-inflammatory practices (omega-3s, cooling foods, rest) support both nervous system and inflammation management. Never intellectualize without moving the body.",
    "F9F0FF"
  ),
  aRow(
    "Mercury Opposition Saturn", "1°7'", orbLevel("1.1"), "Root",
    "Mercury: Throat | Nervous system, communication",
    "Saturn: Root | Bones, structure, skeletal",
    "AXIS: Gemini/Sagittarius axis. Lung/Large Intestine (Mercury) in tension with Kidney Jing (Saturn). Communication system pulled against structural foundations.",
    "TIGHT TENSION. Internalized critique around thinking and communication (Mercury opposition Saturn is the classic self-censorship aspect). Nervous system tension creates skeletal holding patterns. Tight neck, jaw, shoulders from suppressed communication. Grief held in the lungs from unexpressed words.",
    "Voice work, singing, and authentic expression release the skeletal holding patterns. What you do not say, your body holds. Jaw release, neck massage, and breathwork are specific physical healing pathways.",
    "FFFFFF"
  ),
  aRow(
    "Mercury Trine Neptune", "3°58'", orbLevel("3.97"), "Heart",
    "Mercury: Throat | Nervous system, communication",
    "Neptune: Crown | Immunity, dissolution, lymphatic",
    "Lung/Large Intestine (Mercury) flows harmoniously with Governing Vessel (Neptune). Nervous system and immune system are natural allies.",
    "MODERATE HARMONY. Clear communication supports immune health. Spiritual and creative expression strengthens the nervous system. Lymphatic flow supported by mental clarity and release of what no longer serves.",
    "Creative writing, music, and spiritual communication practices maintain both nervous system health and immune resilience. The voice is an immune system tool.",
    "F9F0FF"
  ),
  aRow(
    "Mercury Opposition Pluto", "4°46'", orbLevel("4.77"), "Root",
    "Mercury: Throat | Nervous system, communication",
    "Pluto: Crown | Elimination, cellular transformation",
    "AXIS: Taurus/Scorpio axis - intake/elimination. Lung/Large Intestine (Mercury) in tension with deep Jing transformation (Pluto). Communication and elimination systems pulled against each other.",
    "MODERATE TENSION. Words not spoken become cellular toxins. What is suppressed mentally creates elimination blockages physically. Power dynamics in communication create nervous system dysregulation. Obsessive thinking patterns disrupt elimination pathways.",
    "Speaking truth, even when difficult, is a detox practice. Shadow journaling and honest self-expression release both nervous system tension and cellular elimination blockages.",
    "FFFFFF"
  ),
  aRow(
    "Mercury Trine Vertex", "2°57'", orbLevel("2.97"), "Heart",
    "Mercury: Throat | Nervous system, communication",
    "Vertex: Third Eye | Fated encounters, destined meetings",
    "Lung/Large Intestine (Mercury) flows harmoniously with Third Eye destiny point (Vertex). Voice and fated encounters are natural allies.",
    "MODERATE HARMONY. Fated meetings happen through communication. Destined connections are made through the voice and nervous system. Words spoken at the right moment catalyze destiny contacts.",
    "Trust your voice in significant encounters. What you say in fated moments is guided. Nervous system intuition about when to speak is accurate.",
    "F9F0FF"
  ),
  aRow(
    "Mercury Square Ascendant", "5°27'", orbLevel("5.45"), "Root / Solar Plexus",
    "Mercury: Throat | Nervous system, communication",
    "Ascendant: Root | Physical body, first impression, identity",
    "Lung/Large Intestine (Mercury) in friction with Root identity layer. Communication style in tension with how the body presents itself to the world.",
    "WIDE FRICTION. How you think does not always match how you appear. Nervous system presentation may differ from physical presence. Communication can feel at odds with embodied identity. Background tension between voice and body language.",
    "Embodiment practices that integrate voice and physical presence (movement, performance, vocal embodiment work) bridge the gap between mental communication and physical identity expression.",
    "FFFFFF"
  ),
]);

const venusAspects = aspectTable([
  aRow(
    "Venus Conjunction Chiron", "0°13'", orbLevel("0.22"), "Solar Plexus / Heart",
    "Venus: Heart | Kidneys, skin, hormonal balance",
    "Chiron: Third Eye | Wound and gift, healing wisdom",
    "Pericardium/Heart (Venus) fused with Third Eye healing wisdom (Chiron). Love and the wound are the same activation point.",
    "EXTREMELY TIGHT FUSION. Second tightest orb in the chart. The love wound and the love gift are inseparable. Kidney and skin health directly tied to the healing journey around love and self-worth. Hormonal patterns reflect the wound-gift integration process.",
    "The healing of the love wound IS the gift. Skincare and kidney support as self-love practices. Hormonal health improves as self-worth deepens. This conjunction is the heart of the Chiron in Heart placement.",
    "F9F0FF"
  ),
  aRow(
    "Venus Sextile Part of Fortune", "0°30'", orbLevel("0.5"), "Throat",
    "Venus: Heart | Kidneys, skin, hormonal balance",
    "Part of Fortune: Sacral | Prosperity, luck, creative flow",
    "Pericardium/Heart (Venus) cooperates with creative Sacral fortune (Part of Fortune). Love and prosperity are in easy dialogue.",
    "TIGHT HARMONY. Financial and creative abundance flows easily through love and heart-centered action. Skin and kidney health supported when living in alignment with creative prosperity. Self-love activates luck.",
    "Heart-centered business and creative work is the prosperity pathway. Acts of love and beauty are financially supported. Kidney nourishment (water, rest, warmth) supports both health and abundance flow.",
    "FFFFFF"
  ),
  aRow(
    "Venus Opposition Midheaven", "0°21'", orbLevel("0.35"), "Root",
    "Venus: Heart | Kidneys, skin, hormonal balance",
    "Midheaven: Solar Plexus | Career, public reputation, authority",
    "AXIS: Taurus/Scorpio axis - intake/elimination intersecting career axis. Pericardium/Heart (Venus) in tension with Solar Plexus public power (MC).",
    "TIGHT TENSION. Love values and career ambition in direct tension. Kidney and hormonal health affected by career stress. Skin conditions can flare during professional pressure. The private heart and the public power face pull against each other.",
    "Career choices aligned with heart values reduce the physical tension in kidneys and hormonal system. Boundary work between professional performance and personal love life supports skin and hormonal health.",
    "F9F0FF"
  ),
]);

const marsAspects = aspectTable([
  aRow(
    "Mars Opposition Saturn", "0°46'", orbLevel("0.77"), "Root",
    "Mars: Solar Plexus | Inflammation, drive, muscular",
    "Saturn: Root | Bones, structure, skeletal",
    "AXIS: Taurus/Scorpio axis - intake/elimination. Liver fire (Mars) in tight tension with Kidney Jing (Saturn). Drive and structure in direct opposition.",
    "TIGHT TENSION. Muscular inflammation and skeletal restriction pulling against each other. Adrenal burnout from pushing against structural limitations. Joint inflammation where drive meets restriction. Classic overwork-collapse cycle when not managed.",
    "Rest is not laziness, it is structural maintenance. Alternating phases of intense action with genuine rest prevents adrenal and joint damage. Anti-inflammatory foods and skeletal support (magnesium, calcium) are primary physical supports.",
    "F9F0FF"
  ),
  aRow(
    "Mars Trine Neptune", "3°36'", orbLevel("3.6"), "Heart",
    "Mars: Solar Plexus | Inflammation, drive, muscular",
    "Neptune: Crown | Immunity, dissolution, lymphatic",
    "Liver fire (Mars) flows harmoniously with Governing Vessel (Neptune). Physical drive and immune system are natural allies.",
    "MODERATE HARMONY. Physical action supports immune health. Movement and exercise strengthen lymphatic flow. Spiritual motivation behind physical drive creates sustainable energy without immune depletion.",
    "Exercise with spiritual intention (yoga, tai chi, qigong, intentional movement) maintains both drive and immune strength. Movement as spiritual practice is the optimal expression of this trine.",
    "FFFFFF"
  ),
  aRow(
    "Mars Opposition Pluto", "4°25'", orbLevel("4.42"), "Root",
    "Mars: Solar Plexus | Inflammation, drive, muscular",
    "Pluto: Crown | Elimination, cellular transformation",
    "AXIS: Taurus/Scorpio axis - intake/elimination. Liver fire (Mars) in tension with deep Jing transformation (Pluto). Drive and elimination in opposition.",
    "MODERATE TENSION. Intense physical drive creates cellular toxin buildup when elimination is blocked. Muscular inflammation linked to elimination system dysfunction. Power struggles create physical inflammation patterns.",
    "Regular elimination support (hydration, fiber, liver herbs) prevents inflammatory buildup from high-drive activity. Transformational physical practices (intense yoga, martial arts) channel Pluto-Mars tension productively.",
    "F9F0FF"
  ),
  aRow(
    "Mars Sextile North Node", "4°58'", orbLevel("4.97"), "Throat",
    "Mars: Solar Plexus | Inflammation, drive, muscular",
    "North Node: Third Eye | Soul destiny, karmic direction",
    "Liver fire (Mars) cooperates with soul evolutionary path (North Node). Drive and destiny are in productive dialogue.",
    "MODERATE HARMONY. Physical action aligned with soul purpose creates sustainable drive without inflammatory overload. Moving toward destiny reduces adrenal stress.",
    "Purpose-driven physical activity (movement, creation, building toward mission) is the optimal health expression. The body thrives when drive is channeled toward soul-aligned goals.",
    "FFFFFF"
  ),
  aRow(
    "Mars Trine Vertex", "3°18'", orbLevel("3.3"), "Heart",
    "Mars: Solar Plexus | Inflammation, drive, muscular",
    "Vertex: Third Eye | Fated encounters, destined meetings",
    "Liver fire (Mars) flows harmoniously with Third Eye destiny point (Vertex). Physical action and fated encounters are naturally aligned.",
    "MODERATE HARMONY. Fated meetings often happen through physical action, movement, and drive. The body is the instrument of destiny contact. Physical vitality supports destined connections.",
    "Stay physically active and in motion. Fated connections find you when you are moving toward something. Physical health supports destiny activation.",
    "F9F0FF"
  ),
  aRow(
    "Mars Square Ascendant", "5°48'", orbLevel("5.8"), "Root / Solar Plexus",
    "Mars: Solar Plexus | Inflammation, drive, muscular",
    "Ascendant: Root | Physical body, first impression",
    "Liver fire (Mars) in friction with Root physical identity. Drive and physical presentation in background tension.",
    "WIDE FRICTION. Physical drive can override or clash with physical body needs. Tendency to push the body past its limits because identity is tied to performance. Background inflammatory tension in the physical form.",
    "Body listening practices prevent drive from overriding physical signals. The body is not a vehicle for the will. It is a partner. Rest as identity practice reduces chronic inflammatory background.",
    "FFFFFF"
  ),
]);

const jupiterAspects = aspectTable([
  aRow(
    "Jupiter Conjunction Uranus", "1°52'", orbLevel("1.87"), "Solar Plexus / Heart",
    "Jupiter: Sacral | Liver expansion, abundance, hips",
    "Uranus: Third Eye | Neurological disruption, awakening",
    "Liver/Gallbladder (Jupiter) fused with Triple Burner (Uranus). Expansion and awakening share the same channel. Liver and neurological systems are merged.",
    "TIGHT FUSION. Sudden expansions in consciousness create immediate physical liver and hip responses. Neurological awakenings can trigger liver detox surges. Abundance and disruption are the same activation. This is the Jupiter-Uranus 11th house conjunction that defines the community awakening role.",
    "Liver support during expansion phases (milk thistle, dandelion, clean hydration). Hip mobility practices support neurological integration. Expect physical expansion symptoms during awakening periods.",
    "F9F0FF"
  ),
  aRow(
    "Jupiter Square Vertex", "4°34'", orbLevel("4.57"), "Root / Solar Plexus",
    "Jupiter: Sacral | Liver, hips, abundance",
    "Vertex: Third Eye | Fated encounters, destined meetings",
    "Liver/Gallbladder (Jupiter) in friction with Third Eye destiny point (Vertex). Expansion and fated encounters create physical tension.",
    "MODERATE FRICTION. Fated encounters can trigger over-expansion or liver stress. Tendency to overextend physically and emotionally in destined meetings. Hip tension around significant encounters.",
    "Boundaries in fated encounters protect liver and hip health. Not every destined meeting requires full expansion. Discernment between genuine soul growth and overextension.",
    "FFFFFF"
  ),
  aRow(
    "Jupiter Sextile Ascendant", "2°4'", orbLevel("2.07"), "Throat",
    "Jupiter: Sacral | Liver, hips, abundance",
    "Ascendant: Root | Physical body, first impression",
    "Liver/Gallbladder (Jupiter) cooperates with Root physical identity. Expansion and embodied presence are in productive dialogue.",
    "TIGHT HARMONY. Physical presence and liver/expansion health are cooperative. The body expands naturally and abundantly when in alignment. Hip health supports physical confidence and presence.",
    "Physical confidence practices (posture, movement, presence work) support liver and hip health. Abundance flows through embodied physical presence. Show up in the body.",
    "F9F0FF"
  ),
]);

const saturnAspects = aspectTable([
  aRow(
    "Saturn Sextile Neptune", "2°51'", orbLevel("2.85"), "Throat",
    "Saturn: Root | Bones, structure, skeletal",
    "Neptune: Crown | Immunity, dissolution, lymphatic",
    "Kidney Jing (Saturn) cooperates with Governing Vessel (Neptune). Physical structure and spiritual immune system are productive partners.",
    "TIGHT HARMONY. Spiritual discipline strengthens physical structure. Structured spiritual practice maintains immune health. Bones and immune system support each other when spirituality has form and discipline.",
    "Consistent spiritual practice (not just inspiration but actual discipline) is both bone-strengthening and immune-supporting. Meditation with structure. Ritual with regularity.",
    "F9F0FF"
  ),
  aRow(
    "Saturn Conjunction Pluto", "3°39'", orbLevel("3.65"), "Solar Plexus / Heart",
    "Saturn: Root | Bones, structure, skeletal",
    "Pluto: Crown | Elimination, cellular transformation",
    "Kidney Jing (Saturn) fused with deep Jing transformation (Pluto). Both are Jing-level activations. Structure and transformation are merged at the deepest physical layer.",
    "MODERATE FUSION. Bone density and cellular elimination are linked systems. Structural restrictions create elimination blockages. Deep transformation requires structural breakdown. Skeletal holding patterns store cellular toxins.",
    "Deep bodywork (structural integration, rolfing, bone-level somatic work) releases both skeletal restriction and cellular toxin accumulation simultaneously. This conjunction responds to profound physical transformation practices.",
    "FFFFFF"
  ),
  aRow(
    "Saturn Trine North Node", "4°12'", orbLevel("4.2"), "Heart",
    "Saturn: Root | Bones, structure, skeletal",
    "North Node: Third Eye | Soul destiny, karmic direction",
    "Kidney Jing (Saturn) flows harmoniously with soul evolutionary path (North Node). Physical structure and soul mission are natural allies.",
    "MODERATE HARMONY. Building toward soul destiny strengthens physical foundations. Karmic discipline supports skeletal and structural health. Long-term commitment to purpose maintains physical integrity.",
    "Long-term soul-aligned projects are bone-strengthening practices. Consistency and discipline in service of purpose maintains physical structural health.",
    "F9F0FF"
  ),
  aRow(
    "Saturn Sextile Vertex", "4°4'", orbLevel("4.07"), "Throat",
    "Saturn: Root | Bones, structure, skeletal",
    "Vertex: Third Eye | Fated encounters, destined meetings",
    "Kidney Jing (Saturn) cooperates with Third Eye destiny point (Vertex). Structure and fated encounters are productive partners.",
    "MODERATE HARMONY. Fated encounters build physical and karmic structure. Destined meetings have long-term structural consequences. Bone and joint health supported when engaging with destiny contacts with integrity.",
    "Approach fated encounters with long-term structural thinking. What gets built from these meetings matters more than the immediate experience.",
    "FFFFFF"
  ),
  aRow(
    "Saturn Square Ascendant", "6°34'", orbLevel("6.57"), "Root / Solar Plexus",
    "Saturn: Root | Bones, structure, skeletal",
    "Ascendant: Root | Physical body, first impression",
    "Double Root activation in Square friction. Kidney Jing and physical identity structure pulling against each other.",
    "WIDE FRICTION. Physical self-presentation feels restricted or heavy. Body carries structural tension as identity armor. Bone and joint issues linked to identity suppression. Background tension between who you are and how you hold yourself.",
    "Posture and structural bodywork releases identity armor. As self-expression expands, physical holding patterns in bones and joints soften. The body stops carrying suppression when identity is fully expressed.",
    "F9F0FF"
  ),
]);

const uranusAspects = aspectTable([
  aRow(
    "Uranus Square Vertex", "2°42'", orbLevel("2.7"), "Root / Solar Plexus",
    "Uranus: Third Eye | Neurological disruption, awakening",
    "Vertex: Third Eye | Fated encounters, destined meetings",
    "Double Third Eye activation in Square friction. Triple Burner (Uranus) in tension with Third Eye destiny point (Vertex). Both intuitive systems pulling against each other.",
    "TIGHT FRICTION. Sudden neurological disruptions around fated encounters. Awakenings triggered by destined meetings create nervous system shock. Physical electrical responses (shivers, sudden knowing, body sensations) at destiny contact points.",
    "Ground immediately after significant encounters. Neurological support (magnesium, grounding practices, nature contact) after major awakening contacts. The body is registering something real.",
    "FFFFFF"
  ),
  aRow(
    "Uranus Sextile Ascendant", "0°12'", orbLevel("0.2"), "Throat",
    "Uranus: Third Eye | Neurological disruption, awakening",
    "Ascendant: Root | Physical body, first impression",
    "Triple Burner (Uranus) cooperates with Root physical identity. Neurological awakening and physical presence are in extremely tight productive dialogue.",
    "EXTREMELY TIGHT HARMONY. Third tightest orb in the chart. The body IS the awakening instrument. Physical presence catalyzes neurological activation in others. The Aquarius Rising is perfectly supported by Uranus here. The body radiates awakening frequency.",
    "Trust the physical body as an awakening tool. Embodiment practices amplify the neurological awakening gift. The physical presence is not separate from the spiritual mission.",
    "F9F0FF"
  ),
]);

const neptuneAspects = aspectTable([
  aRow(
    "Neptune Sextile Pluto", "0°48'", orbLevel("0.8"), "Throat",
    "Neptune: Crown | Immunity, dissolution, lymphatic",
    "Pluto: Crown | Elimination, cellular transformation",
    "Double Crown activation in Sextile harmony. Governing Vessel (Neptune) cooperates with deep Jing transformation (Pluto). Both highest-frequency planets in productive dialogue.",
    "TIGHT HARMONY. Spiritual dissolution and cellular transformation support each other. Immune health and elimination health are cooperative systems. Deep spiritual work triggers cellular detox. This is a generational aspect but personally activated through the chart.",
    "Deep spiritual practices that include physical detox components (fasting, cleansing, ceremony) activate both systems simultaneously. Spiritual transformation IS physical transformation at the cellular level.",
    "FFFFFF"
  ),
  aRow(
    "Neptune Opposition North Node", "1°21'", orbLevel("1.35"), "Root",
    "Neptune: Crown | Immunity, dissolution, lymphatic",
    "North Node: Third Eye | Soul destiny, karmic direction",
    "AXIS: Virgo/Pisces axis - digestion/detoxification. Governing Vessel (Neptune) in tension with soul evolutionary path (North Node). Spiritual dissolution and soul direction pulling against each other.",
    "TIGHT TENSION. Spiritual sensitivity (HSP, psychic absorption, dissolution of boundaries) in tension with soul purpose direction. Immune health affected when soul direction is unclear or avoided. Lymphatic congestion linked to spiritual confusion or avoidance of destiny.",
    "Clarity of soul direction is an immune practice. When the path is clear, the immune system is supported. Practices that combine spiritual clarity with physical detox (grounding, lymphatic massage, clarity rituals) address both systems.",
    "F9F0FF"
  ),
  aRow(
    "Neptune Square Part of Fortune", "4°33'", orbLevel("4.55"), "Root / Solar Plexus",
    "Neptune: Crown | Immunity, dissolution, lymphatic",
    "Part of Fortune: Sacral | Prosperity, luck, creative flow",
    "Governing Vessel (Neptune) in friction with creative Sacral fortune. Spiritual dissolution and material prosperity in tension.",
    "MODERATE FRICTION. Spiritual sensitivity can dissolve material abundance if not grounded. Immune health and creative prosperity are in friction. Tendency to give away abundance or dissolve financial boundaries. Lymphatic health affected during financial stress.",
    "Financial grounding practices (budgeting, tangible abundance rituals, earth-based prosperity work) support both immune health and creative prosperity. Ground the spiritual gifts into material form.",
    "FFFFFF"
  ),
]);

const plutoAspects = aspectTable([
  aRow(
    "Pluto Trine North Node", "0°33'", orbLevel("0.55"), "Heart",
    "Pluto: Crown | Elimination, cellular transformation",
    "North Node: Third Eye | Soul destiny, karmic direction",
    "Deep Jing transformation (Pluto) flows harmoniously with soul evolutionary path (North Node). Cellular transformation and soul destiny are natural allies.",
    "TIGHT HARMONY. Deep transformation IS the soul path. Cellular elimination and rebirth directly support destiny activation. The death-rebirth cycle is a destiny feature not a disruption.",
    "Embrace transformational cycles as destiny activations. Cellular cleansing practices (fasting, detox, shadow work) accelerate soul path alignment. What is eliminated creates space for destiny.",
    "F9F0FF"
  ),
]);

const chironAspects = aspectTable([
  aRow(
    "Chiron Sextile Part of Fortune", "0°18'", orbLevel("0.3"), "Throat",
    "Chiron: Third Eye | Wound and gift, healing wisdom",
    "Part of Fortune: Sacral | Prosperity, luck, creative flow",
    "Third Eye healing wisdom (Chiron) cooperates with creative Sacral fortune (Part of Fortune). The wound and the prosperity are in tight productive dialogue.",
    "TIGHT HARMONY. The healing journey IS the prosperity pathway. The wound, when integrated as gift, activates creative abundance. Healing others through your own wound experience creates fortune.",
    "Sharing your healing journey creates abundance. The wound monetized as wisdom is the Part of Fortune activation. Healing work, coaching, and guide work are the prosperity expression of this aspect.",
    "FFFFFF"
  ),
  aRow(
    "Chiron Opposition Midheaven", "0°33'", orbLevel("0.55"), "Root",
    "Chiron: Third Eye | Wound and gift, healing wisdom",
    "Midheaven: Solar Plexus | Career, public reputation, authority",
    "AXIS: Taurus/Scorpio axis. Third Eye healing wisdom in tight tension with Solar Plexus public power. The wound and the career in direct opposition.",
    "TIGHT TENSION. Career and public reputation are directly tied to the healing wound. The wound is publicly visible. The career IS the wound transformed into gift. Hormonal and skin health (Chiron in Taurus/Venus ruled) affected by career stress and public exposure.",
    "The career is not separate from the healing journey. It IS the healing journey made public. Accepting this reduces the physical tension between wound and public expression. Skincare and hormonal support during high-visibility professional periods.",
    "F9F0FF"
  ),
]);

const nodeAspects = aspectTable([
  aRow(
    "North Node Square Part of Fortune", "3°12'", orbLevel("3.2"), "Root / Solar Plexus",
    "North Node: Third Eye | Soul destiny, karmic direction",
    "Part of Fortune: Sacral | Prosperity, luck, creative flow",
    "Soul evolutionary path in friction with creative Sacral fortune. Destiny and prosperity in tension.",
    "MODERATE FRICTION. The soul destiny path and the prosperity path are not always aligned. Choosing destiny can feel financially risky. Choosing prosperity can feel like avoiding soul purpose. Creative abundance and soul mission create physical tension when misaligned.",
    "When soul purpose and prosperity feel at odds, choose soul purpose. The friction resolves when the work becomes the mission. Trust that destiny-aligned work eventually becomes the fortune.",
    "FFFFFF"
  ),
  aRow(
    "North Node Quincunx Midheaven", "2°21'", orbLevel("2.35"), "Sacral / Third Eye",
    "North Node: Third Eye | Soul destiny, karmic direction",
    "Midheaven: Solar Plexus | Career, public reputation, authority",
    "Soul evolutionary path in awkward adjustment with Solar Plexus public power. Destiny and career require constant recalibration.",
    "TIGHT ADJUSTMENT. Soul direction and career trajectory never quite align perfectly. Constant adjustment required between what the soul needs and what the career demands. This is a chronic low-level tension that requires ongoing conscious integration.",
    "Regular career alignment check-ins. The career serves the soul not the other way around. When career drifts from soul purpose, physical symptoms appear as recalibration signals. Listen to the body's signals about career alignment.",
    "F9F0FF"
  ),
]);

const fortuneAspects = aspectTable([
  aRow(
    "Part of Fortune Trine Midheaven", "0°51'", orbLevel("0.85"), "Heart",
    "Part of Fortune: Sacral | Prosperity, luck, creative flow",
    "Midheaven: Solar Plexus | Career, public reputation, authority",
    "Creative Sacral fortune flows harmoniously with Solar Plexus public power. Prosperity and career are natural allies.",
    "TIGHT HARMONY. Creative abundance and career success flow easily together. Sacral creative energy directly supports public reputation and career pinnacle. Fortune activates through career expression.",
    "Creative work expressed publicly activates prosperity. The career IS the fortune pathway. Sacral creative health (emotional expression, creativity, joy) directly supports career success.",
    "FFFFFF"
  ),
]);

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
        size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 }
      }
    },
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "TCM ASTROLOGY CHAKRA SYSTEM", bold: true, size: 48, color: "4A0E4E", font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "Full Aspect Analysis - Deep Medical Chakra Layer", bold: true, size: 32, color: "8B1A8B", font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "Christina Stevens | April 9, 1983 | Hobbs NM | UTC -7", italics: true, size: 24, color: "C2185B", font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 300 },
        children: [new TextRun({ text: "Phoenix Rebirth | Aurelia Reign | Proprietary System | April 2026", size: 20, color: "999999", font: "Arial" })]
      }),
      divider(),
      note("Each aspect is analyzed across 9 dimensions: the two planets involved with their chakra and body system, the aspect type and its chakra activation, orb intensity and physical immediacy, TCM meridian interaction between the two organ systems, specific body tension or harmony created, and the healing pathway indicated. Tight orbs (0-2 degrees) are immediate and physically active. Moderate orbs (2-5 degrees) require awareness. Wide orbs (5+ degrees) are subliminal background influences."),
      spacer(),

      h1("MOON ASPECTS (8 aspects)"),
      note("Moon carries: Third Eye chakra | Stomach, fluids, emotional tides | Yin fluid body"),
      spacer(),
      moonAspects,
      pageBreak(),

      h1("MERCURY ASPECTS (6 aspects)"),
      note("Mercury carries: Throat chakra | Nervous system, communication | Lung/Large Intestine meridians"),
      spacer(),
      mercuryAspects,
      pageBreak(),

      h1("VENUS ASPECTS (3 aspects)"),
      note("Venus carries: Heart chakra | Kidneys, skin, hormonal balance | Pericardium meridian"),
      spacer(),
      venusAspects,
      pageBreak(),

      h1("MARS ASPECTS (6 aspects)"),
      note("Mars carries: Solar Plexus chakra | Inflammation, drive, muscular, adrenal | Liver fire"),
      spacer(),
      marsAspects,
      pageBreak(),

      h1("JUPITER ASPECTS (3 aspects)"),
      note("Jupiter carries: Sacral chakra | Liver expansion, abundance, hips | Liver/Gallbladder Wood element"),
      spacer(),
      jupiterAspects,
      pageBreak(),

      h1("SATURN ASPECTS (5 aspects)"),
      note("Saturn carries: Root chakra | Bones, structure, skeletal system | Kidney Jing essence"),
      spacer(),
      saturnAspects,
      pageBreak(),

      h1("URANUS ASPECTS (2 aspects)"),
      note("Uranus carries: Third Eye chakra | Neurological disruption, awakening | Triple Burner"),
      spacer(),
      uranusAspects,
      pageBreak(),

      h1("NEPTUNE ASPECTS (3 aspects)"),
      note("Neptune carries: Crown chakra | Immunity, dissolution, lymphatic | Governing Vessel"),
      spacer(),
      neptuneAspects,
      pageBreak(),

      h1("PLUTO ASPECTS (1 aspect)"),
      note("Pluto carries: Crown chakra | Elimination, cellular transformation | Deep Jing"),
      spacer(),
      plutoAspects,
      pageBreak(),

      h1("CHIRON ASPECTS (2 aspects)"),
      note("Chiron carries: Third Eye chakra | Wound and gift, healing wisdom | Integrative healing"),
      spacer(),
      chironAspects,
      pageBreak(),

      h1("NORTH NODE ASPECTS (2 aspects)"),
      note("North Node carries: Third Eye chakra | Soul destiny, karmic direction | Evolutionary pathway"),
      spacer(),
      nodeAspects,
      pageBreak(),

      h1("PART OF FORTUNE ASPECTS (1 aspect)"),
      note("Part of Fortune carries: Third Eye chakra | Prosperity, luck, creative fortune | Abundance activation"),
      spacer(),
      fortuneAspects,
      pageBreak(),

      h1("MASTER HEALTH PATTERN SUMMARY"),
      divider(),
      h2("Critical Tight Orb Aspects (0-2 degrees) - Immediate Physical Activation"),
      body("Moon Sextile Mars 0°6' - Emotional body and inflammation are the most tightly linked systems in the chart. Movement IS emotional regulation."),
      body("Venus Conjunction Chiron 0°13' - Love wound and hormonal/kidney/skin health are almost perfectly merged. Self-love is a physical health practice."),
      body("Uranus Sextile Ascendant 0°12' - The body radiates awakening. Physical presence is a neurological instrument."),
      body("Chiron Sextile Part of Fortune 0°18' - The healing wound directly creates prosperity. This is the tightest prosperity aspect in the chart."),
      body("Venus Opposition Midheaven 0°21' - Career stress directly impacts kidney, skin, and hormonal health. Love values and career power are in constant physical negotiation."),
      body("Mercury Conjunction Mars 0°21' - Thinking and inflammation are fused. Mental overload creates physical heat and tension immediately."),
      body("Chiron Opposition Midheaven 0°33' - Career and wound are in tight public tension. The public healing journey IS the career."),
      body("Pluto Trine North Node 0°33' - Transformation and destiny flow easily. Death-rebirth cycles are destiny features."),
      spacer(),

      h2("Primary Physical Vulnerability Patterns"),
      body("Nervous system and inflammation (Mercury Conjunction Mars): Mental activity creates immediate physical heat. Cooling and movement are non-negotiable health practices."),
      body("Bones and drive (Mars Opposition Saturn): Overwork-collapse cycle is the primary structural health risk. Rest IS structural maintenance."),
      body("Communication suppression and skeletal holding (Mercury Opposition Saturn): Unsaid words create physical holding patterns in neck, jaw, and shoulders."),
      body("Emotional shock and stomach disruption (Moon Square Uranus): Sudden events destabilize digestive and fluid systems. Nervous system regulation protects gut health."),
      body("Career stress and hormonal/kidney/skin health (Venus Opposition Midheaven): Professional pressure has direct physical consequences in endocrine system."),
      body("Spiritual sensitivity and immune health (Neptune Opposition North Node): Soul direction confusion creates immune vulnerability."),
      spacer(),

      h2("Primary Physical Strength Patterns"),
      body("Emotional movement and physical vitality (Moon Sextile Mars 0°6'): The body is built to move emotions through physical expression. This is the strongest healing asset."),
      body("Voice and mind harmony (Mercury Sextile Moon, Mercury Trine Neptune): When speaking truth, nervous system and immune health are both supported simultaneously."),
      body("Love and prosperity cooperation (Venus Sextile Part of Fortune): Heart-centered work activates abundance and physical kidney/skin health together."),
      body("Transformation and destiny flow (Pluto Trine North Node): The body heals most profoundly through transformational cycles aligned with soul purpose."),
      body("Spiritual discipline and structure (Saturn Sextile Neptune): Consistent spiritual practice is bone-strengthening and immune-supporting."),
      spacer(),

      h2("The Axis Health Tensions"),
      body("Taurus/Scorpio axis (intake/elimination): Multiple aspects activate this axis. Mercury Opposition Pluto, Mars Opposition Saturn, Mars Opposition Pluto, Venus Opposition Midheaven all involve this polarity. Intake and elimination systems require ongoing conscious attention and balance. What comes in must go out. On all levels."),
      body("Gemini/Sagittarius axis (lungs/liver): Mercury Opposition Saturn activates this axis. Communication suppression creates both lung/breath tension and liver restriction. Speak and move to maintain both systems."),
      body("Virgo/Pisces axis (digestion/detox): Moon Opposition Vertex touches this axis. Gut health and lymphatic detox are in ongoing negotiation around significant encounters and emotional events."),
      spacer(),

      h2("Orb Intensity Health Summary"),
      body("IMMEDIATE (0-2 degree) physical activations: Mars-Moon, Venus-Chiron, Uranus-Ascendant, Chiron-Part of Fortune, Venus-MC, Mercury-Mars, Chiron-MC, Pluto-North Node, Moon-Mercury, Moon-Mars, Moon-Saturn, Mercury-Saturn, Neptune-North Node. These 13 tight aspects are ALWAYS physically active and do not require conscious effort to activate."),
      body("BACKGROUND (5+ degree) influences requiring conscious effort: Moon Square Uranus, Moon Trine North Node, Mars Square Ascendant, Mercury Square Ascendant, Saturn Square Ascendant. These 5 wide aspects are subliminal and benefit from conscious attention to activate their healing potential or manage their tension."),
      divider(),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 0 },
        children: [new TextRun({ text: "Phoenix Rebirth | TCM Astrology Chakra System - Aspect Analysis | April 2026", italics: true, size: 18, color: "999999", font: "Arial" })]
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
  fs.writeFileSync("/mnt/user-data/outputs/TCM_Astrology_Chakra_Aspect_Analysis.docx", buffer);
  console.log("Done");
});
