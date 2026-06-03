<!DOCTYPE html>
<html lang="en">
<head>
  <title>Contact | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    .hero { min-height: 55vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 140px 40px 60px; background: radial-gradient(ellipse at 50% 40%, rgba(194,24,91,0.1) 0%, transparent 55%), var(--plum-deep); }
    .hero h1 { font-family: 'Cinzel', serif; font-size: clamp(32px,4.5vw,58px); font-weight: 400; color: var(--cream); max-width: 700px; margin-bottom: 24px; line-height: 1.2; }
    .hero h1 em { color: var(--gold); font-style: normal; }
    .hero p { font-size: 17px; font-weight: 300; font-style: italic; color: var(--cream-dim); max-width: 500px; }

    .contact-main { padding: 100px 60px; max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1.2fr; gap: 80px; align-items: start; }

    .contact-info { position: sticky; top: 100px; }
    .info-block { margin-bottom: 40px; }
    .info-block h3 { font-family: 'Cinzel', serif; font-size: 12px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); margin-bottom: 12px; }
    .info-block p { font-size: 16px; font-weight: 300; color: var(--cream-dim); }
    .info-block a { color: var(--cream-dim); text-decoration: none; transition: color 0.3s; }
    .info-block a:hover { color: var(--gold); }
    .info-divider { width: 100%; height: 1px; background: rgba(212,175,55,0.12); margin: 32px 0; }
    .expectation-list { list-style: none; }
    .expectation-list li { display: flex; gap: 14px; align-items: flex-start; padding: 12px 0; border-bottom: 1px solid rgba(212,175,55,0.06); font-size: 15px; font-weight: 300; color: var(--cream-dim); line-height: 1.6; }
    .expectation-list li::before { content: '✦'; color: var(--gold); font-size: 9px; flex-shrink: 0; margin-top: 6px; }

    .contact-form { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.15); padding: 48px 40px; }
    .form-group { margin-bottom: 24px; }
    .form-group label { display: block; font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); margin-bottom: 10px; }
    .form-group input,
    .form-group select,
    .form-group textarea { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 16px; font-weight: 300; padding: 14px 16px; outline: none; transition: border-color 0.3s; resize: vertical; }
    .form-group input:focus,
    .form-group select:focus,
    .form-group textarea:focus { border-color: rgba(212,175,55,0.5); }
    .form-group select option { background: var(--plum-mid); color: var(--cream); }
    .form-group textarea { min-height: 140px; }
    .form-note { font-size: 13px; font-style: italic; color: var(--cream-faint); margin-top: 8px; }
    .btn-full { width: 100%; text-align: center; border: none; }

    .quick-links { background: var(--plum-mid); border-top: 1px solid rgba(212,175,55,0.1); padding: 80px 60px; }
    .quick-links-inner { max-width: 1200px; margin: 0 auto; text-align: center; }
    .quick-links h2 { margin-bottom: 12px; }
    .quick-links .body-text { max-width: 540px; margin: 0 auto 48px; font-size: 17px; }
    .quick-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; }
    .quick-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(212,175,55,0.1); padding: 32px 24px; text-align: center; text-decoration: none; transition: border-color 0.3s, transform 0.3s; display: block; }
    .quick-card:hover { border-color: rgba(212,175,55,0.35); transform: translateY(-3px); }
    .quick-card h3 { font-family: 'Cinzel', serif; font-size: 13px; letter-spacing: 1px; color: var(--gold); margin-bottom: 10px; }
    .quick-card p { font-size: 14px; font-weight: 300; color: var(--cream-faint); line-height: 1.6; }

    @media (max-width: 900px) {
      .contact-main { grid-template-columns: 1fr; gap: 40px; padding: 60px 24px; }
      .quick-grid { grid-template-columns: 1fr; }
      .quick-links { padding: 60px 24px; }
    }
  </style>
</head>
<body>

<?php include 'includes/nav.php'; ?>

<div class="hero">
  <span class="eyebrow">Reach Out</span>
  <h1>Let's Figure Out<br><em>Your Next Step</em></h1>
  <p>Not sure which reading or session is right for you? Ask. That's what this is for.</p>
</div>

<div class="contact-main">
  <div class="contact-info">
    <span class="eyebrow">Direct Contact</span>
    <h2 style="font-size:clamp(22px,2.5vw,34px);">Christina Stevens</h2>
    <div class="gold-divider left"></div>

    <div class="info-block">
      <h3>Email</h3>
      <p><a href="mailto:christina@phoenixrebirth.life">christina@phoenixrebirth.life</a></p>
    </div>

    <div class="info-block">
      <h3>Phone</h3>
      <p><a href="tel:5757044549">575-704-4549</a></p>
    </div>

    <div class="info-block">
      <h3>Location</h3>
      <p>Hobbs, NM<br>Remote &amp; Distance Sessions Only<br>Serving clients worldwide</p>
    </div>

    <div class="info-divider"></div>

    <div class="info-block">
      <h3>What to Expect</h3>
      <ul class="expectation-list">
        <li>Responses within 24-48 hours on business days</li>
        <li>No generic auto-replies -- a real answer from Christina</li>
        <li>If you're not sure which service is right, just say that</li>
        <li>All sessions conducted remotely -- no travel required</li>
      </ul>
    </div>
  </div>

  <div class="contact-form">
    <span class="eyebrow" style="margin-bottom:24px;">Send a Message</span>

    <form action="contact-submit.php" method="POST">
      <div class="form-group">
        <label>Your Name</label>
        <input type="text" name="name" placeholder="First and last name" required />
      </div>

      <div class="form-group">
        <label>Email Address</label>
        <input type="email" name="email" placeholder="your@email.com" required />
      </div>

      <div class="form-group">
        <label>What Are You Reaching Out About?</label>
        <select name="topic">
          <option value="">Select one</option>
          <option>I'm not sure where to start</option>
          <option>Question about a specific reading</option>
          <option>Question about a session</option>
          <option>HarmonyHub practitioner inquiry</option>
          <option>soulReady account help</option>
          <option>Something else</option>
        </select>
      </div>

      <div class="form-group">
        <label>Your Message</label>
        <textarea name="message" placeholder="What's going on? What do you need? Don't filter yourself." required></textarea>
        <p class="form-note">No question is too small. No situation is too complicated.</p>
      </div>

      <button class="btn-primary btn-full" type="submit">Send Message &rarr;</button>
    </form>
  </div>
</div>

<div class="quick-links">
  <div class="quick-links-inner">
    <span class="eyebrow">Not Sure Where to Start?</span>
    <h2>These Are the Most<br><em>Common Entry Points</em></h2>
    <p class="body-text">Most people start with one of these. Each one gives you something real, not a taste of something you can't fully access yet.</p>
    <div class="quick-grid">
      <a href="services.php" class="quick-card">
        <h3>Soul Blueprint Decoder Tier 1</h3>
        <p>$77 &nbsp;|&nbsp; Six systems. One complete map. The most comprehensive entry point into your soul architecture.</p>
      </a>
      <a href="services.php" class="quick-card">
        <h3>TCM Astrology Chakra Tier 1</h3>
        <p>$59 &nbsp;|&nbsp; Your birth chart through a completely different lens. Interactive, visual, and immediately actionable.</p>
      </a>
      <a href="services.php" class="quick-card">
        <h3>Name Frequency Reading</h3>
        <p>$10.99 &nbsp;|&nbsp; The most accessible entry point. Your name decoded from the first letter to the last.</p>
      </a>
    </div>
  </div>
</div>

<?php include 'includes/footer.php'; ?>

</body>
</html>
