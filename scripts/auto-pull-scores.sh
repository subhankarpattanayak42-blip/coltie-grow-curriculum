#!/bin/bash
cd /tmp/coltie-grow-curriculum
python3 scripts/pull-scores.py
git add -A && git commit -m "auto-sync scores $(date +%H:%M)" && git push
