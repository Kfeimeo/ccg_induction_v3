#!/bin/sh
# supertagger seed-lexicon experiment (stNP / stNPN x stack-2 / Eisner-NF CKY; controls): scripts/jobs5.txt, 4-way parallel
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
cat scripts/jobs5.txt | xargs -P 4 -I {} sh -c 'echo "start: {} $(date +%H:%M)"; python scripts/run_induction.py {} > /dev/null 2>&1; echo "done: {} $(date +%H:%M)"'
