from __future__ import annotations

from app.models.category import Category


class CategoryService:

    _CATEGORIES: list[Category] = [
        Category(
            id=1,
            name="Economy",
            description="Macroeconomic indicators",
        ),
    ]

    _BY_NAME: dict[str, Category] = {
        cat.name.upper(): cat for cat in _CATEGORIES
    }

    @classmethod
    def get_categories(cls) -> list[Category]:
        return list(cls._CATEGORIES)

    @classmethod
    def get_category(cls, name: str) -> Category:
        category = cls._BY_NAME.get(name.strip().upper())
        if category is not None:
            return category

        raise ValueError(f"Category '{name}' not found")
