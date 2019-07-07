import psycopg2
import exceptions

class PrgrnwDB:
    """Classe que representa conexao com banco de dados do prgrnw"""

    __db_name='prgrnw'

    def __init__(self, host, user, passwd):
        self.__cnx = psycopg2.connect(
            host=host,
            user=user,
            password=passwd,
            dbname=self.__db_name
        )
        self.__cursor = self.__cnx.cursor()


    def pega_credenciais(self, cpf):
        self.__cursor.execute("SELECT cpf,senha,email FROM users WHERE cpf = '{}'".format(cpf))
        result = self.__cursor.fetchone()

        return result
    

    def close(self):
        self.__cnx.close()
