# Shell Scripting Guide

These are Bash examples, not portable POSIX `sh` scripts. `mapfile` and associative
arrays require Bash 4 or later; the older Bash bundled with some macOS versions
does not support them. Run `bash --version` before trying those sections.

Some blocks illustrate one construct and need the variables shown in context.
They are not one script to concatenate. Use disposable files for writes;
check syntax with `bash -n script.sh` before running your own script.

## Basic Script Structure

### Shebang and Header
```bash
#!/bin/bash
# Script Name: example.sh
# Description: Brief description of what the script does
# Author: Your Name
# Date: 2024-01-01
# Version: 1.0

# Exit on an unhandled failure in contexts where errexit applies
set -e

# Exit on undefined variables
set -u
```

`set -e` is not a complete error-handling policy. Tests, AND/OR lists and functions
called as conditions affect when it applies. Check expected failures explicitly.
With `set -u`, use `${1:-}` for an optional argument rather than an unset `$1`.
See the [Bash set builtin](https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html).

### Basic Script Template
```bash
#!/bin/bash

# Script configuration
SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${LOG_FILE:-./script.log}" # Choose a writable path; do not assume root

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Main function
main() {
    log "Starting script execution"
    # Your script logic here
    log "Script completed successfully"
}

# Call main function
main "$@"
```

---

## Variables and Data Types

### Variable Declaration
```bash
# Simple variables
NAME="John"
AGE=25
PI=3.14159

# Read-only variables
readonly CONSTANT="This cannot be changed"

# Declare local variables inside a function
show_status() {
    local status="inside"
    printf '%s\n' "$status"
}

# Export variables for child processes
export PATH="/usr/local/bin:$PATH"
```

### Variable Usage
```bash
# Basic usage
echo "Hello, $NAME"

# Curly braces for clarity
echo "Hello, ${NAME}"

# Default values
echo "User: ${USER:-guest}"

# String length
echo "Name length: ${#NAME}"

# Substring
echo "First 3 chars: ${NAME:0:3}"
```

### Arrays
```bash
# Declare array
fruits=("apple" "banana" "orange")

# Access elements
echo "First fruit: ${fruits[0]}"
echo "All fruits: ${fruits[@]}"
echo "Array length: ${#fruits[@]}"

# Add to array
fruits+=("grape")

# Iterate through array
for fruit in "${fruits[@]}"; do
    echo "Fruit: $fruit"
done
```

---

## Control Structures

### If Statements
```bash
# Basic if
if [ "$1" = "hello" ]; then
    echo "Hello there!"
fi

# If-else
if [ -f "$file" ]; then
    echo "File exists"
else
    echo "File not found"
fi

# If-elif-else
if [ "$age" -lt 18 ]; then
    echo "Minor"
elif [ "$age" -lt 65 ]; then
    echo "Adult"
else
    echo "Senior"
fi

# Multiple conditions
if [ -f "$file" ] && [ -r "$file" ]; then
    echo "File exists and is readable"
fi
```

### Case Statements
```bash
case "$1" in
    "start")
        echo "Starting service..."
        ;;
    "stop")
        echo "Stopping service..."
        ;;
    "restart")
        echo "Restarting service..."
        ;;
    "status")
        echo "Checking status..."
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
```

### Loops
```bash
# For loop with range
for i in {1..5}; do
    echo "Number: $i"
done

# For loop with list
for item in "one" "two" "three"; do
    echo "Item: $item"
done

# While loop
counter=0
while [ $counter -lt 5 ]; do
    echo "Counter: $counter"
    counter=$((counter + 1))
done

# Until loop
until [ $counter -eq 10 ]; do
    echo "Counter: $counter"
    counter=$((counter + 1))
done

# C-style for loop
for ((i=0; i<5; i++)); do
    echo "C-style: $i"
done
```

---

## Functions

### Function Definition
```bash
# Simple function
greet() {
    echo "Hello, $1!"
}

# Function with local variables
calculate_area() {
    local width=$1
    local height=$2
    local area=$((width * height))
    echo "Area: $area"
}

# Function with return value
is_even() {
    local num=$1
    if [ $((num % 2)) -eq 0 ]; then
        return 0  # true
    else
        return 1  # false
    fi
}

# Function with default parameters
create_user() {
    local username=${1:-"default_user"}
    local home_dir=${2:-"/home/$username"}
    echo "Creating user: $username in $home_dir"
}
```

### Function Usage
```bash
# Call functions
greet "Alice"
calculate_area 10 5

# Check return value
if is_even 4; then
    echo "4 is even"
fi

# Use default parameters
create_user
create_user "john" "/home/john"
```

---

## File Operations

### File Testing
```bash
# Check if file exists
if [ -f "$file" ]; then
    echo "File exists"
fi

# Check if directory exists
if [ -d "$dir" ]; then
    echo "Directory exists"
fi

# Check if file is readable
if [ -r "$file" ]; then
    echo "File is readable"
fi

# Check if file is executable
if [ -x "$file" ]; then
    echo "File is executable"
fi

# Check whether a path exists and has a nonzero size
if [ -s "$file" ]; then
    echo "File is not empty"
fi
```

### File Reading
```bash
# Read file line by line
while IFS= read -r line || [[ -n "$line" ]]; do
    echo "Line: $line"
done < "$file"

# Read file into array
mapfile -t lines < "$file"

# Read specific line
line_5=$(sed -n '5p' "$file")

# Count lines
line_count=$(wc -l < "$file")
```

### File Writing
```bash
# Write to file (overwrite)
echo "content" > "$file"

# Append to file
echo "content" >> "$file"

# Write multiple lines
cat > "$file" << EOF
Line 1
Line 2
Line 3
EOF

# Append multiple lines
cat >> "$file" << EOF
Additional line 1
Additional line 2
EOF
```

---

## Command Line Arguments

### Argument Handling
```bash
# Basic argument access
echo "Script name: $0"
echo "First argument: $1"
echo "Second argument: $2"
echo "All arguments: $@"
echo "Number of arguments: $#"

# Shift arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -f|--file)
            file="$2"
            shift 2
            ;;
        -v|--verbose)
            verbose=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done
```

### Getopts Example
```bash
#!/bin/bash

# Default values
file=""
verbose=false
help=false

# Parse options
while getopts ":f:vh" opt; do
    case $opt in
        f)
            file="$OPTARG"
            ;;
        v)
            verbose=true
            ;;
        h)
            help=true
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG needs an argument" >&2
            exit 1
            ;;
    esac
done

# Shift processed options
shift $((OPTIND-1))

# Use the variables
if [ "$verbose" = true ]; then
    echo "Verbose mode enabled"
fi

if [ -n "$file" ]; then
    echo "Processing file: $file"
fi
```

---

## Error Handling

### Exit Codes
```bash
# Successful execution
exit 0

# General error
exit 1

# Custom error codes
exit 2  # File not found
exit 3  # Permission denied
exit 4  # Invalid input
```

### Error Handling Functions
```bash
# Error function
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Usage function
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -f FILE    Specify input file"
    echo "  -v         Verbose mode"
    echo "  -h         Show this help"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    if ! command -v required_command &> /dev/null; then
        error_exit "required_command is not installed"
    fi
    
    if [ ! -f "$config_file" ]; then
        error_exit "Config file not found: $config_file"
    fi
}
```

### Trap for Cleanup
```bash
#!/bin/bash

# Cleanup function
cleanup() {
    local status=$?
    echo "Cleaning up..."
    rm -f -- "$temp_file"
    exit "$status"
}

# Create temporary file
temp_file=$(mktemp) || exit 1

# Register cleanup only after creating the file
trap cleanup EXIT

# Your script logic here
echo "Processing..."
```

---

## Text Processing

### String Manipulation
```bash
# String length
str="Hello World"
echo "Length: ${#str}"

# Substring
echo "First 5 chars: ${str:0:5}"
echo "From position 6: ${str:6}"

# String replacement
echo "Replace 'World' with 'Linux': ${str/World/Linux}"
 
# Remove prefix/suffix
filename="file.txt"
echo "Without extension: ${filename%.txt}"
echo "Without 'file.' prefix: ${filename#file.}"
```

### Pattern Matching
```bash
# Check if string starts with pattern
if [[ "$string" =~ ^[A-Z] ]]; then
    echo "Starts with uppercase"
fi

# Extract regex groups
if [[ "$email" =~ ^([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$ ]]; then
    username="${BASH_REMATCH[1]}"
    domain="${BASH_REMATCH[2]}"
    echo "Username: $username"
    echo "Domain: $domain"
fi
```

---

## Advanced Features

### Associative Arrays
```bash
# Declare associative array
declare -A config

# Set values
config["host"]="localhost"
config["port"]="8080"
config["user"]="admin"

# Access values
echo "Host: ${config[host]}"
echo "Port: ${config[port]}"

# Iterate through keys
for key in "${!config[@]}"; do
    echo "$key: ${config[$key]}"
done
```

### Process Substitution
```bash
# Compare two files
diff <(sort file1.txt) <(sort file2.txt)

# Process output
while read line; do
    echo "Processing: $line"
done < <(grep "pattern" file.txt)
```

### Here Documents
```bash
# Create configuration file
cat > config.conf << 'EOF'
[server]
host = localhost
port = 8080
user = admin

[database]
host = db.example.com
port = 5432
EOF
```

---

## Best Practices

### Script Organization
```bash
#!/bin/bash

# 1. Shebang and header
# 2. Configuration and constants
# 3. Function definitions
# 4. Main script logic
# 5. Error handling

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.conf"
LOG_FILE="$SCRIPT_DIR/script.log"

# Constants
readonly MAX_RETRIES=3
readonly TIMEOUT=30

# Functions
setup_logging() {
    : # Replace with logging setup
}

validate_input() {
    : # Replace with input validation
}

process_data() {
    : # Replace with processing logic
}

# Main logic
main() {
    setup_logging
    validate_input "$@"
    process_data
}

# Call main
main "$@"
```

### Security Considerations
```bash
# Use quotes around variables
echo "$variable"  # Good
echo $variable    # Bad

# Use a complete test; [ ] also works for this equality check
if [[ "$var" = "value" ]]; then
    printf '%s\n' "Matched"
fi

# Validate input
if [[ ! "$1" =~ ^[0-9]+$ ]]; then
    error_exit "Invalid number: $1"
fi

# Use read -r for input
read -r user_input

# Quote file arguments directly; do not use shell-escaped text as a filename
printf 'Input: %s\n' "$user_input"
```

### Performance Tips
```bash
# Use local variables in functions
function process() {
    local var="$1"  # Keep function state separate from the caller
}

# Use built-in commands when possible
# Use printf instead of echo for complex output
printf "User: %s, Age: %d\n" "$user" "$age"

# Use command substitution when you need its output
# result=$(command) removes trailing newlines; do not add temp files just for speed

# Use arrays for multiple values
# Instead of: var1, var2, var3
# Use: array=(var1 var2 var3)
```

---

## Common Patterns

### Configuration File Parser

This small parser accepts plain `key=value` lines, not shell syntax or a full INI
format. Quotes remain literal; there is no variable expansion or inline-comment
handling. Do not `source` a configuration file from an untrusted source.

```bash
declare -A config=()

parse_config() {
    local config_file="$1"
    
    while IFS='=' read -r key value || [[ -n "$key$value" ]]; do
        
        # Remove leading/trailing whitespace
        key="${key#"${key%%[![:space:]]*}"}"
        key="${key%"${key##*[![:space:]]}"}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"

        # Skip blank lines and full-line comments, including indented ones
        [[ -z $key || $key == \#* ]] && continue
        
        # Store in associative array
        config["$key"]="$value"
    done < "$config_file"
}
```

### Logging Framework
```bash
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        DEBUG)
            echo "[$timestamp] DEBUG: $message" >> "$LOG_FILE"
            ;;
        INFO)
            echo "[$timestamp] INFO: $message" | tee -a "$LOG_FILE"
            ;;
        WARN)
            printf '[%s] WARN: %s\n' "$timestamp" "$message" | tee -a "$LOG_FILE" >&2
            ;;
        ERROR)
            printf '[%s] ERROR: %s\n' "$timestamp" "$message" | tee -a "$LOG_FILE" >&2
            ;;
    esac
}
```

### Retry Mechanism
```bash
retry() {
    if (( $# < 2 )); then
        printf '%s\n' 'Usage: retry POSITIVE_COUNT command [args...]' >&2
        return 2
    fi
    local max_attempts="$1"
    shift
    local attempt=1

    if [[ ! "$max_attempts" =~ ^[1-9][0-9]*$ ]] || (( $# == 0 )); then
        printf '%s\n' 'Usage: retry POSITIVE_COUNT command [args...]' >&2
        return 2
    fi
    
    while [ $attempt -le $max_attempts ]; do
        if "$@"; then
            return 0
        else
            echo "Attempt $attempt failed. Retrying..."
            attempt=$((attempt + 1))
            if (( attempt <= max_attempts )); then
                sleep 1
            fi
        fi
    done
    
    echo "Command failed after $max_attempts attempts"
    return 1
}
```

For example, `retry 3 curl --fail --max-time 5 https://example.com` preserves each
argument. Retry only operations that are safe to repeat. This fixed-delay helper
is for small local scripts, not a production retry policy; it does not add
exponential backoff or jitter. A function run as an `if` condition must handle its
own failures explicitly rather than relying on `set -e`.

## Further reading

- [Bash manual: functions and local variables](https://www.gnu.org/software/bash/manual/html_node/Shell-Functions.html)
- [Bash manual: quoting](https://www.gnu.org/software/bash/manual/html_node/Quoting.html)
- [Bash manual: traps](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html)
- [ShellCheck](https://www.shellcheck.net/): catches many shell mistakes, but does not prove a script is safe.
