import mysql.connector
import exceptions

class PrgrnwDB:
    """Classe que representa conexao com banco de dados do prgrnw"""

    __db_name='prgrnw'

    def __init__(self, host, user, passwd):
        try:
            self.__cnx = mysql.connector.connect(
                host=host,
                user=user,
                passwd=passwd,
                database=self.__db_name
            )
        except mysql.connector.errors.ProgrammingError as e:
            if e.split()[0] == '1049':
                raise exceptions.DBNotFound('db not found: {}'.format(self.__db_name))
            if e.split()[0] == '1045':
                raise exceptions.DBAccessDenied('access denied for {}@{}'.format(user,host))
            else:
                raise e    

        self.__cursor = self.__cnx.cursor()


    def pega_credenciais(self, cpf):
        self.__cursor.execute("SELECT cpf,senha,email FROM users WHERE cpf = '{}'".format(cpf))
        result = self.__cursor.fetchone()

        return result
    

    def close(self):
        self.__cnx.close()
