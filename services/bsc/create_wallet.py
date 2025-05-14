from services.bsc.bsc_wallet_client import BSCWalletClient
from configurations import get_config

config = get_config()

client = BSCWalletClient(config.payments_config.get_bsc_rpc_url(), config.payments_config.get_bsc_api_key())
wallet = client.create_wallet()

print("📥 Адрес:", wallet["address"])
print("🛡 Приватный ключ:", wallet["private_key"])
