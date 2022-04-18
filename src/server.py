
import sys
import threading            # Para suporte Multi-Thread

import actions
import database
import passwords
import config
import rsa
import binascii


"""
  Abre arquivo de Log para iniciar o registro
  Cada etapa do programa registra Log no arquivo "log.txt" 
"""
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
        Recebe a mensagem do cliente e a retorna
        """
        input_line = None
        try:
            input_line = self.socket.recv(config.BUFFER_SIZE)
        except:
            print "Erro Inesperado;", sys.exc_info()[0]
            fp = open("log.txt","a")
            fp.write("Erro Inesperado\n")
            fp.close()

        return input_line

    def send(self, message):
        """
        Manda mensagem para o client via socket
        """
        try:
            self.socket.send(message + "\n")
        except:
            print "Erro Inesperado;", sys.exc_info()[0]
            fp = open("log.txt","a")
            fp.write("Erro Inesperado\n")
            fp.close()

    def register(self):
        """
        Funcao que realiza o registro, criando um usuario na base de dados
        register user function
        
        """
        fp = open("log.txt","a")
        fp.write("Registrando Novo usuario\n")
        print "Registrando..."

        is_taken = True
        username = None

        #Verifica se o Nome de Usuario ja esta na base de dados
        while is_taken:
            self.send(actions.USER_ACTION)
            username = self.receive()                                   
            if not database.is_username_taken(username):              
                is_taken = False
            else:
                self.send("Nome de Usuario ja utilizado, tente outro")
                fp.write("Usuario inseriu um nome que ja esta sendo utilizado\n")

        

        is_valid = False
        password = None

        while not is_valid:
            self.send(actions.PASS_ACTION)
            password = self.receive()                                   # Usuario Digita a senha
            self.send("Repita a Senha \n")
            self.send(actions.PASS_ACTION)
            password_repeat = self.receive()                            # Usuario repete a Senha
            if password_repeat != password:                             # Compara para ver se as duas senhas coincidem
                self.send("As senhas estao diferentes, Tente Novamente")      # Se as senhas nao conferem gera log e avisa o usuario
                fp.write("As senhas que o usuario utilizou nao conferem\n")
                continue                                                # Usuario digita nova senha
            if passwords.is_password_valid(password):                   
                is_valid = True
            else:
                self.send("Senha Invalida! (Asenha precisa ter mais de 7 caracteres,"    # Verifica senha valida conforme as regras definidas
                          " com pelo menos um numero, uma letra maiuscula e uma minuscula ),"       
                          " Tente Outra Senha.")
                fp.write("Usuario utilizou uma senha Invalida\n")

        # Senha Valida
        fp.write("Criando Hash\n")
        hashed_password, salt = passwords.hash_password_generate_salt(password)       # Cria hash para a senha
        database.create_user(username, hashed_password, salt)                         # Cria usuario na base de dados
        fp.write("Criando Usuario na Base de Dados\n")
        self.send("Usuario Registrado com Sucesso! \nAgora voce pode realizar log in")  # Confirmacao de registro
        fp.write("Usuario Registrado com Sucesso\n")
        fp.close()

    def login(self):
        """
        Funcao de Login do Usuario
        
        """
        fp = open("log.txt","a")
        fp.write("Usuario fazendo Login\n")
        print "Entrando..."

        self.send(actions.USERNAME_ACTION)
        username = self.receive()                                       # Obtem Usuario via socket
        print username

        hashed_password = None
        salt = None
        hash_and_salt = database.get_password(username)                 # Verifica hash e salt para usuario na base de dados
        if hash_and_salt:
            hashed_password = hash_and_salt[0]
            salt = hash_and_salt[1]

        if not salt:                                                    # Usuario nao existe na base de dados
            salt = passwords.get_salt()                                 
                                                                        
        n = passwords.get_salt()
        self.send(actions.N_ACTION + ":" + salt + ":" + n)
        self.send(actions.PASS_ACTION)
        password = self.receive()                                       

        if hashed_password is not None and passwords.check_password(password, n, hashed_password):
            self.send("Login Realizado com Sucesso!")                             # Verificacao de senha conforme hash na base de dados
            self.logged(username)    
            fp.write("Usuario Realizou Login com Sucesso\n")                                   # acesso garantido caso a senha confira
        else:
            self.send("Usuario ou Senha incorreto(s)")  
            fp.write("O usuario inseriu a senha incorreta\n")                   # Senha incorreta
        fp.close()

    def change_password(self, username):
        """
        Muda a senha do usuario, registra na base de dados
        """
        fp = open("log.txt", "a")
        fp.write("O Usuario solicitou mudanca de senha\n")
        print "Mudando a senha..."

        is_valid = False
        password = None

        while not is_valid:
            self.send(actions.PASS_ACTION)
            password = self.receive()                                   
            self.send("Repita a Senha\n")
            self.send(actions.PASS_ACTION)                               # Etapa de Validacao da Senha
            password_repeat = self.receive()                           
            if password_repeat != password:                             
                self.send("As senhas sao diferentes, Tente Novamente")      
                fp.write("As senhas nao conferem\n")
                continue                                                
            if passwords.is_password_valid(password):                   
                is_valid = True
            else:
                self.send("Senha Invalida! (Asenha precisa ter mais de 7 caracteres,"   
                          " com pelo menos um numero, uma letra maiuscula e uma minuscula ),"       
                          " Tente Outra Senha.")
                fp.write("O usuario inseriu uma Senha invalida\n")

        
        fp.write("Criando a hash para nova senha\n")
        hashed_password, salt = passwords.hash_password_generate_salt(password)       # Cria Hash para a nova senha
        database.change_password(username, hashed_password, salt)           # Muda a senha do usuario na base de dados
        fp.write("Atualizando Senha na Base de Dados\n")
        self.send("Senha alterada com Sucesso! \nAgora voce pode realizar log in com a senha nova")  # Confirma troca de senha
        fp.write("A senha foi alterada com Sucesso\n")
        fp.close()

    def chat(self):
        """
        Funcao que recebe mensagem enviada do cliente para o servidor via socket
        """
        self.send(actions.MESSAGE_ACTION)
        msg = self.receive()  
        print(msg)


    def logged(self, username):
        """
        Funcao que trata o Usuario que esta logado, mostrando um menu de acoes

        """
        fp = open("log.txt","a")
        fp.write("O usuario Realizou Login com sucesso\n")
        self.send("Acesso Garantido!")

        while True:
            self.send(" \nO que voce quer fazer? \nChat|Mudar Senha|Sair|Excluir Conta") # Menu de Acoes
            self.send(actions.TYPE_ACTION)
            current_type = self.receive()                               # Obtem Comando Indicado no Menu (Usuario digita )
            if current_type is None:                                   
                print "Conexao Perdida" 
                fp.write("Conexao Perdida\n")                               
                return                                                  
            elif current_type == "Mudar Senha" or current_type == "mudar senha":
                fp.write("O usuario Solicitou mundanca de Senha\n")
                self.change_password(username)
                
            elif current_type == "Excluir Conta" or current_type == "excluir conta":      # Opcao para remover a conta do usuario
                database.delete_user(username)                          
                fp.write("O usuario solicitou exclusao de Conta\n")
                self.send("Sua conta foi removida do Sistema")
                
                return
            elif current_type == "Sair" or current_type == "sair":                        # Opcao para sair da conta
                return
            elif current_type == "Chat" or current_type == "chat":
                self.chat()                                                               # Opcao para mandar mensagem
            else:
                self.send("Erro: Comando Invalido!\n")
                fp.write("O usuario inseriu um comando invalido\n")
        fp.close()

    def run(self):
        """
        Funcao principal que trata a execucao das Threads para gerenciar a conexao com o cliente

        """
        fp = open("log.txt","a")
        fp.write("Usuario Conectado com o Servidor\n")
        self.send("Conectado com o Servidor")

        while True:
            self.send(" \nO que voce quer?\nEntrar|Sair|Registrar")
            self.send(actions.TYPE_ACTION)
            current_type = self.receive()                               
            if current_type is None:                                    
                break
            elif current_type == "Entrar" or current_type == "entrar":
                self.login()                                            # Opcao para realizar o Login
            elif current_type == "Registrar" or current_type == "registrar":
                self.register()                                         # Opcao para registrar um novo usuario
            elif current_type == "Sair" or current_type == "sair":
                self.send(actions.QUIT_ACTION)                          # Opcao para sair
                break
            else:
                self.send("Erro: Comando Invalido!\n")
                fp.write("O usuario inseriu um comando invalido\n")


        
        print "Cliente Desconectado"
        fp.write("Cliente Desconectado\n")
        self.socket.close()                                             # Encerra a conexao
        fp.write("Conexao encerrada\n")
        fp.close()

