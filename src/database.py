import psycopg2
import exceptions
import os
import sys

from cryptography.fernet import Fernet

class PrgrnwDB:
    """Classe que representa conexao com banco de dados do prgrnw"""

    __db_name='prgrnw'

    def __init__(self):
        db_url = os.environ.get('DATABASE_URL')
        self.__cnx = psycopg2.connect(
            db_url,
            sslmode='require'
        )

        
    def get_user(self, cpf):
        k = os.environ.get('DB_ENC_KEY')
        if not k:
            raise exceptions.DBEncKeyNotFound("Chave de criptografia não pode ser obtida")
        frn = Fernet(k.encode())

        cursor = self.__cnx.cursor()
        cursor.execute('SELECT cpf, senha, email FROM users WHERE cpf = \'{}\''.format(cpf))
        result_encrypted = cursor.fetchone()

        print('r2e')
        print(result_encrypted)
        for i in result_encrypted:
            print(i)
        


        result_unenc = [result_encrypted[0]]
        result_unenc += [ frn.decrypt(i.encode()).decode() for i in result_encrypted[1:] ]

        print('rune', result_unenc)
        sys.stdout.flush()
        return result_unenc

    def update_user(self, cpf=None, senha=None, email=None):
        pass

    def insert_user(self, cpf, senha, email):
        k = os.environ.get('DB_ENC_KEY')
        if not k:
            raise exceptions.DBEncKeyNotFound("Chave de criptografia não pode ser obtida")
        frn = Fernet(k.encode())

        #encrypted_cpf = frn.encrypt(cpf.encode())
        encrypted_senha = frn.encrypt(senha.encode())
        encrypted_email = frn.encrypt(email.encode())

        try:
            cursor = self.__cnx.cursor()
            cursor.execute('INSERT INTO users (cpf, senha, email) VALUES (\'{}\', \'{}\', \'{}\')'.format(cpf, encrypted_senha.decode(), encrypted_email.decode()))
            cursor.close()
            self.__cnx.commit()
        except Exception as e:
            print(e)
            return False
        
        return True

    def close(self):
        self.__cnx.close()
