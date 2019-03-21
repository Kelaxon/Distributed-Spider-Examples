import redis
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

def db_connect():
    return create_engine(get_project_settings().get('CONNECTION_STRING'))


def create_table(engine):
    Base.metadata.create_all(engine)


def get_session(engine):
    session = sessionmaker(bind=engine)
    return session()


def redis_create_pool():
    settings = get_project_settings()
    return redis.ConnectionPool.from_url(url=settings.get('REDIS_URL'))


def redis_connect(pool):
    return redis.Redis(connection_pool=pool)


class ProductIndexModel(Base):
    __tablename__ = 'product_index'
    product_index_id = Column(Integer, primary_key=True)
    product = relationship('ProductModel', backref="product_index", uselist=False)  # 1:1

    product_name = Column(String(100), nullable=False, unique=True)
    product_url = Column(String(2083))
    product_parent_category = Column(Text)

    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')
        self.product_name = kwargs.get('product_name')
        self.product_url = kwargs.get('product_url')
        self.product_parent_category = kwargs.get('product_parent_category')


class ProductModel(Base):
    __tablename__ = 'product'
    product_id = Column(Integer, primary_key=True)
    product_index_id = Column(Integer, ForeignKey('product_index.product_index_id'))
    product_detail_information = Column(JSON)

    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')
        self.product_detail_information = kwargs.get('product_detail_information')


def indexItem2model(index_item):
    if (index_item and index_item.get('product_name')):
        return ProductIndexModel(product_name=index_item.get('product_name'), product_url=index_item.get('product_url'),
                                 product_parent_category=index_item.get('product_parent_category'))


def productItem2model(product_item):
    if (product_item and product_item.get('name')):
        prepare_data = dict(product_item)
        del prepare_data['product_index_id']  # filter product_index_id
        return ProductModel(product_detail_information=json.dumps(prepare_data))

# class Product(Base):
#     __tablename__ = 'product'
#     product_id = Column(Integer, primary_key=True)
#     product_name = Column(String(100), nullable=False)
#     product_price = Column(String(50))
#     product_url = Column(String(2083))
#     product_category = Column(String(200))  # TODO
#     product_short_description = Column(Text)
#     product_full_description = Column(Text)
#     product_more_info = Column(JSON)
#     product_imgs = relationship('ProductImage', backref='product', lazy=True)  # 1:n
#     product_attributes = relationship('Attribute', backref='product', lazy=True)  # 1:n
#
#     def __init__(self, **kwargs):
#         self.product_id = kwargs.get('product_id')
#         self.product_name = kwargs.get('product_name')
#         self.product_price = kwargs.get('product_price')
#         self.product_url = kwargs.get('product_url')
#         self.product_category = kwargs.get('product_category')
#         self.product_short_description = kwargs.get('product_short_description')
#         self.product_full_description = kwargs.get('product_full_description')
#         self.product_more_info = kwargs.get('product_more_info')
#         self.product_imgs = kwargs.get('product_imgs', [])
#         self.product_attributes = kwargs.get('product_attributes', [])
#
#     def __repr__(self):
#         return '<Product id={}>'.format(self.product_id)


# class ProductImage(Base):
#     __tablename__ = 'product_img'
#     product_img_id = Column(Integer, primary_key=True)
#     product_img_checksum = Column(CHAR(32))
#     product_img_url = Column(String(2083))
#     product_img_path = Column(String(2083))
#     product_id = Column(Integer, ForeignKey('product.product_id'))
#
#     def __init__(self, **kwargs):
#         self.product_img_checksum = kwargs.get('product_img_checksum')
#         self.product_img_url = kwargs.get('product_img_url')
#         self.product_img_path = kwargs.get('product_img_path')
#         self.product_id = kwargs.get('product_id')
#
#     def __repr__(self):
#         return '<ProductImage {}>'.format(self.product_img_checksum)
#
#
# association_table = Table('rlst_attribute_color', Base.metadata,
#                           Column('attribute_id', Integer, ForeignKey('attribute.attribute_id')),
#                           Column('color_id', Integer, ForeignKey('color.color_id'))
#                           )
#
#
# class Attribute(Base):
#     __tablename__ = 'attribute'
#     attribute_id = Column(Integer, primary_key=True)
#     attribute_name = Column(String(100), nullable=False)
#     product_id = Column(Integer, ForeignKey('product.product_id'))
#     options = Column(Text)  # TODO
#     colors = relationship('Color', secondary=association_table, backref='attribute')  # n:n
#
#     def __repr__(self):
#         return '<Attribute {}>'.format(self.product_img_checksum)
#
#
# class Color(Base):
#     __tablename__ = 'color'
#     color_id = Column(Integer, primary_key=True)
#     color_name = Column(String(100), nullable=False)
#     color_img_checksum = Column(CHAR(32))
#     color_img_url = Column(String(2083))
#     color_img_path = Column(String(2083))
#
#     def __repr__(self):
#         return '<Color {}>'.format(self.color_name)


# def item2model(item):
#     if item['name']:
#         # create a new SQL Alchemy object and add to the session
#         product = Product(
#             product_name=item.get('name'),
#             product_price=item.get('price'),
#             product_url=item.get('url'),
#             product_category=str(item.get('category')), # TODO str list
#             product_short_description=item.get('short_description'),
#             product_full_description=item.get('full_description')
#
#         )
#
#         product_imgs = []
#         for i in range(len(item.get('images', []))):
#             product_imgs.append(ProductImage(
#                 product_img_checksum=item['images'][i].get('checksum'),
#                 product_img_path=item['images'][i].get('path'),
#                 product_img_url=item['images'][i].get('url')
#             ))
#
#         product.product_imgs = product_imgs
#
#         product_attributes = []
#         for i in range(len(item.get('attributes', []))):
#             colors = []
#             for j in range(len(item.get('attributes')[i].get('colors', []))):
#                 colors.append(Color(
#                     color_name=item['attributes'][i]['colors'][j].get('name'),
#                     color_img_checksum=item['attributes'][i]['colors'][j].get('image').get('checksum'),
#                     color_img_url=item['attributes'][i]['colors'][j].get('image').get('url'),
#                     color_img_path=item['attributes'][i]['colors'][j].get('image').get('path')
#                 ))
#
#             product_attributes.append(Attribute(
#                 attribute_name=item['attributes'][i].get('label'),
#                 options=str(item['attributes'][i].get('options')), # TODO str list
#                 colors=colors
#             ))
#         product.product_attributes = product_attributes
#
#
#     return product
