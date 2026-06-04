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

    $first       = trim($_POST['first_name'] ?? '');
    $last        = trim($_POST['last_name'] ?? '');
    $dob         = trim($_POST['dob'] ?? '');
    $tz          = trim($_POST['timezone'] ?? '');
    $place       = trim($_POST['place_of_birth'] ?? '');
    $phone       = trim($_POST['phone'] ?? '');
    $career_f    = trim($_POST['career_field'] ?? '');
    $career_e    = trim($_POST['career_expression'] ?? '');

    $same_maiden    = isset($_POST['same_maiden']);
    $maiden         = $same_maiden ? $last : trim($_POST['maiden_name'] ?? '');

    $unknown_time   = isset($_POST['unknown_time']);
    $tob            = $unknown_time ? null : trim($_POST['time_of_birth'] ?? '');

    $med_device      = $_POST['medical_device'] ?? '';
    $med_device_desc = trim($_POST['medical_device_desc'] ?? '');
    $terms_agreed    = isset($_POST['terms_agreed']);

    if (!$first || !$last || !$maiden || !$dob || !$tz || !$place || !$phone || !$career_f || !$career_e) {
        $error = 'Please fill in all required fields.';
    } elseif (!$unknown_time && !$tob) {
        $error = 'Please enter a time of birth or check "I don\'t know my birth time."';
    } elseif ($med_device === '') {
        $error = 'Please answer the health disclosure question about medical devices.';
    } elseif ($med_device === '1' && !$med_device_desc) {
        $error = 'Please describe your medical device(s).';
    } elseif (!$terms_agreed) {
        $error = 'You must read and agree to all terms, policies, and disclaimers to continue.';
    } else {
        try {
            $dob_obj = new DateTime($dob);
            $age = (int)(new DateTime())->diff($dob_obj)->y;
            if ($age < 18) {
                $error = 'You must be 18 years of age or older to create an account. This platform is for adults only.';
            }
        } catch (Exception $e) {
            $error = 'Invalid date of birth.';
        }

        if (!$error) {
            $_SESSION['intake'] = [
                'first_name'          => $first,
                'middle_name'         => trim($_POST['middle_name'] ?? ''),
                'last_name'           => $last,
                'maiden_name'         => $maiden,
                'dob'                 => $dob,
                'time_of_birth'       => $tob,
                'birth_time_unknown'  => $unknown_time ? 1 : 0,
                'timezone'            => $tz,
                'place_of_birth'      => $place,
                'latitude'            => trim($_POST['latitude'] ?? '') ?: null,
                'longitude'           => trim($_POST['longitude'] ?? '') ?: null,
                'phone'               => $phone,
                'career_field'        => $career_f,
                'career_expression'   => $career_e,
                'medical_device'      => (int)$med_device,
                'medical_device_desc' => $med_device === '1' ? $med_device_desc : null,
                'terms_agreed_at'     => date('Y-m-d H:i:s'),
            ];
            header('Location: /assessment');
            exit;
        }
    }
}

$post = $_POST;

$career_fields = [
    '' => 'Select your career field',
    'Healthcare / Medicine' => 'Healthcare / Medicine',
    'Nursing / Patient Care' => 'Nursing / Patient Care',
    'Mental Health / Therapy / Counseling' => 'Mental Health / Therapy / Counseling',
    'Social Work / Human Services' => 'Social Work / Human Services',
    'Education / Teaching (K-12)' => 'Education / Teaching (K-12)',
    'Higher Education / Research / Academia' => 'Higher Education / Research / Academia',
    'Business / Management / Operations' => 'Business / Management / Operations',
    'Finance / Banking / Accounting' => 'Finance / Banking / Accounting',
    'Real Estate' => 'Real Estate',
    'Law / Legal Services' => 'Law / Legal Services',
    'Law Enforcement / Military / Security' => 'Law Enforcement / Military / Security',
    'Government / Public Administration' => 'Government / Public Administration',
    'Technology / Software / IT' => 'Technology / Software / IT',
    'Engineering' => 'Engineering',
    'Trades / Construction / Skilled Labor' => 'Trades / Construction / Skilled Labor',
    'Manufacturing / Production' => 'Manufacturing / Production',
    'Retail / Customer Service' => 'Retail / Customer Service',
    'Hospitality / Food & Beverage' => 'Hospitality / Food & Beverage',
    'Transportation / Logistics' => 'Transportation / Logistics',
    'Creative Arts / Design / Photography' => 'Creative Arts / Design / Photography',
    'Writing / Journalism / Content Creation' => 'Writing / Journalism / Content Creation',
    'Music / Performing Arts / Entertainment' => 'Music / Performing Arts / Entertainment',
    'Film / Video / Media Production' => 'Film / Video / Media Production',
    'Marketing / Advertising / PR' => 'Marketing / Advertising / PR',
    'Sales' => 'Sales',
    'Non-Profit / Volunteer / Community Work' => 'Non-Profit / Volunteer / Community Work',
    'Spiritual Work / Healing Arts / Coaching' => 'Spiritual Work / Healing Arts / Coaching',
    'Agriculture / Horticulture / Environmental' => 'Agriculture / Horticulture / Environmental',
    'Self-Employed / Entrepreneur' => 'Self-Employed / Entrepreneur',
    'Stay-at-Home Parent / Family Caregiver' => 'Stay-at-Home Parent / Family Caregiver',
    'Student (Full-Time)' => 'Student (Full-Time)',
    'Retired' => 'Retired',
    'Between Positions' => 'Between Positions',
    'Other' => 'Other',
];

$career_expressions = [
    '' => 'Select how you primarily express yourself in your work',
    'I primarily help and support people directly' => 'I primarily help and support people directly',
    'I primarily create, design, or produce' => 'I primarily create, design, or produce',
    'I primarily lead, manage, or direct others' => 'I primarily lead, manage, or direct others',
    'I primarily teach, train, or mentor' => 'I primarily teach, train, or mentor',
    'I primarily analyze, research, or solve problems' => 'I primarily analyze, research, or solve problems',
    'I primarily build, repair, or construct' => 'I primarily build, repair, or construct',
    'I primarily sell, market, or persuade' => 'I primarily sell, market, or persuade',
    'I primarily heal, treat, or provide care' => 'I primarily heal, treat, or provide care',
    'I primarily perform, present, or entertain' => 'I primarily perform, present, or entertain',
    'I primarily plan, organize, or coordinate' => 'I primarily plan, organize, or coordinate',
    'I primarily protect, enforce, or keep others safe' => 'I primarily protect, enforce, or keep others safe',
    'I primarily write, communicate, or tell stories' => 'I primarily write, communicate, or tell stories',
    'I primarily connect people or build community' => 'I primarily connect people or build community',
    'I primarily grow, cultivate, or work with nature' => 'I primarily grow, cultivate, or work with nature',
];
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
    .form-group input[type=text],
    .form-group input[type=date],
    .form-group input[type=tel],
    .form-group select { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 16px; font-weight: 300; padding: 12px 14px; outline: none; transition: border-color 0.3s; }
    .form-group input:focus, .form-group select:focus { border-color: rgba(212,175,55,0.5); }
    .form-group select option { background: #1a0a2e; color: var(--cream); }
    .form-group input:disabled { opacity: 0.35; cursor: not-allowed; }
    .form-note { font-size: 13px; font-style: italic; color: var(--cream-faint); margin-top: 6px; }
    .section-gap { margin-top: 40px; }
    .error-msg { background: rgba(194,24,91,0.12); border: 1px solid rgba(194,24,91,0.3); color: #f48fb1; font-size: 14px; font-weight: 300; padding: 14px 18px; margin-bottom: 24px; }
    .btn-full { width: 100%; text-align: center; border: none; cursor: pointer; margin-top: 12px; }
    .steps { display: flex; justify-content: center; gap: 8px; margin-bottom: 36px; }
    .step { width: 32px; height: 3px; background: rgba(212,175,55,0.15); }
    .step.active { background: var(--gold); }

    /* Checkbox options */
    .check-opt { display: flex; align-items: center; gap: 10px; margin-top: 10px; cursor: pointer; font-family: 'Cormorant Garamond', serif; font-size: 14px; font-weight: 300; color: var(--cream-dim); }
    .check-opt input[type=checkbox] { width: 15px; height: 15px; accent-color: var(--gold); flex-shrink: 0; cursor: pointer; }

    /* Radio buttons */
    .radio-group { display: flex; flex-direction: column; gap: 12px; margin-top: 4px; }
    .radio-opt { display: flex; align-items: flex-start; gap: 12px; cursor: pointer; font-family: 'Cormorant Garamond', serif; font-size: 16px; font-weight: 300; color: var(--cream); line-height: 1.5; }
    .radio-opt input[type=radio] { margin-top: 3px; width: 16px; height: 16px; accent-color: var(--gold); flex-shrink: 0; cursor: pointer; }

    /* Place of birth autocomplete */
    .autocomplete-wrap { position: relative; }
    .autocomplete-list { display: none; position: absolute; top: 100%; left: 0; right: 0; background: #1a0a2e; border: 1px solid rgba(212,175,55,0.35); border-top: none; z-index: 200; max-height: 220px; overflow-y: auto; }
    .autocomplete-item { padding: 12px 14px; font-family: 'Cormorant Garamond', serif; font-size: 15px; font-weight: 300; color: var(--cream); cursor: pointer; border-bottom: 1px solid rgba(212,175,55,0.1); }
    .autocomplete-item:last-child { border-bottom: none; }
    .autocomplete-item:hover { background: rgba(212,175,55,0.1); color: var(--gold); }

    /* Accordion */
    .accord-wrap { border: 1px solid rgba(212,175,55,0.2); margin-bottom: 20px; }
    .accord-item { border-bottom: 1px solid rgba(212,175,55,0.1); }
    .accord-item:last-child { border-bottom: none; }
    .accord-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; cursor: pointer; font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--gold); transition: background 0.2s; gap: 12px; }
    .accord-header:hover { background: rgba(212,175,55,0.05); }
    .accord-arrow { font-size: 10px; flex-shrink: 0; opacity: 0.6; }
    .accord-body { display: none; background: rgba(0,0,0,0.25); }
    .accord-body.open { display: block; }
    .accord-text { padding: 20px; font-family: 'Cormorant Garamond', serif; font-size: 14px; font-weight: 300; color: var(--cream-dim); line-height: 1.85; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }

    /* Agreement checkbox */
    .agree-box { background: rgba(212,175,55,0.04); border: 1px solid rgba(212,175,55,0.25); padding: 20px; }
    .agree-label { display: flex; align-items: flex-start; gap: 14px; cursor: pointer; }
    .agree-label input[type=checkbox] { margin-top: 3px; width: 17px; height: 17px; accent-color: var(--gold); flex-shrink: 0; cursor: pointer; }
    .agree-label span { font-family: 'Cormorant Garamond', serif; font-size: 15px; font-weight: 300; color: var(--cream); line-height: 1.75; }

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
      <form method="POST" action="/intake" id="intakeForm" autocomplete="off">
        <input type="hidden" name="csrf_token" value="<?= csrf_token() ?>">
        <input type="hidden" name="latitude" id="lat" value="<?= htmlspecialchars($post['latitude'] ?? '') ?>">
        <input type="hidden" name="longitude" id="lng" value="<?= htmlspecialchars($post['longitude'] ?? '') ?>">

        <!-- BIRTH NAME -->
        <div class="section-label">Your Birth Name</div>
        <div class="form-grid">
          <div class="form-group">
            <label>First Name <span style="color:var(--magenta)">*</span></label>
            <input type="text" name="first_name" id="firstName" value="<?= htmlspecialchars($post['first_name'] ?? '') ?>" required />
          </div>
          <div class="form-group">
            <label>Middle Name</label>
            <input type="text" name="middle_name" value="<?= htmlspecialchars($post['middle_name'] ?? '') ?>" />
          </div>
          <div class="form-group">
            <label>Last Name <span style="color:var(--magenta)">*</span></label>
            <input type="text" name="last_name" id="lastName" value="<?= htmlspecialchars($post['last_name'] ?? '') ?>" required />
          </div>
          <div class="form-group">
            <label>Birth Last Name (Maiden Name) <span style="color:var(--magenta)">*</span></label>
            <input type="text" name="maiden_name" id="maidenName" value="<?= htmlspecialchars($post['maiden_name'] ?? '') ?>" <?= isset($post['same_maiden']) ? 'readonly' : 'required' ?> />
            <label class="check-opt">
              <input type="checkbox" name="same_maiden" id="sameMaiden" value="1" <?= isset($post['same_maiden']) ? 'checked' : '' ?>>
              Same as last name
            </label>
            <p class="form-note">All readings are calculated from the birth last name.</p>
          </div>
        </div>

        <!-- BIRTH DATA -->
        <div class="section-label section-gap">Birth Data</div>
        <div class="form-grid">
          <div class="form-group">
            <label>Date of Birth <span style="color:var(--magenta)">*</span></label>
            <input type="date" name="dob" value="<?= htmlspecialchars($post['dob'] ?? '') ?>" required />
          </div>
          <div class="form-group">
            <label>Time of Birth <span style="color:var(--magenta)">*</span></label>
            <input type="text" name="time_of_birth" id="tobInput"
              value="<?= htmlspecialchars($post['time_of_birth'] ?? '') ?>"
              placeholder="HH:MM &nbsp; e.g. 14:30 for 2:30 PM"
              pattern="([01][0-9]|2[0-3]):[0-5][0-9]"
              <?= isset($post['unknown_time']) ? 'disabled' : 'required' ?> />
            <label class="check-opt">
              <input type="checkbox" name="unknown_time" id="unknownTime" value="1" <?= isset($post['unknown_time']) ? 'checked' : '' ?>>
              I don't know my birth time
            </label>
            <p class="form-note">24-hour format. Use exact birth certificate time if available.</p>
          </div>
          <div class="form-group full">
            <label>Place of Birth <span style="color:var(--magenta)">*</span></label>
            <div class="autocomplete-wrap">
              <input type="text" name="place_of_birth" id="placeOfBirth"
                value="<?= htmlspecialchars($post['place_of_birth'] ?? '') ?>"
                placeholder="Start typing a city..." required autocomplete="off" />
              <div class="autocomplete-list" id="autocompleteList"></div>
            </div>
            <p class="form-note">Type your birth city and select from the list. This determines your rising sign and chart.</p>
          </div>
          <div class="form-group full">
            <label>Birth Timezone <span style="color:var(--magenta)">*</span></label>
            <select name="timezone" id="tzSelect" required>
              <option value="">Auto-selects from city above &mdash; or choose manually</option>
              <?php
              $tzones = [
                'Pacific/Honolulu'                 => 'Hawaii (HST, UTC-10)',
                'America/Anchorage'                => 'Alaska (AKST, UTC-9)',
                'America/Los_Angeles'              => 'Pacific (PST/PDT, UTC-8/-7)',
                'America/Denver'                   => 'Mountain (MST/MDT, UTC-7/-6)',
                'America/Phoenix'                  => 'Mountain No DST (MST, UTC-7)',
                'America/Chicago'                  => 'Central (CST/CDT, UTC-6/-5)',
                'America/New_York'                 => 'Eastern (EST/EDT, UTC-5/-4)',
                'America/Halifax'                  => 'Atlantic (AST/ADT, UTC-4/-3)',
                'America/St_Johns'                 => 'Newfoundland (NST/NDT, UTC-3:30/-2:30)',
                'America/Sao_Paulo'                => 'Brasilia (BRT, UTC-3)',
                'America/Argentina/Buenos_Aires'   => 'Argentina (ART, UTC-3)',
                'Atlantic/Reykjavik'               => 'UTC+0 / Reykjavik',
                'Europe/London'                    => 'London (GMT/BST, UTC+0/+1)',
                'Europe/Paris'                     => 'Central Europe (CET/CEST, UTC+1/+2)',
                'Europe/Helsinki'                  => 'Eastern Europe (EET/EEST, UTC+2/+3)',
                'Europe/Moscow'                    => 'Moscow (MSK, UTC+3)',
                'Asia/Dubai'                       => 'Gulf (GST, UTC+4)',
                'Asia/Kolkata'                     => 'India (IST, UTC+5:30)',
                'Asia/Dhaka'                       => 'Bangladesh (BST, UTC+6)',
                'Asia/Bangkok'                     => 'Indochina (ICT, UTC+7)',
                'Asia/Shanghai'                    => 'China (CST, UTC+8)',
                'Asia/Tokyo'                       => 'Japan (JST, UTC+9)',
                'Australia/Sydney'                 => 'Australia East (AEST/AEDT, UTC+10/+11)',
                'Pacific/Auckland'                 => 'New Zealand (NZST/NZDT, UTC+12/+13)',
              ];
              $sel = $post['timezone'] ?? '';
              foreach ($tzones as $tz => $label):
              ?>
                <option value="<?= $tz ?>" <?= $sel === $tz ? 'selected' : '' ?>><?= $label ?></option>
              <?php endforeach; ?>
            </select>
            <p class="form-note" id="tzNote" style="display:none;color:rgba(212,175,55,0.7);">Timezone auto-selected from your birth city.</p>
          </div>
        </div>

        <!-- CONTACT -->
        <div class="section-label section-gap">Contact</div>
        <div class="form-group">
          <label>Phone Number <span style="color:var(--magenta)">*</span></label>
          <input type="tel" name="phone" value="<?= htmlspecialchars($post['phone'] ?? '') ?>" required placeholder="Required" />
        </div>

        <!-- CAREER -->
        <div class="section-label section-gap">Career &amp; Expression</div>
        <div class="form-group full">
          <label>Career Field <span style="color:var(--magenta)">*</span></label>
          <select name="career_field" required>
            <?php foreach ($career_fields as $val => $label): ?>
              <option value="<?= htmlspecialchars($val) ?>" <?= ($post['career_field'] ?? '') === $val ? 'selected' : '' ?>><?= htmlspecialchars($label) ?></option>
            <?php endforeach; ?>
          </select>
        </div>
        <div class="form-group full">
          <label>How You Express Yourself in Your Work <span style="color:var(--magenta)">*</span></label>
          <select name="career_expression" required>
            <?php foreach ($career_expressions as $val => $label): ?>
              <option value="<?= htmlspecialchars($val) ?>" <?= ($post['career_expression'] ?? '') === $val ? 'selected' : '' ?>><?= htmlspecialchars($label) ?></option>
            <?php endforeach; ?>
          </select>
        </div>

        <!-- HEALTH DISCLOSURE -->
        <div class="section-label section-gap">Health &amp; Safety Disclosure</div>
        <div class="form-group full">
          <p style="font-size:14px;font-weight:300;color:var(--cream-dim);margin-bottom:18px;line-height:1.75;">Certain energy work practices and crystals used in this program may be contraindicated for individuals with implanted or electronic medical devices. This disclosure is required for your safety before any sessions begin.</p>
          <label>Do you currently have any implanted or electronic medical device? <span style="color:var(--magenta)">*</span></label>
          <p class="form-note" style="margin-bottom:14px;">Examples: pacemaker, insulin pump, neurostimulator, cochlear implant, deep brain stimulator, electronic cardiac monitor, or any similar device inside or attached to your body.</p>
          <div class="radio-group">
            <label class="radio-opt">
              <input type="radio" name="medical_device" value="0" <?= ($post['medical_device'] ?? '') === '0' ? 'checked' : '' ?>>
              No, I do not have any implanted or electronic medical devices
            </label>
            <label class="radio-opt">
              <input type="radio" name="medical_device" value="1" <?= ($post['medical_device'] ?? '') === '1' ? 'checked' : '' ?>>
              Yes, I have one or more implanted or electronic medical devices
            </label>
          </div>
        </div>
        <div class="form-group full" id="medDeviceDescGroup" style="<?= ($post['medical_device'] ?? '') === '1' ? '' : 'display:none;' ?>">
          <label>Please describe your device(s) <span style="color:var(--magenta)">*</span></label>
          <input type="text" name="medical_device_desc" id="medDeviceDescInput" value="<?= htmlspecialchars($post['medical_device_desc'] ?? '') ?>" placeholder="e.g. pacemaker implanted 2019, insulin pump" />
          <p class="form-note">Kept strictly confidential. Used only to ensure appropriate modifications to energy practices for your safety.</p>
        </div>

        <!-- AGREEMENTS -->
        <div class="section-label section-gap">Terms, Policies &amp; Agreements</div>
        <div class="form-group full">
          <p style="font-size:14px;font-weight:300;color:var(--cream-dim);margin-bottom:18px;line-height:1.75;">Click each section to read the full text before agreeing.</p>

          <div class="accord-wrap">
            <div class="accord-item">
              <div class="accord-header" onclick="toggleAccord(this)">
                <span>Terms &amp; Conditions &mdash; 6 Week Self Love Transformation Program</span>
                <span class="accord-arrow">&#9660;</span>
              </div>
              <div class="accord-body">
                <div class="accord-text">Effective Date: Program Purchase Date
Business Name: Phoenix Rebirth
Program Host: Christina Stevens, Awakening Catalyst and Soul Liberation Guide

1. AGREEMENT TO TERMS
By enrolling in the 6 Week Self Love Transformation Program, you acknowledge that you have read, understood, and agreed to these Terms and Conditions. Participation constitutes a legally binding agreement between you ("Participant") and Phoenix Rebirth ("Provider").

2. NATURE OF THE PROGRAM
This program is a personal development and energetic self-growth program designed to support participants in developing self-awareness, emotional healing, and self-love. The program may include: energy work sessions, guided emotional release processes, personal development coaching, spiritual and energetic practices, and educational materials and exercises. This program is NOT psychotherapy, medical treatment, or mental health counseling. Participants understand that results depend entirely on their own willingness to engage in the process and complete the work assigned.

3. PARTICIPANT RESPONSIBILITY
Participants acknowledge that they are fully responsible for their own emotional, physical, and mental well-being. The Provider cannot and will not do the work for them. Personal transformation requires active participation and commitment. Failure to complete exercises, attend sessions, or engage with the program may limit results.

4. ATTENDANCE POLICY
Participants agree to attend scheduled sessions. If a participant misses more than two (2) sessions, or demonstrates no effort to engage in the program or complete the work, the Provider reserves the right to remove the participant from the program without refund.

5. REFUND POLICY
Participants may request to withdraw within 15 days of enrollment. If withdrawal occurs within that period, no more than 50% of the original payment will be refunded. After 15 days from the date of enrollment, NO REFUNDS will be issued under any circumstances, including non-attendance, failure to complete assignments, personal scheduling conflicts, withdrawal due to lack of participation, personal dissatisfaction after enrollment, or failure to engage in the program work.

6. REMOVAL FROM PROGRAM
The Provider reserves the right to remove any participant who violates program guidelines, is disruptive, repeatedly misses sessions, or demonstrates no intention of participating. Removal does not qualify the participant for a refund.

7. CONFIDENTIALITY
Participants agree to maintain the confidentiality of other participants in group sessions. Sharing personal stories, identities, or experiences of other participants outside the program is strictly prohibited.

8. INTELLECTUAL PROPERTY
All materials provided in this program are the intellectual property of Phoenix Rebirth. Participants may not reproduce, share publicly, record sessions, or distribute materials. Violation may result in removal and legal action.

9. LIMITATION OF LIABILITY
Phoenix Rebirth and its representatives are not liable for any damages or losses resulting from participation, including emotional distress, personal decisions, relationship changes, lifestyle changes, or financial decisions.

10. PAYMENT DISPUTES AND CHARGEBACK PROTECTION
By enrolling, the Participant agrees not to initiate a payment dispute or chargeback without first contacting Phoenix Rebirth to attempt resolution. If a participant initiates a chargeback after agreeing to these terms, they will be considered in breach of contract.

11. NON-DEFAMATION AGREEMENT
Participants agree they will not make false, misleading, or defamatory statements about Phoenix Rebirth, its services, or its representatives on any public platform.

12. SPIRITUAL AND ENERGETIC SERVICES CLAUSE
Participants acknowledge that this program incorporates spiritual, intuitive, and energetic practices. These are personal development and spiritual guidance services, not medical, psychological, or licensed therapeutic services.

13. PROGRAM USE AND NON-RESALE
Participants agree they will not copy, teach, repackage, sell, or distribute program materials, recordings, guides, or journals. Materials are for personal use only.

GOVERNING LAW
This Agreement is governed by the laws of the United States and the State of New Mexico.

CLASS ACTION WAIVER
Any disputes will be handled on an individual basis only, not as part of any class, collective, or representative action.

EMOTIONAL RELEASE AND PERSONAL GROWTH ACKNOWLEDGMENT
Participants understand the program may involve deep emotional exploration. These are normal parts of personal development. Phoenix Rebirth is not liable for emotional responses during or after participation.

PERSONAL DECISIONS AND LIFE CHANGES CLAUSE
All decisions made during or after the program are the participant's sole responsibility. The Provider does not direct or control life decisions.</div>
              </div>
            </div>

            <div class="accord-item">
              <div class="accord-header" onclick="toggleAccord(this)">
                <span>Privacy Policy (HIPAA-Aware)</span>
                <span class="accord-arrow">&#9660;</span>
              </div>
              <div class="accord-body">
                <div class="accord-text">INFORMATION COLLECTED
The program may collect: name and contact information, questionnaire responses, personal reflections or journaling information, health disclosures relevant to energy work, and payment information. This information is collected solely for program participation and safety purposes.

HIPAA AWARENESS
While this program is not a medical service, the Provider respects principles similar to those outlined in HIPAA to protect participant confidentiality. Personal information will never be shared with third parties without consent, except when required by law.

DATA SECURITY
Reasonable measures are taken to protect your information, including secure digital storage, limited access to participant data, and protection of personal information shared in sessions. However, no electronic system can guarantee absolute security.

USE OF INFORMATION
Collected information is used solely for program delivery, personalizing coaching and guidance, and safety considerations for energy work. Information will not be sold, rented, or distributed for marketing purposes.</div>
              </div>
            </div>

            <div class="accord-item">
              <div class="accord-header" onclick="toggleAccord(this)">
                <span>Energy Work Disclaimer &amp; Informed Consent</span>
                <span class="accord-arrow">&#9660;</span>
              </div>
              <div class="accord-body">
                <div class="accord-text">NATURE OF ENERGY WORK
Energy work is a complementary wellness practice that may involve energy alignment, emotional release work, crystal-assisted energetic practices, and spiritual guidance. Energy work does NOT replace medical, psychological, or psychiatric care.

RESULTS ARE NOT GUARANTEED
Each participant's experience is unique. The Provider cannot guarantee specific outcomes. Personal transformation depends on willingness to engage, emotional readiness, consistency in completing exercises, and personal life circumstances.

PERSONAL RESPONSIBILITY
Participants accept full responsibility for their emotional responses, personal decisions, and actions taken during or after the program.

HEALTH DISCLOSURE REQUIREMENT
Participants MUST disclose any implanted or electronic medical devices, including pacemakers, insulin pumps, neurostimulators, or electronic monitoring devices. Certain crystals or energetic practices may be contraindicated for individuals with such devices. Failure to disclose releases the Provider from any liability.

PHYSICAL AND EMOTIONAL REACTIONS
Energy work may produce temporary sensations such as emotional releases, fatigue, tingling sensations, emotional processing, and shifts in awareness. These are considered normal parts of the energetic integration process.

VOLUNTARY PARTICIPATION
Participation is entirely voluntary. Participants may choose to discontinue practices if they feel uncomfortable.

RELEASE OF LIABILITY
By participating, the participant releases Phoenix Rebirth and its representatives from any liability related to emotional responses, personal decisions, physical sensations, or lifestyle changes resulting from participation.</div>
              </div>
            </div>

            <div class="accord-item">
              <div class="accord-header" onclick="toggleAccord(this)">
                <span>Community Rules &amp; Conduct Agreement &mdash; SoulReady Platform</span>
                <span class="accord-arrow">&#9660;</span>
              </div>
              <div class="accord-body">
                <div class="accord-text">A Phoenix Rebirth Platform — Effective March 2026

SoulReady is a sacred space built by Christina Stevens of Phoenix Rebirth for soul-level healing, self-discovery, and authentic community connection. These rules are not suggestions. They are non-negotiable standards of conduct every member agrees to the moment they create an account.

SECTION 1 — MEMBERSHIP STATUS
Alumni Status (Free): access to Soul Blueprint Reading, Community Chat, and free resources. Active Status (Paid): all alumni features plus direct messaging with Christina while enrolled in a course or booked session.

SECTION 2 — COMMUNITY CHAT RULES
STRICTLY PROHIBITED: Politics of any kind. Religious debates or recruitment. False information or misinformation. Harassment, bullying, or threatening behavior. Solicitation of services or products. Sharing another person's private data or reading without consent. Creating conflict or discord.

SECTION 3 — HARMONYHUB FOR PRACTITIONERS
SoulReady is not a platform for practitioners to promote services. Use HarmonyHub ($35/year) for that. Solicitation inside SoulReady: first violation = warning, second = permanent ban.

SECTION 4 — DIRECT MESSAGING WITH CHRISTINA
Direct messaging is exclusively for Active status members and must relate to your active booking or enrollment only. Misuse results in immediate termination of Active status and permanent ban.

SECTION 5 — VIOLATIONS AND ENFORCEMENT
ZERO TOLERANCE (Immediate Permanent Ban, no appeal): Political content. Religious debate or attack. Harassment or threats. Sharing another's private info. Creating significant discord. Misuse of direct messaging.

STANDARD VIOLATIONS (Warning then ban): Solicitation. Spreading unverified info. Minor conduct issues.

THE ALL PARTIES RULE: All parties in a violating conflict are subject to enforcement regardless of who started it. Permanent bans are permanent. No appeals. No exceptions.

SECTION 6 — READING DISCLAIMER
Soul Blueprint Readings are for spiritual guidance and self-reflection only. NOT a substitute for medical, psychological, legal, or financial advice.

SECTION 7 — PRIVACY AND DATA
Your birth data and readings are stored securely and never sold to third parties.

SECTION 8 — INTELLECTUAL PROPERTY
The Soul Blueprint Decoder system, Hebrew Metatron's Cube Frequency System, Phoenix Rebirth Numerology Framework, and all content are the exclusive intellectual property of Christina Stevens and Phoenix Rebirth.

SECTIONS 9-11 — PAYMENTS, CHANGES AND YOUR AGREEMENT
All payments processed via Stripe. Sessions are non-refundable once preparation email is sent. By creating an account you confirm you are 18 or older, have read these rules in full, and agree to abide by every rule without exception.</div>
              </div>
            </div>
          </div>

          <div class="agree-box">
            <label class="agree-label">
              <input type="checkbox" name="terms_agreed" value="1" <?= isset($post['terms_agreed']) ? 'checked' : '' ?>>
              <span>I confirm that I am <strong>18 years of age or older</strong>. I have read and understood the Terms &amp; Conditions, Privacy Policy, Energy Work Disclaimer, and Community Rules &amp; Conduct Agreement in their entirety. I agree to abide by all terms without exception.</span>
            </label>
          </div>
        </div>

        <button class="btn-primary btn-full" type="submit">Save &amp; Continue to Assessment &rarr;</button>
      </form>
    </div>
  </div>
</div>

<script>
// Same as last name checkbox
const sameMaiden  = document.getElementById('sameMaiden');
const maidenInput = document.getElementById('maidenName');
const lastInput   = document.getElementById('lastName');

function syncMaiden() {
  if (sameMaiden.checked) {
    maidenInput.value    = lastInput.value;
    maidenInput.readOnly = true;
    maidenInput.required = false;
  } else {
    maidenInput.readOnly = false;
    maidenInput.required = true;
    maidenInput.value    = '';
  }
}
sameMaiden.addEventListener('change', syncMaiden);
lastInput.addEventListener('input', function() {
  if (sameMaiden.checked) maidenInput.value = this.value;
});
// init
if (sameMaiden.checked) syncMaiden();

// Unknown birth time
const unknownTime = document.getElementById('unknownTime');
const tobInput    = document.getElementById('tobInput');
unknownTime.addEventListener('change', function() {
  if (this.checked) {
    tobInput.value    = '';
    tobInput.disabled = true;
    tobInput.required = false;
  } else {
    tobInput.disabled = false;
    tobInput.required = true;
  }
});
if (unknownTime.checked) { tobInput.disabled = true; tobInput.required = false; }

// Place of birth autocomplete
const placeInput       = document.getElementById('placeOfBirth');
const autocompleteList = document.getElementById('autocompleteList');
const tzSelect         = document.getElementById('tzSelect');
const tzNote           = document.getElementById('tzNote');
let acTimeout;

placeInput.addEventListener('input', function() {
  clearTimeout(acTimeout);
  const val = this.value.trim();
  if (val.length < 3) { autocompleteList.style.display = 'none'; return; }
  acTimeout = setTimeout(async () => {
    try {
      const r    = await fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(val) + '&limit=6&addressdetails=1', { headers: { 'Accept-Language': 'en' } });
      const data = await r.json();
      if (!data || !data.length) { autocompleteList.style.display = 'none'; return; }
      autocompleteList.innerHTML = '';
      data.forEach(function(item) {
        const city    = item.address.city || item.address.town || item.address.village || item.address.county || item.name;
        const state   = item.address.state || '';
        const country = item.address.country || '';
        const display = [city, state, country].filter(Boolean).join(', ');
        const div = document.createElement('div');
        div.className   = 'autocomplete-item';
        div.textContent = display;
        div.addEventListener('mousedown', function(e) {
          e.preventDefault();
          placeInput.value = display;
          document.getElementById('lat').value = item.lat;
          document.getElementById('lng').value = item.lon;
          autocompleteList.style.display = 'none';
          lookupTimezone(item.lat, item.lon);
        });
        autocompleteList.appendChild(div);
      });
      autocompleteList.style.display = 'block';
    } catch(e) { autocompleteList.style.display = 'none'; }
  }, 400);
});

placeInput.addEventListener('blur', function() {
  setTimeout(function() { autocompleteList.style.display = 'none'; }, 200);
});

// Timezone lookup from coordinates
async function lookupTimezone(lat, lon) {
  try {
    const r    = await fetch('https://timeapi.io/api/TimeZone/coordinate?latitude=' + lat + '&longitude=' + lon);
    const data = await r.json();
    if (data && data.timeZone) {
      const opt = tzSelect.querySelector('option[value="' + data.timeZone + '"]');
      if (opt) {
        tzSelect.value = data.timeZone;
        tzNote.style.display = '';
      }
    }
  } catch(e) {}
}

// Medical device show/hide
document.querySelectorAll('[name="medical_device"]').forEach(function(radio) {
  radio.addEventListener('change', function() {
    const descGroup = document.getElementById('medDeviceDescGroup');
    const descInput = document.getElementById('medDeviceDescInput');
    if (this.value === '1') {
      descGroup.style.display = '';
      descInput.required = true;
    } else {
      descGroup.style.display = 'none';
      descInput.required = false;
    }
  });
});

// Accordion
function toggleAccord(header) {
  const body  = header.nextElementSibling;
  const arrow = header.querySelector('.accord-arrow');
  const isOpen = body.classList.contains('open');
  body.classList.toggle('open');
  arrow.innerHTML = isOpen ? '&#9660;' : '&#9650;';
}
</script>

<?php include 'includes/footer.php'; ?>
</body>
</html>
