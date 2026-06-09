import threading
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

class MemoryDB:
    def __init__(self):
        self._lock = threading.RLock()
        self._data: Dict[str, Dict[str, Any]] = {
            "patients": {},
            "appointments": {},
            "charts": {},
            "images": {},
            "bills": {},
            "schedule": {},
            "doctors": {},
            "holidays": {},
            "insurance_catalog": {},
            "recall_logs": {},
            "chart_access_grants": {},
            "supplies": {},
            "swap_logs": {},
        }
        self._module_names = list(self._data.keys())

    @property
    def module_names(self) -> List[str]:
        return self._module_names

    def get_module_count(self, module: str) -> int:
        with self._lock:
            return len(self._data.get(module, {}))

    def acquire(self):
        self._lock.acquire()

    def release(self):
        self._lock.release()

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    def get_all(self, module: str) -> Dict[str, Any]:
        with self._lock:
            return dict(self._data.get(module, {}))

    def get_by_id(self, module: str, item_id: str) -> Optional[Any]:
        with self._lock:
            return self._data.get(module, {}).get(item_id)

    def add(self, module: str, item: Any, item_id: str = None) -> str:
        with self._lock:
            if item_id is None:
                item_id = str(uuid.uuid4())
            if module not in self._data:
                self._data[module] = {}
            self._data[module][item_id] = item
            return item_id

    def update(self, module: str, item_id: str, item: Any) -> bool:
        with self._lock:
            if module in self._data and item_id in self._data[module]:
                self._data[module][item_id] = item
                return True
            return False

    def delete(self, module: str, item_id: str) -> bool:
        with self._lock:
            if module in self._data and item_id in self._data[module]:
                del self._data[module][item_id]
                return True
            return False

    def find(self, module: str, predicate) -> List[tuple]:
        with self._lock:
            results = []
            for item_id, item in self._data.get(module, {}).items():
                if predicate(item):
                    results.append((item_id, item))
            return results

db = MemoryDB()
