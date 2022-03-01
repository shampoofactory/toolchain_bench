from argparse import ArgumentParser
from pathlib import Path
import json
import sys

from scipy import stats


class Welch:

    def __init__(self, toolchain_a, toolchain_b, threshold=0.05):
        self.toolchain_a = toolchain_a
        self.toolchain_b = toolchain_b
        self.threshold = threshold
        self.count = 0
        self.top_a = 0
        self.top_b = 0
        self.discard = 0

    def summary(self):
        print('Summary:')
        print(f'  test count: {self.count}')
        print(f'  discarded (insignificant) tests: {self.discard}')
        print(f'  {self.toolchain_a} fastest: {self.top_a} times')
        print(f'  {self.toolchain_b} fastest: {self.top_b} times')

    def header(self):
        print(f'{"":<32}'
              f'{self.toolchain_a:<17}'
              '    '
              f'{self.toolchain_b:<17}')

        print(f'{"executable":<32}'
              f'{"relative":<8}'
              f'{"median":>9}'
              '    '
              f'{"relative":<8}'
              f'{"median":>9}'
              '    '
              f'significant')
        print('-' * 85)

    def test(self, program, res_a, res_b):
        median_a, median_b = res_a['median'], res_b['median']
        times_a, times_b = res_a['times'], res_b['times']

        _, p = stats.ttest_ind(times_a, times_b, equal_var=False)
        dispose = p < self.threshold

        self.count += 1
        if not dispose:
            self.discard += 1
        elif median_a < median_b:
            self.top_a += 1
        elif median_b < median_a:
            self.top_b += 1
        else:
            self.top_a += 1
            self.top_b += 1

        rel_a, rel_b = (
            median_a / median_b, 1.0) if median_a > median_b else (1.0, median_b / median_a)

        print(f'{program:<32}'
              f'{rel_a:<8.3f}'
              f'{median_a:8.3f}s'
              '    '
              f'{rel_b:<8.3f}'
              f'{median_b:8.3f}s'
              '    '
              f'{"T" if dispose else "F"} '
              f'{p:8.3f}p')


def execute_all(results, toolchain_a, toolchain_b, threshold=0.05):
    welch = Welch(toolchain_a, toolchain_b, threshold)
    welch.header()
    for _, data in results.items():
        for program, groups in data.items():
            set_a, set_b = groups[toolchain_a], groups[toolchain_b]
            res_a, res_b = set_a['results'][0], set_b['results'][0]
            welch.test(program, res_a, res_b)

    print('')
    welch.summary()


def main():
    """Welch's t-test

    Based on hyperfine's welch_ttest.py script:
    https://github.com/sharkdp/hyperfine/blob/master/scripts/welch_ttest.py

    """
    parser = ArgumentParser()
    parser.add_argument('toolchains', nargs=2,
                        help='rustup toolchain pair to compare')
    args = parser.parse_args()
    toolschains = args.toolchains

    results = json.loads(
        Path('my_results', 'outputs.json').read_text(encoding='UTF8'))

    execute_all(results, toolschains[0], toolschains[1])


if __name__ == '__main__':
    sys.exit(main())
