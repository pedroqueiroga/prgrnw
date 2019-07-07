import psycopg2
import exceptions
import os

from cryptography.fernet import Fernet

class PrgrnwDB:
    """Classe que representa conexao com banco de dados do prgrnw"""

    __db_name='prgrnw'

    def __init__(self, user, passwd):
        self.__cnx = psycopg2.connect(
            user=user,
            password=passwd,
            dbname=self.__db_name
        )

        
    def get_user(self, username):
        k = os.environ.get('DB_ENC_KEY')
        if not k:
            raise exceptions.DBEncKeyNotFound("Chave de criptografia não pode ser obtida")
        frn = Fernet(k.encode())

        cursor = self.__cnx.cursor()
        cursor.execute('SELECT * FROM users WHERE username = \'{}\''.format(username))
        result_encrypted = cursor.fetchone()

        result_unenc = [result_encrypted[1]]
        result_unenc += [ frn.decrypt(i.encode()).decode() for i in result_encrypted[2:] ]
        return result_unenc

    def update_user(self, username, cpf=None, senha=None, email=None):
        pass

    def insert_user(self, username, cpf, senha, email):
        k = os.environ.get('DB_ENC_KEY')
        if not k:
            raise exceptions.DBEncKeyNotFound("Chave de criptografia não pode ser obtida")
        frn = Fernet(k.encode())

        encrypted_cpf = frn.encrypt(cpf.encode())
        encrypted_senha = frn.encrypt(senha.encode())
        encrypted_email = frn.encrypt(email.encode())

        try:
            cursor = self.__cnx.cursor()
            cursor.execute('INSERT INTO users (username, cpf, senha, email) VALUES (\'{}\', \'{}\', \'{}\', \'{}\')'.format(username, encrypted_cpf.decode(), encrypted_senha.decode(), encrypted_email.decode()))
            cursor.close()
            self.__cnx.commit()
        except Exception as e:
            print(e.message, e.args)
            return False
        
        return True

    def close(self):
        self.__cnx.close()
