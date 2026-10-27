# PaidTasks — Account & Data Deletion Page

A small Flask site that satisfies Google Play's "Data deletion" requirement
for apps with accounts. It shows a public page where a user enters their
phone/email and requests deletion; the request is logged to Firebase as
`pending` — it does **not** delete data directly from the browser.

## What it does

- `GET /` — the public page (this is the URL you paste into Play Console's
  Data Safety section as the "Account and data deletion" link).
- `POST /api/delete-request` — validates the identifier, normalizes Kenyan
  phone numbers to `+254...`, and writes a record to:

  ```
  https://aviabustout-default-rtdb.firebaseio.com/paidtasks_deletion_requests/{uuid}.json
  { "identifier": "...", "status": "pending", "requestedAt": <ms>, "source": "web-deletion-form" }
  ```

## Deploy to Render (same as your other backends)

1. Push this folder to a GitHub repo.
2. On Render: New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Under **Environment**, add:
   - `FB_HOST` = `https://aviabustout-default-rtdb.firebaseio.com`
   - `FB_AUTH` = `MqfMzEhe0pU9U7vuKXq4Osw2tgj95IiDDnfaTjnP`
   - `SUPPORT_EMAIL` = your support address (optional, defaults to support@ngelicyber.com)

   **Do not put `FB_AUTH` in the code or commit it to GitHub** — it's your
   database's legacy secret and grants full read/write access. Setting it
   as an environment variable on Render keeps it out of your repo and out
   of the page users see.

6. Once deployed, Render gives you a URL like
   `https://paidtasks-deletion.onrender.com` — that's the link to paste into
   Play Console → App content → Data safety → "Account and data deletion".

## Processing pending requests

This page only *logs* requests — it doesn't wipe data itself, because a
public page shouldn't be able to run destructive deletes with no auth.
Check `/paidtasks_deletion_requests` in your Firebase console periodically
(or write a small script/cron) and for each `pending` entry:

1. Delete the user's node(s) under wherever PaidTasks stores them
   (e.g. `/paidtasks_users/{id}`, `/paidtasks_earnings/{id}`, `/paidtasks_referrals/{id}`).
2. Keep M-Pesa withdrawal/transaction records if you're required to retain
   them for tax purposes — the page already tells users this up front.
3. Mark the request `"status": "done"` so you don't reprocess it.

If you want, I can also write that cleanup script (Python, using the same
Firebase REST calls) so processing is one command instead of manual deletes.

## Local testing

```bash
pip install -r requirements.txt
export FB_HOST="https://aviabustout-default-rtdb.firebaseio.com"
export FB_AUTH="MqfMzEhe0pU9U7vuKXq4Osw2tgj95IiDDnfaTjnP"
python app.py
```

Then open http://localhost:5000
