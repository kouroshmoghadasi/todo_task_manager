from __future__ import annotations

import json
import os
from typing import List


class CategoryManager:
    """
    Manages task categories with persistence to a JSON file.
    - Keeps a reserved "All" option for filtering (not persisted)
    - Provides add, rename, delete operations
    """

    def __init__(self, filename: str = "categories.json", defaults: List[str] | None = None) -> None:
        self.filename = filename
        self._user_categories: List[str] = []
        self._defaults = defaults or ["Personal", "Work", "School"]

    # ---------- Persistence ----------
    def load(self) -> None:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cats = data.get("categories", [])
                    self._user_categories = self._normalize_list(cats)
            except Exception:
                # Fallback to defaults on read error
                self._user_categories = list(self._defaults)
        else:
            # Initialize with defaults on first run
            self._user_categories = list(self._defaults)
            self.save()

        # Ensure at least one category available
        if not self._user_categories:
            self._user_categories = list(self._defaults)
            self.save()

    def save(self) -> None:
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump({"categories": self._user_categories}, f, ensure_ascii=False, indent=2)
        except Exception:
            # Ignore persistence errors silently
            pass

    # ---------- Accessors ----------
    def get_all_categories(self) -> List[str]:
        return ["All"] + list(self._user_categories)

    def get_task_categories(self) -> List[str]:
        return list(self._user_categories)

    # ---------- Mutations ----------
    def add_category(self, name: str) -> bool:
        name = self._clean(name)
        if not name or name.lower() == "all" or name in self._user_categories:
            return False
        self._user_categories.append(name)
        self._user_categories = sorted(self._user_categories)
        self.save()
        return True

    def rename_category(self, old: str, new: str, tasks: List[object]) -> bool:
        old = self._clean(old)
        new = self._clean(new)
        if not old or not new or new.lower() == "all":
            return False
        if new in self._user_categories and new != old:
            return False
        # Update tasks
        for t in tasks:
            try:
                if getattr(t, "category", None) == old:
                    setattr(t, "category", new)
            except Exception:
                continue
        # Update list
        try:
            idx = self._user_categories.index(old)
            self._user_categories[idx] = new
        except ValueError:
            # If old not found (already removed), append new
            if new not in self._user_categories:
                self._user_categories.append(new)
        self._user_categories = sorted(self._user_categories)
        self.save()
        return True

    def delete_category(self, name: str, replacement: str, tasks: List[object]) -> bool:
        name = self._clean(name)
        replacement = self._clean(replacement)
        if not name or name.lower() == "all":
            return False
        # Apply reassignment first
        for t in tasks:
            try:
                if getattr(t, "category", None) == name:
                    setattr(t, "category", replacement)
            except Exception:
                continue
        # Remove from list
        try:
            self._user_categories.remove(name)
        except ValueError:
            pass
        # Ensure replacement exists
        if replacement and replacement not in self._user_categories and replacement.lower() != "all":
            self._user_categories.append(replacement)
        self._user_categories = sorted(self._user_categories)
        self.save()
        return True

    # ---------- Helpers ----------
    @staticmethod
    def _clean(val: str | None) -> str:
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

    def __init__(self):
        # در این پیاده‌سازی ساده دسته‌بندی‌ها در حافظه نگهداری می‌شوند
        self.categories = []

    def add_category(self, name):
        """افزودن دسته‌بندی جدید در صورت وجود نداشتن"""
        if name not in self.categories:
            self.categories.append(name)
            return True
        return False

    def remove_category(self, name):
        """حذف دسته‌بندی در صورت وجود"""
        if name in self.categories:
            self.categories.remove(name)
            return True
        return False

    def get_categories(self):
        """برگرداندن لیست دسته‌بندی‌ها (برای سازگاری با تست‌ها)"""
        return list(self.categories)

    # نام مستعار سازگاری
    def list_categories(self):
        return self.get_categories()

    def clear_categories(self):
        """پاک کردن همه دسته‌بندی‌ها (برای استفاده در تست‌ها)"""
        self.categories = []


