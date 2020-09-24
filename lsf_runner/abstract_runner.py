"""Definition of all runner classes."""

from abc import ABC, abstractmethod
from typing import List


class AbstractRunner(ABC):
    """Abstract runner class.

    Parameters
    ----------
    name: str.
        Runner name.
    num_threads: int, optional. (default=1)/.
        Number of threads to use.
    """

    name: str
    num_threads: int

    def __init__(self, name: str, num_threads: int = 1):
        self.name = name
        self.num_threads = num_threads

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
