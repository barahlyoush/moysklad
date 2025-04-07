from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Каталог👙'),
            KeyboardButton(text='Моё избранное❤️'),
            KeyboardButton(text='Связаться с менеджером✉️')
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Для просмотра товаров нажмите на кнопку ==> Каталог👙'
)


adm_main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Каталог👙'),
            KeyboardButton(text='Моё избранное❤️'),
            KeyboardButton(text='Связаться с менеджером✉️'),
            KeyboardButton(text='Рассылка')
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Для просмотра товаров нажмите на кнопку ==> Каталог👙'
)


promobot_main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Каталог👙'),
            KeyboardButton(text='Моё избранное❤️')
        ],
        [
            KeyboardButton(text='Связаться с менеджером✉️'),
            KeyboardButton(text='Активировать промокод🎁')
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Для просмотра товаров нажмите на кнопку ==> Каталог👙'
)


adm_promobot_main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Каталог👙'),
            KeyboardButton(text='Моё избранное❤️')
        ],
        [
            KeyboardButton(text='Связаться с менеджером✉️'),
            KeyboardButton(text='Активировать промокод🎁'),
            KeyboardButton(text='Рассылка')
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Для просмотра товаров нажмите на кнопку ==> Каталог👙'
)

promo_bot_manager_kb= ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Промокод использован')
        ]
    ],
    resize_keyboard = True,
)


def size_kb(
        btns,
        placeholder: str = None
):
    creat_kb = ReplyKeyboardBuilder()
    for btn in btns:
        creat_kb.add(KeyboardButton(text=btn))
    creat_kb.row(KeyboardButton(text='Главное меню↩️'))

    return creat_kb.as_markup(resize_keyboard=True, input_field_placeholder='Выберите размер')


type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Одежда👚'),
            KeyboardButton(text='Нижнее белье👙'),
            KeyboardButton(text='Главное меню↩️')
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Выберите класс белья'
)

undw_class_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Базовые бюстгальтеры❤️'),
            KeyboardButton(text='Сексуальный комплект❤️‍🔥'),
            KeyboardButton(text='Главное меню↩️'),
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Выберите класс белья'
)

cloth_class_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Пижамы с брюками👖'),
            KeyboardButton(text='Пижамы с шортами🩳'),
            KeyboardButton(text='Главное меню↩️')
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Выберите класс одежды'
)


tovar_list_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Главное меню↩️'),
            KeyboardButton(text='Связаться с менеджером✉️'),
            KeyboardButton(text='Больше товаров➕')
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Для выхода в главное меню, наберите /menu'
)

liked_list_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Главное меню↩️'),
            KeyboardButton(text='Связаться с менеджером✉️')
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Для заказа нажмите \"Связаться с менеджером✉️\"'
)

after_enter_sizes = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Связаться с менеджером✉️'),
        ]
    ],
    resize_keyboard = True,
    input_field_placeholder = 'Для заказа нажмите \"Связаться с менеджером✉️\"')

insert_size_data = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Указать данные📏'),
            KeyboardButton(text='Главное меню↩️')
        ]
    ],
    resize_keyboard = True
)


admin_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Обновить товар'),
            KeyboardButton(text='Черный список'),
            KeyboardButton(text='Обновить базу'),
            KeyboardButton(text='Рассылка'),
            KeyboardButton(text='Помощь')
        ]
    ],
    resize_keyboard = True)

admin_conf_update = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Подтверждаю, обновить базу'),
            KeyboardButton(text='Отмена, вернуться в меню')
        ]
    ],
    resize_keyboard = True)


back_to_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Главное меню↩️')
        ]
    ],
    resize_keyboard = True)


admin_back_to_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Отмена, вернуться в меню')
        ]
    ],
    resize_keyboard = True)

solo_admin_back_to_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Ввести другой код'),
            KeyboardButton(text='Отмена, вернуться в меню')
        ]
    ],
    resize_keyboard = True)

admin_help_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Краткое описание работы бота'),
            KeyboardButton(text='Описание кнопок')
        ]
    ],
    resize_keyboard = True)

number_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Направить контакт✉️',request_contact=True),
            KeyboardButton(text='Написать менеджеру самостоятельно✍️')
        ]
    ],
    resize_keyboard = True)

self_number_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Направить контакт✉️',request_contact=True),
            KeyboardButton(text='✅Согласен, напишу менеджеру самостоятельно✍️')
        ]
    ],
    resize_keyboard = True)

mail_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить рассылку'),
            KeyboardButton(text='Запустить рассылку'),
            KeyboardButton(text='Главное меню↩️')
        ]
    ],
    resize_keyboard = True
)

