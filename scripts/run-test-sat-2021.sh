mkdir answers/sat2021

for test_filename in sat2021/*.cnf; do
  test_name=$(basename -- "$test_filename")
  ans_name="${test_name%.*}"

  .venv/bin/python3 -m extraction.extractor "$test_filename" > answers/sat2021/"$ans_name.ans"
done