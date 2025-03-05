#!/bin/bash

# Check if a command was provided
if [ $# -eq 0 ]; then
  echo "Usage: $0 <command> [arguments...]"
  echo "Example: $0 echo \"Hello World\""
  exit 1
fi

trap ctrl_c INT

function ctrl_c() {
  echo -e "\n[!] Script terminated by user (CTRL-C)"
  exit 0
}

# Get the command from arguments
CMD="$@"
count=0

while true; do
  # Run the command
  eval "$CMD"
  exit_status=$?

  count=$((count+1))

  # Notify about restart using osascript
  if command -v osascript &> /dev/null; then
    osascript -e "display notification \"$CMD restarting (iteration $count)\" with title \"Forever\" subtitle \"Exit status: $exit_status\""
  fi

  echo "[*] Command completed with exit status $exit_status, restarting..."
done
