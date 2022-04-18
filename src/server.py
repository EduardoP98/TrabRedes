
# my own modules
import sys
import threading            # Para suporte Multi-Thread

import actions
import database
import passwords
import config
import rsa
import binascii

fp = open("log.txt","w")
fp.write("Iniciando Servidor\n")
fp.write("Gerando Chaves\n")
public, private = rsa.generate_keypair(1024)
fp.write("Chaves Geradas com Sucesso\n")
fp.close()

class ClientHandler(threading.Thread):
    def __init__(self, _socket):
        threading.Thread.__init__(self)
        self.socket = _socket
        

    def receive(self):
        """
        receives and returns message from client
        catch an error if connection brakes
        """
        input_line = None
        try:
            input_line = self.socket.recv(config.BUFFER_SIZE)
        except:
            print "Erro Inesperado;", sys.exc_info()[0]
            fp = open("log.txt","w")
            fp.write("Erro Inesperado"+ sys.exc_info()[0] + "\n")
            fp.close()

        return input_line

    def send(self, message):
        """
        sends message through socket to client
        catch an error if connection brakes
        """
        try:
            self.socket.send(message + "\n")
        except:
            print "Erro Inesperado;", sys.exc_info()[0]
            fp = open("log.txt","w")
            fp.write("Erro Inesperado"+ sys.exc_info()[0] + "\n")
            fp.close()

    def register(self):
        """
        register user function
        create user in database if everything succeed
        """
        fp = open("log.txt","w")
        fp.write("Registrando Novo usuario\n")
        print "Registrando..."

        is_taken = True
        username = None

        while is_taken:
            self.send(actions.USERNAME_ACTION)
            username = self.receive()                                   # get username
            if not database.is_username_taken(username):                # check if is free
                is_taken = False
            else:
                self.send("Nome de Usuario ja utilizado, tente outro")
                fp.write("Usuario inseriu um nome que ja esta sendo utilizado\n")

        #username is free

        is_valid = False
        password = None

        while not is_valid:
            self.send(actions.PASSWORD_ACTION)
            password = self.receive()                                   # get password
            self.send("Repita a Senha \n")
            self.send(actions.PASSWORD_ACTION)
            password_repeat = self.receive()                            # get repeated password
            if password_repeat != password:                             # compare them
                self.send("As senhas estao diferentes, Tente Novamente")      # passwords not the same
                fp.write("As senhas que o usuario utilizou nao conferem\n")
                continue                                                # prompt for passwords again
            if passwords.is_password_valid(password):                   # passwords the same -> check if pass is valid
                is_valid = True
            else:
                self.send("Senha Invalida! (Asenha precisa ter mais de 7 caracteres,"    # pass invalid
                          " com pelo menos um numero, uma letra maiuscula e uma minuscula ),"       # send validate pass rules
                          " Tente Outra Senha.")
                fp.write("Usuario utilizou uma senha Invalida\n")

        # password is valid
        fp.write("Criando Hash")
        hashed_password, salt = passwords.hash_password_generate_salt(password)       # create hash
        database.create_user(username, hashed_password, salt)           # create user into database
        fp.write("Criando Usuario na Base de Dados")
        self.send("Usuario Registrado com Sucesso! \nAgora voce pode realizar log in")  # confirm successful registration
        fp.write("Usuario Registrado com Sucesso\n")
        fp.close()
    def login(self):
        """
        login user function
        give an access for successfully logged user
        """
        fp = open("log.txt","w")
        fp.write("Usuario fazendo Login\n")
        print "Entrando..."

        self.send(actions.USERNAME_ACTION)
        username = self.receive()                                       # get username
        fp.write("Usuario" + username + "tentando acesso\n")
        print username

        hashed_password = None
        salt = None
        hash_and_salt = database.get_password(username)                 # get salt and hashed password from database
        if hash_and_salt:
            hashed_password = hash_and_salt[0]
            salt = hash_and_salt[1]

        if not salt:                                                    # user does not exist in database
            salt = passwords.get_salt()                                 # to not reveal if username exist or not
                                                                        # behave naturally with newly generated salt
        nonce = passwords.get_salt()
        self.send(actions.NONCE_ACTION + ":" + salt + ":" + nonce)
        self.send(actions.PASSWORD_ACTION)
        password = self.receive()                                       # get password

        if hashed_password is not None and passwords.check_password(password, nonce, hashed_password):
            self.send("Login Realizado com Sucesso!")                             # passwords matched
            self.logged(username)    
            fp.write(username + "Realizou Login com Sucesso\n")                                   # access granted
        else:
            self.send("Usuario ou Senha incorreto(s)")  
            fp.write("O usuario inseriu a senha incorreta\n")                   # passwords mismatch
        fp.close()

    def change_password(self, username):
        """
        change password user function
        change password for user in database if everything succeed
        """
        fp = open("log.txt", "w")
        fp.write("O Usuario solicitou mudanca de senha\n")
        print "Mudando a senha..."

        is_valid = False
        password = None

        while not is_valid:
            self.send(actions.PASSWORD_ACTION)
            password = self.receive()                                   # get password
            self.send("Repita a Senha\n")
            self.send(actions.PASSWORD_ACTION)
            password_repeat = self.receive()                            # get repeated password
            if password_repeat != password:                             # compare them
                self.send("As senhas sao diferentes, Tente Novamente")      # passwords not the same
                fp.write("As senhas nao conferem\n")
                continue                                                # prompt for passwords again
            if passwords.is_password_valid(password):                   # passwords the same -> check if pass is valid
                is_valid = True
            else:
                self.send("Senha Invalida! (Asenha precisa ter mais de 7 caracteres,"    # pass invalid
                          " com pelo menos um numero, uma letra maiuscula e uma minuscula ),"       # send validate pass rules
                          " Tente Outra Senha.")
                fp.write("O usuario inseriu uma Senha invalida\n")

        # password is valid
        fp.write("Criando a hash para nova senha\n")
        hashed_password, salt = passwords.hash_password_generate_salt(password)       # create hash
        database.change_password(username, hashed_password, salt)           # change password for user into database
        fp.write("Atualizando Senha na Base de Dados\n")
        self.send("Senha alterada com Sucesso! \nAgora voce pode realizar log in com a senha nova")  # confirm successful action
        fp.write("A senha foi alterada com Sucesso\n")
        fp.close()

    def chat(self):
        self.send(actions.MESSAGE_ACTION)
        msg = self.receive() 
        # msg = int(msg.receive(1024).decode())
        # msg = rsa.decrypt(msg,private)   
        print(msg)


    def logged(self, username):
        """
        function to handle logged user
        shows menu with actions for logged users
        """
        fp = open("log.txt","w")
        fp.write(username+"Logou com sucesso\n")
        self.send("Acesso Garantido!")

        while True:
            self.send(" \nO que voce quer fazer? \nChat|Mudar Senha|Sair|Excluir Conta") # menu for logged user
            self.send(actions.TYPE_ACTION)
            current_type = self.receive()                               # get type
            if current_type is None:                                    # if
                print "Conexao Perdida"                                 # error occurred
                return                                                  # leave function
            elif current_type == "Mudar Senha" or current_type == "mudar senha":
                fp.write("O usuario Solicitou mundanca de Senha\n")
                self.change_password(username)
                
            elif current_type == "Excluir Conta" or current_type == "excluir conta":                      # give possibility to resign of the account
                database.delete_user(username)                          # delete user from database
                fp.write("O usuario solicitou exclusao de Conta\n")
                self.send("Sua conta foi removida do Sistema")
                
                return
            elif current_type == "Sair" or current_type == "sair":                              # end of work
                return
            elif current_type == "Chat" or current_type == "chat":
                self.chat()                                              # leave function
            else:
                self.send("Erro: Comando Invalido!\n")
                fp.write("O usuario inseriu um comando invalido\n")
        fp.close()

    def run(self):
        """
        main function when thread starts
        to manage connection with client
        """
        fp = open("log.txt","w")
        fp.write("Usuario Conectado com o Servidor\n")
        self.send("Conectado com o Servidor")

        while True:
            self.send(" \nO que voce quer?\nEntrar|Sair|Registrar")
            self.send(actions.TYPE_ACTION)
            current_type = self.receive()                               # get type
            if current_type is None:                                    # connection broken
                break
            elif current_type == "Entrar" or current_type == "entrar":
                self.login()                                            # login action
            elif current_type == "Registrar" or current_type == "registrar":
                self.register()                                         # register action
            elif current_type == "Sair" or current_type == "sair":
                self.send(actions.QUIT_ACTION)                          # quit action
                break
            else:
                self.send("Erro: Comando Invalido!\n")
                fp.write("O usuario inseriu um comando invalido\n")


        # user quit from server
        print "Cliente Desconectado"
        fp.write("Cliente Desconectado\n")
        self.socket.close()                                             # Close the connection
        fp.write("Conexao encerrada\n")
        fp.close()

