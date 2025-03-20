script_dir="$(dirname "$0")"
project_dir="$(realpath "${script_dir}/..")"

rsync -av --exclude-from="${project_dir}/.rsyncignore" "${project_dir}/" paddy@meshcontrol.local:~/MeshtasticBot
