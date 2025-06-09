mkdir answers

solutions=(
#  "orchestra.py"
  "fast_orchestra.py"
#  "evolution.py"
#  "fullscan_border.py"
)

# "adder.cnf" "arbiter.cnf" "bar.cnf" "cavlc.cnf" "ctrl.cnf" "dec.cnf" "div.cnf" "hyp.cnf"
skip_tests=(
 "i2c.cnf" "int2float.cnf" "log2.cnf"
  "max.cnf" "mem_ctrl.cnf" "multiplier.cnf" "priority.cnf" "router.cnf" "sin.cnf" "sqrt.cnf" "square.cnf" "voter.cnf"
)


mkdir answers/extractor
cnt=1
for test_filename in tests/cnf/*.cnf; do
  test_name=$(basename -- "$test_filename")

  skip=1
  for st in "${skip_tests[@]}"; do
    if [[ "$st" == "$test_name" ]]; then
      skip=0
      break
    fi
  done

  if (( skip )); then
    continue
  fi

  ans_name="${test_name%.*}"
  echo "Test $test_name on extractor $cnt"
  python3 -m extraction.extractor "$test_filename" > answers/extractor/"$ans_name.ans"
  cnt=$((cnt+1))
done

#for solution in "${solutions[@]}"; do
#  solution_name="${solution%.*}"
#  mkdir answers/"$solution_name"/slower
#  cnt=1
#  for test_filename in tests/cnf/*.cnf; do
#    test_name=$(basename -- "$test_filename")
#
#    skip=0
#    for st in "${skip_tests[@]}"; do
#      if [[ "$st" == "$test_name" ]]; then
#        skip=1
#        break
#      fi
#    done
#
#    if (( skip )); then
#      continue
#    fi
#
#    ans_name="${test_name%.*}"
#    echo "Test $test_name on $solution_name $cnt"
#    python3 "$solution" "$test_filename" > answers/"$solution_name"/slower/"$ans_name.ans"
#    cnt=$((cnt+1))
#  done
#done
