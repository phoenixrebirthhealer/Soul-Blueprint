<?php
require_once 'includes/auth.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /assessment');
    exit;
}

// If already logged in and just redoing assessment
if (is_logged_in()) {
    verify_csrf();
    if (has_completed_assessment()) {
        header('Location: /dashboard');
        exit;
    }
    $client_id = $_SESSION['client_id'];
    $db = get_db();
    goto save_assessment;
}

// New registration flow -- require session data from all 3 steps
if (empty($_SESSION['reg']) || empty($_SESSION['intake'])) {
    header('Location: /register');
    exit;
}

verify_csrf();

// Score the assessment first -- all answers must be present
$scored = [1,2,3,4,5,6,7,8,15,16,17,18,19,20,21,22,24];
$score = 0;
foreach ($scored as $n) {
    $val = intval($_POST['q' . $n] ?? 0);
    if ($val < 1) {
        header('Location: /assessment?error=incomplete');
        exit;
    }
    $score += max(0, min(5, $val));
}

$att_counts = ['S' => 0, 'A' => 0, 'V' => 0, 'D' => 0];
for ($i = 9; $i <= 14; $i++) {
    $v = strtoupper(trim($_POST['q' . $i] ?? ''));
    if (!isset($att_counts[$v])) {
        header('Location: /assessment?error=incomplete');
        exit;
    }
    $att_counts[$v]++;
}

$readiness = intval($_POST['q23'] ?? 0);

$answers = [];
for ($i = 1; $i <= 24; $i++) {
    $answers['q' . $i] = $_POST['q' . $i] ?? '';
}

$attachment_style = classify_attachment(
    $att_counts['S'], $att_counts['A'], $att_counts['V'], $att_counts['D']
);

// All data collected -- now create the account
$db = get_db();

$check = $db->prepare('SELECT id FROM clients WHERE email = ?');
$check->execute([$_SESSION['reg']['email']]);
if ($check->fetch()) {
    // Account already exists (e.g. double submit) -- just log in
    $row = $check->fetch();
    $_SESSION['client_id'] = $row['id'];
    unset($_SESSION['reg'], $_SESSION['intake'], $_SESSION['assessment_answers']);
    header('Location: /dashboard');
    exit;
}

$ins = $db->prepare('INSERT INTO clients (
    email, password_hash,
    first_name, middle_name, last_name, maiden_name,
    dob, time_of_birth, timezone, place_of_birth,
    latitude, longitude, phone,
    career_field, career_expression,
    medical_device, medical_device_desc, terms_agreed_at,
    intake_complete
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)');

$intake = $_SESSION['intake'];
$ins->execute([
    $_SESSION['reg']['email'],
    $_SESSION['reg']['password_hash'],
    $intake['first_name'],
    $intake['middle_name'],
    $intake['last_name'],
    $intake['maiden_name'],
    $intake['dob'],
    $intake['time_of_birth'],
    $intake['timezone'],
    $intake['place_of_birth'],
    $intake['latitude'],
    $intake['longitude'],
    $intake['phone'],
    $intake['career_field'],
    $intake['career_expression'],
    $intake['medical_device'] ?? 0,
    $intake['medical_device_desc'] ?? null,
    $intake['terms_agreed_at'] ?? null,
]);

$client_id = $db->lastInsertId();
$_SESSION['client_id'] = $client_id;

save_assessment:
$stmt = $db->prepare('INSERT INTO assessments
    (client_id, self_love_score, attachment_style, attachment_counts, answers, readiness_score)
    VALUES (?, ?, ?, ?, ?, ?)');
$stmt->execute([
    $client_id,
    $score,
    $attachment_style,
    json_encode($att_counts),
    json_encode($answers),
    $readiness,
]);

unset($_SESSION['reg'], $_SESSION['intake'], $_SESSION['assessment_answers']);

header('Location: /dashboard');
exit;
