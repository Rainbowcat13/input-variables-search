mkdir answers

solutions=(
  "evolution.py"
#  "fullscan_border.py"
)

for solution in "${solutions[@]}"; do
  solution_name="${solution%.*}"
  mkdir answers/"$solution_name"
  cnt=1
  for test_filename in tests/*.cnf; do
    test_name=$(basename -- "$test_filename")
    ans_name="${test_name%.*}"
    echo "Test $test_name on $solution_name $cnt"
    python3 "$solution" "$test_filename" > answers/"$solution_name"/"$ans_name.ans"
    cnt=$((cnt+1))
  done
done