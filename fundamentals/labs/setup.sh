#!/usr/bin/env bash
# Source this file to create a new, private practice directory.
if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
    printf '%s\n' 'Use: source fundamentals/labs/setup.sh' >&2
    exit 2
fi

__linux_helpbook_lab=$(mktemp -d "${TMPDIR:-/tmp}/linux-helpbook.XXXXXX") || return 1

__linux_helpbook_create_lab() {
    local lab=$1
    mkdir -p "$lab"/{config,logs,notes,data,bin,archive} || return 1
    printf '%s\n' 'port=8080' 'environment=staging' 'workers=2' > "$lab/config/app.conf" || return 1
    printf '%s\n' 'INFO api started' 'ERROR api timeout' 'WARN worker queue-full' \
        'ERROR api timeout' 'ERROR db refused' > "$lab/logs/app.log" || return 1
    printf '%s\n' '192.0.2.10 GET /health 200 8' '192.0.2.11 GET /orders 500 135' \
        '192.0.2.10 POST /orders 201 21' '192.0.2.12 GET /orders 500 150' \
        '192.0.2.11 GET /health 200 4' > "$lab/logs/access.log" || return 1
    printf '%s\n' 'learn files' 'read logs' 'check permissions' > "$lab/notes/todo.txt" || return 1
    printf '%s\n' 'spaces belong to this filename' > "$lab/notes/file with spaces.txt" || return 1
    printf '%s\n' 'service,environment,requests' 'api,prod,120' 'worker,prod,45' \
        'api,staging,12' > "$lab/data/report.csv" || return 1
    printf '%s\n' '#!/usr/bin/env bash' "printf '%s\\n' 'hello from the lab'" > "$lab/bin/hello.sh" || return 1
    printf '%s\n' 'a hidden practice file' > "$lab/.practice" || return 1
    printf '%s\n' 'dummy practice value, not a credential' > "$lab/config/private.txt" || return 1
    chmod 600 "$lab/config/private.txt" || return 1
}
if ! __linux_helpbook_create_lab "$__linux_helpbook_lab"; then
    rm -rf -- "$__linux_helpbook_lab"
    unset __linux_helpbook_lab
    unset -f __linux_helpbook_create_lab
    return 1
fi
LINUX_LAB=$__linux_helpbook_lab
export LINUX_LAB
unset __linux_helpbook_lab
unset -f __linux_helpbook_create_lab
printf 'Practice directory: %s\n' "$LINUX_LAB"
