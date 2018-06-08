#!/usr/bin/env bash

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
NC='\033[0m'

OS="$(uname)"

logInfo(){
  echo -e "${CYAN}`date "+%Y-%m-%d %H:%M:%S"`${NC} ${BLUE}[INFO]${NC}: $1"
}

logInfoStep(){
  echo -e "${CYAN}`date "+%Y-%m-%d %H:%M:%S"`${NC} ${BLUE}[INFO]${NC}: $1 ${GREEN}[OK]${NC}"
}

logErr(){
  echo -e "${CYAN}`date "+%Y-%m-%d %H:%M:%S"`${NC} ${RED}[ERR]${NC}: $1"
}

logWarn(){
  echo -e "${CYAN}`date "+%Y-%m-%d %H:%M:%S"`${NC} ${YELLOW}[WARN]${NC}: $1"
}

if [[ $# -lt 1 ]]; then
    logErr "Please specify packages to upload"
    exit -1
fi

while [[ $# -gt 0 ]]
do
    logInfo "Uploading package '$1'"
    cd "$1"
    twine upload -r pypi dist/*
    cd ..
    shift
done