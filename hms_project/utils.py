from config import Config
import mysql.connector
from PIL import Image, ImageTk

# Connect to the database
def connect_to_database():
    conn = mysql.connector.connect(
        host=Config.db_host,
        user=Config.user,
        password=Config.password,
        database=Config.database
    )
    return conn
