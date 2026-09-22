#!/bin/sh
# run all jobs in scripts/jobs.txt with 4-way parallelism
cd "$(dirname "$0")/.."
cat scripts/jobs.txt | xargs -P 4 -I {} sh -c 'python3 scripts/run_induction.py {} > /dev/null 2>&1; echo "done: {}"'
