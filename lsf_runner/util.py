"""Utilities for runners project."""
import itertools
import multiprocessing
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

__author__ = "Sebastian Curi"
__all__ = ["make_commands", "is_ibm", "start_process"]


def get_command(key: str, value: Any) -> str:
    """Get command for a key-value pair."""
    if value is None:
        cmd = ""
    if isinstance(value, bool):
        if value:
            cmd = f" --{key}"  # for store_true arguments.
        else:
            cmd = f"--no-{key}"  # for store_false arguments.
    elif isinstance(value, list):
        assert len(value) > 0, "Non-empty lists are not allowed."
        cmd = f" --{key} {' '.join(str(v) for v in value)}"
    else:
        cmd = f" --{key} {value}"

    return cmd


def make_commands(
    script: str,
    base_args: Optional[Dict[str, Any]] = None,
    common_hyper_args: Optional[Dict[str, List[Any]]] = None,
    algorithm_hyper_args: Optional[Dict[str, List[Any]]] = None,
) -> List[str]:
    """Generate command to run.

    It will generate a list of commands to be use with the runners.
    Each command will look like:
        python script --base_arg_key --base_arg_val
           --common_hyper_key --common_hyper_key
           --algorithm_hyper_key --algorithm_hyper_key
           --mutually_exclusive_args
    where a separate command is generated for each common hyper_parameter and
    algorithm_hyper_parameter

    Parameters
    ----------
    script: str.
        String with script to run.
    base_args: dict
        Base arguments to execute.
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
    base_cmd = interpreter_script + " " + script
    commands = []  # List[str]

    if common_hyper_args is None:
        common_hyper_args = dict()  # pragma: no cover

    common_hyper_args = common_hyper_args.copy()
    if algorithm_hyper_args is not None:
        common_hyper_args.update(algorithm_hyper_args)

    hyper_args_list = list(
        dict(zip(common_hyper_args, x))
        for x in itertools.product(*common_hyper_args.values())
    )

    for hyper_args in hyper_args_list:
        cmd = base_cmd
        for dict_ in [base_args, hyper_args]:
            if dict_ is None:
                continue
            for key, value in dict_.items():
                cmd += get_command(key, value)
        commands.append(cmd)

    return commands


def is_ibm() -> bool:
    """Check if host is IBM."""
    return "LSF_ENVDIR" in os.environ


def start_process(
    target: Callable, args: Optional[Tuple] = None
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
