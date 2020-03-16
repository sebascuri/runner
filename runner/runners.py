"""Definition of all runner classes."""

import multiprocessing
import os
from abc import ABC, abstractmethod
from typing import List, Optional
from .util import start_process


class AbstractRunner(ABC):
    """Abstract runner class.

    Parameters
    ----------
    num_threads: int, optional
        Number of threads to use.
    use_gpu: bool, optional
        Flag to indicate GPU usage.
    wall_time: int, optional
        Required time, in minutes, to run the process.
    memory: int, optional
        Required memory, in MB, to run run the process.
    """

    num_workers: int
    num_threads: int
    use_gpu: bool
    wall_time: Optional[int]
    memory: Optional[int]
    name: Optional[str]

    def __init__(self, name: str = None, num_threads: int = 1, use_gpu: bool = False,
                 wall_time: int = None, memory: int = None) -> None:
        self.num_workers = multiprocessing.cpu_count() // num_threads
        self.num_threads = num_threads
        self.use_gpu = use_gpu
        self.wall_time = wall_time
        self.memory = memory
        self.name = name

    @abstractmethod
    def run(self, cmd_list: List[str]) -> None:
        """Run commands in list.

        Parameters
        ----------
        cmd_list: list

        """
        raise NotImplementedError

    @abstractmethod
    def run_batch(self, cmd_list: List[str]) -> None:
        """Run commands in list in batch mode.

        Parameters
        ----------
        cmd_list: list

        """
        raise NotImplementedError


class IBMRunner(AbstractRunner):
    """Runner in IBM Cluster."""

    def _build_base_cmd(self) -> str:
        bsub_cmd = 'bsub '
        if self.name is not None:  # Add LSF log dir.
            try:
                os.makedirs('logs/')
            except FileExistsError:
                pass
            bsub_cmd += '-o logs/lsf.{} '.format(self.name)

        if self.wall_time is not None:  # Add wall time.
            bsub_cmd += '-W {} '.format(self.wall_time)

        if self.memory is not None:  # Add memory request.
            bsub_cmd += '-R "rusage[mem={}]" '.format(self.memory)

        if self.use_gpu:  # Add GPU request.
            bsub_cmd += '-R "rusage[ngpus_excl_p=1]" '

        bsub_cmd += '-n {} '.format(self.num_threads)  # Add number threads.

        return bsub_cmd

    def run(self, cmd_list: List[str]) -> None:
        """See `AbstractRunner.run'."""
        tasks = cmd_list[:]

        bsub_cmd = self._build_base_cmd()
        for i, cmd in enumerate(tasks):
            bsub_cmd_i = bsub_cmd
            if self.name is not None:
                bsub_cmd_i += '-J "{}-{}"'.format(self.name, i)
            os.system(bsub_cmd_i + '"{}"'.format(cmd))

    def run_batch(self, cmd_list: List[str]) -> None:
        """Run jobs in batch mode."""
        if self.name is not None:
            cmd_file = 'logs/{}_cmd'.format(self.name)
        else:
            cmd_file = 'cmd_file'
        with open(cmd_file, 'w') as f:
            for cmd in cmd_list:
                f.write(cmd + '\n')

        bsub_cmd = self._build_base_cmd()
        if self.name is not None:
            bsub_cmd += '-J "{}[1-{}]"'.format(self.name, len(cmd_list))

        bsub_cmd += ' "awk -v jindex=\\$LSB_JOBINDEX \'NR==jindex\' {} | bash"'.format(
            cmd_file)
        os.system(bsub_cmd)


class SingleRunner(AbstractRunner):
    """Runner in a Single Machine."""

    def run(self, cmd_list: List[str]) -> None:
        """See `AbstractRunner.run'."""
        workers_idle = [False] * self.num_workers
        pool = [start_process(lambda: None) for _ in range(self.num_workers)]
        tasks = cmd_list[:]

        while not all(workers_idle):
            for i in range(self.num_workers):
                if not pool[i].is_alive():
                    pool[i].terminate()
                    if len(tasks) > 0:
                        cmd = tasks.pop(0)
                        pool[i] = start_process(lambda x: os.system(x), (cmd,))
                    else:
                        workers_idle[i] = True

    def run_batch(self, cmd_list: List[str]) -> None:
        """Run batch."""
        self.run(cmd_list)
