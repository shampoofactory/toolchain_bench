from argparse import ArgumentParser
from pathlib import Path
import json
import subprocess
import sys

from pathvalidate import validate_filename
from pathvalidate.argparse import validate_filename_arg
import yaml


class Bencher:

    def __init__(self, data_dir, bin_dir, result_dir, flags=''):
        self.data_dir = Path(data_dir)
        self.bin_dir = Path(bin_dir)
        self.results_dir = Path(result_dir)
        self.flags = flags
        self.outputs = {}

    def init(self):
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True)

    def bench(self, tool, source, name, args, data):
        file = Path(self.results_dir, 'tmp.json')
        command = str(Path(self.bin_dir, tool, source, name))
        if args:
            command += f' {args}'
        if data:
            # *nix only
            command += f' < {Path(self.data_dir, data)}'
        cmd =\
            f'hyperfine'\
            f' {self.flags}'\
            f" '{command}'"\
            f' --export-json {file}'
        print(cmd)
        if subprocess.call(cmd, shell=True) != 0:
            raise RuntimeError(f'bench error: {cmd}')
        output = json.loads(file.read_text(encoding='UTF8'))
        file.unlink()
        self.outputs.setdefault(name, {}).setdefault(source, {})[tool] = output
        dump = json.dumps(self.outputs, indent=2)
        Path(self.results_dir, 'outputs.json').write_text(
            dump, encoding="'UTF8")


def execute_all(toolchains, config, data_dir='my_data', bin_dir='my_bin',
                result_dir='my_results'):
    flags = config['hyperfine']
    bencher = Bencher(data_dir, bin_dir, result_dir, flags=flags)
    bencher.init()

    for group in config['groups']:
        name = group['group']['manifest']['package']['name']
        args = group['group'].get('args')
        data = group['group'].get('data')
        validate_filename(name)
        for source in group['group']['sources']:
            print(f'bench: {source}')
            validate_filename(source)
            for tool in toolchains:
                validate_filename(tool)
                bencher.bench(tool, source, name, args, data)


def main():
    """Execute benchmarks using hyperfine

    Operates in conjunction with 'config.yaml', the user specified {toolchains}
    and the benchmarking binaries located in 'my_bin/{toolchain}.
    Benchmark Json results are located in 'my_results/outputs.json'. Any
    pre-existing benchmark results will be overwritten.

    A temporary 'my_result/tmp.json' will be created, overwritten and
    destroyed.

    """
    parser = ArgumentParser()
    parser.add_argument('toolchains', type=validate_filename_arg, nargs='+',
                        help='rustup toolchain/s to benchmark with')
    args = parser.parse_args()

    config = yaml.safe_load(Path('config.yaml').read_text(encoding='UTF8'))

    execute_all(args.toolchains, config)


if __name__ == '__main__':
    sys.exit(main())
