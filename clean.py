from pathlib import Path
import shutil


def main():
    """Clean any generated or temporary folders: 'my_bin', 'my_results' and
    'my_build'
    """
    if Path('my_bin').exists():
        shutil.rmtree('my_bin')
    if Path('my_build').exists():
        shutil.rmtree('my_build')
    if Path('my_results').exists():
        shutil.rmtree('my_results')


main()
