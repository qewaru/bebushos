#!/bin/bash
set -e
set -o pipefail

VENV_PATH="/tmp/installer-venv"
INSTALLER_PATH="/root/installer/installer.py"
LOG_FILE="/tmp/installer-log.txt"

echo "[$(date)] Starting the script..." | tee -a "$LOG_FILE"

echo "[$(date)] Waiting for root session..." | tee -a "$LOG_FILE"
while ! loginctl | grep -q "tty1"; do
	echo "[$(date)] Root session is not ready yet..." | tee -a "$LOG_FILE"
	sleep 0.5
done

echo "[$(date)] TTY1 is ready. Preparing the environment" | tee -a "$LOG_FILE"

if [ ! -d "$VENV_PATH" ]; then
	echo "[$(date)] Creating venv..." | tee -a "$LOG_FILE"
	python3 -m venv "$VENV_PATH"
fi

echo "[$(date)] Installing Python packages..." | tee -a "$LOG_FILE"
"$VENV_PATH/bin/pip" install rich questionary Babel

"[$(date)] Everything is ready. Clearing..." | tee -a "$LOG_FILE"
clear

echo "[$(date)] Running installer.py..." >> "$LOG_FILE"
exec "$VENV_PATH/bin/python" "$INSTALLER_PATH" | tee -a "$LOG_FILE"
