<!DOCTYPE html>
<html lang="en">
<head>
  <title>My Portal | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; }
    .main { flex: 1; padding: 120px 40px 80px; }
    .inner { max-width: 900px; margin: 0 auto; }

    .welcome { margin-bottom: 48px; }
    .welcome h1 { font-family: 'Cinzel', serif; font-size: clamp(22px,3vw,38px); font-weight: 400; color: var(--cream); margin-bottom: 8px; }
    .welcome h1 em { color: var(--gold); font-style: normal; }
    .welcome p { font-size: 16px; font-weight: 300; color: var(--cream-dim); line-height: 1.8; }

    .step-banner { background: rgba(212,175,55,0.06); border: 1px solid rgba(212,175,55,0.2); padding: 28px 32px; margin-bottom: 40px; display: flex; align-items: center; gap: 24px; }
    .step-icon { font-size: 28px; color: var(--gold); flex-shrink: 0; }
    .step-banner h3 { font-family: 'Cinzel', serif; font-size: 14px; letter-spacing: 2px; color: var(--gold); margin-bottom: 6px; }
    .step-banner p { font-size: 15px; font-weight: 300; color: var(--cream-dim); margin: 0; }

    .score-card { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.15); padding: 32px; margin-bottom: 40px; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    .score-item h4 { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); opacity: 0.6; margin-bottom: 10px; }
    .score-value { font-family: 'Cinzel', serif; font-size: 28px; color: var(--gold); margin-bottom: 4px; }
    .score-label { font-size: 14px; font-weight: 300; color: var(--cream-dim); }

    .readings-title { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 4px; text-transform: uppercase; color: var(--gold); opacity: 0.5; margin-bottom: 24px; }

    .reading-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-bottom: 60px; }
    .reading-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(212,175,55,0.1); padding: 28px 24px; }
    .reading-card.available { border-color: rgba(212,175,55,0.25); }
    .reading-card.complete { border-color: rgba(0,200,83,0.25); }
    .reading-card h3 { font-family: 'Cinzel', serif; font-size: 13px; letter-spacing: 1px; color: var(--gold); margin-bottom: 8px; }
    .reading-card .price { font-size: 13px; color: var(--cream-dim); margin-bottom: 14px; }
    .reading-card .desc { font-size: 14px; font-weight: 300; color: var(--cream-faint); line-height: 1.7; margin-bottom: 20px; }
    .status-badge { display: inline-block; font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; padding: 4px 10px; border-radius: 10px; margin-bottom: 14px; }
    .status-badge.complete { background: rgba(0,200,83,0.1); color: #69f0ae; border: 1px solid rgba(0,200,83,0.2); }
    .status-badge.generating { background: rgba(212,175,55,0.1); color: var(--gold); border: 1px solid rgba(212,175,55,0.2); }
    .status-badge.locked { background: rgba(255,255,255,0.04); color: var(--cream-faint); border: 1px solid rgba(255,255,255,0.08); }
    .btn-sm { display: inline-block; font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; padding: 12px 24px; text-decoration: none; background: rgba(212,175,55,0.1); border: 1px solid rgba(212,175,55,0.3); color: var(--gold); transition: all 0.3s; cursor: pointer; }
    .btn-sm:hover { background: rgba(212,175,55,0.2); border-color: var(--gold); }

    @media (max-width: 640px) {
      .score-card { grid-template-columns: 1fr; }
      .step-banner { flex-direction: column; gap: 12px; }
    }
  </style>
</head>
<body>
<?php include 'includes/nav.php'; ?>

<?php
require_once 'includes/auth.php';
require_login();

$client     = get_client();
$assessment = get_assessment();
$intake_done    = !empty($client['intake_complete']);
$assessment_done = $assessment !== null;

$score = $assessment ? intval($assessment['self_love_score']) : null;
$tier  = $score !== null ? get_self_love_tier($score) : null;
$attachment = $assessment['attachment_style'] ?? null;

// Load readings for this client
$db = get_db();
$readings_stmt = $db->prepare('SELECT * FROM readings WHERE client_id = ?');
$readings_stmt->execute([$_SESSION['client_id']]);
$readings = [];
foreach ($readings_stmt->fetchAll() as $r) {
    $readings[$r['reading_type']] = $r;
}

$first = htmlspecialchars($client['first_name'] ?? 'there');
?>

<div class="main">
  <div class="inner">
    <div class="welcome">
      <h1>Welcome, <em><?= $first ?></em></h1>
      <p>This is your portal. Your readings, your data, your map.</p>
    </div>

    <?php if (!$intake_done): ?>
    <div class="step-banner">
      <div class="step-icon">&#9432;</div>
      <div>
        <h3>Step 1: Complete Your Profile</h3>
        <p>Your readings are built from your birth data and name. Fill in your profile to unlock everything.</p>
      </div>
      <a href="/intake" class="btn-sm" style="flex-shrink:0;">Start Profile &rarr;</a>
    </div>
    <?php elseif (!$assessment_done): ?>
    <div class="step-banner">
      <div class="step-icon">&#9432;</div>
      <div>
        <h3>Step 2: Complete the Self-Love Assessment</h3>
        <p>24 questions. Takes about 5 minutes. Unlocks your readings.</p>
      </div>
      <a href="/assessment" class="btn-sm" style="flex-shrink:0;">Take Assessment &rarr;</a>
    </div>
    <?php else: ?>

    <div class="score-card">
      <div class="score-item">
        <h4>Self-Love Score</h4>
        <div class="score-value"><?= $score ?> <span style="font-size:16px;opacity:0.4">/ 85</span></div>
        <div class="score-label"><?= htmlspecialchars($tier) ?></div>
      </div>
      <div class="score-item">
        <h4>Attachment Style</h4>
        <div class="score-value" style="font-size:18px;line-height:1.3;"><?= htmlspecialchars($attachment ?? 'N/A') ?></div>
      </div>
    </div>

    <?php endif; ?>

    <?php if ($assessment_done): ?>
    <div class="readings-title">Your Readings</div>
    <div class="reading-grid">

      <!-- Name Frequency Reading -->
      <?php
      $nf = $readings['name_frequency'] ?? null;
      $nf_status = $nf['status'] ?? 'not_purchased';
      ?>
      <div class="reading-card <?= $nf_status === 'complete' ? 'complete' : ($nf_status === 'not_purchased' ? 'available' : '') ?>">
        <h3>Name Frequency Reading</h3>
        <div class="price">$10.99</div>
        <div class="desc">Every letter in your birth name carries a frequency. This reading decodes it from first letter to last.</div>
        <?php if ($nf_status === 'complete'): ?>
          <span class="status-badge complete">&#10003; Ready</span><br>
          <a href="/readings/<?= htmlspecialchars($nf['file_name']) ?>" target="_blank" class="btn-sm">Open Reading &rarr;</a>
        <?php elseif ($nf_status === 'generating'): ?>
          <span class="status-badge generating">Generating...</span>
          <br><a href="/reading-generating?id=<?= $nf['id'] ?>" class="btn-sm">Check Status</a>
        <?php else: ?>
          <a href="/purchase-reading?type=name_frequency" class="btn-sm">Purchase $10.99 &rarr;</a>
        <?php endif; ?>
      </div>

      <!-- Placeholder for future readings -->
      <div class="reading-card">
        <h3>Relational Name Frequency</h3>
        <div class="price">From $10.99</div>
        <div class="desc">Your name frequencies compared with someone else's. Shared, mirror, and growth patterns.</div>
        <span class="status-badge locked">Coming Next</span>
      </div>

      <div class="reading-card">
        <h3>Self-Love Language Reading</h3>
        <div class="price">$82</div>
        <div class="desc">How you give and receive love. Built from your chart, your score, and your name frequencies.</div>
        <span class="status-badge locked">Coming Soon</span>
      </div>

      <div class="reading-card">
        <h3>TCM Astrology Chakra</h3>
        <div class="price">$59</div>
        <div class="desc">Your birth chart through Traditional Chinese Medicine and chakra systems. Interactive wheel.</div>
        <span class="status-badge locked">Coming Soon</span>
      </div>

      <div class="reading-card">
        <h3>Soul Blueprint Decoder</h3>
        <div class="price">$77</div>
        <div class="desc">Six systems. One complete soul map. Numerology, astrology, Human Design, Hebrew, TCM, and chakra.</div>
        <span class="status-badge locked">Coming Soon</span>
      </div>

    </div>
    <?php else: ?>
    <div style="opacity:0.4;font-size:15px;font-weight:300;color:var(--cream-dim);margin-top:12px;">Complete the assessment above to unlock your readings.</div>
    <?php endif; ?>

  </div>
</div>

<?php include 'includes/footer.php'; ?>
</body>
</html>
