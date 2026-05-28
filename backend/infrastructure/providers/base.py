from abc import ABC, abstractmethod


class BaseDNSProvider(ABC):
    registry = {}
    
    def __init_subclass__(cls, type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if type:
            BaseDNSProvider.registry[type] = cls

    @abstractmethod
    def update_record(self, domain: str, ip: str) -> str:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    @classmethod
    def get_provider_schema(cls) -> dict:
        return {"fields": []}

    @classmethod
    def get_record_schema(cls) -> dict:
        return {"fields": []}