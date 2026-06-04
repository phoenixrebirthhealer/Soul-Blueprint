<?php
require_once 'includes/auth.php';

if (is_logged_in()) {
    header('Location: /dashboard');
    exit;
}

if (empty($_SESSION['reg'])) {
    header('Location: /register');
    exit;
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();

    $first = trim($_POST['first_name'] ?? '');
    $last  = trim($_POST['last_name'] ?? '');
    $dob   = trim($_POST['dob'] ?? '');
    $tob   = trim($_POST['time_of_birth'] ?? '');
    $tz    = trim($_POST['timezone'] ?? '');
    $place = trim($_POST['place_of_birth'] ?? '');

    if (!$first || !$last || !$dob || !$tob || !$tz || !$place) {
        $error = 'Please fill in all required fields.';
    } else {
        $_SESSION['intake'] = [
            'first_name'       => $first,
            'middle_name'      => trim($_POST['middle_name'] ?? ''),
            'last_name'        => $last,
            'maiden_name'      => trim($_POST['maiden_name'] ?? ''),
            'dob'              => $dob,
            'time_of_birth'    => $tob,
            'timezone'         => $tz,
            'place_of_birth'   => $place,
            'latitude'         => trim($_POST['latitude'] ?? '') ?: null,
            'longitude'        => trim($_POST['longitude'] ?? '') ?: null,
            'phone'            => trim($_POST['phone'] ?? ''),
            'career_field'     => trim($_POST['career_field'] ?? ''),
            'career_expression'=> trim($_POST['career_expression'] ?? ''),
        ];
        header('Location: /assessment');
        exit;
    }
}

$post = $_POST;
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Your Profile | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; }
    .main { flex: 1; padding: 120px 40px 80px; }
    .inner { max-width: 720px; margin: 0 auto; }
    .page-title { font-family: 'Cinzel', serif; font-size: clamp(24px,3vw,40px); font-weight: 400; color: var(--cream); margin-bottom: 10px; }
    .page-title em { color: var(--gold); font-style: normal; }
    .page-sub { font-size: 16px; font-weight: 300; color: var(--cream-dim); margin-bottom: 48px; line-height: 1.8; max-width: 580px; }
    .form-panel { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.15); padding: 48px 44px; }
    .section-label { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 4px; text-transform: uppercase; color: var(--gold); opacity: 0.6; margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid rgba(212,175,55,0.1); }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 24px; }
    .form-group { margin-bottom: 22px; }
    .form-group.full { grid-column: 1 / -1; }
    .form-group label { display: block; font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); margin-bottom: 8px; }
    .form-group input, .form-group select, .form-group textarea { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 16px; font-weight: 300; padding: 12px 14px; outline: none; transition: border-color 0.3s; }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: rgba(212,175,55,0.5); }
    .form-group select option { background: #1a0a2e; color: var(--cream); }
    .form-group textarea { min-height: 90px; resize: vertical; }
    .form-note { font-size: 13px; font-style: italic; color: var(--cream-faint); margin-top: 6px; }
    .section-gap { margin-top: 40px; }
    .error-msg { background: rgba(194,24,91,0.12); border: 1px solid rgba(194,24,91,0.3); color: #f48fb1; font-size: 14px; font-weight: 300; padding: 14px 18px; margin-bottom: 24px; }
    .btn-full { width: 100%; text-align: center; border: none; cursor: pointer; margin-top: 12px; }
    .steps { display: flex; justify-content: center; gap: 8px; margin-bottom: 36px; }
    .step { width: 32px; height: 3px; background: rgba(212,175,55,0.15); }
    .step.active { background: var(--gold); }
    @media (max-width: 600px) { .form-grid { grid-template-columns: 1fr; } .form-panel { padding: 32px 24px; } }
  </style>
</head>
<body>
<?php include 'includes/nav.php'; ?>
<div class="main">
  <div class="inner">
    <div class="steps">
      <div class="step"></div>
      <div class="step active"></div>
      <div class="step"></div>
    </div>
    <h1 class="page-title">Your <em>Soul Profile</em></h1>
    <p class="page-sub">Step 2 of 3. This is the data your readings are built from. Every required field matters. Use the name given to you at birth.</p>

    <?php if ($error): ?>
      <div class="error-msg"><?= htmlspecialchars($error) ?></div>
    <?php endif; ?>

    <div class="form-panel">
      <form method="POST" action="/intake" id="intakeForm">
        <input type="hidden" name="csrf_token" value="<?= csrf_token() ?>">
        <input type="hidden" name="latitude" id="lat">
        <input type="hidden" name="longitude" id="lng">

        <div class="section-label">Your Birth Name</div>
        <div class="form-grid">
          <div class="form-group">
            <label>First Name <span style="color:var(--magenta)">*</span></label>
            <input type="text" name="first_name" value="<?= htmlspecialchars($post['first_name'] ?? '') ?>" required />
          </div>
          <div class="form-group">
            <label>Middle Name</label>
            <input type="text" name="middle_name" value="<?= htmlspecialchars($post['middle_name'] ?? '') ?>" />
          </div>
          <div class="form-group">
            <label>Last Name <span style="color:var(--magenta)">*</span></label>
            <input type="text" name="last_name" value="<?= htmlspecialchars($post['last_name'] ?? '') ?>" required />
          </div>
          <div class="form-group">
            <label>Maiden Name</label>
            <input type="text" name="maiden_name" value="<?= htmlspecialchars($post['maiden_name'] ?? '') ?>" placeholder="If different from last name" />
          </div>
        </div>

        <div class="section-label section-gap">Birth Data</div>
        <div class="form-grid">
          <div class="form-group">
            <label>Date of Birth <span style="color:var(--magenta)">*</span></label>
            <input type="date" name="dob" value="<?= htmlspecialchars($post['dob'] ?? '') ?>" required />
          </div>
          <div class="form-group">
            <label>Time of Birth <span style="color:var(--magenta)">*</span></label>
            <input type="time" name="time_of_birth" value="<?= htmlspecialchars($post['time_of_birth'] ?? '') ?>" required />
            <p class="form-note">Use exact birth certificate time if you have it.</p>
          </div>
          <div class="form-group full">
            <label>Place of Birth <span style="color:var(--magenta)">*</span></label>
            <input type="text" name="place_of_birth" id="placeOfBirth" value="<?= htmlspecialchars($post['place_of_birth'] ?? '') ?>" placeholder="City, State, Country" required />
            <p class="form-note">This determines your rising sign and chart. Be as specific as possible.</p>
          </div>
          <div class="form-group full">
            <label>Timezone <span style="color:var(--magenta)">*</span></label>
            <select name="timezone" required>
              <option value="">Select your birth timezone</option>
              <?php
              $tzones = [
                'Pacific/Honolulu' => 'Hawaii (HST, UTC-10)',
                'America/Anchorage' => 'Alaska (AKST, UTC-9)',
                'America/Los_Angeles' => 'Pacific (PST/PDT, UTC-8/-7)',
                'America/Denver' => 'Mountain (MST/MDT, UTC-7/-6)',
                'America/Phoenix' => 'Mountain No DST (MST, UTC-7)',
                'America/Chicago' => 'Central (CST/CDT, UTC-6/-5)',
                'America/New_York' => 'Eastern (EST/EDT, UTC-5/-4)',
                'America/Halifax' => 'Atlantic (AST/ADT, UTC-4/-3)',
                'America/St_Johns' => 'Newfoundland (NST/NDT, UTC-3:30/-2:30)',
                'America/Sao_Paulo' => 'Brasilia (BRT, UTC-3)',
                'America/Argentina/Buenos_Aires' => 'Argentina (ART, UTC-3)',
                'Atlantic/Reykjavik' => 'UTC+0 / Reykjavik',
                'Europe/London' => 'London (GMT/BST, UTC+0/+1)',
                'Europe/Paris' => 'Central Europe (CET/CEST, UTC+1/+2)',
                'Europe/Helsinki' => 'Eastern Europe (EET/EEST, UTC+2/+3)',
                'Europe/Moscow' => 'Moscow (MSK, UTC+3)',
                'Asia/Dubai' => 'Gulf (GST, UTC+4)',
                'Asia/Kolkata' => 'India (IST, UTC+5:30)',
                'Asia/Dhaka' => 'Bangladesh (BST, UTC+6)',
                'Asia/Bangkok' => 'Indochina (ICT, UTC+7)',
                'Asia/Shanghai' => 'China (CST, UTC+8)',
                'Asia/Tokyo' => 'Japan (JST, UTC+9)',
                'Australia/Sydney' => 'Australia East (AEST/AEDT, UTC+10/+11)',
                'Pacific/Auckland' => 'New Zealand (NZST/NZDT, UTC+12/+13)',
              ];
              $sel = $post['timezone'] ?? '';
              foreach ($tzones as $tz => $label):
              ?>
                <option value="<?= $tz ?>" <?= $sel === $tz ? 'selected' : '' ?>><?= $label ?></option>
              <?php endforeach; ?>
            </select>
          </div>
        </div>

        <div class="section-label section-gap">Contact</div>
        <div class="form-group">
          <label>Phone Number</label>
          <input type="tel" name="phone" value="<?= htmlspecialchars($post['phone'] ?? '') ?>" placeholder="Optional" />
        </div>

        <div class="section-label section-gap">Career &amp; Expression</div>
        <div class="form-group">
          <label>Career Field / Job Title</label>
          <input type="text" name="career_field" value="<?= htmlspecialchars($post['career_field'] ?? '') ?>" placeholder="e.g. Registered Nurse, Software Engineer, Stay-at-home parent" />
        </div>
        <div class="form-group">
          <label>How You Express Yourself in Your Work</label>
          <textarea name="career_expression" placeholder="Describe what your work actually involves day-to-day, not just the title."><?= htmlspecialchars($post['career_expression'] ?? '') ?></textarea>
        </div>

        <button class="btn-primary btn-full" type="submit">Save &amp; Continue to Assessment &rarr;</button>
      </form>
    </div>
  </div>
</div>

<script>
const placeInput = document.getElementById('placeOfBirth');
let geocodeTimeout;
placeInput.addEventListener('input', function() {
  clearTimeout(geocodeTimeout);
  geocodeTimeout = setTimeout(async () => {
    const val = placeInput.value.trim();
    if (val.length < 4) return;
    try {
      const r = await fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(val) + '&limit=1', { headers: { 'Accept-Language': 'en' } });
      const data = await r.json();
      if (data && data[0]) {
        document.getElementById('lat').value = data[0].lat;
        document.getElementById('lng').value = data[0].lon;
      }
    } catch(e) {}
  }, 800);
});
</script>

<?php include 'includes/footer.php'; ?>
</body>
</html>
