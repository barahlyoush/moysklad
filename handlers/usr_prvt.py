import json

import main
import datetime
import asyncio
import os

from aiogram import types, Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandObject,  Command
from aiogram.filters import CommandStart
from kbrd import reply, inline
from aiogram.types import ReplyKeyboardRemove,ErrorEvent
from aiogram.types import FSInputFile
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup,State
from dotenv import find_dotenv,load_dotenv
load_dotenv(find_dotenv())

from midlware.isadmin import adm_list

usr_prvt_router = Router()
manager = str(os.getenv('MANAGER'))
mngr_contact_chat_id = os.getenv('CONTACT_CHAT_ID')
mngr_contact_msg_id = os.getenv('CONTACT_MESSAGE_ID')

class check_sizes(StatesGroup):
    pod_grud = State()
    grud = State()

class mail_id(StatesGroup):
    id = State()

class mailing(StatesGroup):
    mail_message = State()

async def check_class(user):
    with open('data/user_data.JSON') as file:
        user_data = json.load(file)
    clas = user_data[str(user)].get('class')
    return clas

async def main_kb(user_id,kb):
    if kb == 'main':
        if user_id in adm_list:
            return reply.adm_main_menu_kb
        else:
            return reply.main_menu_kb
    if kb == 'promo':
        if user_id in adm_list:
            return reply.adm_promobot_main_menu_kb
        else:
            return reply.promobot_main_menu_kb

async def output_data(message, clas):
    await main.user_data_upd(message.from_user.id, 'class', clas)
    await main.user_data_upd(message.from_user.id, 'page', '0')
    path_data = await main.check_selected_path(message.from_user.id)
    await message.answer(text= path_data[1]+' --> Размер: '+path_data[2],
        reply_markup=reply.ReplyKeyboardRemove())
    await main.filter_parsing(message.from_user.id)
    output_list = await main.output_list(message.from_user.id)
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    for n in output_list:
        try:
            if await main.check_like(n, message.from_user.id) == False:
                kb = inline.get_keyboard_fab()
            if await main.check_like(n, message.from_user.id) == True:
                kb = inline.liked_page_kb()
            capt = dict(product_data[n])
            img = capt['img_path'] + 'img0.jpg'
            b = await message.answer_photo(photo=FSInputFile(img), caption=str('<b>' + capt['name']) + '</b>\n' + capt[
                'description'] + "\n\nЦена:" + str(capt['price']) + "\nАртикул:" + str(capt['article'] + '\n<b>[1/' + str(capt['img_count']) + ']</b>'), reply_markup=kb,
                                           parse_mode='HTML')
            await asyncio.sleep(1)
            await main.data_message(b.message_id, n, 'img0.jpg', [1, capt['img_count']] )
        except:
            capt = dict(product_data[n])
            with open('logs.txt','a') as file:
                file.write('\nТовар '+str(capt['article'])+' не прогрузился в каталоге')
    await message.answer(
        '<b>Для заказа нажмите \"Связаться с менеджером✉️\"\nДля выхода в главное меню нажмите \"Главное меню↩️\"</b>',
        reply_markup=reply.tovar_list_kb, parse_mode=ParseMode.HTML)
    await main.user_data_upd(message.from_user.id, 'status', 1)


@usr_prvt_router.message(CommandStart())
async def strt_cmd(message: types.Message):
    check_promobot = await main.check_newcomer(message.from_user.id)
    if check_promobot == 1:
        kb = await main_kb(message.from_user.id,'promo')
        promo_bot_img = FSInputFile('promo_bot.jpg')
        await message.answer_photo(photo=promo_bot_img, caption='Добро пожаловать в магазин нижнего белья 👙\n\n🎁По промокоду «БОТ» при первом заказе  — фирменная брендированная  косметичка в подарок.\n\nДля просмотра товаров нажмите на кнопку ==> Каталог\n\n🔗Наш основаной аккаунт \nПереходите, если еще не знакомы с нашим брендом. Все новинки, видеообзоры и классные розыгрыши там.\n\n\n___\n*при оформлении первого заказа, не забудьте назвать промокод.\n**промокод действует при покупке от 3000 рублей.\n***не суммируется с другими акциями и предложениями магазина.')
        await message.answer('Для активации промокода нажмите на кнопку ==> Активировать промокод',
                            reply_markup=kb)
    else:
        kb = await main_kb(message.from_user.id, 'main')
        await message.reply('Добро пожаловать в магазин. Для просмотра товаров нажмите на кнопку ==> Каталог👙', reply_markup = kb)
    await main.clear_user_product_list(message.from_user.id)

"""Кнопки - Главное меню"""
@usr_prvt_router.message(F.text == 'Каталог👙')
async def first_size_cmd(message: types.Message):
    await message.answer('Выберите категорию', reply_markup=reply.type_kb)


@usr_prvt_router.message(F.text == 'Моё избранное❤️')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    products_list = await main.liked_products(message.from_user.id)
    if products_list == []:
        await message.answer('Вы еще не добавили товар в \"Избранное\"', reply_markup=reply.liked_list_kb)
    else:
        with open('data/output_product_data.JSON') as file:
            product_data = json.load(file)
        output_list = []
        for n in products_list:
            if n in product_data:
                output_list.append(n)
        if output_list == []:
            await message.answer('Список избранного пуст', reply_markup=reply.liked_list_kb)
        else:
            for n in output_list:
                try:
                    if await main.check_like(n, message.from_user.id) == False:
                        kb = inline.get_keyboard_fab()
                    if await main.check_like(n, message.from_user.id) == True:
                        kb = inline.liked_page_kb()
                    capt = dict(product_data[n])
                    img = capt['img_path'] + 'img0.jpg'
                    b = await message.answer_photo(photo=FSInputFile(img),
                                                   caption=str('<b>' + capt['name']) + '</b>\n' + capt[
                                                       'description'] + "\n\nЦена:" + str(
                                                       capt['price']) + "\nАртикул:" + str(capt['article']+ '\n<b>[1/' + str(capt['img_count']) + ']</b>'),
                                                   reply_markup=kb,
                                                   parse_mode='HTML')
                    await asyncio.sleep(1)
                    await main.data_message(b.message_id, n, 'img0.jpg', [1, capt['img_count']] )
                except:
                    capt = dict(product_data[n])
                    with open('logs.txt', 'a') as file:
                        file.write('\nТовар ' + str(capt['article']) + ' не прогрузился в избранном')
        await message.answer('<b>Для заказа нажмите \"Связаться с менеджером✉️\"\nДля выхода в главное меню нажмите \"Главное меню↩️\"</b>', reply_markup=reply.liked_list_kb,parse_mode=ParseMode.HTML)
    await main.user_data_upd(message.from_user.id, 'status', 1)

#--------------------------Кнопки типа
@usr_prvt_router.message(F.text=='Одежда👚')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    await main.user_data_upd(message.from_user.id, 'тип', 'одежда')
    await message.answer('Выберите что Вас интересует', reply_markup=reply.cloth_class_kb)
    await main.user_data_upd(message.from_user.id, 'status', 1)

@usr_prvt_router.message(F.text=='Нижнее белье👙')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    await main.user_data_upd(message.from_user.id, 'тип', 'нижнее белье')
    await message.answer('Выберите что Вас интересует', reply_markup=reply.undw_class_kb)
    await main.user_data_upd(message.from_user.id, 'status', 1)



#--------------------------Кнопки цвета

@usr_prvt_router.message(F.text=='\"XS\"')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    clas = await check_class(message.from_user.id)
    await main.user_data_upd(message.from_user.id,'Размер','XS')
    await main.user_data_upd(message.from_user.id,'РазмерР','ХS')
    await output_data(message, clas)


@usr_prvt_router.message(F.text=='\"S\"')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    clas = await check_class(message.from_user.id)
    await main.user_data_upd(message.from_user.id,'Размер','S')
    await output_data(message, clas)


@usr_prvt_router.message(F.text=='\"M\"')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    clas = await check_class(message.from_user.id)
    await main.user_data_upd(message.from_user.id,'Размер','M')
    await main.user_data_upd(message.from_user.id,'РазмерР','М')
    await output_data(message, clas)


@usr_prvt_router.message(F.text=='\"L\"')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    clas = await check_class(message.from_user.id)
    await main.user_data_upd(message.from_user.id,'Размер','L')
    await output_data(message, clas)


@usr_prvt_router.message(F.text=='\"XL\"')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    clas = await check_class(message.from_user.id)
    await main.user_data_upd(message.from_user.id,'Размер','XL')
    await main.user_data_upd(message.from_user.id,'РазмерР','ХL')
    await output_data(message, clas)


@usr_prvt_router.message(F.text=='\"XXL\"')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    clas = await check_class(message.from_user.id)
    await main.user_data_upd(message.from_user.id,'Размер','XXL')
    await main.user_data_upd(message.from_user.id,'РазмерР','ХХL')
    await output_data(message, clas)


@usr_prvt_router.message(F.text=='\"XXXL\"')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    clas = await check_class(message.from_user.id)
    await main.user_data_upd(message.from_user.id,'Размер','XXXL')
    await main.user_data_upd(message.from_user.id,'РазмерР','ХХХL')
    await output_data(message, clas)


@usr_prvt_router.message(F.text=='\"XXXXL\"')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    clas = await check_class(message.from_user.id)
    await main.user_data_upd(message.from_user.id,'Размер','XXXXL')
    await main.user_data_upd(message.from_user.id,'РазмерР','ХХХХL')
    await output_data(message, clas)

#----------------------------------------------------Кнопки комплекта
#-----------Нижнее белье

async def class_usr_prvt(clas,message):
    await main.user_data_upd(message.from_user.id, 'class', clas)
    size = await main.check_size(clas, message.from_user.id)
    await message.answer('Выберите размер, в соответствии с таблицей ниже', reply_markup=reply.size_kb(size))
    if clas == 'Базовые комплекты и бюстгальтеры' or clas == 'Комплекты нижнего белья':
        await message.answer_photo(FSInputFile('bel_table.jpg'))
    if clas == 'Пижамы с брюками' or clas == 'Пижамы с шортами':
        await message.answer_photo(FSInputFile('table.jpg'))
    await main.user_data_upd(message.from_user.id, 'status', 1)


@usr_prvt_router.message(F.text=='Базовые бюстгальтеры❤️')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    await class_usr_prvt('Базовые бюстгальтеры', message)


@usr_prvt_router.message(F.text=='Сексуальный комплект❤️‍🔥')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    await class_usr_prvt('Комплекты нижнего белья', message)


#-----------Пижамы
@usr_prvt_router.message(F.text=='Пижамы с брюками👖')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    await class_usr_prvt('Пижамы с брюками', message)


@usr_prvt_router.message(F.text=='Пижамы с шортами🩳')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    await class_usr_prvt('Пижамы с шортами', message)

#----------------------------------------------------

@usr_prvt_router.message(F.text=='Главное меню↩️')
async def first_size_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    check_promobot = await main.check_newcomer(message.from_user.id)
    if check_promobot == 1:
        kb = await main_kb(message.from_user.id, 'promo')
        await message.answer('Для просмотра товаров нажмите на кнопку ==> Каталог👙', reply_markup=kb)
    else:
        kb = await main_kb(message.from_user.id, 'main')
        await message.answer('Для просмотра товаров нажмите на кнопку ==> Каталог👙', reply_markup=kb)
    await main.clear_user_product_list(message.from_user.id)


@usr_prvt_router.message(F.text=='Активировать промокод🎁')
async def first_size_cmd(message: types.Message):
    check_promobot = await main.check_newcomer(message.from_user.id)
    if check_promobot == 1:
        kb = await main_kb(message.from_user.id, 'promo')
        await message.answer('Промокод активирован',
                             reply_markup=kb)
    if check_promobot == 2:
        kb = await main_kb(message.from_user.id, 'main')
        await message.answer('Промокод уже использован',
                             reply_markup=kb)
@usr_prvt_router.message(check_sizes.pod_grud)
async def first_size_cmd(message: types.Message, state: FSMContext):
    await state.update_data(pod_grud=message.text)
    await state.set_state(check_sizes.grud)
    await message.answer(text='Введите обхват вашей ГРУДИ в сантиметрах')

@usr_prvt_router.message(check_sizes.grud)
async def first_size_cmd(message: types.Message, state: FSMContext):
    await state.update_data(grud=message.text)
    data = await state.get_data()
    await main.update_size_data(message.from_user.id,data)
    await state.clear()
    await message.answer('Спасибо за введенные данные!\nДля связи с менеджером нажмите \"Связаться с менеджером✉️\"',reply_markup=reply.after_enter_sizes)


async def mngr_msg(message, state, bot,action = 0):
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    check_bel_in_liked_list = await main.check_bel_in_liked_list(message.from_user.id)
    if check_bel_in_liked_list == 1:
        check_size_data = await main.check_size_data(message.from_user.id)
        if check_size_data == 1:
            article_list = await main.mngr_msg(message.from_user.id)
            sizes = await main.mngr_sizes_msg(message.from_user.id)
            await main.user_data_upd(message.from_user.id, 'status', 1)
            if action == 1:
                await bot.copy_message(chat_id=manager, from_chat_id=manager,
                                       message_id=user_data[str(message.from_user.id)].get('number_msg'))
            check_promobot = await main.check_newcomer(message.from_user.id)
            if check_promobot == 1:
                kb = await main_kb(message.from_user.id, 'promo')
                await message.answer('Ваш контакт направлен менеджеру, он свяжется с Вами в ближайшее время')
                await message.answer(
                    '❣️ Зарегистрируйтесь в нашей системе лояльности по этой ссылочке:\n\n\nКопите баллы и тратьте их на покупки\nНомер телефона нужно указать без 8 или +7 в начале🥰',
                    reply_markup=kb)
                if article_list == []:
                    msg = await bot.send_message(chat_id=manager,
                                           text='Список избранного пуст' + '\n\nuser_id пользователя: ' + str(
                                               message.from_user.id) + '\n\nНомер телефона: ' + user_data[
                                                    str(message.from_user.id)].get(
                                               'phone_number') + '\n_______________________________ ',
                                           reply_markup=inline.mngr_msg_btn())
                    await main.mngr_data_message(msg.message_id, message.from_user.id)
                else:
                    msg = await bot.send_message(chat_id=manager,
                                           text='⬆️Товары в избранном⬆️\n' + article_list + '\n\nОбхват под грудью = ' +
                                                sizes[0] + '\nОбхват груди = ' + sizes[
                                                    1] + '\n\nUser_id пользователя: ' + str(
                                               message.from_user.id) + '\n\nНомер телефона: ' + user_data[
                                                    str(message.from_user.id)].get(
                                               'phone_number') + '\n_______________________________ ',
                                           reply_markup=inline.mngr_msg_btn())
                    await main.mngr_data_message(msg.message_id,message.from_user.id)
            else:
                kb = await main_kb(message.from_user.id, 'main')
                await message.answer('Ваш контакт направлен менеджеру, он свяжется с Вами в ближайшее время')
                await message.answer(
                    '❣️ Зарегистрируйтесь в нашей системе лояльности по этой ссылочке:\n\n\nКопите баллы и тратьте их на покупки\nНомер телефона нужно указать без 8 или +7 в начале🥰',
                    reply_markup=kb)
                if article_list == []:
                    await bot.send_message(chat_id=manager,
                                           text='Список избранного пуст' + '\n\nuser_id пользователя: ' + str(
                                               message.from_user.id)+ '\n\nНомер телефона: ' + user_data[str(message.from_user.id)].get('phone_number')+'\n_______________________________ ')
                else:
                    await bot.send_message(chat_id=manager,
                                           text='⬆️Товары в избранном⬆️\n' + article_list + '\n\nОбхват под грудью = ' +
                                                sizes[0] + '\nОбхват груди = ' + sizes[
                                                    1] + '\n\nUser_id пользователя: ' + str(message.from_user.id)+ '\n\nНомер телефона: ' + user_data[str(message.from_user.id)].get('phone_number')+'\n_______________________________ ')
        if check_size_data == 0:
            await message.answer(
                'В списке избранного присутствует нижнее белье. Для более точного подбора, менеджеру понадобятся данные о размерах')
            await state.clear()
            await state.set_state(check_sizes.pod_grud)
            await message.answer(text='Введите обхват ПОД ГРУДЬЮ в сантиметрах', reply_markup=ReplyKeyboardRemove())

    if check_bel_in_liked_list == 0:
        article_list = await main.mngr_msg(message.from_user.id)
        if action == 1:
            await bot.copy_message(chat_id=manager, from_chat_id=manager,
                                   message_id=user_data[str(message.from_user.id)].get('number_msg'))
        check_promobot = await main.check_newcomer(message.from_user.id)
        if check_promobot == 1:
            kb = await main_kb(message.from_user.id, 'promo')
            await message.answer('Ваш контакт направлен менеджеру, он свяжется с Вами в ближайшее время')
            await message.answer(
                '❣️ Зарегистрируйтесь в нашей системе лояльности по этой ссылочке:\n\n\nКопите баллы и тратьте их на покупки\nНомер телефона нужно указать без 8 или +7 в начале🥰',
                reply_markup=kb)
            if article_list == []:
                await main.user_data_upd(message.from_user.id, 'status', 1)
                msg = await bot.send_message(chat_id=manager,
                                       text='Список избранного пуст' + '\n\nuser_id пользователя: ' + str(
                                           message.from_user.id) + '\n\nНомер телефона: ' + user_data[
                                                str(message.from_user.id)].get(
                                           'phone_number') + '\n_______________________________ ',
                                           reply_markup=inline.mngr_msg_btn())
                await main.mngr_data_message(msg.message_id, message.from_user.id)
            else:
                await main.user_data_upd(message.from_user.id, 'status', 1)
                msg = await bot.send_message(chat_id=manager,
                                       text='⬆️Товары в избранном⬆️\n' + article_list + '\n\nuser_id пользователя: ' + str(
                                           message.from_user.id) + '\n\nНомер телефона: ' + user_data[
                                                str(message.from_user.id)].get(
                                           'phone_number') + '\n_______________________________ ',
                                           reply_markup=inline.mngr_msg_btn())
                await main.mngr_data_message(msg.message_id, message.from_user.id)

        else:
            kb = await main_kb(message.from_user.id, 'main')
            await message.answer('Ваш контакт направлен менеджеру, он свяжется с Вами в ближайшее время')
            await message.answer(
                '❣️ Зарегистрируйтесь в нашей системе лояльности по этой ссылочке:\n\n\nКопите баллы и тратьте их на покупки\nНомер телефона нужно указать без 8 или +7 в начале🥰',
                reply_markup=kb)
            if article_list == []:
                await main.user_data_upd(message.from_user.id, 'status', 1)
                await bot.send_message(chat_id=manager, text='Список избранного пуст' + '\n\nuser_id пользователя: ' + str(
                    message.from_user.id)+ '\n\nНомер телефона: ' + user_data[str(message.from_user.id)].get('phone_number')+'\n_______________________________ ')
            else:
                await main.user_data_upd(message.from_user.id, 'status', 1)
                await bot.send_message(chat_id=manager,
                                       text='⬆️Товары в избранном⬆️\n' + article_list + '\n\nuser_id пользователя: ' + str(
                                           message.from_user.id)+ '\n\nНомер телефона: ' + user_data[str(message.from_user.id)].get('phone_number')+'\n_______________________________ ')


@usr_prvt_router.message(F.text=='Связаться с менеджером✉️')
async def first_size_cmds(message: types.Message, state: FSMContext, bot: Bot):
    await main.clear_user_product_list(message.from_user.id)
    await main.user_data_upd(message.from_user.id, 'status', 0)
    bl_check = await main.check_bl(message.from_user.id)
    if bl_check == 0:
        numb_check = await main.check_number(message.from_user.id)
        if numb_check == 1:
            await mngr_msg(message,state,bot,1)
        if numb_check == 0:
            await message.answer('Оставьте свой контакт для связи с менеджером', reply_markup=reply.number_kb)
    if bl_check == 1:
        pass
    if bl_check == 2:
        check_promobot = await main.check_newcomer(message.from_user.id)
        if check_promobot == 1:
            kb = await main_kb(message.from_user.id, 'promo')
            await message.answer('Добавьте товар в избранное. После этого нажмите кнопку снова',
                                 reply_markup=kb)
        else:
            kb = await main_kb(message.from_user.id, 'main')
            await message.answer('Добавьте товар в избранное. После этого нажмите кнопку снова',
                                 reply_markup=kb)
    await main.user_data_upd(message.from_user.id, 'status', 1)


@usr_prvt_router.message(F.text=='Написать менеджеру самостоятельно✍️')
async def first_size_cmd(message: types.Message,bot: Bot):
    await main.counter()
    await main.user_data_upd(message.from_user.id, 'status', 0)
    await bot.copy_message(chat_id=message.from_user.id,from_chat_id=mngr_contact_chat_id,message_id=int(mngr_contact_msg_id))
    check_promobot = await main.check_newcomer(message.from_user.id)
    if check_promobot == 1:
        kb = await main_kb(message.from_user.id, 'promo')
        await message.answer('В сообщении менеджеру просим  указать товар, размер и промокод (при наличии) самостоятельно 🌸')
        await message.answer('❣️ Зарегистрируйтесь в нашей системе лояльности по этой ссылочке:\n\n\nКопите баллы и тратьте их на покупки\nНомер телефона нужно указать без 8 или +7 в начале🥰',
                             reply_markup=kb)
    else:
        kb = await main_kb(message.from_user.id, 'main')
        await message.answer('В сообщении менеджеру просим  указать товар, размер и промокод (при наличии) самостоятельно 🌸')
        await message.answer('❣️ Зарегистрируйтесь в нашей системе лояльности по этой ссылочке:\n\n\nКопите баллы и тратьте их на покупки\nНомер телефона нужно указать без 8 или +7 в начале🥰',
                             reply_markup=kb)
    await main.clear_user_product_list(message.from_user.id)
    await main.user_data_upd(message.from_user.id, 'status', 1)


@usr_prvt_router.message(F.contact)
async def first_size_cmds(message: types.Message, state: FSMContext, bot: Bot):
    msg = await message.forward(chat_id=manager)
    await main.user_data_upd(message.from_user.id, 'phone_number', message.contact.phone_number)
    await main.user_data_upd(message.from_user.id, 'number_msg', msg.message_id)
    await main.user_data_upd(message.from_user.id, 'number', 1)
    await mngr_msg(message,state,bot)

@usr_prvt_router.message(F.text=='Больше товаров➕')
async def first_size_cmd(message: types.Message):
    await main.user_data_upd(message.from_user.id, 'status', 0)
    await main.filter_parsing(message.from_user.id)
    output_list = await main.output_list(message.from_user.id)
    if output_list == False:
        await message.answer(
            '<b>Товары по заданным параметрам закончились\n\nДля заказа нажмите \"Связаться с менеджером✉️\"\nДля выхода в главное меню нажмите \"Главное меню↩️\"</b>',
            reply_markup=reply.tovar_list_kb, parse_mode=ParseMode.HTML)
    else:
        with open('data/output_product_data.JSON') as file:
            product_data = json.load(file)
        for n in output_list:
            capt = dict(product_data[n])
            try:
                if await main.check_like(n, message.from_user.id) == False:
                    kb = inline.get_keyboard_fab()
                if await main.check_like(n, message.from_user.id) == True:
                    kb = inline.liked_page_kb()
                img = capt['img_path'] + 'img0.jpg'
                b = await message.answer_photo(photo=FSInputFile(img), caption=str('<b>' + capt['name']) + '</b>\n' + capt[
                    'description'] + "\n\nЦена:" + str(capt['price']) + "\nАртикул:" + str(capt['article']+ '\n<b>[1/' + str(capt['img_count']) + ']</b>'), reply_markup=kb,
                                               parse_mode='HTML')
                await asyncio.sleep(1)
                await main.data_message(b.message_id, n, 'img0.jpg', [1, capt['img_count']] )
            except:
                with open('logs.txt', 'a') as file:
                    file.write('\nТовар ' + str(capt['article']) + ' не прогрузился в пагинации каталога')
        await message.answer(
            '<b>Для заказа нажмите \"Связаться с менеджером✉️\"\nДля выхода в главное меню нажмите \"Главное меню↩️\"</b>',
            reply_markup=reply.tovar_list_kb, parse_mode=ParseMode.HTML)
        await main.user_data_upd(message.from_user.id, 'status', 1)

@usr_prvt_router.callback_query(F.data == "change_prev")
async def update_num_text_fab(callback: types.CallbackQuery):
    b = await main.get_img(callback.message.message_id,'prev')
    capt = await main.capt_pag(callback.message.message_id, 'prev')
    photo = FSInputFile(b[1]+b[0])
    await callback.message.edit_media(InputMediaPhoto(media=photo,caption=capt[0], parse_mode='HTML'),reply_markup=inline.get_keyboard_fab())
    await main.upd_data_message(callback.message.message_id, b[2], b[0],capt[1])


@usr_prvt_router.callback_query(F.data == "change_next")
async def update_num_text_fab(callback: types.CallbackQuery):
    b = await main.get_img(callback.message.message_id,'next')
    capt = await main.capt_pag(callback.message.message_id,'next')
    photo = FSInputFile(b[1]+b[0])
    await callback.message.edit_media(InputMediaPhoto(media=photo,caption=capt[0], parse_mode='HTML'),reply_markup=inline.get_keyboard_fab())
    await main.upd_data_message(callback.message.message_id, b[2], b[0],capt[1])


@usr_prvt_router.callback_query(F.data == "add")
async def update_num_text_fab(callback: types.CallbackQuery):
    a = await main.like_product(callback.message.message_id, callback.from_user.id)
    if a == False:
        await callback.answer(text='Товар уже в избранном', show_alert=True)
    else:
        await callback.answer(text='Товар добавлен в избранное',show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=inline.liked_page_kb())


@usr_prvt_router.callback_query(F.data == "change_prev_del")
async def update_num_text_fab(callback: types.CallbackQuery):
    a = await main.filter_parsing(callback.from_user.id)
    b = await main.get_img(callback.message.message_id,'prev')
    capt = await main.capt_pag(callback.message.message_id,'prev')
    photo = FSInputFile(b[1]+b[0])
    await callback.message.edit_media(InputMediaPhoto(media=photo, caption=capt[0], parse_mode='HTML'),
                                      reply_markup=inline.liked_page_kb())
    await main.upd_data_message(callback.message.message_id, b[2], b[0],capt[1])


@usr_prvt_router.callback_query(F.data == "change_next_del")
async def update_num_text_fab(callback: types.CallbackQuery):
    a = await main.filter_parsing(callback.from_user.id)
    b = await main.get_img(callback.message.message_id,'next')
    capt = await main.capt_pag(callback.message.message_id,'next')
    photo = FSInputFile(b[1]+b[0])
    await callback.message.edit_media(InputMediaPhoto(media=photo, caption=capt[0], parse_mode='HTML'),
                                      reply_markup=inline.liked_page_kb())
    await main.upd_data_message(callback.message.message_id, b[2], b[0],capt[1])


@usr_prvt_router.callback_query(F.data == "delete")
async def update_num_text_fab(callback: types.CallbackQuery):
    a = await main.unlike_product(callback.message.message_id, callback.from_user.id)
    if a == False:
        await callback.answer(text='Товар уже удален', show_alert=True)
    else:
        await callback.answer(text='Товар удален из избранного', show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=inline.get_keyboard_fab())


@usr_prvt_router.callback_query(F.data == "promo_is_activated")
async def update_num_text_fab(callback: types.CallbackQuery):
    capt = callback.message.text
    user = await main.check_mngr_msg(callback.message.message_id)
    await main.user_data_upd(user,"promo_bot",2)
    await callback.message.edit_reply_markup(reply_markup = inline.back_mngr_msg_btn())
    await callback.answer(text='Промокод использован', show_alert=True)

@usr_prvt_router.callback_query(F.data == "promo_is_deactivated")
async def update_num_text_fab(callback: types.CallbackQuery):
    capt = callback.message.text
    user = await main.check_mngr_msg(callback.message.message_id)
    await main.user_data_upd(user,"promo_bot",1)
    await callback.message.edit_reply_markup(reply_markup = inline.mngr_msg_btn())
    await callback.answer(text='Использованый промокод отозван', show_alert=True)



@usr_prvt_router.message(F.text=='Рассылка')
async def test_size_cmd(message: types.Message):
    if message.from_user.id in adm_list:

        await message.answer(text='Выберите действие',
                             reply_markup=reply.mail_menu)


@usr_prvt_router.message(F.text=='Добавить рассылку')
async def test_size_cmd(message: types.Message, state: FSMContext):
    if message.from_user.id in adm_list:
        await state.clear()
        await message.answer(text='Отправьте сообщение для рассылки',
                             reply_markup=reply.back_to_menu)
        await state.set_state(mailing.mail_message)


@usr_prvt_router.message(mailing.mail_message)
async def solo_upd(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(mail_message = message.message_id)
    mail = await state.get_data()
    await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id,
                           message_id=mail['mail_message'], reply_markup=inline.adm_confirm_mail())
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer(text='Проверьте сообщение. После подтверждения его нельзя будет редактировать')
    await state.clear()


@usr_prvt_router.callback_query(F.data == "confirm_mail")
async def solo_upd(callback: types.CallbackQuery, state: FSMContext):
    mail_id = await main.add_mail(callback.from_user.id, callback.message.message_id)
    await callback.message.answer(text='Рассылка добавлена, в базу данных. ID рассылки: '+ str(mail_id),
                                  reply_markup=reply.mail_menu)
    await state.clear()


@usr_prvt_router.callback_query(F.data == "confirm_mail_back")
async def solo_upd(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(mailing.mail_message)
    await callback.message.answer(text='Отправьте сообщение для рассылки',
                         reply_markup=reply.back_to_menu)


@usr_prvt_router.callback_query(F.data == "back_to_main")
async def solo_upd(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    check_promobot = await main.check_newcomer(callback.message.from_user.id)
    if check_promobot == 1:
        kb = await main_kb(callback.message.from_user.id, 'promo')
        await callback.message.answer('Для просмотра товаров нажмите на кнопку ==> Каталог👙', reply_markup=kb)
    else:
        kb = await main_kb(callback.message.from_user.id, 'main')
        await callback.message.answer('Для просмотра товаров нажмите на кнопку ==> Каталог👙', reply_markup=kb)
    await main.clear_user_product_list(callback.message.from_user.id)


@usr_prvt_router.message(F.text=='Запустить рассылку')
async def test_size_cmd(message: types.Message, state: FSMContext):
    if message.from_user.id in adm_list:
        await state.clear()
        await state.set_state(mail_id.id)
        await message.answer(text='Отправьте ID рассылки',
                             reply_markup=reply.back_to_menu)

@usr_prvt_router.message(mail_id.id)
async def solo_upd(message: types.Message, state: FSMContext, bot: Bot):
    if message.from_user.id in adm_list:
        await state.update_data(id = message.text)
        msg_id = await main.get_mail(message.text)
        if msg_id == 0:
            await message.answer(text='Рассылка с таким ID не найдена',reply_markup=reply.mail_menu)
        else:
            await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id,
                                message_id=msg_id, reply_markup=inline.start_mail())

@usr_prvt_router.callback_query(F.data == "start_mail")
async def solo_upd(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    mail_id = await state.get_data()
    mail_id = mail_id['id']
    mail_status = await main.get_status(mail_id)
    if mail_status == 0:
        await main.add_mail_start_date(mail_id, callback.from_user.id)
        from_chat = await main.chat_id(mail_id)
        await callback.message.answer('Рассылка запущена, посмотреть статус можно в админ-боте',reply_markup=reply.back_to_menu)
        await main.set_status(mail_id, 2)
        while mail_status != 1 and mail_status !=3:
            await asyncio.sleep(10)
            users_list = await main.get_users(mail_id)
            if users_list != []:
                for user in users_list:
                    if str(user) == str(from_chat):
                        pass
                    else:
                        try:
                            await bot.copy_message(chat_id=user, from_chat_id= await main.chat_id(mail_id),
                                                   message_id=await main.get_mail(mail_id))
                        except:
                            with open('logs.txt', 'a') as file:
                                data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                file.write('\n' + str(data_time) + '     Не удалось отправить сообщение пользователю '+user)
                    await asyncio.sleep(1)
                    mail_status = await main.get_status(mail_id)
            else:
                await main.set_status(mail_id,1)
                await state.clear()
    if mail_status == 1:
        await callback.message.answer(text='Рассылка уже была разослана.', reply_markup=reply.mail_menu)
        await state.clear()
    if mail_status == 2:
        await callback.message.answer(text='Рассылка уже запущена', reply_markup=inline.stop_mail())
    if mail_status == 3:
        await callback.message.answer(text='Рассылка остановлена. Зарегистрируйте новую рассылку.', reply_markup=reply.mail_menu)
        await state.clear()


@usr_prvt_router.callback_query(F.data == "stop_mail")
async def solo_upd(callback: types.CallbackQuery, state: FSMContext):
    mail_id = await state.get_data()
    mail_id = mail_id['id']
    await main.set_status(mail_id, 3)
    await callback.message.answer(text='Рассылка остановлена', reply_markup=reply.mail_menu)
    await state.clear()



@usr_prvt_router.error()
async def del_double_phpto(event: ErrorEvent,bot: Bot):
    message = event.update.message
    if str(event.exception) == 'Telegram server says - Bad Request: message to copy not found':

        await main.user_data_upd(message.from_user.id, 'number', 0)
        await main.user_data_upd(message.from_user.id, 'status', 1)
        await message.answer('Оставьте свой контакт для связи с менеджером', reply_markup=reply.number_kb)
        await bot.send_message(chat_id='',
                               text='Произошла ошибка message to copy not found')
    else:
        try:
            action = event.update.callback_query.data
        except:
            action = 'действие не известно'
        try:
            msg_id = event.update.callback_query.message.message_id
        except:
            msg_id = 'сообщение не известно'
        data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('logs.txt', 'a') as file:
            file.write('\n'+str(data_time)+'    '+str(msg_id)+'     '+str(action))
        try:
            message = event.message
            await main.user_data_upd(message.from_user.id, 'status', 1)
        except:pass



