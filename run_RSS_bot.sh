#!/bin/bash

env/bin/python3 rss_atom_bot.py &
PROC_PID=$!
echo "Bot process:$PROC_PID"

# kill background processes on exit
trap 'kill $(jobs -p)' EXIT

# wait for process to finish. Or simply until this sxcript exits
wait $PROC_PID

exit 0;
