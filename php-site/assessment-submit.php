<?php
require_once 'includes/auth.php';
require_intake();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /assessment');
    exit;
}

verify_csrf();

if (has_completed_assessment()) {
    header('Location: /dashboard');
    exit;
}

// Scored questions (Q1-Q8, Q15-Q24 except Q23): 5 points max each = 85 total
$scored = [1,2,3,4,5,6,7,8,15,16,17,18,19,20,21,22,24];
$score = 0;
foreach ($scored as $n) {
    $val = intval($_POST['q' . $n] ?? 0);
    $score += max(0, min(5, $val));
}

// Attachment questions (Q9-Q14): S/A/V/D
$att_counts = ['S' => 0, 'A' => 0, 'V' => 0, 'D' => 0];
for ($i = 9; $i <= 14; $i++) {
    $val = strtoupper(trim($_POST['q' . $i] ?? ''));
    if (isset($att_counts[$val])) {
        $att_counts[$val]++;
    }
}

$attachment_style = classify_attachment(
    $att_counts['S'],
    $att_counts['A'],
    $att_counts['V'],
    $att_counts['D']
);

$readiness = intval($_POST['q23'] ?? 0);

// Collect all answers
$answers = [];
for ($i = 1; $i <= 24; $i++) {
    $answers['q' . $i] = $_POST['q' . $i] ?? '';
}

$db = get_db();
$stmt = $db->prepare('INSERT INTO assessments
    (client_id, self_love_score, attachment_style, attachment_counts, answers, readiness_score)
    VALUES (?, ?, ?, ?, ?, ?)');
$stmt->execute([
    $_SESSION['client_id'],
    $score,
    $attachment_style,
    json_encode($att_counts),
    json_encode($answers),
    $readiness,
]);

header('Location: /dashboard');
exit;
