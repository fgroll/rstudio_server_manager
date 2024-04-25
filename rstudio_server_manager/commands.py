from functools import partial
from pathlib import Path
import signal
import subprocess
import tempfile
from time import sleep
import urllib.request
import urllib.error

from rich import print
from rich.markdown import Markdown

from rstudio_server_manager import parsers, helpers, CONTAINER_DIR


def start(argv: list[str]):
    """Starts a new RStudio Server container as cluster job."""
    parser = parsers.get_start_parser()
    args = parser.parse_args(argv)

    if not args.name.startswith("rstudio_"):
        args.name = "rstudio_" + args.name

    # Get the absolute path to the jobscript template
    jobscript = Path(__file__).resolve().parent / "jobscript.sh"

    with tempfile.NamedTemporaryFile(
        mode="r",
        suffix=".log",
        dir=Path.home(),
        delete=not args.keep_log
    ) as tmpfile:
        # Construct the command and submit the jobscript
        command = [
            "sbatch",
            "--parsable",
            "--output", tmpfile.name,
            "--job-name", args.name,
            "--partition", args.partition,
            "--cpus-per-task", str(args.threads),
            "--mem", args.memory,
            str(jobscript),
            args.password,
            Path(CONTAINER_DIR) / "bioconductor_docker_RELEASE_{}.sif".format(str(args.release).replace(".", "_")),
            "--bind " + args.bind if args.bind is not None else ""
        ]

        # Submit the job
        process = subprocess.run(command, capture_output=True)
        if process.returncode != 0:
            raise RuntimeError(f"sbatch had non-zero exit:\n{process}")

        # Check size of the file by moving to the end and returning the current
        # stream position
        tmpfile.seek(0, 2)
        while tmpfile.tell() == 0:
            helpers.print_progress("Waiting for the job output")
            sleep(1)
            tmpfile.seek(0, 2)

        tmpfile.seek(0)
        job_output = tmpfile.read().strip()

        if job_output.startswith("RSTUDIO-") and job_output.count("\n") == 0:
            address = job_output.split("-")[-1]
        else:
            raise RuntimeError(f"rstudio had non-zero exit:\n{job_output}")

    # Try to connect to the RStudio Server session to make sure it is reachable
    while True:
        try:
            urllib.request.urlopen(f"http://{address}").getcode()
            break
        except urllib.error.URLError:
            helpers.print_progress("Waiting for RStudio Server to start")
            sleep(1)
            continue

    print("Waiting for RStudio Server to start: Done!")
    # Print the first 2 lines of the file (contain the IP)
    print("Your RStudio Server is running at:")
    print(f"http://{address}")


def stop(argv: list[str]):
    """Stops a running RStudio Server container.

    When run with no arguments, if there is only a single RStudio Server job
    running, that one will be stopped.
    """
    parser = parsers.get_stop_parser()
    args = parser.parse_args(argv)

    jobs = list(helpers.get_cluster_jobs())
    command = ["scancel"]

    # If the `--all` argument is set, delete all running jobs
    if args.all:
        for job in jobs:
            subprocess.run(["scancel", job.id])
        return

    # If no job is specified, check if there is only 1 running job
    if args.job is None:
        if len(jobs) == 1:
            targetjob = [jobs[0].id]
            command += targetjob
        else:
            raise RuntimeError("No job specified and more than 1 job running!")

    # If a job is specified by name, check for that job
    elif any(char.isalpha() for char in args.job):
        targetjob = [job.id for job in jobs if job.name == args.job]
        if len(targetjob) == 0:
            raise RuntimeError(f"The specified job '{args.job}' is not a valid RStudio job name!")
        else:
            command += targetjob

    # If the job is specified by ID, check for that job
    else:
        targetjob = [job.id for job in jobs if job.id == args.job]
        if len(targetjob) == 0:
            raise RuntimeError(f"The specified job '{args.job}' is not a valid RStudio job ID!")
        else:
            command += targetjob

    # Register the target RStudio job for deletion
    ret = subprocess.run(command)
    if ret.returncode != 0:
        raise RuntimeError(f"scancel had non-zero exit:\n{ret}")
    else:
        print(f"Registerd job {targetjob[0]} for deletion.")


def ls(argv: list[str]):
    """Shows all currently running RStudio Server containers."""
    parser = parsers.get_show_parser()
    _ = parser.parse_args(argv)

    # Define format of the printed job list with the Format Specification Mini-Language
    format_str = '{:<10}{:<30}{:<10}'

    jobs = list(helpers.get_cluster_jobs())
    if len(jobs) == 0:
        print("No RStudio Server jobs currently running!")
    else:
        print(format_str.format("ID", "Name", "Time"))
        print("-" * 50)
        for job in jobs:
            # Print the job info, limiting the name to 29 characters to retain a nice table
            print(format_str.format(job.id, job.name[:29], job.time))


def info(argv: list[str]):
    """Prints additional information for all commands."""
    parser = parsers.get_info_parser()
    _ = parser.parse_args(argv)

    readme = Path(__file__).resolve().parent.parent / "README.md"
    with open(readme) as f:
        text = Markdown(f.read())

    print(text)
