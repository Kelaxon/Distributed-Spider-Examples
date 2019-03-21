import requests
from sqlalchemy.exc import IntegrityError

from spiders.models import ProductIndexModel, db_connect, get_session


def fixColorName(color_names):
    if (isinstance(color_names, list)):
        return [color_name.replace('_ ', '_') for color_name in color_names]
    return color_names.replace('_ ', '_')


import html2text


def toPlainText(html, chomp=True):
    if(html):
        h = html2text.HTML2Text()
        h.body_width = 0
        plainText = h.handle(html)
        if (chomp):
            return plainText.rstrip()
        return plainText

def concateTextList(textList):
    return ''.join(textList).strip()

def fixDeco(string):
    return string.replace('Dec;ò', 'Decò')

def fix_Deco_in_DB():
    fix_count = 0
    engine = db_connect()
    session = get_session(engine)
    for product_index in session.query(ProductIndexModel).filter(ProductIndexModel.product_name.like('%Dec;ò%')).all():
        product_index.product_name = (fixDeco(product_index.product_name))
        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            if (e.orig.args[0] == 1062):  # Duplicate entry
                print(product_index.product_name)
                fix_count += 1
                session.delete(product_index)
                session.commit()
    session.close()
    engine.dispose()
    print('fix deco in database complete, total {} items.'.format(fix_count))

def fix_Dot_Dot_Dot():
    engine = db_connect()
    session = get_session(engine)
    header = {
    'method':'GET',
    'authority':'eu1-search.doofinder.com',
    'scheme':'https',
    'origin':'https://www.miliashop.com',
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'accept':'*/*',
    'referer':'https://www.miliashop.com/en/',
    'accept-encoding':'gzip, deflate, br',
    'accept-language':'zh-CN,zh;q=0.9',
    }
    url = 'https://eu1-search.doofinder.com/5/search'
    params = {'hashid':'cf518a4fc64ed58ed14863348a5bae18',
              'transformer': 'basic',
              'rpp': '50',
              'query':'',
              'query_counter': '5',
              'page': '1'
              }
    fix_count = 0
    for product_index in session.query(ProductIndexModel).filter(ProductIndexModel.product_name.like('%...%')).all():
        print('before: ', product_index.product_name)
        try:
            params['query'] = product_index.product_name
            r = requests.get(url, headers=header, params=params)
            fix_name = r.json()['results'][0].get('title')
            if(fix_name == 'Nimrod Low Chair'):
                print('ERROR: No search result!')
                continue
            fix_count += 1
            product_index.product_name = fix_name
            print('after: ', product_index.product_name)
            session.commit()
        except(IntegrityError, AttributeError) as e:
            session.rollback()
            if (e.orig.args[0] == 1062):  # Duplicate entry
                print('Duplicated entry: ', product_index.product_name)
                session.delete(product_index)
                session.commit()

    session.close()
    engine.dispose()
    print('fix ... in database complete, total {} items.'.format(fix_count))
