"""Utilities for runners project."""
import multiprocessing
import os
import sys
import itertools
from typing import Callable, Optional, Tuple, List, Dict, Any

__author__ = 'Sebastian Curi'
__all__ = ['make_commands', 'is_ibm', 'start_process']


def make_commands(script: str, base_args: Dict[str, Any],
                  fixed_hyper_args: Dict[str, Any] = None,
                  common_hyper_args: Dict[str, List[Any]] = None,
                  algorithm_hyper_args: Dict[str, List[Any]] = None
                  ) -> List[str]:
    """Generate command to run.

    It will generate a list of commands to be use with the runners.
    Each command will look like:
        python script --base_arg_key --base_arg_val
           --fixed_hyper_key --fixed_hyper_arg
           --common_hyper_key --common_hyper_key
           --algorithm_hyper_key --algorithm_hyper_key
    where a separate command is generated for each common hyper_parameter and
    algorithm_hyper_parameter

    Parameters
    ----------
    script: str.
        String with script to run.
    base_args: dict
        Base arguments to execute.
    fixed_hyper_args: dict
        Fixed hyper parameters to execute.
    common_hyper_args: dict
        Iterable hyper parameters to execute in different runs.
    algorithm_hyper_args
        Algorithm dependent hyper parameters to execute.

    Returns
    -------
    commands: List[str]
        List with commands to execute.

    """
    interpreter_script = sys.executable
    base_cmd = interpreter_script + ' ' + script
    commands = []  # List[str]

    if fixed_hyper_args is None:
        fixed_hyper_args = dict()

    if common_hyper_args is None:
        common_hyper_args = dict()

    common_hyper_args = common_hyper_args.copy()
    if algorithm_hyper_args is not None:
        common_hyper_args.update(algorithm_hyper_args)

    hyper_args_list = list(dict(zip(common_hyper_args, x))
                           for x in itertools.product(*common_hyper_args.values()))

    for hyper_args in hyper_args_list:
        cmd = base_cmd
        for dict_ in [base_args, fixed_hyper_args, hyper_args]:
            for key, value in dict_.items():
                if isinstance(value, bool):
                    if value:
                        cmd += " --{}".format(key)  # for store_true arguments.
                elif isinstance(value, list):
                    assert len(value) > 0, "Non-empty lists are not allowed."
                    cmd += " --{}".format(key) + (' {}' * len(value)).format(*value)
                else:
                    cmd += " --{} {}".format(key, value)
        commands.append(cmd)

    return commands


def is_ibm() -> bool:
    """Check if host is IBM."""
    return 'LSF_ENVDIR' in os.environ


def start_process(target: Callable, args: Optional[Tuple] = None
                  ) -> multiprocessing.Process:
    """Start a process from with the multiprocessing framework.

    Parameters
    ----------
    target: callable
    args: tuple, optional

    Returns
    -------
    p: Process

    """
    if args:
        p = multiprocessing.Process(target=target, args=args)
    else:
        p = multiprocessing.Process(target=target)
    p.start()
    return p
