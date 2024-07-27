import os
from sys import platform
from colorama import Fore, Style
from lib.utils import win_add_to_user_path, add_unix_alias, ROOT_DIR

installed: bool = False

if platform == 'win32':
    installed = win_add_to_user_path(ROOT_DIR)
else:
    installed = add_unix_alias('claude_console', f'python3 {os.path.join(ROOT_DIR, "main.py")}')

if installed:
    print(f'{Fore.GREEN}Claude Console successfully installed! Usage: {Fore.CYAN}claude_console <[OPTIONAL] prompt>{Style.RESET_ALL}')
else:
    print(f'{Fore.YELLOW}Claude Console already installed! Skipping.{Style.RESET_ALL}')