import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from configurations import get_config
from database.controller.orm_instance import orm_instance as orm
from services.bsc.bsc_wallet_client import BSCWalletClient
from utils.logger import setup_logger
from bot.lexicon.lexicon_ru import LEXICON_RU

logger = setup_logger(__name__, level="INFO")

config = get_config()
bsc_client = BSCWalletClient(
    rpc_url=config.payments_config.get_bsc_rpc_url(),
    bscscan_api_key=config.payments_config.get_bsc_api_key()
)

WALLET_ADDRESS = config.payments_config.get_wallet_address()
USDT_CONTRACT = config.payments_config.get_usdt_contract()
IS_TEST_MODE = config.payments_config.is_test_mode()

bot = Bot(
    token=config.bot_config.get_token(),
    default=DefaultBotProperties(parse_mode="HTML")
)


async def process_transactions():
    pending = await orm.transactions.get_pending_transactions()
    if not pending:
        logger.info(LEXICON_RU["tx_no_pending"])
        return

    logger.info(f"🔍 {LEXICON_RU['tx_checking'].format(len(pending))}")

    try:
        if IS_TEST_MODE:
            logger.info("🧪 Тестовый режим активен")
            all_tx = []
            for db_tx in pending:
                fake_amount = int(db_tx.amount_usdt)
                fake_hash = f"0xFAKE123456789000000000000000000000000000000000000000000000000{fake_amount:03d}"
                all_tx.append({
                    "hash": fake_hash,
                    "to": WALLET_ADDRESS,
                    "value": str(fake_amount * 10 ** 18),
                    "contractAddress": USDT_CONTRACT
                })
        else:
            all_tx = bsc_client.get_token_transactions(
                WALLET_ADDRESS,
                token_contract=USDT_CONTRACT
            )
    except Exception as e:
        logger.exception(f"❌ {LEXICON_RU['tx_bscscan_error']}")
        return

    for db_tx in pending:
        matched = next((
            tx for tx in all_tx
            if tx["hash"].lower() == db_tx.tx_hash.lower()
            and tx["to"].lower() == WALLET_ADDRESS.lower()
            and float(tx["value"]) / 10 ** 18 >= float(db_tx.amount_usdt)
        ), None)

        if matched:
            logger.info(f"✅ {LEXICON_RU['tx_confirmed'].format(db_tx.tx_hash)}")
            await orm.transactions.confirm_transaction(db_tx.tx_hash)

            if db_tx.subscription_id:
                logger.info(f"📍 Готовим активацию подписки: subscription_id={db_tx.subscription_id}")
                await orm.subscriptions.activate_subscription(db_tx.subscription_id)
                logger.info(
                    f"🎟️ {LEXICON_RU['tx_subscription_activated'].format(db_tx.subscription_id, db_tx.user_id)}"
                )
            else:
                logger.warning(f"⚠️ Нет subscription_id у транзакции: {db_tx.tx_hash}")

            telegram_id = await orm.users.get_telegram_id_by_id(db_tx.user_id)
            logger.info(f"📨 Попытка отправки пользователю {telegram_id=} (tx: {db_tx.tx_hash})")

            if not telegram_id:
                logger.warning(f"⚠️ Telegram ID не найден для user_id={db_tx.user_id}")
                continue

            close_button = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=LEXICON_RU["tx_close_btn"], callback_data="close_tx_msg")]
                ]
            )

            try:
                await bot.send_message(
                    chat_id=telegram_id,
                    text=LEXICON_RU["tx_success_msg"].format(
                        tx=db_tx.tx_hash,
                        amount=db_tx.amount_usdt
                    ),
                    reply_markup=close_button
                )
                logger.info(f"✅ Уведомление отправлено пользователю {telegram_id}")
            except TelegramBadRequest as e:
                logger.error(f"❗ TelegramBadRequest при отправке пользователю {telegram_id}: {e}")
            except Exception as e:
                logger.exception(f"❌ Ошибка при отправке сообщения пользователю {telegram_id}")
        else:
            logger.warning(f"⛔ {LEXICON_RU['tx_not_found'].format(db_tx.tx_hash)}")


async def run():
    while True:
        try:
            await process_transactions()
        except Exception:
            logger.exception(LEXICON_RU["tx_loop_error"])
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run())
