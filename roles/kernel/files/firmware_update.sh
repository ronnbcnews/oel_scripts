#!/usr/bin/env bash

#!/bin/bash

set -o nounset
set -o errexit

REPO_URI=${REPO_URI:-"https://github.com/Hexxeh/rpi-firmware"}

UPDATE_SELF=${UPDATE_SELF:-1}
UPDATE_URI="https://raw.githubusercontent.com/raspberrypi/firmware/master"
/boot/bootcode.bin


BRANCH=${BRANCH:-"master"}
ROOT_PATH=${ROOT_PATH:-"/"}
BOOT_PATH=${BOOT_PATH:-"/boot"}
WORK_PATH=${WORK_PATH:-"${ROOT_PATH}/root"}
SKIP_KERNEL=${SKIP_KERNEL:-0}
SKIP_SDK=${SKIP_SDK:-0}
SKIP_REPODELETE=${SKIP_REPODELETE:-0}
SKIP_BACKUP=${SKIP_BACKUP:-0}
SKIP_DOWNLOAD=${SKIP_DOWNLOAD:-0}
SKIP_WARNING=${SKIP_WARNING:-0}
WANT_SYMVERS=${WANT_SYMVERS:-0}
PRUNE_MODULES=${PRUNE_MODULES:-0}
RPI_UPDATE_UNSUPPORTED=${RPI_UPDATE_UNSUPPORTED:-0}
JUST_CHECK=${JUST_CHECK:-0}
GITHUB_API_TOKEN=${GITHUB_API_TOKEN:-""}
FW_REPO="${REPO_URI}.git"
FW_REPOLOCAL=${FW_REPOLOCAL:-"${WORK_PATH}/.rpi-firmware"}
FW_PATH="${BOOT_PATH}"
FW_MODPATH="${ROOT_PATH}/lib/modules"
FW_REV_IN=${1:-""}
FW_REVFILE="${FW_PATH}/.firmware_revision"
[ "${RPI_UPDATE_UNSUPPORTED}" -ne 0 ] && echo -e "You appear to be trying to update firmware on an incompatible distribution. To force update, run the following:\nsudo -E RPI_UPDATE_UNSUPPORTED=0 rpi-update" && exit 1

# Support for custom GitHub Auth Tokens
GITHUB_AUTH_PARAM=""
if [[ -n "${GITHUB_API_TOKEN}" ]]; then
	echo " *** Using GitHub token for all requests."
	GITHUB_AUTH_PARAM="--header \"Authorization: token ${GITHUB_API_TOKEN}\""
fi

GITHUB_API_LIMITED=$(eval curl -Ls ${GITHUB_AUTH_PARAM} https://api.github.com/rate_limit | tr -d "," | awk 'BEGIN {reset=0;} { if ($1 == "\"limit\":") limit=$2; else if ($1 == "\"remaining\":") remaining=$2; else if ($1 == "\"reset\":" && limit>0 && remaining==0) reset=$2;} END { print reset }')
if [ ${GITHUB_API_LIMITED} -gt 0 ]; then
	echo " *** Github api is currently rate limited - please try again after $(date --date @${GITHUB_API_LIMITED})"
	exit 1
fi

curl -O -kL https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/bootcode.bin
curl -O -kL https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/start.elf
curl -O -kL https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/start_cd.elf
curl -O -kL https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/start_db.elf
curl -O -kL https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/start_x.elf
curl -O -kL https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/fixup.dat
curl -O -kL https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/fixup_cd.dat
curl -O -kL https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/fixup_db.dat
curl -O -kL https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/fixup_x.dat
