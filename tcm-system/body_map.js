const fs = require('fs');

const {
    Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
    HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType, PageBreak
} = require('docx');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const hBorder = { style: BorderStyle.SINGLE, size: 1, color: "2D0A3E" };
const hBorders = { top: hBorder, bottom: hBorder, left: hBorder, right: hBorder };

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
function bodyBold(runs) {
    return new Paragraph({ spacing: { before: 80, after: 80 },
        children: runs.map(r => new TextRun({ text: r.text, size: 22, font: "Arial", bold: r.bold || false, color: r.color || "000000" })) });
}
function note(text) {
    return new Paragraph({ spacing: { before: 80, after: 80 },
        children: [new TextRun({ text, size: 20, italics: true, color: "555555", font: "Arial" })] });
}
function disclaimer(text) {
    return new Paragraph({ spacing: { before: 80, after: 80 },
        children: [new TextRun({ text, size: 20, italics: true, color: "CC2244", font: "Arial" })] });
}
function divider() {
    return new Paragraph({
        spacing: { before: 200, after: 200 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "6B1E7A", space: 1 } },
        children: [new TextRun("")] });
}
function spacer() {
    return new Paragraph({ spacing: { before: 80, after: 80 }, children: [new TextRun("")] }); }

function hRow(cells, cols) {
    return new TableRow({ tableHeader: true, children: cells.map((text, i) => new TableCell({
        borders: hBorders,
        width: { size: cols[i], type: WidthType.DXA },
        shading: { fill: "2D0A3E", type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({ children: [new TextRun({ text, bold: true, size: 20, color: "FFFFFF", font: "Arial" })] })]
    }))});
}
function dRow(cells, cols, shade) {
    return new TableRow({ children: cells.map((text, i) => new TableCell({
        borders, width: { size: cols[i], type: WidthType.DXA },
        shading: { fill: shade || "FFFFFF", type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 150, right: 150 },
        children: [new Paragraph({ children: [new TextRun({ text, size: 20, font: "Arial" })] })]
    }))});
}

const CW = 9360;

// COMPARISON TABLE
const compCols = [1600, 2200, 2200, 3360];
const compTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: compCols, rows: [
    hRow(["Aspect", "Western/Ayurvedic", "Traditional Chinese Medicine", "Christina Stevens Body Map"], compCols),
    dRow(["Body Right Side", "Masculine, Solar, Giving", "Yin (Feminine, Receiving)", "Masculine, Giving (body level). Receiving/downloading at head level."], compCols, "F9F0FF"),
    dRow(["Body Left Side", "Feminine, Lunar, Receiving", "Yang (Masculine, Giving)", "Feminine, Receiving (body level). Releasing at head level."], compCols, "FFFFFF"),
    dRow(["Head Right Side", "Not specifically addressed", "Not specifically addressed", "ORIGINAL: Downloading side. Energy enters the body through the right base of skull. Spiritual downloads, energetic upgrades, and incoming information arrive here."], compCols, "F9F0FF"),
    dRow(["Head Left Side", "Not specifically addressed", "Not specifically addressed", "ORIGINAL: Releasing side. Energy exits the body through the left side of the head. Less intense activation than the right side because energy is leaving rather than arriving."], compCols, "FFFFFF"),
    dRow(["Axis / Reversal Point", "Not addressed", "Not addressed", "ORIGINAL: The cervical spine / neck junction is where the body's energy directionality reverses. Below the cervical junction the right side is masculine/giving and left is feminine/receiving. Above it, the directions invert."], compCols, "F9F0FF"),
    dRow(["Central Axis", "Heart as love center but not specifically an energy crossing point", "Heart as Shen/spirit center", "ORIGINAL: The heart is the double crossing point of the infinity figure. Energy crosses through the heart axis twice in a single circuit, once ascending and once descending."], compCols, "FFFFFF"),
    dRow(["Hands", "Right hand gives, left hand receives in some healing traditions", "Not specifically addressed in this way", "Aligned with Christina Stevens framework: left hand receives energy, right hand gives energy. This is the entry and exit point of the infinity circuit."], compCols, "F9F0FF"),
    dRow(["Energy Flow Pattern", "Not mapped as a continuous circuit", "Meridian circuits but not an infinity figure", "ORIGINAL: A standing infinity figure (figure-8) with the heart as the double axis crossing point, the cervical spine as the directional reversal point, left hand as entry and right hand as exit."], compCols, "FFFFFF"),
]});

// FLOW DESCRIPTION TABLE
const flowCols = [1200, 2000, 6160];
const flowTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: flowCols, rows: [
    hRow(["Stage", "Location", "Description"], flowCols),
    dRow(["1 — Entry", "Left Hand", "Energy enters the physical field through the left hand. The left hand is the receiving hand. Feminine. Receptive. Open. This is the first point of contact between the external energy field and the physical body."], flowCols, "F9F0FF"),
    dRow(["2 — Ascent", "Left Arm, Left Side of Body", "Energy flows upward and inward at an angle through the left side of the body toward the heart."], flowCols, "FFFFFF"),
    dRow(["3 — First Heart Crossing", "Heart Axis Point", "Energy crosses through the heart axis for the first time on its ascent. The heart is the central crossing point of the entire circuit. The Shen (spirit of the heart in TCM) is active at this crossing."], flowCols, "F9F0FF"),
    dRow(["4 — Ascent to Cervical", "Right Side of Cervical Spine / Neck", "After crossing the heart, energy wraps upward along the right side of the cervical spine. This is where the directional reversal occurs. The energy is now moving on the right side of the body heading toward the head."], flowCols, "FFFFFF"),
    dRow(["5 — Head Crossing", "Right Base of Skull to Left Side of Head", "Energy rounds over the top of the head from the right base of skull (downloading point, where spiritual downloads and energetic upgrades arrive) to the left side of the head (releasing point, where energy exits the head field)."], flowCols, "F9F0FF"),
    dRow(["6 — Descent", "Left Side of Head, Forward and Down", "Energy moves forward and downward from the left side of the head at an angle, heading back toward the heart axis."], flowCols, "FFFFFF"),
    dRow(["7 — Second Heart Crossing", "Heart Axis Point", "Energy crosses through the heart axis for the second time on its descent. This is what makes the heart the double axis point and what creates the figure-8 / infinity shape of the circuit."], flowCols, "F9F0FF"),
    dRow(["8 — Descent to Exit", "Right Side of Body, Right Arm", "After the second heart crossing, energy descends along the right side of the body toward the right hand."], flowCols, "FFFFFF"),
    dRow(["9 — Exit", "Right Hand", "Energy exits the physical field through the right hand. The right hand is the giving hand. Masculine. Active. Extending. This is where the energy completes its journey through the body and moves back into the external field."], flowCols, "F9F0FF"),
    dRow(["10 — The Connector", "Right Hand to Left Hand through Active Exchange", "The circuit closes through whatever is being interacted with in the moment of exchange, whether a person, a plant, an object, a spiritual presence, or an energetic frequency. The interaction itself becomes the connector between the right hand's exit and the left hand's entry. The circuit completes for the duration of the exchange and returns to an open path when the exchange completes. This means the infinity figure is not a perpetual closed loop. It is a living circuit that closes in relationship and through active exchange. The body is an open path between exchanges and a completed circuit during them. This closing mechanism was confirmed through direct somatic knowing by Christina Stevens in April 2026, completing six years of framework development."], flowCols, "FFFFFF"),
]});

// SOMATIC EVIDENCE TABLE
const evCols = [2000, 7360];
const evTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: evCols, rows: [
    hRow(["Observation", "Description and Significance"], evCols),
    dRow(["Right Base of Skull Migraines", "Christina Stevens experiences her most intense migraines at the base of the skull on the right side. These migraines correlate with periods of spiritual download, energetic upgrade, and incoming higher-frequency information. The intensity is significantly greater than left-side head pain, which she experiences as milder and associated with energy leaving the field. This direct somatic experience is the primary source of the head directionality framework."], evCols, "F9F0FF"),
    dRow(["Left vs Right Head Pain Intensity Differential", "The observable difference in intensity between right-side and left-side head pain is the somatic confirmation of the directional difference. If the directions were symmetrical, the intensity would be symmetrical. The asymmetry of experience confirms the asymmetry of function."], evCols, "FFFFFF"),
    dRow(["Heart as Crossing Point", "The felt sense of the heart as an axis point rather than simply an energy center is consistent with the TCM designation of the heart as the Shen seat and with the anatomical reality that the heart is the central crossing point of the body's circulatory system. Christina's framework adds the specific infinity-figure crossing geometry to this established understanding."], evCols, "F9F0FF"),
    dRow(["Cervical Spine as Reversal Point", "The cervical spine as the point where body directionality reverses is consistent with the neurological reality that the cervical spine is where the brain stem transitions to the spinal cord, where the central nervous system's descending and ascending pathways cross, and where multiple TCM meridians change direction. The anatomical support for a directional shift at this junction is substantial, though this specific energy directionality interpretation is Christina's original observation."], evCols, "FFFFFF"),
    dRow(["November 2007 Confirmation", "The 2007 car accident in which Christina's right pelvis, right knee, right shin, and right ankle were injured while transiting Mars was stationing retrograde in Gemini during her 1st house Aquarius Annual Profection year provides indirect support for the right-side masculine/giving framework. The right side of the body took the entire physical cost of a soul misalignment decision. Whether this is coincidence, confirmation, or something else entirely is not asserted. It is documented as a data point."], evCols, "F9F0FF"),
]});

// PARTIAL TRADITION ALIGNMENT TABLE
const tradCols = [2400, 6960];
const tradTable = new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: tradCols, rows: [
    hRow(["Tradition", "Where It Aligns and Where It Differs"], tradCols),
    dRow(["Western Energy Healing / Ayurveda", "ALIGNS: Right side masculine/solar/giving, left side feminine/lunar/receiving for the body. DIFFERS: Christina's framework adds the cervical reversal point and the specific head directionality, which neither tradition addresses."], tradCols, "F9F0FF"),
    dRow(["Traditional Chinese Medicine", "PARTIAL ALIGNMENT: Heart as Shen center and double crossing point has resonance with TCM's understanding of the heart as the emperor organ and seat of spirit. DIFFERS: TCM assigns Yin to right and Yang to left, which is opposite to Christina's body framework. The cervical reversal and head directionality are not addressed in TCM."], tradCols, "FFFFFF"),
    dRow(["Healing Touch / Reiki", "ALIGNS: Left hand receives, right hand gives is a recognized principle in several hands-on healing traditions including some schools of Reiki and Healing Touch. DIFFERS: The specific infinity circuit flow and cervical reversal are not part of these traditions."], tradCols, "F9F0FF"),
    dRow(["Neuroscience", "PARTIAL SUPPORT: The cervical spine as a neurological transition point where central nervous system pathways change direction has anatomical basis. The brain's hemispheric lateralization creates genuine functional asymmetry. The specific energy directionality interpretation is not neuroscience but the anatomical basis for a reversal point at the cervical junction is real."], tradCols, "FFFFFF"),
    dRow(["Vedic / Kundalini", "PARTIAL RESONANCE: Kundalini energy rising through the central column with energy entering through the base and exiting through the crown has some resonance with the ascending component of Christina's framework. The specific left-right directionality and the infinity figure geometry are distinct from Kundalini models."], tradCols, "F9F0FF"),
]});

const doc = new Document({
    numbering: { config: [] },
    styles: { default: { document: { run: { font: "Arial", size: 22 } } } },
    sections: [{
        properties: { page: { margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } } },
        children: [
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
                children: [new TextRun({ text: "THE CHRISTINA STEVENS BODY MAP", bold: true, size: 48, color: "2D0A3E", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
                children: [new TextRun({ text: "A Proprietary Energy Directionality Framework", bold: true, size: 32, color: "6B1E7A", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
                children: [new TextRun({ text: "Original Framework | Phoenix Rebirth | Christina Stevens", italics: true, size: 24, color: "C2185B", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 300 },
                children: [new TextRun({ text: "Version 1.0 | April 2026 | Framework Complete", size: 20, color: "999999", font: "Arial" })] }),
            divider(),

            new Paragraph({ spacing: { before: 0, after: 200 },
                shading: { fill: "FFF0F0", type: ShadingType.CLEAR },
                border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CC2244" }, bottom: { style: BorderStyle.SINGLE, size: 4, color: "CC2244" }, left: { style: BorderStyle.SINGLE, size: 4, color: "CC2244" }, right: { style: BorderStyle.SINGLE, size: 4, color: "CC2244" } },
                children: [new TextRun({ text: "FRAMEWORK STATUS DECLARATION", bold: true, size: 22, color: "CC2244", font: "Arial" })] }),
            disclaimer("This document describes a proprietary original framework created by Christina Stevens based on her direct somatic and spiritual experience. It is not peer-reviewed. It is not clinically validated. It has not been tested across a population. It is documented here as Christina Stevens' original observational framework, clearly designated as a work in development. Where it aligns with existing traditions, that alignment is noted. Where it diverges from or adds to existing traditions, that divergence is clearly identified. No claims are made that this framework applies universally to all bodies. It is presented as Christina Stevens' truth about her own somatic experience and as a framework she is developing from that truth. When and if it is applied to other people's bodies, it must be presented as such."),
            spacer(),

            h1("PART 1: What This Framework Is and Is Not"),
            body("The Christina Stevens Body Map is an energy directionality framework describing how Christina Stevens directly experiences energy moving through the human body. It is based on years of personal somatic observation, most notably her experience of intense migraines at the right base of the skull during periods of spiritual download, and milder left-side head pain during periods of energy release."),
            spacer(),
            body("It is not derived from any single existing tradition. It has partial overlap with several traditions, most significantly with the Western and Ayurvedic masculine-right/feminine-left body assignment and with the hands-on healing tradition of left hand receiving and right hand giving. It adds two original elements that do not appear in existing frameworks: the cervical spine as a directional reversal point, and the specific geometry of the infinity figure with the heart as a double crossing axis."),
            spacer(),
            body("It contains one unresolved element: the mechanism by which the exiting energy from the right hand reconnects to the receiving entry of the left hand to close the infinity circuit. This closing piece is acknowledged as an open question and will be documented when Christina Stevens' direct observation clarifies it."),
            divider(),

            h1("PART 2: The Framework Described"),
            h2("Core Principles"),
            spacer(),
            bodyBold([
                { text: "Principle 1: Left-Right Body Directionality. ", bold: true, color: "2D0A3E" },
                { text: "In the body below the cervical junction, the left side is feminine and receiving. The right side is masculine and giving. The left hand receives energy. The right hand gives energy." }
            ]),
            spacer(),
            bodyBold([
                { text: "Principle 2: Head Directionality Reversal. ", bold: true, color: "2D0A3E" },
                { text: "At the cervical spine, the body's energy directionality reverses. Above the cervical junction, the right side of the head is the downloading and receiving side. The left side of the head is the releasing side. This is the opposite of the body's directional assignment and is the most original element of this framework." }
            ]),
            spacer(),
            bodyBold([
                { text: "Principle 3: The Heart as Double Axis. ", bold: true, color: "2D0A3E" },
                { text: "The heart is the central crossing point of the energy circuit. Energy passes through the heart axis twice in a single complete circuit, once ascending and once descending. This makes the heart the double axis point of the infinity figure and confirms its role as the energetic center of the physical body." }
            ]),
            spacer(),
            bodyBold([
                { text: "Principle 4: The Cervical Spine as Reversal Junction. ", bold: true, color: "2D0A3E" },
                { text: "The cervical spine is the anatomical point where the body's energy directionality inverts. Below it: left is feminine/receiving, right is masculine/giving. Above it: right is downloading/receiving, left is releasing. This reversal point has anatomical support in the neurological transition that occurs at the cervical spine where brain stem transitions to spinal cord." }
            ]),
            spacer(),
            bodyBold([
                { text: "Principle 5: The Standing Infinity Figure. ", bold: true, color: "2D0A3E" },
                { text: "The complete energy circuit through the body traces a standing infinity figure (figure-8) with the heart at its double crossing point. The circuit enters at the left hand, crosses the heart ascending, wraps through the cervical spine to the right, rounds over the head from right to left, descends crossing the heart again, and exits through the right hand." }
            ]),
            spacer(),
            bodyBold([
                { text: "Principle 6: The Connector. ", bold: true, color: "2D0A3E" },
                { text: "The infinity circuit does not run as a continuously closed loop. It is an open path that completes temporarily through whatever is being interacted with in the moment, whether a person, a plant, an object, a spiritual presence, or an energetic frequency. The interaction itself becomes the connector, closing the circuit for the duration of the exchange, whether the exchange is a full download arriving, a full release completing, or both simultaneously. When the exchange completes, the circuit returns to an open path on the body. This means the infinity figure closes only in relationship and through exchange, not perpetually. This is fundamentally different from most energy circuit models which assume a continuously closed loop." }
            ]),
            spacer(),
            divider(),

            h1("PART 3: The Energy Flow in Sequence"),
            note("The following table describes the complete energy circuit as Christina Stevens has mapped it through direct somatic observation."),
            spacer(),
            flowTable,
            spacer(),
            divider(),

            h1("PART 4: Somatic Evidence and Source Observations"),
            note("These are the direct somatic observations that form the evidential basis of this framework. They are personal observations, not controlled experiments. They are presented as the honest source material for the framework."),
            spacer(),
            evTable,
            spacer(),
            divider(),

            h1("PART 5: Comparison with Existing Traditions"),
            note("This table identifies where the Christina Stevens Body Map aligns with, partially aligns with, or diverges from existing traditions. This comparison is included to demonstrate intellectual honesty and clear framework positioning, not to validate the framework through tradition alignment."),
            spacer(),
            compTable,
            spacer(),
            divider(),

            h1("PART 6: Partial Tradition Alignment Detail"),
            spacer(),
            tradTable,
            spacer(),
            divider(),

            h1("PART 7: How This Framework Integrates with the TCM Astrology Chakra System"),
            body("The Christina Stevens Body Map is a candidate for integration as an additional layer in the TCM Astrology Chakra System once sufficient development and personal validation has occurred. Potential integration points include:"),
            spacer(),
            bodyBold([{ text: "Planetary placement and body side: ", bold: true, color: "2D0A3E" }, { text: "Right-side body area activations (masculine/giving) and left-side body area activations (feminine/receiving) could add a directionality layer to the body part mapping already established in the system." }]),
            spacer(),
            bodyBold([{ text: "Injury and event analysis: ", bold: true, color: "2D0A3E" }, { text: "The right-side injuries of November 2007 during a masculine/giving body side period of maximum transit pressure is a documented personal data point. Whether right-side injuries correlate with masculine/soul-direction-giving choices under pressure is a hypothesis worth tracking across multiple chart analyses." }]),
            spacer(),
            bodyBold([{ text: "Download and release timing: ", bold: true, color: "2D0A3E" }, { text: "Right-base-of-skull migraine timing correlated with planetary transits could yield timing data for when downloads are most likely to arrive. This would require systematic tracking of migraine onset dates against transit data, which has not yet been done." }]),
            spacer(),
            bodyBold([{ text: "Heart axis and chakra work: ", bold: true, color: "2D0A3E" }, { text: "The double crossing of the heart axis in the infinity circuit is consistent with the Heart chakra's central role in the TCM Astrology Chakra System. The double crossing geometry may explain why Heart chakra work has disproportionate effects on the entire system." }]),
            spacer(),
            body("Integration will be developed as the framework matures. No integration is documented as established until it has been validated through Christina Stevens' direct observation and somatic confirmation."),
            divider(),

            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 100 },
                children: [new TextRun({ text: "The Christina Stevens Body Map is an original proprietary framework.", italics: true, size: 20, color: "2D0A3E", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
                children: [new TextRun({ text: "Created by Christina Stevens. Phoenix Rebirth. April 2026. All rights reserved.", italics: true, size: 18, color: "999999", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
                children: [new TextRun({ text: "Framework complete as of April 2026. Version 1.0. The six core principles including the closing mechanism have been confirmed through direct somatic observation by Christina Stevens.", italics: true, size: 18, color: "999999", font: "Arial" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0 },
                children: [new TextRun({ text: "This framework may not be reproduced, taught, or commercialized without written permission from Christina Stevens.", italics: true, size: 18, color: "CC2244", font: "Arial" })] }),
        ]
    }]
});

Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync("/mnt/user-data/outputs/Christina_Stevens_Body_Map_Framework.docx", buffer);
    console.log("Done");
});