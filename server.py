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

        # Atributos do fogo no nível 2-3
        self.fire_visible = True  # Estado inicial do fogo (visível)
        self.fire_timer = 0  # Temporizador para o fogo
        self.fire_interval = 60  # 2 segundos a 30 FPS (30 frames/seg * 2 seg = 60 frames)

        # Atributos para a plataforma elevador no nível 2-3
        self.elevator_y = 60  
        self.elevator_initial_y = 60
        self.elevator_max_y = 4  # 60 - 56 = 4 (56 pixels acima, conforme Platform.max_y)
        self.elevator_speed = 0.5  # Aumentar velocidade para movimento mais fluido (era 0.5)
        self.player_positions = {}  # Armazena posições dos jogadores: {id: {'x': x, 'y': y, 'level': level}}

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
                                # Atualiza a posição do jogador
                                self.player_positions[jogador[0]] = {
                                    'x': message['data']['x'],
                                    'y': message['data']['y'],
                                    'level': message['data']['level']
                                }
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

                # Atualiza o semáforo e o fogo e o elevador
                current_time = time.time()
                if current_time - self.last_update >= 1/30:  # Atualiza a cada ~33ms (30 FPS)
                    # Atualiza o semáforo
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

                    # Atualiza o fogo no nível 2-3
                    self.fire_timer += 1
                    if self.fire_timer >= self.fire_interval:
                        self.fire_visible = not self.fire_visible
                        self.fire_timer = 0
                        # Envia atualização do fogo para todos os jogadores
                        for _, addr_jogador, _ in self.jogadores:
                            self.socket.sendto(json.dumps({
                                'type': 'fire_update',
                                'data': {
                                    'level': 'level2_3',
                                    'is_visible': self.fire_visible
                                }
                            }).encode(), addr_jogador)

                    # Atualiza a plataforma elevador nos níveis 2-3 e 3-1
                    player_on_platform = False
                    for player_id, pos in self.player_positions.items():
                        if pos['level'] in ['level2_3', 'level3_1']:
                            # Verifica se o jogador está na plataforma (x=158, width=48, y=elevator_y)
                            if (pos['x'] + 12 > 158 and
                                pos['x'] < 158 + 48 and
                                abs(pos['y'] + 13 - self.elevator_y) < 6):  # Tolerância aumentada
                                player_on_platform = True
                                break

                    if player_on_platform and self.elevator_y > self.elevator_max_y:
                        self.elevator_y -= self.elevator_speed  # Sobe
                        if self.elevator_y < self.elevator_max_y:
                            self.elevator_y = self.elevator_max_y
                    elif not player_on_platform and self.elevator_y < self.elevator_initial_y:
                        self.elevator_y += self.elevator_speed  # Desce
                        if self.elevator_y > self.elevator_initial_y:
                            self.elevator_y = self.elevator_initial_y

                    # Envia atualização da posição do elevador para todos os jogadores
                    for _, addr_jogador, _ in self.jogadores:
                        for level in ['level2_3', 'level3_1']:
                            self.socket.sendto(json.dumps({
                                'type': 'elevator_update',
                                'data': {
                                    'level': level,
                                    'y': self.elevator_y
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
    host = input("Digite o endereço IP do servidor (ou pressione Enter para usar o padrão  192.168.1.11): ")
    host = host if host else '192.168.1.11'

    port = input("Digite a porta do servidor (ou pressione Enter para usar o padrão 12345): ")
    port = int(port) if port else 12345

    server = Server(host, port)

    server.start()