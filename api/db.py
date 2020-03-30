# from datetime import date, datetime
# from decimal import Decimal
# from os import environ

# from sqlalchemy import create_engine

# # Todo: Make this handle environment configs better
# LOCAL = "mysql+pymysql://dbuser:dbpassword@localhost:3306/quotes_db"
# DOCKER = "mysql+pymysql://dbuser:dbpassword@db/quotes_db"


# class Db():
#     def __init__(self):
#         conn = ConnectionString().get_url()
#         engine = create_engine(conn)
#         self.connection = engine.connect()

#     def __del__(self):
#         self.connection.close()

#     def clean_select_row(self, row, keys):
#         try:
#             clean_row = [str(field) if isinstance(field, datetime) or isinstance(
#                 field, Decimal) or isinstance(field, date) else field for field in list(row)]
#             current_row = {}
#             for i in range(len(keys)):
#                 current_row[keys[i]] = clean_row[i]
#             return current_row
#         except:
#             return None

#     def clean_select_results(self, data, keys):
#         if len(data) == 0:
#             return {}
#         result_data = []
#         for row in data:
#             result_data.append(self.clean_select_row(row, keys))
#         return result_data


# class ConnectionString():
#     def __init__(self):
#         self.environment = environ.get('FLASK_ENV')
#         self.db_url = environ.get('FLASK_DB_URL')

#     def get_url(self):
#         if self.db_url != None:
#             return self.db_url
#         if self.environment == "development":
#             return LOCAL
#         if self.environment == "production":
#             return DOCKER
#         else:
#             return DOCKER
