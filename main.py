import asyncio
import json
import os
import datetime

resize_dict = {
    'одежда': {
        # 'XS': ['XS', '42'],
        'S': ['S', '42', '44'],
        'M': ['M', '44', '46'],
        'L': ['L', '48'],
        'XL': ['XL', '50'],
        # 'XXL': ['XXL', '52'],
        # 'XXXL': ['XXXL', '3XL'],
        # 'XXXXL': ['XXXXL', '4XL']
    },
    'нижнее белье': {
        'XS': ['XS', '70A', '70B', '70C'],
        'S': ['S', '70D', '75A', '75B', '75C'],
        'M': ['M', '75D', '80A', '80B', '80C'],
        'L': ['L', '75E', '80D', '85B', '85C'],
        'XL': ['XL', '80E', '85D', '85E', '90B', '90C'],
        'XXL': ['XXL', '85E', '90D', '95B', '95C'],
        'XXXL': ['XXXL', '95D', '95E'],
        'XXXXL': ['XXXXL']
    }
}

async def check_size(clas, user_id):
    size_range = {'XS':'\"XS\"', 'S':'\"S\"', 'M':'\"M\"', 'L':'\"L\"', 'XL':'\"XL\"', 'XXL':'\"XXL\"', 'XXXL':'\"XXXL\"', 'XXXXL':'\"XXXXL\"'}
    size_list = []
    output_size_list = []
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    selected_clas = user_data[str(user_id)].get('тип')
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    for prod in product_data:
        if product_data[prod].get('class') == clas:
            for mod in product_data[prod].get('mods'):
                for size in resize_dict[selected_clas]:
                    if product_data[prod].get('mods').get(mod).get('РАЗМЕР') in resize_dict[selected_clas].get(size):
                        if size not in size_list:
                            size_list.append(size)
    for size in size_range:
        if size in size_list:
            output_size_list.append(size_range[size])
    return output_size_list

"""Апдейт введенной пользователем информации"""
async def user_data_upd(user, key, meaning):
    user = str(user)
    try:
        with open('data/user_data.JSON', 'r') as file:
            data = json.load(file)
    except:
        data = {}
    key_meaning = {key: meaning}
    data.setdefault(user, key_meaning)
    data[user].update(key_meaning)
    with open('data/user_data.JSON', 'w') as file:
        json.dump(data, file)


'''Формирование листа с отфильтрованными товарами'''
async def filter_parsing(user):
    user = str(user)
    product_output_list = []
    no_size_list = []
    with open('data/user_data.JSON') as file:
        user_data = json.load(file)
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    condition = [user_data.get(user).get('Размер'), user_data.get(user).get('class'),
                 user_data.get(user).get('РазмерР'),user_data.get(user).get('тип')]

    for prod in product_data:
        if product_data[prod].get('class') == condition[1]:
            if product_data[prod].get('price') !=0:
                if product_data[prod].get('img_count') !=0:
                    for mod in product_data[prod].get('mods'):
                        a = product_data[prod].get('mods').get(mod)
                        if 'РАЗМЕР' in product_data[prod].get('mods').get(mod):
                            size = a['РАЗМЕР'].replace('Х','X').replace('В','B').replace('А','A').replace('С','C').replace('М','M')
                            if size in resize_dict[condition[3]].get(condition[0]):
                                if a['count'] > 0:
                                    if prod not in product_output_list:
                                        product_output_list.append(prod)
                        else:
                            if product_data[prod].get('name')+' - '+product_data[prod].get('article') not in no_size_list:
                                no_size_list.append(product_data[prod].get('name')+' - '+product_data[prod].get('article'))
    user_data[user].setdefault('list', product_output_list)

    with open('data/nosize.JSON', 'w') as file:
        json.dump(no_size_list, file)

    with open('data/user_data.JSON', 'w') as file:
        json.dump(user_data, file)
    return product_output_list


"""Вывод по 5 товаров"""
async def output_list(user):
    user = str(user)
    output_list = []
    with open('data/user_data.JSON', 'r') as file:
        data = json.load(file)
    page = int(data[user].get('page'))
    if page != -1:
        end_page = page + 5
        prod_list = data[user].get('list')
        while page < end_page:
            try:
                output_list.append(prod_list[page])
                page += 1
            except:
                end_page = -1
        data[user].update({'page':end_page})
        with open('data/user_data.JSON', 'w') as file:
            json.dump(data, file)
        return output_list
    else:
        return False

"""Очистка параметров выбора товара"""
async def clear_user_product_list(user):
    user = str(user)
    try:
        with open('data/user_data.JSON') as file:
            user_data = json.load(file)
    except:
        pass
    try:
        user_data[user].pop('list')
        with open('data/user_data.JSON', 'w') as file:
            json.dump(user_data, file)
    except:
        pass


"""Сохраняет информацию о том, какому пользователю принадлежит кнопка в сообщении менеджеру"""
async def mngr_data_message(message_id, user):

    message_id = str(message_id)
    try:
        with open('data/message_data.JSON') as file:
            data = json.load(file)
    except:
        data = {}
    data.update({message_id:user})
    with open('data/message_data.JSON', 'w') as file:
        json.dump(data, file)



"""Загружает словарь {id сообщения вывода товара:[продукт,img.jpg]}"""
async def data_message(message_id, product, img, img_count):
    message_id = str(message_id)
    try:
        with open('data/message_data.JSON') as file:
            data = json.load(file)
    except:
        data = {}
    data.update({message_id: [product,img,img_count[0], img_count[1]]})
    with open('data/message_data.JSON', 'w') as file:
        json.dump(data, file)



"""Обновляем img в словаре при пагинации """
async def upd_data_message(message_id, product, img, img_count):
    message_id = str(message_id)
    with open('data/message_data.JSON') as file:
        data = json.load(file)
    endpoint = data[message_id]
    end_count = endpoint[3]
    data.update({message_id: [product,img, img_count,end_count]})
    with open('data/message_data.JSON', 'w') as file:
        json.dump(data, file)


"""Получаем img.jpg для пагинации"""
async def get_img(msg_id, action):
    message_id = str(msg_id)
    with open('data/message_data.JSON') as file:
        data = json.load(file)
    a = data[str(msg_id)]
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    path = product_data[a[0]].get('img_path')
    list = []
    for n in os.listdir(path):
        if n == 'stop':
            pass
        else:
            list.append(n)

    ind = list.index(a[1])
    if action == 'prev':
        try:
            return [list[ind - 1],path,a[0]]
        except:
            return [list[len - 1],path,a[0]]
    if action == 'next':
        try:
            return [list[ind + 1],path,a[0]]
        except:
            return [list[0],path,a[0]]
    if action == 'liked':
        return path + a[1]


"""Удаляем задвоенные картинки"""
async def remove_photo(msg_id, action):
    msg_id = str(msg_id)
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    with open('data/message_data.JSON') as file:
        msg_data = json.load(file)
    prod = msg_data[msg_id][0]
    img = msg_data[msg_id][1]
    path = product_data[prod].get('img_path')
    list = []
    for n in os.listdir(path):
        if n == 'stop':
            pass
        else:
            list.append(n)
    ind = list.index(img)
    if len(list) == 1:
        pass
    else:
        os.remove(path+img)
        if action == 'change_next' or action == 'change_next_del':
            try:
                msg_data.update({msg_id: [prod, list[ind + 1]]})
                print('Удалено '+list[ind + 1])
            except:
                msg_data.update({msg_id: [prod, list[0]]})
                print('Удалено '+list[0])
        else:
            print('ok')
            try:
                msg_data.update({msg_id: [prod, list[ind - 1]]})
                print('Удалено '+list[ind - 1])
            except:
                msg_data.update({msg_id: [prod, list[len - 1]]})
                print('Удалено '+list[len - 1])

        with open('data/message_data.JSON', 'w') as file:
            json.dump(msg_data, file)


"""Перекидывание текста сообщения для пагинации"""
async def capt_pag(msg_id, action):
    with open('data/message_data.JSON') as file:
        data = json.load(file)
    a = data[str(msg_id)]
    img_count = a[2]
    if action == 'next':
        if img_count == a[3]:
            img_count =1
        else: img_count += 1
    if action == 'prev':
        if img_count == 0:
            img_count = a[3]
        else: img_count -= 1
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    n = [product_data[a[0]]]
    capt = n[0]
    capt_step_1 = str('<b>' + capt['name']) + '</b>\n' + capt['description'] + "\n\nЦена:" + str(
        capt['price']) + "\nАртикул:" + str(capt['article']+'\n<b>['+str(img_count)+'/'+str(capt['img_count'])+']</b>')
    return [capt_step_1,img_count]


"""Добавляем продукт в избранное"""
async def like_product(msg_id, user):
    msg_id = str(msg_id)
    user = str(user)
    with open('data/message_data.JSON') as file:
        data = json.load(file)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)

    product = data[msg_id][0]
    if 'liked_list' in user_data[user]:
        if product in user_data[user].get('liked_list'):
            return False
        else:
            user_data[user].get('liked_list').append(product)
    else:
        user_data[user].setdefault('liked_list', [product])
    with open('data/user_data.JSON', 'w') as file:
        json.dump(user_data, file)


"""Направляем текст с артикулами товаров менеджеру"""
async def mngr_msg(user):
    user = str(user)
    article_list = ''
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    if 'liked_list' in user_data[user]:
        if user_data[user].get('liked_list') != []:
            prod_list = user_data[user].get('liked_list')
            for n in prod_list:
                if n in prod_list:
                    if n in product_data:
                        article_list = article_list + '\n' + product_data[n].get('article')
        else:
            article_list = []
    else:
        article_list = []
    return article_list


"""Возвращаем размеры для белья менеджеру"""
async def mngr_sizes_msg(user):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    pod_grud = user_data[user].get('sizes').get('pod_grud')
    grud = user_data[user].get('sizes').get('grud')
    sizes = [pod_grud,grud]
    return sizes


"""Направляем список товаров для страницы избранного"""
async def liked_products(user):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    if 'liked_list' in user_data[user]:
        prod_list = user_data[user].get('liked_list')
    else:
        prod_list = []
    return prod_list


"""Удаление из избранного"""
async def unlike_product(msg_id, user):
    msg_id = str(msg_id)
    user = str(user)
    with open('data/message_data.JSON') as file:
        data = json.load(file)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)

    product = data[str(msg_id)][0]
    if product in user_data[user].get('liked_list'):
        user_data[user].get('liked_list').remove(product)
    else:
        return False
    with open('data/user_data.JSON', 'w') as file:
        json.dump(user_data, file)


"""Проверка на наличие лайка"""
async def check_like(product, user):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
        try:
            if product in user_data[user].get('liked_list'):
                return True
        except:
            return False
        else:
            return False


"""Проверка на черный список при связи с менеджером"""
async def check_bl(user):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    if user in user_data:
        if 'black_list' in user_data[user]:
            if user_data[user].get('black_list') == 1:
                return 1
            else: return 0
        return 0
    else:return 2


async def check_number(user):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    if 'number' in user_data[user]:
        if user_data[user].get('number') == 0:
            return 0
        return 1
    else: return 0


"""Проверка на наличие белья в избранном при связи с менеджером"""
async def check_bel_in_liked_list(user):
    user = str(user)
    status = 0
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    if user in user_data:
        if 'liked_list' in user_data[user]:
            if user_data[user].get('liked_list') != []:
                for prod in user_data[user].get('liked_list'):
                    if prod in product_data:
                        if product_data[prod].get('class') == 'Базовые комплекты и бюстгальтеры' or product_data[prod].get('class') == 'Комплекты нижнего белья':
                            status = 1
                            break
    return status


"""Проверка наличия информации о размерах для белья"""
async def check_size_data(user):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    if 'sizes' in user_data[user]:
        return 1
    else:
        return 0


"""Обновление информации о размерах для белья"""
async def update_size_data(user,data):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    user_data[user].update({'sizes':
                                {'pod_grud':data['pod_grud'],
                                'grud':data['grud']}})
    with open('data/user_data.JSON', 'w') as file:
        json.dump(user_data, file)


"""Прокидывание ветки выбора пользователя в вывод"""
async def check_selected_path(user):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    category = user_data[user].get('тип')
    clas = user_data[user].get('class')
    size = user_data[user].get('Размер')
    return [category,clas,size]


"""Проверка на newcomer + Добавление newcomer для новеньких"""
async def check_newcomer(user):
    user = str(user)
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    if user in user_data:
        if "promo_bot" in user_data[user]:
            if user_data[user].get("promo_bot") == 0:
                return 0
            if user_data[user].get("promo_bot") == 2:
                return 2
            if user_data[user].get("promo_bot") == 1:
                return 1
        else: return 0
    else:
        await user_data_upd(user,"promo_bot",1)
        return 1

async def check_mngr_msg(msg_id):
    message_id = str(msg_id)
    with open('data/message_data.JSON') as file:
        data = json.load(file)
    return data[message_id]


"""Добавляем рассылку в базу рассылок"""
async def add_mail(user,msg_id):
    try:
        with open('data/mails.JSON', 'r') as file:
            mail_data = json.load(file)
    except:
        mail_data = {}
    mail_data.setdefault(len(mail_data) + 1, {'creat_user_id': user,
                                              'create_date':datetime.datetime.now().strftime("%Y-%m-%d"),
                                              "msg_id" : msg_id,
                                              'send_user':[],
                                              'status':0})
    with open('data/mails.JSON', 'w') as file:
        json.dump(mail_data, file)
    return len(mail_data)

"""Добавляем дату и инициатора старта в базу"""
async def add_mail_start_date(msg_id, user_id):
    with open('data/mails.JSON', 'r') as file:
        mail_data = json.load(file)
    mail_data[msg_id].update({'date': datetime.datetime.now().strftime("%Y-%m-%d"),'start_user_id': user_id})
    with open('data/mails.JSON', 'w') as file:
        json.dump(mail_data, file)


"""Возвращаем message_id рассылки по её id"""
async def get_mail(mail_id):
    try:
        with open('data/mails.JSON', 'r') as file:
            mail_data = json.load(file)
    except:
        mail_data = {}
    if mail_id in mail_data:
        return mail_data[mail_id].get('msg_id')
    else: return 0


async def get_status(mail_id):
    with open('data/mails.JSON', 'r') as file:
        mail_data = json.load(file)
    return mail_data[mail_id].get('status')


"""Получаем список клиентов для рассылки"""
async def get_users(mail_id):
    users_list = []
    with open('data/user_data.JSON', 'r') as file:
        user_data = json.load(file)
    with open('data/mails.JSON', 'r') as file:
        mail_data = json.load(file)
    ok_list = mail_data[mail_id].get("send_user")
    for user in user_data:
        if len(users_list) <= 30:
            if user not in ok_list:
                users_list.append(user)
    for n in users_list:
        mail_data[mail_id].get("send_user").append(n)
    with open('data/mails.JSON', 'w') as file:
        json.dump(mail_data, file)
    return users_list


"""Получаем id чата откуда копируем рассылку"""
async def chat_id(mail_id):
    with open('data/mails.JSON', 'r') as file:
        mail_data = json.load(file)
    return mail_data[mail_id].get("creat_user_id")


"""выставляем статус 1"""
async def set_status(mail_id,value):
    with open('data/mails.JSON', 'r') as file:
        mail_data = json.load(file)
    mail_data[mail_id].update({'status':int(value)})
    with open('data/mails.JSON', 'w') as file:
        json.dump(mail_data, file)

"""Счетчик нажатий кнопки <связаться самомтоятельно>"""
async def counter():
    try:
        with open('data/counter.JSON', 'r') as file:
            counter_data = json.load(file)
    except:
        counter_data = {}
    if "self_click" in counter_data:
        count = int(counter_data["self_click"]) + 1
        counter_data.update({"self_click":count})
    else:
        counter_data.setdefault("self_click",1)
    with open('data/counter.JSON', 'w') as file:
        json.dump(counter_data, file)

