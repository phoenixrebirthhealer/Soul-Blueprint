<?php
require_once 'includes/auth.php';

if (is_logged_in()) {
    header('Location: /dashboard');
    exit;
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    $email   = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    $confirm  = $_POST['confirm'] ?? '';

    if (!$email || !$password || !$confirm) {
        $error = 'All fields are required.';
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error = 'Please enter a valid email address.';
    } elseif (strlen($password) < 8) {
        $error = 'Password must be at least 8 characters.';
    } elseif ($password !== $confirm) {
        $error = 'Passwords do not match.';
    } else {
        $db = get_db();
        $check = $db->prepare('SELECT id FROM clients WHERE email = ?');
        $check->execute([$email]);
        if ($check->fetch()) {
            $error = 'An account with that email already exists.';
        } else {
            $_SESSION['reg'] = [
                'email'         => $email,
                'password_hash' => password_hash($password, PASSWORD_DEFAULT),
            ];
            unset($_SESSION['intake'], $_SESSION['assessment_answers']);
            header('Location: /intake');
            exit;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Create Your Account | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; }
    .main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 120px 40px 80px; }
    .box { max-width: 500px; width: 100%; }
    .box h1 { font-family: 'Cinzel', serif; font-size: clamp(22px,3vw,34px); font-weight: 400; color: var(--cream); margin-bottom: 10px; }
    .box h1 em { color: var(--gold); font-style: normal; }
    .box .sub { font-size: 16px; font-weight: 300; color: var(--cream-dim); margin-bottom: 40px; line-height: 1.7; }
    .form-panel { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.15); padding: 40px 36px; }
    .form-group { margin-bottom: 22px; }
    .form-group label { display: block; font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); margin-bottom: 8px; }
    .form-group input { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 16px; font-weight: 300; padding: 12px 14px; outline: none; transition: border-color 0.3s; }
    .form-group input:focus { border-color: rgba(212,175,55,0.5); }
    .error-msg { background: rgba(194,24,91,0.12); border: 1px solid rgba(194,24,91,0.3); color: #f48fb1; font-size: 14px; font-weight: 300; padding: 14px 18px; margin-bottom: 24px; }
    .btn-full { width: 100%; text-align: center; border: none; cursor: pointer; }
    .login-link { text-align: center; margin-top: 24px; font-size: 14px; font-weight: 300; color: var(--cream-dim); }
    .login-link a { color: var(--gold); text-decoration: none; }
    .login-link a:hover { color: var(--gold-light); }
    .steps { display: flex; justify-content: center; gap: 8px; margin-bottom: 36px; }
    .step { width: 32px; height: 3px; background: rgba(212,175,55,0.15); }
    .step.active { background: var(--gold); }
  </style>
</head>
<body>
<?php include 'includes/nav.php'; ?>
<div class="main">
  <div class="box">
    <div class="steps">
      <div class="step active"></div>
      <div class="step"></div>
      <div class="step"></div>
    </div>
    <h1>Create Your <em>Account</em></h1>
    <p class="sub">Step 1 of 3. You will complete your profile and self-love assessment before your account is activated.</p>
    <div class="form-panel">
      <?php if ($error): ?>
        <div class="error-msg"><?= htmlspecialchars($error) ?></div>
      <?php endif; ?>
      <form method="POST" action="/register">
        <input type="hidden" name="csrf_token" value="<?= csrf_token() ?>">
        <div class="form-group">
          <label>Email Address</label>
          <input type="email" name="email" value="<?= htmlspecialchars($_POST['email'] ?? '') ?>" required autocomplete="email" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" name="password" required autocomplete="new-password" placeholder="8 characters minimum" />
        </div>
        <div class="form-group">
          <label>Confirm Password</label>
          <input type="password" name="confirm" required autocomplete="new-password" />
        </div>
        <button class="btn-primary btn-full" type="submit">Continue to Profile &rarr;</button>
      </form>
    </div>
    <p class="login-link">Already have an account? <a href="/login">Sign in here</a></p>
  </div>
</div>
<?php include 'includes/footer.php'; ?>
</body>
</html>
