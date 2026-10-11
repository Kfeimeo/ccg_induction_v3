#!/bin/bash
# Remaining supertagger-seed runs (jobs6.txt), all in parallel on the local machine with the
# C++ extension (CPython).  Per-job stdout: results/induction/queue6_<n>.log
cd "$(dirname "$0")/.." || exit 1
mkdir -p results/induction
i=0
while IFS= read -r cmd; do
  [ -z "$cmd" ] && continue
  i=$((i+1))
  ( start=$(date +%s); $cmd > "results/induction/queue6_$i.log" 2>&1; echo "job $i exit=$? elapsed=$(( $(date +%s) - start ))s :: $cmd" ) &
done < scripts/jobs6.txt
wait
echo "queue6 done"
