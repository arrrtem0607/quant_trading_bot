LEXICON_RU = {
    # Старт и выбор языка
    "language_prompt": (
        "Quant Trading Bot — умный торговый бот для автоматической торговли на криптобиржах. "
        "Получайте стабильный доход без необходимости постоянного мониторинга рынка.\n\n"
        "Quant Trading Bot is a smart trading bot for automated trading on crypto exchanges. "
        "Earn stable income without the need for constant market monitoring.\n\n"
        "🌐 Выберите язык / Choose your language:"
    ),

    # Капча
    "captcha_question": "🤖 Решите пример:\n<b>{captcha_expr}</b>",
    "captcha_wrong": "❌ Неправильный ответ. Осталось попыток: {tries_left}",
    "captcha_failed": "🚫 Превышено число попыток. Попробуйте снова через {minutes} минут.",
    "captcha_blocked": "⏳ Вы временно заблокированы. Попробуйте позже.",


    # Главное меню
    "main_menu_title": "🏠 Главное меню",
    "menu_subs": "🔑 Витрина подписок",
    "menu_ref": "👥 Партнёрская программа",
    "menu_site": "🌐 Веб-сайт",
    "menu_support": "🛠 Техподдержка",
    "menu_exchanges": "📊 Биржи",

    # Отказ от ответственности
    "terms_text": (
        "⚠️ ПРЕДУПРЕЖДЕНИЕ О РИСКАХ\n\n"
        "Торговля криптовалютами сопряжена с высоким риском. Пожалуйста, ознакомьтесь с нашим "
        "отказом от ответственности по ссылке ниже.\n\n"
        "Используя этого бота, вы подтверждаете, что понимаете и принимаете риски, "
        "связанные с криптотрейдингом."
    ),
    "terms_read_btn": "📜 Прочитать условия",
    "terms_accept": "✅ Принять",
    "terms_url": "https://telegra.ph/UVEDOMLENIE-O-RISKAH-04-25",

    # Витрина подписок
    "subs_active_title": "📋 Активные подписки:",
    "subs_no_active": "❌ У вас пока нет активных подписок.",
    "subs_recommend_renew": "🔔 <i>Рекомендуем продлить</i>",
    "subs_until": "✅ До: <code>{end_date}</code>",

    "subs_store_title": "🛍 Витрина подписок:",
    "subs_product_line": "<b>{name}</b>\n{desc}\n💵 <code>{price} USDT</code> / {days} дней",

    "btn_extend": "💳 Продлить подписку",
    "btn_pay": "💰 Оплатить подписку",
    "btn_back": "🔙 Назад в меню",

    "subs_title": "📄 Активные подписки:",
    "btn_renew": "🔄 Продлить подписку",
    "btn_open_store": "🔑 Открыть витрину",
    "btn_back_to_menu": "🔙 Назад в меню",
    "store_select_product": "📦 Выберите продукт для подробной информации:",
    "subs_product_selected": "ℹ️ Вы выбрали продукт с ID {product_id}",

    "store_title": "📦 Витрина продуктов:",
    "store_product_button": "🔘 {item.name}",

    "subs_wallet_prompt": (
        "🧾 Вы выбрали подписку: <b>{product_name}</b>\n"
        "💰 Стоимость: <b>{amount_usdt} USDT</b>\n"
        "🔗 Сеть: <b>BNB Smart Chain (BSC) BEP-20</b>\n\n"
        "📤 Пожалуйста, переведите USDT на адрес:\n\n<code>{wallet_address}</code>\n\n"
        "После перевода нажмите кнопку ниже и введите хэш транзакции."
    ),
    "subs_paid_btn": "✅ Я оплатил",
    "subs_tx_prompt": "🔗 Введите хэш вашей транзакции (начинается с 0x):",
    "subs_tx_invalid": "❌ Неверный формат. Хэш должен начинаться с 0x и содержать 66+ символов.",
    "subs_tx_saved": "⏳ Хэш сохранён. Мы проверим транзакцию и уведомим вас.",
    "subs_user_not_found": "❌ Ошибка: пользователь не найден в базе.",
    "subs_back_btn": "🔙 Назад",

    "product_dashboard_title": "🧩 Управление подпиской",
    "product_dashboard_connected": "📡 Биржа подключена: {exchange}",
    "product_dashboard_not_connected": "🔌 Биржа не подключена",
    "product_dashboard_btn_connect": "🔗 Подключить биржу",

    # Детали продукта
    "product_detail_text": (
        "<b>{product.name}</b>\n"
        "{product.description}\n\n"
        "💰 Цена: <b>{product.price_usdt}</b> USDT\n"
        "⏳ Длительность: <b>{product.duration_days}</b> дней"
    ),
    "btn_subscribe": "📦 Оплатить подписку",
    "btn_renew_sub": "🔄 Продлить подписку",
    "btn_connect_exchange": "🔗 Подключить биржу",
    "btn_back_to_store": "🔙 Назад",



    "tx_no_pending": "⏳ Нет ожидающих транзакций",
    "tx_checking": "🔍 Проверка {0} транзакций...",
    "tx_test_mode": "🧪 Тестовый режим активен: используем фейковую транзакцию",
    "tx_bscscan_error": "❌ Не удалось получить транзакции от BscScan",
    "tx_confirmed": "✅ Подтверждено: tx_hash={0}",
    "tx_subscription_activated": "📦 Подписка {0} активирована для пользователя {1}",
    "tx_success_msg": "🎉 Ваша подписка активирована!\n\n<b>TX:</b> <code>{tx}</code>\n<b>Сумма:</b> {amount} USDT",
    "tx_close_btn": "❌ Закрыть",
    "tx_send_fail": "❗ Не удалось отправить сообщение пользователю",
    "tx_not_found": "⚠️ Транзакция {0} не найдена или неподтверждена",
    "tx_loop_error": "❌ Ошибка в цикле проверки транзакций",
    "exchange_select_prompt": "🔗 Выберите биржу для подключения:",
    "exchange_enter_uid": "Введите UID для биржи <b>{dialog_data[selected_exchange]}</b>:",
    "exchange_connected_msg": (
        "✅ Биржа <b>{exchange}</b> успешно подключена!\n\n"
        "👇 Выберите нужный пункт:"
    ),
    "exchange_manual_btn": "📘 Инструкция по подключению",
    "exchange_copy_btn": "📈 Перейти к копи-трейдингу",
    "exchange_register_btn": "👤 Регистрация новых пользователей",
    "exchange_back_btn": "🔙 Назад",
    "partners_title": "🤝 Официальные партнёры:",
    "support_message": "Свяжитесь с нашей поддержкой по кнопке ниже:",
    "support_open": "📞 Открыть чат поддержки",
}
