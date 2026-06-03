<?php
require_once 'includes/auth.php';
require_once 'includes/config.php';

header('Content-Type: application/json');

if (!is_logged_in()) {
    echo json_encode(['status' => 'error', 'message' => 'Not logged in']);
    exit;
}

$reading_id = intval($_GET['id'] ?? 0);
if (!$reading_id) {
    echo json_encode(['status' => 'error', 'message' => 'Invalid reading']);
    exit;
}

$db   = get_db();
$stmt = $db->prepare('SELECT * FROM readings WHERE id = ? AND client_id = ?');
$stmt->execute([$reading_id, $_SESSION['client_id']]);
$reading = $stmt->fetch();

if (!$reading) {
    echo json_encode(['status' => 'error', 'message' => 'Reading not found']);
    exit;
}

if ($reading['status'] === 'complete') {
    echo json_encode(['status' => 'complete', 'file' => $reading['file_name']]);
    exit;
}

if ($reading['status'] === 'error') {
    echo json_encode(['status' => 'error', 'message' => $reading['error_message'] ?? 'Generation failed']);
    exit;
}

// Check Railway job status
$job_id = $reading['job_id'] ?? '';
if (!$job_id) {
    echo json_encode(['status' => 'generating']);
    exit;
}

$ch = curl_init(RAILWAY_API . '/job-status/' . urlencode($job_id));
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 10,
]);
$job_resp = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http_code === 404) {
    echo json_encode(['status' => 'generating']);
    exit;
}

$job = json_decode($job_resp, true);
$job_status = $job['status'] ?? 'running';

if ($job_status === 'complete') {
    $html = $job['result'] ?? '';

    if (!$html) {
        $db->prepare('UPDATE readings SET status=?, error_message=? WHERE id=?')
           ->execute(['error', 'Empty HTML returned from generation', $reading_id]);
        echo json_encode(['status' => 'error', 'message' => 'Generation produced empty result']);
        exit;
    }

    // Save HTML to readings directory
    if (!is_dir(READINGS_DIR)) {
        mkdir(READINGS_DIR, 0755, true);
    }

    $file_name = bin2hex(random_bytes(16)) . '.html';
    $file_path = READINGS_DIR . $file_name;

    if (file_put_contents($file_path, $html) === false) {
        $db->prepare('UPDATE readings SET status=?, error_message=? WHERE id=?')
           ->execute(['error', 'Could not save reading file', $reading_id]);
        echo json_encode(['status' => 'error', 'message' => 'Could not save file']);
        exit;
    }

    $db->prepare('UPDATE readings SET status=?, file_name=? WHERE id=?')
       ->execute(['complete', $file_name, $reading_id]);

    echo json_encode(['status' => 'complete', 'file' => $file_name]);

} elseif ($job_status === 'failed') {
    $err = $job['error'] ?? 'Unknown error';
    $db->prepare('UPDATE readings SET status=?, error_message=? WHERE id=?')
       ->execute(['error', $err, $reading_id]);
    echo json_encode(['status' => 'error', 'message' => $err]);
} else {
    echo json_encode(['status' => 'generating']);
}
