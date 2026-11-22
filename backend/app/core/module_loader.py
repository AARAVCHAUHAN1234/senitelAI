"""Dynamic module loader. Scans backend/app/modules/*/module.py and registers each."""

import importlib
import os
import logging

from .settings import settings

logger = logging.getLogger(__name__)


def load_modules(app, ctx: dict) -> list[str]:
    """Discover and register all enabled modules.

    Each module must expose a ``register(app, ctx)`` function in its
    ``module.py`` file.  ``ctx`` contains: app, db_factory, event_bus,
    service_registry.

    Returns the list of module names that were successfully loaded.
    """
    modules_dir = os.path.join(os.path.dirname(__file__), "..", "modules")
    modules_dir = os.path.normpath(modules_dir)
    loaded: list[str] = []

    if not os.path.isdir(modules_dir):
        return loaded

    enabled = settings.enabled_module_list

    for name in sorted(os.listdir(modules_dir)):
        module_dir = os.path.join(modules_dir, name)
        module_file = os.path.join(module_dir, "module.py")

        if not os.path.isdir(module_dir) or not os.path.isfile(module_file):
            continue

        if "all" not in enabled and name not in enabled:
            logger.info("Module '%s' is not enabled, skipping", name)
            continue

        try:
            mod = importlib.import_module(f"backend.app.modules.{name}.module")
            if hasattr(mod, "register"):
                mod.register(app, ctx)
                loaded.append(name)
                logger.info("Loaded module '%s'", name)
            else:
                logger.warning("Module '%s' has no register() function", name)
        except Exception:
            logger.exception("Failed to load module '%s'", name)

    return loaded
