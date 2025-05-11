from configurations.reading_env import env


class BotConfig:
    def __init__(self):
        self.__token: str = env("TOKEN")
        self.__developers_id: list[int] = env.list("DEVELOPER_IDS", subcast=int)
        self.__yandex_disk_token: str | None = env("YANDEX_DISK_TOKEN", default=None)

    def get_token(self) -> str:
        return self.__token

    def get_yandex_disk_token(self) -> str | None:
        return self.__yandex_disk_token

    def get_developers_id(self) -> list[int]:
        return self.__developers_id
