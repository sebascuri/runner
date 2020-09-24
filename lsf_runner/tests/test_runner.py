import itertools
import os
import shutil
import sys

import pytest

from lsf_runner import IBMRunner, SingleRunner, init_runner, make_commands


@pytest.fixture(params=[IBMRunner, SingleRunner])
def runner(request):
    runner_ = request.param("test")
    yield runner_
    try:
        shutil.rmtree("logs")
    except FileNotFoundError:
        pass


@pytest.fixture()
def cmds():
    cwd = os.path.dirname(os.path.realpath(__file__))
    script = f"{cwd}/script.py"
    return make_commands(
        script,
        base_args={"threads": 2, "print": True, "lr": 0.1},
        common_hyper_args={"seed": [0, 1, 2]},
        algorithm_hyper_args={"wd": [0.01, 0.1]},
    )


@pytest.fixture(params=[1, 4])
def num_threads(request):
    return request.param


def test_make_commands():
    script = "tests/script.py"

    cmds = make_commands(
        script,
        base_args={"threads": 2, "lr": 0.1, "print": True, "layers": [64, 128]},
        common_hyper_args={"seed": [0, 1, 2]},
        algorithm_hyper_args={"wd": [0.01, 0.1]},
    )

    assert cmds == [
        "{} {} --threads 2 --lr 0.1 --print --layers 64 128 --seed {} --wd {}".format(
            sys.executable, script, seed, wd
        )
        for seed, wd in itertools.product([0, 1, 2], [0.01, 0.1])
    ]


def test_run(runner, cmds):
    runner.run(cmds)


def test_run_batch(runner, cmds):
    runner.run_batch(cmds)


def test_init_run(cmds):
    runner = init_runner("test")
    runner.run(cmds)


def test_init_run_batch(cmds):
    runner = init_runner("test")
    runner.run_batch(cmds)


class TestLSF(object):
    @pytest.fixture(params=[True, False], scope="class")
    def use_gpu(self, request):
        return request.param

    @pytest.fixture(params=[None, 720], scope="class")
    def wall_time(self, request):
        return request.param

    @pytest.fixture(params=[None, 4096], scope="class")
    def memory(self, request):
        return request.param

    def test_lsf_params(self, num_threads, use_gpu, wall_time, memory):
        runner = IBMRunner(
            "test",
            num_threads=num_threads,
            use_gpu=use_gpu,
            wall_time=wall_time,
            memory=memory,
        )

        base_cmd = runner._build_base_cmd()

        cmd = "bsub -o logs/lsf.test "
        if wall_time:
            cmd += "-W {} ".format(wall_time)
        if memory:
            cmd += '-R "rusage[mem={}]" '.format(memory)
        if use_gpu:
            cmd += '-R "rusage[ngpus_excl_p=1]" '

        cmd += "-n {} ".format(num_threads)

        assert cmd == base_cmd
        self.delete_logs()

    def test_lsf_run(self, cmds):
        runner = IBMRunner("test")
        runner.run(cmds)
        self.delete_logs()

    def test_lsf_run_batch(self, cmds):
        runner = IBMRunner("test")
        runner.run_batch(cmds)
        self.delete_logs()

    @staticmethod
    def delete_logs():
        try:
            shutil.rmtree("logs")
        except FileNotFoundError:
            pass


class TestSingle(object):
    @pytest.fixture(params=[1, 2, 4], scope="class")
    def num_threads(self, request):
        return request.param

    def test_warning(self, num_threads):
        with pytest.warns(UserWarning):
            runner = SingleRunner("test", num_threads=num_threads, num_workers=4)

        assert runner.num_workers == max(1, 4 // num_threads - 1)

    def test_default_num_workers(self, num_threads):
        runner = SingleRunner("test", num_threads=num_threads)

        assert runner.num_workers == max(1, 4 // num_threads - 1)

    def test_single_run(self, cmds):
        runner = SingleRunner("test")
        runner.run(cmds)

    def test_single_run_batch(self, cmds):
        runner = SingleRunner("test")
        runner.run_batch(cmds)
