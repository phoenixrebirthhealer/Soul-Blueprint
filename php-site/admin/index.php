<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Dashboard | Phoenix Rebirth</title>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --gold: #d4af37; --gold-light: #f0d060;
      --cream: #f5f0ff; --cream-dim: rgba(245,240,255,0.65); --cream-faint: rgba(245,240,255,0.35);
      --plum: #0f0520; --plum-mid: #1a0a2e; --plum-card: rgba(255,255,255,0.025);
      --magenta: #c2185b; --border: rgba(212,175,55,0.15);
    }
    body { background: var(--plum); color: var(--cream); font-family: 'Cormorant Garamond', serif; min-height: 100vh; }

    /* SIDEBAR */
    .sidebar { position: fixed; top: 0; left: 0; bottom: 0; width: 220px; background: var(--plum-mid); border-right: 1px solid var(--border); padding: 32px 0; display: flex; flex-direction: column; z-index: 10; }
    .sidebar-brand { font-family: 'Cinzel', serif; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--gold); padding: 0 24px 28px; border-bottom: 1px solid var(--border); }
    .sidebar-brand span { display: block; font-size: 8px; letter-spacing: 2px; color: var(--cream-faint); margin-top: 4px; }
    .sidebar nav { padding: 24px 0; flex: 1; }
    .nav-item { display: block; padding: 12px 24px; font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: var(--cream-dim); text-decoration: none; transition: all 0.2s; border-left: 2px solid transparent; }
    .nav-item:hover, .nav-item.active { color: var(--gold); border-left-color: var(--gold); background: rgba(212,175,55,0.04); }
    .nav-item.danger { color: var(--cream-faint); }
    .nav-item.danger:hover { color: #f48fb1; border-left-color: var(--magenta); }

    /* MAIN */
    .main { margin-left: 220px; padding: 40px 48px; }
    .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
    .page-title { font-family: 'Cinzel', serif; font-size: 22px; font-weight: 400; color: var(--cream); }
    .page-title span { color: var(--gold); }

    /* STATS */
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 48px; }
    .stat-card { background: var(--plum-card); border: 1px solid var(--border); padding: 24px; }
    .stat-label { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 3px; text-transform: uppercase; color: var(--cream-faint); margin-bottom: 10px; }
    .stat-value { font-family: 'Cinzel', serif; font-size: 32px; color: var(--gold); }
    .stat-sub { font-size: 13px; font-weight: 300; color: var(--cream-faint); margin-top: 4px; }

    /* CLIENT TABLE */
    .section-title { font-family: 'Cinzel', serif; font-size: 10px; letter-spacing: 4px; text-transform: uppercase; color: var(--cream-faint); margin-bottom: 16px; }
    .search-bar { width: 100%; background: rgba(255,255,255,0.03); border: 1px solid var(--border); color: var(--cream); font-family: 'Cormorant Garamond', serif; font-size: 15px; padding: 11px 16px; outline: none; margin-bottom: 16px; }
    .search-bar:focus { border-color: rgba(212,175,55,0.4); }
    .client-table { width: 100%; border-collapse: collapse; }
    .client-table th { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--cream-faint); text-align: left; padding: 12px 16px; border-bottom: 1px solid var(--border); }
    .client-table td { padding: 14px 16px; border-bottom: 1px solid rgba(212,175,55,0.05); font-size: 15px; font-weight: 300; color: var(--cream-dim); vertical-align: middle; }
    .client-table tr:hover td { background: rgba(212,175,55,0.03); }
    .client-table a { color: var(--gold); text-decoration: none; }
    .client-table a:hover { color: var(--gold-light); }
    .badge { display: inline-block; font-family: 'Cinzel', serif; font-size: 8px; letter-spacing: 1px; text-transform: uppercase; padding: 3px 8px; border-radius: 8px; }
    .badge.yes { background: rgba(0,200,83,0.1); color: #69f0ae; border: 1px solid rgba(0,200,83,0.2); }
    .badge.no { background: rgba(255,255,255,0.04); color: var(--cream-faint); border: 1px solid rgba(255,255,255,0.08); }
    .badge.pending { background: rgba(212,175,55,0.1); color: var(--gold); border: 1px solid rgba(212,175,55,0.2); }
    .btn-view { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: var(--gold); background: rgba(212,175,55,0.06); border: 1px solid rgba(212,175,55,0.2); padding: 7px 14px; text-decoration: none; transition: all 0.2s; white-space: nowrap; }
    .btn-view:hover { border-color: var(--gold); color: var(--gold-light); }
    .empty { text-align: center; padding: 60px; color: var(--cream-faint); font-style: italic; font-size: 16px; }
  </style>
</head>
<body>
<?php
require_once __DIR__ . '/includes/admin-auth.php';
admin_require_login();

$db = get_db();

// Stats
$total_clients    = $db->query('SELECT COUNT(*) FROM clients')->fetchColumn();
$intake_done      = $db->query('SELECT COUNT(*) FROM clients WHERE intake_complete = 1')->fetchColumn();
$assessments_done = $db->query('SELECT COUNT(DISTINCT client_id) FROM assessments')->fetchColumn();
$readings_done    = $db->query('SELECT COUNT(*) FROM readings WHERE status = "complete"')->fetchColumn();

// Client list with latest assessment and reading counts
$clients = $db->query('
  SELECT c.*,
    a.self_love_score, a.attachment_style,
    (SELECT COUNT(*) FROM readings r WHERE r.client_id = c.id AND r.status = "complete") AS readings_complete,
    (SELECT COUNT(*) FROM readings r WHERE r.client_id = c.id) AS readings_total
  FROM clients c
  LEFT JOIN assessments a ON a.client_id = c.id
  GROUP BY c.id
  ORDER BY c.created_at DESC
')->fetchAll();
?>

<aside class="sidebar">
  <div class="sidebar-brand">Phoenix Rebirth<span>Admin Panel</span></div>
  <nav>
    <a href="/admin/" class="nav-item active">Dashboard</a>
    <a href="/admin/?filter=no_intake" class="nav-item">Awaiting Intake</a>
    <a href="/admin/?filter=no_assessment" class="nav-item">Awaiting Assessment</a>
    <a href="/admin/?filter=has_readings" class="nav-item">Has Readings</a>
  </nav>
  <div style="padding: 0 24px 24px;">
    <a href="/admin/logout.php" class="nav-item danger" style="display:block;padding-left:0;">Sign Out</a>
  </div>
</aside>

<div class="main">
  <div class="page-header">
    <div class="page-title">Admin <span>Dashboard</span></div>
    <div style="font-size:13px;color:var(--cream-faint);">Phoenix Rebirth | Christina Stevens</div>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">Total Clients</div>
      <div class="stat-value"><?= $total_clients ?></div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Intake Complete</div>
      <div class="stat-value"><?= $intake_done ?></div>
      <div class="stat-sub"><?= $total_clients > 0 ? round($intake_done/$total_clients*100) : 0 ?>% of clients</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Assessment Done</div>
      <div class="stat-value"><?= $assessments_done ?></div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Readings Generated</div>
      <div class="stat-value"><?= $readings_done ?></div>
    </div>
  </div>

  <div class="section-title">All Clients</div>
  <input class="search-bar" type="text" id="clientSearch" placeholder="Search by name or email..." oninput="filterClients()">

  <?php if (empty($clients)): ?>
    <div class="empty">No clients yet.</div>
  <?php else: ?>
  <table class="client-table" id="clientTable">
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Joined</th>
        <th>Intake</th>
        <th>Assessment</th>
        <th>Score</th>
        <th>Readings</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($clients as $c): ?>
      <tr>
        <td><strong style="color:var(--cream)"><?= htmlspecialchars(trim(($c['first_name'] ?? '') . ' ' . ($c['last_name'] ?? ''))) ?: '(No name yet)' ?></strong></td>
        <td><?= htmlspecialchars($c['email']) ?></td>
        <td style="font-size:13px;color:var(--cream-faint)"><?= date('M j, Y', strtotime($c['created_at'])) ?></td>
        <td><?= $c['intake_complete'] ? '<span class="badge yes">Done</span>' : '<span class="badge no">Pending</span>' ?></td>
        <td><?= $c['attachment_style'] ? '<span class="badge yes">Done</span>' : '<span class="badge no">Pending</span>' ?></td>
        <td><?= $c['self_love_score'] !== null ? '<span style="color:var(--gold)">' . intval($c['self_love_score']) . '/85</span>' : '<span style="color:var(--cream-faint)">--</span>' ?></td>
        <td><?= $c['readings_complete'] > 0 ? '<span class="badge yes">' . $c['readings_complete'] . ' ready</span>' : ($c['readings_total'] > 0 ? '<span class="badge pending">In progress</span>' : '<span style="color:var(--cream-faint)">None</span>') ?></td>
        <td><a href="/admin/client.php?id=<?= $c['id'] ?>" class="btn-view">View &rarr;</a></td>
      </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
  <?php endif; ?>
</div>

<script>
function filterClients() {
  const q = document.getElementById('clientSearch').value.toLowerCase();
  document.querySelectorAll('#clientTable tbody tr').forEach(row => {
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}
</script>
</body>
</html>
