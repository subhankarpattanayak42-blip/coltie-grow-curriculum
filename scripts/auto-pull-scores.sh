#!/bin/bash
mkdir -p /tmp/coltie-grow-curriculum/logs
cd /tmp/coltie-grow-curriculum
python3 scripts/pull-scores.py >> /tmp/coltie-grow-curriculum/logs/cron-pull.log 2>&1
# Only commit if there are actual changes
if git status --porcelain | grep -q "docs/dashboard/data/scores.json"; then
  git add docs/dashboard/data/scores.json
  git commit -m "auto-sync scores $(date +%H:%M)" >> /tmp/coltie-grow-curriculum/logs/cron-pull.log 2>&1
  git push origin main >> /tmp/coltie-grow-curriculum/logs/cron-pull.log 2>&1
  echo "Pushed at $(date)" >> /tmp/coltie-grow-curriculum/logs/cron-pull.log
else
  echo "No changes at $(date)" >> /tmp/coltie-grow-curriculum/logs/cron-pull.log
fi
