from runner import init_runner, make_commands
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
        '{} {} --threads=2 --lr=0.1 --seed={} --wd={}'.format(
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
