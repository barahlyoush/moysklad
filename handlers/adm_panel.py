#!/usr/bin/python
# -*- coding: utf-8 -*-
#vim:fileencoding=utf-8
import datetime

from aiogram import types, Router, F, Bot
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandObject,  Command
from aiogram.filters import CommandStart
import My_sklad, json,adm_main, main
from kbrd import reply, inline
from aiogram.types import FSInputFile
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import ReplyKeyboardRemove

adm_panel_router = Router()
class adm(StatesGroup):
    prod_code = State()

class black_list(StatesGroup):
    user_id = State()

class mails(StatesGroup):
    mail_id = State()

@adm_panel_router.message(CommandStart())
async def strt_cmd(message: types.Message):
    await message.reply('Добро пожаловать в админ панель бота. Выберите нужное действие',
                        reply_markup = reply.admin_main_kb)


"""Тотальное обновление"""
@adm_panel_router.message((F.text == 'Обновить базу'))
async def strt_cmd(message: types.Message):
    await message.answer('Вы уверены что хотите обновить базу? \nНе рекомендуется проводить чаще чем один раз в день',
                        reply_markup=reply.admin_conf_update)

@adm_panel_router.message((F.text == 'Подтверждаю, обновить базу'))
async def strt_cmd(message: types.Message):
    await message.answer(text='update запущен, дождитесь сообщения \"загрузка завершена\"')
    await My_sklad.update()
    await My_sklad.data_loader()
    await message.answer(text='Скачивание информации о товаре завершено, начинаю качать картинки')
    await My_sklad.img_loader()
    await My_sklad.img_count()
    await message.answer(text='загрузка завершена',
                        reply_markup=reply.admin_main_kb)

@adm_panel_router.message((F.text == 'Отмена, вернуться в меню'))
async def strt_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Добро пожаловать в админ панель бота. Выберите нужное действие',
                         reply_markup=reply.admin_main_kb)


"""Соло обновление"""


@adm_panel_router.message((F.text == 'Обновить товар'))
async def solo_upd(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(adm.prod_code)
    await message.answer(text='Отправьте артикул товара для обновления.',
                         reply_markup=reply.admin_back_to_menu)

@adm_panel_router.message((F.text == 'Ввести другой код'))
async def solo_upd(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(adm.prod_code)
    await message.answer(text='Отправьте артикул товара для обновления.',
                         reply_markup=reply.solo_admin_back_to_menu)

@adm_panel_router.message(adm.prod_code)
async def solo_upd(message: types.Message, state: FSMContext):

    await main.user_data_upd(message.from_user.id, 'page', '0')
    await state.update_data(prod_code=message.text)
    prod = await state.get_data()
    prod = await adm_main.check_prod(prod['prod_code'])
    await state.update_data(prod_code=prod)
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    if prod in product_data:
        capt = dict(product_data[prod])

        img = capt['img_path'] + 'img0.jpg'
        try:
            b = await message.answer_photo(photo=FSInputFile(img), caption=str('<b>' + capt['name']) + '</b>\n' + capt[
            'description'] + "\n\nЦена:" + str(capt['price']) + "\nАртикул:" + str(capt['article']),
                                       reply_markup=inline.adm_solo_upd(),
                                       parse_mode='HTML')
            await main.data_message(b.message_id, prod, 'img0.jpg')
        except:
            await message.answer(text=str('<b>' + capt['name']) + '</b>\n' + capt[
                'description'] + "\n\nЦена:" + str(capt['price']) + "\nАртикул:" + str(capt['article']),
                                       reply_markup=inline.adm_solo_upd(),
                                       parse_mode='HTML')

        await message.answer(text='Проверьте, выбран нужный товар?',
                             reply_markup=inline.adm_confirm_solo_update_prod())
    else:
        await message.answer(text='Товара с таким артикулом нет в базе бота.\n\nЕсли товар добален сегодня, то необходимо дождаться полного обновления базы, либо обновить базу вручную через главное меню (Не рекомендуется делать в рабочее время).',
                         reply_markup=reply.admin_back_to_menu)


@adm_panel_router.callback_query(F.data == "change_prev")
async def update_num_text_fab(callback: types.CallbackQuery):
    b = await main.get_img(callback.message.message_id,'prev')
    capt = await main.capt_pag(callback.message.message_id)
    photo = FSInputFile(b[1]+b[0])
    await callback.message.edit_media(InputMediaPhoto(media=photo,caption=capt, parse_mode='HTML'),reply_markup=inline.adm_solo_upd())
    await main.upd_data_message(callback.message.message_id, b[2], b[0])

@adm_panel_router.callback_query(F.data == "change_next")
async def update_num_text_fab(callback: types.CallbackQuery):
    b = await main.get_img(callback.message.message_id,'next')
    capt = await main.capt_pag(callback.message.message_id)
    photo = FSInputFile(b[1]+b[0])
    await callback.message.edit_media(InputMediaPhoto(media=photo,caption=capt, parse_mode='HTML'),reply_markup=inline.adm_solo_upd())
    await main.upd_data_message(callback.message.message_id, b[2], b[0])

@adm_panel_router.callback_query(F.data == "confirm_prod")
async def solo_upd(callback: types.CallbackQuery, state: FSMContext):
    prod = await state.get_data()
    try:
        await My_sklad.solo_update(prod['prod_code'])
        await callback.message.answer(text='загрузка завершена',
                            reply_markup = reply.admin_main_kb)
    except:
        await callback.message.answer(text='Сбой, нажмите \'Обновить товар\' заново',
                                      reply_markup=reply.admin_main_kb)
    await state.clear()

@adm_panel_router.callback_query(F.data == "confirm_prod_back")
async def solo_upd(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(adm.prod_code)
    await callback.message.answer(text='Введите артикул товара для обновления.',
                         reply_markup=reply.admin_back_to_menu)

@adm_panel_router.callback_query(F.data == "back_to_main")
async def solo_upd(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(text='Добро пожаловать в админ панель бота. Выберите нужное действие',
                                  reply_markup = reply.admin_main_kb)

@adm_panel_router.message((F.text == 'Черный список'))
async def bl_list(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Введите id пользователя',
                         reply_markup=reply.admin_back_to_menu)
    await state.set_state(black_list.user_id)

@adm_panel_router.message(black_list.user_id)
async def bl_list(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    id = await state.get_data()
    check = await adm_main.bl_action(id['user_id'],'check')
    if check == 1:
        await message.answer(text='Пользователь находится в черном списке и не может писать менеджеру.',
                                      reply_markup=inline.adm_confirm_bl())
    else:
        await message.answer(text='Пользователь, на данный момент, не находится в черном списке?.',
                                      reply_markup=inline.adm_confirm_bl())

@adm_panel_router.callback_query(F.data == "add_to_bl")
async def bl_list(callback: types.CallbackQuery, state: FSMContext):
    id = await state.get_data()
    await adm_main.bl_action(id['user_id'],'add')
    await callback.message.answer(text='Пользователь в черном списке',
                        reply_markup = reply.admin_main_kb)
    await state.clear()

@adm_panel_router.callback_query(F.data == "del_from_bl")
async def bl_list(callback: types.CallbackQuery, state: FSMContext):
    id = await state.get_data()
    await adm_main.bl_action(id['user_id'],'delete')
    await callback.message.answer(text='Пользователь не в черном списке',
                        reply_markup = reply.admin_main_kb)
    await state.clear()


@adm_panel_router.message((F.text == 'Помощь'))
async def help(message: types.Message):
    await message.answer(text='Что интересует?', reply_markup=reply.admin_help_kb)


@adm_panel_router.message((F.text == 'Краткое описание работы бота'))
async def help(message: types.Message):
    await message.answer(text='Краткое описание работы бота.\n\n'
                              'Бот выводит все товары, которые имеются в наличии, соответствующие критериям выбора пользователя. Товары и размеры, которых в наличии нет, выводиться не будут.\n\n'
                              'Робот каждый день в 01:00 обращается к Moysklad для обновления своей базы товаров.\n'
                              'После скачивания информации, бот формирует список из товаров и модификаций, которые имеются в наличии на момент обновления.\n'
                              'Т.е если товар закончился на складах, бот будет его выводить как имеющийся в наличии до 01:00. И наоборот, если товар только добавлен на склад, бот его будет отображать только после 01:00',
                         parse_mode='HTML',
                         reply_markup = reply.admin_main_kb)

@adm_panel_router.message((F.text == 'Описание кнопок'))
async def help(message: types.Message):
    await message.answer(text='<b> \"Обновить базу\" </b> \nЕсли очень нужно, то можно сделать полное обновление базы дынных (более раза в день не рекомендуется - ограничение от moysklad). При полном обновлении будет заново скачана вся информация о товарах, в том числе информация о наличии товаров на складе, кроме картинок. Если нужно обновить картинки в товаре, то можно воспользоваться кнопкой \"Обновить товар\"\n\n'
                              '<b> \"Черный список\" </b> \nКнопка позволяет добавить/удалить пользователя в черный список(ЧС), (например, если клиент спамит менеджеру). Если пользователь внесен в черный список, то он может смотреть товары, но после нажатия кнопки \"Связаться с менеджером\" ничего не произойдёт, сообщение менеджеру направлено не будет.\n'
                              'Для внесения/удаления из ЧС необходимо указать user_id пользователя (он будет указан в сообщении менеджеру).\n\n'
                              '<b> \"Обновить товар\" </b> \nКнопка обновляет информацию о товаре в базе данных бота: все изображения, имя, код, цена, описание. Кнопка может пригодиться, когда изменили информацию о товаре на складе (например, обнаружили опечатку или изменили/добавили изображения и нужно их обновить в боте).',
                         parse_mode='HTML',
                         reply_markup = reply.admin_main_kb)

@adm_panel_router.message(F.text=='@test')
async def test_size_cmd(message: types.Message):
    await adm_main.test(message.from_user.id)
    await message.answer('ok')

@adm_panel_router.message(F.text=='/users')
async def test_size_cmd(message: types.Message):
    with open('data/user_data.JSON', 'r') as file:
        data = json.load(file)
    await message.answer('Количество пользователей: '+ str(len(data)))

@adm_panel_router.message(F.text=='/numbers')
async def test_size_cmd(message: types.Message):
    usr_list = []
    with open('data/user_data.JSON', 'r') as file:
        data = json.load(file)
    for user in data:
        if 'number' in data[user]:
            usr_list.append(user)
    await message.answer('Количество номеров: '+ str(len(usr_list)))

@adm_panel_router.message(F.text=='/myself')
async def test_size_cmd(message: types.Message):
    try:
        with open('data/counter.JSON', 'r') as file:
            counter_data = json.load(file)
    except:
        counter_data = {}
    if "self_click" not in counter_data:
        await message.answer('Количество нажатий: 0')
    else:
        await message.answer('Количество нажатий: '+str(counter_data["self_click"]))


@adm_panel_router.message(F.text == 'Рассылка')
async def bl_list(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Введите id рассылки',
                         reply_markup=reply.admin_back_to_menu)
    await state.set_state(mails.mail_id)

@adm_panel_router.message(mails.mail_id)
async def bl_list(message: types.Message, state: FSMContext):
    mail_id = message.text
    progress = await adm_main.check_mail(mail_id)
    if progress == 0:
        await message.answer(text='Рассылка с таким id не найдена',
                             reply_markup=reply.admin_main_kb)
    else:
        await message.answer(text=progress,
                             reply_markup=reply.admin_main_kb)
