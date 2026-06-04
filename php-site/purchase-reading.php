<?php
require_once 'includes/auth.php';
require_assessment();

$type = $_GET['type'] ?? '';

$reading_types = [
    'name_frequency' => [
        'name'        => 'Name Frequency Reading',
        'price_cents' => 1099,
        'description' => 'Every letter in your birth name decoded from first to last. Your soul\'s frequency map.',
    ],
];

if (!isset($reading_types[$type])) {
    header('Location: /dashboard');
    exit;
}

$reading = $reading_types[$type];
$client  = get_client();

$db = get_db();
$existing = $db->prepare('SELECT * FROM readings WHERE client_id = ? AND reading_type = ? AND paid = 1');
$existing->execute([$_SESSION['client_id'], $type]);
if ($existing->fetch()) {
    header('Location: /dashboard');
    exit;
}

$first_name    = $client['first_name'] ?? '';
$middle_name   = $client['middle_name'] ?? '';
$maiden_name   = ($client['maiden_name'] && $client['maiden_name'] !== $client['last_name'])
    ? $client['maiden_name'] : $client['last_name'] ?? '';
$client_name   = trim(implode(' ', array_filter([$first_name, $middle_name, $maiden_name])));
$price_dollars = number_format($reading['price_cents'] / 100, 2);
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Purchase Reading | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; }
    .main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 120px 40px 80px; }
    .box { max-width: 560px; width: 100%; }
    .box h1 { font-family: 'Cinzel', serif; font-size: clamp(22px,3vw,36px); font-weight: 400; color: var(--cream); margin-bottom: 10px; }
    .box h1 em { color: var(--gold); font-style: normal; }
    .box .sub { font-size: 16px; font-weight: 300; color: var(--cream-dim); margin-bottom: 40px; line-height: 1.8; }
    .detail-box { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.15); padding: 32px; margin-bottom: 32px; }
    .detail-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(212,175,55,0.07); font-size: 16px; font-weight: 300; color: var(--cream-dim); }
    .detail-row:last-child { border-bottom: none; }
    .detail-row span:last-child { color: var(--cream); }
    .error-msg { background: rgba(194,24,91,0.12); border: 1px solid rgba(194,24,91,0.3); color: #f48fb1; font-size: 14px; padding: 14px 18px; margin-bottom: 24px; }
    #paypal-button-container { margin-top: 8px; }
    .secure-note { font-size: 12px; font-weight: 300; color: var(--cream-faint); text-align: center; margin-top: 16px; }
  </style>
</head>
<body>
<?php include 'includes/nav.php'; ?>

<div class="main">
  <div class="box">
    <h1><?= htmlspecialchars($reading['name']) ?></h1>
    <p class="sub"><?= htmlspecialchars($reading['description']) ?></p>

    <div class="detail-box">
      <div class="detail-row"><span>Reading</span><span><?= htmlspecialchars($reading['name']) ?></span></div>
      <div class="detail-row"><span>For</span><span><?= htmlspecialchars($client_name) ?></span></div>
      <div class="detail-row"><span>Total</span><span>$<?= $price_dollars ?></span></div>
    </div>

    <div id="paypal-button-container"></div>
    <p class="secure-note">Secure payment via PayPal. No account required.</p>
  </div>
</div>

<script src="https://www.paypal.com/sdk/js?client-id=<?= htmlspecialchars($_ENV['PAYPAL_CLIENT_ID'] ?? getenv('PAYPAL_CLIENT_ID') ?? '') ?>&currency=USD"></script>
<script>
paypal.Buttons({
  createOrder: async function() {
    const resp = await fetch('<?= RAILWAY_API ?>/paypal/create-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        service_name: '<?= addslashes($reading['name']) ?>',
        service_price_cents: <?= $reading['price_cents'] ?>,
        return_url: '<?= SITE_URL ?>/reading-purchase-confirm?type=<?= urlencode($type) ?>',
        cancel_url: '<?= SITE_URL ?>/dashboard'
      })
    });
    const data = await resp.json();
    if (!data.order_id) throw new Error(data.error || 'Could not create order');
    sessionStorage.setItem('reading_order', JSON.stringify({
      type: '<?= addslashes($type) ?>',
      order_id: data.order_id,
      charged_cents: data.charged_cents
    }));
    return data.order_id;
  },
  onApprove: async function(data) {
    window.location.href = '/reading-purchase-confirm?type=<?= urlencode($type) ?>&token=' + data.orderID;
  },
  onError: function(err) {
    alert('Payment error: ' + err);
  }
}).render('#paypal-button-container');
</script>

<?php include 'includes/footer.php'; ?>
</body>
</html>
