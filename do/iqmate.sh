#!/usr/bin/env bash

if [[ $# -lt 2 ]]; then
    echo 'Usage: [--workspace=Path] [--reset] <IQ Panel Host> <IQ Panel Secure Token>'
    echo '    IQ Panel Host: The hostname or IP address of the IQ Panel'
    echo '    IQ Panel Secure Token: The secure token from the IQ Panel Control4 integration'
    echo '    --workspace: Optionally specify path the workspace directory (Defaults to ./workspace)'
    echo '    --reset: Optionally delete contents of the workspace and start from scratch'
    echo 'Visit https://support.suretyhome.com/t/surety-iq-mate/32721 for documentation.'
    exit 1
fi

# Pull out the options and build the args array
args=()
for arg; do
    case $arg in 
        --reset) should_reset=1 ;;
        --workspace=*) workspace="${arg:12}" ; workspace="${workspace/#\~/$HOME}" ;;
        *) args+=($arg) ;;
    esac
done

# Figure out what the workspace directory will be and create if necessary
if [[ -z "$workspace" ]]; then
    workspace="$PWD/workspace"
fi
if [[ ! -d "$workspace" ]]; then
    mkdir "$workspace"
fi

# Reset if needed
if [[ -n "$should_reset" ]]; then
    read -p "Are you sure you want to delete everything in $workspace? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -Rf "$workspace"/*
    fi
fi

# Run IQ Mate
docker run --rm -it \
    -p 1880:1880 -p 1883:1883 \
    -v "$workspace":/iqmate -w /iqmate \
    -e IQPANEL_HOST=${args[0]} -e IQPANEL_TOKEN=${args[1]} \
    suretyhome/iqmate /bin/bash
