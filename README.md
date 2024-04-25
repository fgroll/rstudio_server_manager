## RStudio Server Manager

This Python package makes it easy to start new RStudio Server containers as Slurm jobs and stop these jobs once your analysis is done. For this, 3 commands are provided:

### The `start` command

This command allows you to easily start a new RStudio Server container as Slurm job. It will automatically find a free port, start the RStudio Server and return the link to the server. Using the arguments, you can change the name and resources of the Slurm job, as well as the password or specific BioConductor release for your RStudio Server.  
For more information on available options use `rstudio start --help`.

### The `stop` command

With this command you can stop a running RStudio Server Slurm job. If only one job is currently running, the `stop` command will register that job for deletion. When multiple jobs are running use the `--jobs` argument, either by specifying the job ID or job name, to stop a specific RStudio Server job.  
For more information on available options use `rstudio stop --help`.

### The `ls` command

To get an overview of all running RStudio Server jobs you can use the `ls` command, useful in combination with the `stop` command.  
For more information on available options use `rstudio ls --help`.

> Important note: For now only a single concurrent RStudio Server job is supported. If you start a second one this **WILL** break the currently running job!

## Using/installing the manager

First you need to set the directory that contains your Bioconductor singularity containers in `rstudio_server_manager/__init__.py`. The only external dependency required is `rich-argparse`, so install it in your current environment. Or change the interpreter in `rstudio-server-manager/rstudio` to a installation of Python (`>=3.9`) that has `rich-argparse` installed.

Afterwards, simply add the following line to your profile (e.g. `~/.bash_profile` when using `bash`):

`alias rstudio='~/path/to/your/location/of/rstudio_server_manager/rstudio'`

This will make all commands accessible through calling `rstudio`.

## Starting and stopping a new RStudio Server session

To start a new RStudio Server session simply run the following command (optionally supplying a specific BioConductor release, etc.):

```rstudio start --release 3.15```

Once the job has been submitted to Slurm and starts running, it will print the address where the RStudio Server session is running. You should be able to use Cmd + double-click to directly open the link in your browser!

Once you are done, save your files and stop the running job with: 

```rstudio stop```
