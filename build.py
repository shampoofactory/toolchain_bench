from argparse import ArgumentParser
from pathlib import Path
import os
import shutil
import subprocess
import sys

from mergedeep import merge
from pathvalidate import validate_filename
from pathvalidate.argparse import validate_filename_arg
import toml
import yaml


class Builder:
    def __init__(self, root_manifest, build_dir, flags=''):
        self.root_manifest = root_manifest
        self.build_dir = build_dir
        self.flags = flags

    def init(self, child_manifest):
        manifest = {}
        merge(manifest, self.root_manifest)
        merge(manifest, child_manifest)

        Path(self.build_dir).mkdir(parents=True)
        Path(self.build_dir, 'src').mkdir()
        Path(self.build_dir, 'Cargo.toml')\
            .write_text(toml.dumps(manifest), encoding="UTF8")

    def set_src(self, src):
        Path(self.build_dir, 'src', 'main.rs')\
            .write_text(src, encoding="UTF8")

    def build(self, target_dir, toolchain, overwrite):
        # Assuming a simple Config.toml
        manifest = Path(self.build_dir, "Cargo.toml")
        config = manifest.read_text(encoding='UTF8')
        config = toml.loads(config)
        name = config['package']['name']
        validate_filename(name)

        target = Path(target_dir, name)
        if target.exists():
            if overwrite:
                print(f'build: target exists, overwriting: {target}')
                target.unlink()
            else:
                print(f'build: target exists: {target}')
                return

        env = os.environ.copy()
        env['RUSTFLAGS'] = self.flags
        cmd =\
            f'cargo +{toolchain} build '\
            f'--manifest-path={manifest} '\
            f'--target-dir={self.build_dir} '\
            f'--release'
        print(cmd)
        if subprocess.call(cmd, shell=True, env=env) != 0:
            raise RuntimeError(f'build error: {cmd}')

        Path(target_dir).mkdir(parents=True)
        Path(self.build_dir, 'release', name).rename(target)

    def clean(self):
        if Path(self.build_dir).exists():
            shutil.rmtree(self.build_dir)


def execute_all(toolchains, config, bin_dir='my_bin', build_dir='my_build',
                overwrite=False):
    for toolchain in toolchains:
        execute(toolchain, config, bin_dir, build_dir, overwrite)


def execute(toolchain, config, bin_dir='my_bin', build_dir='my_build',
            overwrite=False):
    root_manifest = config['manifest']
    flags = config['rustflags']
    builder = Builder(root_manifest, build_dir, flags=flags)

    for group in config['groups']:
        child_manifest = group['group']['manifest']
        builder.clean()
        builder.init(child_manifest)
        for source in group['group']['sources']:
            target_dir = Path(bin_dir, toolchain, source)
            print(f'build: {source} -> {target_dir}')
            validate_filename(source)
            src = Path('benchmarks', source).read_text(encoding='UTF8')
            builder.set_src(src)
            builder.build(target_dir, toolchain, overwrite)

    builder.clean()


def main():
    """Build benchmark rustc binaries


    Operates in conjunction with 'config.yaml' and the specified {toolchain}.
    Binaries are located 'my_bin/{tool}'.

    A temporary 'my_build' folder will be created, overwritten and destroyed.

    """
    parser = ArgumentParser()
    parser.add_argument('toolchains', type=validate_filename_arg, nargs='+',
                        help='rustup toolchain/s to build with')
    args = parser.parse_args()

    config = yaml.safe_load(Path('config.yaml').read_text(encoding='UTF8'))

    execute_all(args.toolchains, config)


if __name__ == '__main__':
    sys.exit(main())
