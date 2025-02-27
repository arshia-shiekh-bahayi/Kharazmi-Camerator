import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from redis import Redis


class MessageTypes(Enum):
    Error = "Error"
    Success = "Success"


@dataclass
class Message:
    message: str
    type: MessageTypes


class BaseMessageQueue(ABC):
    def __init__(self, key_id: str):
        self.key = key_id

    @abstractmethod
    def add_message(self, message: Message) -> None:
        raise NotImplementedError

    @abstractmethod
    def pop_message(self, count: int = 1) -> list[Message]:
        raise NotImplementedError


class RedisMessageQueue(BaseMessageQueue):
    def __init__(
        self, key_id: str, redis_host: str = "localhost", redis_port: int = 6379
    ):
        super().__init__(key_id=key_id)
        self.redis = Redis(host=redis_host, port=redis_port)

    def add_message(self, message: Message) -> None:
        _message = self._build_message(message)
        self.redis.lpush(self.key, _message)

    def pop_message(self, count: int = 1) -> list[Message]:
        messages = self.redis.rpop(self.key, count=count)
        if not messages:
            return []
        return [json.loads(m) for m in messages]

    @staticmethod
    def _build_message(message: Message) -> str:
        return json.dumps({"message": message.message, "type": message.type.value})

    def list_messages(self):
        return self.redis.lrange(self.key, 0, 10)
