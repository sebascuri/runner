"""Python Script Template."""
import time
from queue import PriorityQueue
from typing import List, Optional

import paramiko
from scp import SCPClient, SCPException

from .abstract_runner import AbstractRunner


class MultiMachineRunner(AbstractRunner):
    """Multi-Machine Runner.

    Given a list of machines, it will query each of them using SSH.
    If there is enough compute power, it will send a command through SSH.
    Once if finishes, it copies the results from result_dir to current run_dir.

    When runner.run(cmd_list) is called it will run

    ssh username@cluster tmux; cd run_dir; conda activate conda_env; command &
    for each command in `cmd_list' and on the cluster with most actions.

    Parameters
    ----------
    name: str.
        Runner name.
    username: str
        user name of ssh connection.
    password: str
        password for ssh connection.
    cluster_list: List[str].
        list with machine names.
    num_threads: int.
        number of threads used by each command.
    max_timeout: int.
        Maximum waiting time for each ssh command.
    conda_env: str, optional.
        If given, it will call conda activate `conda_env' before executing remotely.
    run_dir: str, optional.
        If given, it will call cd `run_dir' before executing remotely.
    result_dir: str, optional.
        If given, it will scp the files at result_dir to the local directory.

    """

    def __init__(
        self,
        name: str,
        username: str,
        password: str,
        cluster_list: List[str],
        num_threads: int = 1,
        max_timeout: int = 3,
        conda_env: Optional[str] = None,
        run_dir: Optional[str] = None,
        result_dir: Optional[str] = None,
    ):
        super().__init__(name, num_threads=num_threads)
        self.username = username
        self.password = password
        self.max_timeout = max_timeout
        self.conda_env = conda_env
        self.run_dir = run_dir
        self.result_dir = result_dir
        self.cluster_list = cluster_list

    def _close(self, cluster_dict):
        """Kill all processes."""
        for name, ssh in cluster_dict.items():
            if self._is_alive(ssh) and self.result_dir is not None:
                scp = SCPClient(ssh.get_transport())
                try:
                    scp.get(
                        self.result_dir,
                        local_path="",
                        recursive=True,
                        preserve_times=True,
                    )
                except SCPException:
                    pass
                scp.close()

        for ssh in cluster_dict.values():
            ssh.close()

    def _connect_to(self, name, ssh=None):
        if ssh is None:
            ssh = paramiko.SSHClient()

        ssh.load_system_host_keys()
        try:
            ssh.connect(
                hostname=name,
                username=self.username,
                password=self.password,
                timeout=self.max_timeout,
            )
        except:
            pass
        return ssh

    @staticmethod
    def _is_alive(ssh):
        transport = ssh.get_transport()
        if transport is None:
            is_alive = False
        else:
            is_alive = transport.is_active()
        return is_alive

    def _get_cpu_count(self, name, cluster_dict):
        ssh = cluster_dict[name]
        if not self._is_alive(ssh):
            self._connect_to(name, ssh=ssh)
        try:
            _, out, _ = ssh.exec_command("nproc --all", timeout=self.max_timeout)
            return [int(o) for o in out.readlines()][0]
        except:
            return 0

    def _get_available_cpu_count(self, name, cluster_dict):
        ssh = cluster_dict[name]
        if not self._is_alive(ssh):
            self._connect_to(name, ssh=ssh)
        try:
            _, out, _ = ssh.exec_command(
                "python get_free_cpu_count.py", timeout=self.max_timeout
            )
            return [int(o) for o in out.readlines()][0]
        except:
            return 0

    def _run_at_machine(self, name, cluster_dict, command):
        try:
            ssh = cluster_dict[name]
            if not self._is_alive(ssh):
                self._connect_to(name, ssh=ssh)

            cmd = "tmux; "
            if self.run_dir is not None:
                cmd += f"cd {self.run_dir}; "
            if self.conda_env is not None:
                cmd += f"conda activate {self.conda_env}; "
            cmd += f"{command} &"
            ssh.exec_command(cmd, timeout=self.max_timeout)
            return 0
        except:
            return -1

    def run(self, cmd_list: List[str]) -> List[str]:
        """See `AbstractRunner.run'."""
        cluster_dict = {name: self._connect_to(name) for name in self.cluster_list}
        cluster_queue = PriorityQueue()  # type: PriorityQueue
        for name, value in cluster_dict.items():
            cluster_queue.put(
                (-self._get_available_cpu_count(name, cluster_dict), 0, name)
            )

        tasks = cmd_list.copy()
        while tasks:
            old_free_cpu, call_count, machine_name = cluster_queue.get()
            new_free_cpu = self._get_available_cpu_count(machine_name, cluster_dict)
            if new_free_cpu > 1 + self.num_threads:
                command = tasks.pop()
                exit_status = self._run_at_machine(
                    machine_name, cluster_dict, command=command
                )
                if exit_status == 0:
                    print(f"Remaining {len(tasks)} tasks")
                    new_free_cpu -= self.num_threads
                    cluster_queue.put((-new_free_cpu, call_count - 1, machine_name))
                else:
                    cluster_queue.put((-new_free_cpu, call_count - 1, machine_name))
            else:
                cluster_queue.put((-new_free_cpu, call_count - 1, machine_name))
                time.sleep(self.max_timeout)

        self._close(cluster_dict)

        return cmd_list

    def run_batch(self, cmd_list: List[str]) -> str:
        """See `AbstractRunner.run_batch'."""
        return "".join(self.run(cmd_list))
