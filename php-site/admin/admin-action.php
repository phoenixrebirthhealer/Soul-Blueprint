<?php
require_once __DIR__ . '/includes/admin-auth.php';
admin_require_login();

header('Content-Type: application/json');

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid request']);
    exit;
}

$token = $input['csrf'] ?? '';
if (!hash_equals(admin_csrf(), $token)) {
    http_response_code(403);
    echo json_encode(['error' => 'Invalid CSRF token']);
    exit;
}

$action    = $input['action'] ?? '';
$client_id = intval($input['client_id'] ?? 0);
$type      = $input['reading_type'] ?? '';

$allowed_types = ['name_frequency', 'relational_name_frequency', 'self_love_language', 'tcm_astrology', 'soul_blueprint'];

if (!$client_id || !in_array($type, $allowed_types, true)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid client or reading type']);
    exit;
}

$db = get_db();

// Verify client exists
$client = $db->prepare('SELECT id FROM clients WHERE id = ?');
$client->execute([$client_id]);
if (!$client->fetch()) {
    http_response_code(404);
    echo json_encode(['error' => 'Client not found']);
    exit;
}

// -------------------------------------------------------
// ensure_paid
// Creates or updates a reading record to paid/generating
// -------------------------------------------------------
if ($action === 'ensure_paid') {
    $existing = $db->prepare('SELECT id, status FROM readings WHERE client_id = ? AND reading_type = ? ORDER BY created_at DESC LIMIT 1');
    $existing->execute([$client_id, $type]);
    $row = $existing->fetch();

    if ($row) {
        // Reset to generating if previously errored or pending
        if (in_array($row['status'], ['error', 'pending'], true)) {
            $upd = $db->prepare('UPDATE readings SET status = "generating", job_id = NULL, file_name = NULL, paid = 1, error_message = NULL, updated_at = NOW() WHERE id = ?');
            $upd->execute([$row['id']]);
            $reading_id = $row['id'];
        } else {
            // complete or generating -- mark paid and return id
            $db->prepare('UPDATE readings SET paid = 1, updated_at = NOW() WHERE id = ?')->execute([$row['id']]);
            $reading_id = $row['id'];
        }
    } else {
        $ins = $db->prepare('INSERT INTO readings (client_id, reading_type, status, paid) VALUES (?, ?, "generating", 1)');
        $ins->execute([$client_id, $type]);
        $reading_id = $db->lastInsertId();
    }

    echo json_encode(['ok' => true, 'reading_id' => $reading_id]);
    exit;
}

// -------------------------------------------------------
// save_job
// Stores the Railway job_id on the reading record
// -------------------------------------------------------
if ($action === 'save_job') {
    $reading_id = intval($input['reading_id'] ?? 0);
    $job_id     = trim($input['job_id'] ?? '');

    if (!$reading_id || !$job_id) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing reading_id or job_id']);
        exit;
    }

    $upd = $db->prepare('UPDATE readings SET job_id = ?, status = "generating", updated_at = NOW() WHERE id = ? AND client_id = ?');
    $upd->execute([$job_id, $reading_id, $client_id]);

    echo json_encode(['ok' => true]);
    exit;
}

// -------------------------------------------------------
// check_job
// Polls Railway for job status; saves file when complete
// -------------------------------------------------------
if ($action === 'check_job') {
    $reading_id = intval($input['reading_id'] ?? 0);
    $job_id     = trim($input['job_id'] ?? '');

    if (!$reading_id || !$job_id) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing reading_id or job_id']);
        exit;
    }

    // Confirm reading belongs to this client
    $r = $db->prepare('SELECT id, status, file_name FROM readings WHERE id = ? AND client_id = ?');
    $r->execute([$reading_id, $client_id]);
    $reading = $r->fetch();

    if (!$reading) {
        http_response_code(404);
        echo json_encode(['error' => 'Reading not found']);
        exit;
    }

    if ($reading['status'] === 'complete') {
        echo json_encode(['status' => 'complete', 'file' => $reading['file_name']]);
        exit;
    }

    // Poll Railway
    $railway_url = RAILWAY_API . '/job-status/' . urlencode($job_id);
    $ch = curl_init($railway_url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 15,
        CURLOPT_HTTPHEADER     => ['Accept: application/json'],
    ]);
    $raw  = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if (!$raw || $code !== 200) {
        echo json_encode(['status' => 'generating']);
        exit;
    }

    $data   = json_decode($raw, true);
    $jstatus = $data['status'] ?? 'generating';

    if ($jstatus === 'complete') {
        $html = $data['result'] ?? '';
        if (!$html) {
            $db->prepare('UPDATE readings SET status = "error", error_message = "Empty result from Railway", updated_at = NOW() WHERE id = ?')->execute([$reading_id]);
            echo json_encode(['status' => 'error', 'message' => 'Empty result from Railway']);
            exit;
        }

        $readings_dir = READINGS_DIR;
        if (!is_dir($readings_dir)) {
            mkdir($readings_dir, 0755, true);
        }

        $file_name = bin2hex(random_bytes(16)) . '.html';
        file_put_contents($readings_dir . $file_name, $html);

        $db->prepare('UPDATE readings SET status = "complete", file_name = ?, updated_at = NOW() WHERE id = ?')->execute([$file_name, $reading_id]);

        echo json_encode(['status' => 'complete', 'file' => $file_name]);
        exit;
    }

    if ($jstatus === 'failed') {
        $msg = $data['error'] ?? 'Generation failed';
        $db->prepare('UPDATE readings SET status = "error", error_message = ?, updated_at = NOW() WHERE id = ?')->execute([$msg, $reading_id]);
        echo json_encode(['status' => 'error', 'message' => $msg]);
        exit;
    }

    echo json_encode(['status' => 'generating']);
    exit;
}

http_response_code(400);
echo json_encode(['error' => 'Unknown action']);
