#!/usr/bin/env bash

scriptname=$(basename "$0")
dtime_format="%Y-%m-%d_%H-%M-%S"
scriptdir=$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd)

# Execute Python script
${scriptdir}/${scriptname%.*}.py "${scriptdir}"



