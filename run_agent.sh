#!/bin/bash
# Infinite loop: Task → 5min sleep → repeat

AGENT_DIR="$HOME/moltbook"
LOG_FILE="$AGENT_DIR/agent_loop.log"

mkdir -p "$AGENT_DIR"
cd "$AGENT_DIR"

echo "🦞 Starting Moltbook agent loop..." | tee -a "$LOG_FILE"
echo "Logs: $LOG_FILE" | tee -a "$LOG_FILE"

CYCLE=0

while true; do
    CYCLE=$((CYCLE + 1))
    echo "" | tee -a "$LOG_FILE"
    echo "=== Cycle $CYCLE - $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a "$LOG_FILE"
    
    # Launch Task via my invocation (this script is called by me)
    # The Task will read CLAUDE.md and explore Moltbook
    echo "Launching agent task..." | tee -a "$LOG_FILE"
    
    # Note: In actual implementation, this would launch a Task
    # For now, we simulate the agent activity
    python3 work/moltbook-agent/moltbook_agent.py
    
    echo "Cycle $CYCLE complete. Waiting 5 minutes..." | tee -a "$LOG_FILE"
    echo "Next cycle: $(date -d '+5 minutes' '+%H:%M:%S')" | tee -a "$LOG_FILE"
    
    sleep 300
done
