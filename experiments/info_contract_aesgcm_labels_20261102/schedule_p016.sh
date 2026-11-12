#!/usr/bin/env bash
# Sequential P016 scheduler.
#
# Waits for the P014 process to exit (so no two cohorts share one AgentRouter
# key concurrently), then runs the two registered labels one at a time. Each
# label writes its own directory; a non-zero exit from one label is logged and
# the next label still runs, because one label failing is a result about that
# label, not a reason to lose the other.
set -u
cd "$(dirname "$0")"
NS="$(pwd)"
LOG="$NS/scheduler.log"
P014_PATTERN="run_p014_aesgcm"

echo "$(date -Is) scheduler start; waiting for P014 to exit" >> "$LOG"

while pgrep -f "$P014_PATTERN" | grep -v "$$" > /dev/null 2>&1; do
  sleep 60
done

echo "$(date -Is) P014 no longer running; starting labels" >> "$LOG"

for LABEL in gpt-6.1-sol gpt-5.6-sol; do
  echo "$(date -Is) label start: $LABEL" >> "$LOG"
  AGENTROUTER_LABEL_MODEL="$LABEL" python3 run_p016_aesgcm.py \
    >> "$NS/label_${LABEL//[^A-Za-z0-9]/_}.log" 2>&1
  rc=$?
  echo "$(date -Is) label done: $LABEL rc=$rc" >> "$LOG"
done

echo "$(date -Is) scheduler finished" >> "$LOG"
