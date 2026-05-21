#!/usr/bin/env python3
"""
Skill: Fetch Quiz Scores → CSV → Email to SAP

Usage:
  python3 scripts/fetch-quiz-scores.py

Workflow:
  1. Reads FormSubmit emails from subhankar@agentmail.to inbox
  2. Extracts name, score, correct, accuracy, time, quiz
  3. Generates CSV matching dashboard template
  4. Emails CSV to subhankar.pattanayak@sap.com

CSV Format: Name,Score,Correct,Accuracy,Time,Quiz
Dashboard-ready for upload at:
  https://subhankarpattanayak42-blip.github.io/coltie-grow-curriculum/dashboard/
"""

import os, json, re, base64
from datetime import datetime

# ── Config ──
AGENTMAIL_KEY = "am_us_inbox_53b2de3faeddf0868ab12536ae99f9fc73c50668be430119c36008f40e487458"
FROM_INBOX = "subhankar@agentmail.to"
TO_EMAIL = "subhankar.pattanayak@sap.com"
CSV_COLUMNS = ["Name", "Score", "Correct", "Accuracy", "Time", "Quiz"]

os.environ["AGENTMAIL_API_KEY"] = AGENTMAIL_KEY
from agentmail import AgentMail
client = AgentMail()


def parse_formsubmit_email(full_msg):
    """Extract fields from FormSubmit HTML email."""
    html = full_msg.html or ""
    data = {}
    
    patterns = {
        'name': r'<strong>name:\s*</strong>\s*<br\s*/?>\s*<pre[^>]*>\s*(.*?)\s*</pre>',
        'score': r'<strong>score:\s*</strong>\s*<br\s*/?>\s*<pre[^>]*>\s*(.*?)\s*</pre>',
        'correct': r'<strong>correct:\s*</strong>\s*<br\s*/?>\s*<pre[^>]*>\s*(.*?)\s*</pre>',
        'wrong': r'<strong>wrong:\s*</strong>\s*<br\s*/?>\s*<pre[^>]*>\s*(.*?)\s*</pre>',
        'accuracy': r'<strong>accuracy:\s*</strong>\s*<br\s*/?>\s*<pre[^>]*>\s*(.*?)\s*</pre>',
        'time_taken': r'<strong>time_taken:\s*</strong>\s*<br\s*/?>\s*<pre[^>]*>\s*(.*?)\s*</pre>',
        'quiz': r'<strong>quiz:\s*</strong>\s*<br\s*/?>\s*<pre[^>]*>\s*(.*?)\s*</pre>',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, html, re.DOTALL)
        if match:
            data[key] = match.group(1).strip()
    
    return data


def fetch_scores():
    """
    Fetch all quiz scores from AgentMail inbox.
    Returns list of dicts with keys matching CSV columns.
    """
    inbox = client.inboxes.messages.list(
        inbox_id=FROM_INBOX,
        limit=50
    )
    
    scores = []
    seen = set()
    
    for msg in inbox.messages:
        sender = str(msg.from_ or "")
        if 'formsubmit' not in sender.lower():
            continue
        
        try:
            full = client.inboxes.messages.get(
                inbox_id=FROM_INBOX,
                message_id=msg.message_id
            )
        except Exception as e:
            print(f"  ⚠️  Could not fetch message: {e}")
            continue
        
        data = parse_formsubmit_email(full)
        if not data.get('name'):
            continue
        
        # Deduplicate
        dedup_key = f"{data.get('name','')}_{data.get('score','')}_{data.get('quiz','')}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        
        # Calculate accuracy
        accuracy = data.get('accuracy', '?')
        if accuracy == '?' and data.get('correct') and data.get('wrong'):
            try:
                c = int(data['correct'])
                w = int(data['wrong'])
                if c + w > 0:
                    accuracy = f"{round(c/(c+w)*100)}%"
            except:
                pass
        
        # Build row
        row = {
            'Name': data.get('name', 'Unknown'),
            'Score': int(data.get('score', 0)),
            'Correct': data.get('correct', '?'),
            'Accuracy': accuracy,
            'Time': data.get('time_taken', '?'),
            'Quiz': data.get('quiz', 'Email Submission')
        }
        scores.append(row)
        print(f"  → {row['Name']}: {row['Score']} pts ({row['Quiz']})")
    
    return scores


def scores_to_csv(scores):
    """Convert scores list to CSV string matching dashboard template."""
    lines = [",".join(CSV_COLUMNS)]
    for s in scores:
        row = [
            s['Name'],
            str(s['Score']),
            str(s['Correct']),
            s['Accuracy'],
            s['Time'],
            s['Quiz']
        ]
        # Escape commas inside fields
        escaped = [f'"{v}"' if ',' in str(v) else str(v) for v in row]
        lines.append(",".join(escaped))
    return "\n".join(lines) + "\n"


def send_csv_email(csv_content, score_count):
    """Email the CSV to SAP inbox via AgentMail."""
    csv_b64 = base64.b64encode(csv_content.encode()).decode()
    
    timestamp = datetime.now().strftime("%b %d, %Y at %H:%M IST")
    subject = f"📊 COLTIE GROW Quiz Scores — {score_count} entries ({datetime.now().strftime('%d %b')})"
    
    text = f"""COLTIE GROW Quiz Scores — {timestamp}

Total Entries: {score_count}

Upload this CSV to the dashboard:
https://subhankarpattanayak42-blip.github.io/coltie-grow-curriculum/dashboard/

→ Go to Manual Entry tab
→ Click "Upload CSV"
→ Select this file

Format: Name, Score, Correct, Accuracy, Time, Quiz
"""

    result = client.inboxes.messages.send(
        inbox_id=FROM_INBOX,
        to=TO_EMAIL,
        subject=subject,
        text=text,
        attachments=[{
            "filename": "coltie-grow-quiz-scores.csv",
            "content": csv_b64
        }]
    )
    
    return result


def main():
    print(f"\n{'='*60}")
    print(f"  COLTIE GROW — Fetch Quiz Scores & Email")
    print(f"{'='*60}")
    print(f"  Inbox:  {FROM_INBOX}")
    print(f"  Send to: {TO_EMAIL}")
    print(f"  Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Step 1: Fetch scores
    print("📧 Fetching scores from AgentMail inbox...")
    scores = fetch_scores()
    
    if not scores:
        print("\n⚠️  No FormSubmit quiz emails found in inbox.")
        print("   Make sure students have completed the quiz at:")
        print("   https://subhankarpattanayak42-blip.github.io/coltie-grow-curriculum/quizzes/\n")
        return
    
    print(f"\n✅ Found {len(scores)} unique quiz submissions\n")
    
    # Step 2: Generate CSV
    print("📝 Generating CSV...")
    csv_content = scores_to_csv(scores)
    print(f"   CSV: {len(csv_content)} bytes, {len(scores)+1} lines (header + data)")
    print(f"\n   Preview:")
    for line in csv_content.strip().split("\n")[:4]:
        print(f"     {line}")
    if len(scores) > 3:
        print(f"     ... ({len(scores)-3} more)")
    
    # Step 3: Email
    print(f"\n📧 Emailing to {TO_EMAIL}...")
    try:
        result = send_csv_email(csv_content, len(scores))
        print(f"   ✅ Sent! Message ID: {result.message_id}")
    except Exception as e:
        print(f"   ❌ Error sending: {e}")
        return
    
    print(f"\n{'='*60}")
    print(f"  ✅ Done! {len(scores)} scores emailed to {TO_EMAIL}")
    print(f"  📊 Dashboard: https://subhankarpattanayak42-blip.github.io/coltie-grow-curriculum/dashboard/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
