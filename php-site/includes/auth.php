<?php
require_once __DIR__ . '/db.php';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

function is_logged_in(): bool {
    return !empty($_SESSION['client_id']);
}

function require_login(): void {
    if (!is_logged_in()) {
        header('Location: /login');
        exit;
    }
}

function get_client(): ?array {
    if (!is_logged_in()) return null;
    $db = get_db();
    $stmt = $db->prepare('SELECT * FROM clients WHERE id = ?');
    $stmt->execute([$_SESSION['client_id']]);
    return $stmt->fetch() ?: null;
}

function get_assessment(): ?array {
    if (!is_logged_in()) return null;
    $db = get_db();
    $stmt = $db->prepare('SELECT * FROM assessments WHERE client_id = ? ORDER BY completed_at DESC LIMIT 1');
    $stmt->execute([$_SESSION['client_id']]);
    return $stmt->fetch() ?: null;
}

function has_completed_intake(): bool {
    $client = get_client();
    return $client && !empty($client['intake_complete']);
}

function has_completed_assessment(): bool {
    return get_assessment() !== null;
}

function require_intake(): void {
    require_login();
    if (!has_completed_intake()) {
        header('Location: /intake');
        exit;
    }
}

function require_assessment(): void {
    require_intake();
    if (!has_completed_assessment()) {
        header('Location: /assessment');
        exit;
    }
}

function csrf_token(): string {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function verify_csrf(): void {
    $token = $_POST['csrf_token'] ?? '';
    if (!hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
        http_response_code(403);
        die('Invalid request.');
    }
}

function classify_attachment(int $s, int $a, int $v, int $d): string {
    if ($s >= 4) return 'Secure';
    if ($a >= 4 && $d <= 1 && $v <= 1) return 'Pure Anxious';
    if ($v >= 4 && $d <= 1 && $a <= 1) return 'Pure Avoidant';
    if ($d >= 4) return 'Pure Disorganized';
    if ($d >= 2) {
        if ($a > $v) return 'Disorganized Anxious Leaning';
        if ($v > $a) return 'Disorganized Avoidant Leaning';
        return 'True Disorganized Equal Split';
    }
    if ($a >= 3 && $a > $v) return 'Pure Anxious';
    if ($v >= 3 && $v > $a) return 'Pure Avoidant';
    if ($d >= 1 && $a >= 1 && $v >= 1) return 'True Disorganized Equal Split';
    if ($a >= 2 && $v >= 2) return 'True Disorganized Equal Split';
    if ($a > $v) return 'Pure Anxious';
    if ($v > $a) return 'Pure Avoidant';
    return 'Secure';
}

function get_self_love_tier(int $score): string {
    if ($score >= 68) return 'Thriving Self-Love Foundation';
    if ($score >= 51) return 'Developing Self-Love Foundation';
    if ($score >= 34) return 'Emerging Self-Love Foundation';
    return 'Low Self-Love Foundation';
}
