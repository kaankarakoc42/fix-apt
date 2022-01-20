import socket
from argparse import ArgumentParser
from subprocess import check_output,STDOUT

description = "netcat python version"

def run_command(command):
    command = command.rstrip()
    try:
      output = check_output(command,stderr=STDOUT, shell=True)
    except:
      output = "Failed to execute command.\r\n"
    return output

class Netcat:
      
      def __init__(self,args) -> None:
          self.settings = args
          self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
          if self.settings.listen:
             self.listen()
          else:
             self.client_sender()    
             
      def client_sender(self,buffer=None):
          client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          try:
            client.connect((self.settings.target,self.settings.port))
            if self.settings.file:
               with open(self.settings.file,"rb") as file:
                     client.send(file.read())
               exit()
            if buffer:
               client.send(buffer)
            while True:
                recv_len = 1
                response = ""
                while recv_len:
                      data = client.recv(4096).decode("utf8")
                      recv_len = len(data)
                      response+= data
                      if recv_len < 4096:
                         break
                print(response,end="")
                buffer = str(input(""))+"\n"
                client.send(buffer.encode("utf8"))
                
          except Exception as e:
               print("[*] Exception! Exiting.",e)
               client.close()                 
                          
      def listen(self):
          self.socket.bind((self.settings.target,self.settings.port))
          self.socket.listen(5)
          while True:
                client_socket, addr = self.socket.accept()
                if self.settings.upload_destination:
                    file_buffer = ""
                    while True:
                          data = client_socket.recv(1024).decode("utf8")
                          if not data:
                             break
                          else:
                             file_buffer += data
                    print(file_buffer)
                    try:
                         with open(self.settings.upload_destination,"wb") as file:
                              file.write(file_buffer.encode("utf8"))
                         client_socket.send(f"Successfully saved file to {self.settings.upload_destination}\r\n".encode("utf8"))
                    except:
                         client_socket.send(f"Failed to save file to {self.settings.upload_destination}\r\n".encode("utf8"))
                    exit()
                if self.settings.execute:
                     output = run_command(self.settings.execute)
                     client_socket.send(output)
                     
                if self.settings.command:
                   while True:
                         client_socket.send(b"command:#> ")
                         cmd_buffer = ""
                         while "\n" not in cmd_buffer:
                               cmd_buffer += client_socket.recv(1024).decode("utf8")
                               response = run_command(cmd_buffer)
                               if type(response) != bytes:
                                  response = response.encode("utf8")
                               client_socket.send(response)
                               
parser = ArgumentParser(description=description)
parser.add_argument('-l','--listen',action='store_true',default=False)
parser.add_argument('-e','--execute',type=str)
parser.add_argument('-c','--command',action='store_true',default=False)
parser.add_argument('-u','--upload_destination',type=str)
parser.add_argument('-t','--target',default="localhost")
parser.add_argument('-p','--port',type=int,default=1234)
parser.add_argument('-f','--file',type=str)

if __name__ == "__main__":
   args = parser.parse_args()
   Netcat(args)
