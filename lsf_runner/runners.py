"""Definition of all runner classes."""

import multiprocessing
import os
import time
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
        self.num_workers = max(1, multiprocessing.cpu_count() // num_threads - 1)
        self.num_threads = num_threads
        self.use_gpu = use_gpu
        self.wall_time = wall_time
        self.memory = memory
        self.name = name

    @abstractmethod
    def run(self, cmd_list: List[str]) -> List[str]:
        """Run commands in list.

        Parameters
        ----------
        cmd_list: list

        """
        raise NotImplementedError

    @abstractmethod
    def run_batch(self, cmd_list: List[str]) -> str:
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
            bsub_cmd += f'-o logs/lsf.{self.name} '

        if self.wall_time is not None:  # Add wall time.
            bsub_cmd += f'-W {self.wall_time} '

        if self.memory is not None:  # Add memory request.
            bsub_cmd += f'-R "rusage[mem={self.memory}]" '

        if self.use_gpu:  # Add GPU request.
            bsub_cmd += '-R "rusage[ngpus_excl_p=1]" '

        bsub_cmd += f'-n {self.num_threads} '  # Add number threads.

        return bsub_cmd

    def run(self, cmd_list: List[str]) -> List[str]:
        """See `AbstractRunner.run'."""
        tasks = cmd_list[:]

        cmds = []
        bsub_cmd = self._build_base_cmd()
        for i, cmd in enumerate(tasks):
            bsub_cmd_i = bsub_cmd
            if self.name is not None:
                bsub_cmd_i += f'-J "{self.name}-{i}" '

            cmds.append(bsub_cmd_i + f'"{cmd}"')
            os.system(cmds[-1])

        return cmds

    def run_batch(self, cmd_list: List[str]) -> str:
        """Run jobs in batch mode."""
        bsub_cmd = self._build_base_cmd()

        if self.name is not None:
            cmd_file = f'logs/{self.name}_cmd'
        else:
            cmd_file = 'cmd_file'
        with open(cmd_file, 'w') as f:
            for cmd in cmd_list:
                f.write(cmd + '\n')

        if self.name is not None:
            bsub_cmd += f'-J "{self.name}[1-{len(cmd_list)}]"'

        bsub_cmd += f' "awk -v jindex=\\$LSB_JOBINDEX \'NR==jindex\' {cmd_file} | bash"'
        os.system(bsub_cmd)
        return bsub_cmd


class SingleRunner(AbstractRunner):
    """Runner in a Single Machine."""

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
        """Run batch."""
        return ''.join(self.run(cmd_list))
