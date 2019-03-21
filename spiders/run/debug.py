from sqlalchemy.exc import IntegrityError
import json

from spiders.models import db_connect, get_session, ProductIndexModel, redis_create_pool, redis_connect
from spiders.spiders.rd_miliashopSpider import rd_miliashopSpider


def check_product_detail():
    engine = db_connect()
    session = get_session(engine)
    try:
        product_index = session.query(ProductIndexModel).filter(ProductIndexModel.product_name == 'Vicino Table Large Molteni & C').first()
        product = json.loads(product_index.product.product_detail_information)

        print(product)
    except IntegrityError as e:
        print(e)

    finally:
        session.close()
        engine.dispose()

def set_start_urls():
    engine = db_connect()
    session = get_session(engine)
    r_pool = redis_create_pool()
    r = redis_connect(r_pool)
    key = rd_miliashopSpider.redis_key
    url = 'https://www.miliashop.com/en/sofas/14351-swingus-dedon-2-seater-sofa.html'
    try:
        r.lpush(key, url)
        print('successful insert {} records into redis start_urls.'.format(r.llen(key)))
    except IntegrityError as e:
        print(e)
    finally:
        r.connection_pool.disconnect()
        session.close()
        engine.dispose()

