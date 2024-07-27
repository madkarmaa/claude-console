import sys
import webbrowser
from argparse import ArgumentParser
from lib.client import Client
from lib.utils import check_for_updates
from colorama import Fore, Style
# https://stackoverflow.com/a/76833666
from rich.console import Console
from rich.markdown import Markdown

check_for_updates()

COMMAND_PREFIX = '!'

def get_command(input_string: str) -> str:
    return input_string.split(' ')[0][len(COMMAND_PREFIX):]

parser = ArgumentParser()
console = Console()
client = Client()

parser.add_argument('-o', '--open', '--web', action = 'store_true', help = 'Open the conversation in your default web browser', required = False)

args, remainder = parser.parse_known_args()
args = vars(args)

cli_prompt = remainder[0] if remainder else None
uuid: str = client.create_new_chat()['uuid']

if cli_prompt:
    if args['open']:
        webbrowser.open(f'https://claude.ai/chat/{uuid}', new = 0, autoraise = True)

    response = client.send_message(cli_prompt, uuid)

    if args['open']:
        sys.exit(0)

    if not response:
        print(f'{Fore.RED}Something went wrong!{Style.RESET_ALL}')
        client.delete_conversation(uuid)
        sys.exit(1)

    print()
    console.print(Markdown(f'{response}'))
    print()

    # client.delete_conversation(uuid)
    sys.exit(0)

print()
while True:
    prompt = str(input(f'{Fore.GREEN}>{Style.RESET_ALL} ')).strip()

    if not prompt:
        continue

    # execute commands
    if prompt.startswith(COMMAND_PREFIX):
        command = get_command(prompt)

        if command in ['quit', 'q', 'exit']:
            break

        elif command in ['open', 'o', 'web']:
            # https://stackoverflow.com/a/4217032
            webbrowser.open(f'https://claude.ai/chat/{uuid}', new = 0, autoraise = True)
            break

        else:
            pass

    response = client.send_message(prompt, uuid)

    if not response:
        print(f'{Fore.RED}Something went wrong!{Style.RESET_ALL}')
        client.delete_conversation(uuid)
        sys.exit(1)

    print()
    console.print(Markdown(f'{response}'))
    print()