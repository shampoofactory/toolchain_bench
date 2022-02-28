from argparse import ArgumentParser
from contextlib import redirect_stdout
from pathlib import Path
import sys

from benchmarks import fasta


def write(path, n):
    global write
    if Path(path).exists():
        print(f'data: target exists: {path}')
    else:
        print(f'data: generate {n} -> {path}')
        with open(path, 'w') as file:
            with redirect_stdout(file):
                fasta.execute(n)


def execute(data_dir='my_data'):
    if not Path(data_dir).exists():
        Path(data_dir).mkdir(parents=True)
    write(Path(data_dir, 'knucleotide-input25000000.txt'), 25000000)
    write(Path(data_dir, 'regexredux-input5000000.txt'), 5000000)
    write(Path(data_dir, 'revcomp-input100000000.txt'), 100000000)


def main():
    """Build benchmark input data
    """
    parser = ArgumentParser()
    args = parser.parse_args()

    execute()


if __name__ == '__main__':
    sys.exit(main())
