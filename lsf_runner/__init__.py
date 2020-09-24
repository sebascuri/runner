from .ibm_runner import IBMRunner
from .multi_machine_runner import MultiMachineRunner
from .single_machine_runner import SingleRunner
from .util import is_ibm, make_commands


def init_runner(
    name,
    num_threads=1,
    use_gpu=False,
    wall_time=None,
    memory=None,
    num_workers=None,
    cluster_list=None,
    username="",
    password="",
    conda_env=None,
    run_dir=None,
    result_dir=None,
):
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
    cluster_list: List[str].
        List with cluster machines.
    username: str.
        Username for cluster list.
    password: str.
        Password for cluster list.
    conda_env: str.
        Name of conda environment in clusters.
    run_dir: str.
        Name of running directory in cluster.
    result_dir: str.
        Directory where results are stored in cluster.

    Returns
    -------
    runner: AbstractRunner
        An initialized runner.

    """
    if is_ibm():
        return IBMRunner(
            name,
            num_threads=num_threads,
            use_gpu=use_gpu,
            wall_time=wall_time,
            memory=memory,
        )
    else:
        if cluster_list is None:
            return SingleRunner(name, num_threads=num_threads, num_workers=num_workers)
        else:
            return MultiMachineRunner(
                name,
                num_threads=num_threads,
                username=username,
                password=password,
                cluster_list=cluster_list,
                conda_env=conda_env,
                run_dir=run_dir,
                result_dir=result_dir,
            )
