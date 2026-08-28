import base64
from typing import Union
import sys
import pyotp
import argparse
import time
import random
import getpass
import ruyaml
import traceback
import re

def writelog(text, end='\n'):
    # stderr is displayed on the screen
    sys.stderr.write(text + end)
    sys.stderr.flush()

def writepass(text, end='\n'):
    # stdout is piped as the input to the password prompt
    sys.stdout.write(text + end)
    sys.stdout.flush()

def main():
    ap = argparse.ArgumentParser(
        description='SSH_ASKPASS responding utility for auto Password + Verification Code interactive login.'
    )
    ap.add_argument(
        '--passwords',
        action='append',
        type=str,
        default=[],
        help='Path to passwords files (should contain a dict[str, dict[str, str]] YAML file).'
    )
    ap.add_argument(
        'prompt',
        type=str,
        nargs='*',
        default=[],
        help='Prompt from SSH.'
    )
    a = ap.parse_args()

    passwords_paths = a.passwords
    passwords_data: dict[str, dict[str, str]] = {}
    for passwords_path in passwords_paths:
        try:
            data: dict[str, dict[str, str]] = ruyaml.load(open(passwords_path, 'r', encoding='utf-8'), Loader=ruyaml.SafeLoader)
            if data == None:
                writelog(f'AutoLogin WARNING: Empty passwords file "{passwords_path}".')
                continue
            passwords_data = { **passwords_data, **data }
        except Exception:
            writelog(f'AutoLogin WARNING: Failed to load passwords file "{passwords_path}".')
            traceback.print_exc(chain=False)
    if len(passwords_paths) == 0:
        writelog('AutoLogin WARNING: No passwords file provided for askpass helper.')
    prompt: str = ' '.join(a.prompt)

    # Example prompt: '(user@realhostname) Password:'
    match: Union[re.Match, None] = re.match(r'^\(([^@\(\)]+@)?([^@\(\)]+)\)(.*)$', prompt)
    secret: Union[str, None] = None
    server_identifier = ''
    if match != None:
        username: Union[str, None] = match.group(1)
        if username != None:
            username = username[:-1]
        realhostname: str = match.group(2)
        restprompt: str = match.group(3).strip()
        
        secret_dict: Union[dict[str, str], None] = None
        if username != None:
            server_identifier = username + '@' + realhostname
            secret_dict = passwords_data.get(server_identifier)
        if secret_dict == None:
            server_identifier = realhostname
            secret_dict = passwords_data.get(realhostname)
        if secret_dict == None:
            server_identifier = ''
            secret_dict = {}
        assert secret_dict != None

        secret: Union[str, None] = None
        for fragment, secret in secret_dict.items():
            if fragment.lower() in restprompt.lower():
                break
        else:
            secret = None

    CONTENTLESS_TYPES = [ 'prompt' ]
    DEFAULT_TYPE = 'prompt'
    assert DEFAULT_TYPE in CONTENTLESS_TYPES
    secret_type = DEFAULT_TYPE
    secret_encoding = ''
    secret_content = ''

    if secret != None:
        secret_frags = secret.split('/')
        secret_type = '/'.join(secret_frags[0:1])
        secret_encoding = '/'.join(secret_frags[1:2])
        secret_content = '/'.join(secret_frags[2:])

    if secret_type not in CONTENTLESS_TYPES:
        if secret_encoding == 'plain':
            pass
        elif secret_encoding == 'base64':
            secret_content = base64.b64decode(secret_content).decode('utf-8')
        else:
            writelog(f'AutoLogin WARNING: Unsupported secret encoding "{secret_encoding}".')
            secret_type = DEFAULT_TYPE

    def writelog_prompt():
        # Remove colon, avoid triggering VSCode password prompt
        writelog('[WAIT] ' + prompt.replace(':', '') + '...', end='\r')
    def writelog_secretinput(secret: str):
        writelog('[AUTO] ' + prompt.replace(':', '') + secret.rjust(3, ' '))

    if secret_type == 'password':
        writelog_prompt()
        time.sleep(random.random() * 2.0 + 0.5)  # Avoid suspicion due to too fast input
        writepass(secret_content + "\n")
        writelog_secretinput('********')
    elif secret_type == 'otp':
        writelog_prompt()
        time.sleep(random.random() * 2.5 + 2.5)  # Avoid suspicion due to too fast input
        totp = pyotp.TOTP(secret_content, digits=6)
        code = totp.now()
        writepass(code + "\n")
        writelog_secretinput(f'***{code[3:]}')
    else:
        if secret_type != 'prompt':
            writelog(f'AutoLogin WARNING: Unsupported secret type "{secret_type}".')
        writepass(getpass.getpass(prompt))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C
        writepass("\x03", end='')
        pass
    except:
        writepass("\x03", end='')
        traceback.print_exc()
