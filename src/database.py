#Modulo que trata da conexao com o Banco de dados


import sqlite3 as lite
import sys

#define o nome da base de dados dos usuarios
DATABASE_NAME = "users.db"


def create_table():
    """
    Cria usuario na tabela de dados, caso eles nao existam
    USERS: (login: username, password: hashed_password, salt: generated_salt_unique_value)
    """
    try:
        conn = lite.connect(DATABASE_NAME)

        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS USERS (login TEXT PRIMARY KEY, password TEXT, salt TEXT);')
        print "Tabela Criada com Sucesso!"

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if conn:
            conn.commit()
            conn.close()


def create_user(username, password, salt):
    """
    Insere Usuario na tabela USERS da base de dados
    
    """
    try:
        conn = lite.connect(DATABASE_NAME)

        cur = conn.cursor()
        cur.execute('INSERT INTO USERS (login, password, salt) values (?, ?, ?)', (username, password, salt))
        print "Usuario Registrado com Sucesso!"

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if conn:
            conn.commit()
            conn.close()


def delete_user(username):
    """
    Remove usuario da tabela  USERS na base de dados
    """
    try:
        conn = lite.connect(DATABASE_NAME)

        cur = conn.cursor()
        cur.execute('DELETE from USERS where login = ?', (username, ))
        print "Usuario Removido com Sucesso!"

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if conn:
            conn.commit()
            conn.close()


def change_password(username, new_password, new_salt):
    """
    Muda a senha e o valor de salt da tabela USERS na base de dados
    """
    try:
        conn = lite.connect(DATABASE_NAME)

        cur = conn.cursor()
        cur.execute('UPDATE USERS set password = ?, salt = ? where login = ?', (new_password, new_salt, username))

        print "Senha Alterada com Sucesso!"

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if conn:
            conn.commit()
            conn.close()

def get_users():
    """
    Imprime todos os usuarios da tabela USERS da base de dados
    Para testar
    """
    try:
        conn = lite.connect(DATABASE_NAME)

        cur = conn.cursor()
        result = cur.execute("SELECT login, password, salt from USERS")

        for row in result:
            print "username = ", row[0]
            print "password = ", row[1]
            print "salt = ", row[2] + "\n"

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if conn:
            conn.commit()
            conn.close()


def get_user(username):
    """
    Retorna a linha da base de dados que contem o usuario (login)
    Se nao existir retorna None
    """
    try:
        conn = lite.connect(DATABASE_NAME)

        cur = conn.cursor()
        result = cur.execute("SELECT * FROM USERS WHERE login = ?", (username, ))

        return result.fetchone()

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if conn:
            conn.close()


def get_password(username):
    """
    Retorna o registro (password, salt) para dado usuario da base de dados
    Se nao existir retorna  None
    """
    user = get_user(username)
    if user is not None:
        return (user[1], user[2])   #return (password , salt)
    else:
        return None


def is_username_taken(username):
    """
    Checa se o usuario ja foi usado
    
    """

    try:
        conn = lite.connect(DATABASE_NAME)

        cur = conn.cursor()
        result = cur.execute("SELECT * FROM USERS WHERE login = ?", (username, ))

        return len(list(result)) > 0

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if conn:
            conn.close()