from argparse import ArgumentParser
from pathlib import Path
import json
import subprocess
import sys

from welch import Welch


class Sleep:

    def __init__(self, result_dir, flags=''):
        self.flags = flags
        self.results_dir = Path(result_dir)

    def init(self):
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True)

    def bench(self, time):
        file = Path(self.results_dir, 'tmp.json')
        # *nix only
        command = f'sleep {time}'
        cmd =\
            f'hyperfine'\
            f' {self.flags}'\
            f" '{command}'"\
            f' --export-json {file}'
        print(cmd)
        if subprocess.call(cmd, shell=True) != 0:
            raise RuntimeError(f'bench error: {cmd}')
        return json.loads(file.read_text(encoding='UTF8'))['results'][0]


def execute(time_a, time_b, result_dir='my_results', flags='--warmup 1',
            threshold=0.05):
    sleep = Sleep(result_dir, flags)
    sleep.init()

    res_a, res_b = sleep.bench(time_a), sleep.bench(time_b)

    welch = Welch(time_a, time_b, threshold)
    welch.header()
    welch.test('sleep', res_a, res_b)
    print('')
    welch.summary()


def main():
    """Sleep comparison test.
    $ python3 test.py 1 2
    """
    parser = ArgumentParser()
    parser.add_argument('times', nargs=2, help='sleep times in seconds')
    args = parser.parse_args()
    times = args.times

    execute(times[0], times[1])


if __name__ == '__main__':
    sys.exit(main())
