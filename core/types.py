from typing import TypedDict, Dict, Any

class ServiceResult(TypedDict):
    code: int
    message: str
    data: Dict[str, Any] | None