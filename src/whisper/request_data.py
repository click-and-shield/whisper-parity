from typing import cast, Optional, Union
import json

class RequestMessage:

    def __init__(self, role: str, content: str) -> None:
        self.role: str = role
        self.content: str = content

    @staticmethod
    def from_dict(message: dict[str, str]):
        if 'role' not in message:
            raise ValueError('Message must contain a role.')
        if 'content' not in message:
            raise ValueError('Message must contain a content.')
        return RequestMessage(role=message['role'], content=message['content'])

    @staticmethod
    def from_json(text: str):
        try:
            message: dict[str, str] = json.loads(text)
        except ValueError:
            raise ValueError("Invalid message content")
        return RequestMessage.from_dict(message)

    def to_dict(self) -> dict[str, str]:
        return {'role': self.role, 'content': self.content }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False, sort_keys=True)

class RequestData:

    def __init__(self, positions: list[int] = None, messages: Optional[list[RequestMessage]] = None) -> None:
        self.positions: Optional[list[int]] = positions
        self.messages: Optional[list[RequestMessage]] = messages

    @staticmethod
    def from_dict(data: dict[str, Union[list[int], list[dict[str, str]]]]):
        if 'positions' not in data:
            raise ValueError('Message must contain a positions.')
        if 'messages' not in data:
            raise ValueError('Message must contain messages')
        messages_data = cast(list[dict[str, str]], data['messages'])
        messages: list[RequestMessage] = []
        for message in messages_data:
            messages.append(RequestMessage.from_dict(message))
        return RequestData(positions=cast(list[int], data['positions']), messages=messages)

    @staticmethod
    def from_json(text: str):
        try:
            data: dict[str, Union[list[int], list[dict[str, str]]]] = json.loads(text)
        except ValueError:
            raise ValueError("Invalid message data (not valid JSON)")
        return RequestData.from_dict(data)

    def add_message(self, message: RequestMessage) -> None:
        if self.messages is None:
            self.messages = []
        cast(list[RequestMessage], self.messages).append(message)

    def to_dict(self) -> dict[str, Union[list[int], list[dict[str, str]]]]:
        messages: list[dict[str, str]] = []
        for message in cast(list[RequestMessage], self.messages):
            messages.append(message.to_dict())
        json_data: dict[str, Union[list[int], list[dict[str, str]]]] = {
            'positions': cast(list[int], self.positions),
            'messages': messages
        }
        return json_data

    def to_json(self) -> str:
        json_data: dict[str, Union[list[int], list[dict[str, str]]]] = self.to_dict()
        return json.dumps(json_data, indent=4, ensure_ascii=False, sort_keys=True)

    def messages_to_json(self) -> str:
        messages: list[dict[str, str]] = []
        for message in cast(list[RequestMessage], self.messages):
            messages.append(message.to_dict())
        return json.dumps(messages, indent=4, ensure_ascii=False, sort_keys=True)
