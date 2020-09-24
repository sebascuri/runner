"""Definition of all runner classes."""

import os
from datetime import datetime
from typing import List, Optional

from .abstract_runner import AbstractRunner


class IBMRunner(AbstractRunner):
    """Runner in IBM Cluster.

    The runner submits to the bsub queueing system.

    Parameters
    ----------
    name: str.
        Runner name.
    num_threads: int, optional. (default=1)/.
        Number of threads to use.
    use_gpu: bool, optional. (default: No GPU request).
        Flag to indicate GPU usage.
    wall_time: int, optional. (default: No extra time request).
        Required time, in minutes, to run the process.
    memory: int, optional. (default: No extra memory request).
        Required memory, in MB, to run run the process.

    """

    use_gpu: bool
    wall_time: Optional[int]
    memory: Optional[int]

    def __init__(
        self,
        name: str,
        num_threads: int = 1,
        use_gpu: bool = False,
        wall_time: Optional[int] = None,
        memory: Optional[int] = None,
    ) -> None:
        super().__init__(name, num_threads=num_threads)
        self.use_gpu = use_gpu
        self.wall_time = wall_time
        self.memory = memory

    def _build_base_cmd(self) -> str:
        bsub_cmd = "bsub "
        try:
            os.makedirs("logs/")
        except FileExistsError:
            pass
        if self.name is not None:  # Add LSF log dir.
            bsub_cmd += f"-o logs/lsf.{self.name} "

        if self.wall_time is not None:  # Add wall time.
            bsub_cmd += f"-W {self.wall_time} "

        if self.memory is not None:  # Add memory request.
            bsub_cmd += f'-R "rusage[mem={self.memory}]" '

        if self.use_gpu:  # Add GPU request.
            bsub_cmd += '-R "rusage[ngpus_excl_p=1]" '

        bsub_cmd += f"-n {self.num_threads} "  # Add number threads.

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
        """See `AbstractRunner.run_batch'."""
        bsub_cmd = self._build_base_cmd()

        current_time = datetime.now().strftime("%b%d_%H-%M-%S")
        cmd_file = f"logs/{self.name}_cmd_{current_time}"

        with open(cmd_file, "w") as f:
            for cmd in cmd_list:
                f.write(cmd + "\n")

        if self.name is not None:
            bsub_cmd += f'-J "{self.name}[1-{len(cmd_list)}]"'

        bsub_cmd += f" \"awk -v jindex=\\$LSB_JOBINDEX 'NR==jindex' {cmd_file} | bash\""
        os.system(bsub_cmd)
        return bsub_cmd
