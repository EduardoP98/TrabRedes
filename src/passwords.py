import uuid                 # Biblioteca que gera valor de salto
import re                   # Biblioteca que Checa Password com regex
import hashlib              # Biblioteca para fazer hash do password


def is_password_valid(password):
    """
    Funcao que retorna True se a senha for valida
    Contendo os seguintes parametros
    
     - Numero
     - Letra Minuscula
     - Letra Maiuscula
     - Tamanho > 7
     
     Caso contrario, retorna False
    """

    if len(password) < 8:
        return False

    #Digito de checagem
    pattern = ".*\d.*"
    pattern_compiled = re.compile(pattern)
    result = pattern_compiled.match(password)
    if not bool(result):
        return False

    #Conferencia de Minusculas
    pattern = ".*[a-z].*"
    pattern_compiled = re.compile(pattern)
    result = pattern_compiled.match(password)
    if not bool(result):
        return False

    #Conferencia de Maiusculas
    pattern = ".*[A-Z].*"
    pattern_compiled = re.compile(pattern)
    result = pattern_compiled.match(password)
    if not bool(result):
        return False

    
    return True


def hash_password(password, salt):
    """
    Cria Hash SHA 256 para a senha
    Retorna tupla
    """
    return (hashlib.sha256(salt.encode() + password.encode()).hexdigest(), salt)

def hash_password_generate_salt(password):
    """
    Cria Hash SHA 256 
    e gera um numero aleatorio de salta
    retorna a tupla respectiva
    """
    salt = get_salt()                                               # Gera um Numero aleatorio
    return (hashlib.sha256(salt.encode() + password.encode()).hexdigest(), salt)

def check_password(hashed_password, salt, user_password):
    """
    Checa se o Hash da senha em relacao ao Usuario
    """
    return hashed_password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

def get_salt():
    """
    Gera um valor unico de salt
    """
    return uuid.uuid4().hex