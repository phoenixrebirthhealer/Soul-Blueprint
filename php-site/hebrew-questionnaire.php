<?php
require_once 'includes/auth.php';
require_once 'includes/config.php';

// Handle AJAX save — must be before any HTML output
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json');
    if (!is_logged_in()) {
        echo json_encode(['ok' => false, 'error' => 'Not logged in']);
        exit;
    }
    $raw  = file_get_contents('php://input');
    $body = json_decode($raw, true);
    if (!$body || !isset($body['csrf']) || !hash_equals($_SESSION['csrf_token'] ?? '', $body['csrf'])) {
        echo json_encode(['ok' => false, 'error' => 'Invalid request']);
        exit;
    }
    $responses = $body['responses'] ?? [];
    if (!is_array($responses) || count($responses) !== 22) {
        echo json_encode(['ok' => false, 'error' => 'Invalid response data']);
        exit;
    }
    $clean = [];
    foreach ($responses as $r) {
        $clean[] = [
            'letter_id'        => intval($r['letterId'] ?? 0),
            'letter_name'      => substr(preg_replace('/[^A-Za-z\s]/', '', $r['letterName'] ?? ''), 0, 32),
            'pronounced'       => substr(htmlspecialchars($r['pronounced'] ?? '', ENT_QUOTES, 'UTF-8'), 0, 64),
            'felt_response'    => substr(trim($r['feltResponse'] ?? ''), 0, 2000),
            'notes'            => substr(trim($r['notes'] ?? ''), 0, 1000),
            'response_time_ms' => intval($r['responseTimeMs'] ?? 0),
        ];
    }
    $db = get_db();
    try {
        $db->exec('CREATE TABLE IF NOT EXISTS hebrew_responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            client_id INT NOT NULL,
            responses_json MEDIUMTEXT NOT NULL,
            completed_at DATETIME NOT NULL,
            UNIQUE KEY uq_client (client_id)
        )');
    } catch (Exception $e) {}
    try {
        $stmt = $db->prepare('INSERT INTO hebrew_responses (client_id, responses_json, completed_at)
            VALUES (?, ?, NOW())
            ON DUPLICATE KEY UPDATE responses_json=VALUES(responses_json), completed_at=NOW()');
        $stmt->execute([$_SESSION['client_id'], json_encode($clean)]);
        echo json_encode(['ok' => true]);
    } catch (Exception $e) {
        echo json_encode(['ok' => false, 'error' => 'Could not save responses']);
    }
    exit;
}

require_login();
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Hebrew Frequency Questionnaire | soulReady</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; background: linear-gradient(135deg, #1a0a2e 0%, #2d1b4e 50%, #1a0a2e 100%); }
    .wrap { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 20px; }

    .progress-row { width: 100%; max-width: 620px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }
    .progress-label { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: rgba(245,240,255,0.3); }
    .progress-bar { width: 100%; max-width: 620px; height: 2px; background: rgba(212,175,55,0.12); margin-bottom: 24px; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, #d4af37, #b8941e); transition: width 0.4s ease; }

    .card { width: 100%; max-width: 620px; background: rgba(255,255,255,0.03); border: 1px solid rgba(212,175,55,0.25); padding: 48px 40px; }

    .gold-label { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 4px; text-transform: uppercase; color: var(--gold); margin-bottom: 20px; }
    .card-title { color: var(--cream); font-size: 26px; font-weight: 300; line-height: 1.4; margin-bottom: 24px; }
    .card-body { color: rgba(245,240,255,0.7); font-size: 15px; line-height: 1.9; margin-bottom: 32px; }
    .card-body p { margin-bottom: 16px; }
    .card-body strong { color: var(--gold); }

    .letter-display { text-align: center; margin-bottom: 40px; }
    .sit-label { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 4px; text-transform: uppercase; color: rgba(245,240,255,0.25); margin-bottom: 20px; }
    .letter-name { font-family: 'Cormorant Garamond', serif; font-size: 64px; font-weight: 300; letter-spacing: 6px; color: var(--gold); margin-bottom: 14px; }
    .letter-pronounced { font-family: 'Cinzel', serif; font-size: 22px; font-weight: 400; letter-spacing: 4px; color: var(--cream); margin-bottom: 12px; }
    .letter-phonetic { font-size: 14px; font-style: italic; color: rgba(245,240,255,0.4); }

    .field-label { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: rgba(245,240,255,0.45); display: block; margin-bottom: 10px; }
    .field-label-dim { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: rgba(245,240,255,0.25); display: block; margin-bottom: 8px; }
    textarea { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(212,175,55,0.2); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 15px; font-weight: 300; padding: 14px; outline: none; resize: vertical; transition: border-color 0.3s; box-sizing: border-box; }
    textarea:focus { border-color: rgba(212,175,55,0.5); }
    textarea.notes { background: rgba(255,255,255,0.02); border-color: rgba(212,175,55,0.12); font-size: 14px; color: rgba(245,240,255,0.6); }
    .field-wrap { margin-bottom: 20px; }
    .notes-wrap { margin-bottom: 32px; }

    .nav-row { display: flex; gap: 12px; }
    .btn-primary { flex: 1; padding: 16px; background: linear-gradient(135deg, var(--gold), #b8941e); color: var(--plum); font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; border: none; cursor: pointer; transition: opacity 0.2s; }
    .btn-primary:disabled { opacity: 0.4; cursor: default; }
    .btn-back { padding: 16px 24px; background: transparent; color: rgba(245,240,255,0.4); border: 1px solid rgba(212,175,55,0.18); font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; cursor: pointer; }
    .hint { text-align: center; font-size: 13px; color: rgba(245,240,255,0.2); font-style: italic; margin-top: 16px; }
    .error-msg { color: #f48fb1; font-size: 13px; text-align: center; margin-bottom: 14px; }

    .screen { display: none; }
    .screen.active { display: block; }

    @media (max-width: 640px) {
      .card { padding: 32px 22px; }
      .letter-name { font-size: 48px; }
    }
  </style>
</head>
<body>
<?php include 'includes/nav.php'; ?>

<div class="wrap">

  <!-- PROGRESS (hidden on intro/complete) -->
  <div class="progress-row" id="progressRow" style="display:none;">
    <span class="progress-label" id="progressLabel">Letter 1 of 22</span>
    <span class="progress-label" id="progressPct">0%</span>
  </div>
  <div class="progress-bar" id="progressBar" style="display:none;">
    <div class="progress-fill" id="progressFill" style="width:0%"></div>
  </div>

  <!-- INTRO SCREEN -->
  <div class="screen active" id="screenIntro">
    <div class="card">
      <div class="gold-label">Hebrew Frequency Questionnaire</div>
      <h1 class="card-title">You are about to sit with 22 ancient words.</h1>
      <div class="card-body">
        <p>One at a time you will see a name and how to pronounce it. That is all you get. No definitions. No meanings. No explanations.</p>
        <p>Say the word out loud if you are able to. Say it slowly. Say it more than once if you feel called to. Then notice what arises in your body.</p>
        <p>Not what you <em>think</em> about it. What you <strong>FEEL</strong>.</p>
        <p style="margin-bottom:0;">Write whatever comes immediately. Do not edit yourself. First response only.</p>
      </div>
      <button class="btn-primary" onclick="startQuestionnaire()" style="width:100%;">I Am Ready</button>
    </div>
  </div>

  <!-- QUESTIONNAIRE SCREEN -->
  <div class="screen" id="screenQ">
    <div class="card">
      <div class="letter-display">
        <div class="sit-label">Sit with this word</div>
        <div class="letter-name" id="letterName"></div>
        <div class="letter-pronounced" id="letterPronounced"></div>
        <div class="letter-phonetic" id="letterPhonetic"></div>
      </div>

      <div class="field-wrap">
        <label class="field-label">What do you feel in your body?</label>
        <textarea id="feltResponse" rows="4" placeholder="Write whatever arises. First response only. Do not edit yourself."></textarea>
      </div>

      <div class="notes-wrap">
        <label class="field-label-dim">Additional notes (optional)</label>
        <textarea id="notesField" class="notes" rows="2" placeholder="Anything else that came up..."></textarea>
      </div>

      <div id="errorMsg" class="error-msg" style="display:none;"></div>

      <div class="nav-row">
        <button class="btn-back" id="btnBack" onclick="goBack()" style="display:none;">Back</button>
        <button class="btn-primary" id="btnNext" onclick="goNext()">Next Letter</button>
      </div>

      <div class="hint" id="hintText">You can move forward without writing if nothing comes. Your silence is also data.</div>
    </div>
  </div>

  <!-- COMPLETE SCREEN -->
  <div class="screen" id="screenComplete">
    <div class="card">
      <div class="gold-label">Complete</div>
      <h1 class="card-title">Your responses have been received.</h1>
      <div class="card-body">
        <p style="margin-bottom:0;">Every word you wrote is part of your Soul Blueprint. Nothing is wrong. Nothing is too much. What you felt is exactly what needed to be felt.</p>
      </div>
      <a href="/dashboard" class="btn-primary" style="display:block;text-align:center;text-decoration:none;padding:16px;">Continue to My Portal</a>
    </div>
  </div>

</div>

<?php include 'includes/footer.php'; ?>

<script>
const LETTERS = [
  { id:1,  name:'Aleph',  pronounced:'AH-lef',   phonetic:'Silent — breathe out gently. No sound.' },
  { id:2,  name:'Bet',    pronounced:'BET',       phonetic:'Like the English word bet.' },
  { id:3,  name:'Gimel',  pronounced:'GEE-mel',   phonetic:'Hard G — like the word give.' },
  { id:4,  name:'Dalet',  pronounced:'DAH-let',   phonetic:'DAH as in father, let as in let.' },
  { id:5,  name:'Heh',    pronounced:'HEH',       phonetic:'A soft breath — like a gentle sigh.' },
  { id:6,  name:'Vav',    pronounced:'VAHV',      phonetic:'Like the word vow with a V.' },
  { id:7,  name:'Zayin',  pronounced:'ZAY-in',    phonetic:'ZAY rhymes with say, in as in in.' },
  { id:8,  name:'Chet',   pronounced:'KHET',      phonetic:'Deep guttural KH from back of throat.' },
  { id:9,  name:'Tet',    pronounced:'TET',       phonetic:'Like tet-a-tet — short T sound.' },
  { id:10, name:'Yod',    pronounced:'YODE',      phonetic:'Rhymes with road.' },
  { id:11, name:'Kaf',    pronounced:'KAHF',      phonetic:'Like the word cough.' },
  { id:12, name:'Lamed',  pronounced:'LAH-med',   phonetic:'LAH like la in music, med as in medicine.' },
  { id:13, name:'Mem',    pronounced:'MEM',       phonetic:'Like the letter M said twice.' },
  { id:14, name:'Nun',    pronounced:'NOON',      phonetic:'Like the word noon.' },
  { id:15, name:'Samech', pronounced:'SAH-mekh',  phonetic:'SAH as in father, mekh with guttural KH at end.' },
  { id:16, name:'Ayin',   pronounced:'AH-yin',    phonetic:'Silent guttural stop — AH from deep in throat, then yin.' },
  { id:17, name:'Peh',    pronounced:'PEH',       phonetic:'Like the letter P with a breath.' },
  { id:18, name:'Tzadi',  pronounced:'TZAH-dee',  phonetic:'TZ like end of pizza — TZAH-dee.' },
  { id:19, name:'Qof',    pronounced:'KOFE',      phonetic:'Deep K from back of throat — like coke with an F.' },
  { id:20, name:'Resh',   pronounced:'RAYSH',     phonetic:'Soft R — RAYSH rhymes with mesh.' },
  { id:21, name:'Shin',   pronounced:'SHEEN',     phonetic:'Like the word sheen.' },
  { id:22, name:'Tav',    pronounced:'TAHV',      phonetic:'Like the word top with a V.' },
];

const CSRF = <?= json_encode(csrf_token()) ?>;

let currentIndex = 0;
let startTime = null;
const responses = LETTERS.map(l => ({
  letterId: l.id,
  letterName: l.name,
  pronounced: l.pronounced,
  feltResponse: '',
  notes: '',
  responseTimeMs: null,
}));

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function startQuestionnaire() {
  currentIndex = 0;
  showScreen('screenQ');
  document.getElementById('progressRow').style.display = 'flex';
  document.getElementById('progressBar').style.display = 'block';
  startTime = Date.now();
  renderLetter();
}

function renderLetter() {
  const l = LETTERS[currentIndex];
  const r = responses[currentIndex];

  document.getElementById('letterName').textContent = l.name;
  document.getElementById('letterPronounced').textContent = l.pronounced;
  document.getElementById('letterPhonetic').textContent = l.phonetic;
  document.getElementById('feltResponse').value = r.feltResponse;
  document.getElementById('notesField').value = r.notes;
  document.getElementById('errorMsg').style.display = 'none';

  document.getElementById('progressLabel').textContent = 'Letter ' + (currentIndex + 1) + ' of 22';
  const pct = Math.round((currentIndex / 22) * 100);
  document.getElementById('progressPct').textContent = pct + '%';
  document.getElementById('progressFill').style.width = pct + '%';

  document.getElementById('btnBack').style.display = currentIndex > 0 ? 'block' : 'none';

  const isLast = currentIndex === LETTERS.length - 1;
  document.getElementById('btnNext').textContent = isLast ? 'Complete' : 'Next Letter';

  const hint = document.getElementById('hintText');
  hint.style.display = r.feltResponse ? 'none' : 'block';
  document.getElementById('feltResponse').addEventListener('input', function() {
    hint.style.display = this.value ? 'none' : 'block';
  }, { once: true });

  document.getElementById('feltResponse').focus();
}

function saveCurrentAndAdvance() {
  const ms = startTime ? Date.now() - startTime : null;
  responses[currentIndex].feltResponse = document.getElementById('feltResponse').value;
  responses[currentIndex].notes        = document.getElementById('notesField').value;
  responses[currentIndex].responseTimeMs = ms;
  startTime = Date.now();
}

function goNext() {
  saveCurrentAndAdvance();
  if (currentIndex < LETTERS.length - 1) {
    currentIndex++;
    renderLetter();
  } else {
    submitResponses();
  }
}

function goBack() {
  saveCurrentAndAdvance();
  if (currentIndex > 0) {
    currentIndex--;
    renderLetter();
  }
}

async function submitResponses() {
  const btn = document.getElementById('btnNext');
  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    const res = await fetch('/hebrewquestionnaire.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ responses, csrf: CSRF }),
    });
    const data = await res.json();
    if (data.ok) {
      document.getElementById('progressRow').style.display = 'none';
      document.getElementById('progressBar').style.display = 'none';
      showScreen('screenComplete');
    } else {
      document.getElementById('errorMsg').textContent = 'Could not save your responses. Please try again.';
      document.getElementById('errorMsg').style.display = 'block';
      btn.disabled = false;
      btn.textContent = 'Complete';
    }
  } catch (e) {
    document.getElementById('errorMsg').textContent = 'Network error. Please check your connection and try again.';
    document.getElementById('errorMsg').style.display = 'block';
    btn.disabled = false;
    btn.textContent = 'Complete';
  }
}
</script>
</body>
</html>
