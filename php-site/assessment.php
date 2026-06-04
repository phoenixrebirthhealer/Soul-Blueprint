<?php
require_once 'includes/auth.php';

if (is_logged_in()) {
    if (has_completed_assessment()) {
        header('Location: /dashboard');
        exit;
    }
    // Logged-in user redoing assessment -- allowed through
} else {
    // New registration flow -- must have completed both prior steps
    if (empty($_SESSION['reg'])) {
        header('Location: /register');
        exit;
    }
    if (empty($_SESSION['intake'])) {
        header('Location: /intake');
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Self-Love Assessment | Phoenix Rebirth</title>
  <?php include 'includes/head.php'; ?>
  <style>
    body { min-height: 100vh; display: flex; flex-direction: column; }
    .main { flex: 1; padding: 120px 40px 80px; }
    .inner { max-width: 760px; margin: 0 auto; }
    .page-title { font-family: 'Cinzel', serif; font-size: clamp(22px,3vw,38px); font-weight: 400; color: var(--cream); margin-bottom: 10px; }
    .page-title em { color: var(--gold); font-style: normal; }
    .page-sub { font-size: 16px; font-weight: 300; color: var(--cream-dim); margin-bottom: 16px; line-height: 1.8; max-width: 600px; }
    .progress-bar { height: 2px; background: rgba(212,175,55,0.1); margin-bottom: 48px; }
    .progress-fill { height: 2px; background: var(--gold); transition: width 0.4s ease; }

    .question-block { display: none; }
    .question-block.active { display: block; animation: fadeIn 0.5s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    .q-num { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 4px; color: var(--gold); opacity: 0.5; text-transform: uppercase; margin-bottom: 16px; }
    .q-section { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 3px; color: var(--magenta); opacity: 0.6; text-transform: uppercase; margin-bottom: 10px; }
    .q-text { font-family: 'Cormorant Garamond', serif; font-size: clamp(18px,2.5vw,26px); font-weight: 400; color: var(--cream); margin-bottom: 36px; line-height: 1.5; }

    .options { display: flex; flex-direction: column; gap: 10px; }
    .option-btn {
      display: flex; align-items: center; gap: 16px;
      background: rgba(255,255,255,0.02); border: 1px solid rgba(212,175,55,0.12);
      color: var(--cream-dim); font-family: 'Cormorant Garamond', serif;
      font-size: 17px; font-weight: 300; padding: 16px 22px;
      cursor: pointer; transition: all 0.25s; text-align: left;
    }
    .option-btn:hover { border-color: rgba(212,175,55,0.35); color: var(--cream); background: rgba(212,175,55,0.05); }
    .option-btn.selected { border-color: var(--gold); color: var(--cream); background: rgba(212,175,55,0.08); }
    .option-dot { width: 8px; height: 8px; border-radius: 50%; border: 1px solid rgba(212,175,55,0.4); flex-shrink: 0; transition: all 0.25s; }
    .option-btn.selected .option-dot { background: var(--gold); border-color: var(--gold); }

    .nav-row { display: flex; justify-content: space-between; align-items: center; margin-top: 40px; }
    .nav-btn-q { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); background: none; border: 1px solid rgba(212,175,55,0.2); padding: 14px 28px; cursor: pointer; transition: all 0.3s; }
    .nav-btn-q:hover { border-color: var(--gold); }
    .nav-btn-q:disabled { opacity: 0.25; cursor: default; }
    .nav-btn-q.next { background: rgba(212,175,55,0.08); }

    .q-counter { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 2px; color: var(--cream-dim); opacity: 0.4; }
    .steps { display: flex; justify-content: center; gap: 8px; margin-bottom: 36px; }
    .step { width: 32px; height: 3px; background: rgba(212,175,55,0.15); }
    .step.active { background: var(--gold); }
  </style>
</head>
<body>
<?php include 'includes/nav.php'; ?>

<div class="main">
  <div class="inner">
    <?php if (!is_logged_in()): ?>
    <div class="steps">
      <div class="step"></div>
      <div class="step"></div>
      <div class="step active"></div>
    </div>
    <?php endif; ?>
    <h1 class="page-title">Self-Love <em>Assessment</em></h1>
    <p class="page-sub">24 questions. No wrong answers. Answer what is true right now, not what you wish were true.</p>

    <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:4%"></div></div>

    <form method="POST" action="/assessment-submit" id="assessmentForm">
      <input type="hidden" name="csrf_token" value="<?= csrf_token() ?>">

      <!-- Q1 -->
      <div class="question-block active" data-q="1">
        <div class="q-section">Current Emotional State</div>
        <div class="q-num">Question 1 of 24</div>
        <div class="q-text">How would you describe your current relationship with yourself?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q1" data-value="5"><span class="option-dot"></span>I genuinely like and respect myself</button>
          <button type="button" class="option-btn" data-name="q1" data-value="4"><span class="option-dot"></span>I like parts of myself but struggle with others</button>
          <button type="button" class="option-btn" data-name="q1" data-value="3"><span class="option-dot"></span>I am very critical of myself</button>
          <button type="button" class="option-btn" data-name="q1" data-value="2"><span class="option-dot"></span>I feel disconnected from who I really am</button>
          <button type="button" class="option-btn" data-name="q1" data-value="1"><span class="option-dot"></span>I often feel like I don't know myself at all</button>
        </div>
        <input type="hidden" name="q1" id="q1_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(1)" disabled>Back</button>
          <span class="q-counter">1 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(1)">Next</button>
        </div>
      </div>

      <!-- Q2 -->
      <div class="question-block" data-q="2">
        <div class="q-section">Current Emotional State</div>
        <div class="q-num">Question 2 of 24</div>
        <div class="q-text">When something goes wrong in your life, your first thought is usually:</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q2" data-value="5"><span class="option-dot"></span>What can I learn from this?</button>
          <button type="button" class="option-btn" data-name="q2" data-value="4"><span class="option-dot"></span>I probably caused this somehow</button>
          <button type="button" class="option-btn" data-name="q2" data-value="3"><span class="option-dot"></span>Things never work out for me</button>
          <button type="button" class="option-btn" data-name="q2" data-value="2"><span class="option-dot"></span>People always let me down</button>
          <button type="button" class="option-btn" data-name="q2" data-value="1"><span class="option-dot"></span>I should have done something differently</button>
        </div>
        <input type="hidden" name="q2" id="q2_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(2)">Back</button>
          <span class="q-counter">2 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(2)">Next</button>
        </div>
      </div>

      <!-- Q3 -->
      <div class="question-block" data-q="3">
        <div class="q-section">Current Emotional State</div>
        <div class="q-num">Question 3 of 24</div>
        <div class="q-text">How often do you feel emotionally overwhelmed?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q3" data-value="5"><span class="option-dot"></span>Rarely</button>
          <button type="button" class="option-btn" data-name="q3" data-value="4"><span class="option-dot"></span>Occasionally</button>
          <button type="button" class="option-btn" data-name="q3" data-value="3"><span class="option-dot"></span>Sometimes</button>
          <button type="button" class="option-btn" data-name="q3" data-value="2"><span class="option-dot"></span>Frequently</button>
          <button type="button" class="option-btn" data-name="q3" data-value="1"><span class="option-dot"></span>Almost constantly</button>
        </div>
        <input type="hidden" name="q3" id="q3_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(3)">Back</button>
          <span class="q-counter">3 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(3)">Next</button>
        </div>
      </div>

      <!-- Q4 -->
      <div class="question-block" data-q="4">
        <div class="q-section">Current Emotional State</div>
        <div class="q-num">Question 4 of 24</div>
        <div class="q-text">Which statement resonates most with you?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q4" data-value="5"><span class="option-dot"></span>I trust my decisions</button>
          <button type="button" class="option-btn" data-name="q4" data-value="4"><span class="option-dot"></span>I often second-guess myself</button>
          <button type="button" class="option-btn" data-name="q4" data-value="3"><span class="option-dot"></span>I rely heavily on others for validation</button>
          <button type="button" class="option-btn" data-name="q4" data-value="2"><span class="option-dot"></span>I avoid making decisions if possible</button>
          <button type="button" class="option-btn" data-name="q4" data-value="1"><span class="option-dot"></span>I feel paralyzed when making important choices</button>
        </div>
        <input type="hidden" name="q4" id="q4_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(4)">Back</button>
          <span class="q-counter">4 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(4)">Next</button>
        </div>
      </div>

      <!-- Q5 -->
      <div class="question-block" data-q="5">
        <div class="q-section">Childhood Emotional Environment</div>
        <div class="q-num">Question 5 of 24</div>
        <div class="q-text">Growing up, how emotionally safe did you feel in your home?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q5" data-value="5"><span class="option-dot"></span>Very safe</button>
          <button type="button" class="option-btn" data-name="q5" data-value="4"><span class="option-dot"></span>Mostly safe</button>
          <button type="button" class="option-btn" data-name="q5" data-value="3"><span class="option-dot"></span>Neutral</button>
          <button type="button" class="option-btn" data-name="q5" data-value="2"><span class="option-dot"></span>Often unsafe</button>
          <button type="button" class="option-btn" data-name="q5" data-value="1"><span class="option-dot"></span>Consistently unsafe</button>
        </div>
        <input type="hidden" name="q5" id="q5_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(5)">Back</button>
          <span class="q-counter">5 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(5)">Next</button>
        </div>
      </div>

      <!-- Q6 -->
      <div class="question-block" data-q="6">
        <div class="q-section">Childhood Emotional Environment</div>
        <div class="q-num">Question 6 of 24</div>
        <div class="q-text">When you expressed emotions as a child, the response you usually received was:</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q6" data-value="5"><span class="option-dot"></span>Comfort and support</button>
          <button type="button" class="option-btn" data-name="q6" data-value="4"><span class="option-dot"></span>Advice or problem solving</button>
          <button type="button" class="option-btn" data-name="q6" data-value="3"><span class="option-dot"></span>Being told to toughen up</button>
          <button type="button" class="option-btn" data-name="q6" data-value="2"><span class="option-dot"></span>Being ignored</button>
          <button type="button" class="option-btn" data-name="q6" data-value="1"><span class="option-dot"></span>Being punished or criticized</button>
        </div>
        <input type="hidden" name="q6" id="q6_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(6)">Back</button>
          <span class="q-counter">6 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(6)">Next</button>
        </div>
      </div>

      <!-- Q7 -->
      <div class="question-block" data-q="7">
        <div class="q-section">Childhood Emotional Environment</div>
        <div class="q-num">Question 7 of 24</div>
        <div class="q-text">How predictable were the emotional reactions of your caregivers?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q7" data-value="5"><span class="option-dot"></span>Very predictable and stable</button>
          <button type="button" class="option-btn" data-name="q7" data-value="4"><span class="option-dot"></span>Mostly predictable</button>
          <button type="button" class="option-btn" data-name="q7" data-value="3"><span class="option-dot"></span>Somewhat unpredictable</button>
          <button type="button" class="option-btn" data-name="q7" data-value="2"><span class="option-dot"></span>Frequently unpredictable</button>
          <button type="button" class="option-btn" data-name="q7" data-value="1"><span class="option-dot"></span>Completely unpredictable</button>
        </div>
        <input type="hidden" name="q7" id="q7_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(7)">Back</button>
          <span class="q-counter">7 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(7)">Next</button>
        </div>
      </div>

      <!-- Q8 -->
      <div class="question-block" data-q="8">
        <div class="q-section">Childhood Emotional Environment</div>
        <div class="q-num">Question 8 of 24</div>
        <div class="q-text">Did you feel responsible for other people's emotions growing up?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q8" data-value="5"><span class="option-dot"></span>Never</button>
          <button type="button" class="option-btn" data-name="q8" data-value="4"><span class="option-dot"></span>Rarely</button>
          <button type="button" class="option-btn" data-name="q8" data-value="3"><span class="option-dot"></span>Sometimes</button>
          <button type="button" class="option-btn" data-name="q8" data-value="2"><span class="option-dot"></span>Often</button>
          <button type="button" class="option-btn" data-name="q8" data-value="1"><span class="option-dot"></span>Almost always</button>
        </div>
        <input type="hidden" name="q8" id="q8_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(8)">Back</button>
          <span class="q-counter">8 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(8)">Next</button>
        </div>
      </div>

      <!-- Q9 (Attachment) -->
      <div class="question-block" data-q="9">
        <div class="q-section">Relationship Patterns</div>
        <div class="q-num">Question 9 of 24</div>
        <div class="q-text">In close relationships, I tend to:</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q9" data-value="S"><span class="option-dot"></span>Feel secure and comfortable</button>
          <button type="button" class="option-btn" data-name="q9" data-value="A"><span class="option-dot"></span>Worry about being abandoned</button>
          <button type="button" class="option-btn" data-name="q9" data-value="V"><span class="option-dot"></span>Avoid emotional closeness</button>
          <button type="button" class="option-btn" data-name="q9" data-value="D"><span class="option-dot"></span>Feel both needy and distant at different times</button>
        </div>
        <input type="hidden" name="q9" id="q9_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(9)">Back</button>
          <span class="q-counter">9 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(9)">Next</button>
        </div>
      </div>

      <!-- Q10 -->
      <div class="question-block" data-q="10">
        <div class="q-section">Relationship Patterns</div>
        <div class="q-num">Question 10 of 24</div>
        <div class="q-text">When someone gets emotionally close to you, your instinct is to:</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q10" data-value="S"><span class="option-dot"></span>Welcome the connection</button>
          <button type="button" class="option-btn" data-name="q10" data-value="A"><span class="option-dot"></span>Feel nervous but stay present</button>
          <button type="button" class="option-btn" data-name="q10" data-value="V"><span class="option-dot"></span>Pull away</button>
          <button type="button" class="option-btn" data-name="q10" data-value="D"><span class="option-dot"></span>Feel confused and emotionally overwhelmed</button>
        </div>
        <input type="hidden" name="q10" id="q10_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(10)">Back</button>
          <span class="q-counter">10 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(10)">Next</button>
        </div>
      </div>

      <!-- Q11 -->
      <div class="question-block" data-q="11">
        <div class="q-section">Relationship Patterns</div>
        <div class="q-num">Question 11 of 24</div>
        <div class="q-text">When conflict happens in relationships, you usually:</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q11" data-value="S"><span class="option-dot"></span>Address it calmly</button>
          <button type="button" class="option-btn" data-name="q11" data-value="A"><span class="option-dot"></span>Try to fix things immediately</button>
          <button type="button" class="option-btn" data-name="q11" data-value="V"><span class="option-dot"></span>Avoid the conversation</button>
          <button type="button" class="option-btn" data-name="q11" data-value="D"><span class="option-dot"></span>Shut down emotionally</button>
        </div>
        <input type="hidden" name="q11" id="q11_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(11)">Back</button>
          <span class="q-counter">11 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(11)">Next</button>
        </div>
      </div>

      <!-- Q12 -->
      <div class="question-block" data-q="12">
        <div class="q-section">Attachment Style</div>
        <div class="q-num">Question 12 of 24</div>
        <div class="q-text">Which statement feels most accurate?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q12" data-value="S"><span class="option-dot"></span>I generally trust people and feel comfortable relying on them</button>
          <button type="button" class="option-btn" data-name="q12" data-value="A"><span class="option-dot"></span>I worry that people will eventually leave me</button>
          <button type="button" class="option-btn" data-name="q12" data-value="V"><span class="option-dot"></span>I value independence and avoid relying on others</button>
          <button type="button" class="option-btn" data-name="q12" data-value="D"><span class="option-dot"></span>I want closeness but feel afraid of it at the same time</button>
        </div>
        <input type="hidden" name="q12" id="q12_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(12)">Back</button>
          <span class="q-counter">12 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(12)">Next</button>
        </div>
      </div>

      <!-- Q13 -->
      <div class="question-block" data-q="13">
        <div class="q-section">Attachment Style</div>
        <div class="q-num">Question 13 of 24</div>
        <div class="q-text">When someone important to you pulls away emotionally, you usually:</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q13" data-value="S"><span class="option-dot"></span>Give them space and trust things will resolve</button>
          <button type="button" class="option-btn" data-name="q13" data-value="A"><span class="option-dot"></span>Feel anxious and try to reconnect immediately</button>
          <button type="button" class="option-btn" data-name="q13" data-value="V"><span class="option-dot"></span>Distance yourself further</button>
          <button type="button" class="option-btn" data-name="q13" data-value="D"><span class="option-dot"></span>Oscillate between clinging and pushing away</button>
        </div>
        <input type="hidden" name="q13" id="q13_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(13)">Back</button>
          <span class="q-counter">13 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(13)">Next</button>
        </div>
      </div>

      <!-- Q14 -->
      <div class="question-block" data-q="14">
        <div class="q-section">Attachment Style</div>
        <div class="q-num">Question 14 of 24</div>
        <div class="q-text">How do you respond to vulnerability in relationships?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q14" data-value="S"><span class="option-dot"></span>I'm comfortable expressing emotions</button>
          <button type="button" class="option-btn" data-name="q14" data-value="A"><span class="option-dot"></span>I want to share but fear rejection</button>
          <button type="button" class="option-btn" data-name="q14" data-value="V"><span class="option-dot"></span>I avoid emotional conversations</button>
          <button type="button" class="option-btn" data-name="q14" data-value="D"><span class="option-dot"></span>I share sometimes but then regret it</button>
        </div>
        <input type="hidden" name="q14" id="q14_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(14)">Back</button>
          <span class="q-counter">14 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(14)">Next</button>
        </div>
      </div>

      <!-- Q15 -->
      <div class="question-block" data-q="15">
        <div class="q-section">Self-Worth &amp; Identity</div>
        <div class="q-num">Question 15 of 24</div>
        <div class="q-text">Which belief do you resonate with the most?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q15" data-value="5"><span class="option-dot"></span>I am worthy of love as I am</button>
          <button type="button" class="option-btn" data-name="q15" data-value="4"><span class="option-dot"></span>I need to earn love</button>
          <button type="button" class="option-btn" data-name="q15" data-value="3"><span class="option-dot"></span>Love eventually disappears</button>
          <button type="button" class="option-btn" data-name="q15" data-value="2"><span class="option-dot"></span>It's safer not to depend on people</button>
          <button type="button" class="option-btn" data-name="q15" data-value="1"><span class="option-dot"></span>I don't believe in love</button>
        </div>
        <input type="hidden" name="q15" id="q15_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(15)">Back</button>
          <span class="q-counter">15 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(15)">Next</button>
        </div>
      </div>

      <!-- Q16 -->
      <div class="question-block" data-q="16">
        <div class="q-section">Self-Worth &amp; Identity</div>
        <div class="q-num">Question 16 of 24</div>
        <div class="q-text">How comfortable are you receiving love or support?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q16" data-value="5"><span class="option-dot"></span>Very comfortable</button>
          <button type="button" class="option-btn" data-name="q16" data-value="4"><span class="option-dot"></span>Somewhat comfortable</button>
          <button type="button" class="option-btn" data-name="q16" data-value="3"><span class="option-dot"></span>Neutral</button>
          <button type="button" class="option-btn" data-name="q16" data-value="2"><span class="option-dot"></span>Uncomfortable</button>
          <button type="button" class="option-btn" data-name="q16" data-value="1"><span class="option-dot"></span>Extremely uncomfortable</button>
        </div>
        <input type="hidden" name="q16" id="q16_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(16)">Back</button>
          <span class="q-counter">16 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(16)">Next</button>
        </div>
      </div>

      <!-- Q17 -->
      <div class="question-block" data-q="17">
        <div class="q-section">Self-Worth &amp; Identity</div>
        <div class="q-num">Question 17 of 24</div>
        <div class="q-text">When someone compliments you, you usually:</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q17" data-value="5"><span class="option-dot"></span>Accept it easily</button>
          <button type="button" class="option-btn" data-name="q17" data-value="4"><span class="option-dot"></span>Appreciate it but feel awkward</button>
          <button type="button" class="option-btn" data-name="q17" data-value="3"><span class="option-dot"></span>Deflect the compliment</button>
          <button type="button" class="option-btn" data-name="q17" data-value="2"><span class="option-dot"></span>Assume they're just being nice</button>
          <button type="button" class="option-btn" data-name="q17" data-value="1"><span class="option-dot"></span>Believe they are mistaken</button>
        </div>
        <input type="hidden" name="q17" id="q17_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(17)">Back</button>
          <span class="q-counter">17 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(17)">Next</button>
        </div>
      </div>

      <!-- Q18 -->
      <div class="question-block" data-q="18">
        <div class="q-section">Energy &amp; Emotional Drain</div>
        <div class="q-num">Question 18 of 24</div>
        <div class="q-text">What drains your energy the most?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q18" data-value="5"><span class="option-dot"></span>Feeling misunderstood</button>
          <button type="button" class="option-btn" data-name="q18" data-value="4"><span class="option-dot"></span>Emotional caretaking</button>
          <button type="button" class="option-btn" data-name="q18" data-value="3"><span class="option-dot"></span>People pleasing</button>
          <button type="button" class="option-btn" data-name="q18" data-value="2"><span class="option-dot"></span>Overthinking</button>
          <button type="button" class="option-btn" data-name="q18" data-value="1"><span class="option-dot"></span>Conflict</button>
        </div>
        <input type="hidden" name="q18" id="q18_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(18)">Back</button>
          <span class="q-counter">18 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(18)">Next</button>
        </div>
      </div>

      <!-- Q19 -->
      <div class="question-block" data-q="19">
        <div class="q-section">Energy &amp; Emotional Drain</div>
        <div class="q-num">Question 19 of 24</div>
        <div class="q-text">After spending time with people, you usually feel:</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q19" data-value="5"><span class="option-dot"></span>Energized</button>
          <button type="button" class="option-btn" data-name="q19" data-value="4"><span class="option-dot"></span>Neutral</button>
          <button type="button" class="option-btn" data-name="q19" data-value="3"><span class="option-dot"></span>Slightly drained</button>
          <button type="button" class="option-btn" data-name="q19" data-value="2"><span class="option-dot"></span>Emotionally exhausted</button>
          <button type="button" class="option-btn" data-name="q19" data-value="1"><span class="option-dot"></span>Completely depleted</button>
        </div>
        <input type="hidden" name="q19" id="q19_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(19)">Back</button>
          <span class="q-counter">19 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(19)">Next</button>
        </div>
      </div>

      <!-- Q20 -->
      <div class="question-block" data-q="20">
        <div class="q-section">Energy &amp; Emotional Drain</div>
        <div class="q-num">Question 20 of 24</div>
        <div class="q-text">How often do you ignore your own needs to meet someone else's?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q20" data-value="5"><span class="option-dot"></span>Never</button>
          <button type="button" class="option-btn" data-name="q20" data-value="4"><span class="option-dot"></span>Rarely</button>
          <button type="button" class="option-btn" data-name="q20" data-value="3"><span class="option-dot"></span>Sometimes</button>
          <button type="button" class="option-btn" data-name="q20" data-value="2"><span class="option-dot"></span>Often</button>
          <button type="button" class="option-btn" data-name="q20" data-value="1"><span class="option-dot"></span>Almost always</button>
        </div>
        <input type="hidden" name="q20" id="q20_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(20)">Back</button>
          <span class="q-counter">20 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(20)">Next</button>
        </div>
      </div>

      <!-- Q21 -->
      <div class="question-block" data-q="21">
        <div class="q-section">Self-Care Awareness</div>
        <div class="q-num">Question 21 of 24</div>
        <div class="q-text">How consistent are you with self-care?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q21" data-value="5"><span class="option-dot"></span>Very consistent</button>
          <button type="button" class="option-btn" data-name="q21" data-value="4"><span class="option-dot"></span>Somewhat consistent</button>
          <button type="button" class="option-btn" data-name="q21" data-value="3"><span class="option-dot"></span>Occasionally</button>
          <button type="button" class="option-btn" data-name="q21" data-value="2"><span class="option-dot"></span>Rarely</button>
          <button type="button" class="option-btn" data-name="q21" data-value="1"><span class="option-dot"></span>Never</button>
        </div>
        <input type="hidden" name="q21" id="q21_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(21)">Back</button>
          <span class="q-counter">21 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(21)">Next</button>
        </div>
      </div>

      <!-- Q22 -->
      <div class="question-block" data-q="22">
        <div class="q-section">Self-Care Awareness</div>
        <div class="q-num">Question 22 of 24</div>
        <div class="q-text">When you feel emotionally triggered, your typical reaction is:</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q22" data-value="5"><span class="option-dot"></span>Pause and reflect</button>
          <button type="button" class="option-btn" data-name="q22" data-value="4"><span class="option-dot"></span>Talk it through</button>
          <button type="button" class="option-btn" data-name="q22" data-value="3"><span class="option-dot"></span>Distract myself</button>
          <button type="button" class="option-btn" data-name="q22" data-value="2"><span class="option-dot"></span>Withdraw</button>
          <button type="button" class="option-btn" data-name="q22" data-value="1"><span class="option-dot"></span>React emotionally</button>
        </div>
        <input type="hidden" name="q22" id="q22_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(22)">Back</button>
          <span class="q-counter">22 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(22)">Next</button>
        </div>
      </div>

      <!-- Q23 -->
      <div class="question-block" data-q="23">
        <div class="q-section">Readiness for Transformation</div>
        <div class="q-num">Question 23 of 24</div>
        <div class="q-text">Are you willing to face uncomfortable emotions if it leads to real transformation?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q23" data-value="5"><span class="option-dot"></span>Yes, completely ready</button>
          <button type="button" class="option-btn" data-name="q23" data-value="4"><span class="option-dot"></span>Yes, but I feel nervous</button>
          <button type="button" class="option-btn" data-name="q23" data-value="3"><span class="option-dot"></span>I think so</button>
          <button type="button" class="option-btn" data-name="q23" data-value="2"><span class="option-dot"></span>I'm unsure</button>
          <button type="button" class="option-btn" data-name="q23" data-value="1"><span class="option-dot"></span>I'm afraid to do that work</button>
        </div>
        <input type="hidden" name="q23" id="q23_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(23)">Back</button>
          <span class="q-counter">23 / 24</span>
          <button type="button" class="nav-btn-q next" onclick="nextQ(23)">Next</button>
        </div>
      </div>

      <!-- Q24 -->
      <div class="question-block" data-q="24">
        <div class="q-section">Readiness for Transformation</div>
        <div class="q-num">Question 24 of 24</div>
        <div class="q-text">What do you most hope to gain from this transformation?</div>
        <div class="options">
          <button type="button" class="option-btn" data-name="q24" data-value="5"><span class="option-dot"></span>Self-confidence</button>
          <button type="button" class="option-btn" data-name="q24" data-value="4"><span class="option-dot"></span>Emotional peace</button>
          <button type="button" class="option-btn" data-name="q24" data-value="3"><span class="option-dot"></span>Healthier relationships</button>
          <button type="button" class="option-btn" data-name="q24" data-value="2"><span class="option-dot"></span>Clarity about myself</button>
          <button type="button" class="option-btn" data-name="q24" data-value="1"><span class="option-dot"></span>Healing from past wounds</button>
        </div>
        <input type="hidden" name="q24" id="q24_val">
        <div class="nav-row">
          <button type="button" class="nav-btn-q" onclick="prevQ(24)">Back</button>
          <span class="q-counter">24 / 24</span>
          <button type="submit" class="nav-btn-q next btn-primary" id="submitBtn" style="font-family:'Cinzel',serif;font-size:11px;letter-spacing:3px;">Complete Assessment</button>
        </div>
      </div>

    </form>
  </div>
</div>

<script>
let current = 1;
const total = 24;
const answers = {};

function showQ(n) {
  document.querySelectorAll('.question-block').forEach(el => el.classList.remove('active'));
  const block = document.querySelector('[data-q="' + n + '"]');
  if (block) block.classList.add('active');
  document.getElementById('progressFill').style.width = ((n / total) * 100) + '%';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function nextQ(n) {
  const val = answers['q' + n];
  if (!val) { highlightUnanswered(n); return; }
  if (n < total) { current = n + 1; showQ(current); }
}

function prevQ(n) {
  if (n > 1) { current = n - 1; showQ(current); }
}

function highlightUnanswered(n) {
  const block = document.querySelector('[data-q="' + n + '"]');
  if (block) {
    block.style.borderLeft = '2px solid var(--magenta)';
    setTimeout(() => { block.style.borderLeft = ''; }, 1500);
  }
}

document.querySelectorAll('.option-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    const name = this.dataset.name;
    const val  = this.dataset.value;
    answers[name] = val;
    document.getElementById(name + '_val').value = val;

    const siblings = document.querySelectorAll('[data-name="' + name + '"]');
    siblings.forEach(b => b.classList.remove('selected'));
    this.classList.add('selected');
  });
});

document.getElementById('assessmentForm').addEventListener('submit', function(e) {
  for (let i = 1; i <= total; i++) {
    if (!answers['q' + i]) {
      e.preventDefault();
      showQ(i);
      highlightUnanswered(i);
      return;
    }
  }
});
</script>

<?php include 'includes/footer.php'; ?>
</body>
</html>
