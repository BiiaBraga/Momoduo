from pyxel import *
import socket
import json
import threading

# Janela
init(160, 120)

TILE_WIDTH = TILE_HEIGHT = 8
WIDTH = 160
HEIGHT = 120
PLAYER_SPRITE_WIDTH = 12
PLAYER_SPRITE_HEIGHT = 13
PLAYER_SPEED = 4
GRAVITY_SPEED = 4

# Estado do jogo
class GameState:
    def __init__(self):
        self.esta_menu = True
        self.esta_choose_character = False
        self.esta_levels = False

        self.esta_levels_hello = False
        self.option_level_hello = 1
        self.level_hello_1_achivied = False
        self.level_hello_2_achivied = False
        self.level_hello_3_achivied = False
        self.esta_level1_1 = False
        self.esta_level1_2 = False
        self.esta_level1_3 = False

        self.esta_levels_stopmove = False
        self.option_level_stopmove = 1
        self.level_stopmove_1_achivied = False
        self.level_stopmove_2_achivied = False
        self.level_stopmove_3_achivied = False
        self.esta_level2_1 = False
        self.esta_level2_2 = False
        self.esta_level2_3 = False

        self.option_menu = 1
        self.x_seta1 = 42
        self.y_seta1 = 75

        self.option_character = 1
        self.character_color = 1
        self.x_seta2 = 42
        self.y_seta2 = 67

        self.option_level = 0
        self.x_seta3 = 42
        self.y_seta3 = 75
        self.pode_selecionar = False

game_state = GameState()

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = WIDTH
        self.height = HEIGHT
        
    def update(self, target):
        # Centraliza a câmera no player, com limites para não mostrar áreas fora do nível
        self.x = target.x - self.width // 2 + PLAYER_SPRITE_WIDTH // 2
        self.y = target.y - self.height // 2 + PLAYER_SPRITE_HEIGHT // 2

class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

        self.socket = None
        self.id = None # usado para armazenar o endereço do cliente e deferenciar dos outros jogadores

        self.running = False

    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.socket.sendto(json.dumps({
                'type': 'connect',
                'data': game_state.character_color
            }).encode(), (self.server_ip, self.server_port))

            self.running = True

            while self.running:
                data, _ = self.socket.recvfrom(1024)

                if data:
                    message = json.loads(data.decode())
                    
                    if message['type'] == 'connect':
                        self.id = message['data']
                        
                        self.socket.sendto(json.dumps({
                            'type': 'connected'
                        }).encode(), (self.server_ip, self.server_port))

                    elif message['type'] == 'player_list':
                        data = message['data']

                        for id, addr, color in data:
                            if id != self.id:
                                player = PlayerOnline(-10, -10, color, id)
                                players_online.append(player)
                                print(f"Jogador online conectado: {addr} com ID {id} e cor {color}")
                    
                    elif message['type'] == 'server_shutdown':
                        print("Servidor desligado.")
                        break
                    
                    elif message['type'] == 'move':
                        id = message['id']
                        data = message['data']
                        
                        for player in players_online:
                            if player.id == id:
                                player.update(data['x'], data['y'], data['color'], data['andando'], data['level'], data['facing_right'])
                                break
                    
                    elif message['type'] == 'disconnect':
                        id = message['id']
                        
                        for player in players_online:
                            if player.id == id:
                                players_online.remove(player)
                                print(f"Jogador desconectado: {id}")
                                break
                    
                    elif message['type'] == 'level_update':
                        data = message['data']

                        if data['level'] == "level1_1":
                            for item in level1_1.itens:
                                if item.id == data['item_id']:
                                    item.x = data['new_x']
                                    item.y = data['new_y']
                                    break
                        elif data['level'] == "level1_2":
                            for item in level1_2.itens:
                                if item.id == data['item_id']:
                                    item.x = data['new_x']
                                    item.y = data['new_y']
                                    break
                        elif data['level'] == "level1_3":
                            for item in level1_3.itens:
                                if item.id == data['item_id']:
                                    item.x = data['new_x']
                                    item.y = data['new_y']
                                    break
                        elif data['level'] == "level2_1":
                            for item in level2_1.itens:
                                if item.id == data['item_id']:
                                    item.x = data['new_x']
                                    item.y = data['new_y']
                                    break
                        elif data['level'] == "level2_2":
                            for item in level2_2.itens:
                                if item.id == data['item_id']:
                                    item.x = data['new_x']
                                    item.y = data['new_y']
                                    break
                        elif data['level'] == "level2_3":
                            for item in level2_3.itens:
                                if item.id == data['item_id']:
                                    item.x = data['new_x']
                                    item.y = data['new_y']
                                    break
                                
                    elif message['type'] == 'event_button':
                        data = message['data']
                        level = data['level']
                        button_id = data['button_id']
                        is_active = data['is_active']

                        if level == "level1_2" and player.level == "level1_2":
                            for item in level1_2.interactive_itens:
                                if item.id == button_id:
                                    item.is_active = is_active
                                    break
                        elif level == "level1_3" and player.level == "level1_3":
                            for item in level1_3.interactive_itens:
                                if item.id == button_id:
                                    item.is_active = is_active
                                    break
                                
                    elif message['type'] == 'event_door':
                        data = message['data']
                        level = data['level']

                        if level == "level1_1" and player.level == "level1_1":
                            load("levels_hello_stop.pyxres")
                            game_state.esta_level1_1 = False
                            game_state.esta_levels_hello = True
                            game_state.level_hello_1_achivied = True
                            game_state.option_level_hello = 1
                            game_state.x_seta3 = 42
                            game_state.pode_selecionar = False
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                        elif level == "level1_2" and player.level == "level1_2":
                            load("levels_hello_stop.pyxres")
                            game_state.esta_level1_2 = False
                            game_state.esta_levels_hello = True
                            game_state.level_hello_2_achivied = True
                            game_state.option_level_hello = 1
                            game_state.x_seta3 = 42
                            game_state.pode_selecionar = False
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                        elif level == "level1_3" and player.level == "level1_3":
                            load("levels_hello_stop.pyxres")
                            game_state.esta_level1_3 = False
                            game_state.esta_levels_hello = True
                            game_state.level_hello_3_achivied = True
                            game_state.option_level_hello = 1
                            game_state.x_seta3 = 42
                            game_state.pode_selecionar = False
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                        elif level == "level2_1" and player.level == "level2_1":
                            load("levels_hello_stop.pyxres")
                            game_state.esta_level2_1 = False
                            game_state.esta_levels_hello = True
                            game_state.level_stopmove_1_achivied = True
                            game_state.option_level_hello = 1
                            game_state.x_seta3 = 42
                            game_state.pode_selecionar = False
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                        elif level == "level2_2" and player.level == "level2_2":
                            load("levels_hello_stop.pyxres")
                            game_state.esta_level2_2 = False
                            game_state.esta_levels_hello = True
                            game_state.level_stopmove_2_achivied = True
                            game_state.option_level_hello = 1
                            game_state.x_seta3 = 42
                            game_state.pode_selecionar = False
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                        elif level == "level2_3" and player.level == "level2_3":
                            load("levels_hello_stop.pyxres")
                            game_state.esta_level2_3 = False
                            game_state.esta_levels_hello = True
                            game_state.level_stopmove_3_achivied = True
                            game_state.option_level_hello = 1
                            game_state.x_seta3 = 42
                            game_state.pode_selecionar = False
                            player.x, player.y = WIDTH // 2, HEIGHT // 2

        except Exception as e:
            print(f"Erro no cliente: {e}")
        
        finally:
            self.stop()

    def stop(self):
        self.running = False

        if self.socket:
            self.socket.close()

        self.socket = None

    def send_position(self, x, y, color, andando, level, facing_right):
        if self.socket and self.running:
            
            self.socket.sendto(json.dumps({
                'type': 'move',
                'id': self.id,
                'data': {
                    'x': x,
                    'y': y,
                    'color': color,
                    'andando': andando,
                    'level': level,
                    'facing_right': facing_right
                }
            }).encode(), (self.server_ip, self.server_port))
    
    def send_disconnect(self):
        if self.socket and self.running:
            self.socket.sendto(json.dumps({
                'type': 'disconnect',
                'id': self.id
            }).encode(), (self.server_ip, self.server_port))
    
    def send_level_update(self, level, item_id, new_x, new_y):
        if self.socket and self.running:
            self.socket.sendto(json.dumps({
                'type': 'level_update',
                'id': self.id,
                'data': {
                    'level': level,
                    'item_id': item_id,
                    'new_x': new_x,
                    'new_y': new_y
                }
            }).encode(), (self.server_ip, self.server_port))
    
    def send_event_button(self, level, button_id, is_active):
        if self.socket and self.running:
            self.socket.sendto(json.dumps({
                'type': 'event_button',
                'id': self.id,
                'data': {
                    'level': level,
                    'button_id': button_id,
                    'is_active': is_active
                }
            }).encode(), (self.server_ip, self.server_port))
    
    def send_event_door(self, level):
        if self.socket and self.running:
            self.socket.sendto(json.dumps({
                'type': 'event_door',
                'id': self.id,
                'data': {
                    'level': level,
                }
            }).encode(), (self.server_ip, self.server_port))
    
class Player:
    def __init__(self, x: int, y: int, color: int):
        self.x = x
        self.y = y
        self.color = color
        self.speed = PLAYER_SPEED
        self.on_floor = False
        self.upward_speed = 0
        self.andando = False
        self.respawn_x = x
        self.respawn_y = y
        self.facing_right = False  # New attribute to track facing direction
        self.width = PLAYER_SPRITE_WIDTH
        self.height = PLAYER_SPRITE_HEIGHT

        self.level = None  # Atributo para armazenar o nível atual

    def update(self, platforms, itens, players_online):
        self.andando = False

        # Gravidade
        for _ in range(GRAVITY_SPEED):
            previous_y = self.y
            self.y += 1
            did_collide_with_floor = False
            # Verifica colisão com plataformas
            for platform in platforms:
                if collision_detect(self, platform):
                    self.on_floor = True
                    did_collide_with_floor = True
                    self.y = previous_y
                    break
            # Verifica colisão com caixas (caixa1 e caixa2)
            if not did_collide_with_floor:
                for item in itens:
                    if item.id in ["caixa1", "caixa2"] and collision_detect(self, item):
                        self.on_floor = True
                        did_collide_with_floor = True
                        self.y = previous_y
                        break
            if not did_collide_with_floor:
                self.on_floor = False
            
            for player in players_online:
                if collision_detect(self, player):
                    self.on_floor = True
                    did_collide_with_floor = True
                    self.y = previous_y
                    break

        # Verifica se caiu abaixo da tela
        if self.y >= HEIGHT:
            self.respawn()

        # Pulo
        if btnp(KEY_UP) and self.on_floor:
            self.upward_speed = 10

        # Movimento horizontal
        if btn(KEY_LEFT):
            self.andando = True
            self.facing_right = False
            for _ in range(self.speed):
                previous_x = self.x
                self.x -= 1
                # Verifica colisão com a caixa1 e tenta empurrá-la
                for item in itens:
                    if item.id == "caixa1" and collision_detect(self, item):
                        # Tenta mover a caixa para a esquerda
                        temp_item = Item(item.x - 1, item.y, item.width, item.height, item.xPyxel, item.yPyxel, item.id)
                        can_move = True
                        # Verifica colisão da caixa com plataformas
                        for platform in platforms:
                            if collision_detect(temp_item, platform):
                                can_move = False
                                break
                        # Verifica colisão da caixa com outros itens
                        for other_item in itens:
                            if other_item != item and other_item.id in ["caixa2", "caixa1"]:
                                if collision_detect(temp_item, other_item):
                                    can_move = False
                                    break
                        if can_move:
                            item.x -= 1  # Move a caixa
                        else:
                            self.x = previous_x  # Bloqueia o jogador
                            break
                # Verifica colisão com plataformas e caixa2
                for platform in platforms:
                    if collision_detect(self, platform):
                        self.x = previous_x
                        break
                for item in itens:
                    if item.id == "caixa2" and collision_detect(self, item):
                        self.x = previous_x
                        break
                
                # verifica colisão com outros jogadores
                for player in players_online:
                    if collision_detect(self, player):
                        self.x = previous_x
                        break


        if btn(KEY_RIGHT):
            self.andando = True
            self.facing_right = True
            for _ in range(self.speed):
                previous_x = self.x
                self.x += 1
                # Verifica colisão com a caixa1 e tenta empurrá-la
                for item in itens:
                    if item.id == "caixa1" and collision_detect(self, item):
                        # Tenta mover a caixa para a direita
                        temp_item = Item(item.x + 1, item.y, item.width, item.height, item.xPyxel, item.yPyxel, item.id)
                        can_move = True
                        # Verifica colisão da caixa com plataformas
                        for platform in platforms:
                            if collision_detect(temp_item, platform):
                                can_move = False
                                break
                        # Verifica colisão da caixa com outros itens
                        for other_item in itens:
                            if other_item != item and other_item.id in ["caixa2", "caixa1"]:
                                if collision_detect(temp_item, other_item):
                                    can_move = False
                                    break
                        if can_move:
                            item.x += 1  # Move a caixa
                        else:
                            self.x = previous_x  # Bloqueia o jogador
                            break
                # Verifica colisão com plataformas e caixa2
                for platform in platforms:
                    if collision_detect(self, platform):
                        self.x = previous_x
                        break
                for item in itens:
                    if item.id == "caixa2" and collision_detect(self, item):
                        self.x = previous_x
                        break
                
                # verifica colisão com outros jogadores
                for player in players_online:
                    if collision_detect(self, player):
                        self.x = previous_x
                        break

        # Aplicar velocidade de pulo
        if self.upward_speed > 0:
            for _ in range(self.upward_speed):
                previous_y = self.y
                self.y -= 1
                for platform in platforms:
                    if collision_detect(self, platform):
                        self.y = previous_y
                        break
                # Verifica colisão com caixas durante o pulo
                for item in itens:
                    if item.id in ["caixa1", "caixa2"] and collision_detect(self, item):
                        self.y = previous_y
                        self.upward_speed = 0  # Para o pulo ao bater a cabeça na caixa
                        break
            self.upward_speed -= 1

    def respawn(self):
        self.x = self.respawn_x
        self.y = self.respawn_y
        self.upward_speed = 0
        self.on_floor = False
        if game_state.esta_level1_1 and level1_1:
            for item in level1_1.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level1_2 and level1_2:
            for item in level1_2.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level1_3 and level1_3:
            for item in level1_3.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level2_1 and level2_1:
            for item in level2_1.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level2_2 and level2_2:
            for item in level2_2.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level2_3 and level2_3:
            for item in level2_3.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y

    def draw(self, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        sprite_width = PLAYER_SPRITE_WIDTH if not self.facing_right else -PLAYER_SPRITE_WIDTH  # Flip sprite if facing right
        
        if self.color == 1:
            if self.andando:
                blt(screen_x, screen_y, 0, 16, 0, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
            else:
                blt(screen_x, screen_y, 0, 0, 0, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
        elif self.color == 2:
            if self.andando:
                blt(screen_x, screen_y, 0, 16, 16, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
            else:
                blt(screen_x, screen_y, 0, 0, 16, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
        elif self.color == 3:
            if self.andando:
                blt(screen_x, screen_y, 0, 16, 32, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
            else:
                blt(screen_x, screen_y, 0, 0, 32, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
        elif self.color == 4:
            if self.andando:
                blt(screen_x, screen_y, 0, 16, 48, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
            else:
                blt(screen_x, screen_y, 0, 0, 48, sprite_width, PLAYER_SPRITE_HEIGHT, 4)

class PlayerOnline:
    def __init__(self, x, y, color, id):
        self.id = id
        self.x = x
        self.y = y
        self.color = color
        self.speed = PLAYER_SPEED
        self.on_floor = False
        self.upward_speed = 0
        self.andando = False
        self.respawn_x = x
        self.respawn_y = y
        self.facing_right = False  # New attribute to track facing direction
        self.width = PLAYER_SPRITE_WIDTH
        self.height = PLAYER_SPRITE_HEIGHT
        self.level = None

    def update(self, x, y, color, andando, level, facing_right):
        self.x = x
        self.y = y
        self.color = color
        self.andando = andando
        self.level = level
        self.facing_right = facing_right  # Update facing direction
        
    def respawn(self):
        self.x = self.respawn_x
        self.y = self.respawn_y
        self.upward_speed = 0
        self.on_floor = False
        if game_state.esta_level1_1 and level1_1:
            for item in level1_1.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level1_2 and level1_2:
            for item in level1_2.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level1_3 and level1_3:
            for item in level1_3.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level2_1 and level2_1:
            for item in level2_1.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level2_2 and level2_2:
            for item in level2_2.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level2_3 and level2_3:
            for item in level2_3.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y

    def draw(self, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        sprite_width = PLAYER_SPRITE_WIDTH if not self.facing_right else -PLAYER_SPRITE_WIDTH  # Flip sprite if facing right
        
        if self.color == 1:
            if self.andando:
                blt(screen_x, screen_y, 0, 16, 0, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
            else:
                blt(screen_x, screen_y, 0, 0, 0, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
        elif self.color == 2:
            if self.andando:
                blt(screen_x, screen_y, 0, 16, 16, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
            else:
                blt(screen_x, screen_y, 0, 0, 16, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
        elif self.color == 3:
            if self.andando:
                blt(screen_x, screen_y, 0, 16, 32, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
            else:
                blt(screen_x, screen_y, 0, 0, 32, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
        elif self.color == 4:
            if self.andando:
                blt(screen_x, screen_y, 0, 16, 48, sprite_width, PLAYER_SPRITE_HEIGHT, 4)
            else:
                blt(screen_x, screen_y, 0, 0, 48, sprite_width, PLAYER_SPRITE_HEIGHT, 4)

class Platform:
    def __init__(self, x: int, y: int, width: int, height: int, xPyxel: int, yPyxel: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.xPyxel = xPyxel
        self.yPyxel = yPyxel

    def draw(self, camera):
        # Desenha a plataforma do player.pyxres com offset da câmera
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        # Assumindo que o sprite da plataforma está em (u=0, v=64) no player.pyxres
        # Ajuste u, v, w, h conforme o sprite no player.pyxres
        blt(screen_x, screen_y, 0, self.xPyxel, self.yPyxel, self.width, self.height, 1)

class Item:
    def __init__(self, x: int, y: int, width: int, height: int, xPyxel: int, yPyxel: int, id: str = None):
        self.x = x
        self.y = y
        self.initial_x = x
        self.initial_y = y
        self.width = width
        self.height = height
        self.xPyxel = xPyxel
        self.yPyxel = yPyxel
        self.id = id
        self.collected = False
        # Atributos para animação do choque
        self.facing_up = True
        self.animation_timer = 0
        self.animation_interval = 7
        # Atributos para movimento da gosma
        if self.id == "gosma":
            self.moving_right = False
            self.move_speed = 0.5
            self.move_distance = 60
            self.min_x = self.initial_x - self.move_distance
            self.max_x = self.initial_x

    def update(self, player):
        # Atualiza a chave se coletada
        if self.id == "key" and self.collected:
            self.x = player.x + PLAYER_SPRITE_WIDTH // 2 - self.width // 2
            self.y = player.y - self.height - 5
            client.send_level_update(player.level, self.id, self.x, self.y)
        # Animação do choque
        if self.id == "chock":
            self.animation_timer += 1
            if self.animation_timer >= self.animation_interval:
                self.facing_up = not self.facing_up
                self.animation_timer = 0
        # Movimento da gosma
        if self.id == "gosma":
            if self.moving_right:
                self.x += self.move_speed
                if self.x >= self.max_x:
                    self.x = self.max_x
                    self.moving_right = False
            else:
                self.x -= self.move_speed
                if self.x <= self.min_x:
                    self.x = self.min_x
                    self.moving_right = True

    def check_collision(self, player):
        a_left_edge = player.x
        a_top_edge = player.y
        a_right_edge = player.x + (PLAYER_SPRITE_WIDTH - 1)
        a_bottom_edge = player.y + (PLAYER_SPRITE_HEIGHT - 1)
        b_left_edge = self.x
        b_top_edge = self.y
        b_right_edge = self.x + (self.width - 1)
        b_bottom_edge = self.y + (self.height - 1)
        if a_top_edge > b_bottom_edge or b_top_edge > a_bottom_edge or a_left_edge > b_right_edge or b_left_edge > a_right_edge:
            return False
        return True

    def draw(self, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        if self.id == "chock":
            if self.facing_up:
                blt(screen_x, screen_y, 0, 11, 64, self.width, self.height, 1)
            else:
                blt(screen_x, screen_y, 0, 0, 64, self.width, self.height, 1)
        elif self.id == "gosma":
            # Inverte o sprite horizontalmente se estiver movendo para a direita
            sprite_width = self.width if not self.moving_right else -self.width
            blt(screen_x, screen_y, 0, self.xPyxel, self.yPyxel, sprite_width, self.height, 1)
        else:
            blt(screen_x, screen_y, 0, self.xPyxel, self.yPyxel, self.width, self.height, 1)

class InteractiveItem:
    def __init__(self, x: int, y: int, width: int, height: int, xPyxel: int, yPyxel: int, id: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.xPyxel = xPyxel
        self.yPyxel = yPyxel
        self.id = id  # Identificador único para o item
        self.is_active = False  # Estado do botão (pressionado ou não)

    def draw(self, camera):
        # Desenha o item com offset da câmera
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        # Muda o sprite dependendo se está ativo ou não
        if self.is_active:
            # Sprite do botão pressionado
            blt(screen_x, screen_y, 0, 92, 45, self.width, self.height, 1)
        else:
            # Sprite do botão não pressionado
            blt(screen_x, screen_y, 0, self.xPyxel, self.yPyxel, self.width, self.height, 1)

    def check_collision(self, player):
        # Verifica se o jogador está colidindo com o item
        a_left_edge = player.x
        a_top_edge = player.y
        a_right_edge = player.x + (PLAYER_SPRITE_WIDTH - 1)
        a_bottom_edge = player.y + (PLAYER_SPRITE_HEIGHT - 1)

        b_left_edge = self.x
        b_top_edge = self.y
        b_right_edge = self.x + (self.width - 1)
        b_bottom_edge = self.y + (self.height - 1)

        if a_top_edge > b_bottom_edge or b_top_edge > a_bottom_edge or a_left_edge > b_right_edge or b_left_edge > a_right_edge:
            return False
        return True

class Level1_1:
    def __init__(self):
        self.platforms = [
            #plataforma principal
            Platform(0, 64, 16, 14, 32, 0), Platform(16, 64, 16, 14, 32, 16), Platform(32, 64, 16, 14, 32, 16), 
            Platform(48, 64, 16, 14, 32, 16), Platform(64, 64, 16, 14, 32, 16), Platform(80, 64, 16, 14, 32, 16),
            Platform(96, 64, 16, 14, 32, 16), Platform(112, 64, 16, 14, 32, 16), Platform(128, 64, 16, 14, 32, 16), 
            Platform(144, 64, 16, 14, 32, 16), Platform(160, 64, 16, 14, 32, 16), Platform(176, 64, 16, 14, 32, 16),
            Platform(192, 64, 16, 14, 32, 16), Platform(208, 64, 16, 14, 32, 16), Platform(224, 64, 16, 14, 32, 16), 
            Platform(240, 64, 16, 14, 32, 32), 

            #plataforma suspensa
            Platform(91, 36, 16, 14, 32, 0), Platform(107, 36, 16, 14, 32, 16), Platform(123, 36, 16, 14, 32, 16), 
            Platform(139, 36, 16, 14, 32, 32),
        ]
        self.itens = [

            #flor vermelha
            Item(10, 60, 5, 4, 90, 52), Item(50, 60, 5, 4, 90, 52), Item(90, 60, 5, 4, 90, 52),
            Item(130, 60, 5, 4, 90, 52), Item(170, 60, 5, 4, 90, 52), Item(210, 60, 5, 4, 90, 52),
            
            #flor amarela
            Item(30, 60, 5, 4, 98, 52), Item(70, 60, 5, 4, 98, 52), Item(110, 60, 5, 4, 98, 52),
            Item(150, 60, 5, 4, 98, 52), Item(190, 60, 5, 4, 98, 52),

            #chave e porta
            Item(117, 29, 16, 7, 90, 34, "key"),
            Item(230, 50, 16, 14, 72, 40, "door")
        ]
        self.camera = Camera()

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        load("levels_hello_stop.pyxres")
                        game_state.esta_level1_1 = False
                        game_state.esta_levels_hello = True
                        game_state.level_hello_1_achivied = True
                        game_state.option_level_hello = 1
                        game_state.x_seta3 = 42
                        game_state.pode_selecionar = False
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 117, 29
                        client.send_event_door("level1_1")
                        break

    def draw(self):

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)

class Level1_2:
    def __init__(self):
        self.platforms = [

            #plataforma principal 1
            Platform(0, 64, 16, 14, 32, 0), Platform(16, 64, 16, 14, 32, 16), Platform(32, 64, 16, 14, 32, 16), 
            Platform(48, 64, 16, 14, 32, 16), Platform(64, 64, 16, 14, 32, 32), 

            #plataforma principal 2
            Platform(210, 64, 16, 14, 32, 0), Platform(226, 64, 16, 14, 32, 16), Platform(242, 64, 16, 14, 32, 16), 
            Platform(258, 64, 16, 14, 32, 16), Platform(274, 64, 16, 14, 32, 16), Platform(290, 64, 16, 14, 32, 32),
            
            #plataforma azul
            Platform(80, 64, 0, 4, 120, 80)
        ]

        self.itens = [

            #flor vermelha
            Item(10, 60, 5, 4, 90, 52), Item(50, 60, 5, 4, 90, 52), Item(240, 60, 5, 4, 90, 52),

            #flor amarela
            Item(30, 60, 5, 4, 98, 52), Item(280, 60, 5, 4, 98, 52), Item(53, 40, 20, 20, 65, 0),
            Item(204, 40, 20, 20, 65, 0),
            
            #chave e porta
            Item(150, 53, 16, 7, 90, 34, "key"),
            Item(250, 50, 16, 14, 72, 40, "door")
        ]
        self.interactive_itens = [
            InteractiveItem(67, 61, 4, 2, 92, 45, "button1"),
            Item(66, 63, 6, 1, 91, 47),
            InteractiveItem(217, 61, 4, 2, 92, 45, "button1"),
            Item(216, 63, 6, 1, 91, 47)
        ]
        self.camera = Camera()
        self.bridge_growth_speed = 2
        self.bridge_max_width = 110
        self.bridge_min_width = 0

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        load("levels_hello_stop.pyxres")
                        game_state.esta_level1_2 = False
                        game_state.esta_levels_hello = True
                        game_state.level_hello_2_achivied = True
                        game_state.option_level_hello = 1
                        game_state.x_seta3 = 42
                        game_state.pode_selecionar = False
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 150, 53
                        client.send_event_door("level1_2")
                        break

        for item in self.interactive_itens:
            if isinstance(item, InteractiveItem):
                item.is_active = item.check_collision(player)
                
                if not item.is_active:
                    for online_player in players_online:
                        if item.check_collision(online_player):
                            item.is_active = True
                            break

        bridge = self.platforms[11]
        if any(item.is_active for item in self.interactive_itens if isinstance(item, InteractiveItem) and item.id == "button1"):
            if bridge.width < self.bridge_max_width:
                bridge.width += self.bridge_growth_speed
                if bridge.width > self.bridge_max_width:
                    bridge.width = self.bridge_max_width
        else:
            if bridge.width > self.bridge_min_width:
                bridge.width -= self.bridge_growth_speed
                if bridge.width < self.bridge_min_width:
                    bridge.width = self.bridge_min_width

    def draw(self):
        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)
        for item in self.interactive_itens:
            item.draw(self.camera)

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

class Level1_3:
    def __init__(self):
        self.platforms = [
            # Plataforma principal 1
            Platform(0, 64, 16, 14, 32, 0),
            Platform(16, 64, 16, 14, 32, 16),
            Platform(32, 64, 16, 14, 32, 16),
            Platform(48, 64, 16, 14, 32, 16),
            Platform(64, 64, 16, 14, 32, 16),
            Platform(80, 64, 16, 14, 32, 16),
            Platform(96, 64, 16, 14, 32, 16),
            Platform(112, 64, 16, 14, 32, 16),
            Platform(128, 64, 16, 14, 32, 16),
            Platform(144, 64, 16, 14, 32, 16),
            Platform(160, 64, 16, 14, 32, 16),
            Platform(176, 64, 16, 14, 32, 16),
            Platform(192, 64, 16, 14, 32, 16),
            Platform(208, 64, 16, 14, 32, 16),
            Platform(224, 64, 16, 14, 32, 16),
            Platform(240, 64, 16, 14, 32, 32),

            # Plataforma principal 2
            Platform(308, 64, 16, 14, 32, 0),
            Platform(324, 64, 16, 14, 32, 16),
            Platform(340, 64, 16, 14, 32, 16),
            Platform(356, 64, 16, 14, 32, 16),
            Platform(372, 64, 16, 14, 32, 32),

            # Plataformas azuis verticais
            Platform(95, -14, 4, 24, 50, 0),  # Plataforma 1 (vertical)
            Platform(125, -14, 4, 24, 50, 0), # Plataforma 2 (vertical)
            Platform(155, -14, 4, 24, 50, 0), # Plataforma 3 (vertical)
            Platform(185, -14, 4, 24, 50, 0), # Plataforma 4 (vertical)
            Platform(256, 64, 0, 4, 120, 88), # Plataforma 5 (horizontal, ponte)

            # Plataforma suspensa principal
            Platform(90, 10, 16, 14, 32, 0),
            Platform(106, 10, 16, 14, 32, 16),
            Platform(122, 10, 16, 14, 32, 16),
            Platform(138, 10, 16, 14, 32, 16),
            Platform(150, 10, 16, 14, 32, 16),
            Platform(166, 10, 16, 14, 32, 16),
            Platform (182, 10, 16, 14, 32, 32),

            # Mini plataformas suspensas
            Platform(40, 36, 16, 14, 0, 96),
            Platform(65, 23, 16, 14, 0, 96),
            Platform(215, 10, 16, 14, 0, 96),
            Platform(245, 23, 16, 14, 0, 96),
            Platform(275, 36, 16, 14, 0, 96)
        ]

        self.itens = [
            Item(10, 60, 5, 4, 90, 52),  # Flor vermelha
            Item(50, 60, 5, 4, 90, 52),
            Item(110, 60, 5, 4, 90, 52),
            Item(171, 60, 5, 4, 90, 52),
            Item(220, 60, 5, 4, 90, 52),
            Item(340, 60, 5, 4, 90, 52),
            Item(30, 60, 5, 4, 98, 52),  # Flor amarela
            Item(70, 60, 5, 4, 98, 52),
            Item(142, 60, 5, 4, 98, 52),
            Item(200, 60, 5, 4, 98, 52),
            Item(240, 60, 5, 4, 98, 52),
            Item(320, 60, 5, 4, 98, 52),
            Item(375, 60, 5, 4, 98, 52),
            Item(166, 0, 16, 7, 90, 34, "key"),  # Chave
            Item(350, 50, 16, 14, 72, 40, "door")  # Porta
        ]
        self.interactive_itens = [
            InteractiveItem(96, 61, 4, 2, 92, 45, "button2"),
            Item(95, 63, 6, 1, 91, 47),
            InteractiveItem(126, 61, 4, 2, 92, 45, "button3"),
            Item(125, 63, 6, 1, 91, 47),
            InteractiveItem(156, 61, 4, 2, 92, 45, "button4"),
            Item(155, 63, 6, 1, 91, 47),
            InteractiveItem(186, 61, 4, 2, 92, 45, "button5"),
            Item(185, 63, 6, 1, 91, 47),
            InteractiveItem(281, 33, 4, 2, 92, 45, "button6"),
            Item(280, 35, 6, 1, 91, 47)
        ]
        self.camera = Camera()
        self.platform_speed = 2  # Velocidade de movimento das plataformas
        self.vertical_min_y = -14  # Posição elevada das plataformas verticais
        self.vertical_max_y = 64   # Posição descida das plataformas verticais
        self.bridge_growth_speed = 2  # Velocidade de crescimento da ponte
        self.bridge_max_width = 52    # Largura máxima da ponte
        self.bridge_min_width = 0     # Largura mínima da ponte

    def update(self, player, game_state):
        self.camera.update(player)
        
        # Atualiza itens (chave, porta, etc.)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        load("levels_hello_stop.pyxres")
                        game_state.esta_level1_3 = False
                        game_state.level_hello_3_achivied = True
                        game_state.esta_levels_hello = True
                        game_state.option_level_hello = 1
                        game_state.x_seta3 = 42
                        game_state.pode_selecionar = False
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 166, 0
                        client.send_event_door("level1_3")
                        break

        # Atualiza estado dos botões
        for item in self.interactive_itens:
            if isinstance(item, InteractiveItem):
                item.is_active = item.check_collision(player)
                
                if not item.is_active:
                    for online_player in players_online:
                        if item.check_collision(online_player):
                            item.is_active = True
                            break

        # Mapeia botões às plataformas
        button_to_platform = {
            "button2": self.platforms[21],  # Plataforma 1
            "button3": self.platforms[22],  # Plataforma 2
            "button4": self.platforms[23],  # Plataforma 3
            "button5": self.platforms[24],  # Plataforma 4
            "button6": self.platforms[25]   # Plataforma 5 (ponte)
        }

        # Atualiza plataformas verticais (botões 2, 3, 4, 5)
        for button_id, platform in list(button_to_platform.items())[:-1]:  # Exclui button6
            button_active = any(
                item.is_active and item.id == button_id
                for item in self.interactive_itens
                if isinstance(item, InteractiveItem)
            )
            if button_active:
                # Move plataforma para baixo
                if platform.y < self.vertical_max_y:
                    platform.y -= self.platform_speed
                    if platform.y > self.vertical_max_y:
                        platform.y = self.vertical_max_y
            else:
                # Move plataforma para cima
                if platform.y < self.vertical_min_y:
                    platform.y += self.platform_speed
                    if platform.y > self.vertical_min_y:
                        platform.y = self.vertical_min_y

        # Atualiza plataforma horizontal (botão 6)
        bridge = button_to_platform["button6"]
        button6_active = any(
            item.is_active and item.id == "button6"
            for item in self.interactive_itens
            if isinstance(item, InteractiveItem)
        )
        if button6_active:
            # Cresce a ponte
            if bridge.width < self.bridge_max_width:
                bridge.width += self.bridge_growth_speed
                if bridge.width > self.bridge_max_width:
                    bridge.width = self.bridge_max_width
        else:
            # Encolhe a ponte
            if bridge.width > self.bridge_min_width:
                bridge.width -= self.bridge_growth_speed
                if bridge.width < self.bridge_min_width:
                    bridge.width = self.bridge_min_width

    def draw(self):
        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)
        for item in self.interactive_itens:
            item.draw(self.camera)
        
        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

class Level2_1:
    def __init__(self):
        self.platforms = [
            # Plataforma principal 1
            Platform(0, 64, 16, 14, 32, 0), Platform(16, 64, 16, 14, 32, 16), Platform(32, 64, 16, 14, 32, 16), 
            Platform(48, 64, 16, 14, 32, 16), Platform(64, 64, 16, 14, 32, 16), Platform(80, 64, 16, 14, 32, 16),
            Platform(96, 64, 16, 14, 32, 16), Platform(112, 64, 16, 14, 32, 16), Platform(128, 64, 16, 14, 32, 16), 
            Platform(144, 64, 16, 14, 32, 16), Platform(160, 64, 16, 14, 32, 16), Platform(176, 64, 16, 14, 32, 16),
            Platform(192, 64, 16, 14, 32, 16), Platform(208, 64, 16, 14, 32, 16), Platform(224, 64, 16, 14, 32, 16), 
            Platform(240, 64, 16, 14, 32, 16), Platform(256, 64, 16, 14, 32, 16), Platform(272, 64, 16, 14, 32, 16), 
            Platform(288, 64, 16, 14, 32, 16), Platform(304, 64, 16, 14, 32, 16), Platform(320, 64, 16, 14, 32, 16), 
            Platform(336, 64, 16, 14, 32, 16), Platform(352, 64, 16, 14, 32, 16), Platform(368, 64, 16, 14, 32, 16),
            Platform(384, 64, 16, 14, 32, 16), Platform(400, 64, 16, 14, 32, 16), Platform(416, 64, 16, 14, 32, 16), 
            Platform(432, 64, 16, 14, 32, 16), Platform(448, 64, 16, 14, 32, 16), Platform(464, 64, 16, 14, 32, 32)
        ]

        self.itens = [

            #flor vermelha
            Item(10, 60, 5, 4, 90, 52), Item(50, 60, 5, 4, 90, 52), Item(90, 60, 5, 4, 90, 52), Item(130, 60, 5, 4, 90, 52), 
            Item(170, 60, 5, 4, 90, 52), Item(210, 60, 5, 4, 90, 52), Item(250, 60, 5, 4, 90, 52), Item(290, 60, 5, 4, 90, 52), 
            Item(330, 60, 5, 4, 90, 52), Item(370, 60, 5, 4, 90, 52), Item(410, 60, 5, 4, 90, 52),

            #flor amarela
            Item(30, 60, 5, 4, 98, 52), Item(70, 60, 5, 4, 98, 52), Item(110, 60, 5, 4, 98, 52), Item(150, 60, 5, 4, 98, 52), 
            Item(190, 60, 5, 4, 98, 52), Item(230, 60, 5, 4, 98, 52), Item(270, 60, 5, 4, 98, 52), Item(310, 60, 5, 4, 98, 52), 
            Item(350, 60, 5, 4, 98, 52), Item(390, 60, 5, 4, 98, 52), Item(430, 60, 5, 4, 98, 52),

            #chave e porta
            Item(117, 29, 16, 7, 90, 34, "key"), Item(450, 50, 16, 14, 72, 40, "door"),

            #fantasma
            Item(-60, 10, 30, 27, 90, 0, "ghost")
        ]
        self.camera = Camera()

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        load("levels_hello_stop.pyxres")
                        game_state.esta_level2_1 = False
                        game_state.esta_levels_stopmove = True
                        game_state.level_stopmove_1_achivied = True
                        game_state.option_level_stopmove = 1
                        game_state.x_seta3 = 42
                        game_state.pode_selecionar = False
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 117, 29
                        client.send_event_door("level2_1")
                        break

    def draw(self):

        # Define a posição fixa do texto no mundo do jogo
        text_world_x = -60  # Posição x no mundo
        text_world_y = 50  # Posição y no mundo
        # Ajusta a posição do texto com base na câmera
        screen_x = text_world_x - self.camera.x
        screen_y = text_world_y - self.camera.y

        # Desenha o texto na posição ajustada
        text(screen_x, screen_y, "Don't move", 1)
        text(screen_x+8, screen_y+10, "together!", 1)

        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)
        
class Level2_2:
    def __init__(self):
        self.platforms = [

            #base inferior 1
            Platform(0, 64, 16, 14, 32, 0), Platform(16, 64, 16, 14, 32, 16), Platform(32, 64, 16, 14, 32, 16), 
            Platform(48, 64, 16, 14, 32, 16), Platform(64, 64, 16, 14, 32, 16), Platform(80, 64, 16, 14, 32, 16),
            Platform(96, 64, 16, 14, 32, 16), Platform(112, 64, 16, 14, 32, 16), Platform(128, 64, 16, 14, 32, 16), 
            Platform(144, 64, 16, 14, 32, 48), Platform(160, 64, 16, 14, 32, 48), Platform(176, 64, 16, 14, 32, 48),
            Platform(192, 64, 16, 14, 32, 48), Platform(208, 64, 16, 14, 32, 48), Platform(224, 64, 16, 14, 32, 48), 
            Platform(240, 64, 16, 14, 32, 48), 

            #base inferior 2
            Platform(384, 64, 16, 14, 32, 0), Platform(400, 64, 16, 14, 32, 16), Platform(416, 64, 16, 14, 32, 16), 
            Platform(432, 64, 16, 14, 32, 16), Platform(448, 64, 16, 14, 32, 16), Platform(464, 64, 16, 14, 32, 16),  
            Platform(480, 64, 16, 14, 32, 16), Platform(480, 64, 16, 14, 32, 16), Platform(496, 64, 16, 14, 32, 16), 
            Platform(512, 64, 16, 14, 32, 16), Platform(528, 64, 16, 14, 32, 16), Platform(544, 64, 16, 14, 32, 16), 
            Platform(560, 64, 16, 14, 32, 16), Platform(576, 64, 16, 14, 32, 16), Platform(592, 64, 16, 14, 32, 16), 
            Platform(608, 64, 16, 14, 32, 16), Platform(624, 64, 16, 14, 32, 16), Platform(640, 64, 16, 14, 32, 16), 
            Platform(652, 64, 16, 14, 32, 32),

            # primeira montanha
            Platform(144, 50, 16, 16, 24, 96), Platform(177, 34, 16, 16, 24, 96), Platform(192, 18, 16, 16, 24, 96),
            Platform(208, 2, 16, 16, 24, 96), Platform(256, 2, 16, 16, 72, 96), Platform(160, 50, 16, 16, 48, 96), 
            Platform(224, 2, 16, 16, 48, 96), Platform(240, 2, 16, 16, 48, 96), Platform(176, 50, 16, 16, 72, 72), 
            Platform(192, 50, 16, 16, 72, 72), Platform(208, 50, 16, 16, 72, 72), Platform(224, 50, 16, 16, 72, 72), 
            Platform(240, 50, 16, 16, 72, 72), Platform(192, 34, 16, 16, 72, 72), Platform(208, 34, 16, 16, 72, 72), 
            Platform(208, 18, 16, 16, 72, 72), Platform(224, 34, 16, 16, 72, 72), Platform(224, 18, 16, 16, 72, 72), 
            Platform(224, 34, 16, 16, 72, 72), Platform(240, 34, 16, 16, 72, 72), Platform(240, 18, 16, 16, 72, 72), 
            Platform(256, 64, 16, 14, 48, 74), Platform(256, 18, 16, 16, 96, 72), Platform(256, 34, 16, 16, 96, 72), 
            Platform(256, 50, 16, 16, 96, 72),

            #base final
            Platform(668, 30, 16, 14, 32, 0), Platform(684, 30, 16, 14, 32, 16), Platform(700, 30, 16, 14, 32, 16), 
            Platform(716, 30, 16, 14, 32, 32)
            
        ]

        self.itens = [

            #flor vermelha
            Item(160, 46, 5, 4, 90, 52), Item(250, -2, 5, 4, 90, 52), 
            
            #flor amarela
            Item(228, -2, 5, 4, 98, 52), 

            #gosma que mata
            Item(130, 58, 8, 6, 40, 66, "gosma"),

            #chave e a porta
            Item(440, -25, 16, 7, 90, 34, "key"),
            Item(690, 16, 16, 14, 72, 40, "door"),

            #choque
            Item(272, 64, 9, 6, 0, 64, "chock"), Item(281, 64, 9, 6, 0, 64, "chock"), Item(290, 64, 9, 6, 0, 64, "chock"), 
            Item(299, 64, 9, 6, 0, 64, "chock"), Item(308, 64, 9, 6, 0, 64, "chock"), Item(317, 64, 9, 6, 0, 64, "chock"),
            Item(326, 64, 9, 6, 0, 64, "chock"), Item(335, 64, 9, 6, 0, 64, "chock"), Item(344, 64, 9, 6, 0, 64, "chock"),
            Item(353, 64, 9, 6, 0, 64, "chock"), Item(362, 64, 9, 6, 0, 64, "chock"), Item(371, 64, 9, 6, 0, 64, "chock"), 
            Item(380, 64, 4, 6, 0, 64, "chock"),

            #trampolim
            Item(420, 56, 9, 8, 24, 64, "trampoline"), Item(429, 56, 9, 8, 24, 64, "trampoline"), Item(438, 56, 9, 8, 24, 64, "trampoline"),
            Item(447, 56, 9, 8, 24, 64, "trampoline"), Item(456, 56, 9, 8, 24, 64, "trampoline"), Item(465, 56, 9, 8, 24, 64, "trampoline"),    # posição estimada em cima da segunda plataforma

            #Caixas
             Item(540, 52, 12, 12, 72, 24, "caixa1"), Item(620, 35, 16, 29, 56, 27, "caixa2")

        ]
        self.camera = Camera()
        self.bridge_growth_speed = 2
        self.bridge_max_width = 110
        self.bridge_min_width = 0

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        load("levels_hello_stop.pyxres")
                        game_state.esta_level2_2 = False
                        game_state.esta_levels_stopmove = True
                        game_state.level_stopmove_2_achivied = True
                        game_state.option_level_stopmove = 1
                        game_state.x_seta3 = 42
                        game_state.pode_selecionar = False
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 440, -25
                        client.send_event_door("level2_2")
                        break
            if item.id == "gosma" and item.check_collision(player):
                player.respawn()
            if item.id == "chock" and item.check_collision(player):
                player.respawn()
            if item.id == "trampoline" and item.check_collision(player):
                player.upward_speed = 15  # aumenta o valor pra um pulo mais forte

    def draw(self):
        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

class Level2_3:
    def __init__(self):
        self.platforms = [
            # Plataforma principal 1
            Platform(0, 64, 16, 14, 32, 0), Platform(16, 64, 16, 14, 32, 16), Platform(32, 64, 16, 14, 32, 16), 
            Platform(48, 64, 16, 14, 32, 16), Platform(64, 64, 16, 14, 32, 16), Platform(80, 64, 16, 14, 32, 16),
            Platform(96, 64, 16, 14, 32, 16), Platform(112, 64, 16, 14, 32, 16), Platform(128, 64, 16, 14, 32, 16), 
            Platform(144, 64, 16, 14, 32, 16), Platform(160, 64, 16, 14, 32, 16), Platform(176, 64, 16, 14, 32, 16),
            Platform(192, 64, 16, 14, 32, 16), Platform(208, 64, 16, 14, 32, 16), Platform(224, 64, 16, 14, 32, 16), 
            Platform(240, 64, 16, 14, 32, 16), Platform(256, 64, 16, 14, 32, 16), Platform(272, 64, 16, 14, 32, 16), 
            Platform(288, 64, 16, 14, 32, 16), Platform(304, 64, 16, 14, 32, 16), Platform(320, 64, 16, 14, 32, 16), 
            Platform(336, 64, 16, 14, 32, 16), Platform(352, 64, 16, 14, 32, 16), Platform(368, 64, 16, 14, 32, 16),
            Platform(384, 64, 16, 14, 32, 16), Platform(400, 64, 16, 14, 32, 16), Platform(416, 64, 16, 14, 32, 16), 
            Platform(432, 64, 16, 14, 32, 16), Platform(448, 64, 16, 14, 32, 16), Platform(464, 64, 16, 14, 32, 32)
        ]

        self.itens = [

            #flor vermelha
            Item(10, 60, 5, 4, 90, 52), Item(50, 60, 5, 4, 90, 52), Item(90, 60, 5, 4, 90, 52), Item(130, 60, 5, 4, 90, 52), 
            Item(170, 60, 5, 4, 90, 52), Item(210, 60, 5, 4, 90, 52), Item(250, 60, 5, 4, 90, 52), Item(290, 60, 5, 4, 90, 52), 
            Item(330, 60, 5, 4, 90, 52), Item(370, 60, 5, 4, 90, 52), Item(410, 60, 5, 4, 90, 52),

            #flor amarela
            Item(30, 60, 5, 4, 98, 52), Item(70, 60, 5, 4, 98, 52), Item(110, 60, 5, 4, 98, 52), Item(150, 60, 5, 4, 98, 52), 
            Item(190, 60, 5, 4, 98, 52), Item(230, 60, 5, 4, 98, 52), Item(270, 60, 5, 4, 98, 52), Item(310, 60, 5, 4, 98, 52), 
            Item(350, 60, 5, 4, 98, 52), Item(390, 60, 5, 4, 98, 52), Item(430, 60, 5, 4, 98, 52),

            #chave e porta
            Item(117, 29, 16, 7, 90, 34, "key"), Item(450, 50, 16, 14, 72, 40, "door")
        ]
        self.camera = Camera()

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        load("levels_hello_stop.pyxres")
                        game_state.esta_level2_3 = False
                        game_state.esta_levels_stopmove = True
                        game_state.level_stopmove_3_achivied = True
                        game_state.option_level_stopmove = 1
                        game_state.x_seta3 = 42
                        game_state.pode_selecionar = False
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 117, 29
                        client.send_event_door("level2_3")
                        break

    def draw(self):

        # Define a posição fixa do texto no mundo do jogo
        text_world_x = -60  # Posição x no mundo
        text_world_y = 50  # Posição y no mundo
        # Ajusta a posição do texto com base na câmera
        screen_x = text_world_x - self.camera.x
        screen_y = text_world_y - self.camera.y

        # Desenha o texto na posição ajustada
        text(screen_x, screen_y, "Look at the", 1)
        text(screen_x+8, screen_y+10, "ghost!", 1)

        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

def collision_detect(a, b):
    return not (
        a.y + a.height - 1 < b.y or
        a.y > b.y + b.height - 1 or
        a.x + a.width - 1 < b.x or
        a.x > b.x + b.width - 1
    )

# conexao com o servidor
server_ip = input("Digite o endereço do servidor: ")
server_ip = server_ip if server_ip else "10.1.40.203"

server_port = input("Digite a porta do servidor: ")
server_port = int(server_port) if server_port else 12345

# Inicialização
player = Player(WIDTH // 2, HEIGHT // 2, 1)
client = Client(server_ip, server_port)
client_thread = threading.Thread(target=client.start, daemon=True)
client_thread.start()

players_online = []

level1_1 = None
level1_2 = None
level1_3 = None
level2_1 = None
level2_2 = None
level2_3 = None

def update():
    global game_state, level1_1, level1_2, level1_3, level2_1, level2_2, level2_3

    if game_state.esta_menu:
        if btnp(KEY_RIGHT) and game_state.option_menu < 4:
            game_state.option_menu += 1
            game_state.x_seta1 += 19
        if btnp(KEY_LEFT) and game_state.option_menu > 1:
            game_state.option_menu -= 1
            game_state.x_seta1 -= 19

        if game_state.option_menu == 1 and btnp(KEY_SPACE):
            load("levels.pyxres")
            game_state.esta_menu = False
            game_state.esta_levels = True
            player.level = None
        if game_state.option_menu == 3 and btnp(KEY_SPACE):
            load("Change_character.pyxres")
            game_state.esta_menu = False
            game_state.esta_choose_character = True
            player.level = None
        if game_state.option_menu == 4 and btnp(KEY_SPACE):
            client.send_disconnect()
            quit()

    if game_state.esta_choose_character:
        if btnp(KEY_RIGHT) and game_state.option_character < 4:
            game_state.option_character += 1
            game_state.x_seta2 += 19
        if btnp(KEY_LEFT) and game_state.option_character > 1:
            game_state.option_character -= 1
            game_state.x_seta2 -= 19

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_SPACE):
            load("Intro.pyxres")
            game_state.character_color = game_state.option_character
            player.color = game_state.character_color
            game_state.esta_choose_character = False
            game_state.esta_menu = True
            game_state.option_menu = 1
            game_state.pode_selecionar = False
            game_state.x_seta1 = 42
            player.level = None

        if game_state.pode_selecionar and btnp(KEY_B):
            load("Intro.pyxres")
            game_state.esta_choose_character = False
            game_state.esta_menu = True
            game_state.option_menu = 1
            game_state.pode_selecionar = False
            game_state.x_seta1 = 42
            player.level = None

    if game_state.esta_levels:
        if btnp(KEY_RIGHT) and game_state.option_level < 2:
            game_state.option_level += 1
            game_state.x_seta3 += 23
        if btnp(KEY_LEFT) and game_state.option_level > 0:
            game_state.option_level -= 1
            game_state.x_seta3 -= 23

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_SPACE) and game_state.option_level == 0:
            load("levels_hello_stop.pyxres")
            game_state.esta_levels = False
            game_state.esta_levels_hello = True
            game_state.pode_selecionar = False
            player.level = None

        if game_state.pode_selecionar and btnp(KEY_SPACE) and game_state.option_level == 1:
            load("levels_hello_stop.pyxres")
            game_state.esta_levels = False
            game_state.esta_levels_stopmove = True
            game_state.pode_selecionar = False
            game_state.x_seta3 = 42
            player.level = None
        
        if game_state.pode_selecionar and btnp(KEY_SPACE) and game_state.option_level == 2:
            load("levels_hello_stop.pyxres")
            game_state.esta_levels = False
            game_state.esta_levels_stopmove = True
            game_state.pode_selecionar = False
            game_state.x_seta3 = 42
            player.level = None

        if game_state.pode_selecionar and btnp(KEY_B):
            load("Intro.pyxres")
            game_state.esta_levels = False
            game_state.esta_menu = True
            game_state.option_menu = 1
            game_state.pode_selecionar = False
            game_state.x_seta1 = 42
            player.level = None

    # hello momoduo
    if game_state.esta_levels_hello:
        if btnp(KEY_RIGHT) and game_state.option_level_hello < 3:
            game_state.option_level_hello += 1
            game_state.x_seta3 += 27
        if btnp(KEY_LEFT) and game_state.option_level_hello > 1:
            game_state.option_level_hello -= 1
            game_state.x_seta3 -= 27

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_SPACE):
            load("player.pyxres")
            if game_state.option_level_hello == 1:
                level1_1 = Level1_1()
                game_state.esta_levels_hello = False
                game_state.esta_level1_1 = True
                game_state.pode_selecionar = False
                player.x, player.y = 0, 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x, player.respawn_y = 0, 50
                player.level = 'level1_1'
            elif game_state.option_level_hello == 2:
                level1_2 = Level1_2()
                game_state.esta_levels_hello = False
                game_state.esta_level1_2 = True
                game_state.pode_selecionar = False
                player.x, player.y = 0, 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x, player.respawn_y = 0, 50
                player.level = 'level1_2'
            elif game_state.option_level_hello == 3:
                level1_3 = Level1_3()
                game_state.esta_levels_hello = False
                game_state.esta_level1_3 = True
                game_state.pode_selecionar = False
                player.x, player.y = 0, 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x, player.respawn_y = 0, 50
                player.level = 'level1_3'

        if game_state.pode_selecionar and btnp(KEY_B):
            load("levels.pyxres")
            game_state.esta_levels_hello = False
            game_state.esta_levels = True
            game_state.option_level = 0
            game_state.pode_selecionar = False
            player.level = None

    if game_state.esta_level1_1:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level1_1.platforms, level1_1.itens, players_online)
        level1_1.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels_hello_stop.pyxres")
                game_state.esta_level1_1 = False
                game_state.esta_levels_hello = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None

    if game_state.esta_level1_2:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level1_2.platforms, level1_2.itens, players_online)
        level1_2.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels_hello_stop.pyxres")
                game_state.esta_level1_2 = False
                game_state.esta_levels_hello = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
    
    if game_state.esta_level1_3:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level1_3.platforms, level1_3.itens, players_online)
        level1_3.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels_hello_stop.pyxres")
                game_state.esta_level1_3 = False
                game_state.esta_levels_hello = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None

    # stop and move
    if game_state.esta_levels_stopmove:
        if btnp(KEY_RIGHT) and game_state.option_level_stopmove < 3:
            game_state.option_level_stopmove += 1
            game_state.x_seta3 += 27
        if btnp(KEY_LEFT) and game_state.option_level_stopmove > 1:
            game_state.option_level_stopmove -= 1
            game_state.x_seta3 -= 27

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_SPACE):
            load("player.pyxres")
            if game_state.option_level_stopmove == 1:
                level2_1 = Level2_1()
                game_state.esta_levels_stopmove= False
                game_state.esta_level2_1 = True
                game_state.pode_selecionar = False
                player.x, player.y = 0, 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x, player.respawn_y = 0, 50
                player.level = 'level2_1'
            elif game_state.option_level_stopmove == 2:
                level2_2 = Level2_2()
                game_state.esta_levels_stopmove = False
                game_state.esta_level2_2 = True
                game_state.pode_selecionar = False
                player.x, player.y = 0, 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x, player.respawn_y = 0, 50
                player.level = 'level2_2'
            elif game_state.option_level_stopmove == 3:
                level2_3 = Level2_3()
                game_state.esta_levels_stopmove = False
                game_state.esta_level2_3 = True
                game_state.pode_selecionar = False
                player.x, player.y = 0, 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x, player.respawn_y = 0, 50
                player.level = 'level2_3'

        if game_state.pode_selecionar and btnp(KEY_B):
            load("levels.pyxres")
            game_state.esta_levels_stopmove = False
            game_state.esta_levels = True
            game_state.option_level = 0
            game_state.pode_selecionar = False
            player.level = None

    if game_state.esta_level2_1:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level2_1.platforms, level2_1.itens, players_online)
        level2_1.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels_hello_stop.pyxres")
                game_state.esta_level2_1 = False
                game_state.esta_levels_stopmove = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None

    if game_state.esta_level2_2:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level2_2.platforms, level2_2.itens, players_online)
        level2_2.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels_hello_stop.pyxres")
                game_state.esta_level2_2 = False
                game_state.esta_levels_stopmove = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None

    if game_state.esta_level2_3:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level2_3.platforms, level2_3.itens, players_online)
        level2_3.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels_hello_stop.pyxres")
                game_state.esta_level2_3 = False
                game_state.esta_levels_stopmove = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None

    # Manda para o servidor a posição do player
    if game_state.esta_level1_1 or game_state.esta_level1_2 or game_state.esta_level1_3 or game_state.esta_level2_1 or game_state.esta_level2_2 or game_state.esta_level2_3:
        client.send_position(player.x, player.y, player.color, player.andando, player.level, player.facing_right)

def draw():
    cls(7)

    if game_state.esta_menu:
        blt(0, 0, 0, 0, 0, 160, 120)
        blt(game_state.x_seta1, game_state.y_seta1, 0, 0, 128, 12, 12)

    if game_state.esta_choose_character:
        blt(0, 0, 0, 0, 0, 160, 120)
        blt(game_state.x_seta2, game_state.y_seta2, 1, 0, 0, 12, 12)

    if game_state.esta_levels:
        blt(0, 0, game_state.option_level, 0, 0, 160, 120)

        if game_state.level_hello_1_achivied and game_state.level_hello_2_achivied and game_state.level_hello_3_achivied:
            blt(39, 62, game_state.option_level, 26, 134, 21, 17, 1)

        if game_state.level_stopmove_1_achivied and game_state.level_stopmove_2_achivied and game_state.level_stopmove_3_achivied:
            blt(66, 62, game_state.option_level, 2, 134, 21, 17, 1)

        # if game_state.level_other_1_achivied and game_state.level_other_2_achivied and game_state.level_other_3_achivied:
        #     blt(93, 62, game_state.option_level, 2, 134, 21, 17, 1)


    # hello momoduo
    if game_state.esta_levels_hello:
        blt(0, 0, 0, 0, 0, 160, 120)
        blt(game_state.x_seta3, game_state.y_seta3, 1, 0, 0, 12, 12)

        #desenha coroa no nivel que foi finalizado
        if game_state.level_hello_1_achivied:
            blt(40, 47, 0, 160, 0, 14, 12, 1)
        if game_state.level_hello_2_achivied:
            blt(67, 47, 0, 160, 0, 14, 12, 1)
        if game_state.level_hello_3_achivied:
            blt(93, 47, 0, 160, 0, 14, 12, 1)

    if game_state.esta_level1_1:
        level1_1.draw()
        player.draw(level1_1.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level1_1.camera)
    
    if game_state.esta_level1_2:
        level1_2.draw()
        player.draw(level1_2.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level1_2.camera)

    if game_state.esta_level1_3:
        level1_3.draw()
        player.draw(level1_3.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level1_3.camera)

    # stop and move
    if game_state.esta_levels_stopmove:
        blt(0, 0, 0, 0, 128, 160, 120)
        blt(game_state.x_seta3, game_state.y_seta3, 1, 0, 0, 12, 12)

        #desenha coroa no nivel que foi finalizado
        if game_state.level_stopmove_1_achivied:
            blt(40, 47, 0, 160, 0, 14, 12, 1)
        if game_state.level_stopmove_2_achivied:
            blt(67, 47, 0, 160, 0, 14, 12, 1)
        if game_state.level_stopmove_3_achivied:
            blt(93, 47, 0, 160, 0, 14, 12, 1)

    if game_state.esta_level2_1:
        level2_1.draw()
        player.draw(level2_1.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level2_1.camera)
    
    if game_state.esta_level2_2:
        level2_2.draw()
        player.draw(level2_2.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level2_2.camera)

    if game_state.esta_level2_3:
        level2_3.draw()
        player.draw(level2_3.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level2_3.camera)

load("Intro.pyxres")
run(update, draw)