---
name: fetch-quiz-scores
description: >
  Fetch COLTIE GROW student quiz scores from AgentMail inbox, generate a
  CSV file matching the dashboard upload format, and email it to
  subhankar.pattanayak@sap.com.
---

# Fetch Quiz Scores → CSV → Email

## What This Skill Does

1. Reads the `subhankar@agentmail.to` inbox for FormSubmit quiz result emails
2. Extracts: name, score, correct, accuracy, time taken, quiz title
3. Generates a CSV in the exact format required by the COLTIE GROW dashboard
4. Emails the CSV as an attachment to `subhankar.pattanayak@sap.com`

## Triggers

Use this skill when:
- A quiz session has ended and you need the scores
- Students say "I finished the quiz" and you want to collect results
- You want to check who has submitted so far
- Before a session starts, to clear old data

## CSV Format

Matches dashboard upload template:
```
Name,Score,Correct,Accuracy,Time,Quiz
```

## Usage

```bash
# One command — fetch, generate CSV, email
python3 scripts/fetch-quiz-scores.py
```

## Output

- **Email sent to:** subhankar.pattanayak@sap.com
- **Attachment:** coltie-grow-quiz-scores.csv
- **Dashboard for upload:**
  https://subhankarpattanayak42-blip.github.io/coltie-grow-curriculum/dashboard/

## Dashboard Upload Steps

1. Open the dashboard
2. Go to **Manual Entry** tab
3. Click **Upload CSV**
4. Select the emailed CSV file
5. Scores appear in the leaderboard

## Dependencies

- `agentmail` Python SDK
- AGENTMAIL_API_KEY environment variable (set in the script)

## Related Skills

- `scripts/pull-scores.py` — generates JSON for the dashboard data endpoint
- Dashboard: reads `scores.json` for the "Fetch from Email" button
