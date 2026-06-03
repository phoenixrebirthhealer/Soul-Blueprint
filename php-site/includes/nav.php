<?php
require_once __DIR__ . '/auth.php';
$_current = basename($_SERVER['PHP_SELF']);
function _nav_active(string $page): string {
    global $_current;
    return $_current === $page ? 'class="active"' : '';
}
?>
<nav>
  <a href="/" class="nav-logo">Phoenix Rebirth</a>
  <ul class="nav-links">
    <li><a href="/about" <?= _nav_active('about.php') ?>>About</a></li>
    <li><a href="/services" <?= _nav_active('services.php') ?>>Services</a></li>
    <li><a href="/booking" <?= _nav_active('booking.php') ?>>Book a Session</a></li>
    <li><a href="/contact" <?= _nav_active('contact.php') ?>>Contact</a></li>
    <?php if (is_logged_in()): ?>
      <li><a href="/dashboard" <?= _nav_active('dashboard.php') ?> style="color:var(--gold);">My Portal</a></li>
      <li><a href="/logout" style="color:var(--cream-dim);font-size:13px;">Sign Out</a></li>
    <?php else: ?>
      <li><a href="/login" <?= _nav_active('login.php') ?>>Sign In</a></li>
      <li><a href="/register" class="btn-primary" style="padding:10px 24px;font-size:11px;">Get Started</a></li>
    <?php endif; ?>
  </ul>
</nav>
