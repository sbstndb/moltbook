#!/bin/bash
# Daemon qui gère la boucle de Tasks Moltbook

CYCLE=16
AGENT_DIR="$HOME/moltbook"
LOG="$AGENT_DIR/loop.log"

mkdir -p "$AGENT_DIR"

while true; do
    echo "=== Cycle $CYCLE - $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"
    
    # Attendre que la Task courante finisse
    while pgrep -f "a361b15" > /dev/null; do
        sleep 10
    done
    
    echo "Task $CYCLE complete. Sleeping 5 min..." >> "$LOG"
    sleep 300
    
    # Relancer (sera fait par toi en manuel pour l'instant)
    CYCLE=$((CYCLE + 1))
    echo "Ready for cycle $CYCLE" >> "$LOG"
done &
