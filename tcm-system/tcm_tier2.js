const fs = require('fs');

const {
    Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
    HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType, PageBreak
} = require('docx');

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
        children: [new TextRun({ text, size: 20, italics: true, color: "666666", font: "Arial" })] });
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
    return new Paragraph({ spacing: { before: 80, after: 80 }, children: [new TextRun("")] }); }
function pageBreak() {
    return new Paragraph({ children: [new PageBreak()] }); }

function hRow(cells, cols, color) {
    return new TableRow({ tableHeader: true, children: cells.map((text, i) => new TableCell({
        borders: color === 'accent' ? aBorders : hBorders,
        width: { size: cols[i], type: WidthType.DXA },
        shading: { fill: color === 'accent' ? "C2185B" : "2D0A3E", type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({ children: [new TextRun({ text, bold: true, size: 19, color: "FFFFFF", font: "Arial" })] })]
    }))});
}
function dRow(cells, cols, shade) {
    return new TableRow({ children: cells.map((text, i) => new TableCell({
        borders, width: { size: cols[i], type: WidthType.DXA },
        shading: { fill: shade || "FFFFFF", type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 150, right: 150 },
        children: [new Paragraph({ children: [new TextRun({ text, size: 19, font: "Arial" })] })]
    }))});
}

const CW = 9360;

// ============================================================
// TABLE 1: BENEFIC/MALEFIC PLANET FRAMEWORK
// ============================================================
const bfCols = [1200, 1000, 1200, 1400, 4560];
const beneficTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: bfCols, rows: [
    hRow(["Planet", "Classification", "Chakra", "Physical Force", "Body Health Implications"], bfCols),
    dRow(["Sun", "Generally Benefic", "Third Eye", "Vitality, life force", "When well-aspected: strong cardiovascular health, excellent vitality, clear vision, strong immune system. When afflicted (square, opposition from malefics): heart strain, blood pressure issues, adrenal fatigue, vision problems, ego-driven inflammation."], bfCols, "FFF8F0"),
    dRow(["Moon", "Benefic (waxing) / Neutral (waning)", "Third Eye", "Emotional fluids, cycles", "Waxing Moon energy supports fluid retention, growth, and emotional receptivity. Waning Moon energy supports release, detox, and elimination. Afflicted Moon: digestive irregularities, fluid imbalances, hormonal disruption, emotional eating patterns, stomach sensitivity."], bfCols, "FFFFFF"),
    dRow(["Mercury", "Neutral (adapts to conjunctions)", "Throat", "Nervous system, communication", "Mercury well-aspected: clear nervous system, good coordination, effective communication of symptoms. Mercury afflicted: nervous system dysregulation, anxiety-driven physical symptoms, respiratory sensitivity, communication-suppression body patterns (neck/jaw/shoulder tension)."], bfCols, "FFF8F0"),
    dRow(["Venus", "Lesser Benefic", "Heart", "Harmony, kidneys, skin", "Well-aspected: healthy kidney function, clear skin, balanced hormones, strong connective tissue. Afflicted Venus: kidney strain, skin conditions, hormonal imbalance, blood sugar issues, overconsumption patterns that stress elimination organs."], bfCols, "FFFFFF"),
    dRow(["Mars", "Lesser Malefic", "Solar Plexus", "Heat, inflammation, drive", "Well-aspected: excellent physical energy, strong immune response, healthy aggression/assertion. Afflicted Mars: chronic inflammation, fever patterns, accidents, adrenal overactivation, muscular tension, inflammatory conditions in the body areas governed by the sign/house Mars occupies."], bfCols, "FFF8F0"),
    dRow(["Jupiter", "Greater Benefic", "Sacral", "Expansion, liver, abundance", "Well-aspected: excellent liver function, strong metabolism, good fortune in health. Afflicted Jupiter: overconsumption, liver strain, weight gain through excess, hip issues, over-expansion of health problems, tendency to bypass medical attention assuming natural recovery."], bfCols, "FFFFFF"),
    dRow(["Saturn", "Greater Malefic", "Root", "Structure, restriction, bones", "Well-aspected: strong skeletal integrity, excellent discipline in health practices, longevity. Afflicted Saturn: chronic conditions, structural restrictions, skeletal issues, joint inflammation, dental problems, adrenal suppression, karmic health lessons that repeat until addressed."], bfCols, "FFF8F0"),
    dRow(["Uranus", "Disruptive/Awakening", "Third Eye", "Nervous system disruption", "Well-aspected: innovative health approaches, sudden healings, neurological breakthroughs. Afflicted Uranus: sudden onset conditions, erratic health patterns, nervous system dysregulation, electrical sensitivity, unpredictable symptoms that confuse diagnosis."], bfCols, "FFFFFF"),
    dRow(["Neptune", "Dissolving/Spiritual", "Crown", "Immunity, sensitivity, lymph", "Well-aspected: strong spiritual immunity, sensitivity as gift, psychic health awareness. Afflicted Neptune: immune compromise, mystery illnesses, misdiagnosis patterns, substance sensitivity, boundary dissolution leading to energy depletion, lymphatic congestion."], bfCols, "FFF8F0"),
    dRow(["Pluto", "Transforming/Eliminating", "Crown", "Cellular transformation, elimination", "Well-aspected: profound healing capacity, deep cellular regeneration, transformational health journeys. Afflicted Pluto: obsessive health patterns, power struggles around healing, hidden conditions that erupt suddenly, elimination organ stress, inherited health patterns requiring deep transformation."], bfCols, "FFFFFF"),
    dRow(["North Node Rx", "Karmic Destiny Point", "Third Eye", "Soul direction, evolutionary pull", "Well-aspected: health improves as soul path aligns. Afflicted: immune and digestive stress when avoiding destiny direction. The body registers soul misalignment as physical symptoms."], bfCols, "FFF8F0"),
    dRow(["Chiron", "Planetary Bridge (Wound/Gift)", "Bridge (see system doc)", "Wound activation, healing capacity", "The body area governed by Chiron's house and sign holds both the primary wound pattern AND the primary healing gift. Chiron's aspects to other planets indicate which body systems are involved in the wound-gift integration process."], bfCols, "FFFFFF"),
]});

// ============================================================
// TABLE 2: HOUSE BENEFIC/MALEFIC FRAMEWORK
// ============================================================
const houseBFCols = [800, 1200, 1200, 1400, 4760];
const houseBFTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: houseBFCols, rows: [
    hRow(["House", "Classification", "Chakra", "Life Area", "Health Implications of Planets Here"], houseBFCols),
    dRow(["1st", "Benefic", "Root", "Body, identity, first impression", "Planets here directly affect the physical body and its vitality. Benefic planets strengthen constitution. Malefic planets create chronic physical patterns in the body itself."], houseBFCols, "FFF8F0"),
    dRow(["2nd", "Mixed (mildly malefic in some traditions)", "Sacral", "Resources, values, throat/neck", "Planets here affect metabolism, nutritional patterns, and throat/thyroid health. Overconsumption or scarcity patterns linked to self-worth show up here."], houseBFCols, "FFFFFF"),
    dRow(["3rd", "Mixed/Neutral", "Solar Plexus", "Communication, nervous system, lungs", "Planets here affect the respiratory system, nervous system, and communication-body connection. Anxiety patterns and nervous exhaustion often traced here."], houseBFCols, "FFF8F0"),
    dRow(["4th", "Benefic", "Heart", "Home, roots, stomach, emotional foundation", "Planets here affect emotional body, stomach health, and the foundational physical constitution inherited from family. Early childhood health patterns stored here."], houseBFCols, "FFFFFF"),
    dRow(["5th", "Benefic", "Throat", "Creativity, heart, spine", "Planets here affect heart health, spinal integrity, and the physical experience of joy and creative expression. Suppressed creativity can create physical tension here."], houseBFCols, "FFF8F0"),
    dRow(["6th", "Malefic (Dusthana)", "Third Eye", "Health, service, daily routines, digestion", "The primary health house. Planets here directly indicate areas of chronic health focus, daily health habits, and the specific digestive and intestinal patterns most relevant for this chart."], houseBFCols, "FFFFFF"),
    dRow(["7th", "Mixed", "Heart", "Partnerships, kidneys, skin", "Planets here affect kidney function, skin health, and how relationship stress manifests physically. Partnership dynamics create direct physical responses in the kidney/skin system."], houseBFCols, "FFF8F0"),
    dRow(["8th", "Malefic (Dusthana)", "Sacral", "Transformation, reproductive system, elimination", "Planets here affect reproductive health, elimination organs, and the body's capacity for cellular transformation. Chronic deep-level health patterns often have 8th house origins."], houseBFCols, "FFFFFF"),
    dRow(["9th", "Benefic", "Third Eye", "Philosophy, hips, liver, thighs", "Planets here affect liver function, hip health, and the sciatic nerve. Belief system disruptions create physical responses in these areas."], houseBFCols, "FFF8F0"),
    dRow(["10th", "Benefic", "Throat", "Career, knees, joints, bones", "Planets here affect skeletal health, particularly knees and load-bearing joints. Career stress manifests in the structural body. Public pressure creates skeletal holding patterns."], houseBFCols, "FFFFFF"),
    dRow(["11th", "Benefic", "Heart", "Community, ankles, circulation", "Planets here affect circulatory health, ankle stability, and how community belonging (or its absence) affects the cardiovascular system."], houseBFCols, "FFF8F0"),
    dRow(["12th", "Malefic (Dusthana)", "Crown", "Hidden, subconscious, immune, lymph", "The house of hidden health. Planets here govern immune function, lymphatic health, and conditions that are difficult to diagnose. Subconscious patterns manifest as physical symptoms here."], houseBFCols, "FFFFFF"),
]});

// ============================================================
// TABLE 3: CRITICAL DEGREE BODY STRESS
// ============================================================
const critCols = [900, 1200, 1600, 1800, 3860];
const critTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: critCols, rows: [
    hRow(["Degree", "Type", "Signs Affected", "Chakra", "Body Stress Pattern"], critCols, 'accent'),
    dRow(["0°", "Cardinal Critical / Pure", "Aries, Cancer, Libra, Capricorn", "Crown (Pure)", "Most intense expression of the sign's body area. 0° Aries: acute head/blood activation. 0° Cancer: intense stomach/fluid activation. 0° Libra: acute kidney/hormonal activation. 0° Capricorn: intense skeletal/joint activation. Any planet at 0° cardinal operates at full unfiltered intensity in its body area."], critCols, "FFF0F5"),
    dRow(["4°", "Mutable High Sensitivity", "Gemini, Virgo, Sagittarius, Pisces", "Third Eye", "Heightened nervous system and lymphatic sensitivity. 4° Gemini: acute lung/nerve sensitivity. 4° Virgo: intense digestive sensitivity. 4° Sagittarius: liver and hip sensitivity. 4° Pisces: immune and lymphatic hypersensitivity. Planets here are highly responsive to environmental and emotional triggers."], critCols, "FFFFFF"),
    dRow(["8°-9°", "Fixed Stubborn", "Taurus, Leo, Scorpio, Aquarius", "Solar Plexus", "Fixed energy creates stubborn, persistent physical patterns that resist easy resolution. 8°-9° Taurus: chronic throat/thyroid patterns. 8°-9° Leo: persistent heart/spine issues. 8°-9° Scorpio: stubborn reproductive/elimination patterns. 8°-9° Aquarius: chronic circulatory/neurological patterns."], critCols, "FFF0F5"),
    dRow(["13°", "Karmic (Aries series)", "All signs", "Solar Plexus", "13° carries karmic intensification energy. Planets here often indicate health patterns with a karmic or repeated-lesson quality. The body area governed by the sign holding 13° will demonstrate patterns that require conscious intervention rather than resolving naturally."], critCols, "FFFFFF"),
    dRow(["15°", "Midpoint / Sensitive", "Gemini specifically noted", "Throat", "15° Gemini is flagged as particularly sensitive in classical degree theory. Represents the midpoint of Gemini's lung/nervous system activation. Planets here in any sign represent midpoint culmination of that sign's body expression."], critCols, "FFF0F5"),
    dRow(["17°", "Mutable High Sensitivity", "Gemini, Virgo, Sagittarius, Pisces", "Third Eye", "Same body systems as 4° but at a later stage of the mutable cycle. More internalized sensitivity pattern. Often manifests as chronic low-level sensitivity rather than acute responses."], critCols, "FFFFFF"),
    dRow(["20°", "Scorpio Intensity", "Scorpio specifically noted", "Solar Plexus", "20° Scorpio carries intense Solar Plexus/reproductive activation. Planets here can indicate deep-seated patterns in elimination, reproductive health, or transformational health crises that carry emotional intensity."], critCols, "FFF0F5"),
    dRow(["21°-22°", "Fixed Stubborn", "Taurus, Leo, Scorpio, Aquarius", "Root / Sacral", "Second fixed critical window. Similar to 8°-9° but later in the fixed sign cycle. Often manifests as patterns that have become deeply entrenched over time. Requires sustained intervention rather than acute treatment."], critCols, "FFFFFF"),
    dRow(["22°", "Capricorn Malevolent", "Capricorn specifically noted", "Root", "22° Capricorn carries the classical designation of structural destruction energy. Planets here in Capricorn specifically indicate skeletal or structural health vulnerabilities that require proactive support rather than reactive treatment."], critCols, "FFF0F5"),
    dRow(["25°", "Aries series Karmic", "All signs", "Solar Plexus", "25° carries another karmic intensification layer. The body area governed by the sign holding 25° demonstrates patterns requiring power and authority reclamation for resolution. Power suppression creates physical patterns here."], critCols, "FFFFFF"),
    dRow(["29°", "Anaretic / Fated", "ALL signs", "Crown (Fated)", "The most significant critical degree. Any planet at 29° is at the completion and release point of that sign's energy. Carries intense karmic health implications. The body area governed by the sign holding 29° is under maximum pressure for transformation and completion. 29° is never neutral. It always demands resolution of the pattern it holds."], critCols, "FFF0F5"),
]});

// ============================================================
// TABLE 4: SIGN BODY PART MAPPING
// ============================================================
const signBodyCols = [1000, 1200, 1000, 1200, 5960];
const signBodyTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: signBodyCols, rows: [
    hRow(["Sign", "Chakra", "Modality/Element", "Primary Body Areas", "Detailed Body Parts and Health Systems"], signBodyCols),
    dRow(["Aries", "Solar Plexus", "Cardinal/Fire", "Head, blood", "Head, brain, face, eyes, arteries, hair, tongue, teeth. Governs adrenal function, blood pressure, and the inflammatory response. Aries rules the first spark of physical energy. Afflictions here create headaches, migraines, facial conditions, dental issues, anemia, or inflammatory disorders."], signBodyCols, "FFF8F0"),
    dRow(["Taurus", "Heart", "Fixed/Earth", "Throat, thyroid", "Throat, neck, thyroid gland, vocal cords, tonsils, sinuses, ears, cervical vertebrae. Governs metabolic rate through thyroid and the physical experience of values and self-worth in the body. Afflictions create thyroid dysregulation, throat conditions, neck tension, hearing issues, and weight patterns linked to self-worth."], signBodyCols, "FFFFFF"),
    dRow(["Gemini", "Throat", "Mutable/Air", "Lungs, shoulders, nervous system", "Lungs, shoulders, arms, hands, fingers, bronchial tubes, capillaries, nervous system. Governs respiration, neural pathways, and the communication-body interface. Afflictions create respiratory conditions, shoulder tension, carpal tunnel, anxiety, and nervous system dysregulation."], signBodyCols, "FFF8F0"),
    dRow(["Cancer", "Third Eye", "Cardinal/Water", "Stomach, breasts, lymph", "Chest, breasts, stomach, alimentary canal, diaphragm, womb, lymphatic system, right eye. Governs emotional digestion and fluid management. Afflictions create digestive issues, breast health concerns, fluid retention, emotional eating patterns, and immune/lymphatic congestion."], signBodyCols, "FFFFFF"),
    dRow(["Leo", "Third Eye", "Fixed/Fire", "Heart, spine", "Heart, spine, upper back, spinal column, blood circulation, blood pressure, left eye. Governs cardiac function and spinal integrity. Afflictions create heart conditions, upper back pain, blood pressure issues, and conditions linked to suppressed joy or creative expression."], signBodyCols, "FFF8F0"),
    dRow(["Virgo", "Throat", "Mutable/Earth", "Digestive system", "Abdomen, small intestines, bowels, digestive system, spleen, pancreas. Governs the body's ability to discriminate, process, and assimilate. Afflictions create IBS, digestive sensitivity, pancreatic stress, anxiety-digestion connection, and conditions linked to perfectionism and worry."], signBodyCols, "FFFFFF"),
    dRow(["Libra", "Heart", "Cardinal/Air", "Kidneys, skin", "Kidneys, lower back (lumbar region), buttocks, bladder, insulin regulation, veins, skin. Governs hormonal balance and the beauty/health connection. Afflictions create kidney strain, lower back pain, skin conditions, blood sugar dysregulation, and conditions linked to relationship imbalance."], signBodyCols, "FFF8F0"),
    dRow(["Scorpio", "Solar Plexus", "Fixed/Water", "Reproductive system", "Sexual organs, reproductive system, bowels, excretory system, prostate, rectum, pubic bone, urinary tract. Governs elimination and cellular transformation. Afflictions create reproductive conditions, elimination dysfunction, urinary issues, and conditions linked to suppressed transformation or power."], signBodyCols, "FFFFFF"),
    dRow(["Sagittarius", "Sacral", "Mutable/Fire", "Hips, liver", "Hips, thighs, liver, sciatic nerve, sacrum, lumbar vertebrae. Governs physical expansion and the liver's detoxification function. Afflictions create hip issues, sciatica, liver strain, and conditions linked to overexpansion or philosophical restlessness expressed physically."], signBodyCols, "FFF8F0"),
    dRow(["Capricorn", "Root", "Cardinal/Earth", "Joints, bones", "Knees, joints, bones, skeletal system, skin (structural layer), teeth, hair, ligaments, tendons. Governs structural integrity and karmic health patterns. Afflictions create joint inflammation, arthritis, dental issues, and chronic structural conditions requiring long-term management."], signBodyCols, "FFFFFF"),
    dRow(["Aquarius", "Root", "Fixed/Air", "Circulation, calves", "Ankles, calves, shins, forearms, blood circulation, veins, neurological system. Governs circulatory patterns and revolutionary health approaches. Afflictions create circulatory issues, varicose veins, ankle instability, and erratic neurological patterns."], signBodyCols, "FFF8F0"),
    dRow(["Pisces", "Sacral", "Mutable/Water", "Feet, lymphatic", "Feet, toes, lymphatic system, body fluids, pituitary gland (endorphins), pineal gland (melatonin). Governs spiritual immunity and psychic sensitivity in the physical body. Afflictions create foot conditions, immune dysregulation, lymphatic congestion, sleep disruption, and conditions linked to boundary dissolution."], signBodyCols, "FFFFFF"),
]});

// ============================================================
// TABLE 5: PLANET BODY PART MAPPING
// ============================================================
const planetBodyCols = [900, 900, 1200, 1400, 4960];
const planetBodyTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: planetBodyCols, rows: [
    hRow(["Planet", "Chakra", "Primary System", "Body Parts", "Health Influence and Pattern"], planetBodyCols),
    dRow(["Sun", "Third Eye", "Cardiovascular", "Heart, spine, right eye, vital force", "Governs overall vitality and the cardiac system. The Sun's aspects determine how well the vital force flows. Sun-Saturn aspects restrict vitality. Sun-Mars aspects inflame it. Sun-Neptune aspects dissolve it. The house the Sun occupies shows where vitality is most expressed and most vulnerable."], planetBodyCols, "FFF8F0"),
    dRow(["Moon", "Third Eye", "Digestive/Lymphatic", "Stomach, breasts, fluids, lymph, left eye", "Governs emotional digestion and fluid regulation. The Moon's phase and aspects indicate digestive health patterns. Moon-Saturn restricts fluid flow. Moon-Neptune increases fluid sensitivity. Moon-Mars inflames the digestive system. The house shows where emotional-physical connection is most active."], planetBodyCols, "FFFFFF"),
    dRow(["Mercury", "Throat", "Nervous System", "Lungs, nervous system, hands, arms, respiratory", "Governs neural pathways and the communication-body interface. Mercury-Saturn creates nervous tension and suppression. Mercury-Mars creates nervous inflammation and racing mind-body. Mercury-Neptune dissolves clear nervous signals. The house shows where nervous system patterns are most expressed."], planetBodyCols, "FFF8F0"),
    dRow(["Venus", "Heart", "Endocrine/Renal", "Kidneys, skin, throat (secondary), hormones", "Governs hormonal harmony and kidney function. Venus-Saturn restricts hormonal flow. Venus-Mars inflames skin and hormonal systems. Venus-Neptune dissolves healthy endocrine boundaries. The house shows where love and the body intersect most directly."], planetBodyCols, "FFFFFF"),
    dRow(["Mars", "Solar Plexus", "Muscular/Adrenal", "Muscles, adrenals, blood, inflammatory system", "Governs physical drive and the inflammatory response. The sign Mars occupies shows where inflammation most naturally concentrates. Mars aspects to outer planets determine whether the inflammatory force is channeled productively or destructively. Mars-Saturn creates suppressed inflammation that erupts. Mars-Pluto creates deep transformational inflammatory patterns."], planetBodyCols, "FFF8F0"),
    dRow(["Jupiter", "Sacral", "Hepatic/Lymphatic", "Liver, hips, thighs, arterial blood", "Governs liver expansion and the body's capacity for growth and abundance. Jupiter overcorrects: too much expansion in the body area it occupies. Jupiter in health houses creates a tendency to over-rely on natural recovery. The house shows where excess and expansion most manifest physically."], planetBodyCols, "FFFFFF"),
    dRow(["Saturn", "Root", "Skeletal/Adrenal", "Bones, joints, teeth, skin (deep layer), knees", "Governs structural integrity and karmic health patterns. Saturn restricts and crystallizes in the body area it occupies. Planets in hard aspect to Saturn show where restriction creates physical holding patterns. Saturn transits often correlate with bone, joint, and dental health events."], planetBodyCols, "FFF8F0"),
    dRow(["Uranus", "Third Eye", "Neurological", "Nervous system, ankles, electrical system of the body", "Governs sudden disruption and awakening in the body. Uranus creates unpredictable health events in the body area it occupies. Uranus transits often correlate with sudden onset conditions or sudden unexpected healings. The nervous system is always involved."], planetBodyCols, "FFFFFF"),
    dRow(["Neptune", "Crown", "Immune/Lymphatic", "Lymph, immune system, feet, pineal, psychic sensitivity", "Governs immune function and the dissolution of physical boundaries. Neptune in hard aspect creates mystery conditions, misdiagnosis patterns, and sensitivity to substances. Neptune transits often correlate with immune compromise periods. Spiritual alignment is immune support with Neptune activated."], planetBodyCols, "FFF8F0"),
    dRow(["Pluto", "Crown", "Eliminative/Reproductive", "Reproductive organs, elimination, cellular level, DNA", "Governs deep cellular transformation and elimination. Pluto in hard aspect creates obsessive health patterns, hidden conditions, and inherited health themes. Pluto transits often correlate with profound health transformations, including conditions that completely change how the person lives. Elimination organ health is always central."], planetBodyCols, "FFFFFF"),
    dRow(["Chiron", "Bridge", "Wound/Gift Interface", "Determined by house and sign placement", "The body area governed by Chiron's house and sign holds the primary wound-gift pattern. Chiron's aspects show which other body systems are recruited into the wound-gift integration process. Chiron transits activate healing crises that, when engaged, unlock profound healing capacity."], planetBodyCols, "FFF8F0"),
]});

// ============================================================
// TABLE 6: HOUSE BODY PART MAPPING
// ============================================================
const houseBodyCols = [700, 1000, 1200, 1400, 5060];
const houseBodyTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: houseBodyCols, rows: [
    hRow(["House", "Chakra", "Life Area", "Body Areas", "Health Pattern When Activated by Planets"], houseBodyCols),
    dRow(["1st", "Root", "Self, body, appearance", "Physical constitution, head, face, overall vitality", "Planets here directly affect physical constitution. The Rising sign colors the entire physical body. Malefics here create chronic constitutional patterns. Benefics strengthen overall health."], houseBodyCols, "FFF8F0"),
    dRow(["2nd", "Sacral", "Resources, values", "Throat, neck, thyroid, lower jaw, cervical spine", "Planets here affect metabolic health and throat/thyroid function. Financial stress and self-worth issues manifest physically in the throat and neck with planets here."], houseBodyCols, "FFFFFF"),
    dRow(["3rd", "Solar Plexus", "Communication, siblings", "Lungs, shoulders, arms, hands, nervous system", "Planets here affect respiratory health and nervous system function. Communication-suppression patterns create physical tension in shoulders and arms."], houseBodyCols, "FFF8F0"),
    dRow(["4th", "Heart", "Home, roots, mother", "Stomach, breasts, chest, emotional body foundation", "Planets here affect emotional digestion and stomach health. Early family patterns create lasting physical imprints in the chest and stomach area."], houseBodyCols, "FFFFFF"),
    dRow(["5th", "Throat", "Creativity, children, joy", "Heart, spine, upper back, blood", "Planets here affect cardiac health and spinal integrity. Suppressed creativity and joy create physical tension in the upper back and heart area."], houseBodyCols, "FFF8F0"),
    dRow(["6th", "Third Eye", "Health, service, routines", "Intestines, digestive system, spleen, pancreas", "The primary health house. Whatever planets occupy the 6th directly indicate the most relevant chronic health focus areas. Malefics here require the most conscious health management."], houseBodyCols, "FFFFFF"),
    dRow(["7th", "Heart", "Partnerships, contracts", "Kidneys, lower back, skin, lumbar spine", "Planets here affect kidney and skin health through the lens of relationship. Partnership stress and imbalance manifests physically in the lower back and kidneys."], houseBodyCols, "FFF8F0"),
    dRow(["8th", "Sacral", "Transformation, shared resources", "Reproductive system, elimination organs, rectum", "Planets here affect reproductive and elimination health. Deep transformation patterns, both psychological and physical, are stored here. Malefics here require deep-level health work."], houseBodyCols, "FFFFFF"),
    dRow(["9th", "Third Eye", "Philosophy, travel, higher learning", "Hips, thighs, liver, sciatic nerve", "Planets here affect hip and liver health through the lens of belief. Philosophical or spiritual crisis can create physical patterns in the hips and liver."], houseBodyCols, "FFF8F0"),
    dRow(["10th", "Throat", "Career, reputation, authority", "Knees, joints, bones, structural body", "Planets here affect skeletal health through career and public life pressure. Career stress and suppressed public authority manifest in joints and bones."], houseBodyCols, "FFFFFF"),
    dRow(["11th", "Heart", "Friends, community, hopes", "Ankles, calves, circulation, neurological", "Planets here affect circulatory health through community. Isolation or community disconnection creates circulatory and neurological patterns."], houseBodyCols, "FFF8F0"),
    dRow(["12th", "Crown", "Hidden, karma, subconscious", "Immune system, lymphatic, feet, psychic body", "The hidden health house. Planets here govern conditions that are difficult to diagnose, immune patterns, and the psychic-physical interface. Malefics here require the most attention to hidden health patterns."], houseBodyCols, "FFFFFF"),
]});

// ============================================================
// TABLE 7: ELEMENTAL BODY SYSTEM PATTERNS
// ============================================================
const elemCols = [900, 1100, 1200, 1500, 4660];
const elemTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: elemCols, rows: [
    hRow(["Element", "Signs", "Primary Body System", "TCM Correspondence", "Health Pattern Rules"], elemCols),
    dRow(["Fire", "Aries, Leo, Sagittarius", "Energy, cardiovascular, spine, adrenals", "Heart/Small Intestine (Fire element TCM), Liver fire (Mars)", "Charts dominant in Fire: high physical energy, inflammation tendency, adrenal activation patterns. Fire excess: hypertension, inflammatory conditions, adrenal fatigue from overactivation. Fire deficiency: low energy, poor circulation, depression. Fire-heavy charts need: cooling practices, anti-inflammatory support, regular rest between high-output periods."], elemCols, "FFF8F0"),
    dRow(["Earth", "Taurus, Virgo, Capricorn", "Structure, digestion, metabolism, skeletal", "Spleen/Stomach (Earth TCM), Kidney Jing (Saturn)", "Charts dominant in Earth: strong physical constitution, tendency toward digestive sensitivity and structural rigidity. Earth excess: weight gain, digestive sluggishness, over-accumulation patterns, stubborn physical conditions. Earth deficiency: poor nutrient absorption, weak constitution, structural fragility. Earth-heavy charts need: regular movement to prevent stagnation, digestive support, structural bodywork."], elemCols, "FFFFFF"),
    dRow(["Air", "Gemini, Libra, Aquarius", "Nervous system, respiration, circulation", "Lung/Large Intestine (Metal TCM), Triple Burner", "Charts dominant in Air: highly active nervous system, respiratory sensitivity, circulatory patterns. Air excess: anxiety, nervous exhaustion, racing mind-body patterns, hyperventilation tendency. Air deficiency: poor circulation, respiratory weakness, nervous system depletion. Air-heavy charts need: grounding practices, breathwork, nervous system regulation, circulatory support."], elemCols, "FFF8F0"),
    dRow(["Water", "Cancer, Scorpio, Pisces", "Fluids, lymph, elimination, immune, hormones", "Kidney/Bladder (Water TCM), Liver detox (Wood TCM)", "Charts dominant in Water: high emotional sensitivity, fluid retention tendency, immune responsiveness. Water excess: fluid retention, lymphatic congestion, hormonal flooding, immune overactivation. Water deficiency: dehydration patterns, immune weakness, emotional dryness. Water-heavy charts need: lymphatic support, hormonal balance practices, emotional processing protocols to prevent physical fluid stagnation."], elemCols, "FFFFFF"),
    dRow(["Wood (TCM only)", "Not an astrological element", "Liver/Gallbladder, tendons, eyes, emotional processing", "Liver/Gallbladder (Wood TCM)", "Wood does not exist as an astrological element. Its presence in a chart is determined by TCM body clock analysis and Sacral chakra activation patterns. Charts with high Wood meridian activation (indicated by strong Sacral activation across multiple placements) require: Liver support practices, emotional processing protocols, anger/frustration release work, and attention to the 1 to 3 AM Liver window. Wood imbalance: tendon issues, vision problems, anger/depression patterns, hormonal disruption."], elemCols, "FFF8F0"),
]});

// ============================================================
// TABLE 8: HOLISTIC SYMPTOM CROSS-REFERENCE LOGIC
// ============================================================
const sympCols = [1600, 1600, 1600, 4560];
const sympTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: sympCols, rows: [
    hRow(["If This Placement", "Combined With This", "Flag This Body Pattern", "Reading Language Framework"], sympCols, 'accent'),
    dRow(["Mars in a Fixed sign (Taurus, Leo, Scorpio, Aquarius)", "At 8°, 9°, 21°, or 22°", "Chronic stubborn inflammation in that sign's body area", "The inflammatory force of Mars is locked into a Fixed pattern at a critical degree. Taurus: chronic throat/thyroid inflammation. Leo: persistent cardiac or spinal inflammation. Scorpio: reproductive or elimination inflammation that resists treatment. Aquarius: circulatory or neurological inflammation."], sympCols, "FFF8F0"),
    dRow(["Saturn in the 6th house", "Especially with hard aspects to Mars", "Chronic health conditions requiring long-term management", "Saturn in the health house creates karmic health patterns that do not resolve quickly. The conditions here are the curriculum, not the punishment. Identifying and working WITH rather than against these patterns is the healing pathway."], sympCols, "FFFFFF"),
    dRow(["Neptune in the 6th or 12th house", "Especially conjunct or opposite personal planets", "Mystery conditions, misdiagnosis patterns, immune sensitivity", "Neptune in health houses creates conditions that are difficult to diagnose conventionally. The immune system and lymphatic system are the primary focus. Spiritual alignment is not optional for this health pattern. It is physiologically required."], sympCols, "FFF8F0"),
    dRow(["Moon square or opposite Saturn", "Tight orb (0-3°)", "Emotional suppression creating digestive and fluid restriction", "The emotional body and physical structure in friction. What is not felt creates physical restriction. Digestive issues, fluid imbalances, and lymphatic congestion are the most common physical expressions. Emotional processing practices are physical health practices for this aspect."], sympCols, "FFFFFF"),
    dRow(["Mercury opposition or square Saturn", "Any orb under 5°", "Nervous system tension from suppressed communication creating physical holding patterns", "Unsaid words become physical tension in the neck, jaw, and shoulders. Respiratory sensitivity from suppressed communication. Voice work, singing, and authentic expression are the primary physical healing modalities for this aspect pattern."], sympCols, "FFF8F0"),
    dRow(["Venus in hard aspect to Mars", "Square or opposition", "Hormonal and inflammatory interaction, skin-adrenal connection", "The love and drive systems in friction. Hormonal patterns linked to relationship dynamics. Skin conditions and adrenal patterns that flare with relationship stress. Physical health improves when the love-drive tension is resolved rather than suppressed."], sympCols, "FFFFFF"),
    dRow(["Pluto in the 6th or 8th house", "With hard aspects to personal planets", "Deep cellular health patterns, inherited conditions, transformational health crises", "Pluto in health houses indicates health patterns that require deep transformation rather than surface treatment. Inherited conditions from the ancestral line are most relevant. The health journey IS the transformational curriculum."], sympCols, "FFF8F0"),
    dRow(["Multiple planets in a single sign", "Especially in the 6th house", "Concentrated body system vulnerability in that sign's area", "A stellium concentrates planetary force in one sign's body area. The body system governed by that sign is both the primary strength AND the primary vulnerability. Both the wound and the gift of health live in the same anatomical location."], sympCols, "FFFFFF"),
    dRow(["Chiron conjunct a personal planet (0-3°)", "Especially Venus, Mars, or Moon", "The wound-gift bridge directly activating that planet's body system", "When Chiron fuses with a personal planet at tight orb, the wound-gift pattern IS that planet's body system. Venus-Chiron: hormonal and kidney wound-gift. Mars-Chiron: inflammatory and muscular wound-gift. Moon-Chiron: emotional-digestive wound-gift. The healing of the wound and the expression of the gift occur in the same physical system."], sympCols, "FFF8F0"),
    dRow(["Uranus conjunct or opposite a health planet", "In tight orb", "Sudden onset patterns, erratic symptoms, unexpected health events", "Uranus adds unpredictability and electrical disruption to whatever it touches. Health patterns with Uranus involved do not follow conventional progression timelines. They arrive suddenly and respond to approaches that conventional medicine does not expect."], sympCols, "FFFFFF"),
    dRow(["North Node in the 6th house", "Or aspecting health planets", "Soul destiny expressed through health and healing work", "The evolutionary path moves through health. The person either heals themselves as their destiny work or heals others as their vocation, or both. Resisting the health journey slows the soul's evolution and the immune system registers the resistance."], sympCols, "FFF8F0"),
    dRow(["Anaretic degree (29°) on a health-relevant planet", "Any health house placement", "Karmic completion of that body system's health pattern", "A planet at 29° in a health house or health sign is at the completion point of a cycle. The health pattern it governs is ready for final resolution in this lifetime. Engaging the pattern consciously accelerates its completion. Avoiding it intensifies the urgency of resolution."], sympCols, "FFFFFF"),
    dRow(["Sun or Moon in the 12th house", "Especially with Neptune aspects", "Hidden vitality or emotional patterns, immune sensitivity from subconscious", "The life force (Sun) or emotional body (Moon) operating from the hidden house creates physical patterns that are difficult to trace to their source. Immune health is the primary physical expression. Subconscious processing work is required alongside physical treatment."], sympCols, "FFF8F0"),
    dRow(["Mars in the 12th house", "Any aspect", "Suppressed inflammatory force creating hidden chronic conditions", "Mars in the hidden house means the inflammatory force operates beneath conscious awareness. The person may not recognize when they are physically activated or inflamed. Chronic conditions that have been present so long they feel normal are most common. Bringing the inflammation to conscious awareness is the first healing step."], sympCols, "FFFFFF"),
]});

// ============================================================
// TABLE 9: RETROGRADE HEALTH IMPLICATIONS
// ============================================================
const rxCols = [1000, 1200, 7160];
const rxTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: rxCols, rows: [
    hRow(["Planet Rx", "Chakra", "Health Implications of Retrograde Motion"], rxCols),
    dRow(["Mercury Rx", "Throat", "When Mercury is retrograde in the natal chart, the nervous system and communication-body interface operates in an internalized, non-linear way. Physical symptoms from suppressed communication are more likely. The body registers what the mind cannot easily externalize. Voice work and journaling are particularly effective healing modalities."], rxCols, "FFF8F0"),
    dRow(["Venus Rx", "Heart", "Natal Venus Rx indicates internalized values around love and self-worth that affect hormonal and kidney health from the inside out. The body's love-health connection operates in a more private, less externally expressed way. Self-love practices must be genuinely internal rather than performative to affect physical health."], rxCols, "FFFFFF"),
    dRow(["Mars Rx", "Solar Plexus", "Natal Mars Rx indicates internalized drive and inflammation that may not be visible externally but creates significant internal physical patterns. The inflammatory force turns inward. Autoimmune tendencies and internal inflammatory conditions are more common. Physical output may be inconsistent or cyclic rather than sustained."], rxCols, "FFF8F0"),
    dRow(["Jupiter Rx", "Sacral", "Natal Jupiter Rx indicates internalized expansion and a more private relationship with abundance and liver health. The liver's detoxification capacity may be less robust externally but more thorough internally. Overconsumption patterns are less likely but under-expansion of healing capacity is more common. Trust in natural healing may require more internal cultivation."], rxCols, "FFFFFF"),
    dRow(["Saturn Rx", "Root", "Natal Saturn Rx indicates internalized restriction and a karmic health curriculum that operates more privately than outwardly. Skeletal and structural patterns are felt internally before they manifest visibly. The discipline required for health is self-imposed rather than externally motivated. Self-accountability in health practices is the primary healing mechanism."], rxCols, "FFF8F0"),
    dRow(["Uranus Rx", "Third Eye", "Natal Uranus Rx indicates internalized awakening and nervous system disruption that operates more subtly than direct Uranus. Health disruptions may be internal and harder to trace. The neurological awakening is inward first, outward second. Sudden health events may have a longer internal buildup that was not externally visible."], rxCols, "FFFFFF"),
    dRow(["Neptune Rx", "Crown", "Natal Neptune Rx indicates internalized spiritual immunity and a more private relationship with dissolution and psychic sensitivity. Immune patterns are more internally generated than environmentally triggered. Spiritual work for immune health must be genuinely internal rather than externally performed. The boundary dissolution of Neptune Rx is often unconscious."], rxCols, "FFF8F0"),
    dRow(["Pluto Rx", "Crown", "Natal Pluto Rx indicates internalized transformation and elimination patterns that operate below conscious awareness. Deep cellular health patterns may be hereditary and operate without the person's full conscious recognition. The transformational health work required is inward and often requires assistance (therapy, bodywork, deep healing modalities) to access what Pluto Rx keeps below the surface."], rxCols, "FFFFFF"),
    dRow(["North Node Rx", "Third Eye", "North Node is almost always retrograde. Natal North Node Rx reinforces the inward quality of the soul's evolutionary path. The immune-soul alignment connection of the North Node is felt as an internal compass. Physical health responds to internal soul alignment work more than external life changes."], rxCols, "FFF8F0"),
]});

// ============================================================
// TABLE 10: TCM BODY CLOCK FULL REFERENCE FOR READING GENERATION
// ============================================================
const clockCols = [1100, 1000, 1000, 1000, 5260];
const clockTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: clockCols, rows: [
    hRow(["Window", "Organ", "Element/Chakra", "Astrological Ruler", "Reading Application: If Planet X Governs This System"], clockCols),
    dRow(["11 PM - 1 AM", "Gallbladder", "Wood/Sacral", "Jupiter (expansion of Wood)", "If Jupiter, Uranus, Neptune, or Sacral-dominant planets are prominent: this window is for decision-making courage and creative processing. Disrupted sleep here = Gallbladder processing incomplete = expansion and courage depleted."], clockCols, "FFF8F0"),
    dRow(["1 AM - 3 AM", "Liver", "Wood/Sacral", "Jupiter, Mars (Liver fire)", "If Mars, Jupiter, or multiple Sacral activations: this is the primary emotional processing and detox window. Waking here = emotional or inflammatory backlog from the day. Protocol: emotional release before midnight."], clockCols, "FFFFFF"),
    dRow(["3 AM - 5 AM", "Lung", "Metal/Throat", "Mercury, Saturn (grief in Lung)", "If Mercury, Saturn, or Throat-dominant placements: this is the grief and release window. Waking here = unexpressed grief, suppressed communication, or letting-go resistance. Protocol: morning breathwork and voice activation."], clockCols, "FFF8F0"),
    dRow(["5 AM - 7 AM", "Large Intestine", "Metal/Throat", "Mercury (elimination of what no longer serves)", "If Mercury or multiple Throat activations: this is the elimination and release window for body and communication. Morning bowel health directly linked to Throat chakra expression the day before."], clockCols, "FFFFFF"),
    dRow(["7 AM - 9 AM", "Stomach", "Earth/Solar Plexus", "Sun, Mars (digestive fire)", "If Sun, Mars, or Solar Plexus-dominant placements: this is the optimal nourishment window. The Solar Plexus power point receives its morning charge here. Skipping breakfast with these activations depletes the power center."], clockCols, "FFF8F0"),
    dRow(["9 AM - 11 AM", "Spleen", "Earth/Solar Plexus", "Saturn (structural digestion)", "If Saturn or multiple Earth/Solar Plexus activations: this is the intellectual and physical transformation window. The body converts yesterday's input into today's energy. Career and power work are most supported here."], clockCols, "FFFFFF"),
    dRow(["11 AM - 1 PM", "Heart", "Fire/Heart", "Sun, Venus (Shen/spirit)", "If Sun, Venus, Moon, or Heart-dominant placements: this is the peak Heart meridian window. Love-based work, connection, and heart-centered decisions are most available. The Shen (spirit of the heart) is most accessible."], clockCols, "FFF8F0"),
    dRow(["1 PM - 3 PM", "Small Intestine", "Fire/Heart", "Mercury (discernment)", "If Mercury or Heart-dominant placements: this is the discernment and assimilation window. The afternoon sorting function: what nourishes and what needs to be released. Physical movement here supports Mars-Mercury aspect patterns."], clockCols, "FFFFFF"),
    dRow(["3 PM - 5 PM", "Bladder", "Water/Root", "Saturn, Moon (fluid purification)", "If Saturn, Moon, or Root-dominant placements: this is the fluid purification window. Kidney Jing restoration begins here. Overworking in this window depletes foundational reserves. Rest and hydration are the physical support."], clockCols, "FFF8F0"),
    dRow(["5 PM - 7 PM", "Kidney", "Water/Root", "Saturn (Jing essence)", "If Saturn, Moon, or multiple Root activations: this is the vital essence restoration window. The most important replenishment window of the day. Evening plans that drain this window create foundational depletion over time."], clockCols, "FFFFFF"),
    dRow(["7 PM - 9 PM", "Pericardium", "Fire/Third Eye", "Venus (heart protection)", "If Venus, Moon, or Heart-adjacent placements: this is the emotional boundary and intimacy window. Who has access to your energy in this window matters physiologically. The Pericardium protects the Shen."], clockCols, "FFF8F0"),
    dRow(["9 PM - 11 PM", "Triple Burner", "Fire/Third Eye", "Uranus, Neptune (energetic regulation)", "If Uranus, Neptune, or Crown/Third Eye-dominant placements: this is the Qi harmonization and spiritual preparation window. Screens and external stimulation in this window disrupt the Triple Burner's regulatory function. Spiritual practice here directly supports immune health."], clockCols, "FFFFFF"),
]});

// ============================================================
// READING GENERATION RULES
// ============================================================
const rulesCols = [2400, 6960];
const rulesTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: rulesCols, rows: [
    hRow(["Rule", "Application"], rulesCols),
    dRow(["Priority Hierarchy", "1. Tight orb aspects (0-2°) to health planets are ALWAYS mentioned first. They are always active. 2. Planets in the 6th house are primary health indicators regardless of aspect. 3. Critical degree placements (0°, 8°-9°, 21°-22°, 29°) are flagged before standard degree placements. 4. Malefic planets (Mars, Saturn) in health houses (6th, 8th, 12th) receive specific attention. 5. The Chiron Planetary Bridge is always included as its own section."], rulesCols, "FFF8F0"),
    dRow(["Retrograde Protocol", "All retrograde planets receive the Rx modifier in their reading language. The internalization quality of retrograde is always noted. Retrograde malefics create more hidden patterns requiring more self-awareness. Retrograde benefics create more private healing capacities."], rulesCols, "FFFFFF"),
    dRow(["Benefic/Malefic Qualification", "Never present malefic placements as purely negative. Mars afflicted = inflammatory curriculum requiring conscious engagement. Saturn afflicted = structural lesson requiring long-term commitment. Neptune afflicted = immune sensitivity requiring spiritual alignment. Every malefic pattern has a direct healing pathway."], rulesCols, "FFF8F0"),
    dRow(["Body Clock Integration", "Every health pattern identified must include the primary TCM body clock window where that pattern is most active and most available for support. The window is not optional in the reading. It is the practical application layer that makes the reading actionable."], rulesCols, "FFFFFF"),
    dRow(["Language Standards", "Never use the words 'disorder', 'condition', 'diagnosis', or 'disease' in the reading output. Use: 'pattern', 'activation', 'health curriculum', 'physical expression', 'body signal'. Never diagnose. Never prescribe. Always frame as: here is what the chart indicates, here is where to look, here is the support pathway."], rulesCols, "FFF8F0"),
    dRow(["Chakra-Meridian Bridge", "Every body system identification must include both its chakra designation AND its TCM meridian. The two systems must be named together. Example: 'the Throat chakra activation of Mercury, governed by the Lung and Large Intestine meridians' not just 'Mercury in Throat'."], rulesCols, "FFFFFF"),
    dRow(["Elemental Integration", "When multiple planets share an element, identify the elemental pattern explicitly. 'Your chart carries a [element] dominant pattern, which concentrates [body system] activation across [list planets]. The primary health consideration for this elemental concentration is [TCM pattern].'"], rulesCols, "FFF8F0"),
    dRow(["Symptom Cross-Reference", "When a symptom pattern from Table 8 is triggered by the chart, lead with the pattern identification, follow with the specific body system, then provide the body clock support window. Never speculate beyond what the chart confirms. If a pattern is not confirmed by at least two independent chart factors, do not include it."], rulesCols, "FFFFFF"),
]});

const doc = new Document({
    numbering: { config: [] },
    styles: { default: { document: { run: { font: "Arial", size: 22 } } } },
    sections: [{
        properties: { page: { size: { width: 15840, height: 12240 }, margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 }, orientation: "landscape" } },
        children: [
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
                children: [new TextRun({ text: "TCM ASTROLOGY CHAKRA SYSTEM", bold: true, size: 48, color: "2D0A3E", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
                children: [new TextRun({ text: "Tier 2 Deep Dive — Backend Reference System", bold: true, size: 32, color: "6B1E7A", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
                children: [new TextRun({ text: "Reading Generation Framework | Practitioner and AI Reference Only", italics: true, size: 24, color: "C2185B", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 300 },
                children: [new TextRun({ text: "Phoenix Rebirth | Aurelia Reign | April 2026 | Version 1.0 | PROPRIETARY — NOT FOR CLIENT DISTRIBUTION", size: 20, color: "999999", font: "Arial" })] }),
            divider(),
            note("This document is the backend engine for generating TCM Astrology Chakra Tier 2 Deep Dive readings. It is not shown to clients. It is the lookup reference that the reading generator uses to identify health patterns, body system activations, and healing pathways for any natal chart run through the system. All language rules, priority hierarchies, and cross-reference logic are contained here."),
            spacer(),

            h1("SECTION 1: Benefic and Malefic Planet Framework"),
            note("Benefic planets support the body systems they govern. Malefic planets create tension, restriction, or excess in those systems. The classification is not fixed. Context, aspects, and chart dignity all modify the expression. No placement is purely negative. Every pattern has a healing pathway."),
            spacer(),
            beneficTable,
            pageBreak(),

            h1("SECTION 2: Benefic and Malefic House Framework"),
            note("The 6th, 8th, and 12th houses are the Dusthana (malefic) houses in Vedic tradition. Planets here require the most conscious health management. The 1st, 4th, 5th, 9th, 10th, and 11th are benefic houses. The 2nd, 3rd, and 7th are mixed. Every house carries its chakra assignment and corresponding body area regardless of whether a planet occupies it."),
            spacer(),
            houseBFTable,
            pageBreak(),

            h1("SECTION 3: Critical Degree Body Stress Reference"),
            note("Critical degrees intensify the physical expression of any planet or point that occupies them. They do not create conditions independently. They amplify the pattern of the planet or sign they occupy. A planet at a critical degree in a health house or health sign receives priority mention in the Tier 2 reading."),
            spacer(),
            critTable,
            pageBreak(),

            h1("SECTION 4: Sign Body Part Mapping Reference"),
            note("Each zodiac sign governs specific body areas. When a sign occupies a house, is occupied by a planet, or is activated by a transit or progression, the body areas it governs become relevant to the health reading. Multiple planets in the same sign concentrate activation in those body areas."),
            spacer(),
            signBodyTable,
            pageBreak(),

            h1("SECTION 5: Planet Body Part Mapping Reference"),
            note("Each planet governs specific body systems. The planet's placement by sign and house determines WHERE in the body its influence concentrates. Aspects to the planet determine HOW that body system is activated (harmoniously, under stress, with sudden disruption, etc.)."),
            spacer(),
            planetBodyTable,
            pageBreak(),

            h1("SECTION 6: House Body Part Mapping Reference"),
            note("Each house governs specific body areas through both its inherent nature and the sign that occupies it. The house body area is activated whenever a planet transits the house, a planet natally occupies it, or it is activated by progression."),
            spacer(),
            houseBodyTable,
            pageBreak(),

            h1("SECTION 7: Elemental Body System Patterns"),
            note("The astrological elements determine the fundamental physical constitution pattern. A chart dominant in one element shows concentrated activation and vulnerability in that element's body system. TCM Wood is included as a fifth element because it governs the most common meridian pattern that astrological analysis alone cannot fully capture."),
            spacer(),
            elemTable,
            pageBreak(),

            h1("SECTION 8: Holistic Symptom Cross-Reference Logic"),
            note("These are the conditional health pattern rules. When a chart contains both factors in the first two columns simultaneously, flag the body pattern in column three and apply the reading language framework in column four. Two independent chart confirmations are required before including a pattern in the reading."),
            spacer(),
            sympTable,
            pageBreak(),

            h1("SECTION 9: Retrograde Planet Health Implications"),
            note("Retrograde planets internalize their function. In health readings, retrograde planets create more hidden, internally-generated patterns that require more self-awareness to identify and address. The body system governed by a retrograde planet operates inwardly before it manifests outwardly."),
            spacer(),
            rxTable,
            pageBreak(),

            h1("SECTION 10: TCM Body Clock Reading Application Reference"),
            note("Every health pattern identified in a Tier 2 reading must include the TCM body clock window where that pattern is most active. This table maps astrological rulers to their corresponding body clock windows and provides the reading application language for each window."),
            spacer(),
            clockTable,
            pageBreak(),

            h1("SECTION 11: Reading Generation Rules and Standards"),
            note("These are the non-negotiable rules for generating Tier 2 readings from this system. All rules must be applied to every reading generated. No exceptions."),
            spacer(),
            rulesTable,
            spacer(),
            divider(),

            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 100 },
                children: [new TextRun({ text: "TCM Astrology Chakra System | Tier 2 Deep Dive Backend Reference", italics: true, size: 20, color: "2D0A3E", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
                children: [new TextRun({ text: "Proprietary system created by Christina Stevens / Aurelia Reign. Phoenix Rebirth. April 2026. All rights reserved.", italics: true, size: 18, color: "999999", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0 },
                children: [new TextRun({ text: "This backend reference document is for practitioner and AI reading generation use only. It is not distributed to clients under any circumstances.", italics: true, size: 18, color: "C2185B", font: "Arial" })] }),
        ]
    }]
});

Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync("/mnt/user-data/outputs/TCM_Tier2_Backend_Reference.docx", buffer);
    console.log("Done");
});