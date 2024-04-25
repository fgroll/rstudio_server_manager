from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys
from typing import Generator, Callable

from rstudio_server_manager import CONTAINER_DIR


@dataclass
class Job:
    """Class representation of a cluster job."""
    id: str
    name: str
    state: str
    time: str

    @classmethod
    def from_squeue(cls, string: str, sep: str = ",") -> "Job":
        """Constructs a `Job` object from a `squeue` line."""
        return cls(*string.split(sep))


def get_cluster_jobs() -> Generator[Job, None, None]:
    """Returns a list of all running RStudio jobs of the user."""
    process = subprocess.run(["squeue", "--me", "--format", "%i,%j,%T,%M"], capture_output=True)

    for job in (Job.from_squeue(line) for line in process.stdout.decode("UTF-8").splitlines()[1:]):
        if job.name.startswith("rstudio_") and job.state == "RUNNING":
            yield job


def _get_spinner() -> Callable[[str], None]:
    """Returns a closure to print a message and the progress."""
    i = 0

    def _inner(msg: str) -> None:
        """Prints the message and updates the spinner."""
        nonlocal i
        spinner_parts = "|/-\\"
        print(f"{msg} {spinner_parts[i % 4]}", end="\r")
        i += 1
        sys.stdout.flush()

    return _inner


print_progress = _get_spinner()


def get_available_releases() -> list[str]:
    """Returns a list of all available Bioconductor container releases."""
    release_pattern = re.compile(r"bioconductor_docker_RELEASE_(\d)_(\d+)")

    dir = Path(CONTAINER_DIR)
    files = dir.glob("*.sif")
    matched_releases = (release_pattern.findall(str(file)) for file in files)
    return [f"{major}.{minor}" for sublist in matched_releases for major, minor in sublist]
