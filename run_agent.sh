#! /usr/bin/env bash

cd "$(dirname $1)"
echo "Running '$1'..."
export PYTHONUNBUFFERED=1
uv run "$(basename $1)"
