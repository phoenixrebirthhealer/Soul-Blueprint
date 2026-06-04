<?php
require_once 'includes/auth.php';
require_once 'includes/config.php';
require_assessment();

$type     = $_GET['type'] ?? '';
$order_id = $_GET['token'] ?? '';

if (!$type || !$order_id) {
    header('Location: /dashboard');
    exit;
}

$client = get_client();
$first  = $client['first_name'] ?? '';
$middle = $client['middle_name'] ?? '';
$maiden = ($client['maiden_name'] && $client['maiden_name'] !== $client['last_name'])
    ? $client['maiden_name'] : $client['last_name'] ?? '';
$client_name = trim(implode(' ', array_filter([$first, $middle, $maiden])));

$reading_prices = ['name_frequency' => 1099];
$price_cents = $reading_prices[$type] ?? 1099;

$capture_payload = json_encode([
    'order_id'            => $order_id,
    'client_name'         => $client_name,
    'client_email'        => $client['email'] ?? '',
    'service_name'        => 'Name Frequency Reading',
    'service_price_cents' => $price_cents,
    'charged_price_cents' => $price_cents,
]);

$ch = curl_init(RAILWAY_API . '/paypal/capture-order');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $capture_payload,
    CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 30,
]);
$capture_resp = curl_exec($ch);
$capture_data = json_decode($capture_resp, true);
curl_close($ch);

$payment_ok = ($capture_data['status'] ?? '') === 'confirmed';
$capture_error = $capture_data['error'] ?? 'Payment capture failed';

$reading_id = null;
$job_id     = null;

if ($payment_ok) {
    $db = get_db();

    $existing = $db->prepare('SELECT id FROM readings WHERE client_id = ? AND reading_type = ? AND paypal_order_id = ?');
    $existing->execute([$_SESSION['client_id'], $type, $order_id]);
    $row = $existing->fetch();

    if (!$row) {
        $ins = $db->prepare('INSERT INTO readings (client_id, reading_type, status, paypal_order_id, paid, amount_cents)
            VALUES (?, ?, ?, ?, 1, ?)');
        $ins->execute([$_SESSION['client_id'], $type, 'generating', $order_id, $price_cents]);
        $reading_id = $db->lastInsertId();
    } else {
        $reading_id = $row['id'];
    }

    $gen_payload = json_encode([
        'first_name'  => $first,
        'middle_name' => $middle,
        'last_name'   => $maiden,
    ]);

    $ch = curl_init(RAILWAY_API . '/generate-name-frequency');
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $gen_payload,
        CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 15,
    ]);
    $gen_resp = curl_exec($ch);
    $gen_data = json_decode($gen_resp, true);
    curl_close($ch);

    $job_id = $gen_data['job_id'] ?? null;
    if ($job_id) {
        $db->prepare('UPDATE readings SET job_id = ? WHERE id = ?')->execute([$job_id, $reading_id]);
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Processing | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; }
    .main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 120px 40px 80px; text-align: center; }
    .box { max-width: 500px; }
    .spinner { display: inline-block; width: 48px; height: 48px; border: 2px solid rgba(212,175,55,0.15); border-top-color: var(--gold); border-radius: 50%; animation: spin 0.9s linear infinite; margin-bottom: 28px; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .box h1 { font-family: 'Cinzel', serif; font-size: clamp(20px,2.5vw,30px); font-weight: 400; color: var(--cream); margin-bottom: 14px; }
    .box p { font-size: 16px; font-weight: 300; color: var(--cream-dim); line-height: 1.8; }
    .error-box { background: rgba(194,24,91,0.1); border: 1px solid rgba(194,24,91,0.3); padding: 24px; }
    .error-box h1 { color: #f48fb1; }
  </style>
</head>
<body>
<?php include 'includes/nav.php'; ?>

<div class="main">
  <?php if (!$payment_ok): ?>
  <div class="box error-box">
    <h1>Payment Issue</h1>
    <p>Your payment may have been processed but confirmation failed. Please contact Christina at <a href="mailto:christina@phoenixrebirth.life" style="color:var(--gold)">christina@phoenixrebirth.life</a> with your PayPal receipt.</p>
    <p style="margin-top:16px;font-size:13px;opacity:0.5;"><?= htmlspecialchars($capture_error) ?></p>
  </div>
  <?php else: ?>
  <div class="box">
    <div class="spinner"></div>
    <h1>Payment Confirmed</h1>
    <p>Your Name Frequency Reading is being generated. This takes about a minute. You'll be redirected automatically when it's ready.</p>
  </div>
  <?php endif; ?>
</div>

<?php if ($payment_ok): ?>
<script>
const readingId = <?= intval($reading_id) ?>;
const jobId = <?= $job_id ? json_encode($job_id) : 'null' ?>;

async function checkStatus() {
  try {
    const resp = await fetch('/reading-status.php?id=' + readingId);
    const data = await resp.json();
    if (data.status === 'complete') {
      window.location.href = '/dashboard';
    } else if (data.status === 'error') {
      document.querySelector('.box').innerHTML = '<h1 style="color:#f48fb1">Generation Failed</h1><p>' + (data.message || 'Please contact Christina directly.') + '</p><a href="/dashboard" class="btn-primary">Go to Dashboard</a>';
    } else {
      setTimeout(checkStatus, 4000);
    }
  } catch(e) {
    setTimeout(checkStatus, 5000);
  }
}

setTimeout(checkStatus, 5000);
</script>
<?php endif; ?>

<?php include 'includes/footer.php'; ?>
</body>
</html>
