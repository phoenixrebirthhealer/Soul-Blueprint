# Quiz.jsx handleSubmit Change for Survival Mode PDF Trigger

## Location
Inside the `handleSubmit` async function in Quiz.jsx.

---

## FIND this exact block (the Assessment.create call):

```javascript
      // Create assessment record
      await base44.entities.Assessment.create({
        client_id: client.id,
        answers: { ...answers, medical_device_disclosure: disclosureData },
        ...scores,
        completed_at: new Date().toISOString(),
      });
```

---

## REPLACE with this exact block:

```javascript
      // Create assessment record
      const assessmentRecord = await base44.entities.Assessment.create({
        client_id: client.id,
        answers: { ...answers, medical_device_disclosure: disclosureData },
        ...scores,
        completed_at: new Date().toISOString(),
      });

      // Survival Mode PDF trigger
      const SURVIVAL_QUALIFYING_STYLES = new Set([
        'Pure Avoidant',
        'Pure Anxious',
        'Pure Disorganized',
        'Disorganized Anxious Leaning',
        'Disorganized Avoidant Leaning',
        'True Disorganized Equal Split',
      ]);
      const survivalTriggered =
        scores.self_love_score <= 33 ||
        (scores.self_love_score <= 67 &&
          SURVIVAL_QUALIFYING_STYLES.has(scores.attachment_style));

      if (survivalTriggered) {
        try {
          const readings = await base44.entities.SoulBlueprintReading.filter({
            client_id: client.id,
          });
          const reading = readings?.[0];
          const hdData = reading?.human_design_data
            ? JSON.parse(reading.human_design_data)
            : {};
          const astroData = reading?.astrology_data
            ? JSON.parse(reading.astrology_data)
            : {};
          const numData = reading?.numerology_data
            ? JSON.parse(reading.numerology_data)
            : {};

          const pdfRes = await fetch(
            'https://soul-blueprint-production.up.railway.app/generate-survival-mode-pdf',
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                client_name: client.first_name || formData.first_name || '',
                hd_type: hdData.type || '',
                hd_authority: hdData.authority || '',
                moon: astroData.moon || '',
                north_node: astroData.northNode || '',
                south_node: astroData.southNode || '',
                life_path:
                  numData.lifePath ??
                  numData.life_path ??
                  numData.lifePathNumber ??
                  '',
                attachment_style: scores.attachment_style,
                self_love_score: scores.self_love_score,
                self_love_result: scores.self_love_result,
              }),
            }
          );

          if (pdfRes.ok) {
            const pdfData = await pdfRes.json();
            await base44.entities.Assessment.update(assessmentRecord.id, {
              survival_mode_pdf_html: pdfData.pdf_html,
              survival_mode_triggered: true,
            });
          }
        } catch (err) {
          console.error('Survival mode PDF generation failed:', err);
        }
      }
```

---

## Base44 entity fields to add

Before this code will save correctly, add these two fields to the **Assessment** entity in Base44:

| Field name | Type |
|---|---|
| `survival_mode_triggered` | Boolean |
| `survival_mode_pdf_html` | Long Text |

---

## How it works

- Trigger fires if `self_love_score <= 33` (any attachment style)
- Trigger also fires if `self_love_score <= 67` AND the attachment style is one of the six qualifying insecure styles
- Pulls `SoulBlueprintReading` for this client to get HD, astrology, and numerology data
- Calls Railway endpoint `/generate-survival-mode-pdf` with all personalization data
- Stores the returned HTML back on the Assessment record for display on the client dashboard
