from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="<== Фото", callback_data="change_prev"
    )
    builder.button(
        text="В избранное", callback_data="add")

    builder.button(
        text="Фото ==> ", callback_data="change_next"
    )
    builder.adjust(3)
    return builder.as_markup()

def liked_page_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="<== Фото", callback_data="change_prev_del"
    )
    builder.button(
        text="Удалить", callback_data="delete")

    builder.button(
        text="Фото ==> ", callback_data="change_next_del"
    )
    builder.adjust(3)
    return builder.as_markup()

def adm_confirm_solo_update_prod():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Подтверждаю", callback_data="confirm_prod")

    builder.button(
        text="Не тот товар", callback_data="confirm_prod_back")

    builder.button(
        text="Меню", callback_data="confirm_prod_back_to_main")

    builder.adjust(3)
    return builder.as_markup()

def adm_confirm_bl():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Добавить в ЧС", callback_data="add_to_bl")

    builder.button(
        text="Убрать из ЧС", callback_data="del_from_bl")

    builder.button(
        text="Меню", callback_data="back_to_main")

    builder.adjust(3)
    return builder.as_markup()

def adm_solo_upd():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="<== Фото", callback_data="change_prev"
    )
    builder.button(
        text="Фото ==> ", callback_data="change_next"
    )
    builder.adjust(3)
    return builder.as_markup()

def mngr_msg_btn():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Промокод использован", callback_data="promo_is_activated"
    )
    builder.adjust(3)
    return builder.as_markup()

def back_mngr_msg_btn():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Вернуть промокод", callback_data="promo_is_deactivated"
    )

    builder.adjust(3)
    return builder.as_markup()

def adm_confirm_mail():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Подтверждаю", callback_data="confirm_mail")

    builder.button(
        text="Ввести снова", callback_data="confirm_mail_back")

    builder.button(
        text="Меню", callback_data="back_to_main")

    builder.adjust(3)
    return builder.as_markup()

def start_mail():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Начать рассылку", callback_data="start_mail")

    builder.button(
        text="Меню", callback_data="back_to_main")

    builder.adjust(3)
    return builder.as_markup()

def stop_mail():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Остановить рассылку", callback_data="stop_mail")

    builder.button(
        text="Меню", callback_data="back_to_main")

    builder.adjust(3)
    return builder.as_markup()