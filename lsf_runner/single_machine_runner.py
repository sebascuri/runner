"""Definition of all runner classes."""

import multiprocessing
import os
import time
import warnings
from typing import List, Optional

from .abstract_runner import AbstractRunner
from .util import start_process


class SingleRunner(AbstractRunner):
    """Runner in a Single Machine.

    The runner submits the jobs in parallel to the `num_workers'. While the workers are
    working, it keeps on checking and spawns a new job every time a worker is freed up.

    Parameters
    ----------
    name: str.
        Runner name.
    num_threads: int, optional. (default=1)/.
        Number of threads to use.
    num_workers: int, optional. (default = cpu_count() // num_threads - 1).
        Number of workers where to run the process.
    """

    num_workers: int

    def __init__(
        self, name: str, num_threads: int = 1, num_workers: Optional[int] = None
    ):
        super().__init__(name, num_threads=num_threads)
        if num_workers is None:
            num_workers = max(1, multiprocessing.cpu_count() // num_threads - 1)

        if (num_workers >= multiprocessing.cpu_count() // num_threads) and (
            num_workers > 1
        ):
            num_workers = max(1, multiprocessing.cpu_count() // num_threads - 1)
            warnings.warn(f"Too many workers requested. Limiting them to {num_workers}")
        self.num_workers = num_workers

    def run(self, cmd_list: List[str]) -> List[str]:
        """See `AbstractRunner.run'."""
        workers_idle = [False] * self.num_workers
        pool = [start_process(lambda: None) for _ in range(self.num_workers)]
        tasks = cmd_list[:]

        while not all(workers_idle):
            for i in range(self.num_workers):
                if not pool[i].is_alive():
                    pool[i].terminate()
                    if len(tasks) > 0:
                        time.sleep(1)
                        cmd = tasks.pop(0)
                        pool[i] = start_process(lambda x: os.system(x), (cmd,))
                    else:
                        workers_idle[i] = True

        return cmd_list

    def run_batch(self, cmd_list: List[str]) -> str:
        """See `AbstractRunner.run_batch'."""
        return "".join(self.run(cmd_list))
