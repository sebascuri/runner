# Runner

Runner is a package for running experiments, particular at a IBM LSF cluster. 
It provides a runner that can run locally on CPUs or GPUs, or on an IBM LSF cluster.

This package will change often as it is under development. 
## Installation  
```bash
pip install -U git+https://github.com/sebascuri/runner
```
Or clone and install 
```bash
git clone https://github.com/sebascuri/runner.git
cd runner 
pip install -e .[test]
```

## Running 
To run a command using this you can use a modification of the following snippet, 
where it will run a target `main.py`, using 

```python
from lsf_runner import init_runner, make_commands

TARGET = "main.py"
EXPERIMENT_NAME = "experiment_name"
CONFIG_FILE_DIR = "path/to/config/file"
SEEDS = [0, 1, 2, 3, 4]
ALPHAS = [1e-3, 1e-2, 1e-1]

runner = init_runner(
    f"{EXPERIMENT_NAME}", wall_time=24 * 60, num_threads=1, memory=4096
)
commands = make_commands(
    script=TARGET,
    base_args={
        "config-file": f"{CONFIG_FILE_DIR}",
    },
    common_hyper_args={"seed": SEEDS, "alpha": ALPHAS},
)
runner.run_batch(commands)
```