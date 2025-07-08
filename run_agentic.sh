#!/bin/bash
# Minimal agentic system status and log viewer

set -e

show_status() {
  echo "==== Repo Runner Status ===="
  if [ -f run_checkpoint.json ]; then
    cat run_checkpoint.json | jq . || cat run_checkpoint.json
  else
    echo "No run_checkpoint.json found. Run the CLI first."
  fi
}

tail_logs() {
  echo "==== Tailing Agent Logs (logs/agent_logs) ===="
  if [ -d logs/agent_logs ]; then
    tail -n 40 logs/agent_logs/*.log
  else
    echo "No agent logs found."
  fi
}

show_model_stats() {
  echo "==== Model Usage Stats ===="
  if [ -f reports/summary_*.json ]; then
    ls -1 reports/summary_*.json | xargs cat | jq . || ls -1 reports/summary_*.json | xargs cat
  else
    echo "No model usage summaries found."
  fi
}

case "$1" in
  status)
    show_status
    ;;
  logs)
    tail_logs
    ;;
  models)
    show_model_stats
    ;;
  *)
    echo "Usage: $0 {status|logs|models}"
    ;;
esac 