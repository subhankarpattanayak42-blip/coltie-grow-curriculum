#!/usr/bin/env python3
"""Pull quiz scores from AgentMail inbox and publish as static JSON for the dashboard."""
import os, json, re, base64, subprocess
from datetime import datetime

# ── Config ──
AGENTMAIL_KEY = "am_us_inbox_53b2de3faeddf0868ab12536ae99f9fc73c50668be430119c36008f40e487458"
REPO_DIR = "/tmp/coltie-grow-curriculum"  # or actual path
SCORES_PATH = "docs/dashboard/data/scores.json"

os.environ["AGENTMAIL_API_KEY"] = AGENTMAIL_KEY
from agentmail import AgentMail
client = AgentMail()

def parse_formsubmit_email(full_msg):
    """Extract name, score, correct, wrong, quiz from FormSubmit HTML email."""
    html = full_msg.html or ""
    data = {}
    
    # Extract field values from FormSubmit email format
    # Pattern: <strong>field:</strong><pre>value</pre>
    # FormSubmit format: <strong>name: </strong><pre style="...">value</pre>
    # The label includes the colon
    # FormSubmit format: <strong>name: </strong><br /><pre style="...">value</pre>
    # The label includes the colon, and there's a <br /> between </strong> and <pre>
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

def main():
    print(f"[{datetime.now().isoformat()}] Pulling scores from AgentMail inbox...")
    
    # List inbox messages
    inbox = client.inboxes.messages.list(
        inbox_id="subhankar@agentmail.to",
        limit=50
    )
    
    scores = []
    seen = set()
    
    for msg in inbox.messages:
        sender = str(msg.from_ or "")
        if 'formsubmit' not in sender.lower():
            continue
        
        # Get full message
        try:
            full = client.inboxes.messages.get(
                inbox_id="subhankar@agentmail.to",
                message_id=msg.message_id
            )
        except:
            continue
        
        data = parse_formsubmit_email(full)
        if not data.get('name'):
            continue
        
        # Deduplicate by name+score+quiz combo
        dedup_key = f"{data.get('name','')}_{data.get('score','')}_{data.get('quiz','')}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        
        # Calculate accuracy if not provided
        accuracy = data.get('accuracy', '?')
        if accuracy == '?' and data.get('correct') and data.get('wrong'):
            try:
                c = int(data['correct'])
                w = int(data['wrong'])
                if c + w > 0:
                    accuracy = f"{round(c/(c+w)*100)}%"
            except:
                pass
        
        # Determine correct/total display
        correct_display = data.get('correct', '?')
        
        entry = {
            'n': data.get('name', 'Unknown'),
            's': int(data.get('score', 0)),
            'c': correct_display,
            'a': accuracy,
            't': data.get('time_taken', '?'),
            'q': data.get('quiz', 'Email Submission')
        }
        scores.append(entry)
        print(f"  → {entry['n']}: {entry['s']} pts ({entry['q']})")
    
    # Write scores JSON
    scores_path = os.path.join(REPO_DIR, SCORES_PATH)
    os.makedirs(os.path.dirname(scores_path), exist_ok=True)
    with open(scores_path, 'w') as f:
        json.dump({"scores": scores, "last_updated": datetime.now().isoformat()}, f, indent=2)
    
    print(f"\n✅ {len(scores)} scores written to {SCORES_PATH}")
    print(f"   Total: {len(scores)} entries")

if __name__ == "__main__":
    main()
