<!DOCTYPE html>
<html lang="en">
<head>
  <title>soulReady App | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    .hero { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 140px 40px 80px; background: radial-gradient(ellipse at 50% 35%, rgba(194,24,91,0.16) 0%, transparent 55%), radial-gradient(ellipse at 20% 80%, rgba(212,175,55,0.06) 0%, transparent 50%), var(--plum-deep); }
    .hero-brand { font-family: 'Cinzel', serif; font-size: clamp(48px,8vw,96px); font-weight: 400; color: var(--cream); letter-spacing: 8px; margin-bottom: 8px; }
    .hero-brand em { color: var(--magenta); font-style: normal; }
    .hero-tagline { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 8px; text-transform: uppercase; color: rgba(212,175,55,0.6); margin-bottom: 48px; }
    .hero-statement { font-family: 'Cormorant Garamond', serif; font-size: clamp(20px,2.5vw,28px); font-weight: 300; font-style: italic; color: var(--cream-dim); max-width: 700px; margin-bottom: 56px; line-height: 1.7; }
    .hero-statement em { color: var(--cream); font-style: normal; }
    .hero-btns { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }

    .what { padding: 100px 60px; max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center; }
    .what-copy .body-text { font-size: 17px; margin-bottom: 24px; }
    .what-visual { background: linear-gradient(160deg, rgba(45,16,84,0.8), rgba(194,24,91,0.12)); border: 1px solid rgba(194,24,91,0.2); padding: 52px 40px; }
    .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; }
    .stat-block { padding: 28px 24px; border: 1px solid rgba(194,24,91,0.12); text-align: center; }
    .stat-num { font-family: 'Cinzel', serif; font-size: 36px; color: var(--gold); display: block; margin-bottom: 6px; }
    .stat-label { font-size: 13px; color: var(--cream-faint); font-style: italic; line-height: 1.4; }

    .features { background: var(--plum-mid); border-top: 1px solid rgba(212,175,55,0.1); border-bottom: 1px solid rgba(212,175,55,0.1); padding: 100px 60px; }
    .features-inner { max-width: 1200px; margin: 0 auto; }
    .features-header { text-align: center; margin-bottom: 64px; }
    .features-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 24px; }
    .feature-card { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.1); padding: 36px 28px; transition: border-color 0.3s, transform 0.3s; }
    .feature-card:hover { border-color: rgba(212,175,55,0.3); transform: translateY(-3px); }
    .feature-icon { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 4px; color: var(--magenta); text-transform: uppercase; margin-bottom: 16px; display: block; }
    .feature-card h3 { font-family: 'Cinzel', serif; font-size: 14px; color: var(--cream); margin-bottom: 12px; line-height: 1.4; }
    .feature-card p { font-size: 15px; font-weight: 300; color: var(--cream-faint); line-height: 1.7; }

    .how { padding: 100px 60px; max-width: 1000px; margin: 0 auto; }
    .how-header { text-align: center; margin-bottom: 64px; }
    .steps { display: flex; flex-direction: column; }
    .step { display: flex; gap: 32px; align-items: flex-start; padding: 36px 0; border-bottom: 1px solid rgba(212,175,55,0.08); }
    .step:last-child { border-bottom: none; }
    .step-num { font-family: 'Cinzel', serif; font-size: 40px; color: rgba(212,175,55,0.2); line-height: 1; flex-shrink: 0; width: 60px; }
    .step h3 { font-family: 'Cinzel', serif; font-size: 16px; color: var(--gold); margin-bottom: 10px; }
    .step p { font-size: 16px; font-weight: 300; color: var(--cream-dim); line-height: 1.8; }

    .nd-note { background: radial-gradient(ellipse at 50% 50%, rgba(194,24,91,0.08), transparent 70%), var(--plum-mid); border-top: 1px solid rgba(194,24,91,0.15); padding: 80px 60px; text-align: center; }
    .nd-note-inner { max-width: 720px; margin: 0 auto; }
    .nd-note blockquote { font-family: 'Cormorant Garamond', serif; font-size: clamp(20px,2.5vw,28px); font-weight: 300; font-style: italic; color: var(--cream); line-height: 1.6; margin-bottom: 32px; }
    .nd-note blockquote em { color: var(--magenta); font-style: normal; }
    .nd-note .body-text { font-size: 16px; }

    .cta-section { padding: 100px 60px; text-align: center; }
    .cta-section h2 { margin-bottom: 20px; }
    .cta-section .body-text { max-width: 560px; margin: 0 auto 48px; font-size: 17px; }

    @media (max-width: 900px) {
      .what, .features-grid { grid-template-columns: 1fr; }
      .what, .features, .how, .nd-note, .cta-section { padding: 60px 24px; }
    }
  </style>
</head>
<body>

<?php include 'includes/nav.php'; ?>

<div class="hero">
  <p class="hero-tagline">Phoenix Rebirth &nbsp;|&nbsp; Your Activation Platform</p>
  <h1 class="hero-brand">soul<em>Ready</em></h1>
  <p class="hero-statement">
    Everything Christina does lives here. Your readings. Your chart data.<br>
    Your courses. Your resources. Your <em>direct line to your next step.</em>
  </p>
  <div class="hero-btns">
    <a href="contact.php" class="btn-magenta">Enter soulReady &rarr;</a>
    <a href="services.php" class="btn-primary">See All Readings</a>
  </div>
</div>

<div class="what">
  <div class="what-copy">
    <span class="eyebrow">What Is soulReady</span>
    <h2>Not Just a Platform.<br><em>Your Activation Center.</em></h2>
    <div class="gold-divider left"></div>
    <p class="body-text">soulReady is where the work actually lives. When you purchase a reading, it's delivered here as an interactive experience -- not an email attachment, not a PDF, not a Zoom call. A fully built, visual, interactive map of your soul architecture that you can return to any time.</p>
    <p class="body-text">Your chart data stays in your account. Your readings stay in your account. Your conversations with Christina happen here. Everything in one place, built specifically for the way you're wired -- not the way everyone else is.</p>
  </div>
  <div class="what-visual">
    <span class="eyebrow" style="text-align:center; display:block; margin-bottom:32px;">Inside soulReady</span>
    <div class="stat-grid">
      <div class="stat-block">
        <span class="stat-num">6</span>
        <span class="stat-label">Soul systems integrated</span>
      </div>
      <div class="stat-block">
        <span class="stat-num">1</span>
        <span class="stat-label">Place for everything</span>
      </div>
      <div class="stat-block">
        <span class="stat-num">0</span>
        <span class="stat-label">Generic content</span>
      </div>
      <div class="stat-block">
        <span class="stat-num">&#8734;</span>
        <span class="stat-label">Your actual data</span>
      </div>
    </div>
  </div>
</div>

<div class="features">
  <div class="features-inner">
    <div class="features-header">
      <span class="eyebrow">What's Inside</span>
      <h2>Everything You Need.<br><em>Nothing You Don't.</em></h2>
      <div class="gold-divider"></div>
    </div>
    <div class="features-grid">
      <div class="feature-card">
        <span class="feature-icon">Readings</span>
        <h3>Interactive Soul Readings</h3>
        <p>Every reading delivered as a fully interactive HTML experience. Visual, immersive, and built to be returned to -- not filed away and forgotten.</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">Chart Data</span>
        <h3>Your Complete Chart Archive</h3>
        <p>Your astrology, Human Design, numerology, and Hebrew frequency data stored in your account. Always accessible. Always yours.</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">Sessions</span>
        <h3>Session Booking</h3>
        <p>Book any session directly through soulReady. Choose your service, pick your time, and pay -- all in one place. Your timezone is auto-detected.</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">Courses</span>
        <h3>Courses &amp; Training</h3>
        <p>Self-paced courses built from the Phoenix Rebirth system. Go deeper at your own speed, in your own time, without overwhelm.</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">Resources</span>
        <h3>Downloadable Resource Library</h3>
        <p>Tools, guides, and resources you can access and download anytime. Gated to what you've unlocked -- nothing overwhelming, nothing irrelevant.</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">Direct Line</span>
        <h3>Messaging with Christina</h3>
        <p>Direct messaging inside the app. Ask questions, get support, follow up on your reading -- without going through email or social media.</p>
      </div>
    </div>
  </div>
</div>

<div class="how">
  <div class="how-header">
    <span class="eyebrow">How It Works</span>
    <h2>Simple.<br><em>No Learning Curve.</em></h2>
    <div class="gold-divider"></div>
  </div>
  <div class="steps">
    <div class="step">
      <div class="step-num">01</div>
      <div>
        <h3>Create Your Account</h3>
        <p>Sign up with your email. Your account is where everything gets delivered and stored. Takes two minutes.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">02</div>
      <div>
        <h3>Complete Your Intake</h3>
        <p>Enter your birth data -- date, time, and place. This is what powers every reading. The more accurate the data, the more precise the map.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">03</div>
      <div>
        <h3>Choose Your Reading or Session</h3>
        <p>Pick what you want to start with. Not sure? The Soul Blueprint Decoder Tier 1 is where most people begin -- it gives you the full picture.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">04</div>
      <div>
        <h3>Receive Your Reading</h3>
        <p>Christina generates your reading and delivers it directly to your account. You get notified when it's ready. Open it on a desktop browser for the full interactive experience.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">05</div>
      <div>
        <h3>Come Back to It</h3>
        <p>Your readings live in your account permanently. Return to them as you integrate. Things you didn't see the first time will become clear the second and third time.</p>
      </div>
    </div>
  </div>
</div>

<div class="nd-note">
  <div class="nd-note-inner">
    <blockquote>
      "This platform was built by someone with<br>
      <em>23 confirmed neurodivergent wiring patterns.</em><br>
      It shows."
    </blockquote>
    <div class="gold-divider"></div>
    <p class="body-text">soulReady is designed for the way neurodivergent, highly sensitive, and awakening souls actually process information. No overwhelm by design. No notification floods. No gamification. Just your data, your readings, and your next step -- when you're ready for it.</p>
  </div>
</div>

<div class="cta-section">
  <span class="eyebrow">You're Ready</span>
  <h2>Your Blueprint Is<br><em>Already Encoded</em></h2>
  <p class="body-text">You just need the map. Everything you need to understand how you're wired, why you operate the way you do, and what your soul came here to do -- it's all already in your data. Let's read it.</p>
  <a href="contact.php" class="btn-magenta">Enter soulReady &rarr;</a>
</div>

<?php include 'includes/footer.php'; ?>

</body>
</html>
