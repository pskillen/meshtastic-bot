#!/usr/bin/env bash

script_dir="$(dirname "$0")"
project_dir="$(realpath "${script_dir}/../..")"

scp paddy@meshcontrol.local:~/MeshtasticBot/*.json "${project_dir}/"
