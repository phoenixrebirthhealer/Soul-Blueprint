<?php
require_once 'includes/auth.php';
require_once 'includes/config.php';

header('Content-Type: application/json');

if (!is_logged_in()) {
    echo json_encode(['ok' => false, 'error' => 'Not logged in']);
    exit;
}

$raw  = file_get_contents('php://input');
$body = json_decode($raw, true);

if (!$body || !isset($body['csrf']) || !hash_equals($_SESSION['csrf_token'] ?? '', $body['csrf'])) {
    echo json_encode(['ok' => false, 'error' => 'Invalid request']);
    exit;
}

$responses = $body['responses'] ?? [];
if (!is_array($responses) || count($responses) !== 22) {
    echo json_encode(['ok' => false, 'error' => 'Invalid response data']);
    exit;
}

// Sanitize each response — only keep known fields, no HTML
$clean = [];
foreach ($responses as $r) {
    $clean[] = [
        'letter_id'       => intval($r['letterId'] ?? 0),
        'letter_name'     => substr(preg_replace('/[^A-Za-z\s]/', '', $r['letterName'] ?? ''), 0, 32),
        'pronounced'      => substr(htmlspecialchars($r['pronounced'] ?? '', ENT_QUOTES, 'UTF-8'), 0, 64),
        'felt_response'   => substr(trim($r['feltResponse'] ?? ''), 0, 2000),
        'notes'           => substr(trim($r['notes'] ?? ''), 0, 1000),
        'response_time_ms'=> intval($r['responseTimeMs'] ?? 0),
    ];
}

$db = get_db();

try {
    $db->exec('CREATE TABLE IF NOT EXISTS hebrew_responses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        client_id INT NOT NULL,
        responses_json MEDIUMTEXT NOT NULL,
        completed_at DATETIME NOT NULL,
        UNIQUE KEY uq_client (client_id)
    )');
} catch (Exception $e) {}

try {
    $stmt = $db->prepare('INSERT INTO hebrew_responses (client_id, responses_json, completed_at)
        VALUES (?, ?, NOW())
        ON DUPLICATE KEY UPDATE responses_json=VALUES(responses_json), completed_at=NOW()');
    $stmt->execute([$_SESSION['client_id'], json_encode($clean)]);
    echo json_encode(['ok' => true]);
} catch (Exception $e) {
    echo json_encode(['ok' => false, 'error' => 'Could not save responses']);
}
