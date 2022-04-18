
import socket
import ssl

import config
from src.client import Client

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Cria Socket
s = ssl.wrap_socket(s)                                        

s.connect((config.IP, config.PORT))                           # Conecta ao servidor (IP e Porta carregados a partir de config.py)

client = Client(s)                                            # Cria NOVO OBJETO CLIENT
client.handle_connection()                                    # Trata conexao 
