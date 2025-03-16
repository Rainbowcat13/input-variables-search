mkdir stats

solutions=(
  "evolution.py"
)

for solution in "${solutions[@]}"; do
  solution_name="${solution%.*}"
  mkdir stats/"$solution_name"

  for size in $(seq 1 35); do
    for test_filename in tests/*.cnf; do
      test_name=$(basename -- "$test_filename")
      stat_file=stats/"$solution_name"/"$ans_name.stat"
      ans_name="${test_name%.*}"
      echo "Test $test_name on $solution_name size=$size"
      python3 "$solution" "$test_filename" -s $size -m conflicts -e 100 -g 100 >> $stat_file
    done
  done
done