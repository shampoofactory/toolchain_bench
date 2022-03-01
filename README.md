# toolchain_bench
Benchmark and compare `rustup` toolchain executable performance using [The Computer Language Benchmarks Game](https://benchmarksgame-team.pages.debian.net/benchmarksgame/index.html) benchmarks and [hyperfine](https://github.com/sharkdp/hyperfine).


## Prerequisites

Python3 and the following packages:

```
$ pip3 install mergedeep pathvalidate scipy toml pyyaml
```

Hyperfine:

```
$ sudo apt install hyperfine
```

`rustup` configured with the correct tool chains.
E.g.
```
$ rustup install 1.58.1
```
```
$ rustup toolchain link {my-toolchain} {path/to/my/toolchain/sysroot}
```

## Quick start

Compare `1.58.0` and `1.58.1`:
```
$ python3 bench.py 1.58.0 1.58.1
```

This will build, benchmark and output results:
```
                                1.58.1               1.58.1.revert    
executable                      relative   median    relative   median    significant
-------------------------------------------------------------------------------------
empty.rs                        1.042      0.001s    1.000      0.001s    T    0.000p
binarytrees.rust                1.005      2.268s    1.000      2.257s    F    0.315p
binarytrees.rust-2.rust         1.014      1.221s    1.000      1.204s    F    0.351p
.
.
.
spectralnorm.rust-7.rust        1.000      1.025s    1.000      1.025s    F    0.498p

Summary:
  test count: 63
  discarded (insignificant) tests: 43
  1.58.1 fastest: 12 times
  1.58.1.revert fastest: 8 times
```

To output the results without running the benchmarks again:
```
python3 welch.py 1.58.0 1.58.1
```

Alternatively, assuming `rustup` has been configured with `1.58.1` and a modified variant `1.58.1.revert`:
```
$ python3 bench.py 1.58.1 1.58.1.revert
```

**Important!** To cut down on rebuild times, `bench.py`, or more specifically `build.py`, will not rebuild binaries that already exist in the corresponding `my_bin/{toolchain}` folder. To force a rebuild simply remove the relevant `my_bin/{toolchain}` folder.


## Breakdown

Four commands are invoked by `bench.py` in order:

- Data (`data.py`), generate input data for benchmarks. This data is cached.
- Build (`build.py`), build rust executables into `my_bin`. These binaries are cached. To force a rebuild simply remove the relevant `my_bin/{toolchain}` folder.
- Benchmark (`hyper.py`), benchmark using [hyperfine](https://github.com/sharkdp/hyperfine) and output to `my_results/outputs.json`
- Analysis (`welch.py`), Welch's t-test based on [this](https://github.com/sharkdp/hyperfine/blob/master/scripts/welch_ttest.py) hyperfine script.

These can also be called individually.


## Analysis

This implementation currently only provides a simple Welch's t-test.

The benchmark output data is saved in `my_results/outputs.json`. The data is organised as `group.source.toolchain.results`.

Example:
```json
{
  "binarytrees": {
    "binarytrees.rust": {
      "1.58.1": {
        "results": [
          {
            "command": "my_bin/1.58.1/binarytrees.rust/binarytrees 21",
            "mean": 2.25133281418,
            "stddev": 0.02438307964580027,
            "median": 2.25123771508,
            "user": 7.6929631999999994,
            "system": 0.08517338,
            "min": 2.2172595720799997,
            "max": 2.28075038708,
            "times": [
              2.28075038708,
              2.27312458908,
              2.23069984308,
              2.25781735108,
              2.24171778808,
              2.2446580790799997,
              2.21759370008,
              2.2172595720799997,
              2.27494145808,
              2.27476537408
            ],
            "exit_codes": [
              0,
              0,
              0,
              0,
              0,
              0,
              0,
              0,
              0,
              0
            ]
          }
        ]
      }
    }
  } 
}
```

## Configuration

Configuration is via 'config.yaml'.


## The Computer Language Benchmarks Game

'The Computer Language Benchmarks Game' homepage is [here](https://benchmarksgame-team.pages.debian.net/benchmarksgame/index.html) with the project repo [here](https://salsa.debian.org/benchmarksgame-team/benchmarksgame).

I am in no way affiliated with the 'The Computer Language Benchmarks Game'. All trademarks belong to their respective owners.


## License

Licensed under either of

 * Apache License, Version 2.0
   ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
 * MIT license
   ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

Any [Benchmarks Game](https://benchmarksgame-team.pages.debian.net/benchmarksgame/index.html) source code, located in 'benchmarks' folder, is covered by the enclosed [Revised BSD license](/benchmarks/LICENSE).
