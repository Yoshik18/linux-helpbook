#!/usr/bin/env bash
# Source this file to create a new, private practice directory.
if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
    printf '%s\n' 'Use: source fundamentals/labs/setup.sh' >&2
    exit 2
fi

LINUX_LAB=$(mktemp -d "${TMPDIR:-/tmp}/linux-helpbook.XXXXXX") || return 1
export LINUX_LAB
mkdir -p "$LINUX_LAB"/{config,logs,notes,data,bin,archive} || return 1
printf '%s\n' 'port=8080' 'environment=staging' 'workers=2' > "$LINUX_LAB/config/app.conf"
printf '%s\n' 'INFO api started' 'ERROR api timeout' 'WARN worker queue-full' \
    'ERROR api timeout' 'ERROR db refused' > "$LINUX_LAB/logs/app.log"
printf '%s\n' '192.0.2.10 GET /health 200 8' '192.0.2.11 GET /orders 500 135' \
    '192.0.2.10 POST /orders 201 21' '192.0.2.12 GET /orders 500 150' \
    '192.0.2.11 GET /health 200 4' > "$LINUX_LAB/logs/access.log"
printf '%s\n' 'learn files' 'read logs' 'check permissions' > "$LINUX_LAB/notes/todo.txt"
printf '%s\n' 'spaces belong to this filename' > "$LINUX_LAB/notes/file with spaces.txt"
printf '%s\n' 'service,environment,requests' 'api,prod,120' 'worker,prod,45' \
    'api,staging,12' > "$LINUX_LAB/data/report.csv"
printf '%s\n' '#!/usr/bin/env bash' "printf '%s\\n' 'hello from the lab'" > "$LINUX_LAB/bin/hello.sh"
printf '%s\n' 'a hidden practice file' > "$LINUX_LAB/.practice"
printf '%s\n' 'dummy practice value, not a credential' > "$LINUX_LAB/config/private.txt"
chmod 600 "$LINUX_LAB/config/private.txt" || return 1
printf 'Practice directory: %s\n' "$LINUX_LAB"
