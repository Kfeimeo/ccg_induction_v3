#!/bin/sh
cd "$(dirname "$0")/.."
cat scripts/jobs3.txt | xargs -P 2 -I {} sh -c 'python3 scripts/run_induction.py {} > /dev/null 2>&1; echo "done: {}"'
