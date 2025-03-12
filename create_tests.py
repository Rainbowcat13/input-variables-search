import os
import sys
from pathlib import Path

output_dir = 'tests'
if len(sys.argv) > 1:
    output_dir = sys.argv[1]

blif_dirs = ['benchmarks/arithmetic', 'benchmarks/random_control']
blif_files = [
    str(file.absolute())
    for file in sum([
        list(Path(d).glob('**/*'))
        for d in blif_dirs
    ], [])
    if file.name.endswith('.blif')
]

for blf in blif_files:
    cnf_filename = f'{blf.split("/")[-1].split(".")[0]}.cnf'
    if os.path.exists(f'{output_dir}/{cnf_filename}'):
        print(f'File {cnf_filename} already exists. To regenerate clear {output_dir}.')
    else:
        print(f'\nConverting {blf}...')
        os.system(f'abc/abc -c "read_blif {blf}; strash; write_cnf {output_dir}/{cnf_filename}"')

if os.path.exists('abc.history'):
    os.system('rm abc.history')
