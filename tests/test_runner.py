from runner import init_runner, make_commands
from runner.runners import IBMRunner
import pytest
import sys
import itertools


def test_make_commands():
    script = 'tests/script.py'

    cmds = make_commands(
        script, base_args={'threads': 2}, fixed_hyper_args={'lr': 0.1},
        common_hyper_args={'seed': [0, 1, 2]},
        algorithm_hyper_args={'wd': [0.01, 0.1]}
    )

    assert cmds == [
        '{} {} --threads 2 --lr 0.1 --seed {} --wd {}'.format(
            sys.executable, script, seed, wd) for seed, wd in itertools.product(
            [0, 1, 2], [0.01, 0.1])]


def test_runner():
    script = 'tests/script.py'

    cmds = make_commands(
        script, base_args={'threads': 2}, fixed_hyper_args={'lr': 0.1},
        common_hyper_args={'seed': [0, 1, 2]},
        algorithm_hyper_args={'wd': [0.01, 0.1]}
    )

    runner = init_runner('test')
    runner.run(cmds)
    runner.run_batch(cmds)


@pytest.fixture(params=[1, 4])
def num_threads(request):
    return request.param


@pytest.fixture(params=[True, False])
def use_gpu(request):
    return request.param


@pytest.fixture(params=[None, 720])
def wall_time(request):
    return request.param


@pytest.fixture(params=[None, 4096])
def memory(request):
    return request.param


def test_ibm(num_threads, use_gpu, wall_time, memory):
    runner = IBMRunner(num_threads=num_threads, use_gpu=use_gpu, wall_time=wall_time,
                       memory=memory)

    base_cmd = runner._build_base_cmd()

    cmd = "bsub "
    if wall_time:
        cmd += '-W {} '.format(wall_time)
    if memory:
        cmd += '-R "rusage[mem={}]" '.format(memory)
    if use_gpu:
        cmd += '-R "rusage[ngpus_excl_p=1]" '

    cmd += '-n {} '.format(num_threads)

    assert cmd == base_cmd
