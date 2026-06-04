<?php
require_once __DIR__ . '/includes/admin-auth.php';
require_once __DIR__ . '/../includes/auth.php';
admin_require_login();

// Hebrew calc — load if available
if (file_exists(__DIR__ . '/../includes/hebrew-calc.php')) {
    include __DIR__ . '/../includes/hebrew-calc.php';
}

$client_id = intval($_GET['id'] ?? 0);
if (!$client_id) {
    header('Location: /admin/');
    exit;
}

$db = get_db();
$flash = '';
$flash_type = 'success';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    admin_verify_csrf();
    $action = $_POST['action'] ?? '';

    if ($action === 'update_client') {
        $db->prepare('UPDATE clients SET
            first_name=?, middle_name=?, last_name=?, maiden_name=?,
            dob=?, time_of_birth=?, timezone=?, place_of_birth=?,
            latitude=?, longitude=?, phone=?,
            career_field=?, career_expression=?, intake_complete=?
            WHERE id=?')->execute([
            trim($_POST['first_name'] ?? ''),
            trim($_POST['middle_name'] ?? ''),
            trim($_POST['last_name'] ?? ''),
            trim($_POST['maiden_name'] ?? ''),
            trim($_POST['dob'] ?? '') ?: null,
            trim($_POST['time_of_birth'] ?? '') ?: null,
            trim($_POST['timezone'] ?? '') ?: null,
            trim($_POST['place_of_birth'] ?? '') ?: null,
            trim($_POST['latitude'] ?? '') ?: null,
            trim($_POST['longitude'] ?? '') ?: null,
            trim($_POST['phone'] ?? ''),
            trim($_POST['career_field'] ?? ''),
            trim($_POST['career_expression'] ?? ''),
            isset($_POST['intake_complete']) ? 1 : 0,
            $client_id,
        ]);
        $flash = 'Client profile updated.';

    } elseif ($action === 'update_assessment') {
        $score = intval($_POST['self_love_score'] ?? 0);
        $att   = trim($_POST['attachment_style'] ?? '');
        $assess_id = intval($_POST['assessment_id'] ?? 0);
        if ($assess_id) {
            $db->prepare('UPDATE assessments SET self_love_score=?, attachment_style=? WHERE id=? AND client_id=?')
               ->execute([$score, $att, $assess_id, $client_id]);
        } else {
            $db->prepare('INSERT INTO assessments (client_id, self_love_score, attachment_style) VALUES (?,?,?)')
               ->execute([$client_id, $score, $att]);
        }
        $flash = 'Assessment updated.';

    } elseif ($action === 'mark_reading_paid') {
        $rtype = trim($_POST['reading_type'] ?? '');
        if ($rtype) {
            $exists = $db->prepare('SELECT id FROM readings WHERE client_id=? AND reading_type=?');
            $exists->execute([$client_id, $rtype]);
            if (!$exists->fetch()) {
                $db->prepare('INSERT INTO readings (client_id, reading_type, paid, amount_cents) VALUES (?,?,1,0)')
                   ->execute([$client_id, $rtype]);
            } else {
                $db->prepare('UPDATE readings SET paid=1 WHERE client_id=? AND reading_type=?')
                   ->execute([$client_id, $rtype]);
            }
        }
        $flash = 'Reading marked as paid.';

    } elseif ($action === 'delete_reading') {
        $rtype = trim($_POST['reading_type'] ?? '');
        $existing = $db->prepare('SELECT file_name FROM readings WHERE client_id=? AND reading_type=?');
        $existing->execute([$client_id, $rtype]);
        $r = $existing->fetch();
        if ($r && $r['file_name'] && file_exists(READINGS_DIR . $r['file_name'])) {
            unlink(READINGS_DIR . $r['file_name']);
        }
        $db->prepare('DELETE FROM readings WHERE client_id=? AND reading_type=?')->execute([$client_id, $rtype]);
        $flash = 'Reading record deleted.';
    }

    header('Location: /admin/client.php?id=' . $client_id . '&flash=' . urlencode($flash));
    exit;
}

if (isset($_GET['flash'])) {
    $flash = htmlspecialchars($_GET['flash']);
}

$client = $db->prepare('SELECT * FROM clients WHERE id=?');
$client->execute([$client_id]);
$client = $client->fetch();

if (!$client) {
    header('Location: /admin/');
    exit;
}

$assessment = $db->prepare('SELECT * FROM assessments WHERE client_id=? ORDER BY completed_at DESC LIMIT 1');
$assessment->execute([$client_id]);
$assessment = $assessment->fetch();

$readings = $db->prepare('SELECT * FROM readings WHERE client_id=?');
$readings->execute([$client_id]);
$readings_list = [];
foreach ($readings->fetchAll() as $r) {
    $readings_list[$r['reading_type']] = $r;
}

$full_name = trim(
    ($client['first_name'] ?? '') . ' ' .
    ($client['middle_name'] ? $client['middle_name'] . ' ' : '') .
    ($client['last_name'] ?? '')
);

$all_reading_types = [
    'name_frequency'       => ['label' => 'Name Frequency Reading',              'price' => '$10.99'],
    'relational_tier1'     => ['label' => 'Relational Name Frequency Tier 1',    'price' => '$10.99'],
    'self_love_language'   => ['label' => 'Self-Love Language Reading',           'price' => '$82'],
    'tcm_astrology_tier1'  => ['label' => 'TCM Astrology Chakra Tier 1',         'price' => '$59'],
    'soul_blueprint_tier1' => ['label' => 'Soul Blueprint Decoder Tier 1',       'price' => '$77'],
];

$attachment_options = [
    'Secure', 'Pure Anxious', 'Pure Avoidant', 'Pure Disorganized',
    'Disorganized Anxious Leaning', 'Disorganized Avoidant Leaning', 'True Disorganized Equal Split',
];

$q_labels = [
    'q1'  => 'Relationship with self',      'q2'  => 'When things go wrong',
    'q3'  => 'Emotional overwhelm',         'q4'  => 'Decision making',
    'q5'  => 'Emotional safety in childhood','q6' => 'When expressed emotions',
    'q7'  => 'Caregiver predictability',    'q8'  => 'Responsible for others emotions',
    'q9'  => 'In close relationships',      'q10' => 'When someone gets close',
    'q11' => 'When conflict happens',        'q12' => 'Most accurate statement',
    'q13' => 'When someone pulls away',     'q14' => 'Responding to vulnerability',
    'q15' => 'Belief about love',           'q16' => 'Receiving love/support',
    'q17' => 'When complimented',           'q18' => 'What drains energy',
    'q19' => 'After time with people',      'q20' => 'Ignoring own needs',
    'q21' => 'Self-care consistency',       'q22' => 'When emotionally triggered',
    'q23' => 'Willingness to face discomfort','q24'=> 'Hope from transformation',
];

// Auto-create client_calculations table and load calc row
try {
    $db->exec('CREATE TABLE IF NOT EXISTS client_calculations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        client_id INT NOT NULL,
        astrology_data MEDIUMTEXT DEFAULT NULL,
        human_design_data MEDIUMTEXT DEFAULT NULL,
        tier2_neuro MEDIUMTEXT DEFAULT NULL,
        tier2_clairs MEDIUMTEXT DEFAULT NULL,
        nd_profile_unlocked TINYINT(1) NOT NULL DEFAULT 0,
        calculated_at DATETIME DEFAULT NULL,
        updated_at DATETIME DEFAULT NULL,
        UNIQUE KEY uq_client (client_id)
    )');
} catch (Exception $e) {}

$calc = null;
try {
    $cq = $db->prepare('SELECT * FROM client_calculations WHERE client_id=?');
    $cq->execute([$client_id]);
    $calc = $cq->fetch() ?: null;
} catch (Exception $e) {}

$astro_data = $calc ? json_decode($calc['astrology_data'] ?? 'null', true) : null;
$hd_derived = $astro_data['summary']['derived'] ?? null;

// Load Hebrew responses
$hebrew_row = null;
$hebrew_responses = [];
try {
    $db->exec('CREATE TABLE IF NOT EXISTS hebrew_responses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        client_id INT NOT NULL,
        responses_json MEDIUMTEXT NOT NULL,
        completed_at DATETIME NOT NULL,
        UNIQUE KEY uq_client (client_id)
    )');
    $hq = $db->prepare('SELECT * FROM hebrew_responses WHERE client_id=?');
    $hq->execute([$client_id]);
    $hebrew_row = $hq->fetch() ?: null;
    if ($hebrew_row) {
        $hebrew_responses = json_decode($hebrew_row['responses_json'], true) ?: [];
    }
} catch (Exception $e) {}

// Run Hebrew calculation if client has full name and DOB
$hebrew_calc = null;
$dob_parts = null;
if ($client['dob']) {
    $dob_parts = explode('-', $client['dob']);
}
if (function_exists('run_hebrew_calculation') && $client['first_name'] && $client['last_name'] && $dob_parts && count($dob_parts) === 3) {
    try {
        $hebrew_calc = run_hebrew_calculation(
            $client['first_name'],
            $client['middle_name'] ?? '',
            $client['last_name'],
            intval($dob_parts[2]),
            intval($dob_parts[1]),
            intval($dob_parts[0])
        );
    } catch (Exception $e) { $hebrew_calc = null; }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><?= htmlspecialchars($full_name ?: 'Client') ?> | Admin</title>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --gold: #d4af37; --gold-light: #f0d060;
      --cream: #f5f0ff; --cream-dim: rgba(245,240,255,0.65); --cream-faint: rgba(245,240,255,0.35);
      --plum: #0f0520; --plum-mid: #1a0a2e; --plum-card: rgba(255,255,255,0.025);
      --magenta: #c2185b; --border: rgba(212,175,55,0.15); --green: #69f0ae;
    }
    body { background: var(--plum); color: var(--cream); font-family: 'Cormorant Garamond', serif; }

    /* SIDEBAR */
    .sidebar { position: fixed; top: 0; left: 0; bottom: 0; width: 220px; background: var(--plum-mid); border-right: 1px solid var(--border); padding: 32px 0; display: flex; flex-direction: column; z-index: 10; }
    .sidebar-brand { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); padding: 0 24px 28px; border-bottom: 1px solid var(--border); }
    .sidebar-brand span { display: block; font-size: 8px; letter-spacing: 2px; color: var(--cream-faint); margin-top: 4px; }
    .nav-item { display: block; padding: 12px 24px; font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: var(--cream-dim); text-decoration: none; transition: all 0.2s; border-left: 2px solid transparent; }
    .nav-item:hover { color: var(--gold); border-left-color: var(--gold); background: rgba(212,175,55,0.04); }

    /* MAIN */
    .main { margin-left: 220px; padding: 40px 48px; max-width: 1100px; }
    .breadcrumb { font-size: 13px; color: var(--cream-faint); margin-bottom: 24px; }
    .breadcrumb a { color: var(--gold); text-decoration: none; }
    .client-name { font-family: 'Cinzel', serif; font-size: 28px; font-weight: 400; color: var(--cream); margin-bottom: 6px; }
    .client-meta { font-size: 15px; color: var(--cream-faint); margin-bottom: 28px; line-height: 1.6; }

    /* ACTION BAR */
    .action-bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; padding: 16px 20px; background: rgba(212,175,55,0.04); border: 1px solid rgba(212,175,55,0.12); }
    #calcStatus { font-size: 13px; color: var(--gold); font-style: italic; }

    /* TIMEZONE SELECTOR */
    .tz-row { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
    .tz-row label { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: rgba(212,175,55,0.6); }
    .tz-row select { background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 14px; padding: 7px 12px; outline: none; }
    .tz-row select option { background: var(--plum-mid); }

    /* TABS */
    .tab-nav { display: flex; border-bottom: 1px solid rgba(212,175,55,0.15); margin-bottom: 28px; gap: 0; flex-wrap: wrap; }
    .tab-btn { padding: 11px 22px; background: none; border: none; border-bottom: 2px solid transparent; color: rgba(245,240,255,0.4); font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; cursor: pointer; transition: all 0.2s; margin-bottom: -1px; }
    .tab-btn.active { color: var(--gold); border-bottom-color: var(--gold); }
    .tab-btn:hover { color: var(--cream-dim); }
    .tab-panel { display: none; }
    .tab-panel.active { display: block; }

    /* SECTIONS */
    .section { background: var(--plum-card); border: 1px solid var(--border); padding: 32px; margin-bottom: 24px; }
    .section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(212,175,55,0.08); }
    .section-title { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); }
    .section-actions { display: flex; gap: 10px; }

    /* DATA GRID */
    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
    .data-label { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--cream-faint); padding: 11px 0; border-bottom: 1px solid rgba(212,175,55,0.05); }
    .data-value { font-size: 15px; font-weight: 300; color: var(--cream); padding: 11px 0 11px 16px; border-bottom: 1px solid rgba(212,175,55,0.05); }
    .data-value.empty { color: var(--cream-faint); font-style: italic; }

    /* FORMS */
    .edit-form { display: none; }
    .edit-form.open { display: block; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 20px; }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-group.full { grid-column: 1/-1; }
    .form-group label { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: rgba(212,175,55,0.6); }
    .form-group input,
    .form-group select,
    .form-group textarea { background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 15px; font-weight: 300; padding: 10px 12px; outline: none; transition: border-color 0.3s; width: 100%; }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: rgba(212,175,55,0.5); }
    .form-group select option { background: var(--plum-mid); }
    .form-group textarea { min-height: 80px; resize: vertical; }
    .form-actions { display: flex; gap: 12px; margin-top: 20px; }

    /* BUTTONS */
    .btn { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; padding: 10px 20px; cursor: pointer; transition: all 0.2s; text-decoration: none; display: inline-block; border: none; }
    .btn-gold { background: rgba(212,175,55,0.12); border: 1px solid rgba(212,175,55,0.3); color: var(--gold); }
    .btn-gold:hover { background: rgba(212,175,55,0.2); border-color: var(--gold); }
    .btn-solid { background: var(--gold); color: var(--plum); border: 1px solid var(--gold); }
    .btn-solid:hover { background: var(--gold-light); }
    .btn-magenta { background: rgba(194,24,91,0.15); border: 1px solid rgba(194,24,91,0.4); color: #f48fb1; }
    .btn-magenta:hover { background: rgba(194,24,91,0.25); }
    .btn-ghost { background: none; border: 1px solid rgba(255,255,255,0.1); color: var(--cream-faint); }
    .btn-ghost:hover { border-color: rgba(255,255,255,0.25); color: var(--cream-dim); }
    .btn-green { background: rgba(0,200,83,0.1); border: 1px solid rgba(0,200,83,0.3); color: var(--green); }
    .btn-green:hover { background: rgba(0,200,83,0.2); }
    .btn-danger { background: rgba(194,24,91,0.1); border: 1px solid rgba(194,24,91,0.3); color: #f48fb1; }
    .btn-danger:hover { background: rgba(194,24,91,0.2); }
    .btn:disabled { opacity: 0.4; cursor: default; }

    /* SCORE DISPLAY */
    .score-big { font-family: 'Cinzel', serif; font-size: 48px; color: var(--gold); line-height: 1; }
    .score-tier { font-size: 16px; font-weight: 300; color: var(--cream-dim); margin-top: 6px; }
    .att-style { font-family: 'Cinzel', serif; font-size: 18px; color: var(--cream); margin-top: 16px; }

    /* ANSWERS GRID */
    .answers-toggle { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--gold); cursor: pointer; border: none; background: none; padding: 0; }
    .answers-grid { display: none; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 20px; }
    .answers-grid.open { display: grid; }
    .answer-item { background: rgba(255,255,255,0.02); border: 1px solid rgba(212,175,55,0.06); padding: 10px 14px; }
    .answer-item .q-label { font-family: 'Cinzel', serif; font-size: 8px; letter-spacing: 1px; color: var(--cream-faint); margin-bottom: 4px; }
    .answer-item .q-val { font-size: 14px; color: var(--cream-dim); }

    /* READINGS */
    .reading-item { border: 1px solid var(--border); padding: 24px; margin-bottom: 12px; display: flex; align-items: center; gap: 24px; }
    .reading-item:last-child { margin-bottom: 0; }
    .reading-info { flex: 1; }
    .reading-info h3 { font-family: 'Cinzel', serif; font-size: 13px; letter-spacing: 1px; color: var(--cream); margin-bottom: 4px; }
    .reading-info p { font-size: 13px; color: var(--cream-faint); }
    .reading-status { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; padding: 5px 12px; border-radius: 10px; }
    .status-complete { background: rgba(0,200,83,0.1); color: var(--green); border: 1px solid rgba(0,200,83,0.2); }
    .status-generating { background: rgba(212,175,55,0.1); color: var(--gold); border: 1px solid rgba(212,175,55,0.2); }
    .status-error { background: rgba(194,24,91,0.1); color: #f48fb1; border: 1px solid rgba(194,24,91,0.2); }
    .status-none { background: rgba(255,255,255,0.04); color: var(--cream-faint); border: 1px solid rgba(255,255,255,0.08); }
    .gen-status { font-size: 13px; color: var(--cream-faint); font-style: italic; margin-top: 8px; min-height: 20px; }

    /* TIER 2 TEXTAREAS */
    .tier2-area { width: 100%; min-height: 160px; resize: vertical; background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 15px; font-weight: 300; padding: 12px; outline: none; }
    .tier2-area:focus { border-color: rgba(212,175,55,0.5); }
    .tier2-saved { font-size: 13px; color: var(--green); font-style: italic; min-height: 20px; margin-top: 6px; }

    /* EMPTY STATE */
    .empty-state { color: var(--cream-faint); font-style: italic; font-size: 15px; padding: 24px 0; }

    /* FLASH */
    .flash { padding: 14px 18px; margin-bottom: 20px; font-size: 14px; }
    .flash.success { background: rgba(0,200,83,0.1); border: 1px solid rgba(0,200,83,0.3); color: var(--green); }
    .flash.error { background: rgba(194,24,91,0.1); border: 1px solid rgba(194,24,91,0.3); color: #f48fb1; }

    /* CALC TIMESTAMP */
    .calc-ts { font-size: 12px; color: var(--cream-faint); font-style: italic; margin-top: 20px; }

    @media (max-width: 800px) {
      .data-grid, .form-grid, .answers-grid { grid-template-columns: 1fr; }
      .reading-item { flex-direction: column; align-items: flex-start; }
      .tab-btn { padding: 10px 14px; font-size: 9px; }
    }
  </style>
</head>
<body>

<aside class="sidebar">
  <div class="sidebar-brand">soulReady<span>Admin Panel</span></div>
  <nav style="padding:24px 0;">
    <a href="/admin/" class="nav-item">&#8592; All Clients</a>
  </nav>
</aside>

<div class="main">

  <div class="breadcrumb"><a href="/admin/">Clients</a> &rsaquo; <?= htmlspecialchars($full_name ?: $client['email']) ?></div>

  <?php if ($flash): ?>
    <div class="flash success"><?= $flash ?></div>
  <?php endif; ?>

  <div class="client-name"><?= htmlspecialchars($full_name ?: '(Name not set)') ?></div>
  <div class="client-meta">
    <?= htmlspecialchars($client['email']) ?>
    <?php if ($client['dob']): ?>&nbsp;&middot;&nbsp; DOB: <?= htmlspecialchars($client['dob']) ?><?php endif; ?>
    <?php if ($client['time_of_birth']): ?>&nbsp;&middot;&nbsp; <?= htmlspecialchars($client['time_of_birth']) ?><?php endif; ?>
    <?php if ($client['place_of_birth']): ?>&nbsp;&middot;&nbsp; <?= htmlspecialchars($client['place_of_birth']) ?><?php endif; ?>
    <br>Client since <?= date('F j, Y', strtotime($client['created_at'])) ?>
  </div>

  <!-- ACTION BAR -->
  <div class="action-bar">
    <button class="btn btn-solid" onclick="autoCalculate()">Auto-Calculate</button>
    <button class="btn btn-magenta" onclick="generateReading('name_frequency', <?= $client_id ?>)">Generate Name Frequency</button>
    <span id="calcStatus"></span>
  </div>

  <!-- TIMEZONE SELECTOR -->
  <div class="tz-row">
    <label for="tzSelect">Birth Timezone &mdash; set before Auto-Calculate</label>
    <select id="tzSelect">
      <option value="-12">UTC-12 (Baker Island)</option>
      <option value="-11">UTC-11 (Samoa)</option>
      <option value="-10">UTC-10 (Hawaii)</option>
      <option value="-9">UTC-9 (Alaska)</option>
      <option value="-8">UTC-8 (Pacific)</option>
      <option value="-7" <?= (!$client['timezone'] || str_contains($client['timezone'] ?? '', 'Mountain') || str_contains($client['timezone'] ?? '', 'Denver') || str_contains($client['timezone'] ?? '', 'Hobbs') || $client['timezone'] === 'America/Denver') ? 'selected' : '' ?>>UTC-7 (Mountain)</option>
      <option value="-6" <?= str_contains($client['timezone'] ?? '', 'Chicago') || str_contains($client['timezone'] ?? '', 'Central') ? 'selected' : '' ?>>UTC-6 (Central)</option>
      <option value="-5" <?= str_contains($client['timezone'] ?? '', 'New_York') || str_contains($client['timezone'] ?? '', 'Eastern') ? 'selected' : '' ?>>UTC-5 (Eastern)</option>
      <option value="-4">UTC-4 (Atlantic)</option>
      <option value="-3">UTC-3 (Argentina)</option>
      <option value="-2">UTC-2 (South Georgia)</option>
      <option value="-1">UTC-1 (Azores)</option>
      <option value="0">UTC+0 (London/GMT)</option>
      <option value="1">UTC+1 (Central Europe)</option>
      <option value="2">UTC+2 (Eastern Europe)</option>
      <option value="3">UTC+3 (Moscow)</option>
      <option value="4">UTC+4 (Dubai)</option>
      <option value="5">UTC+5 (Pakistan)</option>
      <option value="5.5">UTC+5:30 (India)</option>
      <option value="6">UTC+6 (Bangladesh)</option>
      <option value="7">UTC+7 (Bangkok)</option>
      <option value="8">UTC+8 (Singapore/Beijing)</option>
      <option value="9">UTC+9 (Tokyo)</option>
      <option value="9.5">UTC+9:30 (Adelaide)</option>
      <option value="10">UTC+10 (Sydney)</option>
      <option value="11">UTC+11 (Solomon Islands)</option>
      <option value="12">UTC+12 (Auckland)</option>
    </select>
  </div>

  <!-- TAB NAVIGATION -->
  <div class="tab-nav">
    <button class="tab-btn active" data-tab="raw" onclick="showTab('raw')">Raw Data</button>
    <button class="tab-btn" data-tab="astrology" onclick="showTab('astrology')">Astrology</button>
    <button class="tab-btn" data-tab="hd" onclick="showTab('hd')">Human Design</button>
    <button class="tab-btn" data-tab="reading" onclick="showTab('reading')">Reading</button>
    <button class="tab-btn" data-tab="tier2" onclick="showTab('tier2')">Tier 2</button>
    <button class="tab-btn" data-tab="nd" onclick="showTab('nd')">ND Profile</button>
    <button class="tab-btn" data-tab="hebrew" onclick="showTab('hebrew')">Hebrew</button>
  </div>

  <!-- ============================================================ -->
  <!-- TAB 1: RAW DATA -->
  <!-- ============================================================ -->
  <div class="tab-panel active" id="tab-raw">

    <!-- CLIENT PROFILE -->
    <div class="section">
      <div class="section-head">
        <div class="section-title">Client Profile</div>
        <div class="section-actions">
          <button class="btn btn-gold" onclick="toggleEdit('profileEdit')">Edit Profile</button>
        </div>
      </div>

      <div id="profileDisplay" class="data-grid">
        <?php
        $profile_fields = [
            'First Name'      => $client['first_name'],
            'Middle Name'     => $client['middle_name'],
            'Last Name'       => $client['last_name'],
            'Maiden Name'     => $client['maiden_name'],
            'Date of Birth'   => $client['dob'],
            'Time of Birth'   => $client['time_of_birth'],
            'Timezone'        => $client['timezone'],
            'Place of Birth'  => $client['place_of_birth'],
            'Latitude'        => $client['latitude'],
            'Longitude'       => $client['longitude'],
            'Phone'           => $client['phone'],
            'Career Field'    => $client['career_field'],
            'Career Expression' => $client['career_expression'],
            'Medical Device'  => $client['medical_device'] ?? null,
            'Intake Complete' => $client['intake_complete'] ? 'Yes' : 'No',
        ];
        foreach ($profile_fields as $label => $val): ?>
          <div class="data-label"><?= htmlspecialchars($label) ?></div>
          <div class="data-value <?= $val ? '' : 'empty' ?>"><?= $val ? htmlspecialchars((string)$val) : 'Not set' ?></div>
        <?php endforeach; ?>
      </div>

      <form method="POST" id="profileEdit" class="edit-form">
        <input type="hidden" name="csrf_token" value="<?= admin_csrf() ?>">
        <input type="hidden" name="action" value="update_client">
        <div class="form-grid">
          <div class="form-group"><label>First Name</label><input type="text" name="first_name" value="<?= htmlspecialchars($client['first_name'] ?? '') ?>"></div>
          <div class="form-group"><label>Middle Name</label><input type="text" name="middle_name" value="<?= htmlspecialchars($client['middle_name'] ?? '') ?>"></div>
          <div class="form-group"><label>Last Name</label><input type="text" name="last_name" value="<?= htmlspecialchars($client['last_name'] ?? '') ?>"></div>
          <div class="form-group"><label>Maiden Name</label><input type="text" name="maiden_name" value="<?= htmlspecialchars($client['maiden_name'] ?? '') ?>"></div>
          <div class="form-group"><label>Date of Birth</label><input type="date" name="dob" value="<?= htmlspecialchars($client['dob'] ?? '') ?>"></div>
          <div class="form-group"><label>Time of Birth</label><input type="time" name="time_of_birth" value="<?= htmlspecialchars($client['time_of_birth'] ?? '') ?>"></div>
          <div class="form-group"><label>Place of Birth</label><input type="text" name="place_of_birth" value="<?= htmlspecialchars($client['place_of_birth'] ?? '') ?>"></div>
          <div class="form-group"><label>Timezone</label><input type="text" name="timezone" value="<?= htmlspecialchars($client['timezone'] ?? '') ?>" placeholder="e.g. America/Chicago"></div>
          <div class="form-group"><label>Latitude</label><input type="text" name="latitude" value="<?= htmlspecialchars($client['latitude'] ?? '') ?>"></div>
          <div class="form-group"><label>Longitude</label><input type="text" name="longitude" value="<?= htmlspecialchars($client['longitude'] ?? '') ?>"></div>
          <div class="form-group"><label>Phone</label><input type="text" name="phone" value="<?= htmlspecialchars($client['phone'] ?? '') ?>"></div>
          <div class="form-group"><label>Career Field / Title</label><input type="text" name="career_field" value="<?= htmlspecialchars($client['career_field'] ?? '') ?>"></div>
          <div class="form-group full"><label>Career Expression</label><textarea name="career_expression"><?= htmlspecialchars($client['career_expression'] ?? '') ?></textarea></div>
          <div class="form-group">
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
              <input type="checkbox" name="intake_complete" value="1" <?= $client['intake_complete'] ? 'checked' : '' ?> style="width:auto;padding:0;">
              Intake Complete
            </label>
          </div>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-solid">Save Changes</button>
          <button type="button" class="btn btn-ghost" onclick="toggleEdit('profileEdit')">Cancel</button>
        </div>
      </form>
    </div>

    <!-- SELF-LOVE ASSESSMENT -->
    <div class="section">
      <div class="section-head">
        <div class="section-title">Self-Love Assessment</div>
        <div class="section-actions">
          <button class="btn btn-gold" onclick="toggleEdit('assessEdit')">Override</button>
        </div>
      </div>

      <?php if ($assessment): ?>
        <div style="display:flex;align-items:baseline;gap:32px;flex-wrap:wrap;margin-bottom:24px;">
          <div>
            <div class="score-big"><?= intval($assessment['self_love_score']) ?></div>
            <div style="font-size:13px;color:var(--cream-faint);">out of 85</div>
            <div class="score-tier"><?= htmlspecialchars(get_self_love_tier(intval($assessment['self_love_score']))) ?></div>
          </div>
          <div>
            <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--cream-faint);margin-bottom:6px;">Attachment Style</div>
            <div class="att-style"><?= htmlspecialchars($assessment['attachment_style'] ?? 'Not classified') ?></div>
          </div>
          <?php
          $counts = json_decode($assessment['attachment_counts'] ?? '{}', true);
          if ($counts):
          ?>
          <div>
            <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--cream-faint);margin-bottom:8px;">Attachment Counts</div>
            <div style="font-size:14px;color:var(--cream-dim);line-height:1.8;">
              S: <?= intval($counts['S'] ?? 0) ?> &nbsp; A: <?= intval($counts['A'] ?? 0) ?> &nbsp; V: <?= intval($counts['V'] ?? 0) ?> &nbsp; D: <?= intval($counts['D'] ?? 0) ?>
            </div>
          </div>
          <?php endif; ?>
          <?php
          $readiness = null;
          if ($assessment) {
              $raw_answers = json_decode($assessment['answers'] ?? '{}', true);
              $readiness = $raw_answers['q23'] ?? null;
          }
          if ($readiness !== null):
          ?>
          <div>
            <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--cream-faint);margin-bottom:6px;">Readiness Score (Q23)</div>
            <div style="font-size:22px;font-family:'Cinzel',serif;color:var(--cream);"><?= htmlspecialchars((string)$readiness) ?></div>
          </div>
          <?php endif; ?>
        </div>

        <?php
        $answers = json_decode($assessment['answers'] ?? '{}', true);
        if ($answers):
        ?>
        <button class="answers-toggle" onclick="toggleAnswers()">Show All 24 Answers &#9660;</button>
        <div class="answers-grid" id="answersGrid">
          <?php foreach ($q_labels as $key => $label): ?>
            <div class="answer-item">
              <div class="q-label"><?= htmlspecialchars($label) ?></div>
              <div class="q-val"><?= htmlspecialchars($answers[$key] ?? '--') ?></div>
            </div>
          <?php endforeach; ?>
        </div>
        <?php endif; ?>

      <?php else: ?>
        <div class="empty-state">No assessment completed yet.</div>
      <?php endif; ?>

      <form method="POST" id="assessEdit" class="edit-form" style="margin-top:20px;">
        <input type="hidden" name="csrf_token" value="<?= admin_csrf() ?>">
        <input type="hidden" name="action" value="update_assessment">
        <input type="hidden" name="assessment_id" value="<?= intval($assessment['id'] ?? 0) ?>">
        <div class="form-grid">
          <div class="form-group">
            <label>Self-Love Score (0-85)</label>
            <input type="number" name="self_love_score" min="0" max="85" value="<?= intval($assessment['self_love_score'] ?? 0) ?>">
          </div>
          <div class="form-group">
            <label>Attachment Style</label>
            <select name="attachment_style">
              <?php foreach ($attachment_options as $opt): ?>
                <option value="<?= htmlspecialchars($opt) ?>" <?= ($assessment['attachment_style'] ?? '') === $opt ? 'selected' : '' ?>><?= htmlspecialchars($opt) ?></option>
              <?php endforeach; ?>
            </select>
          </div>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-solid">Save Override</button>
          <button type="button" class="btn btn-ghost" onclick="toggleEdit('assessEdit')">Cancel</button>
        </div>
      </form>
    </div>

  </div><!-- /tab-raw -->

  <!-- ============================================================ -->
  <!-- TAB 2: ASTROLOGY -->
  <!-- ============================================================ -->
  <div class="tab-panel" id="tab-astrology">
    <div class="section">
      <div class="section-head">
        <div class="section-title">Birth Chart Data</div>
      </div>

      <?php if (!$astro_data): ?>
        <div class="empty-state">No chart data yet. Click Auto-Calculate to generate chart data.</div>
      <?php else:
        $birth_planets = $astro_data['birth']['planet_positions'] ?? [];
        $houses        = $astro_data['birth']['whole_sign_houses'] ?? [];
        $rising_sign   = $houses[0]['sign'] ?? null;

        // Build a keyed lookup by planet name
        $planet_map = [];
        foreach ($birth_planets as $p) {
            $planet_map[$p['planet']] = $p;
        }

        $planet_order = [
            'Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn',
            'Uranus','Neptune','Pluto','North Node','South Node','Chiron',
            'Black Moon Lilith','Part of Fortune','Ascendant','Midheaven','Vertex',
        ];
      ?>
        <div class="data-grid">
          <?php if ($rising_sign): ?>
            <div class="data-label">Rising Sign</div>
            <div class="data-value"><?= htmlspecialchars($rising_sign) ?></div>
          <?php endif; ?>

          <?php foreach ($planet_order as $pname):
            $p = $planet_map[$pname] ?? null;
            if (!$p) continue;
            $deg  = isset($p['degree']) ? floor($p['degree']) . '&deg;' : '';
            $rx   = !empty($p['retrograde']) ? ' Rx' : '';
            $house = isset($p['house']) ? ' H' . $p['house'] : '';
            $sign = $p['sign'] ?? '';
          ?>
            <div class="data-label"><?= htmlspecialchars($pname) ?></div>
            <div class="data-value"><?= htmlspecialchars($sign) ?> <?= $deg ?><?= $rx ?><?= htmlspecialchars($house) ?></div>
          <?php endforeach; ?>
        </div>

        <?php if ($calc && $calc['calculated_at']): ?>
          <div class="calc-ts">Calculated at: <?= htmlspecialchars($calc['calculated_at']) ?></div>
        <?php endif; ?>

      <?php endif; ?>
    </div>
  </div><!-- /tab-astrology -->

  <!-- ============================================================ -->
  <!-- TAB 3: HUMAN DESIGN -->
  <!-- ============================================================ -->
  <div class="tab-panel" id="tab-hd">
    <div class="section">
      <div class="section-head">
        <div class="section-title">Human Design</div>
      </div>

      <?php if (!$hd_derived): ?>
        <div class="empty-state">No Human Design data yet. Click Auto-Calculate to generate.</div>
      <?php else:
        $design_date = $astro_data['summary']['design']['date'] ?? null;
        $inc_cross   = $astro_data['summary']['incarnation_cross'] ?? null;

        $hd_fields = [
            'Type'             => $hd_derived['type'] ?? null,
            'Strategy'         => $hd_derived['strategy'] ?? null,
            'Authority'        => $hd_derived['inner_authority'] ?? null,
            'Profile'          => $hd_derived['profile']['profile'] ?? ($hd_derived['profile'] ?? null),
            'Definition'       => $hd_derived['definition'] ?? null,
            'Incarnation Cross'=> $inc_cross,
            'Design Date'      => $design_date,
            'Defined Centers'  => is_array($hd_derived['defined_centers'] ?? null)
                                    ? implode(', ', $hd_derived['defined_centers'])
                                    : ($hd_derived['defined_centers'] ?? null),
            'Undefined Centers'=> is_array($hd_derived['undefined_centers'] ?? null)
                                    ? implode(', ', $hd_derived['undefined_centers'])
                                    : ($hd_derived['undefined_centers'] ?? null),
            'Active Channels'  => is_array($hd_derived['active_channels'] ?? null)
                                    ? implode(', ', $hd_derived['active_channels'])
                                    : ($hd_derived['active_channels'] ?? null),
            'Active Gates'     => is_array($hd_derived['active_gates'] ?? null)
                                    ? implode(', ', $hd_derived['active_gates'])
                                    : ($hd_derived['active_gates'] ?? null),
            'Digestion'        => $hd_derived['digestion'] ?? null,
            'Environment'      => $hd_derived['environment'] ?? null,
            'Design Sense'     => $hd_derived['design_sense'] ?? null,
        ];
      ?>
        <div class="data-grid">
          <?php foreach ($hd_fields as $label => $val): ?>
            <div class="data-label"><?= htmlspecialchars($label) ?></div>
            <div class="data-value <?= $val ? '' : 'empty' ?>"><?= $val ? htmlspecialchars((string)$val) : 'Not set' ?></div>
          <?php endforeach; ?>
        </div>

        <?php if ($calc && $calc['calculated_at']): ?>
          <div class="calc-ts">Calculated at: <?= htmlspecialchars($calc['calculated_at']) ?></div>
        <?php endif; ?>

      <?php endif; ?>
    </div>
  </div><!-- /tab-hd -->

  <!-- ============================================================ -->
  <!-- TAB 4: READING -->
  <!-- ============================================================ -->
  <div class="tab-panel" id="tab-reading">
    <div class="section">
      <div class="section-head">
        <div class="section-title">Readings</div>
      </div>

      <?php foreach ($all_reading_types as $rtype => $rinfo):
        $r      = $readings_list[$rtype] ?? null;
        $status = $r['status'] ?? 'not_purchased';
        $paid   = $r['paid'] ?? 0;
      ?>
      <div class="reading-item" id="reading-<?= htmlspecialchars($rtype) ?>">
        <div class="reading-info">
          <h3><?= htmlspecialchars($rinfo['label']) ?></h3>
          <p><?= htmlspecialchars($rinfo['price']) ?>
            <?php if ($r): ?>
              &nbsp;&middot;&nbsp; Paid: <?= $paid ? 'Yes' : 'No' ?>
              <?php if ($r['created_at']): ?>&nbsp;&middot;&nbsp; <?= date('M j, Y', strtotime($r['created_at'])) ?><?php endif; ?>
              <?php if ($r['paypal_order_id']): ?>&nbsp;&middot;&nbsp; PayPal: <?= htmlspecialchars($r['paypal_order_id']) ?><?php endif; ?>
            <?php endif; ?>
          </p>
          <div class="gen-status" id="genstatus-<?= htmlspecialchars($rtype) ?>"></div>
        </div>

        <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
          <?php if ($status === 'complete'): ?>
            <span class="reading-status status-complete">&#10003; Complete</span>
            <a href="/readings/<?= htmlspecialchars($r['file_name']) ?>" target="_blank" class="btn btn-green">View Reading</a>
            <?php if ($rtype === 'name_frequency'): ?>
            <button class="btn btn-gold" onclick="generateReading('<?= htmlspecialchars($rtype) ?>', <?= $client_id ?>)">Re-Generate</button>
            <?php endif; ?>
            <form method="POST" style="display:inline" onsubmit="return confirm('Delete this reading? Cannot be undone.');">
              <input type="hidden" name="csrf_token" value="<?= admin_csrf() ?>">
              <input type="hidden" name="action" value="delete_reading">
              <input type="hidden" name="reading_type" value="<?= htmlspecialchars($rtype) ?>">
              <button type="submit" class="btn btn-danger">Delete</button>
            </form>

          <?php elseif ($status === 'generating'): ?>
            <span class="reading-status status-generating">Generating...</span>
            <button class="btn btn-gold" onclick="pollReadingStatus('<?= htmlspecialchars($rtype) ?>', <?= intval($r['id']) ?>, <?= $client_id ?>)">Check Status</button>

          <?php elseif ($status === 'error'): ?>
            <span class="reading-status status-error">Error</span>
            <span style="font-size:12px;color:#f48fb1;"><?= htmlspecialchars($r['error_message'] ?? '') ?></span>
            <?php if ($rtype === 'name_frequency'): ?>
            <button class="btn btn-gold" onclick="generateReading('<?= htmlspecialchars($rtype) ?>', <?= $client_id ?>)">Retry</button>
            <?php endif; ?>

          <?php else: ?>
            <span class="reading-status status-none"><?= $paid ? 'Paid / Not Generated' : 'Not Purchased' ?></span>
            <?php if (!$paid): ?>
            <form method="POST" style="display:inline">
              <input type="hidden" name="csrf_token" value="<?= admin_csrf() ?>">
              <input type="hidden" name="action" value="mark_reading_paid">
              <input type="hidden" name="reading_type" value="<?= htmlspecialchars($rtype) ?>">
              <button type="submit" class="btn btn-ghost">Mark as Paid</button>
            </form>
            <?php endif; ?>
            <?php if ($rtype === 'name_frequency' && ($paid || !$r)): ?>
            <button class="btn btn-gold" onclick="generateReading('<?= htmlspecialchars($rtype) ?>', <?= $client_id ?>)">Generate Now</button>
            <?php endif; ?>
          <?php endif; ?>
        </div>
      </div>
      <?php endforeach; ?>

    </div>
  </div><!-- /tab-reading -->

  <!-- ============================================================ -->
  <!-- TAB 5: TIER 2 -->
  <!-- ============================================================ -->
  <div class="tab-panel" id="tab-tier2">
    <div class="section">
      <div class="section-head">
        <div class="section-title">Tier 2 Notes</div>
      </div>

      <div style="margin-bottom:28px;">
        <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:rgba(212,175,55,0.6);margin-bottom:10px;">Neurodivergence Findings</div>
        <textarea id="tier2_tier2_neuro" class="tier2-area"><?= htmlspecialchars($calc['tier2_neuro'] ?? '') ?></textarea>
        <div style="display:flex;align-items:center;gap:12px;margin-top:10px;">
          <button class="btn btn-gold" onclick="saveTier2('tier2_neuro')">Save</button>
          <span id="saved_tier2_neuro" class="tier2-saved"></span>
        </div>
      </div>

      <div>
        <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:rgba(212,175,55,0.6);margin-bottom:10px;">Clairs Connection</div>
        <textarea id="tier2_tier2_clairs" class="tier2-area"><?= htmlspecialchars($calc['tier2_clairs'] ?? '') ?></textarea>
        <div style="display:flex;align-items:center;gap:12px;margin-top:10px;">
          <button class="btn btn-gold" onclick="saveTier2('tier2_clairs')">Save</button>
          <span id="saved_tier2_clairs" class="tier2-saved"></span>
        </div>
      </div>
    </div>
  </div><!-- /tab-tier2 -->

  <!-- ============================================================ -->
  <!-- TAB 6: ND PROFILE -->
  <!-- ============================================================ -->
  <div class="tab-panel" id="tab-nd">
    <div class="section">
      <div class="section-head">
        <div class="section-title">ND Wiring Pattern Profile</div>
      </div>

      <?php if (!$astro_data): ?>
        <div class="empty-state">Wiring pattern profile requires chart data. Run Auto-Calculate first, then this tab will populate.</div>
      <?php else: ?>
        <div class="empty-state">Chart calculated. ND Pattern detection coming in next build.</div>
      <?php endif; ?>
    </div>
  </div><!-- /tab-nd -->

  <!-- ============================================================ -->
  <!-- TAB 7: HEBREW -->
  <!-- ============================================================ -->
  <div class="tab-panel" id="tab-hebrew">

    <!-- CALCULATION RESULTS -->
    <div class="section">
      <div class="section-head">
        <div class="section-title">Hebrew Metatron's Cube Calculation</div>
      </div>

      <?php if (!$hebrew_calc): ?>
        <div class="empty-state">
          <?php
          $heb_file = __DIR__ . '/../includes/hebrew-calc.php';
          if (!file_exists($heb_file)) {
              echo 'DEBUG: hebrew-calc.php not found. Looking for it at: ' . htmlspecialchars($heb_file);
          } elseif (!function_exists('run_hebrew_calculation')) {
              echo 'DEBUG: File found but function not loaded. PHP may have a parse error in hebrew-calc.php.';
          } elseif (!$client['first_name'] || !$client['last_name']) {
              echo 'DEBUG: Missing first or last name.';
          } elseif (!$dob_parts || count($dob_parts) !== 3) {
              echo 'DEBUG: DOB missing or not in expected format. dob=' . htmlspecialchars($client['dob'] ?? 'null');
          } else {
              echo 'DEBUG: All inputs present but run_hebrew_calculation returned null. Possible exception.';
          }
          ?>
        </div>
      <?php else: ?>

        <?php
        $element_colors = [
            'Fire'  => '#FF6B35',
            'Water' => '#4FC3F7',
            'Earth' => '#81C784',
            'Air'   => '#CE93D8',
            'Void'  => 'rgba(245,240,255,0.3)',
        ];
        $element_icons = ['Fire' => '&#128293;', 'Water' => '&#128167;', 'Earth' => '&#127793;', 'Air' => '&#127788;', 'Void' => '&#11088;'];
        ?>

        <!-- SUMMARY ROW -->
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px;margin-bottom:28px;">
          <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(212,175,55,0.1);padding:18px;">
            <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--cream-faint);margin-bottom:8px;">Dominant Element</div>
            <div style="font-family:'Cinzel',serif;font-size:18px;color:<?= $element_colors[$hebrew_calc['dominant_element']] ?? 'var(--cream)' ?>;">
              <?= $element_icons[$hebrew_calc['dominant_element']] ?? '' ?> <?= htmlspecialchars($hebrew_calc['dominant_element'] ?? 'N/A') ?>
            </div>
          </div>
          <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(212,175,55,0.1);padding:18px;">
            <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--cream-faint);margin-bottom:8px;">Elemental Wounds</div>
            <div style="font-size:15px;font-weight:300;color:var(--cream);">
              <?php if ($hebrew_calc['elemental_wounds']): ?>
                <?= htmlspecialchars(implode(', ', $hebrew_calc['elemental_wounds'])) ?>
              <?php else: ?>
                <span style="color:var(--green);">None</span>
              <?php endif; ?>
            </div>
          </div>
          <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(212,175,55,0.1);padding:18px;">
            <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--cream-faint);margin-bottom:8px;">Convergence Points</div>
            <div style="font-size:15px;font-weight:300;color:var(--cream);">
              <?= $hebrew_calc['convergence_points'] ? htmlspecialchars(implode(', ', $hebrew_calc['convergence_points'])) : 'None' ?>
            </div>
          </div>
          <?php foreach ($hebrew_calc['element_counts'] as $el => $cnt): ?>
          <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(212,175,55,0.06);padding:18px;">
            <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--cream-faint);margin-bottom:8px;"><?= htmlspecialchars($el) ?></div>
            <div style="font-family:'Cinzel',serif;font-size:22px;color:<?= $element_colors[$el] ?? 'var(--cream)' ?>;"><?= intval($cnt) ?></div>
          </div>
          <?php endforeach; ?>
        </div>

        <!-- CONVERGENCE DETAILS -->
        <?php if ($hebrew_calc['convergence_details']): ?>
        <div style="margin-bottom:28px;">
          <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:rgba(212,175,55,0.5);margin-bottom:14px;">Convergence Power Points</div>
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;">
            <?php foreach ($hebrew_calc['convergence_details'] as $cp): ?>
            <div style="background:rgba(212,175,55,0.05);border:1px solid rgba(212,175,55,0.2);padding:16px;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="font-family:'Cinzel',serif;font-size:22px;color:var(--gold);"><?= intval($cp['position']) ?></span>
                <div>
                  <div style="font-family:'Cinzel',serif;font-size:11px;letter-spacing:1px;color:var(--cream);"><?= htmlspecialchars($cp['name'] ?? '') ?></div>
                  <div style="font-size:11px;color:<?= $element_colors[$cp['element'] ?? ''] ?? 'var(--cream-faint)' ?>;"><?= htmlspecialchars($cp['element'] ?? '') ?><?= !empty($cp['is_fibonacci']) ? ' &nbsp;&#11088; Fibonacci' : '' ?></div>
                </div>
              </div>
              <div style="font-size:13px;font-weight:300;color:var(--cream-dim);line-height:1.6;"><?= htmlspecialchars($cp['meaning'] ?? '') ?></div>
            </div>
            <?php endforeach; ?>
          </div>
        </div>
        <?php endif; ?>

        <!-- LAYER 1 (NAME) POSITIONS -->
        <div style="margin-bottom:28px;">
          <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:rgba(212,175,55,0.5);margin-bottom:14px;">
            Layer 1 &mdash; Name Activations (<?= count($hebrew_calc['layer1_positions']) ?> positions)
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;">
            <?php foreach ($hebrew_calc['layer1_positions'] as $lp): ?>
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(212,175,55,0.1);padding:10px 14px;min-width:80px;">
              <div style="font-family:'Cinzel',serif;font-size:16px;color:var(--gold);"><?= intval($lp['position']) ?></div>
              <div style="font-size:12px;color:var(--cream-dim);"><?= htmlspecialchars($lp['name'] ?? '') ?></div>
              <div style="font-size:11px;color:<?= $element_colors[$lp['element'] ?? ''] ?? 'var(--cream-faint)' ?>;"><?= htmlspecialchars($lp['element'] ?? '') ?></div>
              <?php if (!empty($lp['is_fibonacci'])): ?><div style="font-size:10px;color:var(--gold);margin-top:3px;">&#11088;</div><?php endif; ?>
            </div>
            <?php endforeach; ?>
          </div>
        </div>

        <!-- LAYER 2 (DOB) POSITIONS -->
        <div style="margin-bottom:28px;">
          <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:rgba(212,175,55,0.5);margin-bottom:14px;">
            Layer 2 &mdash; Birth Date Activations
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;">
            <?php foreach ($hebrew_calc['layer2_positions'] as $lp): ?>
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(212,175,55,0.1);padding:10px 14px;min-width:80px;">
              <div style="font-family:'Cinzel',serif;font-size:16px;color:var(--gold);"><?= intval($lp['position']) ?></div>
              <div style="font-size:12px;color:var(--cream-dim);"><?= htmlspecialchars($lp['name'] ?? '') ?></div>
              <div style="font-size:11px;color:<?= $element_colors[$lp['element'] ?? ''] ?? 'var(--cream-faint)' ?>;"><?= htmlspecialchars($lp['element'] ?? '') ?></div>
            </div>
            <?php endforeach; ?>
          </div>
        </div>

        <!-- LAYER 1 DETAIL TABLE -->
        <details style="margin-bottom:12px;">
          <summary style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:rgba(212,175,55,0.5);cursor:pointer;padding:10px 0;">Show Layer 1 Full Breakdown</summary>
          <div style="overflow-x:auto;margin-top:12px;">
            <table style="width:100%;border-collapse:collapse;font-size:13px;">
              <thead>
                <tr style="border-bottom:1px solid rgba(212,175,55,0.15);">
                  <th style="text-align:left;padding:8px 12px;font-family:'Cinzel',serif;font-size:8px;letter-spacing:1px;color:var(--cream-faint);">Name</th>
                  <th style="text-align:left;padding:8px 12px;font-family:'Cinzel',serif;font-size:8px;letter-spacing:1px;color:var(--cream-faint);">Letters</th>
                  <th style="text-align:center;padding:8px 12px;font-family:'Cinzel',serif;font-size:8px;letter-spacing:1px;color:var(--cream-faint);">Value</th>
                  <th style="text-align:center;padding:8px 12px;font-family:'Cinzel',serif;font-size:8px;letter-spacing:1px;color:var(--cream-faint);">Position</th>
                  <th style="text-align:center;padding:8px 12px;font-family:'Cinzel',serif;font-size:8px;letter-spacing:1px;color:var(--cream-faint);">Sum</th>
                  <th style="text-align:center;padding:8px 12px;font-family:'Cinzel',serif;font-size:8px;letter-spacing:1px;color:var(--cream-faint);">Result</th>
                  <th style="text-align:left;padding:8px 12px;font-family:'Cinzel',serif;font-size:8px;letter-spacing:1px;color:var(--cream-faint);">Letter Name</th>
                </tr>
              </thead>
              <tbody>
                <?php
                $heb_letter_ref_data = _heb_letter_ref();
                foreach ($hebrew_calc['layer1'] as $row):
                  $ref = array();
                  if (!$row['is_bridge'] && $row['position'] <= 22) {
                      $ref = isset($heb_letter_ref_data[$row['position']]) ? $heb_letter_ref_data[$row['position']] : array();
                  }
                ?>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                  <td style="padding:7px 12px;color:var(--cream-dim);"><?= htmlspecialchars($row['name']) ?></td>
                  <td style="padding:7px 12px;color:var(--gold);font-family:'Cinzel',serif;"><?= htmlspecialchars($row['letters']) ?><?= $row['is_combo'] ? '<sup style="font-size:9px;color:var(--cream-faint);">combo</sup>' : '' ?><?= !empty($row['is_final_letter']) ? '<sup style="font-size:9px;color:var(--cream-faint);">final</sup>' : '' ?></td>
                  <td style="padding:7px 12px;text-align:center;color:var(--cream);"><?= intval($row['letter_value']) ?></td>
                  <td style="padding:7px 12px;text-align:center;color:var(--cream-dim);"><?= intval($row['position']) ?></td>
                  <td style="padding:7px 12px;text-align:center;color:var(--cream);"><?= intval($row['sum']) ?></td>
                  <td style="padding:7px 12px;text-align:center;">
                    <?php if ($row['is_bridge']): ?>
                      <span style="color:var(--cream-faint);font-size:12px;">Bridge <?= intval($row['bridge'][0]) ?>/<?= intval($row['bridge'][1]) ?></span>
                    <?php else: ?>
                      <span style="color:var(--gold);font-family:'Cinzel',serif;"><?= intval($row['position']) ?></span>
                    <?php endif; ?>
                  </td>
                  <td style="padding:7px 12px;color:var(--cream-dim);">
                    <?php if (!$row['is_bridge'] && $row['position'] <= 22): ?>
                      <?= htmlspecialchars($ref['name'] ?? '') ?>
                    <?php endif; ?>
                  </td>
                </tr>
                <?php endforeach; ?>
              </tbody>
            </table>
          </div>
        </details>

      <?php endif; ?>
    </div>

    <!-- FELT RESPONSES -->
    <div class="section">
      <div class="section-head">
        <div class="section-title">Felt Body Responses</div>
        <?php if ($hebrew_row): ?>
          <span style="font-size:12px;color:var(--cream-faint);font-style:italic;">Completed <?= date('M j, Y', strtotime($hebrew_row['completed_at'])) ?></span>
        <?php endif; ?>
      </div>

      <?php if (!$hebrew_responses): ?>
        <div class="empty-state">Client has not completed the Hebrew Frequency Questionnaire yet.</div>
      <?php else: ?>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <?php foreach ($hebrew_responses as $r):
            $has_response = !empty(trim($r['felt_response'] ?? ''));
          ?>
          <div style="background:rgba(255,255,255,0.02);border:1px solid <?= $has_response ? 'rgba(212,175,55,0.18)' : 'rgba(255,255,255,0.05)' ?>;padding:16px;">
            <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:8px;">
              <span style="font-family:'Cinzel',serif;font-size:15px;color:var(--gold);"><?= intval($r['letter_id'] ?? 0) ?>.</span>
              <span style="font-family:'Cinzel',serif;font-size:13px;letter-spacing:1px;color:var(--cream);"><?= htmlspecialchars($r['letter_name'] ?? '') ?></span>
              <span style="font-size:11px;color:var(--cream-faint);"><?= htmlspecialchars($r['pronounced'] ?? '') ?></span>
            </div>
            <?php if ($has_response): ?>
              <div style="font-size:14px;font-weight:300;color:var(--cream-dim);line-height:1.7;margin-bottom:6px;"><?= htmlspecialchars($r['felt_response']) ?></div>
              <?php if (!empty(trim($r['notes'] ?? ''))): ?>
                <div style="font-size:12px;font-style:italic;color:rgba(245,240,255,0.35);border-top:1px solid rgba(255,255,255,0.05);padding-top:6px;margin-top:6px;"><?= htmlspecialchars($r['notes']) ?></div>
              <?php endif; ?>
              <?php if (!empty($r['response_time_ms'])): ?>
                <div style="font-size:10px;color:rgba(245,240,255,0.2);margin-top:6px;"><?= number_format($r['response_time_ms'] / 1000, 1) ?>s</div>
              <?php endif; ?>
            <?php else: ?>
              <div style="font-size:13px;font-style:italic;color:rgba(245,240,255,0.2);">No response written.</div>
            <?php endif; ?>
          </div>
          <?php endforeach; ?>
        </div>
      <?php endif; ?>
    </div>

  </div><!-- /tab-hebrew -->

</div><!-- /main -->

<script>
const CLIENT_ID   = <?= $client_id ?>;
const CSRF_TOKEN  = <?= json_encode(admin_csrf()) ?>;
const RAILWAY_URL = <?= json_encode(RAILWAY_API) ?>;

// TAB SWITCHING
function showTab(name) {
  document.querySelectorAll('.tab-btn').forEach(function(b) {
    b.classList.toggle('active', b.dataset.tab === name);
  });
  document.querySelectorAll('.tab-panel').forEach(function(p) {
    p.classList.toggle('active', p.id === 'tab-' + name);
  });
}

// EDIT TOGGLE
function toggleEdit(id) {
  document.getElementById(id).classList.toggle('open');
}

// ANSWERS TOGGLE
function toggleAnswers() {
  var grid = document.getElementById('answersGrid');
  if (!grid) return;
  grid.classList.toggle('open');
  document.querySelector('.answers-toggle').textContent =
    grid.classList.contains('open') ? 'Hide Answers ▲' : 'Show All 24 Answers ▼';
}

// AUTO-CALCULATE
async function autoCalculate() {
  var statusEl = document.getElementById('calcStatus');
  statusEl.textContent = 'Calling Railway API...';
  var tz = document.getElementById('tzSelect').value;
  try {
    var resp = await fetch('/admin/admin-action.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action:     'auto_calculate',
        client_id:  CLIENT_ID,
        tz_offset:  parseFloat(tz),
        csrf:       CSRF_TOKEN
      })
    });
    var data = await resp.json();
    if (data.ok) {
      statusEl.textContent = 'Calculated (' + (data.type || 'done') + '). Reloading...';
      setTimeout(function() { location.reload(); }, 1200);
    } else {
      statusEl.textContent = 'Error: ' + (data.error || 'unknown');
    }
  } catch (e) {
    statusEl.textContent = 'Network error: ' + e.message;
  }
}

// GENERATE NAME FREQUENCY READING
async function generateReading(type, clientId) {
  var statusEl = document.getElementById('genstatus-' + type);
  if (statusEl) statusEl.textContent = 'Starting generation...';

  // Mark as paid (admin override)
  await fetch('/admin/admin-action.php', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'ensure_paid', client_id: clientId, reading_type: type, csrf: CSRF_TOKEN })
  });

  var client = <?= json_encode([
    'first_name'  => $client['first_name'] ?? '',
    'middle_name' => $client['middle_name'] ?? '',
    'last_name'   => ($client['maiden_name'] && $client['maiden_name'] !== $client['last_name'])
                       ? $client['maiden_name']
                       : ($client['last_name'] ?? ''),
  ]) ?>;

  var jobId = null;
  try {
    var resp = await fetch(RAILWAY_URL + '/generate-name-frequency', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(client)
    });
    var data = await resp.json();
    jobId = data.job_id;
    if (!jobId) throw new Error(data.error || 'No job_id returned');
  } catch (e) {
    if (statusEl) statusEl.textContent = 'Error starting generation: ' + e.message;
    return;
  }

  await fetch('/admin/admin-action.php', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'save_job', client_id: clientId, reading_type: type, job_id: jobId, csrf: CSRF_TOKEN })
  });

  if (statusEl) statusEl.textContent = 'Generating... (job ' + jobId.substring(0, 8) + '...)';
  pollJob(type, clientId, jobId, statusEl);
}

async function pollJob(type, clientId, jobId, statusEl) {
  try {
    var resp = await fetch('/admin/admin-action.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'check_job', client_id: clientId, reading_type: type, job_id: jobId, csrf: CSRF_TOKEN })
    });
    var data = await resp.json();
    if (data.status === 'complete') {
      if (statusEl) statusEl.textContent = 'Done! Reloading...';
      setTimeout(function() { location.reload(); }, 1200);
    } else if (data.status === 'failed' || data.status === 'error') {
      if (statusEl) statusEl.textContent = 'Generation failed: ' + (data.error || data.message || 'unknown error');
    } else {
      if (statusEl) statusEl.textContent = 'Still generating...';
      setTimeout(function() { pollJob(type, clientId, jobId, statusEl); }, 5000);
    }
  } catch (e) {
    if (statusEl) statusEl.textContent = 'Poll error: ' + e.message;
    setTimeout(function() { pollJob(type, clientId, jobId, statusEl); }, 8000);
  }
}

async function pollReadingStatus(type, readingId, clientId) {
  var statusEl = document.getElementById('genstatus-' + type);
  if (statusEl) statusEl.textContent = 'Checking...';
  var resp = await fetch('/reading-status.php?id=' + readingId);
  var data = await resp.json();
  if (data.status === 'complete') {
    if (statusEl) statusEl.textContent = 'Complete! Reloading...';
    setTimeout(function() { location.reload(); }, 1000);
  } else {
    if (statusEl) statusEl.textContent = 'Status: ' + data.status;
  }
}

// SAVE TIER 2
async function saveTier2(field) {
  var val     = document.getElementById('tier2_' + field).value;
  var savedEl = document.getElementById('saved_' + field);
  if (savedEl) savedEl.textContent = 'Saving...';
  try {
    var resp = await fetch('/admin/admin-action.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action:    'save_tier2',
        client_id: CLIENT_ID,
        field:     field,
        value:     val,
        csrf:      CSRF_TOKEN
      })
    });
    var data = await resp.json();
    if (data.ok) {
      if (savedEl) { savedEl.textContent = 'Saved.'; setTimeout(function() { savedEl.textContent = ''; }, 3000); }
    } else {
      if (savedEl) savedEl.textContent = 'Error: ' + (data.error || 'unknown');
    }
  } catch (e) {
    if (savedEl) savedEl.textContent = 'Network error: ' + e.message;
  }
}
</script>
</body>
</html>
