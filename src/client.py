import getpass
import sys

import config
import actions
import passwords
import rsa
import binascii

public, private = rsa.generate_keypair(1024) # Gera chave

class Client:
    """
    Classe Simples para tratar a conexao com o servidor
    """

    def __init__(self, _socket):
        self.socket = _socket
        self.n = 0
        self.salt = 0
        self.send_n = False
        

    def send(self, message):
        """
        Envia mensagem para o servidor via Socket 

        """
        try:
            self.socket.send(message)
        except:
            print "Erro inesperado:", sys.exc_info()[0]

    def receive(self):
        """
        Recebe a mensagem do Servidor e a Retorna
        """
        input_line = None
        try:
            input_line = self.socket.recv(config.BUFFER_SIZE)
        except:
            print "Erro inesperado:", sys.exc_info()[0]

        return input_line


    def chat(self, msg):
        """
        Funcao que cifra a mensagem a ser enviada do cliente para o servidor
        """
        msg = str.encode(msg)
        hex_data   = binascii.hexlify(msg)
        msg = int(hex_data, 16)
        ctt = rsa.encrypt(msg,public)
        self.socket.send(str(ctt).encode())
        print (ctt)

    def select_action(self, action_name):
        """
        Com base no nome da acao definida no arquivo actions.py, seleciona a funcao a ser executada
        """
        if action_name == actions.QUIT_ACTION or len(action_name) == 0:
            return
        elif action_name == actions.USER_ACTION:
            input_line = raw_input("Usuario: ")                    # Obtem Nome de Usuario
        elif action_name == actions.PASS_ACTION:
            input_line = getpass.getpass("Senha: ")                # Obtem Senha
            if self.send_n:
                hashed_password = passwords.hashed_password(input_line, self.salt)[0]      # Faz hash da senha
                input_line = passwords.hash_password(hashed_password, self.n)[0]     
                self.send_n = False
        elif action_name == actions.OLD_PASS_ACTION:
            input_line = getpass.getpass("Senha Antiga: ")          # Usuario Digita a senha antiga
        elif action_name == actions.NEW_PASS_ACTION:
            input_line = getpass.getpass("Nova Senha: ")            # Usuario Digita a nova Senha
        elif action_name == actions.TYPE_ACTION:                    # Recebe a acao selecionada pelo usuario
            input_line = raw_input(">> ") 
        elif action_name == actions.MESSAGE_ACTION:
            input_line = raw_input("Mensagem: ")                    # Usuario digita Mensagem a ser enviada para o servidor
            self.chat(input_line)
                                     
        elif action_name.find(actions.N_ACTION) != -1:
            action, salt_value, n_value = action_name.split(':')
            self.salt = salt_value
            self.n = n_value
            self.send_n = True
            return
        
        else:                                                       
            print action_name                                       
            return

        if len(input_line) == 0:
                input_line = "__"
        self.send(input_line)                                       # Caso necessario, manda resposta para o Servidor

    def handle_connection(self):
        """
        Funcao principal para lidar com a conexao com o Servidor
        """

        action_name = "_"
        while action_name != actions.QUIT_ACTION and len(action_name) != 0:
            action_name = self.receive()

            actions_array = action_name.splitlines()

            for action in actions_array:
                self.take_action(action)
        print "Conexao Finalizada"
        self.socket.close()                                          # Finaliza o socket quando terminar
