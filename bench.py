from argparse import ArgumentParser
from pathlib import Path
import json
import yaml

from pathvalidate.argparse import validate_filename_arg

import build
import data
import hyper
import welch


parser = ArgumentParser()
parser.add_argument('toolchains', type=validate_filename_arg, nargs=2,
                    help='rustup toolchains to benchmark')
args = parser.parse_args()

toolchains = args.toolchains

config = yaml.safe_load(Path('config.yaml').read_text(encoding='UTF8'))

data.execute()

build.execute_all(toolchains, config)

hyper.execute_all(toolchains, config)

results = json.loads(
    Path('my_results', 'outputs.json').read_text(encoding='UTF8'))

welch.execute_all(results, toolchains[0], toolchains[1])
