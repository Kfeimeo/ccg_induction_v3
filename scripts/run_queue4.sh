#!/bin/sh
# seed-lexicon (anchors) experiment: scripts/jobs4.txt with 3-way parallelism
cd "$(dirname "$0")/.."
cat scripts/jobs4.txt | xargs -P 3 -I {} sh -c 'python3 scripts/run_induction.py {} > /dev/null 2>&1; echo "done: {}"'
