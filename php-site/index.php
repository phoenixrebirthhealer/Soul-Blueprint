<!DOCTYPE html>
<html lang="en">
<head>
  <title>Phoenix Rebirth | Christina Stevens</title>
  <?php include 'includes/head.php'; ?>
  <style>
    .hero {
      min-height: 100vh;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      text-align: center; padding: 140px 40px 100px;
      background: radial-gradient(ellipse at 50% 35%, rgba(194,24,91,0.14) 0%, transparent 55%),
                  radial-gradient(ellipse at 20% 80%, rgba(212,175,55,0.06) 0%, transparent 50%),
                  var(--plum-deep);
    }
    .hero-title { font-family: 'Cinzel', serif; font-size: clamp(36px,5.5vw,68px); font-weight: 400; line-height: 1.2; color: var(--cream); max-width: 860px; margin-bottom: 28px; }
    .hero-title em { color: var(--gold); font-style: normal; }
    .hero-sub { font-size: clamp(18px,2vw,24px); font-weight: 300; font-style: italic; color: var(--magenta); margin-bottom: 48px; letter-spacing: 1px; }
    .hero-body { font-size: 18px; font-weight: 300; color: var(--cream-dim); max-width: 620px; margin-bottom: 56px; line-height: 1.9; }

    .truth { background: var(--plum-mid); border-top: 1px solid rgba(212,175,55,0.1); border-bottom: 1px solid rgba(212,175,55,0.1); padding: 100px 60px; }
    .truth-inner { max-width: 780px; margin: 0 auto; text-align: center; }
    .truth-inner blockquote { font-size: clamp(22px,2.5vw,32px); font-weight: 300; font-style: italic; line-height: 1.6; color: var(--cream); margin-bottom: 48px; }
    .truth-inner blockquote em { color: var(--gold); font-style: normal; }
    .truth-inner .body-text { font-size: 17px; max-width: 640px; margin: 0 auto 16px; }

    .about-strip { padding: 100px 60px; max-width: 1200px; margin: 0 auto; }
    .about-grid { display: grid; grid-template-columns: 1fr 1.4fr; gap: 80px; align-items: center; }
    .photo-block { width: 100%; aspect-ratio: 3/4; background: linear-gradient(160deg, var(--plum-light) 0%, rgba(194,24,91,0.15) 100%); border: 1px solid rgba(212,175,55,0.2); display: flex; align-items: center; justify-content: center; }
    .photo-label { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; color: rgba(212,175,55,0.35); text-transform: uppercase; text-align: center; }
    .about-copy .body-text { margin-bottom: 20px; font-size: 17px; }

    .services-section { background: var(--plum-mid); border-top: 1px solid rgba(212,175,55,0.1); padding: 100px 60px; }
    .services-inner { max-width: 1200px; margin: 0 auto; }
    .services-header { text-align: center; margin-bottom: 64px; }
    .services-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 24px; }
    .service-card { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.12); padding: 36px 28px; transition: border-color 0.3s,transform 0.3s; display: flex; flex-direction: column; }
    .service-card:hover { border-color: rgba(212,175,55,0.35); transform: translateY(-3px); }
    .service-price { font-family: 'Cinzel', serif; font-size: 12px; letter-spacing: 2px; color: var(--gold); margin-bottom: 12px; }
    .service-card h3 { font-family: 'Cinzel', serif; font-size: 14px; font-weight: 600; letter-spacing: 1px; color: var(--cream); margin-bottom: 14px; line-height: 1.4; }
    .service-card p { font-size: 15px; font-weight: 300; color: var(--cream-faint); line-height: 1.7; flex: 1; margin-bottom: 24px; }
    .service-link { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--magenta); text-decoration: none; display: inline-flex; align-items: center; gap: 8px; transition: gap 0.2s; }
    .service-link:hover { gap: 14px; }
    .services-footer { text-align: center; margin-top: 56px; padding-top: 48px; border-top: 1px solid rgba(212,175,55,0.1); }
    .services-footer p { font-size: 15px; color: var(--cream-faint); margin-bottom: 24px; font-style: italic; }

    .soulready-section { padding: 100px 60px; background: radial-gradient(ellipse at 60% 50%, rgba(194,24,91,0.1) 0%, transparent 60%), var(--plum-deep); border-top: 1px solid rgba(194,24,91,0.15); }
    .soulready-inner { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.2fr 1fr; gap: 80px; align-items: center; }
    .soulready-copy .body-text { font-size: 17px; margin-bottom: 20px; }
    .soulready-copy h2 { margin-bottom: 24px; }
    .soulready-features { list-style: none; margin: 32px 0 40px; }
    .soulready-features li { font-size: 16px; font-weight: 300; color: var(--cream-dim); padding: 10px 0; border-bottom: 1px solid rgba(212,175,55,0.08); display: flex; align-items: center; gap: 14px; }
    .soulready-features li::before { content: '✦'; color: var(--gold); font-size: 10px; flex-shrink: 0; }
    .soulready-visual { background: linear-gradient(160deg, rgba(45,16,84,0.8), rgba(194,24,91,0.12)); border: 1px solid rgba(194,24,91,0.2); padding: 60px 40px; text-align: center; }
    .app-name { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 8px; text-transform: uppercase; color: var(--magenta); margin-bottom: 24px; display: block; }
    .app-headline { font-size: 28px; font-weight: 300; font-style: italic; color: var(--cream); line-height: 1.5; margin-bottom: 40px; }
    .divider-m { width: 40px; height: 1px; background: var(--magenta); margin: 0 auto 40px; }
    .app-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    .app-stat { padding: 20px; border: 1px solid rgba(194,24,91,0.15); }
    .app-stat-num { font-family: 'Cinzel', serif; font-size: 28px; color: var(--gold); display: block; margin-bottom: 4px; }
    .app-stat-label { font-size: 13px; color: var(--cream-faint); font-style: italic; }

    @media (max-width: 900px) {
      .about-grid, .soulready-inner { grid-template-columns: 1fr; gap: 40px; }
      .services-grid { grid-template-columns: 1fr; }
      .about-strip, .truth, .services-section, .soulready-section { padding: 60px 24px; }
    }
  </style>
</head>
<body>

<?php include 'includes/nav.php'; ?>

<div class="hero">
  <span class="eyebrow">Christina Stevens &nbsp;|&nbsp; Awakening Catalyst &nbsp;|&nbsp; Soul Liberation Guide</span>
  <h1 class="hero-title">What if <em>nothing is wrong</em> with you?<br>What if you just never had a map?</h1>
  <p class="hero-sub">Your Soul Blueprint isn't a diagnosis. It's a direction.</p>
  <p class="hero-body">You weren't built to fit the default settings. You were built for something that requires knowing exactly who you are — all the way down to your wiring, your soul architecture, and your energetic blueprint.</p>
  <a href="services.php" class="btn-primary">Start With Your Blueprint &rarr;</a>
</div>

<div class="truth">
  <div class="truth-inner">
    <blockquote>"You've read the books. Done the practices.<br>Made progress. And something underneath it all<br><em>still won't move.</em>"</blockquote>
    <div class="gold-divider"></div>
    <p class="body-text">You're not broken. You're not doing it wrong. You've just been working from incomplete data — using systems that were never designed for the depth you carry, the sensitivity you navigate, or the kind of soul you came in as.</p>
    <p class="body-text">Most healing frameworks weren't built for people like you. They flatten what's complex, skip what's subtle, and leave you wondering why you still can't just "get it together" like everyone else.</p>
    <p class="body-text">This is a different kind of work. And it starts with your actual data.</p>
  </div>
</div>

<div class="about-strip">
  <div class="about-grid">
    <div class="photo-block"><span class="photo-label">Christina Stevens<br>Photo</span></div>
    <div class="about-copy">
      <span class="eyebrow" style="margin-bottom:16px;">The Work</span>
      <h2>I'm Not Here<br>to Fix <em>Anyone</em></h2>
      <div class="gold-divider left"></div>
      <p class="body-text">I work with people who are done with surface-level solutions. Using a proprietary multi-system approach — your astrology, Human Design, numerology, Hebrew frequency, ancestral patterns, and TCM energy mapping — we build an actual map of who you are and why you operate the way you do.</p>
      <p class="body-text">Not to fix you. To show you who you already are — and activate what's been waiting to come online.</p>
      <p class="body-text">I'm neurodivergent with 23 confirmed wiring patterns. I built these systems because nothing else existed that went this deep. I work remotely, worldwide. No chanting required.</p>
      <br>
      <a href="about.php" class="btn-ghost">More About Christina</a>
    </div>
  </div>
</div>

<div class="services-section">
  <div class="services-inner">
    <div class="services-header">
      <span class="eyebrow">Readings &amp; Sessions</span>
      <h2>Where Do You Start?</h2>
      <div class="gold-divider"></div>
    </div>
    <div class="services-grid">
      <div class="service-card">
        <div class="service-price">$10.99</div>
        <h3>Name Frequency Reading</h3>
        <p>Your name carries a measurable energetic signature. This reading decodes what it broadcasts and what it activates in every interaction.</p>
        <a href="services.php" class="service-link">Learn More &rarr;</a>
      </div>
      <div class="service-card">
        <div class="service-price">$59</div>
        <h3>TCM Astrology Chakra Reading — Tier 1</h3>
        <p>Your birth chart mapped through Traditional Chinese Medicine and the chakra system. Interactive. Visual. A completely different lens on your astrology.</p>
        <a href="services.php" class="service-link">Learn More &rarr;</a>
      </div>
      <div class="service-card">
        <div class="service-price">$77</div>
        <h3>Soul Blueprint Decoder — Tier 1</h3>
        <p>Six systems in one reading: astrology, Human Design, numerology, Hebrew frequency, ancestral patterns, and chakra mapping. Your complete soul architecture.</p>
        <a href="services.php" class="service-link">Learn More &rarr;</a>
      </div>
      <div class="service-card">
        <div class="service-price">$82</div>
        <h3>Self-Love Language Reading</h3>
        <p>Discover exactly how you receive, block, and sabotage love — decoded through your actual chart data. Not a quiz. Not generic. Your specific wiring.</p>
        <a href="services.php" class="service-link">Learn More &rarr;</a>
      </div>
      <div class="service-card">
        <div class="service-price">$75</div>
        <h3>Field Frequency Scan</h3>
        <p>A targeted energetic read of what's currently active in your field. Credited toward a session if you book within 30 days.</p>
        <a href="services.php" class="service-link">Learn More &rarr;</a>
      </div>
      <div class="service-card">
        <div class="service-price">From $225</div>
        <h3>1:1 Guidance Sessions</h3>
        <p>Direct work. Soul Liberation Guidance, Rapid Relief, or deep-dive Chronic pattern work. All remote. All by appointment.</p>
        <a href="booking.php" class="service-link">Book Now &rarr;</a>
      </div>
    </div>
    <div class="services-footer">
      <p>Not sure which one is right for you? The Soul Blueprint Decoder Tier 1 is the best place to start for most people.</p>
      <a href="services.php" class="btn-ghost">View All Readings &amp; Pricing</a>
    </div>
  </div>
</div>

<div class="soulready-section">
  <div class="soulready-inner">
    <div class="soulready-copy">
      <span class="eyebrow">Now Available</span>
      <h2>The <em>soulReady</em> App</h2>
      <p class="body-text">Everything I do lives inside soulReady. Your readings are delivered there. Your chart data lives there. Your tools, your progress, your direct line to me — all in one place.</p>
      <p class="body-text">It's built specifically for the neurodivergent, the awakening, and the people who've never had a system that actually worked for them. No overwhelm. Just your data and your next step.</p>
      <ul class="soulready-features">
        <li>Interactive readings delivered directly to your account</li>
        <li>Astrology, Human Design, and numerology in one integrated system</li>
        <li>Secure messaging with Christina</li>
        <li>Transit tracking and activation window alerts</li>
        <li>Built for neurodivergent nervous systems</li>
      </ul>
      <a href="soulready.php" class="btn-magenta">Enter soulReady &rarr;</a>
    </div>
    <div class="soulready-visual">
      <span class="app-name">soulReady</span>
      <p class="app-headline">"Step into a platform built<br>for the way you're actually wired."</p>
      <div class="divider-m"></div>
      <div class="app-stats">
        <div class="app-stat"><span class="app-stat-num">6</span><span class="app-stat-label">Systems integrated</span></div>
        <div class="app-stat"><span class="app-stat-num">1</span><span class="app-stat-label">Place for everything</span></div>
        <div class="app-stat"><span class="app-stat-num">0</span><span class="app-stat-label">Generic guidance</span></div>
        <div class="app-stat"><span class="app-stat-num">&#8734;</span><span class="app-stat-label">Your actual data</span></div>
      </div>
    </div>
  </div>
</div>

<?php include 'includes/footer.php'; ?>

</body>
</html>
