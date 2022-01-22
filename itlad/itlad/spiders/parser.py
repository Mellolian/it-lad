import scrapy
from sqlalchemy import create_engine, insert, select, event
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, Date, Boolean, PrimaryKeyConstraint, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.sql import text
from datetime import datetime, date, timedelta
from sqlalchemy.orm import relationship
from sqlalchemy.sql.ddl import DDL
from psycopg2.errors import CheckViolation

#функция для поиска понедельника указанной недели указанного года
def monday_of_calenderweek(year, week):
    first = date(year, 1, 1)
    base = 1 if first.isocalendar()[1] == 1 else 8
    return first + timedelta(days=base - first.isocalendar()[2] + 7 * (week - 1))


engine = create_engine("postgresql+psycopg2://root:root@localhost/test_db", echo=True, future=True)


Base = declarative_base()



class ProductsTable(Base):
    '''
    Таблица, содержащая товары и их уникальные id
    '''
    
    __tablename__ = 'products'

    id = Column(Integer(), nullable=False, primary_key=True, unique=True, autoincrement=True)
    product_name = Column(String(200), nullable=False, unique=True)
    products = relationship("Products", passive_deletes=True, cascade='all,delete',cascade_backrefs=True)


class QuantityTable(Base):
    
    '''
    Таблица, содержащая id товара, его количество и дату сбора данных
    '''
    
    __tablename__ =  'quantities'
    
    id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    # product_id = Column(Integer(), ForeignKey('products.id'))
    product_quantity = Column(Integer())
    report_date = Column(Date(), nullable=False, default=datetime.now().date())

    @declared_attr
    def product_id(cls):
        return Column(Integer, ForeignKey('products.id', ondelete='CASCADE'))
    quantities = relationship("Quantities", backref='products', cascade='all,delete')



class PricesTable(Base):
    '''
    Таблица, содержащая id товара, его цену, дату сбора данных и указание партиций
    '''
    __tablename__ =  'prices'
    __table_args__ = {
        'postgresql_partition_by': 'RANGE (report_date)'
    }
    id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)

    @declared_attr
    def product_id(cls):
        return Column(Integer, ForeignKey('products.id', ondelete='CASCADE'))
    product_price = Column(Numeric(), nullable=False)
    report_date = Column(Date(), nullable=False, default=datetime.now(), primary_key=True)
    prices = relationship("prices", backref='products', cascade='all,delete')

#очищаем базу перед перед загрузкой
Base.metadata.drop_all(engine)    
#создаем необходимые таблицы
Base.metadata.create_all(engine)


#класс кравлера
class ParserSpider(scrapy.Spider):
    name = 'parser'
    allowed_domains = ['toledo24.pro']
    start_urls = ['https://www.toledo24.pro/catalog/ustanovka-vyklyuchateli-rozetki-i-aksessuary/']

    def parse(self, response):
        #получаем все элементы с товарами
        products = response.xpath("//div[@class='product-card js-product-item']")
        #вычисляем неделю и год для параметров партиции
        week = datetime.now().isocalendar()[1]
        year = datetime.now().isocalendar()[0]
        week_start = monday_of_calenderweek(year, week)
        r_date = str(week_start)
        r_date_next = str(week_start + timedelta(days=7))
        
        #запрос для создания партиции
        query = text(f"CREATE TABLE IF NOT EXISTS {PricesTable.__tablename__}_{week} PARTITION OF {PricesTable.__tablename__} FOR VALUES FROM ('{r_date}') TO ('{r_date_next}')")
        
        with engine.begin() as conn:
            conn.execute(query)
            
        for product in products:
            name = product.xpath(".//a[@class='link product-name']/text()").get().strip()
            quantity = int((product.xpath(".//div[@class='amount-title']/text()").get()  or '0').strip().strip(' шт'))
            price = float(product.xpath('.//div[@class="price-current"]/text()').get() or '0')
            report_date = datetime.now()
            
            with engine.begin() as conn:

                stmt1 = insert(ProductsTable).values(product_name=name).returning(ProductsTable.id)
                try:
                    product_id = conn.execute(stmt1).first()[0]
                except:
                    stmt1_select = select(ProductsTable.id).where(ProductsTable.product_name == name)
                    product_id = conn.execute(stmt1).first()[0]
                stmt2 = insert(QuantityTable).values(product_id=product_id, product_quantity=quantity, report_date=report_date).returning(None)
                stmt3 =insert(PricesTable).values(product_id=product_id, product_price=price, report_date=report_date).returning(None)
                conn.execute(stmt2)
                conn.execute(stmt3)

                    
            
            
            