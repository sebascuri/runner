from .util import make_commands, is_ibm
from .runners import AbstractRunner, IBMRunner, SingleRunner


def init_runner(name, num_threads=1, use_gpu=False, wall_time=None, memory=None):
    """Initialize the runner.

    Parameters
    ----------
    name: str.
        Name of experiment.
    num_threads: int, optional
        Number of threads to use.
    use_gpu: bool, optional
        Flag to indicate GPU usage.
    wall_time: int, optional
        Required time, in minutes, to run the process.
    memory: int, optional
        Required memory, in MB, to run run the process.

    Returns
    -------
    runner: AbstractRunner

    """
    if is_ibm():
        return IBMRunner(name, num_threads, use_gpu, wall_time, memory)
    else:
        return SingleRunner(name, num_threads, use_gpu)
