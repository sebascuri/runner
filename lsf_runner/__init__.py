from .util import make_commands, is_ibm
from .runners import AbstractRunner, IBMRunner, SingleRunner


def init_runner(name, num_threads=1, use_gpu=False, wall_time=None, memory=None,
                num_workers=None):
    """Initialize the runner.

    Parameters
    ----------
    name: str.
        Name of experiment.
    num_threads: int, optional (default=1).
        Number of threads to use.
    use_gpu: bool, optional (default=False).
        Flag to indicate GPU usage.
    wall_time: int, optional (default=None).
        Required time, in minutes, to run the process.
    memory: int, optional. (default=None).
        Required memory, in MB, to run run the process.
    num_workers: int, optional. (default=num_available cpu // num_threads - 1).
        Set the maximum number of parallel workers to launch.

    Returns
    -------
    runner: AbstractRunner
        An initialized runner.

    """
    if is_ibm():
        return IBMRunner(name, num_threads=num_threads, use_gpu=use_gpu,
                         wall_time=wall_time, memory=memory)
    else:
        return SingleRunner(name, num_threads=num_threads, num_workers=num_workers)
