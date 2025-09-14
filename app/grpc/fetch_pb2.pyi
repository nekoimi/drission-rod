from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FetchRequest(_message.Message):
    __slots__ = ("url", "timeout")
    URL_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    url: str
    timeout: int
    def __init__(
        self, url: _Optional[str] = ..., timeout: _Optional[int] = ...
    ) -> None: ...

class FetchResponse(_message.Message):
    __slots__ = ("success", "html", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    HTML_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    html: str
    error: str
    def __init__(
        self,
        success: bool = ...,
        html: _Optional[str] = ...,
        error: _Optional[str] = ...,
    ) -> None: ...
