import asyncio
import json
import datetime

from midlware.isadmin import adm_list


async def check_prod(prod_code):
    prod_code = str(prod_code)
    with open('data/product_data.JSON') as file:
        product_data = json.load(file)
    for n in product_data:
        if product_data[n].get('article') == prod_code:
            return n

"""Черный список"""

async def bl_action(user_id,action):
    user_id = str(user_id)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    if action == 'add':
        if user_id in user_data:
            if user_data[user_id].get('black_list') != 1:
                user_data[user_id].update({'black_list': 1})
        else:
            user_data.update({user_id:{'black_list': 1}})

    if action == 'delete':
        if user_id in user_data:
            if user_data[user_id].get('black_list') != 0:
                user_data[user_id].update({'black_list': 0})

    if action == 'check':
        if user_id in user_data:
            if 'black_list' in user_data[user_id]:
                if user_data[user_id].get('black_list') == 1:
                    return 1
                else:return 0
            else:
                user_data[user_id].update({'black_list': 0})
                return 0
        else: return 0
    with open('data/user_data.JSON', 'w') as file:
        json.dump(user_data, file)

'''Очищаем список сообщений'''
async def check_count_msg():
    msg_list = []
    with open('data/message_data.JSON') as file:
        msg_data = json.load(file)
    msg_data_size = len(msg_data)
    count = msg_data_size - 200000
    if count > 0:
        for msg in msg_data:
            if count == 0:
                break
            else:
                msg_list.append(msg)
                count -= 1

        for msg in msg_list:
            msg_data.pop(msg)
        with open('data/message_data.JSON', 'w') as file:
            json.dump(msg_data, file)

async def check_mail(mail_id):
    with open('data/user_data.JSON', 'r') as file:
        users_data = json.load(file)
    users_count = len(users_data)
    try:
        with open('data/mails.JSON', 'r') as file:
            mails_data = json.load(file)
    except:
        mails_data = {}
    if mail_id not in mails_data:
        print(mail_id)
        print(mails_data)
        return 0
    else:
        count = len(mails_data[mail_id].get("send_user"))
        if 'date' in mails_data[mail_id]:
            start_date = mails_data[mail_id].get("date")
            create_date = mails_data[mail_id].get("create_date")
            return 'Создал рассылку - '+adm_list[int(mails_data[mail_id].get("creat_user_id"))]+ '\nДата создания - '+str(create_date)+ '\nЗапустил рассылку - '+adm_list[int(mails_data[mail_id].get("start_user_id"))]+ '\nДата запуска - '+str(start_date)+ '\nКоличество-во пользователей - '+str(count)+ '/'+str(users_count)
        else:
            create_date = mails_data[mail_id].get("create_date")
            return 'Создал рассылку - ' + adm_list[
                int(mails_data[mail_id].get("creat_user_id"))] +'\nДата создания - '+str(create_date)+ '\nЗапустил рассылку - Не запущено\nДата запуска - Не запущено\nКоличество-во пользователей - ' + str(count) + '/' + str(users_count)

async def test(user):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    if 'number' in user_data[user]:
        user_data[user].pop('number',None)
        with open('data/user_data.JSON', 'w') as file:
            json.dump(user_data, file)
async def logger(event):
    data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('logs.txt', 'a') as file:
        file.write('\n' + str(data_time) + '     Успешно проведён '+event)