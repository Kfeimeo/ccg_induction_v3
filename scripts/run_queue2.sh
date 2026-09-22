#!/bin/sh
cd "$(dirname "$0")/.."
cat scripts/jobs2.txt | xargs -P 3 -I {} sh -c 'python3 scripts/run_induction.py {} > /dev/null 2>&1; echo "done: {}"'
