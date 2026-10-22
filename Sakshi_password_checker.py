import re
import math
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

COMMON_PASSWORDS = [
    "password", "123456", "12345678", "password123", "qwerty",
    "abc123", "letmein", "admin", "welcome", "monkey",
    "1234567890", "iloveyou", "sunshine", "princess", "dragon",
    "master", "pass", "hello", "shadow", "superman",
]

def evaluate_rules(password):
    rules = [
        ("At least 8 characters",  len(password) >= 8),
        ("Uppercase letter (A-Z)", bool(re.search(r"[A-Z]", password))),
        ("Lowercase letter (a-z)", bool(re.search(r"[a-z]", password))),
        ("Number (0-9)",           bool(re.search(r"\d", password))),
        ("Special symbol (!@#$)",  bool(re.search(r"[!@#$%^&*()\-_=+\[\]{};:'\",.<>/?\\|`~]", password))),
    ]
    return [{"label": label, "passed": passed} for label, passed in rules]

def calc_entropy(password):
    if not password: return 0.0
    pool = 0
    if re.search(r"[a-z]", password): pool += 26
    if re.search(r"[A-Z]", password): pool += 26
    if re.search(r"\d",    password): pool += 10
    if re.search(r"[!@#$%^&*()\-_=+\[\]{};:'\",.<>/?\\|`~]", password): pool += 32
    if pool == 0: pool = 26
    return len(password) * math.log2(pool)

def score_password(entropy):
    if entropy < 28:  return {"label": "Weak",   "percent": 25}
    if entropy < 36:  return {"label": "Fair",   "percent": 50}
    if entropy < 60:  return {"label": "Good",   "percent": 75}
    return             {"label": "Strong", "percent": 100}

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>PassCheck &mdash; Password Strength Checker</title>
  <style>
    :root {
      --page-bg:#f0f2f5; --nav-bg:#fff; --nav-bd:#e5e7eb;
      --card-bg:#fff; --text:#1f2937; --muted:#6b7280;
      --border:#e5e7eb; --input-bg:#fff; --surface:#f9fafb;
      --surface-b:#f3f4f6; --divider:#e5e7eb;
      --tip-bg:#f0fdf4; --tip-bd:#bbf7d0;
      --footer-bg:#1e2235; --footer-txt:#94a3b8;
      --accent:#667eea; --accent2:#764ba2;
    }
    [data-theme="dark"] {
      --page-bg:#0f172a; --nav-bg:#1e2235; --nav-bd:#334155;
      --card-bg:#1e2235; --text:#f1f5f9; --muted:#94a3b8;
      --border:#334155; --input-bg:#0f172a; --surface:#0f172a;
      --surface-b:#1e293b; --divider:#334155;
      --tip-bg:#052e16; --tip-bd:#166534;
      --footer-bg:#0a0f1e; --footer-txt:#475569;
    }
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    html{scroll-behavior:smooth}
    body{font-family:-apple-system,"Segoe UI",system-ui,sans-serif;font-size:15px;
      line-height:1.6;background:var(--page-bg);color:var(--text);
      min-height:100vh;display:flex;flex-direction:column;
      transition:background .3s,color .3s}

    /* ── Navbar ── */
    .navbar{position:sticky;top:0;z-index:100;background:var(--nav-bg);
      border-bottom:1px solid var(--nav-bd);box-shadow:0 1px 8px rgba(0,0,0,.07);
      transition:background .3s,border-color .3s}
    .nav-inner{max-width:1200px;margin:0 auto;padding:0 24px;height:60px;
      display:flex;align-items:center;justify-content:space-between}
    .nav-brand{display:flex;align-items:center;gap:10px;font-size:1.05rem;
      font-weight:700;color:var(--text);text-decoration:none}
    .brand-icon{width:34px;height:34px;border-radius:9px;
      background:linear-gradient(135deg,var(--accent),var(--accent2));
      display:flex;align-items:center;justify-content:center;font-size:1rem;color:#fff}
    .nav-links{display:flex;align-items:center;gap:6px}
    .nav-link{padding:6px 14px;border-radius:8px;font-size:.85rem;font-weight:500;
      color:var(--muted);text-decoration:none;border:none;background:none;
      cursor:pointer;transition:background .2s,color .2s}
    .nav-link:hover{background:var(--surface);color:var(--text)}
    .nav-link.active{background:var(--surface-b);color:var(--accent);font-weight:600}
    .theme-btn{width:36px;height:36px;border-radius:50%;background:var(--surface);
      border:1.5px solid var(--border);cursor:pointer;font-size:1rem;
      display:flex;align-items:center;justify-content:center;color:var(--muted);
      transition:all .2s;margin-left:8px}
    .theme-btn:hover{border-color:var(--accent);color:var(--accent);transform:rotate(20deg)}

    /* ── Hero ── */
    .hero{background:linear-gradient(135deg,var(--accent) 0%,var(--accent2) 100%);
      padding:52px 24px 56px;text-align:center;color:#fff}
    .hero h1{font-size:2.2rem;font-weight:800;letter-spacing:-.03em;margin-bottom:10px}
    .hero p{font-size:1rem;opacity:.88;max-width:540px;margin:0 auto}
    .hero-chips{display:flex;gap:8px;justify-content:center;margin-top:18px;flex-wrap:wrap}
    .chip{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.3);
      border-radius:99px;padding:4px 14px;font-size:.78rem;font-weight:600}

    /* ── Layout ── */
    .page-wrap{max-width:1200px;margin:0 auto;padding:36px 24px 56px;
      display:grid;grid-template-columns:1fr 340px;gap:28px;flex:1}
    @media(max-width:900px){.page-wrap{grid-template-columns:1fr}.sidebar{order:-1}}

    /* ── Cards ── */
    .card{background:var(--card-bg);border:1px solid var(--border);border-radius:18px;
      overflow:hidden;box-shadow:0 2px 14px rgba(0,0,0,.06);
      transition:background .3s,border-color .3s;margin-bottom:24px}
    .card:last-child{margin-bottom:0}
    .card-head{padding:16px 22px;border-bottom:1px solid var(--divider);
      display:flex;align-items:center;gap:12px}
    .card-icon{width:34px;height:34px;border-radius:9px;flex-shrink:0;
      background:linear-gradient(135deg,var(--accent),var(--accent2));
      display:flex;align-items:center;justify-content:center;font-size:.95rem;color:#fff}
    .card-head h3{font-size:.95rem;font-weight:700;color:var(--text)}
    .card-head p{font-size:.77rem;color:var(--muted);margin-top:1px}
    .card-body{padding:22px}

    /* ── Input ── */
    .lbl{display:block;font-size:.73rem;font-weight:700;color:var(--muted);
      text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px}
    .input-wrap{display:flex;align-items:center;border:2px solid var(--border);
      border-radius:12px;overflow:hidden;background:var(--input-bg);
      transition:border-color .2s,box-shadow .2s}
    .input-wrap:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px rgba(102,126,234,.15)}
    .input-wrap input{flex:1;border:none;outline:none;padding:14px 16px;font-size:1rem;
      color:var(--text);background:transparent;letter-spacing:.04em}
    .input-wrap input::placeholder{color:var(--muted)}
    .eye-btn{background:none;border:none;cursor:pointer;padding:0 14px;
      color:var(--muted);font-size:1.2rem;transition:color .2s}
    .eye-btn:hover{color:var(--accent)}

    /* ── Buttons row ── */
    .btn-row{display:flex;gap:8px;margin-top:12px}
    .btn-gen{flex:1;padding:11px 16px;border-radius:11px;
      border:1.5px solid #bfdbfe;background:#eff6ff;
      color:#1d4ed8;font-size:.85rem;font-weight:700;cursor:pointer;
      transition:all .2s;display:flex;align-items:center;justify-content:center;gap:6px}
    .btn-gen:hover{background:#dbeafe;border-color:#93c5fd}
    [data-theme="dark"] .btn-gen{background:#1e3a5f;border-color:#3b82f6;color:#93c5fd}
    [data-theme="dark"] .btn-gen:hover{background:#1e4080}
    .btn-copy{padding:11px 18px;border-radius:11px;border:1.5px solid var(--border);
      background:var(--surface);color:var(--muted);font-size:.85rem;font-weight:700;
      cursor:pointer;transition:all .2s;white-space:nowrap}
    .btn-copy:hover{border-color:var(--accent);color:var(--accent)}
    .btn-copy.ok{border-color:#22c55e;color:#22c55e;background:#f0fdf4}

    /* ── Strength meter ── */
    .meter-wrap{margin-top:22px}
    .meter-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
    .meter-ttl{font-size:.73rem;font-weight:700;color:var(--muted);
      text-transform:uppercase;letter-spacing:.07em}
    .strength-badge{font-size:.78rem;font-weight:800;padding:3px 13px;
      border-radius:99px;transition:all .3s}
    .s-none  {background:#f3f4f6;color:#9ca3af}
    .s-weak  {background:#fee2e2;color:#dc2626}
    .s-fair  {background:#ffedd5;color:#ea580c}
    .s-good  {background:#fef9c3;color:#ca8a04}
    .s-strong{background:#dcfce7;color:#16a34a}
    [data-theme="dark"] .s-none  {background:#1e293b;color:#64748b}
    [data-theme="dark"] .s-weak  {background:#450a0a;color:#f87171}
    [data-theme="dark"] .s-fair  {background:#431407;color:#fb923c}
    [data-theme="dark"] .s-good  {background:#422006;color:#facc15}
    [data-theme="dark"] .s-strong{background:#052e16;color:#4ade80}
    .meter-track{height:14px;background:var(--surface-b);border-radius:99px;overflow:hidden}
    .meter-fill{height:100%;width:0%;border-radius:99px;transition:width .5s cubic-bezier(.4,0,.2,1),background .4s}
    .f-weak  {background:linear-gradient(90deg,#ef4444,#f87171)}
    .f-fair  {background:linear-gradient(90deg,#f97316,#fb923c)}
    .f-good  {background:linear-gradient(90deg,#eab308,#facc15)}
    .f-strong{background:linear-gradient(90deg,#22c55e,#4ade80)}
    .entropy-txt{font-size:.75rem;color:var(--muted);margin-top:7px}
    .entropy-txt strong{color:var(--text)}

    /* ── Improvement tip ── */
    .improve-tip{display:none;align-items:center;gap:10px;margin-top:14px;
      padding:10px 14px;background:#eff6ff;border:1.5px solid #bfdbfe;
      border-radius:11px;font-size:.82rem;color:#1d4ed8;animation:pop .3s ease}
    .improve-tip.show{display:flex}
    [data-theme="dark"] .improve-tip{background:#1e3a5f;border-color:#3b82f6;color:#93c5fd}

    /* ── Stats ── */
    .stats-row{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:18px}
    .stat-box{background:var(--surface);border:1.5px solid var(--surface-b);
      border-radius:13px;padding:14px 12px;text-align:center;
      transition:background .3s,border-color .3s,transform .2s}
    .stat-box:hover{transform:translateY(-2px);border-color:var(--accent)}
    .stat-val{font-size:1.4rem;font-weight:800;color:var(--text)}
    .stat-lbl{font-size:.67rem;color:var(--muted);text-transform:uppercase;
      letter-spacing:.06em;margin-top:2px}

    /* ── Divider ── */
    .divider{height:1px;background:var(--divider);margin:20px 0}

    /* ── Rules grid ── */
    .rules-hdr{font-size:.73rem;font-weight:700;color:var(--muted);
      text-transform:uppercase;letter-spacing:.07em;margin-bottom:12px}
    .rules-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
    .rule-item{display:flex;align-items:center;gap:9px;padding:11px 13px;
      border-radius:11px;font-size:.83rem;font-weight:500;
      background:var(--surface);border:1.5px solid var(--surface-b);
      color:var(--muted);transition:all .25s}
    .rule-item.pass{background:#f0fdf4;border-color:#bbf7d0;color:#15803d}
    .rule-item.fail{background:#fff1f2;border-color:#fecdd3;color:#be123c}
    [data-theme="dark"] .rule-item.pass{background:#052e16;border-color:#166534;color:#4ade80}
    [data-theme="dark"] .rule-item.fail{background:#450a0a;border-color:#991b1b;color:#f87171}
    [data-theme="dark"] .rule-item{background:var(--surface);border-color:var(--surface-b);color:var(--muted)}
    .rule-ico{width:22px;height:22px;border-radius:50%;display:flex;
      align-items:center;justify-content:center;font-size:.7rem;
      font-weight:800;flex-shrink:0;transition:all .25s}
    .rule-item.pass .rule-ico{background:#22c55e;color:#fff}
    .rule-item.fail .rule-ico{background:#fecdd3;color:#be123c}
    [data-theme="dark"] .rule-item.fail .rule-ico{background:#991b1b;color:#fca5a5}

    /* ── Warning banner ── */
    .warn-banner{display:none;align-items:flex-start;gap:10px;
      background:#fffbeb;border:1.5px solid #fcd34d;border-radius:12px;
      padding:12px 16px;margin-top:16px;font-size:.83rem;color:#92400e;
      animation:slideIn .3s ease}
    .warn-banner.show{display:flex}
    [data-theme="dark"] .warn-banner{background:#422006;border-color:#d97706;color:#fde68a}

    /* ── Sidebar legend ── */
    .legend{display:flex;flex-direction:column;gap:10px}
    .legend-row{display:flex;align-items:center;gap:12px}
    .legend-bar{height:9px;width:52px;border-radius:99px;flex-shrink:0}
    .lb-weak  {background:linear-gradient(90deg,#ef4444,#f87171)}
    .lb-fair  {background:linear-gradient(90deg,#f97316,#fb923c)}
    .lb-good  {background:linear-gradient(90deg,#eab308,#facc15)}
    .lb-strong{background:linear-gradient(90deg,#22c55e,#4ade80)}
    .legend-name{font-size:.8rem;font-weight:700;width:52px}
    .legend-desc{font-size:.76rem;color:var(--muted)}

    /* ── Tips ── */
    .tip-item{display:flex;gap:12px;padding:13px;
      background:var(--tip-bg);border:1px solid var(--tip-bd);
      border-radius:11px;margin-bottom:10px;
      transition:background .3s,border-color .3s,transform .2s}
    .tip-item:last-child{margin-bottom:0}
    .tip-item:hover{transform:translateX(4px)}
    .tip-icon{font-size:1.2rem;flex-shrink:0;margin-top:2px}
    .tip-ttl{font-size:.83rem;font-weight:700;color:var(--text)}
    .tip-dsc{font-size:.77rem;color:var(--muted);margin-top:2px;line-height:1.5}

    /* ── Footer ── */
    footer{background:var(--footer-bg);border-top:1px solid var(--nav-bd);
      padding:28px 24px;text-align:center;transition:background .3s}
    .foot-inner{max-width:1200px;margin:0 auto}
    .foot-brand{font-size:.9rem;font-weight:700;color:#fff;margin-bottom:6px}
    .foot-desc{font-size:.78rem;color:var(--footer-txt);line-height:1.6}
    .foot-links{display:flex;gap:20px;justify-content:center;margin-top:14px;flex-wrap:wrap}
    .foot-link{font-size:.78rem;color:var(--footer-txt);text-decoration:none;transition:color .2s}
    .foot-link:hover{color:var(--accent)}
    .foot-copy{font-size:.72rem;color:var(--footer-txt);margin-top:12px;opacity:.7}

    /* ── Toast ── */
    .toast{position:fixed;bottom:28px;left:50%;
      transform:translateX(-50%) translateY(60px);
      background:#1f2937;color:#fff;padding:10px 22px;border-radius:99px;
      font-size:.82rem;font-weight:600;opacity:0;pointer-events:none;
      z-index:9999;transition:opacity .25s,transform .25s;
      display:flex;align-items:center;gap:8px}
    .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

    @keyframes slideIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
    @keyframes pop{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
  </style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar">
  <div class="nav-inner">
    <a class="nav-brand" href="#">
      <span class="brand-icon">&#128274;</span>PassCheck
    </a>
    <div class="nav-links">
      <a class="nav-link active" href="#">Checker</a>
      <a class="nav-link" href="#tips-card">Tips</a>
      <button class="theme-btn" id="themeBtn" title="Toggle dark/light">&#9790;</button>
    </div>
  </div>
</nav>

<!-- Hero -->
<div class="hero">
  <h1>&#128274; Password Strength Checker</h1>
  <p>Analyse your password instantly &mdash; entropy score, live rule checklist, breach detection, and a built-in strong-password generator.</p>
  <div class="hero-chips">
    <span class="chip">&#9889; Real-time</span>
    <span class="chip">&#128272; Entropy scoring</span>
    <span class="chip">&#9881; Generator</span>
    <span class="chip">&#127759; 100% client-side</span>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"><span id="toastIcon"></span><span id="toastMsg"></span></div>

<!-- Main -->
<div class="page-wrap">
  <div class="main-col">

    <!-- Input card -->
    <div class="card">
      <div class="card-head">
        <div class="card-icon">&#9999;</div>
        <div><h3>Enter Your Password</h3><p>Results update on every keystroke &mdash; nothing leaves your browser.</p></div>
      </div>
      <div class="card-body">
        <label class="lbl" for="pwdInput">Password</label>
        <div class="input-wrap">
          <input id="pwdInput" type="password" placeholder="Start typing your password..."
                 autocomplete="off" spellcheck="false"/>
          <button class="eye-btn" id="toggleBtn" type="button" title="Show / hide">&#128065;</button>
        </div>

        <div class="btn-row">
          <button class="btn-gen" id="genBtn" type="button">&#9881; Generate Strong Password</button>
          <button class="btn-copy" id="copyBtn" type="button">&#128203; Copy</button>
        </div>

        <!-- Strength meter -->
        <div class="meter-wrap">
          <div class="meter-top">
            <span class="meter-ttl">Password Strength</span>
            <span class="strength-badge s-none" id="strengthBadge">None</span>
          </div>
          <div class="meter-track"><div class="meter-fill" id="meterFill"></div></div>
          <p class="entropy-txt" id="entropyTxt">Enter a password to see entropy score.</p>
        </div>

        <!-- Next-step improvement tip -->
        <div class="improve-tip" id="improveTip">
          <span style="font-size:1.1rem;flex-shrink:0">&#128161;</span>
          <span id="improveTipTxt"></span>
        </div>

        <!-- Stats -->
        <div class="stats-row">
          <div class="stat-box"><div class="stat-val" id="sLen">0</div><div class="stat-lbl">Characters</div></div>
          <div class="stat-box"><div class="stat-val" id="sEnt">0</div><div class="stat-lbl">Entropy (bits)</div></div>
          <div class="stat-box"><div class="stat-val" id="sRules">0/5</div><div class="stat-lbl">Rules passed</div></div>
        </div>
      </div>
    </div>

    <!-- Requirements card -->
    <div class="card">
      <div class="card-head">
        <div class="card-icon">&#9989;</div>
        <div><h3>Requirements</h3><p>Each rule card turns green as you meet it.</p></div>
      </div>
      <div class="card-body">
        <div class="rules-hdr">Checklist</div>
        <div class="rules-grid">
          <div class="rule-item" id="rule-length"><span class="rule-ico">&#10005;</span><span>8+ characters</span></div>
          <div class="rule-item" id="rule-upper"> <span class="rule-ico">&#10005;</span><span>Uppercase (A-Z)</span></div>
          <div class="rule-item" id="rule-lower"> <span class="rule-ico">&#10005;</span><span>Lowercase (a-z)</span></div>
          <div class="rule-item" id="rule-number"><span class="rule-ico">&#10005;</span><span>Number (0-9)</span></div>
          <div class="rule-item" id="rule-symbol"><span class="rule-ico">&#10005;</span><span>Special symbol</span></div>
        </div>
        <div class="warn-banner" id="warnBanner">
          <span style="font-size:1rem;flex-shrink:0">&#9888;&#65039;</span>
          <span><strong>Common password detected.</strong> This appears on widely-known breach lists. Please choose something more unique.</span>
        </div>
      </div>
    </div>

  </div><!-- /main-col -->

  <!-- Sidebar -->
  <div class="sidebar">

    <!-- Strength scale -->
    <div class="card">
      <div class="card-head">
        <div class="card-icon">&#128200;</div>
        <div><h3>Strength Scale</h3><p>Based on entropy in bits.</p></div>
      </div>
      <div class="card-body">
        <div class="legend">
          <div class="legend-row"><div class="legend-bar lb-weak"></div><span class="legend-name" style="color:#dc2626">Weak</span><span class="legend-desc">Below 28 bits &mdash; easily cracked.</span></div>
          <div class="legend-row"><div class="legend-bar lb-fair"></div><span class="legend-name" style="color:#ea580c">Fair</span><span class="legend-desc">28&ndash;35 bits &mdash; needs more variety.</span></div>
          <div class="legend-row"><div class="legend-bar lb-good"></div><span class="legend-name" style="color:#ca8a04">Good</span><span class="legend-desc">36&ndash;59 bits &mdash; decent protection.</span></div>
          <div class="legend-row"><div class="legend-bar lb-strong"></div><span class="legend-name" style="color:#16a34a">Strong</span><span class="legend-desc">60+ bits &mdash; very hard to crack.</span></div>
        </div>
      </div>
    </div>

    <!-- Tips -->
    <div class="card" id="tips-card">
      <div class="card-head">
        <div class="card-icon">&#128161;</div>
        <div><h3>Security Tips</h3><p>Best practices to stay safe.</p></div>
      </div>
      <div class="card-body">
        <div class="tip-item"><span class="tip-icon">&#128272;</span><div><div class="tip-ttl">Use a passphrase</div><div class="tip-dsc">Four random words like <em>correct-horse-battery-staple</em> are strong and memorable.</div></div></div>
        <div class="tip-item"><span class="tip-icon">&#128260;</span><div><div class="tip-ttl">Never reuse passwords</div><div class="tip-dsc">One breach exposes every site that shares the same password.</div></div></div>
        <div class="tip-item"><span class="tip-icon">&#128241;</span><div><div class="tip-ttl">Enable 2FA everywhere</div><div class="tip-dsc">Two-factor auth blocks 99% of automated attacks, even if your password leaks.</div></div></div>
        <div class="tip-item"><span class="tip-icon">&#128196;</span><div><div class="tip-ttl">Use a password manager</div><div class="tip-dsc">Tools like Bitwarden or 1Password create and store a unique password for every site.</div></div></div>
      </div>
    </div>

  </div><!-- /sidebar -->
</div><!-- /page-wrap -->

<!-- Footer -->
<footer>
  <div class="foot-inner">
    <div class="foot-brand">&#128274; PassCheck</div>
    <div class="foot-desc">A privacy-first password strength checker.<br>No data is collected, stored, or transmitted &mdash; everything runs in your browser.</div>
    <div class="foot-links">
      <a class="foot-link" href="#">Checker</a>
      <a class="foot-link" href="#tips-card">Security Tips</a>
    </div>
    <div class="foot-copy">Built with Flask &amp; Vanilla JS</div>
  </div>
</footer>

<script>
  const COMMON = new Set([
    "password","123456","12345678","password123","qwerty","abc123",
    "letmein","admin","welcome","monkey","1234567890","iloveyou",
    "sunshine","princess","dragon","master","pass","hello","shadow","superman"
  ]);
  const LOWER="abcdefghijklmnopqrstuvwxyz", UPPER="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const DIGITS="0123456789", SYMBOLS="!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~";

  const pwdInput   = document.getElementById("pwdInput");
  const toggleBtn  = document.getElementById("toggleBtn");
  const genBtn     = document.getElementById("genBtn");
  const copyBtn    = document.getElementById("copyBtn");
  const themeBtn   = document.getElementById("themeBtn");
  const meterFill  = document.getElementById("meterFill");
  const badge      = document.getElementById("strengthBadge");
  const entropyTxt = document.getElementById("entropyTxt");
  const warnBanner = document.getElementById("warnBanner");
  const sLen       = document.getElementById("sLen");
  const sEnt       = document.getElementById("sEnt");
  const sRules     = document.getElementById("sRules");
  const improveTip = document.getElementById("improveTip");
  const improveTxt = document.getElementById("improveTipTxt");
  const toast      = document.getElementById("toast");
  const toastIcon  = document.getElementById("toastIcon");
  const toastMsg   = document.getElementById("toastMsg");

  const RULES = [
    {id:"rule-length", test:p=>p.length>=8,     tip:"Add more characters to reach 8+"},
    {id:"rule-upper",  test:p=>/[A-Z]/.test(p), tip:"Add an uppercase letter (A-Z)"},
    {id:"rule-lower",  test:p=>/[a-z]/.test(p), tip:"Add a lowercase letter (a-z)"},
    {id:"rule-number", test:p=>/\d/.test(p),     tip:"Add a number (0-9)"},
    {id:"rule-symbol", test:p=>/[!@#$%^&*()\-_=+\[\]{};:'",.<>/?\\|`~]/.test(p), tip:"Add a special symbol like !@#$"},
  ];

  /* Theme */
  function applyTheme(t){
    document.documentElement.setAttribute("data-theme",t);
    themeBtn.innerHTML = t==="dark"?"&#9728;":"&#9790;";
    localStorage.setItem("pwdTheme",t);
  }
  applyTheme(localStorage.getItem("pwdTheme")||"light");
  themeBtn.addEventListener("click",()=>{
    applyTheme(document.documentElement.getAttribute("data-theme")==="dark"?"light":"dark");
  });

  /* Show/hide */
  toggleBtn.addEventListener("click",()=>{
    const h=pwdInput.type==="password";
    pwdInput.type=h?"text":"password";
    toggleBtn.innerHTML=h?"&#128064;":"&#128065;";
  });

  /* Toast */
  let toastT;
  function showToast(icon,msg){
    clearTimeout(toastT);
    toastIcon.textContent=icon; toastMsg.textContent=msg;
    toast.classList.add("show");
    toastT=setTimeout(()=>toast.classList.remove("show"),2400);
  }

  /* Copy */
  function copyText(t){ navigator.clipboard.writeText(t).then(()=>showToast("&#128203;","Copied to clipboard!")); }
  copyBtn.addEventListener("click",()=>{
    if(!pwdInput.value) return;
    copyText(pwdInput.value);
    copyBtn.textContent="Copied!"; copyBtn.classList.add("ok");
    setTimeout(()=>{ copyBtn.innerHTML="&#128203; Copy"; copyBtn.classList.remove("ok"); },2000);
  });

  /* Generator */
  function generatePassword(){
    const all=LOWER+UPPER+DIGITS+SYMBOLS;
    let p=LOWER[Math.floor(Math.random()*LOWER.length)]
         +UPPER[Math.floor(Math.random()*UPPER.length)]
         +DIGITS[Math.floor(Math.random()*DIGITS.length)]
         +SYMBOLS[Math.floor(Math.random()*SYMBOLS.length)];
    for(let i=4;i<16;i++) p+=all[Math.floor(Math.random()*all.length)];
    return p.split("").sort(()=>Math.random()-.5).join("");
  }
  genBtn.addEventListener("click",()=>{
    const pwd=generatePassword();
    pwdInput.value=pwd; pwdInput.type="text"; toggleBtn.innerHTML="&#128064;";
    update(); showToast("&#9881;","Strong password generated!");
  });

  /* Entropy */
  function calcEntropy(p){
    if(!p) return 0;
    let pool=0;
    if(/[a-z]/.test(p)) pool+=26;
    if(/[A-Z]/.test(p)) pool+=26;
    if(/\d/.test(p))    pool+=10;
    if(/[!@#$%^&*()\-_=+\[\]{};:'",.<>/?\\|`~]/.test(p)) pool+=32;
    return p.length*Math.log2(pool||26);
  }

  function getScore(e){
    if(e===0) return {label:"None",  pct:0,  cls:"s-none",  fill:""};
    if(e<28)  return {label:"Weak",  pct:25, cls:"s-weak",  fill:"f-weak"};
    if(e<36)  return {label:"Fair",  pct:50, cls:"s-fair",  fill:"f-fair"};
    if(e<60)  return {label:"Good",  pct:75, cls:"s-good",  fill:"f-good"};
    return           {label:"Strong",pct:100,cls:"s-strong",fill:"f-strong"};
  }

  /* Main update */
  function update(){
    const p=pwdInput.value;
    let passed=0, firstFail=null;

    RULES.forEach(({id,test,tip})=>{
      const ok=test(p);
      const el=document.getElementById(id);
      const ico=el.querySelector(".rule-ico");
      el.classList.toggle("pass",ok);
      el.classList.toggle("fail",!ok&&p.length>0);
      ico.innerHTML=ok?"&#10003;":"&#10005;";
      if(ok) passed++;
      else if(!firstFail) firstFail=tip;
    });

    const entropy=calcEntropy(p), score=getScore(entropy);

    meterFill.style.width=score.pct+"%";
    meterFill.className="meter-fill "+(score.fill||"");
    badge.textContent=score.label;
    badge.className="strength-badge "+score.cls;

    entropyTxt.innerHTML=p
      ?`Estimated entropy: <strong>${entropy.toFixed(1)} bits</strong>`
      :"Enter a password to see entropy score.";

    sLen.textContent=p.length;
    sEnt.textContent=entropy.toFixed(1);
    sRules.textContent=passed+"/5";

    /* Improvement tip */
    if(p && firstFail && score.label!=="Strong"){
      improveTxt.textContent=firstFail;
      improveTip.classList.add("show");
    } else {
      improveTip.classList.remove("show");
    }

    warnBanner.classList.toggle("show",!!(p&&COMMON.has(p.toLowerCase())));
  }

  pwdInput.addEventListener("input",update);
  update();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/check", methods=["POST"])
def api_check():
    data     = request.get_json(silent=True) or {}
    password = data.get("password", "")
    rules    = evaluate_rules(password)
    entropy  = calc_entropy(password)
    score    = score_password(entropy)
    return jsonify(
        rules=rules, entropy=round(entropy,2), score=score,
        is_common=password.lower() in COMMON_PASSWORDS,
    )

if __name__ == "__main__":
    app.run(debug=True)
