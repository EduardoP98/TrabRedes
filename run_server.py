
#Inicia Servidor
import socket
from OpenSSL import SSL

import src.database as database
import config
from src.server import ClientHandler

context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('keys/key')                                 # Carrega arquivos das chaves Public e Private Key (Arquivos que contem a chave)
context.use_certificate_file('keys/cert')                               # Carrega arquivo de certificadp das chaves 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                   # Cria Um Socket
s = SSL.Connection(context, s)                                          # Faz a Conexao 

s.bind((config.IP, config.PORT))                                        # Seleciona Porta e IP pra conectar

s.listen(5)                                                             # Escuta conexao do cliente
database.create_table()                                                 # Cria a tabela de dados (Registro de usuarios) caso nao exista

while True:
    client_socket, address = s.accept()                                 # Estabelece Conexao com o CLiente
    clientThread = ClientHandler(client_socket)                         # Cria uma Thread para cada Usuario
    clientThread.start()                                                # Executa Thread
