<?php
require_once __DIR__ . '/includes/admin-auth.php';
require_once __DIR__ . '/../includes/auth.php';
admin_require_login();

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
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Client | Admin</title>
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
    .sidebar { position: fixed; top: 0; left: 0; bottom: 0; width: 220px; background: var(--plum-mid); border-right: 1px solid var(--border); padding: 32px 0; display: flex; flex-direction: column; z-index: 10; }
    .sidebar-brand { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); padding: 0 24px 28px; border-bottom: 1px solid var(--border); }
    .sidebar-brand span { display: block; font-size: 8px; letter-spacing: 2px; color: var(--cream-faint); margin-top: 4px; }
    .nav-item { display: block; padding: 12px 24px; font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: var(--cream-dim); text-decoration: none; transition: all 0.2s; border-left: 2px solid transparent; }
    .nav-item:hover { color: var(--gold); border-left-color: var(--gold); background: rgba(212,175,55,0.04); }
    .main { margin-left: 220px; padding: 40px 48px; max-width: 1100px; }
    .breadcrumb { font-size: 13px; color: var(--cream-faint); margin-bottom: 24px; }
    .breadcrumb a { color: var(--gold); text-decoration: none; }
    .client-name { font-family: 'Cinzel', serif; font-size: 28px; font-weight: 400; color: var(--cream); margin-bottom: 6px; }
    .client-email { font-size: 16px; color: var(--cream-faint); margin-bottom: 40px; }

    /* SECTIONS */
    .section { background: var(--plum-card); border: 1px solid var(--border); padding: 32px; margin-bottom: 24px; }
    .section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(212,175,55,0.08); }
    .section-title { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); }
    .section-actions { display: flex; gap: 10px; }

    /* DATA GRID */
    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
    .data-row { display: contents; }
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
    .score-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px; }
    .score-meta-item h4 { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--cream-faint); margin-bottom: 8px; }
    .score-meta-item p { font-size: 15px; color: var(--cream-dim); }

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

    /* MESSAGES */
    .flash { padding: 14px 18px; margin-bottom: 20px; font-size: 14px; }
    .flash.success { background: rgba(0,200,83,0.1); border: 1px solid rgba(0,200,83,0.3); color: var(--green); }
    .flash.error { background: rgba(194,24,91,0.1); border: 1px solid rgba(194,24,91,0.3); color: #f48fb1; }

    @media (max-width: 800px) {
      .data-grid, .form-grid, .score-meta, .answers-grid { grid-template-columns: 1fr; }
      .reading-item { flex-direction: column; align-items: flex-start; }
    }
  </style>
</head>
<body>
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

$full_name = trim(($client['first_name'] ?? '') . ' ' . ($client['middle_name'] ? $client['middle_name'] . ' ' : '') . ($client['last_name'] ?? ''));

$all_reading_types = [
    'name_frequency'      => ['label' => 'Name Frequency Reading', 'price' => '$10.99'],
    'relational_tier1'    => ['label' => 'Relational Name Frequency Tier 1', 'price' => '$10.99'],
    'self_love_language'  => ['label' => 'Self-Love Language Reading', 'price' => '$82'],
    'tcm_astrology_tier1' => ['label' => 'TCM Astrology Chakra Tier 1', 'price' => '$59'],
    'soul_blueprint_tier1'=> ['label' => 'Soul Blueprint Decoder Tier 1', 'price' => '$77'],
];

$attachment_options = ['Secure','Pure Anxious','Pure Avoidant','Pure Disorganized','Disorganized Anxious Leaning','Disorganized Avoidant Leaning','True Disorganized Equal Split'];

$q_labels = [
    'q1'=>'Relationship with self','q2'=>'When things go wrong','q3'=>'Emotional overwhelm','q4'=>'Decision making',
    'q5'=>'Emotional safety in childhood','q6'=>'When expressed emotions','q7'=>'Caregiver predictability','q8'=>'Responsible for others emotions',
    'q9'=>'In close relationships','q10'=>'When someone gets close','q11'=>'When conflict happens','q12'=>'Most accurate statement',
    'q13'=>'When someone pulls away','q14'=>'Responding to vulnerability',
    'q15'=>'Belief about love','q16'=>'Receiving love/support','q17'=>'When complimented',
    'q18'=>'What drains energy','q19'=>'After time with people','q20'=>'Ignoring own needs',
    'q21'=>'Self-care consistency','q22'=>'When emotionally triggered',
    'q23'=>'Willingness to face discomfort','q24'=>'Hope from transformation',
];
?>

<aside class="sidebar">
  <div class="sidebar-brand">Phoenix Rebirth<span>Admin Panel</span></div>
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
  <div class="client-email"><?= htmlspecialchars($client['email']) ?> &nbsp;&middot;&nbsp; Client since <?= date('F j, Y', strtotime($client['created_at'])) ?></div>

  <!-- ============================================================ -->
  <!-- PROFILE -->
  <!-- ============================================================ -->
  <div class="section">
    <div class="section-head">
      <div class="section-title">Client Profile</div>
      <div class="section-actions">
        <button class="btn btn-gold" onclick="toggleEdit('profileEdit')">Edit Profile</button>
      </div>
    </div>

    <!-- DISPLAY -->
    <div id="profileDisplay" class="data-grid">
      <?php
      $fields = [
        'First Name' => $client['first_name'],
        'Middle Name' => $client['middle_name'],
        'Last Name' => $client['last_name'],
        'Maiden Name' => $client['maiden_name'],
        'Date of Birth' => $client['dob'],
        'Time of Birth' => $client['time_of_birth'],
        'Timezone' => $client['timezone'],
        'Place of Birth' => $client['place_of_birth'],
        'Latitude' => $client['latitude'],
        'Longitude' => $client['longitude'],
        'Phone' => $client['phone'],
        'Career Field' => $client['career_field'],
        'Intake Complete' => $client['intake_complete'] ? 'Yes' : 'No',
      ];
      foreach ($fields as $label => $val): ?>
        <div class="data-label"><?= $label ?></div>
        <div class="data-value <?= $val ? '' : 'empty' ?>"><?= $val ? htmlspecialchars($val) : 'Not set' ?></div>
      <?php endforeach; ?>
      <?php if ($client['career_expression']): ?>
        <div class="data-label">Career Expression</div>
        <div class="data-value"><?= htmlspecialchars($client['career_expression']) ?></div>
      <?php endif; ?>
    </div>

    <!-- EDIT FORM -->
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

  <!-- ============================================================ -->
  <!-- ASSESSMENT -->
  <!-- ============================================================ -->
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
            S: <?= $counts['S'] ?? 0 ?> &nbsp; A: <?= $counts['A'] ?? 0 ?> &nbsp; V: <?= $counts['V'] ?? 0 ?> &nbsp; D: <?= $counts['D'] ?? 0 ?>
          </div>
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
            <div class="q-label"><?= $label ?></div>
            <div class="q-val"><?= htmlspecialchars($answers[$key] ?? '--') ?></div>
          </div>
        <?php endforeach; ?>
      </div>
      <?php endif; ?>

    <?php else: ?>
      <div style="color:var(--cream-faint);font-style:italic;font-size:15px;">No assessment completed yet.</div>
    <?php endif; ?>

    <!-- OVERRIDE FORM -->
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
              <option value="<?= $opt ?>" <?= ($assessment['attachment_style'] ?? '') === $opt ? 'selected' : '' ?>><?= $opt ?></option>
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

  <!-- ============================================================ -->
  <!-- READINGS -->
  <!-- ============================================================ -->
  <div class="section">
    <div class="section-head">
      <div class="section-title">Readings</div>
    </div>

    <?php foreach ($all_reading_types as $rtype => $rinfo):
      $r = $readings_list[$rtype] ?? null;
      $status = $r['status'] ?? 'not_purchased';
      $paid   = $r['paid'] ?? 0;
    ?>
    <div class="reading-item" id="reading-<?= $rtype ?>">
      <div class="reading-info">
        <h3><?= $rinfo['label'] ?></h3>
        <p><?= $rinfo['price'] ?>
          <?php if ($r): ?>
            &nbsp;&middot;&nbsp; Paid: <?= $paid ? 'Yes' : 'No' ?>
            <?php if ($r['created_at']): ?>&nbsp;&middot;&nbsp; <?= date('M j, Y', strtotime($r['created_at'])) ?><?php endif; ?>
            <?php if ($r['paypal_order_id']): ?>&nbsp;&middot;&nbsp; PayPal: <?= htmlspecialchars($r['paypal_order_id']) ?><?php endif; ?>
          <?php endif; ?>
        </p>
        <div class="gen-status" id="genstatus-<?= $rtype ?>"></div>
      </div>

      <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
        <?php if ($status === 'complete'): ?>
          <span class="reading-status status-complete">&#10003; Complete</span>
          <a href="/readings/<?= htmlspecialchars($r['file_name']) ?>" target="_blank" class="btn btn-green">View Reading</a>
          <?php if ($rtype === 'name_frequency'): ?>
          <button class="btn btn-gold" onclick="generateReading('<?= $rtype ?>', <?= $client_id ?>)">Re-Generate</button>
          <?php endif; ?>
          <form method="POST" style="display:inline" onsubmit="return confirm('Delete this reading? Cannot be undone.');">
            <input type="hidden" name="csrf_token" value="<?= admin_csrf() ?>">
            <input type="hidden" name="action" value="delete_reading">
            <input type="hidden" name="reading_type" value="<?= $rtype ?>">
            <button type="submit" class="btn btn-danger">Delete</button>
          </form>

        <?php elseif ($status === 'generating'): ?>
          <span class="reading-status status-generating">Generating...</span>
          <button class="btn btn-gold" onclick="pollReadingStatus('<?= $rtype ?>', <?= $r['id'] ?>, <?= $client_id ?>)">Check Status</button>

        <?php elseif ($status === 'error'): ?>
          <span class="reading-status status-error">Error</span>
          <span style="font-size:12px;color:#f48fb1;"><?= htmlspecialchars($r['error_message'] ?? '') ?></span>
          <?php if ($rtype === 'name_frequency'): ?>
          <button class="btn btn-gold" onclick="generateReading('<?= $rtype ?>', <?= $client_id ?>)">Retry</button>
          <?php endif; ?>

        <?php else: ?>
          <span class="reading-status status-none"><?= $paid ? 'Paid / Not Generated' : 'Not Purchased' ?></span>
          <?php if (!$paid): ?>
          <form method="POST" style="display:inline">
            <input type="hidden" name="csrf_token" value="<?= admin_csrf() ?>">
            <input type="hidden" name="action" value="mark_reading_paid">
            <input type="hidden" name="reading_type" value="<?= $rtype ?>">
            <button type="submit" class="btn btn-ghost">Mark as Paid</button>
          </form>
          <?php endif; ?>
          <?php if ($rtype === 'name_frequency' && ($paid || !$r)): ?>
          <button class="btn btn-gold" onclick="generateReading('<?= $rtype ?>', <?= $client_id ?>)">Generate Now</button>
          <?php endif; ?>
        <?php endif; ?>
      </div>
    </div>
    <?php endforeach; ?>
  </div>

</div>

<script>
function toggleEdit(id) {
  const el = document.getElementById(id);
  el.classList.toggle('open');
}

function toggleAnswers() {
  const grid = document.getElementById('answersGrid');
  grid.classList.toggle('open');
  document.querySelector('.answers-toggle').textContent =
    grid.classList.contains('open') ? 'Hide Answers ▲' : 'Show All 24 Answers ▼';
}

async function generateReading(type, clientId) {
  const statusEl = document.getElementById('genstatus-' + type);
  statusEl.textContent = 'Starting generation...';

  // Mark as paid if not yet (admin override)
  await fetch('/admin/admin-action.php', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'ensure_paid', client_id: clientId, reading_type: type, csrf: '<?= admin_csrf() ?>' })
  });

  // Call Railway to start generation
  const client = <?= json_encode([
    'first_name'  => $client['first_name'] ?? '',
    'middle_name' => $client['middle_name'] ?? '',
    'last_name'   => ($client['maiden_name'] && $client['maiden_name'] !== $client['last_name']) ? $client['maiden_name'] : ($client['last_name'] ?? ''),
  ]) ?>;

  let jobId = null;
  try {
    const resp = await fetch('<?= RAILWAY_API ?>/generate-name-frequency', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(client)
    });
    const data = await resp.json();
    jobId = data.job_id;
    if (!jobId) throw new Error(data.error || 'No job_id returned');
  } catch(e) {
    statusEl.textContent = 'Error starting generation: ' + e.message;
    return;
  }

  // Save job_id to database
  await fetch('/admin/admin-action.php', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'save_job', client_id: clientId, reading_type: type, job_id: jobId, csrf: '<?= admin_csrf() ?>' })
  });

  statusEl.textContent = 'Generating... (job ' + jobId.substring(0,8) + '...)';
  pollJob(type, clientId, jobId, statusEl);
}

async function pollJob(type, clientId, jobId, statusEl) {
  try {
    const resp = await fetch('/admin/admin-action.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'check_job', client_id: clientId, reading_type: type, job_id: jobId, csrf: '<?= admin_csrf() ?>' })
    });
    const data = await resp.json();
    if (data.status === 'complete') {
      statusEl.textContent = 'Done! Reloading...';
      setTimeout(() => location.reload(), 1200);
    } else if (data.status === 'failed') {
      statusEl.textContent = 'Generation failed: ' + (data.error || 'unknown error');
    } else {
      statusEl.textContent = 'Still generating...';
      setTimeout(() => pollJob(type, clientId, jobId, statusEl), 5000);
    }
  } catch(e) {
    statusEl.textContent = 'Poll error: ' + e.message;
    setTimeout(() => pollJob(type, clientId, jobId, statusEl), 8000);
  }
}

async function pollReadingStatus(type, readingId, clientId) {
  const statusEl = document.getElementById('genstatus-' + type);
  statusEl.textContent = 'Checking...';
  const resp = await fetch('/reading-status.php?id=' + readingId);
  const data = await resp.json();
  if (data.status === 'complete') {
    statusEl.textContent = 'Complete! Reloading...';
    setTimeout(() => location.reload(), 1000);
  } else {
    statusEl.textContent = 'Status: ' + data.status;
  }
}
</script>
</body>
</html>
