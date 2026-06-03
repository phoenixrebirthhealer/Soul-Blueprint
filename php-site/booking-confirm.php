<!DOCTYPE html>
<html lang="en">
<head>
  <title>Booking Confirmed | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; }
    .main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 120px 40px 80px; }
    .box { max-width: 600px; width: 100%; text-align: center; }
    .icon { font-size: 56px; color: var(--gold); margin-bottom: 32px; }
    .icon.err { color: var(--magenta); }
    .conf-title { font-family: 'Cinzel', serif; font-size: clamp(24px,3.5vw,40px); font-weight: 400; color: var(--cream); margin-bottom: 20px; line-height: 1.2; }
    .conf-title em { color: var(--gold); font-style: normal; }
    .conf-sub { font-size: 17px; font-weight: 300; font-style: italic; color: var(--cream-dim); margin-bottom: 40px; max-width: 480px; margin-left: auto; margin-right: auto; }
    .detail-box { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.2); padding: 32px; text-align: left; margin-bottom: 40px; }
    .detail-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(212,175,55,0.07); font-size: 16px; font-weight: 300; color: var(--cream-dim); }
    .detail-row:last-child { border-bottom: none; }
    .detail-row span:last-child { color: var(--cream); }
    .meet-link-box { background: rgba(212,175,55,0.06); border: 1px solid rgba(212,175,55,0.25); padding: 20px 24px; margin-bottom: 40px; }
    .meet-link-box p { font-size: 15px; font-weight: 300; color: var(--cream-dim); margin-bottom: 10px; }
    .meet-link-box a { color: var(--gold); text-decoration: none; font-size: 15px; word-break: break-all; }
    .meet-link-box a:hover { color: var(--gold-light); }
    .spinner { display: inline-block; width: 40px; height: 40px; border: 2px solid rgba(212,175,55,0.2); border-top-color: var(--gold); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 24px; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .btn-conf-ghost { display: inline-block; font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 4px; text-transform: uppercase; color: var(--cream-dim); border: 1px solid rgba(212,175,55,0.25); padding: 16px 40px; text-decoration: none; transition: all 0.3s; margin-left: 16px; }
    .btn-conf-ghost:hover { border-color: var(--gold); color: var(--gold); }
    .conf-footer { border-top: 1px solid rgba(212,175,55,0.12); padding: 32px 60px; display: flex; align-items: center; justify-content: space-between; }
    .conf-footer span { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 2px; color: rgba(245,240,255,0.18); }
    @media (max-width: 600px) {
      .conf-footer { padding: 24px; flex-direction: column; gap: 10px; text-align: center; }
      .btn-conf-ghost { margin-left: 0; margin-top: 12px; }
    }
  </style>
</head>
<body>

<nav style="position:fixed; top:0; left:0; right:0; z-index:100; display:flex; align-items:center; justify-content:space-between; padding:20px 60px; background:rgba(15,5,32,0.94); backdrop-filter:blur(10px); border-bottom:1px solid rgba(212,175,55,0.15);">
  <a href="index.php" class="nav-logo">Phoenix Rebirth</a>
</nav>

<div class="main">
  <div class="box" id="mainBox">
    <div class="spinner" id="spinner"></div>
    <p style="color:var(--cream-dim);font-style:italic;font-size:16px;">Confirming your booking...</p>
  </div>
</div>

<div class="conf-footer">
  <span>&copy; 2026 Phoenix Rebirth &nbsp;|&nbsp; Christina Stevens &nbsp;|&nbsp; All Rights Reserved</span>
  <span>Hobbs, NM &nbsp;|&nbsp; Remote Worldwide</span>
</div>

<script>
  const API = 'https://soul-blueprint-production.up.railway.app';

  async function confirmBooking() {
    const params = new URLSearchParams(window.location.search);
    const orderId = params.get('token');
    const box = document.getElementById('mainBox');

    if (!orderId) {
      showError('No order found. If you completed payment, please contact Christina directly.');
      return;
    }

    const pendingRaw = localStorage.getItem('pendingBooking');
    if (!pendingRaw) {
      showError('Booking details not found. If you completed payment, please contact Christina at christina@phoenixrebirth.life with your PayPal receipt.');
      return;
    }

    let pending;
    try { pending = JSON.parse(pendingRaw); } catch (e) {
      showError('Booking data error. Please contact Christina directly.');
      return;
    }

    try {
      const resp = await fetch(`${API}/paypal/capture-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...pending, order_id: orderId })
      });
      const data = await resp.json();
      if (data.status === 'confirmed') {
        localStorage.removeItem('pendingBooking');
        showSuccess(pending, data.meet_link);
      } else {
        throw new Error(data.error || 'Capture failed');
      }
    } catch (e) {
      showError('Your payment may have been processed but booking confirmation failed. Please contact Christina at christina@phoenixrebirth.life immediately with your PayPal receipt. Error: ' + e.message);
    }
  }

  function showSuccess(booking, meetLink) {
    const box = document.getElementById('mainBox');
    const dateFmt = booking.slot_mt_display || 'Your scheduled time';
    box.innerHTML = `
      <div class="icon">&#10003;</div>
      <h1 class="conf-title">You're <em>Confirmed</em></h1>
      <p class="conf-sub">Your session is booked. Christina will be there.</p>
      <div class="detail-box">
        <div class="detail-row"><span>Service</span><span>${booking.service_name}</span></div>
        <div class="detail-row"><span>Date &amp; Time</span><span>${dateFmt}</span></div>
        <div class="detail-row"><span>Name</span><span>${booking.client_name}</span></div>
        <div class="detail-row"><span>Email</span><span>${booking.client_email}</span></div>
        <div class="detail-row"><span>Total Paid</span><span>$${(booking.charged_price_cents / 100).toFixed(2)}</span></div>
      </div>
      ${meetLink ? `
      <div class="meet-link-box">
        <p>Your Google Meet link for the session:</p>
        <a href="${meetLink}" target="_blank">${meetLink}</a>
      </div>` : `
      <div class="meet-link-box">
        <p>A confirmation has been sent to <strong style="color:var(--cream);">${booking.client_email}</strong>. Christina will be in touch with session details before your appointment.</p>
      </div>`}
      <a href="services.php" class="btn-primary">Back to Services</a>
      <a href="contact.php" class="btn-conf-ghost">Contact Christina</a>
    `;
  }

  function showError(msg) {
    const box = document.getElementById('mainBox');
    box.innerHTML = `
      <div class="icon err">&#9888;</div>
      <h1 class="conf-title">Something Went <em>Wrong</em></h1>
      <p class="conf-sub">${msg}</p>
      <a href="booking.php" class="btn-primary">Try Again</a>
      <a href="contact.php" class="btn-conf-ghost">Contact Christina</a>
    `;
  }

  confirmBooking();
</script>

</body>
</html>
