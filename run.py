import sys
import logging
import asyncio

from aiogram import Bot, Dispatcher

from config.config import load_config
from app.handlers import router
from app.admin_handlers import admin_router


config = load_config()# Подключение конфигурационного файла


bot = Bot(config.tg_bot.token)# Добавление токена бота
dp = Dispatcher()# Инициализация диспетчера
dp.include_routers(admin_router, router)# Добавление в диспетчер обработчиков сообщений


# Функция которая запускает бота и выводит в терминал данные с логов
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
