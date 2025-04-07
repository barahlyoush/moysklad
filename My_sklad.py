import requests
import json
import io,os, shutil
import time
import asyncio
from dotenv import find_dotenv,load_dotenv
load_dotenv(find_dotenv())


tovar = 'https://api.moysklad.ru/api/remap/1.2/entity/product/?offset='
modificators = 'https://api.moysklad.ru/api/remap/1.2/entity/variant/?offset='
ostatok = "https://api.moysklad.ru/api/remap/1.2/report/stock/all/?offset="

groups = ['Базовые бюстгальтеры', 'Комплекты нижнего белья', 'Пижамы с брюками', 'Пижамы с шортами']
token = os.getenv('API_TOKEN')

headers = {
    'Authorization': token,
    'Accept-Encoding': 'gzip',
}


'''Функция обновления данных (на всякий случай)'''
async def update():
    try:
        listprod = []
        count = 0
        data = {'rows': [1, 2]}
        while len(data['rows']) != 0:
            r = requests.get(tovar + str(count), headers=headers)
            data = r.json()
            for n in data['rows']:
                listprod.append(n)
            count += 1000
            await asyncio.sleep(3)

        listmod = []
        count = 0
        data = {'rows': [1, 2]}
        while len(data['rows']) != 0:
            r = requests.get(modificators + str(count), headers=headers)
            data = r.json()
            for n in data['rows']:
                listmod.append(n)
            count += 1000
            await asyncio.sleep(3)

        dictstock = {}
        liststock = []
        count = 0
        data = {'rows': [1, 2]}
        while len(data['rows']) != 0:
            r = requests.get(ostatok + str(count), headers=headers)
            data = r.json()
            for n in data['rows']:
                liststock.append(n)
            count += 1000
            await asyncio.sleep(3)
        for n in liststock:
            dictstock.setdefault(n['code'],{'count':int(n['stock'])})

        t_m_data = {'prod': listprod,
                    'mod': listmod,
                    'count':dictstock}
        with open('data/data.JSON', 'w') as file:
            json.dump(t_m_data, file)
        print('update выполнен')
        return 1
    except:return 0


'''Загружаем бд на сервер.'''
async def data_loader():
    try:
        print('data_loader запущен')
        with open('data/data.JSON') as file:
            data = json.load(file)
        prod_list = {}
        prod_dict = {}
        for n in data['mod']:
            prod = dict(n).get('product').get('meta').get('href')
            id = n['code']
            char = {id: {}}
            char[id].setdefault('img_href', dict(n).get('images').get('meta').get('href'))
            for m in n['characteristics']:
                char[id].setdefault(m['name'], m['value'])
            if id in data['count']:
                char[id].setdefault('count', data['count'].get(id).get('count'))
            else:
                char[id].setdefault('count', 0)
            if prod in prod_dict:
                prod_dict[prod].get('mods').update(char)
            else:
                prod_dict.setdefault(prod, {'mods': char})

        for n in data['prod']:
            product_data = {}
            try:
                if n['code'] in data['count']:
                    count = data['count'].get(n['code']).get('count')
                else:
                    count = 0
                id = n['id']
                href = n.get('meta').get('href')
                article = n['code']
                img_path = 'catalog_data/' + article + '/'
                name = n.get('name')
                product_class = n['pathName']
                if 'description' in n:
                    desc = n['description']
                else: desc = ''

                price_prod = int(n.get('salePrices')[0].get('value')/100)
                api_img_url = n.get('images').get('meta').get('href')

                product_data.setdefault("name", name)
                product_data.setdefault("description", desc)
                product_data.setdefault('class', product_class)
                product_data.setdefault("img_path", img_path)
                product_data.setdefault("price", price_prod)
                product_data.setdefault('article', article)
                product_data.setdefault('count', count)
                product_data.setdefault('img_url', api_img_url)
                product_data.setdefault('id', id)
                if href in prod_dict:
                    prod_dict[href].update(product_data)
                else:
                    prod_dict.setdefault(href,product_data)
            except FileExistsError:
                pass
        with open('data/product_data.JSON', 'w') as file:
            json.dump(prod_dict, file)

        for n in prod_dict:
            if prod_dict[n].get('class') in groups:
                count = 0
                if 'mods' in prod_dict[n]:
                    for m in prod_dict[n].get('mods'):
                        count += prod_dict[n].get('mods').get(m).get('count')

                count += prod_dict[n].get('count')
                if count != 0:
                    prod_list.setdefault(n, prod_dict[n])

        with open('data/output_product_data.JSON', 'w') as file:
            json.dump(prod_list, file)
        return 1
    except:return 0


'''Загружаем картинки на сервер.'''
async def img_loader():
    try:
        with open('data/output_product_data.JSON') as file:
            prod_list = json.load(file)
        try:
            with open('data/dnld_list.JSON') as file:
                dnld_list = file.read()
                dnld_list = json.loads(dnld_list)
        except:
            dnld_list = []
        count = 0
        large = len(prod_list)

        for n in prod_list:
            if n not in dnld_list:
                if os.path.isdir(prod_list[n].get('img_path')) == False:
                    os.mkdir(prod_list[n].get('img_path'))
                if count >= 30:
                    time.sleep(3)
                    count = 0
                img_url = prod_list[n].get('img_url')
                img_dwld_url = await identify_img(img_url,count)
                cnt = img_dwld_url[1]
                count = await image_work(img_dwld_url[0], prod_list[n].get('img_path'),cnt)

                # Фото продукта загружено

                if 'mods' in prod_list[n]:
                    for mod in prod_list[n].get('mods'):
                        if count >= 30:
                            time.sleep(3)
                            count = 0
                        mod_href = prod_list[n].get('mods').get(mod).get('img_href')
                        url = await identify_img(mod_href, count)
                        count = url[1]
                        if url[0] != []:
                            for href in url[0]:
                                count = await image_mods_work(href, prod_list[n].get('img_path'), count)


                dnld_list.append(n)
                with open('data/dnld_list.JSON', 'w') as file:
                    json.dump(dnld_list, file)
                large -= 1
                print('Продукт ' + str(prod_list[n].get('article')) + ' загружен. Еще ' + str(large) + ' товаров')
            else:
                large -= 1
                print('Продукт ' + str(prod_list[n].get('article')) + ' был загружен ранее. Еще ' + str(large) + ' товаров')
        return 1
    except:return 0


'''Пересчитваем кол-во картинок в папке'''
async def img_count():
    try:
        with open('data/output_product_data.JSON') as file:
            prod_list = json.load(file)
        for n in prod_list:
            img_count = len(os.listdir(prod_list[n].get('img_path')))

            prod_list[n].update({'img_count': img_count})
            with open('data/output_product_data.JSON', 'w') as file:
                json.dump(prod_list, file)
        return 1
    except:return 0


'''Получаем ссылку на скачивание картинки.'''
async def identify_img(api_url,count):
    href_list = []
    try:
        r = requests.get(api_url, headers=headers)
        count += 1
        data = r.json()
        path = data.get('rows')
        for key in path:
            img_dwld_url = key.get('meta').get('downloadHref')
            href_list.append(img_dwld_url)
    except:pass
    return [href_list,count]


'''Скачивание изображения.'''
async def image_work(url,path,count,action = 'download'):
    try:
        with open('data/dnld_img_list.JSON') as file:
            dnld_img_list = json.load(file)
    except:
        dnld_img_list = {}

    if action == 'update':
        try:
            del dnld_img_list[path]
        except:pass

    img_count = 0
    for img_url in url:
        r = requests.head(img_url, headers=headers)
        count += 1
        a = r.headers['Location']
        pos = a.find('?')
        id = a[:pos]
        text = ('')
        for n in range(-36, 0):
            text += id[n]
        if 'qr-code' not in a:
            if path not in dnld_img_list:
                dnld_img_list.update({path:[]})
            if text not in dnld_img_list[path]:
                dnld_img_list[path].append(text)
                r = requests.get(a)

                if path+'img'+str(img_count)+'.jpg' in os.listdir(path[:-1]):
                    pass
                else:
                    with io.open(path+'img'+str(img_count)+'.jpg', 'wb') as file:
                        file.write(r.content)
                        img_count += 1
        if 'qr-code' in text:
            pass
    with open('data/dnld_img_list.JSON', 'w') as file:
        json.dump(dnld_img_list, file)
    return count


'''Скачивание изображений из модификаций.'''
async def image_mods_work(url,path,count):
    try:
        with open('data/dnld_img_list.JSON') as file:
            dnld_img_list = json.load(file)
    except:
        dnld_img_list = {}
    r = requests.head(url, headers=headers)
    count += 1
    a = r.headers['Location']
    pos = a.find('?')
    id = a[:pos]
    text = ('')
    for n in range(-36, 0):
        text += id[n]

    if path not in dnld_img_list:
        dnld_img_list.update({path: []})
    if text not in dnld_img_list[path]:
        img_count = len(os.listdir(path))
        dnld_img_list[path].append(text)
        r = requests.get(a)
        with io.open(path+'img'+str(img_count)+'.jpg', 'wb') as file:
            file.write(r.content)
            img_count += 1

    with open('data/dnld_img_list.JSON', 'w') as file:
        json.dump(dnld_img_list, file)
    return count


'''Апдейт фоток одного товара'''
async def solo_update(prod_code):
    count = 0
    with open('data/output_product_data.JSON') as file:
        product_data = json.load(file)
    path = product_data[prod_code].get('img_path')
    try:
        shutil.rmtree(path)
    except:pass
    os.mkdir(path)
    prod_id = product_data[prod_code].get('id')
    r = requests.get('https://api.moysklad.ru/api/remap/1.2/entity/product/'+prod_id, headers=headers)
    count += 1
    data = r.json()
    name = data['name']
    desc = data['description']
    article = data['code']
    price = str(data.get('salePrices')[0].get('value')/100)

    product_data[prod_code].update({'name':name+'test'})
    product_data[prod_code].update({'description': desc})
    product_data[prod_code].update({'article': article})
    product_data[prod_code].update({'price': price})

    api_img_href = data.get('images').get('meta').get('href')
    api_img_href = await identify_img(api_img_href,count)
    count = api_img_href[1]
    count = await image_work(api_img_href[0],path,count,action='update')
    r = requests.get('https://api.moysklad.ru/api/remap/1.2/entity/variant/?filter=productid='+prod_id, headers=headers)
    count += 1
    data = r.json()
    if data['rows'] != []:
        for mod in data['rows']:
            if count >= 30:
                time.sleep(3)
                count = 0
            mod_href = mod['images'].get('meta').get('href')
            url = await identify_img(mod_href, count)
            count = url[1]
            if url[0] != []:
                for href in url[0]:
                    count = await image_mods_work(href, product_data[prod_code].get('img_path'), count)
    with open('data/output_product_data.JSON', 'w') as file:
        json.dump(product_data, file)

    with open('data/output_product_data.JSON') as file:
        prod_list = json.load(file)
    img_count = len(os.listdir(prod_list[prod_code].get('img_path')))
    prod_list[prod_code].update({'img_count': img_count})
    with open('data/output_product_data.JSON', 'w') as file:
        json.dump(prod_list, file)