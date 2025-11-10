from __future__ import annotations

import json
import os
from typing import List, Optional


class CategoryManager:
    """
    Simple category manager with optional JSON persistence.
    """

    def __init__(self, filename: Optional[str] = "categories.json", defaults: Optional[List[str]] = None) -> None:
        self.filename = filename
        self._defaults = defaults or ["Personal", "Work", "School"]
        self._user_categories: List[str] = []
        if self.filename:
            self.load()
        else:
            self._user_categories = list(self._defaults)

    # Persistence
    def load(self) -> None:
        if not self.filename:
            self._user_categories = list(self._defaults)
            return
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cats = data.get("categories", [])
                    self._user_categories = self._normalize_list(cats) or list(self._defaults)
            except Exception:
                self._user_categories = list(self._defaults)
        else:
            self._user_categories = list(self._defaults)
            self.save()

    def save(self) -> None:
        if not self.filename:
            return
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump({"categories": self._user_categories}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # Accessors
    def get_all_categories(self) -> List[str]:
        return ["All"] + list(self._user_categories)

    def get_task_categories(self) -> List[str]:
        return list(self._user_categories)

    # Backwards-compatible names
    def get_categories(self) -> List[str]:
        return self.get_task_categories()

    def list_categories(self) -> List[str]:
        return self.get_task_categories()

    # Mutations
    def add_category(self, name: str) -> bool:
        name = self._clean(name)
        if not name or name.lower() == "all" or name in self._user_categories:
            return False
        self._user_categories.append(name)
        self._user_categories.sort()
        self.save()
        return True

    def remove_category(self, name: str) -> bool:
        name = self._clean(name)
        if not name or name.lower() == "all":
            return False
        try:
            self._user_categories.remove(name)
            self.save()
            return True
        except ValueError:
            return False

    def rename_category(self, old: str, new: str, tasks: Optional[List[object]] = None) -> bool:
        old = self._clean(old)
        new = self._clean(new)
        if not old or not new or new.lower() == "all":
            return False
        if new in self._user_categories and new != old:
            return False
        if tasks:
            for t in tasks:
                try:
                    if getattr(t, "category", None) == old:
                        setattr(t, "category", new)
                except Exception:
                    continue
        try:
            idx = self._user_categories.index(old)
            self._user_categories[idx] = new
        except ValueError:
            if new not in self._user_categories:
                self._user_categories.append(new)
        self._user_categories.sort()
        self.save()
        return True

    def delete_category(self, name: str, replacement: str = "", tasks: Optional[List[object]] = None) -> bool:
        name = self._clean(name)
        replacement = self._clean(replacement)
        if not name or name.lower() == "all":
            return False
        if tasks:
            for t in tasks:
                try:
                    if getattr(t, "category", None) == name:
                        setattr(t, "category", replacement)
                except Exception:
                    continue
        try:
            self._user_categories.remove(name)
        except ValueError:
            pass
        if replacement and replacement.lower() != "all" and replacement not in self._user_categories:
            self._user_categories.append(replacement)
        self._user_categories.sort()
        self.save()
        return True

    # Utilities
    def clear_categories(self) -> None:
        self._user_categories = []
        self.save()

    @staticmethod
    def _clean(val: Optional[str]) -> str:
        return (val or "").strip()

    @staticmethod
    def _normalize_list(values: List[str]) -> List[str]:
        seen = set()
        normalized: List[str] = []
        for v in values:
            v2 = (v or "").strip()
            if not v2 or v2.lower() == "all" or v2 in seen:
                continue
            normalized.append(v2)
            seen.add(v2)
        return normalized


