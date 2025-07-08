# config.py
DB_USERNAME = 'root'
DB_PASSWORD = 'Dhivi@29'
DB_HOST = '127.0.0.1'
DB_NAME = 'doctor_health_db'

SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD.replace("@", "%40")}@{DB_HOST}/{DB_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
