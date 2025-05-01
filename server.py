import socket
import json
import time

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False

        self.jogadores = []

        # Atributos do semáforo
        self.semaphore_color = 1  # Começa em vermelho
        self.animation_timer = 0
        self.animation_interval = 45  # Mesmo intervalo usado nos clientes
        self.last_update = time.time()  # Para controlar o tempo de atualização

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
                    
                    elif message['type'] == 'level_update':
                        for jogador in self.jogadores:
                            if jogador[0] == message['id']:
                                # Envia a atualização de nível para todos os jogadores
                                for _, addr_jogador, _ in self.jogadores:
                                    if addr_jogador != addr:
                                        self.socket.sendto(json.dumps({
                                            'type': 'level_update',
                                            'id': jogador[0],
                                            'data': message['data']
                                        }).encode(), addr_jogador)
                                break
                        else:
                            print(f"Jogador não encontrado: {addr}")
                    
                    elif message['type'] == 'event_button':
                        for jogador in self.jogadores:
                            if jogador[0] == message['id']:
                                # Envia o evento para todos os jogadores
                                for _, addr_jogador, _ in self.jogadores:
                                    if addr_jogador != addr:
                                        self.socket.sendto(json.dumps({
                                            'type': 'event_button',
                                            'id': jogador[0],
                                            'data': message['data']
                                        }).encode(), addr_jogador)
                                break
                        else:
                            print(f"Jogador não encontrado: {addr}")
                    
                    elif message['type'] == 'event_door':
                        for _, addr_jogador, _ in self.jogadores:
                            self.socket.sendto(json.dumps({
                                'type': 'event_door',
                                'id': message['id'],
                                'data': message['data']
                            }).encode(), addr_jogador)
                        print(f"Evento de porta recebido de {addr} para nível {message['data']['level']}")

                    elif message['type'] == 'respawn':
                            print(f"Evento de respawn recebido do jogador {message['id']} para {message['data']['player_id']}")
                            for jogador in self.jogadores:
                                if jogador[0] == message['id']:
                                    for _, addr_jogador, _ in self.jogadores:
                                        if addr_jogador != addr:
                                            self.socket.sendto(json.dumps({
                                                'type': 'respawn',
                                                'id': message['id'],
                                                'data': message['data']
                                            }).encode(), addr_jogador)
                                    break
                            else:
                                print(f"Jogador não encontrado: {addr}")

                # Atualiza o semáforo
                current_time = time.time()
                if current_time - self.last_update >= 1/30:  # Atualiza a cada ~33ms (30 FPS)
                    self.animation_timer += 1
                    if self.animation_timer >= self.animation_interval:
                        if self.semaphore_color == 1:
                            self.semaphore_color = 3  # Vermelho -> Verde
                        elif self.semaphore_color == 2:
                            self.semaphore_color = 1  # Amarelo -> Vermelho
                        elif self.semaphore_color == 3:
                            self.semaphore_color = 2  # Verde -> Amarelo
                        self.animation_timer = 0
                        # Envia atualização do semáforo para todos os jogadores
                        for _, addr_jogador, _ in self.jogadores:
                            self.socket.sendto(json.dumps({
                                'type': 'semaphore_update',
                                'data': {
                                    'semaphore_color': self.semaphore_color
                                }
                            }).encode(), addr_jogador)
                    self.last_update = current_time

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
    host = input("Digite o endereço IP do servidor (ou pressione Enter para usar o padrão  192.168.1.12): ")
    host = host if host else '192.168.1.12'

    port = input("Digite a porta do servidor (ou pressione Enter para usar o padrão 12345): ")
    port = int(port) if port else 12345

    server = Server(host, port)

    server.start()