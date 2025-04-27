import socket
import json

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False

        self.jogadores = []

    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.host, self.port))
            self.running = True

            print(f"Servidor iniciado em {self.host}:{self.port}")

            while self.running:
                data, addr = self.socket.recvfrom(1024)

                if data:
                    message = json.loads(data.decode())

                    if message['type'] == 'connect':
                        for jogador in self.jogadores:
                            if jogador[1] == addr:
                                print(f"Jogador já conectado: {addr}")
                                break
                        else:
                            color = message['data']
                            id = 0
                            for id_jogador, _, _ in self.jogadores:
                                if id_jogador == id:
                                    id += 1
                            
                            self.jogadores.append((id, addr, color))
                            self.socket.sendto(json.dumps({
                                'type': 'connect',
                                'data': id
                            }).encode(), addr)
 
                            print(f"Jogador conectado: {addr} com cor {color}")

                    elif message['type'] == 'connected':
                        # Envia a lista de jogadores atuais para todos os jogadores
                        for _, addr_jogador, _ in self.jogadores:
                            self.socket.sendto(json.dumps({
                                'type': 'player_list',
                                'data': list(self.jogadores)
                            }).encode(), addr_jogador)

                    elif message['type'] == 'disconnect':
                        for jogador in self.jogadores:
                            if jogador[0] == message['id']:
                                self.jogadores.remove(jogador)
                                
                                # Envia a lista de jogadores atuais para todos os jogadores
                                for _, addr_jogador, _ in self.jogadores:
                                    self.socket.sendto(json.dumps({
                                        'type': 'player_list',
                                        'data': list(self.jogadores)
                                    }).encode(), addr_jogador)
                        else:
                            print(f"Jogador não encontrado: {addr}")

                    elif message['type'] == 'move':
                        for jogador in self.jogadores:
                            if jogador[0] == message['id']:
                                # Envia a movimentação para todos os jogadores
                                for _, addr_jogador, _ in self.jogadores:
                                    if addr_jogador != addr:
                                        self.socket.sendto(json.dumps({
                                            'type': 'move',
                                            'id': jogador[0],
                                            'data': message['data']
                                        }).encode(), addr_jogador)
                                break
                        else:
                            print(f"Jogador não encontrado: {addr}")

        except KeyboardInterrupt:
            print("Servidor interrompido pelo usuário.")

        except Exception as e:
            print(f"Erro no servidor: {e}")
        
        finally:
            for jogador in self.jogadores:
                addr = jogador[1]
                self.socket.sendto(json.dumps({
                    'type': 'server_shutdown'
                }).encode(), addr)

            self.stop()

    def stop(self):
        self.running = False

        if self.socket:
            self.socket.close()

        self.socket = None
        self.jogadores = []
        print("Servidor parado.")

if __name__ == "__main__":
    host = input("Digite o endereço IP do servidor (ou pressione Enter para usar o padrão 192.168.1.17): ")
    host = host if host else '192.168.1.17'

    port = input("Digite a porta do servidor (ou pressione Enter para usar o padrão 12345): ")
    port = int(port) if port else 12345

    server = Server(host, port)

    server.start()