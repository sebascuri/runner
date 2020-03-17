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