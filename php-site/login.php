<?php
require_once 'includes/auth.php';

if (is_logged_in()) {
    header('Location: /dashboard');
    exit;
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email    = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';

    if (!$email || !$password) {
        $error = 'Email and password are required.';
    } else {
        $db   = get_db();
        $stmt = $db->prepare('SELECT id, password_hash FROM clients WHERE email = ?');
        $stmt->execute([$email]);
        $row = $stmt->fetch();
        if ($row && password_verify($password, $row['password_hash'])) {
            session_regenerate_id(true);
            $_SESSION['client_id'] = $row['id'];
            $redirect = $_GET['redirect'] ?? '/dashboard';
            header('Location: ' . $redirect);
            exit;
        } else {
            $error = 'Email or password is incorrect.';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Sign In | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; }
    .main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 120px 40px 80px; }
    .box { max-width: 460px; width: 100%; }
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
    .register-link { text-align: center; margin-top: 24px; font-size: 14px; font-weight: 300; color: var(--cream-dim); }
    .register-link a { color: var(--gold); text-decoration: none; }
    .register-link a:hover { color: var(--gold-light); }
  </style>
</head>
<body>
<?php include 'includes/nav.php'; ?>

<div class="main">
  <div class="box">
    <h1>Welcome <em>Back</em></h1>
    <p class="sub">Sign in to access your readings and profile.</p>

    <div class="form-panel">
      <?php if ($error): ?>
        <div class="error-msg"><?= htmlspecialchars($error) ?></div>
      <?php endif; ?>

      <form method="POST" action="/login">
        <input type="hidden" name="csrf_token" value="<?= csrf_token() ?>">

        <div class="form-group">
          <label>Email Address</label>
          <input type="email" name="email" value="<?= htmlspecialchars($_POST['email'] ?? '') ?>" required autocomplete="email" />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input type="password" name="password" required autocomplete="current-password" />
        </div>

        <button class="btn-primary btn-full" type="submit">Sign In &rarr;</button>
      </form>
    </div>

    <p class="register-link">New here? <a href="/register">Create your account</a></p>
  </div>
</div>

<?php include 'includes/footer.php'; ?>
</body>
</html>
