import argparse
from inspect import cleandoc, getmembers, isfunction

from rich_argparse import RawDescriptionRichHelpFormatter

from rstudio_server_manager import commands, helpers


def get_main_parser() -> argparse.ArgumentParser:
    """Creates the main parser for the CLI."""
    # Create the parser and set its description
    parser = argparse.ArgumentParser(
        prog="rstudio",
        usage=argparse.SUPPRESS,
        description=cleandoc(
            f"""
            [dark_orange]Usage:[/dark_orange]
                [grey50]%(prog)s[/grey50] <[cyan]command[/cyan]> [cyan]...[/cyan]

            Manages RStudio Server Singularity containers running as cluster jobs.

            [dark_orange]Commands:[/dark_orange]
                [cyan]start[/cyan]       {commands.start.__doc__.split(".")[0]}
                [cyan]stop[/cyan]        {commands.stop.__doc__.split(".")[0]}
                [cyan]ls[/cyan]          {commands.ls.__doc__.split(".")[0]}
                [cyan]info[/cyan]        {commands.info.__doc__.split(".")[0]}
            """
        ),
        formatter_class=RawDescriptionRichHelpFormatter
    )
    # Add argument to choose the command
    parser.add_argument(
        "command",
        choices=[x[0] for x in getmembers(commands, isfunction)],
        help=argparse.SUPPRESS
    )
    # Add argument to show version
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s==0.1"
    )

    return parser


def get_start_parser() -> argparse.ArgumentParser:
    """Creates the parser for the `start` subcommand."""
    # Create the parser and set its description
    parser = argparse.ArgumentParser(
        prog="rstudio start",
        description=cleandoc(f"{commands.start.__doc__}"),
        formatter_class=RawDescriptionRichHelpFormatter
    )
    # Add argument to name the SGE job
    parser.add_argument(
        "-n", "--name",
        default="rstudio_server",
        help="Set the name for the Slurm job. Default: '%(default)s'"
    )

    # Add argument to change the password for the session
    parser.add_argument(
        "-p", "--password",
        default="rstudioserver",
        help="Set the password for the RStudio Server session. Default: '%(default)s'"
    )

    # Add argument to change the specific container/Bioconductor release
    parser.add_argument(
        "-r", "--release",
        default="3.13",
        help="Choose the release of Bioconductor used for the session. Default: %(default)s. Choices: %(choices)s",
        choices=helpers.get_available_releases(),
        metavar="RELEASE"
    )

    # Add argument to change the partition for running RStudio Server
    parser.add_argument(
        "-q", "--partition",
        default="compute",
        help="Choose the partition for running RStudio Server"
    )

    # Add argument to change the number of threads
    parser.add_argument(
        "-t", "--threads",
        default=1,
        type=int,
        help="Set the number of threads requested. Default: %(default)s"
    )

    # Add argument to change the amount of memory
    parser.add_argument(
        "-m", "--memory",
        default="8G",
        type=str,
        help="Set the amount of memory requested. Default: %(default)s"
    )

    # Add argument to add custom bindings using the Singularity syntax
    parser.add_argument(
        "-b", "--bind",
        type=str,
        help="Bind additional paths to the container, using the Singularity spec src[:dest[:opts]]. "
            "Multiple bind paths can be given as comma-separated list."
    )

    # Add argument to keep the temporary log file for debugging purporses
    parser.add_argument(
        "-k", "--keep-log",
        action="store_true",
        help="Keep the temporary log file created by Slurm"
    )

    return parser


def get_stop_parser() -> argparse.ArgumentParser:
    """Creates the parser for the `stop` subcommand."""
    # Create the parser and set its description
    parser = argparse.ArgumentParser(
        prog="rstudio stop",
        description=cleandoc(f"{commands.stop.__doc__}"),
        formatter_class=RawDescriptionRichHelpFormatter
    )
    # Add argument to select a RStudio Server job
    parser.add_argument(
        "-j", "--job",
        help="Select a specific RStudio job to be stopped"
    )
    # Add argument to stop all Rstudio Server jobs
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Stop all currently running RStudio jobs"
    )

    return parser


def get_show_parser() -> argparse.ArgumentParser:
    """Creates the parser for the `show` subcommand."""
    parser = argparse.ArgumentParser(
        prog="rstudio ls",
        description=cleandoc(f"{commands.ls.__doc__}"),
        formatter_class=RawDescriptionRichHelpFormatter
    )

    return parser


def get_info_parser() -> argparse.ArgumentParser:
    """Creates the parser for the `info` subcommand."""
    parser = argparse.ArgumentParser(
        prog="rstudio info",
        description=cleandoc(f"{commands.info.__doc__}"),
        formatter_class=RawDescriptionRichHelpFormatter
    )

    return parser
