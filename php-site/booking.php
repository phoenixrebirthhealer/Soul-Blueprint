<!DOCTYPE html>
<html lang="en">
<head>
  <title>Book a Session | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    .hero { min-height: 42vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 140px 40px 60px; background: radial-gradient(ellipse at 50% 40%, rgba(194,24,91,0.1) 0%, transparent 55%), var(--plum-deep); }
    .hero h1 { font-family: 'Cinzel', serif; font-size: clamp(28px,4vw,52px); font-weight: 400; color: var(--cream); max-width: 700px; margin-bottom: 20px; line-height: 1.2; }
    .hero h1 em { color: var(--gold); font-style: normal; }
    .hero p { font-size: 17px; font-weight: 300; font-style: italic; color: var(--cream-dim); max-width: 500px; }

    .booking-wrap { max-width: 860px; margin: 0 auto; padding: 80px 40px 120px; }

    .step { display: none; }
    .step.active { display: block; }
    .step-label { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 4px; text-transform: uppercase; color: var(--gold); margin-bottom: 12px; display: block; }
    .step h2 { font-family: 'Cinzel', serif; font-size: clamp(22px,3vw,36px); font-weight: 400; color: var(--cream); margin-bottom: 12px; }
    .step h2 em { color: var(--magenta); font-style: normal; }
    .step-sub { font-size: 16px; font-weight: 300; font-style: italic; color: var(--cream-dim); margin-bottom: 48px; }

    .service-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; margin-bottom: 40px; }
    .service-card { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.15); padding: 28px 24px; cursor: pointer; transition: border-color 0.3s, transform 0.2s; }
    .service-card:hover { border-color: rgba(212,175,55,0.4); transform: translateY(-2px); }
    .service-card.selected { border-color: var(--gold); background: rgba(212,175,55,0.06); }
    .service-card h3 { font-family: 'Cinzel', serif; font-size: 13px; letter-spacing: 1px; color: var(--gold); margin-bottom: 10px; }
    .service-card .price { font-family: 'Cinzel', serif; font-size: 22px; font-weight: 400; color: var(--cream); margin-bottom: 10px; }
    .service-card p { font-size: 15px; font-weight: 300; color: var(--cream-dim); line-height: 1.6; }

    .cal-nav { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; }
    .cal-nav h3 { font-family: 'Cinzel', serif; font-size: 16px; letter-spacing: 2px; color: var(--cream); }
    .cal-btn { background: none; border: 1px solid rgba(212,175,55,0.3); color: var(--gold); font-family: 'Cinzel', serif; font-size: 12px; letter-spacing: 2px; padding: 8px 18px; cursor: pointer; transition: all 0.3s; }
    .cal-btn:hover { border-color: var(--gold); background: rgba(212,175,55,0.08); }
    .cal-grid { display: grid; grid-template-columns: repeat(7,1fr); gap: 6px; margin-bottom: 40px; }
    .cal-day-label { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--cream-faint); text-align: center; padding: 8px 0; }
    .cal-day { aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-family: 'Cormorant Garamond', serif; font-size: 15px; font-weight: 300; color: var(--cream-faint); border: 1px solid transparent; }
    .cal-day.available { color: var(--cream); border-color: rgba(212,175,55,0.2); cursor: pointer; transition: all 0.2s; }
    .cal-day.available:hover { border-color: var(--gold); color: var(--gold); background: rgba(212,175,55,0.06); }
    .cal-day.selected { border-color: var(--gold); background: rgba(212,175,55,0.12); color: var(--gold); }
    .cal-day.past { opacity: 0.2; }
    .cal-day.empty { border: none; }

    .slots-loading { text-align: center; padding: 40px; color: var(--cream-dim); font-style: italic; font-size: 16px; }
    .time-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px,1fr)); gap: 12px; margin-bottom: 40px; }
    .time-slot { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.2); padding: 14px 16px; text-align: center; cursor: pointer; transition: all 0.2s; font-family: 'Cormorant Garamond', serif; font-size: 16px; font-weight: 300; color: var(--cream); }
    .time-slot:hover { border-color: var(--gold); color: var(--gold); }
    .time-slot.selected { border-color: var(--gold); background: rgba(212,175,55,0.1); color: var(--gold); }
    .no-slots { padding: 32px; background: rgba(255,255,255,0.02); border: 1px solid rgba(212,175,55,0.08); text-align: center; font-size: 15px; font-weight: 300; font-style: italic; color: var(--cream-dim); }

    .form-group { margin-bottom: 24px; }
    .form-group label { display: block; font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); margin-bottom: 10px; }
    .form-group input { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 16px; font-weight: 300; padding: 14px 16px; outline: none; transition: border-color 0.3s; }
    .form-group input:focus { border-color: rgba(212,175,55,0.5); }
    .form-group input::placeholder { color: var(--cream-faint); }

    .ffs-notice { background: rgba(212,175,55,0.06); border: 1px solid rgba(212,175,55,0.25); padding: 20px 24px; margin-bottom: 24px; display: none; }
    .ffs-notice.visible { display: flex; align-items: flex-start; gap: 16px; }
    .ffs-notice p { font-size: 15px; font-weight: 300; color: var(--cream-dim); line-height: 1.6; }
    .ffs-notice strong { color: var(--gold); }
    .ffs-check { display: flex; align-items: center; gap: 10px; margin-top: 10px; cursor: pointer; }
    .ffs-check input[type="checkbox"] { width: 16px; height: 16px; accent-color: var(--gold); cursor: pointer; }
    .ffs-check span { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: var(--gold); }

    .review-box { background: rgba(255,255,255,0.025); border: 1px solid rgba(212,175,55,0.2); padding: 36px 32px; margin-bottom: 40px; }
    .review-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(212,175,55,0.08); font-size: 16px; font-weight: 300; color: var(--cream-dim); }
    .review-row:last-child { border-bottom: none; }
    .review-row span:last-child { color: var(--cream); font-weight: 400; }
    .review-total { display: flex; justify-content: space-between; padding: 20px 0 0; font-family: 'Cinzel', serif; font-size: 18px; letter-spacing: 1px; color: var(--cream); border-top: 1px solid rgba(212,175,55,0.2); margin-top: 8px; }
    .review-total span:last-child { color: var(--gold); font-size: 22px; }
    .review-credit { color: var(--magenta); font-size: 14px; }

    .btn-book { display: block; width: 100%; font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 4px; text-transform: uppercase; color: var(--plum-deep); background: linear-gradient(135deg, var(--gold), #b8941e); padding: 18px 48px; border: none; cursor: pointer; transition: all 0.3s; text-align: center; }
    .btn-book:hover { background: linear-gradient(135deg, var(--gold-light), var(--gold)); transform: translateY(-2px); }
    .btn-book:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
    .btn-back { background: none; border: 1px solid rgba(212,175,55,0.25); color: var(--cream-dim); font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; padding: 12px 28px; cursor: pointer; transition: all 0.3s; margin-bottom: 24px; }
    .btn-back:hover { border-color: var(--gold); color: var(--gold); }

    .error-msg { background: rgba(194,24,91,0.1); border: 1px solid rgba(194,24,91,0.35); padding: 16px 20px; font-size: 15px; font-weight: 300; color: var(--cream-dim); margin-bottom: 24px; display: none; }
    .error-msg.visible { display: block; }

    .progress-bar { display: flex; gap: 8px; margin-bottom: 56px; }
    .progress-step { flex: 1; height: 2px; background: rgba(212,175,55,0.15); transition: background 0.3s; }
    .progress-step.done { background: var(--gold); }
    .progress-step.active { background: rgba(212,175,55,0.5); }

    .booking-footer { border-top: 1px solid rgba(212,175,55,0.12); padding: 48px 60px; display: flex; align-items: center; justify-content: space-between; }
    .booking-footer span { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 2px; color: rgba(245,240,255,0.18); }

    @media (max-width: 680px) {
      .booking-wrap { padding: 60px 24px 80px; }
      .service-grid { grid-template-columns: 1fr; }
      .booking-footer { padding: 32px 24px; flex-direction: column; gap: 12px; text-align: center; }
    }
  </style>
</head>
<body>

<?php include 'includes/nav.php'; ?>

<div class="hero">
  <span class="eyebrow">Work With Christina</span>
  <h1>Book a <em>Session</em></h1>
  <p>All sessions are conducted remotely. Pick your service, choose your time, and pay securely through PayPal.</p>
</div>

<div class="booking-wrap">

  <div class="progress-bar" id="progressBar">
    <div class="progress-step active" id="ps1"></div>
    <div class="progress-step" id="ps2"></div>
    <div class="progress-step" id="ps3"></div>
    <div class="progress-step" id="ps4"></div>
  </div>

  <div class="error-msg" id="errorMsg"></div>

  <div class="step active" id="step1">
    <span class="step-label">Step 1 of 4</span>
    <h2>Choose Your <em>Session</em></h2>
    <p class="step-sub">Select the session that fits where you are right now.</p>
    <div class="service-grid" id="serviceGrid"></div>
    <button class="btn-book" id="btnStep1" disabled onclick="goToStep(2)">Select a Date &amp; Time &rarr;</button>
  </div>

  <div class="step" id="step2">
    <button class="btn-back" onclick="goToStep(1)">&larr; Back</button>
    <span class="step-label">Step 2 of 4</span>
    <h2>Choose Your <em>Date &amp; Time</em></h2>
    <p class="step-sub">All times are Mountain Time (MT). Christina is based in Hobbs, NM.</p>

    <div class="cal-nav">
      <button class="cal-btn" onclick="prevMonth()">&larr;</button>
      <h3 id="calMonthLabel"></h3>
      <button class="cal-btn" onclick="nextMonth()">&rarr;</button>
    </div>

    <div class="cal-grid" id="calGrid"></div>

    <div id="timeSection" style="display:none;">
      <span class="step-label" style="margin-bottom:16px;">Available Times &mdash; <span id="selectedDateLabel"></span></span>
      <div class="time-grid" id="timeGrid"></div>
    </div>

    <button class="btn-book" id="btnStep2" disabled onclick="goToStep(3)">Enter Your Info &rarr;</button>
  </div>

  <div class="step" id="step3">
    <button class="btn-back" onclick="goToStep(2)">&larr; Back</button>
    <span class="step-label">Step 3 of 4</span>
    <h2>Your <em>Information</em></h2>
    <p class="step-sub">This is how Christina will reach you and where your confirmation goes.</p>

    <div class="form-group">
      <label>Your Full Name</label>
      <input type="text" id="clientName" placeholder="First and last name" oninput="checkStep3()" />
    </div>
    <div class="form-group">
      <label>Email Address</label>
      <input type="email" id="clientEmail" placeholder="your@email.com" oninput="checkStep3()" onblur="checkFfsCredit()" />
    </div>

    <div class="ffs-notice" id="ffsNotice">
      <div>
        <p>You have an unused <strong>Field Frequency Scan credit ($75)</strong> on file. Would you like to apply it to this session?</p>
        <label class="ffs-check">
          <input type="checkbox" id="ffsCheckbox" onchange="updateReview()" />
          <span>Apply $75 Credit</span>
        </label>
      </div>
    </div>

    <button class="btn-book" id="btnStep3" disabled onclick="goToStep(4)">Review &amp; Pay &rarr;</button>
  </div>

  <div class="step" id="step4">
    <button class="btn-back" onclick="goToStep(3)">&larr; Back</button>
    <span class="step-label">Step 4 of 4</span>
    <h2>Review &amp; <em>Pay</em></h2>
    <p class="step-sub">Confirm everything looks right, then complete payment through PayPal.</p>

    <div class="review-box" id="reviewBox"></div>

    <p style="font-size:14px; font-weight:300; color:var(--cream-faint); margin-bottom:24px; font-style:italic;">
      You will be redirected to PayPal to complete your payment. After payment, your booking will be confirmed and a confirmation will be sent to your email.
    </p>

    <button class="btn-book" id="btnPay" onclick="initiatePayment()">Pay with PayPal &rarr;</button>
  </div>

</div>

<div class="booking-footer">
  <span>&copy; 2026 Phoenix Rebirth &nbsp;|&nbsp; Christina Stevens &nbsp;|&nbsp; All Rights Reserved</span>
  <span>Hobbs, NM &nbsp;|&nbsp; Remote Worldwide</span>
</div>

<script>
  const API = 'https://soul-blueprint-production.up.railway.app';

  const SERVICES = [
    { name: 'Field Frequency Scan', price: 7500, duration: 60, note: '$75 credited toward any session booked within 30 days.', desc: 'A deep energetic assessment of your current field. Identifies active patterns, blocks, and activation points.' },
    { name: 'Rapid Relief Session', price: 22500, duration: 60, desc: 'Targeted intervention for acute energetic disturbance or pattern disruption. Focused, fast, and direct.' },
    { name: 'Mild Session', price: 27500, duration: 90, desc: 'Comprehensive session for moderate-intensity work. Deeper than Rapid Relief, more targeted than Chronic.' },
    { name: 'Chronic Session', price: 47500, duration: 120, desc: 'Deep long-form session for entrenched patterns and chronic activation. The full excavation.' },
    { name: 'Guidance Session', price: 45000, duration: 90, desc: 'Strategic clarity session. Path, direction, and next-step activation. Where are you going and how do you get there.' },
    { name: 'Oracle & Tarot Reading', price: 57500, duration: 90, desc: 'A full oracle and tarot reading with integration guidance and pattern activation.' },
  ];

  let selectedService = null;
  let allSlots = [];
  let selectedDate = null;
  let selectedSlot = null;
  let calYear = new Date().getFullYear();
  let calMonth = new Date().getMonth() + 1;
  let hasFfsCredit = false;

  function formatPrice(cents) {
    return '$' + (cents / 100).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  }

  function showError(msg) {
    const el = document.getElementById('errorMsg');
    el.textContent = msg;
    el.classList.add('visible');
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function clearError() {
    document.getElementById('errorMsg').classList.remove('visible');
  }

  function buildServices() {
    const grid = document.getElementById('serviceGrid');
    grid.innerHTML = '';
    SERVICES.forEach((svc, i) => {
      const card = document.createElement('div');
      card.className = 'service-card';
      card.innerHTML = `<h3>${svc.name}</h3><div class="price">${formatPrice(svc.price)}</div><p>${svc.desc}${svc.note ? '<br><em style="font-size:13px;color:var(--gold);">' + svc.note + '</em>' : ''}</p>`;
      card.onclick = () => selectService(i, card);
      grid.appendChild(card);
    });
  }

  function selectService(i, card) {
    document.querySelectorAll('.service-card').forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    selectedService = SERVICES[i];
    document.getElementById('btnStep1').disabled = false;
  }

  const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const DAYS   = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

  function prevMonth() {
    calMonth--;
    if (calMonth < 1) { calMonth = 12; calYear--; }
    selectedDate = null; selectedSlot = null;
    document.getElementById('timeSection').style.display = 'none';
    document.getElementById('btnStep2').disabled = true;
    loadSlots();
  }

  function nextMonth() {
    calMonth++;
    if (calMonth > 12) { calMonth = 1; calYear++; }
    selectedDate = null; selectedSlot = null;
    document.getElementById('timeSection').style.display = 'none';
    document.getElementById('btnStep2').disabled = true;
    loadSlots();
  }

  async function loadSlots() {
    document.getElementById('calMonthLabel').textContent = `${MONTHS[calMonth - 1]} ${calYear}`;
    document.getElementById('calGrid').innerHTML = '<div class="slots-loading" style="grid-column:1/-1">Loading available dates...</div>';
    allSlots = [];
    try {
      const resp = await fetch(`${API}/slots`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ year: calYear, month: calMonth }) });
      const data = await resp.json();
      allSlots = data.slots || [];
    } catch (e) {
      showError('Could not load available times. Please refresh and try again.');
    }
    renderCalendar();
  }

  function renderCalendar() {
    const grid = document.getElementById('calGrid');
    grid.innerHTML = '';
    DAYS.forEach(d => {
      const lbl = document.createElement('div');
      lbl.className = 'cal-day-label';
      lbl.textContent = d;
      grid.appendChild(lbl);
    });
    const firstDay = new Date(calYear, calMonth - 1, 1).getDay();
    const daysInMonth = new Date(calYear, calMonth, 0).getDate();
    const today = new Date();
    const availDates = new Set(allSlots.map(s => s.date));
    for (let i = 0; i < firstDay; i++) {
      const empty = document.createElement('div');
      empty.className = 'cal-day empty';
      grid.appendChild(empty);
    }
    for (let d = 1; d <= daysInMonth; d++) {
      const cell = document.createElement('div');
      const dateStr = `${calYear}-${String(calMonth).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
      const cellDate = new Date(calYear, calMonth - 1, d);
      const isPast = cellDate < new Date(today.getFullYear(), today.getMonth(), today.getDate());
      cell.className = 'cal-day';
      cell.textContent = d;
      if (isPast) {
        cell.classList.add('past');
      } else if (availDates.has(dateStr)) {
        cell.classList.add('available');
        if (selectedDate === dateStr) cell.classList.add('selected');
        cell.onclick = () => selectDate(dateStr, cell);
      }
      grid.appendChild(cell);
    }
  }

  function selectDate(dateStr, cell) {
    document.querySelectorAll('.cal-day.selected').forEach(c => c.classList.remove('selected'));
    cell.classList.add('selected');
    selectedDate = dateStr;
    selectedSlot = null;
    document.getElementById('btnStep2').disabled = true;
    renderTimeSlots(dateStr);
  }

  function renderTimeSlots(dateStr) {
    const slotsForDate = allSlots.filter(s => s.date === dateStr);
    const section = document.getElementById('timeSection');
    const grid = document.getElementById('timeGrid');
    const dt = new Date(dateStr + 'T12:00:00');
    document.getElementById('selectedDateLabel').textContent = dt.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
    section.style.display = 'block';
    grid.innerHTML = '';
    if (slotsForDate.length === 0) {
      grid.innerHTML = '<div class="no-slots" style="grid-column:1/-1">No times available on this date.</div>';
      return;
    }
    slotsForDate.forEach(slot => {
      const btn = document.createElement('div');
      btn.className = 'time-slot';
      btn.textContent = slot.label;
      if (selectedSlot && selectedSlot.utc === slot.utc) btn.classList.add('selected');
      btn.onclick = () => {
        document.querySelectorAll('.time-slot').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        selectedSlot = slot;
        document.getElementById('btnStep2').disabled = false;
        clearError();
      };
      grid.appendChild(btn);
    });
  }

  async function checkFfsCredit() {
    const email = document.getElementById('clientEmail').value.trim().toLowerCase();
    if (!email || !email.includes('@')) return;
    try {
      const resp = await fetch(`${API}/ffs-credit`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }) });
      const data = await resp.json();
      hasFfsCredit = data.hasCredit || false;
      const notice = document.getElementById('ffsNotice');
      if (hasFfsCredit && selectedService && selectedService.name !== 'Field Frequency Scan') {
        notice.classList.add('visible');
      } else {
        notice.classList.remove('visible');
        document.getElementById('ffsCheckbox').checked = false;
      }
    } catch (e) { /* silent */ }
  }

  function checkStep3() {
    const name  = document.getElementById('clientName').value.trim();
    const email = document.getElementById('clientEmail').value.trim();
    document.getElementById('btnStep3').disabled = !(name && email && email.includes('@'));
  }

  function updateReview() {
    const applyCredit = hasFfsCredit && document.getElementById('ffsCheckbox').checked;
    const credit = applyCredit ? 7500 : 0;
    const charged = Math.max(0, selectedService.price - credit);
    const dt = new Date(selectedSlot.date + 'T12:00:00');
    const dateStr = dt.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
    document.getElementById('reviewBox').innerHTML = `
      <div class="review-row"><span>Service</span><span>${selectedService.name}</span></div>
      <div class="review-row"><span>Date</span><span>${dateStr}</span></div>
      <div class="review-row"><span>Time</span><span>${selectedSlot.label}</span></div>
      <div class="review-row"><span>Name</span><span>${document.getElementById('clientName').value.trim()}</span></div>
      <div class="review-row"><span>Email</span><span>${document.getElementById('clientEmail').value.trim()}</span></div>
      ${applyCredit ? `<div class="review-row"><span>FFS Credit</span><span class="review-credit">-$75.00</span></div>` : ''}
      <div class="review-total"><span>Total Due</span><span>${formatPrice(charged)}</span></div>
    `;
  }

  function goToStep(n) {
    clearError();
    document.querySelectorAll('.step').forEach((s, i) => s.classList.toggle('active', i + 1 === n));
    for (let i = 1; i <= 4; i++) {
      const ps = document.getElementById('ps' + i);
      ps.className = 'progress-step' + (i < n ? ' done' : i === n ? ' active' : '');
    }
    if (n === 2 && allSlots.length === 0) loadSlots();
    if (n === 4) updateReview();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function initiatePayment() {
    const applyCredit = hasFfsCredit && document.getElementById('ffsCheckbox').checked;
    const btn = document.getElementById('btnPay');
    btn.disabled = true;
    btn.textContent = 'Redirecting to PayPal...';
    clearError();
    const clientName  = document.getElementById('clientName').value.trim();
    const clientEmail = document.getElementById('clientEmail').value.trim().toLowerCase();
    const credit      = applyCredit ? 7500 : 0;
    const charged     = Math.max(0, selectedService.price - credit);
    const dt = new Date(selectedSlot.date + 'T12:00:00');
    const dateFmt = dt.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
    const slotMtDisplay = `${dateFmt} at ${selectedSlot.label}`;
    const pendingBooking = {
      client_name:              clientName,
      client_email:             clientEmail,
      service_name:             selectedService.name,
      service_price_cents:      selectedService.price,
      charged_price_cents:      charged,
      ffs_credit_applied:       applyCredit,
      slot_utc:                 selectedSlot.utc,
      slot_mt:                  selectedSlot.mt,
      client_timezone:          Intl.DateTimeFormat().resolvedOptions().timeZone,
      slot_mt_display:          slotMtDisplay,
      service_duration_minutes: selectedService.duration,
    };
    localStorage.setItem('pendingBooking', JSON.stringify(pendingBooking));
    try {
      const resp = await fetch(`${API}/paypal/create-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_name:          selectedService.name,
          service_price_cents:   selectedService.price,
          ffs_credit_applied:    applyCredit,
          return_url:            `${window.location.origin}/booking-confirm.php`,
          cancel_url:            `${window.location.origin}/booking.php`,
        })
      });
      const data = await resp.json();
      if (data.approval_url) {
        window.location.href = data.approval_url;
      } else {
        throw new Error(data.error || 'Could not create PayPal order.');
      }
    } catch (e) {
      showError('Payment could not be started: ' + e.message);
      btn.disabled = false;
      btn.textContent = 'Pay with PayPal →';
    }
  }

  buildServices();
</script>

</body>
</html>
