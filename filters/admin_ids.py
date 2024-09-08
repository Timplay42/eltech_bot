from aiogram.filters import Filter
from aiogram import types


# Фильтр, который проверяет на наличие админ-прав
class AdminIdsFilter(Filter):
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in self.admin_ids
