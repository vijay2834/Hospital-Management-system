import mysql.connector
class Config():
    domain = 'hms.com'
    smtp_username=""
    smtp_password=""
    db_host = '127.0.0.1'
    user='root'
    password='Venkat2834.p'
    database ='hospitalmanagementdb'


    @classmethod
    def get_domain(cls):
        return cls.domain
