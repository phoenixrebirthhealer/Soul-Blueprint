<!DOCTYPE html>
<html lang="en">
<head>
  <title>Services &amp; Readings | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    .hero { min-height: 55vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 140px 40px 60px; background: radial-gradient(ellipse at 50% 40%, rgba(194,24,91,0.1) 0%, transparent 55%), var(--plum-deep); }
    .hero h1 { font-family: 'Cinzel', serif; font-size: clamp(32px,4.5vw,58px); font-weight: 400; color: var(--cream); max-width: 800px; margin-bottom: 24px; line-height: 1.2; }
    .hero h1 em { color: var(--gold); font-style: normal; }
    .hero p { font-size: 17px; font-weight: 300; font-style: italic; color: var(--cream-dim); max-width: 560px; }

    .section { padding: 80px 60px; max-width: 1200px; margin: 0 auto; }
    .section-divider { border: none; border-top: 1px solid rgba(212,175,55,0.12); margin: 0; }
    .section-header { margin-bottom: 48px; }

    .cards-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; }
    .cards-grid.two-col { grid-template-columns: repeat(2,1fr); }

    .service-card { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.12); padding: 32px 26px; display: flex; flex-direction: column; transition: border-color 0.3s, transform 0.3s; }
    .service-card:hover { border-color: rgba(212,175,55,0.35); transform: translateY(-3px); }
    .service-card.featured { border-color: rgba(212,175,55,0.3); background: rgba(212,175,55,0.04); }
    .card-price { font-family: 'Cinzel', serif; font-size: 13px; letter-spacing: 2px; color: var(--gold); margin-bottom: 10px; }
    .card-price .gate-note { font-size: 10px; color: var(--cream-faint); letter-spacing: 1px; display: block; margin-top: 4px; }
    .service-card h3 { font-family: 'Cinzel', serif; font-size: 14px; font-weight: 600; letter-spacing: 1px; color: var(--cream); margin-bottom: 12px; line-height: 1.4; }
    .service-card p { font-size: 15px; font-weight: 300; color: var(--cream-faint); line-height: 1.7; flex: 1; margin-bottom: 24px; }
    .card-link { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--magenta); text-decoration: none; display: inline-flex; align-items: center; gap: 8px; transition: gap 0.2s; }
    .card-link:hover { gap: 14px; }

    .session-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(212,175,55,0.1); padding: 28px; display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; transition: border-color 0.3s; margin-bottom: 12px; }
    .session-card:hover { border-color: rgba(212,175,55,0.3); }
    .session-card h3 { font-family: 'Cinzel', serif; font-size: 14px; color: var(--cream); margin-bottom: 8px; }
    .session-card p { font-size: 15px; font-weight: 300; color: var(--cream-faint); line-height: 1.7; }
    .session-card .duration { font-size: 12px; color: rgba(212,175,55,0.5); letter-spacing: 1px; margin-top: 6px; }
    .session-price { text-align: right; flex-shrink: 0; }
    .session-price .price { font-family: 'Cinzel', serif; font-size: 22px; color: var(--gold); display: block; margin-bottom: 12px; }

    .ffs-note { background: rgba(212,175,55,0.05); border-left: 3px solid var(--gold); padding: 16px 20px; margin-top: 24px; }
    .ffs-note p { font-size: 14px; color: var(--cream-dim); font-style: italic; }

    .harmonyhub { background: var(--plum-mid); border-top: 1px solid rgba(212,175,55,0.1); border-bottom: 1px solid rgba(212,175,55,0.1); }
    .harmonyhub-inner { padding: 80px 60px; max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.2fr 1fr; gap: 60px; align-items: center; }
    .harmonyhub-inner .body-text { font-size: 17px; margin-bottom: 20px; }
    .hh-price-box { background: rgba(255,255,255,0.02); border: 1px solid rgba(212,175,55,0.15); padding: 40px 32px; text-align: center; }

    @media (max-width: 900px) {
      .cards-grid, .cards-grid.two-col { grid-template-columns: 1fr; }
      .harmonyhub-inner { grid-template-columns: 1fr; }
      .session-card { flex-direction: column; }
      .session-price { text-align: left; }
      .section, .harmonyhub-inner { padding: 60px 24px; }
    }
  </style>
</head>
<body>

<?php include 'includes/nav.php'; ?>

<div class="hero">
  <span class="eyebrow">Readings &amp; Sessions</span>
  <h1>Every Offering Is Built<br><em>From Your Actual Data</em></h1>
  <p>Nothing generic. Nothing templated. Everything decoded from the specific architecture of who you are.</p>
</div>

<div class="section">
  <div class="section-header">
    <span class="eyebrow">Soul Readings</span>
    <h2>Delivered as Interactive<br><em>HTML Experiences</em></h2>
    <p class="body-text" style="max-width:580px; font-size:16px; margin-top:8px;">Every reading is a standalone interactive file delivered through your soulReady account. Open on a desktop browser for the full experience.</p>
  </div>
  <div class="cards-grid">
    <div class="service-card">
      <div class="card-price">$10.99</div>
      <h3>Name Frequency Reading</h3>
      <p>Your name carries a measurable energetic signature. This reading decodes every letter, every position, and what the full sequence broadcasts into every interaction you have.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
    <div class="service-card featured">
      <div class="card-price">$59</div>
      <h3>TCM Astrology Chakra Reading &mdash; Tier 1</h3>
      <p>Your birth chart mapped through Traditional Chinese Medicine and the chakra system. An interactive wheel showing how your planetary placements affect every layer of your energetic body.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
    <div class="service-card featured">
      <div class="card-price">$77</div>
      <h3>Soul Blueprint Decoder &mdash; Tier 1</h3>
      <p>Six systems in one reading: astrology, Human Design, numerology, Hebrew frequency, ancestral patterns, and chakra mapping. Your complete soul architecture in one interactive map.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
    <div class="service-card">
      <div class="card-price">$82</div>
      <h3>Self-Love Language Reading</h3>
      <p>Decoded from your actual chart data -- how you receive love, how you block it, and the specific patterns that have been running underneath your relationships your entire life.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
    <div class="service-card">
      <div class="card-price">$47<span class="gate-note">Requires Self-Love Language Reading first</span></div>
      <h3>Soul's Journey Reading</h3>
      <p>An interactive journey map of your soul's major activation points -- past, present, and what's being activated right now in your current profection year.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
    <div class="service-card">
      <div class="card-price">$110</div>
      <h3>TCM Astrology Chakra Tier 2 &mdash; Deep Dive</h3>
      <p>The full depth of your TCM chakra map. Every planet, every tension, every healing pathway decoded in a live deep-dive session with full written delivery.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
    <div class="service-card">
      <div class="card-price">$325<span class="gate-note">Includes live session</span></div>
      <h3>Soul Blueprint Decoder &mdash; Tier 2</h3>
      <p>Everything in Tier 1 plus a live 90-minute deep-dive session. We go into your neurodivergence connections, your clairs, your Rebirth activations, and exactly what's ready to shift.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
  </div>
</div>

<hr class="section-divider" />

<div class="section">
  <div class="section-header">
    <span class="eyebrow">Relational Name Frequency</span>
    <h2>Two Names.<br><em>One Frequency Map.</em></h2>
    <p class="body-text" style="max-width:580px; font-size:16px; margin-top:8px;">Any two people -- romantic partners, business partners, parent and child, best friends. The frequency between two names tells a story nothing else can.</p>
  </div>
  <div class="cards-grid two-col">
    <div class="service-card">
      <div class="card-price">$10.99</div>
      <h3>Relational Tier 1 &mdash; Shared Frequencies</h3>
      <p>Where your name frequencies align, reinforce each other, and create the foundational resonance of this connection.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
    <div class="service-card">
      <div class="card-price">$10.99</div>
      <h3>Relational Tier 2 &mdash; What Each Activates</h3>
      <p>What each person activates in the other that they cannot generate alone. The asymmetry that makes this connection uniquely powerful.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
    <div class="service-card">
      <div class="card-price">$10.99</div>
      <h3>Relational Tier 3 &mdash; The Friction Map</h3>
      <p>Where the frequencies create tension -- and why that tension is actually the growth edge, not the problem.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
    <div class="service-card featured">
      <div class="card-price">From $18.99</div>
      <h3>Relational Bundles</h3>
      <p>Tiers 2 + 3 together: $18.99 &nbsp;|&nbsp; All three tiers together: $26.99. The complete picture of any relationship decoded from both names.</p>
      <a href="soulready.php" class="card-link">Get This Reading &rarr;</a>
    </div>
  </div>
</div>

<hr class="section-divider" />

<div class="section">
  <div class="section-header">
    <span class="eyebrow">Live Sessions</span>
    <h2>Direct Work.<br><em>Remote. Worldwide.</em></h2>
    <p class="body-text" style="max-width:580px; font-size:16px; margin-top:8px;">All sessions are conducted remotely via distance. No geographic limitations. Book through soulReady and Christina will confirm your appointment.</p>
  </div>

  <div class="session-card">
    <div>
      <h3>Field Frequency Scan</h3>
      <p>Quick energetic field assessment and clearing. Credited toward any session booked within 30 days.</p>
      <p class="duration">30 minutes</p>
    </div>
    <div class="session-price">
      <span class="price">$75</span>
      <a href="booking.php" class="btn-primary">Book</a>
    </div>
  </div>

  <div class="session-card">
    <div>
      <h3>Rapid Relief</h3>
      <p>Targeted relief for acute energetic disruptions. When something is actively wrong and you need it addressed now.</p>
      <p class="duration">60 minutes</p>
    </div>
    <div class="session-price">
      <span class="price">$225</span>
      <a href="booking.php" class="btn-primary">Book</a>
    </div>
  </div>

  <div class="session-card">
    <div>
      <h3>Mild Healing Session</h3>
      <p>Gentle healing for mild energetic imbalances. Clearing, realignment, and integration work.</p>
      <p class="duration">60 minutes</p>
    </div>
    <div class="session-price">
      <span class="price">$275</span>
      <a href="booking.php" class="btn-primary">Book</a>
    </div>
  </div>

  <div class="session-card">
    <div>
      <h3>Chronic Healing Session</h3>
      <p>Deep healing work for long-standing patterns, chronic blocks, and what keeps coming back no matter what you try.</p>
      <p class="duration">90 minutes</p>
    </div>
    <div class="session-price">
      <span class="price">$475</span>
      <a href="booking.php" class="btn-primary">Book</a>
    </div>
  </div>

  <div class="session-card">
    <div>
      <h3>Guidance Session</h3>
      <p>Soul-aligned guidance and clarity for major life decisions, direction, and what your next move actually is.</p>
      <p class="duration">60 minutes</p>
    </div>
    <div class="session-price">
      <span class="price">$450</span>
      <a href="booking.php" class="btn-primary">Book</a>
    </div>
  </div>

  <div class="session-card">
    <div>
      <h3>Sovereign Multidimensional Oracle Reading</h3>
      <p>Full multidimensional oracle and channeled reading. Evidential mediumship, spirit team guidance, and direct soul-level transmission.</p>
      <p class="duration">75 minutes</p>
    </div>
    <div class="session-price">
      <span class="price">$575</span>
      <a href="booking.php" class="btn-primary">Book</a>
    </div>
  </div>

  <div class="ffs-note">
    <p>The Field Frequency Scan ($75) is credited toward any session booked within 30 days. You pay the session price minus $75.</p>
  </div>
</div>

<hr class="section-divider" />

<div class="harmonyhub">
  <div class="harmonyhub-inner">
    <div>
      <span class="eyebrow">For Practitioners</span>
      <h2>HarmonyHub</h2>
      <p class="body-text">A platform built for healing arts practitioners who want access to the Phoenix Rebirth system for their own practice. Tools, frameworks, and resources -- $35 per year.</p>
      <p class="body-text" style="font-size:15px; margin-top:8px;">Practitioner access only. Not a public platform.</p>
      <br>
      <a href="contact.php" class="btn-magenta">Inquire About Access &rarr;</a>
    </div>
    <div class="hh-price-box">
      <span class="eyebrow" style="display:block; margin-bottom:16px;">Annual Access</span>
      <p style="font-family:'Cinzel',serif; font-size:52px; color: var(--gold); line-height:1; margin-bottom:8px;">$35</p>
      <p style="font-size:14px; color: var(--cream-faint); font-style:italic;">Per year. Practitioners only.</p>
    </div>
  </div>
</div>

<?php include 'includes/footer.php'; ?>

</body>
</html>
