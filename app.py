
import os
import re
import time
import uuid

import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Firebase configuration: set these in your hosting provider's environment.
FB_HOST = os.environ.get(
    "FB_HOST",
    "https://aviabustout-default-rtdb.firebaseio.com"
)
FB_AUTH = os.environ.get("FB_AUTH", "")

REQUESTS_PATH = "task_earn_deletion_requests"
APP_NAME = "Task & Earn"
SUPPORT_EMAIL = os.environ.get(
    "SUPPORT_EMAIL",
    "support@ngelicyber.com"
)


def identifier_is_valid(identifier: str) -> bool:
    identifier = identifier.strip()
    phone_pattern = re.compile(r"^(?:\+254|0)[17]\d{8}$")
    email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    return bool(
        phone_pattern.fullmatch(identifier)
        or email_pattern.fullmatch(identifier)
    )


def normalize_phone(identifier: str) -> str:
    identifier = identifier.strip()
    if identifier.startswith("0") and len(identifier) == 10:
        return "+254" + identifier[1:]
    return identifier


PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Delete My Account &amp; Data — {{ app_name }}</title>
<style>
  :root {
    --ink: #16241d;
    --ink-soft: #4b5c53;
    --paper: #f6f4ee;
    --card: #ffffff;
    --line: #dcd6c8;
    --accent: #1f7a4d;
    --accent-dark: #14512f;
    --danger: #a8371f;
    --danger-bg: #fbf0ec;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
    line-height: 1.5;
  }
  .wrap {
    max-width: 620px;
    margin: 0 auto;
    padding: 56px 24px 80px;
  }
  header.top {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 40px;
    border-bottom: 1px solid var(--line);
    padding-bottom: 18px;
  }
  .mark {
    font-weight: 700;
    font-size: 19px;
    letter-spacing: 0.01em;
  }
  .mark span { color: var(--accent); }
  header.top .tag {
    font-family: Arial, sans-serif;
    font-size: 12px;
    color: var(--ink-soft);
  }
  h1 {
    font-size: 30px;
    line-height: 1.2;
    margin: 0 0 10px;
    max-width: 22ch;
  }
  p.lede {
    font-family: Arial, sans-serif;
    color: var(--ink-soft);
    font-size: 15px;
    max-width: 46ch;
    margin: 0 0 36px;
  }
  section.block { margin-bottom: 34px; }
  h2 {
    font-family: Arial, sans-serif;
    font-size: 13px;
    font-weight: 600;
    margin: 0 0 12px;
  }
  ul.data-list {
    font-family: Arial, sans-serif;
    font-size: 14.5px;
    color: var(--ink-soft);
    margin: 0;
    padding-left: 0;
    list-style: none;
  }
  ul.data-list li {
    padding: 10px 0;
    border-top: 1px solid var(--line);
    display: flex;
    justify-content: space-between;
    gap: 16px;
  }
  ul.data-list li:last-child { border-bottom: 1px solid var(--line); }
  ul.data-list li .what { color: var(--ink); }
  ul.data-list li .retain {
    color: var(--ink-soft);
    font-size: 13px;
  }
  form.card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 28px;
    font-family: Arial, sans-serif;
  }
  label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 6px;
  }
  input[type=text] {
    width: 100%;
    padding: 12px 14px;
    border: 1px solid var(--line);
    border-radius: 3px;
    font-size: 15px;
    font-family: inherit;
    margin-bottom: 18px;
    background: #fcfbf8;
  }
  input[type=text]:focus {
    outline: 2px solid var(--accent);
    outline-offset: 1px;
  }
  .confirm-row {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin-bottom: 22px;
    font-size: 13.5px;
    color: var(--ink-soft);
  }
  .confirm-row input { margin-top: 3px; }
  button.submit {
    width: 100%;
    padding: 14px 18px;
    background: var(--danger);
    color: #fff;
    border: none;
    border-radius: 3px;
    font-size: 15px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
  }
  button.submit:hover { background: #8a2c18; }
  button.submit:disabled {
    background: #c9a89f;
    cursor: not-allowed;
  }
  #msg {
    margin-top: 16px;
    font-size: 14px;
    padding: 12px 14px;
    border-radius: 3px;
    display: none;
  }
  #msg.ok {
    display: block;
    background: #eaf4ee;
    color: var(--accent-dark);
    border: 1px solid #bfe0cc;
  }
  #msg.err {
    display: block;
    background: var(--danger-bg);
    color: var(--danger);
    border: 1px solid #eecbc0;
  }
  footer {
    margin-top: 48px;
    font-family: Arial, sans-serif;
    font-size: 12.5px;
    color: var(--ink-soft);
  }
  footer a { color: var(--accent-dark); }
  @media (max-width: 480px) {
    .wrap { padding: 32px 18px 56px; }
    header.top { flex-wrap: wrap; }
    form.card { padding: 20px; }
  }
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="mark"><span>{{ app_name }}</span></div>
    <div class="tag">Account &amp; Data Deletion</div>
  </header>

  <h1>Delete your account and its data</h1>
  <p class="lede">
    Submit a request using the phone number or email registered to your
    {{ app_name }} account. We aim to process valid deletion requests
    within 30 days.
  </p>

  <section class="block">
    <h2>WHAT GETS DELETED</h2>
    <ul class="data-list">
      <li>
        <span class="what">Profile information</span>
        <span class="retain">Deleted</span>
      </li>
      <li>
        <span class="what">Tasks and earnings history</span>
        <span class="retain">Deleted</span>
      </li>
      <li>
        <span class="what">Referral records</span>
        <span class="retain">Deleted</span>
      </li>
      <li>
        <span class="what">Payment and withdrawal records</span>
        <span class="retain">As legally required</span>
      </li>
    </ul>
  </section>

  <form class="card" id="delForm">
    <label for="identifier">
      Phone number or email used on {{ app_name }}
    </label>
    <input
      type="text"
      id="identifier"
      name="identifier"
      placeholder="0712 345 678 or you@example.com"
      autocomplete="email"
      required
    >

    <div class="confirm-row">
      <input type="checkbox" id="confirm" required>
      <label for="confirm" style="font-weight:400; margin:0;">
        I understand that deleting my account is permanent and may remove
        my profile, task history, earnings history, and referral records.
      </label>
    </div>

    <button type="submit" class="submit" id="submitBtn">
      Request account deletion
    </button>
    <div id="msg" role="status" aria-live="polite"></div>
  </form>

  <footer>
    Questions? Contact
    <a href="mailto:{{ support_email }}">{{ support_email }}</a>.
    Certain records may be retained where legally required or necessary
    to resolve outstanding transactions.
  </footer>
</div>

<script>
const form = document.getElementById('delForm');
const msg = document.getElementById('msg');
const btn = document.getElementById('submitBtn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const identifier = document.getElementById('identifier').value.trim();

  msg.className = '';
  msg.style.display = 'none';
  btn.disabled = true;
  btn.textContent = 'Submitting…';

  try {
    const res = await fetch('/api/delete-request', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({identifier})
    });

    const data = await res.json();

    if (res.ok) {
      msg.textContent = data.message;
      msg.className = 'ok';
      form.reset();
      btn.textContent = 'Request submitted';
    } else {
      msg.textContent = data.error || 'Something went wrong. Please try again.';
      msg.className = 'err';
      btn.disabled = false;
      btn.textContent = 'Request account deletion';
    }
  } catch (err) {
    msg.textContent = 'Network error. Please try again.';
    msg.className = 'err';
    btn.disabled = false;
    btn.textContent = 'Request account deletion';
  }
});
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(
        PAGE_TEMPLATE,
        app_name=APP_NAME,
        support_email=SUPPORT_EMAIL
    )


@app.route("/api/delete-request", methods=["POST"])
def delete_request():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or "").strip()

    if not identifier or not identifier_is_valid(identifier):
        return jsonify({
            "error": "Enter a valid Kenyan phone number or email address."
        }), 400

    if not FB_AUTH:
        app.logger.error("Firebase authentication is not configured.")
        return jsonify({
            "error": "Service temporarily unavailable. Please contact support."
        }), 500

    identifier_norm = normalize_phone(identifier)
    request_id = str(uuid.uuid4())

    payload = {
        "identifier": identifier_norm,
        "appName": APP_NAME,
        "status": "pending",
        "requestedAt": int(time.time() * 1000),
        "source": "task-earn-web-deletion-form",
    }

    try:
        resp = requests.put(
            f"{FB_HOST.rstrip('/')}/{REQUESTS_PATH}/{request_id}.json",
            params={"auth": FB_AUTH},
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException:
        app.logger.exception("Failed to save account deletion request.")
        return jsonify({
            "error": "Could not submit your request right now. Please try again shortly."
        }), 502

    return jsonify({
        "message": (
            "Your Task & Earn deletion request has been received. "
            "We aim to process valid requests within 30 days."
        )
    }), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
