import importlib
import pkgutil
import backend.infrastructure.providers as pkg
from backend.infrastructure.providers.base import BaseDNSProvider


def load_providers():
    for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
        if module_name in {"base", "factory", "discovery"}:
            continue

        importlib.import_module(
            f"backend.infrastructure.providers.{module_name}"
        )

    return BaseDNSProvider.registry