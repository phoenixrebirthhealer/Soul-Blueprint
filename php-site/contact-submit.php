<!DOCTYPE html>
<html lang="en">
<head>
  <title>Message Sent | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; }
    .main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 120px 40px 80px; text-align: center; }
    .box { max-width: 560px; }
    .icon { font-size: 48px; color: var(--gold); margin-bottom: 28px; }
    .box h1 { font-family: 'Cinzel', serif; font-size: clamp(24px,3vw,38px); font-weight: 400; color: var(--cream); margin-bottom: 20px; }
    .box h1 em { color: var(--gold); font-style: normal; }
    .box p { font-size: 17px; font-weight: 300; color: var(--cream-dim); margin-bottom: 40px; line-height: 1.8; }
  </style>
</head>
<body>

<?php include 'includes/nav.php'; ?>

<?php
$name    = htmlspecialchars(trim($_POST['name']    ?? ''));
$email   = htmlspecialchars(trim($_POST['email']   ?? ''));
$topic   = htmlspecialchars(trim($_POST['topic']   ?? ''));
$message = htmlspecialchars(trim($_POST['message'] ?? ''));

if ($name && $email && $message) {
  $to      = 'christina@phoenixrebirth.life';
  $subject = 'Phoenix Rebirth Contact: ' . ($topic ?: 'New Message');
  $body    = "Name: $name\nEmail: $email\nTopic: $topic\n\nMessage:\n$message";
  $headers = "From: noreply@phoenixrebirth.life\r\nReply-To: $email";
  @mail($to, $subject, $body, $headers);
}
?>

<div class="main">
  <div class="box">
    <div class="icon">&#10003;</div>
    <h1>Message <em>Received</em></h1>
    <p>Thank you<?php if ($name) echo ', ' . $name; ?>. Christina will respond within 24-48 hours on business days. No generic auto-replies -- a real answer from Christina.</p>
    <a href="index.php" class="btn-primary">Back to Home &rarr;</a>
  </div>
</div>

<?php include 'includes/footer.php'; ?>

</body>
</html>
