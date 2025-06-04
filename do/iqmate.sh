#!/usr/bin/env bash

if [[ $# -lt 2 ]]; then
    echo 'Usage: [--shared=Path] [--reset] <IQ Panel Host> <IQ Panel Secure Token>'
    echo '    IQ Panel Host: The hostname or IP address of the IQ Panel'
    echo '    IQ Panel Secure Token: The secure token from the IQ Panel Control4 integration'
    echo '    --shared: Optionally specify path the shared directory (Defaults to ./shared)'
    echo '    --reset: Optionally delete contents of shared directory and start from scratch'
    echo 'Visit https://support.suretyhome.com/t/surety-iq-mate/32721 for documentation.'
    exit 1
fi

# Pull out the options and build the args array
args=()
for arg; do
    case $arg in 
        --reset) should_reset=1 ;;
        --shared=*) shared_dir="${arg:9}" ; shared_dir="${shared_dir/#\~/$HOME}" ;;
        *) args+=($arg) ;;
    esac
done

# Figure out what the shared directory will be and create if necessary
if [[ -z "$shared_dir" ]]; then
    shared_dir="$PWD/shared"
fi
if [[ ! -d "$shared_dir" ]]; then
    mkdir "$shared_dir"
fi

# Reset if needed
if [[ -n "$should_reset" ]]; then
    read -p "Are you sure you want to delete everything in $shared_dir? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -Rf "$shared_dir"/*
    fi
fi

# Run IQ Mate
docker run --rm -it \
    -p 1880:1880 -p 1883:1883 \
    -v "$shared_dir":/iqmate -w /iqmate \
    -e IQPANEL_HOST=${args[0]} -e IQPANEL_TOKEN=${args[1]} \
    suretyhome/iqmate /bin/bash
