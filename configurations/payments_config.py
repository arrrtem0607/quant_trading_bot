from configurations.reading_env import env

class PaymentsConfig:
    def __init__(self):
        self.__wallet_address: str = env("WALLET_ADDRESS")
        self.__bsc_api_key: str = env("BSC_API_KEY")
        self.__bsc_rpc_url: str = env("BSC_RPC_URL")
        self.__usdt_contract: str = env("USDT_CONTRACT_ADDR")
        self.__test_mode: bool = env("TEST_MODE", "false").lower() == "true"

    def get_wallet_address(self) -> str:
        return self.__wallet_address

    def get_bsc_api_key(self) -> str:
        return self.__bsc_api_key

    def get_bsc_rpc_url(self) -> str:
        return self.__bsc_rpc_url

    def get_usdt_contract(self) -> str:
        return self.__usdt_contract

    def is_test_mode(self) -> bool:
        return self.__test_mode
