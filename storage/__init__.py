"""
storage package initialization
"""
from storage.storage_interface import StorageProvider
from storage.json_storage import JSONStorage

__all__ = ["StorageProvider", "JSONStorage"]
