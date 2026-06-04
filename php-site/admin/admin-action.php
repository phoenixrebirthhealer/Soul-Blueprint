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

if (!$client_id) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid client']);
    exit;
}

$allowed_types = ['name_frequency', 'relational_tier1', 'self_love_language', 'tcm_astrology_tier1', 'soul_blueprint_tier1'];

// Only validate reading type for actions that require it
$type_required_actions = ['ensure_paid', 'save_job', 'check_job'];
if (in_array($action, $type_required_actions, true) && !in_array($type, $allowed_types, true)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid reading type']);
    exit;
}

$db = get_db();

// Verify client exists
$client_check = $db->prepare('SELECT id FROM clients WHERE id = ?');
$client_check->execute([$client_id]);
if (!$client_check->fetch()) {
    http_response_code(404);
    echo json_encode(['error' => 'Client not found']);
    exit;
}

// -------------------------------------------------------
// auto_calculate
// Calls Railway /chart and stores result
// -------------------------------------------------------
if ($action === 'auto_calculate') {
    // Ensure client_calculations table exists
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

    // Get client birth data
    $c = $db->prepare('SELECT dob, time_of_birth, place_of_birth, timezone, latitude, longitude FROM clients WHERE id=?');
    $c->execute([$client_id]);
    $client_row = $c->fetch();

    if (!$client_row || !$client_row['dob']) {
        echo json_encode(['error' => 'Client missing date of birth']);
        exit;
    }

    // Build payload for Railway /chart
    $payload = [
        'date' => $client_row['dob'],
        'time' => $client_row['time_of_birth'] ?: '12:00',
    ];

    // Prefer IANA timezone name, fall back to offset from UI
    if (!empty($client_row['timezone'])) {
        $payload['timezone'] = $client_row['timezone'];
    } elseif (isset($input['tz_offset'])) {
        $payload['timezoneOffset'] = floatval($input['tz_offset']);
    }

    // Location: prefer lat/lon, fall back to place string
    if (!empty($client_row['latitude']) && !empty($client_row['longitude'])) {
        $payload['latitude']  = floatval($client_row['latitude']);
        $payload['longitude'] = floatval($client_row['longitude']);
    } elseif (!empty($client_row['place_of_birth'])) {
        $payload['location'] = $client_row['place_of_birth'];
    } else {
        echo json_encode(['error' => 'Client missing location data']);
        exit;
    }

    // Call Railway /chart
    $ch = curl_init(RAILWAY_API . '/chart');
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => json_encode($payload),
        CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 60,
    ]);
    $raw  = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if (!$raw || $code !== 200) {
        echo json_encode(['error' => 'Railway API error (HTTP ' . $code . ')']);
        exit;
    }

    $chart = json_decode($raw, true);
    if (!$chart) {
        echo json_encode(['error' => 'Invalid response from Railway']);
        exit;
    }

    // Upsert into client_calculations
    $existing = $db->prepare('SELECT id FROM client_calculations WHERE client_id=?');
    $existing->execute([$client_id]);
    if ($existing->fetch()) {
        $db->prepare('UPDATE client_calculations SET astrology_data=?, calculated_at=NOW(), updated_at=NOW() WHERE client_id=?')
           ->execute([json_encode($chart), $client_id]);
    } else {
        $db->prepare('INSERT INTO client_calculations (client_id, astrology_data, calculated_at, updated_at) VALUES (?,?,NOW(),NOW())')
           ->execute([$client_id, json_encode($chart)]);
    }

    echo json_encode(['ok' => true, 'type' => $chart['summary']['derived']['type'] ?? 'calculated']);
    exit;
}

// -------------------------------------------------------
// save_tier2
// Saves Tier 2 neuro or clairs notes
// -------------------------------------------------------
if ($action === 'save_tier2') {
    $field = $input['field'] ?? '';
    $value = $input['value'] ?? '';

    if (!in_array($field, ['tier2_neuro', 'tier2_clairs'], true)) {
        echo json_encode(['error' => 'Invalid field']);
        exit;
    }

    // Ensure table exists
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

    $existing = $db->prepare('SELECT id FROM client_calculations WHERE client_id=?');
    $existing->execute([$client_id]);
    if ($existing->fetch()) {
        $db->prepare("UPDATE client_calculations SET {$field}=?, updated_at=NOW() WHERE client_id=?")
           ->execute([$value, $client_id]);
    } else {
        $db->prepare("INSERT INTO client_calculations (client_id, {$field}, updated_at) VALUES (?,?,NOW())")
           ->execute([$client_id, $value]);
    }

    echo json_encode(['ok' => true]);
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
        if (in_array($row['status'], ['error', 'pending'], true)) {
            $upd = $db->prepare('UPDATE readings SET status = "generating", job_id = NULL, file_name = NULL, paid = 1, error_message = NULL, updated_at = NOW() WHERE id = ?');
            $upd->execute([$row['id']]);
            $reading_id = $row['id'];
        } else {
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
    $job_id = trim($input['job_id'] ?? '');

    if (!$job_id) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing job_id']);
        exit;
    }

    // Find the most recent generating record for this client/type
    $r = $db->prepare('SELECT id FROM readings WHERE client_id = ? AND reading_type = ? ORDER BY created_at DESC LIMIT 1');
    $r->execute([$client_id, $type]);
    $row = $r->fetch();

    if (!$row) {
        http_response_code(404);
        echo json_encode(['error' => 'Reading record not found']);
        exit;
    }

    $upd = $db->prepare('UPDATE readings SET job_id = ?, status = "generating", updated_at = NOW() WHERE id = ? AND client_id = ?');
    $upd->execute([$job_id, $row['id'], $client_id]);

    echo json_encode(['ok' => true]);
    exit;
}

// -------------------------------------------------------
// check_job
// Polls Railway for job status; saves file when complete
// -------------------------------------------------------
if ($action === 'check_job') {
    $job_id = trim($input['job_id'] ?? '');

    if (!$job_id) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing job_id']);
        exit;
    }

    // Find the reading record
    $r = $db->prepare('SELECT id, status, file_name FROM readings WHERE client_id = ? AND reading_type = ? ORDER BY created_at DESC LIMIT 1');
    $r->execute([$client_id, $type]);
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

    $data    = json_decode($raw, true);
    $jstatus = $data['status'] ?? 'generating';

    if ($jstatus === 'complete') {
        $html = $data['result'] ?? '';
        if (!$html) {
            $db->prepare('UPDATE readings SET status = "error", error_message = "Empty result from Railway", updated_at = NOW() WHERE id = ?')
               ->execute([$reading['id']]);
            echo json_encode(['status' => 'error', 'message' => 'Empty result from Railway']);
            exit;
        }

        $readings_dir = READINGS_DIR;
        if (!is_dir($readings_dir)) {
            mkdir($readings_dir, 0755, true);
        }

        $file_name = bin2hex(random_bytes(16)) . '.html';
        file_put_contents($readings_dir . $file_name, $html);

        $db->prepare('UPDATE readings SET status = "complete", file_name = ?, updated_at = NOW() WHERE id = ?')
           ->execute([$file_name, $reading['id']]);

        echo json_encode(['status' => 'complete', 'file' => $file_name]);
        exit;
    }

    if ($jstatus === 'failed') {
        $msg = $data['error'] ?? 'Generation failed';
        $db->prepare('UPDATE readings SET status = "error", error_message = ?, updated_at = NOW() WHERE id = ?')
           ->execute([$msg, $reading['id']]);
        echo json_encode(['status' => 'error', 'message' => $msg]);
        exit;
    }

    echo json_encode(['status' => 'generating']);
    exit;
}

http_response_code(400);
echo json_encode(['error' => 'Unknown action']);
