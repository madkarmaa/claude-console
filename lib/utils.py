import os
import base64
import subprocess
import requests
import sys
import re
from colorama import Fore, Style

ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
COOKIES_PATH: str = os.path.normpath(os.path.join(ROOT_DIR, 'claude.enc.cookies'))
VERSION_PATH: str = os.path.normpath(os.path.join(ROOT_DIR, 'version'))

COMMANDS = [
    ['git', 'add', '.'],
    ['git', 'stash'],
    ['git', 'pull'],
    ['git', 'stash', 'pop']
]

def base64encode(s: str) -> str:
    return base64.b64encode(s.encode()).decode()

def base64decode(s: str) -> str:
    return base64.b64decode(s).decode()

def headers(is_json_request: bool = True, force_user_refresh: bool = False) -> dict[str, str]:
    cookies: str

    if not os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, 'x') as f:
            f.close()

    while True:
        with open(COOKIES_PATH, 'r') as f:
            cookies = f.read()

        if cookies and not force_user_refresh:
            cookies = base64decode(cookies)
            break

        else:
            print(f'{Fore.RED}SESSION COOKIES MISSING{Style.RESET_ALL}')
            cookies = str(input(f'{Fore.GREEN}Input cookies {Fore.YELLOW}>{Style.RESET_ALL} '))

            with open(COOKIES_PATH, 'w') as f:
                f.write(base64encode(cookies))

            if force_user_refresh:
                force_user_refresh = False

    headers =  {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{cookies}',
        'TE': 'trailers'
    }

    if is_json_request:
        headers['Content-Type'] = 'application/json'

    return headers

def win_add_to_user_path(new_path: str) -> bool:
    # PowerShell command to retrieve the current user PATH environment variable
    ps_get_command = '[Environment]::GetEnvironmentVariable("PATH", "User")'
    result = subprocess.run(['powershell', '-Command', ps_get_command], capture_output=True, text=True, check=True)
    current_path = result.stdout.strip()

    # Split the PATH into individual paths
    path_list = current_path.split(';')

    # Check if the new path is already in the PATH
    if new_path not in path_list:
        # Append the new path to the list of paths
        path_list.append(new_path)
        # Join the paths back into a single string
        new_path_string = ';'.join(path_list)
        # PowerShell command to update the PATH environment variable
        ps_set_command = f'[Environment]::SetEnvironmentVariable("PATH", "{new_path_string}", "User")'
        subprocess.run(['powershell', '-Command', ps_set_command], check=True)

        return True
    else:
        return False

def add_unix_alias(alias_name: str, command: str) -> bool:
    shell = os.environ.get('SHELL', '').split('/')[-1]
    home = os.path.expanduser('~')
    config_file = f'{home}/.{shell}rc' if shell in ['bash', 'zsh'] else f'{home}/.config/fish/config.fish'
    alias_line = f'alias {alias_name}=\'{command}\'\n'

    with open(config_file, 'a+') as f:
        f.seek(0)
        if not re.search(rf'alias\s+{re.escape(alias_name)}\s*=', f.read()):
            f.seek(0, 2)  # Move to the end of the file
            f.write(alias_line)
            return True
        else:
            return False

def check_for_updates() -> None:
    url = 'https://api.github.com/repos/madkarmaa/claude-console/commits'

    if not os.path.exists(VERSION_PATH):
        with open(VERSION_PATH, 'x') as f:
            f.close()

    online_last_commit_sha: str = requests.get(url).json()[0]['sha']
    local_commit_sha: str

    with open(VERSION_PATH, 'r') as f:
        local_commit_sha = f.read()

    if local_commit_sha == online_last_commit_sha:
        return

    with open(VERSION_PATH, 'w') as f:
        f.write(online_last_commit_sha)

    for command in COMMANDS:
        subprocess.run(command, shell = True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

    print(f'{Fore.GREEN}Update completed! Exiting to apply changes...{Style.RESET_ALL}')
    sys.exit(0)

def get_command(input_string: str, prefix: str) -> str:
    return input_string.split(' ')[0][len(prefix):]