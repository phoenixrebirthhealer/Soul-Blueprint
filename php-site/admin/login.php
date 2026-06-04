<?php
require_once __DIR__ . '/includes/admin-auth.php';

if (admin_is_logged_in()) {
    header('Location: /admin/');
    exit;
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $pw = $_POST['password'] ?? '';
    if (hash_equals(ADMIN_PASSWORD, $pw)) {
        session_regenerate_id(true);
        $_SESSION['admin_logged_in'] = true;
        header('Location: /admin/');
        exit;
    } else {
        $error = 'Incorrect password.';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin | Phoenix Rebirth</title>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Cormorant+Garamond:wght@300;400&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root { --gold: #d4af37; --cream: #f5f0ff; --plum: #0f0520; --magenta: #c2185b; }
    body { background: var(--plum); min-height: 100vh; display: flex; align-items: center; justify-content: center; font-family: 'Cormorant Garamond', serif; }
    .box { max-width: 380px; width: 100%; padding: 48px 40px; background: rgba(255,255,255,0.03); border: 1px solid rgba(212,175,55,0.15); }
    h1 { font-family: 'Cinzel', serif; font-size: 18px; letter-spacing: 4px; text-transform: uppercase; color: var(--gold); text-align: center; margin-bottom: 36px; }
    .form-group { margin-bottom: 20px; }
    label { display: block; font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 3px; text-transform: uppercase; color: rgba(212,175,55,0.6); margin-bottom: 8px; }
    input[type=password] { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 16px; padding: 12px 14px; outline: none; }
    input[type=password]:focus { border-color: rgba(212,175,55,0.5); }
    button { width: 100%; font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--plum); background: var(--gold); border: none; padding: 16px; cursor: pointer; margin-top: 8px; }
    button:hover { background: #f0d060; }
    .error { color: #f48fb1; font-size: 14px; text-align: center; margin-bottom: 20px; }
  </style>
</head>
<body>
<div class="box">
  <h1>Admin Access</h1>
  <?php if ($error): ?><div class="error"><?= htmlspecialchars($error) ?></div><?php endif; ?>
  <form method="POST">
    <div class="form-group">
      <label>Password</label>
      <input type="password" name="password" autofocus />
    </div>
    <button type="submit">Enter</button>
  </form>
</div>
</body>
</html>
