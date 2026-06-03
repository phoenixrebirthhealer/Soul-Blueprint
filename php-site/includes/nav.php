<nav>
  <a href="index.php" class="nav-logo">Phoenix Rebirth</a>
  <ul class="nav-links">
    <li><a href="about.php" <?php if(basename($_SERVER['PHP_SELF'])=='about.php') echo 'class="active"'; ?>>About</a></li>
    <li><a href="services.php" <?php if(basename($_SERVER['PHP_SELF'])=='services.php') echo 'class="active"'; ?>>Services</a></li>
    <li><a href="soulready.php" <?php if(basename($_SERVER['PHP_SELF'])=='soulready.php') echo 'class="active"'; ?>>soulReady</a></li>
    <li><a href="booking.php" <?php if(basename($_SERVER['PHP_SELF'])=='booking.php') echo 'class="active"'; ?>>Book a Session</a></li>
    <li><a href="contact.php" <?php if(basename($_SERVER['PHP_SELF'])=='contact.php') echo 'class="active"'; ?>>Contact</a></li>
  </ul>
</nav>
