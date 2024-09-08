"""
A module for config in the app.config package.
"""

from functools import lru_cache

from app.config.init_settings import InitSettings
from app.config.settings import Settings


@lru_cache
def get_init_settings() -> InitSettings:
    """
    Get init settings cached

    :return: The init settings instance
    :rtype: InitSettings
    """
    return InitSettings()


@lru_cache
def get_settings() -> Settings:
    """
    Get settings cached

    :return: The settings instance
    :rtype: Settings
    """
    return Settings()


init_setting: InitSettings = get_init_settings()
setting: Settings = get_settings()
