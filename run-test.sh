mkdir answers

solutions=(
#  "orchestra.py"
  "fast_orchestra.py"
#  "evolution.py"
#  "fullscan_border.py"
)

skip_tests=(
  "adder.cnf" "arbiter.cnf" "bar.cnf" "cavlc.cnf" "ctrl.cnf" "dec.cnf" "div.cnf" "hyp.cnf" "i2c.cnf" "int2float.cnf" "log2.cnf"
  "max.cnf" "mem_ctrl.cnf" "multiplier.cnf" "priority.cnf" "router.cnf" "sin.cnf" "sqrt.cnf" "square.cnf" "voter.cnf"
)


mkdir answers/orchestra/prop
mkdir answers/orchestra/conflicts
for solution in "${solutions[@]}"; do
  solution_name="${solution%.*}"
  mkdir answers/"$solution_name"
  mkdir answers/"$solution_name"/fasten

  cnt=1
  for test_filename in tests/cnf/*.cnf; do
    test_name=$(basename -- "$test_filename")

    skip=0
    for st in "${skip_tests[@]}"; do
      if [[ "$st" == "$test_name" ]]; then
        skip=1
        break
      fi
    done

    if (( skip )); then
      continue
    fi

    ans_name="${test_name%.*}"
    echo "Test $test_name on $solution_name $cnt"
    python3 "$solution" "$test_filename" --slow > answers/"$solution_name"/extra_slow/"$ans_name.ans"
    cnt=$((cnt+1))
  done
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
