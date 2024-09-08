from dataclasses import dataclass

from environs import Env


# Описание класса тг-бота
@dataclass
class TgBot:
    token: str# Токен бота
    admin_ids: list[int]# Список айди админов


# Конфиг
@dataclass
class Config:
    tg_bot: TgBot


# Функция загрузки конфига, которая принимает данные из .env
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(token=env("BOT_TOKEN"), admin_ids=list(map(int, env.list("ADMIN_IDS")))))

