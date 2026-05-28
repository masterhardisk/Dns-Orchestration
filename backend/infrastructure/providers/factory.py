from backend.infrastructure.providers.base import BaseDNSProvider

def build_provider(provider_data):
    cls = BaseDNSProvider.registry.get(provider_data["type"])
    return cls(**provider_data["credentials"])