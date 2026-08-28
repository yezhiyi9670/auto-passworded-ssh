#!/bin/sh
# Shim to Python script

APSSH_DIR=$(cd "$(dirname "$0")"/.. && pwd)
PASSWORDS_FILE=~/.ssh/apssh_passwords.yml
PASSWORDS_DIR=~/.ssh/apssh_passwords.d

passwords_args=( )
for file in "$PASSWORDS_FILE" "$PASSWORDS_DIR"/*.yml; do
    if [[ -f "$file" ]]; then
        passwords_args+=( "--passwords" "$file" )
    fi
done

python3 "$APSSH_DIR/helper/askpass.py" "${passwords_args[@]}" "$@"
exit $?
