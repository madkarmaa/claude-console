import json
import uuid
import mimetypes
from curl_cffi import requests
from typing import Any, Literal
from .utils import headers

class Client:

  def __init__(self) -> None:
    self.headers = headers()
    self.organization_id = self.get_organization_id()

  def get_organization_id(self) -> str:
    url = 'https://claude.ai/api/organizations'

    response = requests.get(url, headers = self.headers, impersonate = 'chrome110')

    # refresh headers here since the method is called in the constructor
    if not response.ok:
      self.headers = headers(force_user_refresh = True)
      self.organization_id = self.get_organization_id()
      response = requests.get(url, headers = self.headers, impersonate = 'chrome110')

    return response.json()[0]['uuid']

  def get_content_type(self, file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"

  def list_all_conversations(self) -> Any:
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations'
    response = requests.get(url, headers = self.headers, impersonate = 'chrome110')
    return response.json()

  def send_message(self, prompt: str, conversation_id: str) -> str | Literal[False]:
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}/completion'

    payload = json.dumps({
      'attachments': [], # later add attachments
      'files': [], # what does this do?
      'prompt': prompt,
      'rendering_mode': 'raw',
      'timezone': 'Europe/Berlin'
    })

    response = requests.post(url, headers = self.headers, data = payload, impersonate = 'chrome110')

    if not response.ok:
      return False

    conversation_data: list = self.chat_conversation_history(conversation_id)
    conversation_data = [msg for msg in conversation_data if msg['sender'] == 'assistant']

    last_message = sorted(conversation_data, key = lambda x: x['index'], reverse = True)[0]
    return last_message['text'].strip()

  def delete_conversation(self, conversation_id: str) -> bool:
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}'

    payload = json.dumps(f'{conversation_id}')
    response = requests.delete(url, headers = self.headers, data = payload, impersonate = 'chrome110')

    return response.ok

  def chat_conversation_history(self, conversation_id: str) -> Any:
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}'
    response = requests.get(url, headers = self.headers, impersonate = 'chrome110')
    return response.json()['chat_messages']

  def generate_uuid(self) -> str:
    random_uuid = uuid.uuid4()
    random_uuid_str = str(random_uuid)
    formatted_uuid = f'{random_uuid_str[0:8]}-{random_uuid_str[9:13]}-{random_uuid_str[14:18]}-{random_uuid_str[19:23]}-{random_uuid_str[24:]}'
    return formatted_uuid

  def create_new_chat(self) -> Any:
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations'
    uuid = self.generate_uuid()

    payload = json.dumps({'uuid': uuid, 'name': ''})
    response = requests.post(url, headers = self.headers, data = payload, impersonate = 'chrome110')

    return response.json()

  def delete_all_conversations(self) -> bool:
    conversations = self.list_all_conversations()
    deleted: list[bool] = []

    for conversation in conversations:
      conversation_id = conversation['uuid']
      deleted.append(self.delete_conversation(conversation_id))

    return all(deleted)

  def rename_chat(self, title: str, conversation_id: str) -> bool:
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}'

    payload = json.dumps({
        'name': f'{title}'
    })

    response = requests.put(url, headers = self.headers, data = payload, impersonate = 'chrome110')

    return response.ok