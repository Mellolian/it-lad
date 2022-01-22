import psycopg2, sqlalchemy

conn = psycopg2.connect("dbname=itlad user=itlad password=itlad host=localhost")


# engine = create_engine("postgresql+psycopg2://itlad:pass@localhost/mydb")