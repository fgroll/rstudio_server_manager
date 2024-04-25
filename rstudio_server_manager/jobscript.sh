#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --ntasks=1

set -euo pipefail

# This is the template for submitting the jobs to start RStudio Server.
# The output file and name are defined when submitting the script from within python

cleanup() {
    # Kill rserver manually
    ps | grep rserver | tr -s ' ' | cut -d ' ' -f1 | xargs -r kill

    # Wait 10 seconds for rserver to shutdown gracefully
    sleep 10

    # Remove the temporary directories used by rserver
    rm -rf ${SINGTMP}
}

# Get the IP of the node the job is running on and a random open port
IP=$(hostname -i)
PORT=$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1])')

# Create a set of temporary directories needed for RStudio Server in the container
SINGTMP=$(mktemp -d $TMPDIR/${USER}_rstudio.XXXXXXXXXX)
mkdir -p -m 700 ${SINGTMP}/{tmp,run,lib}

# Print the IP and Port to the log file
echo "RSTUDIO-${IP}:${PORT}"

# If the script gets stopped delete the Singularity directories
trap cleanup EXIT

# Start the RStudio Server in the Singularity container
PASSWORD=${1} \
singularity exec \
    --bind ${SINGTMP}/tmp:/tmp \
    --bind ${SINGTMP}/run:/run \
    --bind ${SINGTMP}/lib:/var/lib/rstudio-server \
    ${3} \
    ${2} \
    rserver \
    --server-user ${USER} \
    --auth-none=0  \
    --auth-pam-helper-path=pam-helper \
    --www-port ${PORT} \
    --server-data-dir /tmp
