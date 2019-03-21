from sqlalchemy.exc import IntegrityError
from spiders.models import db_connect, get_session, redis_create_pool, redis_connect, ProductIndexModel, create_table, \
    ProductModel
from spiders.spiders.rd_miliashopSpider import rd_miliashopSpider

def load_start_urls():
    engine = db_connect()
    session = get_session(engine)
    r_pool = redis_create_pool()
    r = redis_connect(r_pool)
    key = rd_miliashopSpider.redis_key
    try:
        start_urls = [x.product_url for x in
                      session.query(ProductIndexModel.product_url).filter(ProductIndexModel.product == None).all()]
        print(len(start_urls))
        for url in start_urls:
             r.lpush(key, url)
        print('successful insert {} records into redis start_urls.'.format(r.llen(key)))
    except IntegrityError as e:
        print(e)
    finally:
        r.connection_pool.disconnect()
        session.close()
        engine.dispose()

def clean_incomplete_item():
    engine = db_connect()
    session = get_session(engine)
    r_pool = redis_create_pool()
    r = redis_connect(r_pool)
    try:
        incomplete_items = [x for x in
                      session.query(ProductModel).filter(ProductModel.product_index_id == None).all()]
        for item in incomplete_items:
            session.delete(item)
        session.commit()
        print('successful clean {} incomplete item in database.'.format(len(incomplete_items)))
    except IntegrityError as e:
        print(e)
    finally:
        session.close()
        engine.dispose()

def create_database_table():
    engine = db_connect()
    session = get_session(engine)
    try:
        create_table(engine)
    finally:
        session.close()
        engine.dispose()
clean_incomplete_item()