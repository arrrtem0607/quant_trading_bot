import secrets
import requests
import logging
from eth_account import Account
from web3 import Web3

logger = logging.getLogger(__name__)

class BSCWalletClient:
    def __init__(self, rpc_url: str, bscscan_api_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.api_key = bscscan_api_key
        Account.enable_unaudited_hdwallet_features()
        logger.info("🔗 BSCWalletClient инициализирован с RPC %s", rpc_url)

    @staticmethod
    def create_wallet() -> dict:
        """Создание нового кошелька"""
        private_key = "0x" + secrets.token_hex(32)
        account = Account.from_key(private_key)
        logger.info("🆕 Новый кошелёк создан: %s", account.address)
        return {
            "address": account.address,
            "private_key": private_key
        }

    def get_token_transactions(self, address: str, token_contract: str = None) -> list:
        """Получение входящих токен-транзакций по адресу"""
        logger.debug("📥 Запрос транзакций для адреса %s", address)
        url = "https://api.bscscan.com/api"
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "startblock": 1,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": self.api_key
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("status") != "1":
                logger.warning("⚠️ Ошибка ответа от BscScan: %s", data.get("message"))
                return []

            result = data.get("result", [])
            if token_contract:
                filtered = [
                    tx for tx in result
                    if tx["contractAddress"].lower() == token_contract.lower()
                    and tx["to"].lower() == address.lower()
                ]
                logger.info("🔍 Найдено %d входящих транзакций по токену %s", len(filtered), token_contract)
                return filtered

            logger.info("🔍 Найдено %d транзакций без фильтра по токену", len(result))
            return result
        except Exception as e:
            logger.exception("❌ Ошибка при запросе к BscScan: %s", e)
            return []

    def get_balance(self, address: str) -> float:
        """Получение BNB-баланса"""
        try:
            checksummed = self.w3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(checksummed)
            balance = self.w3.from_wei(balance_wei, 'ether')
            logger.info("💰 Баланс %s: %.6f BNB", address, balance)
            return balance
        except Exception as e:
            logger.exception("❌ Ошибка при получении баланса: %s", e)
            return 0.0