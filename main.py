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
        self.esta_level1_1 = False
        self.esta_level1_2 = False
        self.esta_level1_3 = False
        self.level_hello_achivied = False

        self.esta_levels_stopmove = False
        self.option_level_stopmove = 1
        self.esta_level2_1 = False
        self.esta_level2_2 = False
        self.esta_level2_3 = False
        self.level_stopmove_achivied = False

        self.esta_levels_pushjump = False
        self.option_level_pushjump = 1
        self.esta_level3_1 = False
        self.esta_level3_2 = False
        self.esta_level3_3 = False
        self.level_pushjump_achivied = False

        self.semaphore_color = 1

        self.option_menu = 1
        self.x_seta1 = 46
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
    def __init__(self, server_ip, server_port, player):
        self.server_ip = server_ip
        self.server_port = server_port
        self.player = player
        self.socket = None
        self.id = None 
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
                        self.player.id = self.id
                        
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
                        level = data['level']
                        item_id = data['item_id']
                        level_instance = {
                            "level1_1": level1_1,
                            "level1_2": level1_2,
                            "level1_3": level1_3,
                            "level2_1": level2_1,
                            "level2_2": level2_2,
                            "level2_3": level2_3,
                            "level3_1": level3_1,
                            "level3_2": level3_2,
                            "level3_3": level3_3
                        }.get(level)
                        if level_instance:
                            for item in level_instance.itens:
                                if item.id == item_id:
                                    if item_id.startswith("caixa"):
                                        item.x = data['new_x']
                                        item.y = data['new_y']
                                    elif item_id in ["key_picked", "key_dropped", "key"]:
                                        item.x = data['new_x']
                                        item.y = data['new_y']
                                        item.collected = data['collected']
                                        item.holder_id = data['holder_id']
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
                        
                        # Transição para o próximo nível com base no nível atual
                        if level == "level1_1":
                            game_state.esta_level1_1 = False
                            game_state.esta_levels_hello = True
                            game_state.option_level_hello = 2  # Vai para o nível 1_2
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                            player.level = "level1_2"
                        elif level == "level1_2":
                            game_state.esta_level1_2 = False
                            game_state.esta_levels_hello = True
                            game_state.option_level_hello = 3  # Vai para o nível 1_3
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                            player.level = "level1_3"
                        elif level == "level1_3":
                            game_state.esta_level1_3 = False
                            game_state.esta_levels_hello = True
                            game_state.level_hello_achivied = True
                            game_state.option_level_hello = 4  # Volta para o menu ou outro estado
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                            player.level = None
                        
                        elif level == "level2_1" and player.level == "level2_1":
                            game_state.esta_level2_1 = False
                            game_state.esta_levels_stopmove = True
                            game_state.option_level_stopmove = 2
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                            player.level = "level2_2"
                        elif level == "level2_2" and player.level == "level2_2":
                            game_state.esta_level2_2 = False
                            game_state.esta_levels_stopmove = True
                            game_state.option_level_stopmove = 3
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                            player.level = "level2_3"
                        elif level == "level2_3" and player.level == "level2_3":
                            game_state.esta_level2_3 = False
                            game_state.esta_levels_stopmove = True
                            game_state.level_stopmove_achivied = True
                            game_state.option_level_stopmove = 4
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                            player.level = None
                        elif level == "level3_1" and player.level == "level3_1":
                            game_state.esta_level3_1 = False
                            game_state.esta_levels_pushjump = True
                            game_state.option_level_pushjump = 2
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                            player.level = "level3_2"
                        elif level == "level3_2" and player.level == "level3_2":
                            game_state.esta_level3_2 = False
                            game_state.esta_levels_pushjump = True
                            game_state.option_level_pushjump = 3
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                            player.level = "level3_3"
                        elif level == "level3_3" and player.level == "level3_3":
                            game_state.esta_level3_3 = False
                            game_state.esta_levels_pushjump = True
                            game_state.level_pushjump_achivied = True
                            game_state.option_level_pushjump = 4
                            player.x, player.y = WIDTH // 2, HEIGHT // 2
                            player.level = None

                    elif message['type'] == 'semaphore_update':
                        data = message['data']
                        game_state.semaphore_color = data['semaphore_color']
                        game_state.animation_timer = 0  # Reseta o timer local para evitar conflitos

                    elif message['type'] == 'respawn':
                        data = message['data']
                        player_id = data['player_id']
                        x = data['x']
                        y = data['y']
                        if player_id == self.id:
                            self.player.x = x
                            self.player.y = y
                            self.player.upward_speed = 0
                            self.player.on_floor = False
                            print(f"Jogador local {player_id} respawned at ({x}, {y})")
                            # Reseta itens (como a chave) localmente
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
                            elif game_state.esta_level3_1 and level3_1:
                                for item in level3_1.itens:
                                    if item.id == "key":
                                        item.collected = False
                                        item.x = item.initial_x
                                        item.y = item.initial_y
                            elif game_state.esta_level3_2 and level3_2:
                                for item in level3_2.itens:
                                    if item.id == "key":
                                        item.collected = False
                                        item.x = item.initial_x
                                        item.y = item.initial_y
                            elif game_state.esta_level3_3 and level3_3:
                                for item in level3_3.itens:
                                    if item.id == "key":
                                        item.collected = False
                                        item.x = item.initial_x
                                        item.y = item.initial_y

                        else:
                            for online_player in players_online:
                                if online_player.id == player_id:
                                    online_player.x = x
                                    online_player.y = y
                                    online_player.upward_speed = 0
                                    online_player.on_floor = False
                                    print(f"Jogador online {player_id} respawned at ({x}, {y})")
                                    # Reseta itens (como a chave) localmente
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
                                    elif game_state.esta_level3_1 and level3_1:
                                        for item in level3_1.itens:
                                            if item.id == "key":
                                                item.collected = False
                                                item.x = item.initial_x
                                                item.y = item.initial_y
                                    elif game_state.esta_level3_2 and level3_2:
                                        for item in level3_2.itens:
                                            if item.id == "key":
                                                item.collected = False
                                                item.x = item.initial_x
                                                item.y = item.initial_y
                                    elif game_state.esta_level3_3 and level3_3:
                                        for item in level3_3.itens:
                                            if item.id == "key":
                                                item.collected = False
                                                item.x = item.initial_x
                                                item.y = item.initial_y                                 
                                    break
                    
                    elif message['type'] == 'elevator_update':
                        data = message['data']
                        if (data['level'] == 'level2_3' and 
                            self.player.level == 'level2_3' and 
                            level2_3 is not None):
                            for platform in level2_3.platforms:
                                if platform.is_elevator and platform.x == data['x']:  # Verifica a posição x
                                    platform.y = data['y']
                                    if (self.player.x + self.player.width > platform.x and
                                        self.player.x < platform.x + platform.width and
                                        abs(self.player.y + self.player.height - platform.y) < 6):
                                        self.player.y = platform.y - self.player.height
                                        self.player.on_floor = True
                                        break
                        if (data['level'] == 'level3_1' and 
                            self.player.level == 'level3_1' and 
                            level3_1 is not None):
                            for platform in level3_1.platforms:
                                if platform.is_elevator and platform.x == data['x']:  # Verifica a posição x
                                    platform.y = data['y']
                                    if (self.player.x + self.player.width > platform.x and
                                        self.player.x < platform.x + platform.width and
                                        abs(self.player.y + self.player.height - platform.y) < 6):
                                        self.player.y = platform.y - self.player.height
                                        self.player.on_floor = True
                                        break
                        if (data['level'] == 'level3_2' and 
                            self.player.level == 'level3_2' and 
                            level3_2 is not None):
                            for platform in level3_2.platforms:
                                if platform.is_elevator and platform.x == data['x']:  # Verifica a posição x
                                    platform.y = data['y']
                                    if (self.player.x + self.player.width > platform.x and
                                        self.player.x < platform.x + platform.width and
                                        abs(self.player.y + self.player.height - platform.y) < 6):
                                        self.player.y = platform.y - self.player.height
                                        self.player.on_floor = True
                                        break

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
    
    def send_level_update(self, level, item_id, new_x, new_y, holder_id=None, collected = False):
        if self.socket and self.running:
            self.socket.sendto(json.dumps({
                'type': 'level_update',
                'id': self.id,
                'data': {
                    'level': level,
                    'item_id': item_id,
                    'new_x': new_x,
                    'new_y': new_y,
                    'holder_id': holder_id,
                    'collected': collected
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
    
    def send_event_respawn(self, player_id, x, y):
        if self.socket and self.running and player_id is not None:
            self.socket.sendto(json.dumps({
                'type': 'respawn',
                'id': self.id,
                'data': {
                    'player_id': player_id,  # ID of the respawning player
                    'x': x,
                    'y': y
                }
            }).encode(), (self.server_ip, self.server_port))

class Player:
    def __init__(self, x: int, y: int, color: int):
        self.id = None
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
                    self.y = platform.y - self.height
                    if platform.is_elevator and abs(platform.y - platform.max_y) < 0.01:
                        self.y = platform.y - self.height
                    break
            # Verifica colisão com caixas (caixa1)
            if not did_collide_with_floor:
                for item in itens:
                    if item.id and item.id.startswith("caixa") and collision_detect(self, item):  # Check if item.id is not None
                        self.on_floor = True
                        did_collide_with_floor = True
                        self.y = item.y - self.height
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
            client.send_event_respawn(self.id, self.x, self.y)

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
                for item in itens:
                    if item.id and item.id.startswith("caixa") and collision_detect(self, item):  # Check if item.id is not None
                        temp_item = Item(item.x - 1, item.y, item.width, item.height, item.xPyxel, item.yPyxel, item.id)
                        can_move = True
                        for platform in platforms:
                            if collision_detect(temp_item, platform):
                                can_move = False
                                break
                        for other_item in itens:
                            if other_item != item and other_item.id and other_item.id.startswith("caixa"):  # Check if other_item.id is not None
                                if collision_detect(temp_item, other_item) and (temp_item.x != other_item.x or temp_item.y != other_item.y):
                                    can_move = False
                                    break
                        for online_player in players_online:
                            if collision_detect(temp_item, online_player):
                                can_move = False
                                break
                        if can_move:
                            item.x -= 1
                            client.send_level_update(self.level, item.id, item.x, item.y, None, False)
                        else:
                            self.x = previous_x
                        break
                for platform in platforms:
                    if collision_detect(self, platform):
                        self.x = previous_x
                        break
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
                for item in itens:
                    if item.id and item.id.startswith("caixa") and collision_detect(self, item):  # Check if item.id is not None
                        temp_item = Item(item.x + 1, item.y, item.width, item.height, item.xPyxel, item.yPyxel, item.id)
                        can_move = True
                        for platform in platforms:
                            if collision_detect(temp_item, platform):
                                can_move = False
                                break
                        for other_item in itens:
                            if other_item != item and other_item.id and other_item.id.startswith("caixa"):  # Check if other_item.id is not None
                                if collision_detect(temp_item, other_item) and (temp_item.x != other_item.x or temp_item.y != other_item.y):
                                    can_move = False
                                    break
                        for online_player in players_online:
                            if collision_detect(temp_item, online_player):
                                can_move = False
                                break
                        if can_move:
                            item.x += 1
                            client.send_level_update(self.level, item.id, item.x, item.y, None, False)
                        else:
                            self.x = previous_x
                        break
                for platform in platforms:
                    if collision_detect(self, platform):
                        self.x = previous_x
                        break
                for player in players_online:
                    if collision_detect(self, player):
                        self.x = previous_x
                        break

        if self.upward_speed > 0:
            for _ in range(self.upward_speed):
                previous_y = self.y
                self.y -= 1
                for platform in platforms:
                    if collision_detect(self, platform):
                        self.y = previous_y
                        break
                for item in itens:
                    if item.id and item.id.startswith("caixa") and collision_detect(self, item):  # Check if item.id is not None
                        self.y = previous_y
                        self.upward_speed = 0
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
        elif game_state.esta_level3_1 and level3_1:
            for item in level3_1.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level3_2 and level3_2:
            for item in level3_2.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level3_3 and level3_3:
            for item in level3_3.itens:
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
        self.respawn_x = 0 + (id * 13)
        self.respawn_y = 50
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
        elif game_state.esta_level3_1 and level3_1:
            for item in level3_1.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level3_2 and level3_2:
            for item in level3_2.itens:
                if item.id == "key":
                    item.collected = False
                    item.x = item.initial_x
                    item.y = item.initial_y
        elif game_state.esta_level3_3 and level3_3:
            for item in level3_3.itens:
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
    def __init__(self, x: int, y: int, width: int, height: int, xPyxel: int, yPyxel: int, is_elevator: bool = False):
        self.x = x
        self.y = y
        self.initial_y = y  # Guarda a posição inicial
        self.width = width
        self.height = height
        self.xPyxel = xPyxel
        self.yPyxel = yPyxel
        self.is_elevator = is_elevator
        self.max_y = y - 56 if is_elevator else y  # Plataforma sobe até 56 pixels acima da posição inicial
        self.speed = 0.5  # Velocidade de subida do elevador

    def draw(self, camera):
        screen_x = self.x - camera.x
        screen_y = int(self.y - camera.y)  # Arredonda para evitar artefatos
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
        self.holder_id = None
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
        if self.id == "fire":
            self.is_visible = True  # Controla se o fogo está visível
            self.fire_timer = 0  # Temporizador para alternar visibilidade
            self.fire_interval = 40  # 2 segundos a 30 FPS (30 frames/seg * 2 seg = 60 frames)

    def update(self, player):
        previous_x = self.x
        previous_y = self.y

        # Atualiza a chave se coletada
        if self.id == "key" and self.collected and self.holder_id == player.id:
            self.x = player.x + PLAYER_SPRITE_WIDTH // 2 - self.width // 2
            self.y = player.y - self.height - 5
            client.send_level_update(player.level, self.id, self.x, self.y, self.holder_id, self.collected)

        #Aplica gravidade para caixas
        if self.id and self.id.startswith("caixa") and not self.collected:
            previous_y = self.y
            self.y += 1  # Aplica gravidade (1 pixel por frame)
            did_collide = False

            # Determina o nível atual
            current_level = None
            level_name = None
            if game_state.esta_level3_1:
                current_level = level3_1
                level_name = "level3_1"
            elif game_state.esta_level2_2:
                current_level = level2_2
                level_name = "level2_2"
            elif game_state.esta_level1_1:
                current_level = level1_1
                level_name = "level1_1"
            elif game_state.esta_level1_2:
                current_level = level1_2
                level_name = "level1_2"
            elif game_state.esta_level1_3:
                current_level = level1_3
                level_name = "level1_3"
            elif game_state.esta_level2_1:
                current_level = level2_1
                level_name = "level2_1"
            elif game_state.esta_level2_3:
                current_level = level2_3
                level_name = "level2_3"
            elif game_state.esta_level3_2:
                current_level = level3_2
                level_name = "level3_2"
            elif game_state.esta_level3_3:
                current_level = level3_3
                level_name = "level3_3"

            if current_level:
                # Verifica colisão com plataformas
                for platform in current_level.platforms:
                    if collision_detect(self, platform):
                        did_collide = True
                        self.y = platform.y - self.height
                        # Se for um elevador, acompanha o movimento
                        if platform.is_elevator and hasattr(platform, 'speed'):
                            if platform.y < platform.initial_y:  # Elevador subindo
                                self.y -= platform.speed
                            elif platform.y > platform.initial_y:  # Elevador descendo
                                self.y += platform.speed
                        break

                # Verifica colisão com outras caixas
                if not did_collide:
                    for other_item in current_level.itens:
                        if other_item != self and other_item.id and other_item.id.startswith("caixa") and not other_item.collected:
                            if collision_detect(self, other_item):
                                did_collide = True
                                self.y = other_item.y - self.height
                                break

                # Verifica colisão com jogadores (local e online)
                if not did_collide:
                    if collision_detect(self, player):
                        did_collide = True
                        self.y = player.y - self.height
                    for online_player in players_online:
                        if collision_detect(self, online_player):
                            did_collide = True
                            self.y = online_player.y - self.height
                            break

                if not did_collide:
                    # Continua caindo
                    self.y = previous_y + 1  # Aplica a gravidade
                else:
                    # Mantém a posição ajustada pela colisão
                    pass

                if self.y != previous_y:
                    # Sincroniza a nova posição com o servidor
                    client.send_level_update(level_name, self.id, self.x, self.y)
                    print(f"Caixa {self.id} atualizada para y={self.y} no nível {level_name}")

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
        
        # Animação do fogo
        if self.id == "fire":
            self.fire_timer += 1
            if self.fire_timer >= self.fire_interval:
                self.is_visible = not self.is_visible
                self.fire_timer = 0

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
        elif self.id == "key":
            blt(screen_x, screen_y, 0, self.xPyxel, self.yPyxel, self.width, self.height, 1)
        elif self.id == "door":
            blt(screen_x, screen_y, 0, self.xPyxel, self.yPyxel, self.width, self.height, 1)
        elif self.id and self.id.startswith("caixa"):  # Check if self.id is not None
            blt(screen_x, screen_y, 0, 72, 24, self.width, self.height, 1)
        elif self.id == "gosma":
            # Inverte o sprite horizontalmente se estiver movendo para a direita
            sprite_width = self.width if not self.moving_right else -self.width
            blt(screen_x, screen_y, 0, self.xPyxel, self.yPyxel, sprite_width, self.height, 1)
        else:
            # Handle items without an ID (e.g., flowers) or other cases
            blt(screen_x, screen_y, 0, self.xPyxel, self.yPyxel, self.width, self.height, 7)  # Use colorkey 7 for flowers

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

            #chave e porta e fogo
            Item(117, 29, 12, 5, 90, 34, "key"),
            Item(230, 50, 16, 14, 72, 40, "door")
            
        ]
        self.camera = Camera()

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
                item.holder_id = player.id
                client.send_level_update(player.level, "key_picked", item.x, item.y, item.holder_id, item.collected)
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        game_state.esta_level1_1 = False
                        game_state.esta_levels_hello = True
                        game_state.option_level_hello = 2
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 117, 29
                        other_item.holder_id = None
                        client.send_level_update(player.level, "key_dropped", other_item.x, other_item.y, None, False)
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
            Item(150, 53, 12, 5, 90, 34, "key"),
            Item(250, 50, 16, 14, 72, 40, "door")
        ]
        self.interactive_itens = [
            InteractiveItem(67, 61, 4, 2, 92, 45, "button1"),
            Item(66, 63, 6, 1, 91, 47),
            InteractiveItem(217, 61, 4, 2, 92, 45, "button1"),
            Item(216, 63, 6, 1, 91, 47)
        ]
        self.camera = Camera()
        self.bridge_growth_speed = 5
        self.bridge_max_width = 110
        self.bridge_min_width = 0

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
                item.holder_id = player.id
                client.send_level_update(player.level, "key_picked", item.x, item.y, item.holder_id, item.collected)
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        game_state.esta_level1_2 = False
                        game_state.esta_levels_hello = True
                        game_state.option_level_hello = 3
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 150, 53
                        other_item.holder_id = None
                        client.send_level_update(player.level, "key_dropped", other_item.x, other_item.y, None, False)
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
            Item(166, 0, 12, 5, 90, 34, "key"),  # Chave
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
                item.holder_id = player.id
                client.send_level_update(player.level, "key_picked", item.x, item.y, item.holder_id, item.collected)
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        game_state.esta_level1_3 = False
                        game_state.level_hello_achivied = True
                        game_state.esta_levels_hello = True
                        game_state.option_level_hello = 4
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 166, 0
                        other_item.holder_id = None
                        client.send_level_update(player.level, "key_dropped", other_item.x, other_item.y, None, False)
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
            Item(117, 29, 12, 5, 90, 34, "key"), Item(450, 50, 16, 14, 72, 40, "door"),

        ]
        self.camera = Camera()

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
                item.holder_id = player.id
                client.send_level_update(player.level, "key_picked", item.x, item.y, item.holder_id, item.collected)
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        game_state.esta_level2_1 = False
                        game_state.esta_levels_stopmove = True
                        game_state.option_level_stopmove = 2
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 117, 29
                        other_item.holder_id = None
                        client.send_level_update(player.level, "key_dropped", other_item.x, other_item.y, None, False)
                        client.send_event_door("level2_1")
                        break

        # Verifica se qualquer jogador está andando no vermelho
        trigger_respawn = False
        
        # Checa jogador local
        if game_state.semaphore_color == 1 and (player.andando or player.upward_speed != 0):
            trigger_respawn = True
        # Checa jogadores online
        for online_player in players_online:
            if game_state.semaphore_color == 1 and (online_player.andando or online_player.upward_speed != 0):
                trigger_respawn = True

        # Aplica respawn a todos os jogadores se necessário
        if trigger_respawn:
            # Respawn do jogador local
            player.respawn()
            client.send_event_respawn(player.id, player.x, player.y)  # Sincroniza respawn do jogador local
            
            # Respawn de todos os jogadores online
            for online_player in players_online:
                online_player.respawn()
                client.send_event_respawn(online_player.id, online_player.x, online_player.y)  # Sincroniza respawn

    def draw(self):

        # Define a posição fixa do texto no mundo do jogo
        text_world_x = -60  # Posição x no mundo
        text_world_y = 50  # Posição y no mundo
        # Ajusta a posição do texto com base na câmera
        screen_x = text_world_x - self.camera.x
        screen_y = text_world_y - self.camera.y

        # Desenha o texto na posição ajustada
        text(screen_x, screen_y, "Attention to the", 1)
        text(screen_x+8, screen_y+10, "semaphore!", 1)

        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

        # Desenha o semáforo
        blt(66, 5, 0, 112, 49, 31, 12)
        if game_state.semaphore_color == 1:
            blt(66, 5, 0, 112, 65, 11, 12)     #red
        elif game_state.semaphore_color == 2:
            blt(76, 5, 0, 128, 65, 11, 12)     #yellow
        elif game_state.semaphore_color == 3:
            blt(86, 5, 0, 144, 65, 11, 12)     #green
              
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
            Platform(652, 64, 16, 14, 32, 16),

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

            #base para pegar a caixa
            Platform(620, 15, 16, 14, 0, 96), Platform(600, 5, 16, 14, 0, 96), 
            Platform(548, -5, 16, 14, 32, 0), Platform(564, -5, 16, 14, 32, 16), Platform(580, -5, 16, 14, 32, 32),

            #base final
            Platform(668, 30, 16, 16, 24, 96), Platform(684, 30, 16, 16, 48, 96), Platform(700, 30, 16, 16, 48, 96), Platform(716, 30, 16, 16, 72, 96),
            Platform(668, 46, 16, 16, 96, 96), Platform(684, 46, 16, 16, 72, 72), Platform(700, 46, 16, 16, 72, 72), Platform(716, 46, 16, 16, 96, 72),
            Platform(668, 62, 16, 16, 24, 72), Platform(684, 62, 16, 16, 24, 72), Platform(700, 62, 16, 16, 24, 72), Platform(716, 62, 16, 16, 48, 72)
            
        ]

        self.itens = [

            #flor vermelha
            Item(160, 46, 5, 4, 90, 52), Item(250, -2, 5, 4, 90, 52), 
            
            #flor amarela
            Item(228, -2, 5, 4, 98, 52), 

            #gosma que mata
            Item(130, 58, 8, 6, 40, 66, "gosma"),

            #chave e a porta
            Item(440, -25, 12, 5, 90, 34, "key"),
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
             Item(550, -20, 12, 15, 72, 24, "caixa1")

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
                item.holder_id = player.id
                client.send_level_update(player.level, "key_picked", item.x, item.y, item.holder_id, item.collected)
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        game_state.esta_level2_2 = False
                        game_state.esta_levels_stopmove = True
                        game_state.option_level_stopmove = 3
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 440, -25
                        other_item.holder_id = None
                        client.send_level_update(player.level, "key_dropped", other_item.x, other_item.y, None, False)
                        client.send_event_door("level2_2")
                        break

            if item.id == "gosma" and item.check_collision(player):
                player.respawn()
            if item.id == "chock" and item.check_collision(player):
                player.respawn()
            if item.id == "trampoline" and item.check_collision(player):
                player.upward_speed = 15  # aumenta o valor pra um pulo mais forte

        # Verifica se qualquer jogador está andando no vermelho
        trigger_respawn = False
        
        # Checa jogador local
        if game_state.semaphore_color == 1 and (player.andando or player.upward_speed != 0):
            trigger_respawn = True
        # Checa jogadores online
        for online_player in players_online:
            if game_state.semaphore_color == 1 and (online_player.andando or online_player.upward_speed != 0):
                trigger_respawn = True

        # Aplica respawn a todos os jogadores se necessário
        if trigger_respawn:
            # Respawn do jogador local
            player.respawn()
            client.send_event_respawn(player.id, player.x, player.y)  # Sincroniza respawn do jogador local
         
            # Respawn de todos os jogadores online
            for online_player in players_online:
                online_player.respawn()
                client.send_event_respawn(online_player.id, online_player.x, online_player.y)  # Sincroniza respawn

    def draw(self):
        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

        # Desenha o semáforo
        blt(66, 5, 0, 112, 49, 31, 12)
        if game_state.semaphore_color == 1:
            blt(66, 5, 0, 112, 65, 11, 12)     #red
        elif game_state.semaphore_color == 2:
            blt(76, 5, 0, 128, 65, 11, 12)     #yellow
        elif game_state.semaphore_color == 3:
            blt(86, 5, 0, 144, 65, 11, 12)     #green

class Level2_3:
    def __init__(self):
        
        self.platforms = [

            #plataforma 1 - pré montanha
            Platform(0, 64, 16, 14, 32, 0), Platform(16, 64, 16, 14, 32, 16), Platform(32, 64, 16, 14, 32, 16), 
            Platform(48, 64, 16, 14, 32, 16), Platform(64, 64, 16, 14, 32, 16), Platform(80, 64, 16, 14, 32, 16),
            Platform(96, 64, 16, 14, 32, 16), Platform(112, 64, 16, 14, 32, 16), Platform(128, 64, 16, 14, 32, 16), 
            Platform(144, 64, 16, 14, 32, 16), Platform(160, 64, 16, 14, 32, 16), Platform(176, 64, 16, 14, 32, 16),
            Platform(192, 64, 16, 14, 32, 16), 
            
            #base da montanha
            Platform(208, 64, 16, 14, 32, 48), Platform(224, 64, 16, 14, 32, 48), Platform(240, 64, 16, 14, 32, 48), 
            Platform(256, 64, 16, 14, 32, 48), Platform(272, 64, 16, 14, 32, 48), Platform(288, 64, 16, 14, 32, 48), 
            Platform(304, 64, 16, 14, 32, 48), Platform(320, 64, 16, 14, 32, 48), 

            #primeira montanha
            Platform(208, 2, 16, 16, 24, 96), Platform(224, 2, 16, 16, 72, 96),                                                                                                                                               Platform(304, 2, 16, 16, 24, 96), Platform(320, 2, 16, 16, 48, 96),                                    
            Platform(208, 18, 16, 16, 96, 96), Platform(224, 18, 16, 16, 72, 72), Platform(240, 18, 16, 16, 48, 96), Platform(256, 18, 16, 16, 48, 96), Platform(272, 18, 16, 16, 48, 96), Platform(288, 18, 16, 16, 48, 96), Platform(304, 18, 16, 16, 72, 72), Platform(320, 18, 16, 16, 96, 72), 
            Platform(208, 34, 16, 16, 96, 96), 
            Platform(224, 34, 16, 16, 72, 72), Platform(240, 34, 16, 16, 72, 72), Platform(256, 34, 16, 16, 72, 72), Platform(272, 34, 16, 16, 72, 72), Platform(288, 34, 16, 16, 72, 72), Platform(304, 34, 16, 16, 72, 72), Platform(320, 34, 16, 16, 96, 72),
            Platform(208, 50, 16, 16, 96, 96), Platform(224, 50, 16, 16, 72, 72), Platform(240, 50, 16, 16, 72, 72), Platform(256, 50, 16, 16, 72, 72), Platform(272, 50, 16, 16, 72, 72), Platform(288, 50, 16, 16, 72, 72), Platform(304, 50, 16, 16, 72, 72), Platform(320, 50, 16, 16, 96, 72),

            #plataforma 2 - inferior pós montanha
            Platform(336, 64, 16, 14, 32, 16), Platform(352, 64, 16, 14, 32, 16), Platform(368, 64, 16, 14, 32, 16),
            Platform(384, 64, 16, 14, 32, 16), Platform(400, 64, 16, 14, 32, 16), Platform(416, 64, 16, 14, 32, 16),
            Platform(432, 64, 16, 14, 32, 16), Platform(448, 64, 16, 14, 32, 16), Platform(464, 64, 16, 14, 32, 16),
            Platform(480, 64, 16, 14, 32, 16), Platform(496, 64, 16, 14, 32, 16), Platform(512, 64, 16, 14, 32, 16),
            Platform(528, 50, 16, 16, 24, 96), Platform(528, 64, 16, 14, 50, 72), Platform(544, 50, 16, 14, 32, 32),

            #bloco de fogo
            Platform(336, 2, 16, 14, 88, 0),

            #plataforma 3 - superior pós montanha
            Platform(352, 2, 16, 14, 32, 16), Platform(368, 2, 16, 14, 32, 16), Platform(384, 2, 16, 14, 32, 16),
            Platform(400, 16, 16, 16, 0, 72),  Platform(416, 18, 16, 14, 32, 16), Platform(432, 18, 16, 14, 32, 32),
            Platform(400, 2, 16, 15, 72, 96),

            # plataforma da gosma 2
            Platform(464, 2, 16, 14, 32, 0), Platform(480, 2, 16, 14, 32, 16), Platform(496, 2, 16, 14, 32, 16), 
            Platform(512, 2, 16, 14, 32, 16), Platform(528, 2, 16, 14, 32, 32),
            Platform(544, -14, 16, 14, 0, 96),

            #plataforma azul
            Platform(158, 60, 48, 4, 120, 96, is_elevator=True),
            Platform(560, 50, 0, 4, 120, 80),

            ## plataforma pós plataforma azul
            Platform(651, 50, 16, 14, 32, 0), Platform(667, 50, 16, 14, 32, 16), Platform(683, 50, 16, 14, 32, 16), Platform(699, 50, 16, 14, 32, 16), Platform(715, 50, 16, 14, 32, 32)
    
        ]

        self.itens = [

            #flor vermelha
            Item(10, 60, 5, 4, 90, 52), Item(50, 60, 5, 4, 90, 52), Item(90, 60, 5, 4, 90, 52), 

            #flor amarela
            Item(30, 60, 5, 4, 98, 52), Item(70, 60, 5, 4, 98, 52), Item(110, 60, 5, 4, 98, 52), 

            #chave e porta e fogo
            Item(370, 30, 12, 5, 90, 34, "key"), Item(660, 36, 16, 14, 72, 40, "door"), Item(337, -12, 13, 14, 113, 2, "fire"),

            #gosma que mata
            Item(300, 12, 8, 6, 40, 66, "gosma"),
            Item(530, -2, 8, 6, 40, 66, "gosma")
        ]
        
        self.interactive_itens = [
            InteractiveItem(550, -17, 4, 2, 92, 45, "button7"),
            Item(549, -15, 6, 1, 91, 47),  
        ]

        self.camera = Camera()
        self.bridge_growth_speed = 5
        self.bridge_max_width = 110
        self.bridge_min_width = 0

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
                item.holder_id = player.id
                client.send_level_update(player.level, "key_picked", item.x, item.y, item.holder_id, item.collected)
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        game_state.esta_level2_3 = False
                        game_state.esta_levels_stopmove = True
                        game_state.level_stopmove_achivied = True
                        game_state.option_level_stopmove = 4
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 117, 29
                        other_item.holder_id = None
                        client.send_level_update(player.level, "key_dropped", other_item.x, other_item.y, None, False)
                        client.send_event_door("level2_3")
                        break
            if item.id == "gosma" and item.check_collision(player):
                player.respawn()
            if item.id == "fire" and item.is_visible and item.check_collision(player):
                player.respawn()

        # Verifica se qualquer jogador está andando no vermelho
        trigger_respawn = False
        
        # Checa jogador local
        if game_state.semaphore_color == 1 and (player.andando or player.upward_speed != 0):
            trigger_respawn = True
        # Checa jogadores online
        for online_player in players_online:
            if game_state.semaphore_color == 1 and (online_player.andando or online_player.upward_speed != 0):
                trigger_respawn = True

        # Aplica respawn a todos os jogadores se necessário
        if trigger_respawn:
            # Respawn do jogador local
            player.respawn()
            client.send_event_respawn(player.id, player.x, player.y)  # Sincroniza respawn do jogador local
            
            # Respawn de todos os jogadores online
            for online_player in players_online:
                online_player.respawn()
                client.send_event_respawn(online_player.id, online_player.x, online_player.y)  # Sincroniza respawn

        # Botão
        for item in self.interactive_itens:
            if isinstance(item, InteractiveItem):
                item.is_active = item.check_collision(player)
                    
                if not item.is_active:
                    for online_player in players_online:
                        if item.check_collision(online_player):
                            item.is_active = True
                            break

        # Atualiza plataforma azul
        bridge = self.platforms[79]
        if any(item.is_active for item in self.interactive_itens if isinstance(item, InteractiveItem) and item.id == "button7"):
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
            if item.id == "fire":
                if item.is_visible:
                  item.draw(self.camera)        
            else:    
                item.draw(self.camera)
        for item in self.interactive_itens:
            item.draw(self.camera)

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

        # Desenha o semáforo
        blt(66, 5, 0, 112, 49, 31, 12)
        if game_state.semaphore_color == 1:
            blt(66, 5, 0, 112, 65, 11, 12)     #red
        elif game_state.semaphore_color == 2:
            blt(76, 5, 0, 128, 65, 11, 12)     #yellow
        elif game_state.semaphore_color == 3:
            blt(86, 5, 0, 144, 65, 11, 12)     #green

class Level3_1:

    def __init__(self):
        self.platforms = [

            #plataforma 1 - pré montanha
            Platform(0, 64, 16, 14, 32, 0), Platform(16, 64, 16, 14, 32, 16), Platform(32, 64, 16, 14, 32, 16), 
            Platform(48, 64, 16, 14, 32, 16), Platform(64, 64, 16, 14, 32, 16), Platform(80, 64, 16, 14, 32, 16),
            Platform(96, 64, 16, 14, 32, 16), Platform(112, 64, 16, 14, 32, 16), Platform(128, 64, 16, 14, 32, 16), 
            Platform(144, 64, 16, 14, 32, 16), Platform(160, 64, 16, 14, 32, 16), Platform(176, 64, 16, 14, 32, 16),
            Platform(192, 64, 16, 14, 32, 16), 

            # montanha 1 
            Platform(208, 2, 16, 16, 24, 96), Platform(224, 2, 16, 16, 48, 96), Platform(240, 2, 16, 16, 48, 96), Platform(256, 2, 16, 16, 72, 96),
            Platform(208, 18, 16, 16, 96, 96), Platform(224, 18, 16, 16, 72, 72), Platform(240, 18, 16, 16, 72, 72), Platform(256, 18, 16, 16, 96, 72), 
            Platform(208, 34, 16, 16, 96, 96), Platform(224, 34, 16, 16, 72, 72), Platform(240, 34, 16, 16, 72, 72), Platform(256, 34, 16, 16, 96, 72),
            Platform(208, 50, 16, 16, 96, 96), Platform(224, 50, 16, 16, 72, 72), Platform(240, 50, 16, 16, 72, 72), Platform(256, 50, 16, 16, 96, 72), 
            Platform(208, 64, 16, 14, 24, 74), Platform(224, 64, 16, 14, 24, 74), Platform(240, 64, 16, 14, 24, 74), Platform(256, 64, 16, 14, 48, 74),
            
            #plataforma azul
            Platform(158, 60, 48, 4, 120, 96, is_elevator=True),

            #plataforma suspensa entre montanhas 1 e 2
            Platform(334, 2, 16, 14, 32, 0), Platform(350, 2, 16, 14, 32, 16), Platform(366, 2, 16, 14, 32, 32), 

            # montanha 2
            Platform(431, 2, 16, 16, 24, 96),  Platform(447, 2, 16, 16, 48, 96),  Platform(463, 2, 16, 16, 72, 96),
            Platform(431, 18, 16, 16, 96, 96), Platform(447, 18, 16, 16, 72, 72), Platform(463, 18, 16, 16, 96, 72), 
            Platform(431, 34, 16, 16, 96, 96), Platform(447, 34, 16, 16, 72, 72), Platform(463, 34, 16, 16, 96, 72),
            Platform(431, 50, 16, 16, 96, 96), Platform(447, 50, 16, 16, 72, 72), Platform(463, 50, 16, 16, 96, 72), 
            Platform(431, 64, 16, 14, 0, 74),  Platform(447, 64, 16, 14, 24, 74), Platform(463, 64, 16, 14, 24, 74),

            #plataforma entre montanhas 2 e 3
            Platform(479, 64, 16, 16, 32, 16), Platform(495, 64, 16, 16, 32, 16), Platform(511, 64, 16, 16, 32, 16), 
            Platform(527, 64, 16, 16, 32, 16), Platform(543, 64, 16, 16, 32, 16), Platform(559, 64, 16, 16, 32, 16),

            #plataforma para teste do nivel 3_2
            Platform(479, 2, 16, 16, 32, 16), Platform(495, 2, 16, 16, 32, 16), Platform(511, 2, 16, 16, 32, 16), 
            Platform(527, 2, 16, 16, 32, 16), Platform(543, 2, 16, 16, 32, 16), Platform(559, 2, 16, 16, 32, 16),

            # montanha 3
            Platform(575, 2, 16, 16, 24, 96),  Platform(591, 2, 16, 16, 48, 96),  Platform(607, 2, 16, 16, 72, 96),
            Platform(575, 18, 16, 16, 96, 96), Platform(591, 18, 16, 16, 72, 72), Platform(607, 18, 16, 16, 96, 72), 
            Platform(575, 34, 16, 16, 96, 96), Platform(591, 34, 16, 16, 72, 72), Platform(607, 34, 16, 16, 96, 72),
            Platform(575, 50, 16, 16, 96, 96), Platform(591, 50, 16, 16, 72, 72), Platform(607, 50, 16, 16, 96, 72), 
            Platform(575, 64, 16, 14, 24, 74),  Platform(591, 64, 16, 14, 24, 74), Platform(607, 64, 16, 14, 48, 74),
            
        ]

        self.itens = [

            #flor vermelha
            Item(100, 60, 5, 4, 90, 52), Item(250, -2, 5, 4, 90, 52), 
            
            #flor amarela
            Item(228, -2, 5, 4, 98, 52), 

            #chave e a porta
            Item(440, -25, 12, 5, 90, 34, "key"),
            Item(591, -12, 16, 14, 72, 40, "door"),

            #choque
            Item(272, 64, 9, 6, 0, 64, "chock"), Item(281, 64, 9, 6, 0, 64, "chock"), Item(290, 64, 9, 6, 0, 64, "chock"), 
            Item(299, 64, 9, 6, 0, 64, "chock"), Item(308, 64, 9, 6, 0, 64, "chock"), Item(317, 64, 9, 6, 0, 64, "chock"),
            Item(326, 64, 9, 6, 0, 64, "chock"), Item(335, 64, 9, 6, 0, 64, "chock"), Item(344, 64, 9, 6, 0, 64, "chock"),
            Item(353, 64, 9, 6, 0, 64, "chock"), Item(362, 64, 9, 6, 0, 64, "chock"), Item(371, 64, 9, 6, 0, 64, "chock"), 
            Item(380, 64, 9, 6, 0, 64, "chock"), Item(389, 64, 9, 6, 0, 64, "chock"), Item(398, 64, 9, 6, 0, 64, "chock"),
            Item(407, 64, 9, 6, 0, 64, "chock"), Item(416, 64, 9, 6, 0, 64, "chock"), Item(425, 64, 6, 6, 0, 64, "chock"),

            #Caixas
            Item(510, 49, 12, 15, 72, 24, "caixa1"), Item(520, 34, 12, 15, 72, 24, "caixa2"), Item(530, 19, 12, 15, 72, 24, "caixa3"),
            Item(540, 4, 12, 15, 72, 24, "caixa4"),

        ]

        self.camera = Camera()
        self.bridge_growth_speed = 5
        self.bridge_max_width = 110
        self.bridge_min_width = 0

    def update(self, player, game_state):
        self.camera.update(player)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
                item.holder_id = player.id
                client.send_level_update(player.level, "key_picked", item.x, item.y, item.holder_id, item.collected)
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        game_state.esta_level3_1 = False
                        game_state.esta_levels_pushjump = True
                        game_state.option_level_pushjump = 2
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 440, -25
                        other_item.holder_id = None
                        client.send_level_update(player.level, "key_dropped", other_item.x, other_item.y, None, False)
                        client.send_event_door("level3_1")
                        break
            if item.id == "chock" and item.check_collision(player):
                player.respawn()

    def draw(self):
        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

class Level3_2:
    def __init__(self):
        self.platforms = [

            #plataforma 1 - pré montanha
            Platform(0, 64, 16, 14, 32, 0), Platform(16, 64, 16, 14, 32, 16), Platform(32, 64, 16, 14, 32, 16), 
            Platform(48, 64, 16, 14, 32, 16), Platform(64, 64, 16, 14, 32, 16), Platform(80, 64, 16, 14, 32, 16),
            Platform(96, 64, 16, 14, 32, 16), Platform(112, 64, 16, 14, 32, 16), Platform(128, 64, 16, 14, 32, 16), 
            Platform(144, 64, 16, 14, 32, 16), Platform(160, 64, 16, 14, 32, 16), Platform(176, 64, 16, 14, 32, 16),
            Platform(192, 64, 16, 14, 32, 16), 

            # montanha 1 
            Platform(208, 18, 16, 16, 24, 96), Platform(224, 18, 16, 16, 48, 96), Platform(240, 18, 16, 16, 48, 96), Platform(256, 18, 16, 16, 72, 96), 
            Platform(208, 34, 16, 16, 96, 96), Platform(224, 34, 16, 16, 72, 72), Platform(240, 34, 16, 16, 72, 72), Platform(256, 34, 16, 16, 96, 72),
            Platform(208, 50, 16, 16, 96, 96), Platform(224, 50, 16, 16, 72, 72), Platform(240, 50, 16, 16, 72, 72), Platform(256, 50, 16, 16, 96, 72), 
            Platform(208, 64, 16, 14, 24, 74), Platform(224, 64, 16, 14, 24, 74), Platform(240, 64, 16, 14, 24, 74), Platform(256, 64, 16, 14, 48, 74),

            # montanha 2
            Platform(330, 2, 16, 16, 24, 96),  Platform(346, 2, 16, 16, 48, 96),  Platform(362, 2, 16, 16, 48, 96),  Platform(378, 2, 16, 16, 72, 96),
            Platform(330, 18, 16, 16, 96, 96), Platform(346, 18, 16, 16, 72, 72), Platform(362, 18, 16, 16, 72, 72), Platform(378, 18, 16, 16, 96, 72), 
            Platform(330, 34, 16, 16, 96, 96), Platform(346, 34, 16, 16, 72, 72), Platform(362, 34, 16, 16, 72, 72), Platform(378, 34, 16, 16, 96, 72),
            Platform(330, 50, 16, 16, 96, 96), Platform(346, 50, 16, 16, 72, 72), Platform(362, 50, 16, 16, 72, 72), Platform(378, 50, 16, 16, 96, 72), 
            Platform(330, 64, 16, 14, 0, 74), Platform(346, 64, 16, 14, 24, 74), Platform(362, 64, 16, 14, 24, 74), Platform(378, 64, 16, 14, 48, 74),

            # montanha 3
            Platform(458, 2, 16, 16, 24, 96),  Platform(474, 2, 16, 16, 48, 96),  Platform(490, 2, 16, 16, 48, 96),  Platform(506, 2, 16, 16, 72, 96),
            Platform(458, 18, 16, 16, 96, 96), Platform(474, 18, 16, 16, 72, 72), Platform(490, 18, 16, 16, 72, 72), Platform(506, 18, 16, 16, 96, 72), 
            Platform(458, 34, 16, 16, 96, 96), Platform(474, 34, 16, 16, 72, 72), Platform(490, 34, 16, 16, 72, 72), Platform(506, 34, 16, 16, 96, 72),
            Platform(458, 50, 16, 16, 96, 96), Platform(474, 50, 16, 16, 72, 72), Platform(490, 50, 16, 16, 72, 72), Platform(506, 50, 16, 16, 96, 72), 
            Platform(458, 64, 16, 14, 0, 74), Platform(474, 64, 16, 14, 24, 74), Platform(490, 64, 16, 14, 24, 74), Platform(506, 64, 16, 14, 48, 74),

            # montanha 4
            Platform(594, 2, 16, 16, 24, 96),  Platform(610, 2, 16, 16, 48, 96),  Platform(626, 2, 16, 16, 48, 96),  Platform(642, 2, 16, 16, 72, 96),
            Platform(594, 18, 16, 16, 96, 96), Platform(610, 18, 16, 16, 72, 72), Platform(626, 18, 16, 16, 72, 72), Platform(642, 18, 16, 16, 96, 72), 
            Platform(594, 34, 16, 16, 96, 96), Platform(610, 34, 16, 16, 72, 72), Platform(626, 34, 16, 16, 72, 72), Platform(642, 34, 16, 16, 96, 72),
            Platform(594, 50, 16, 16, 96, 96), Platform(610, 50, 16, 16, 72, 72), Platform(626, 50, 16, 16, 72, 72), Platform(642, 50, 16, 16, 96, 72), 
            Platform(594, 64, 16, 14, 0, 74), Platform(610, 64, 16, 14, 24, 74), Platform(626, 64, 16, 14, 24, 74), Platform(642, 64, 16, 14, 48, 74),

            #plataforma rosa, que só funciona se os dois players estiverem em cima dela
            Platform(277, 64, 48, 4, 120, 104, is_elevator=True),
            Platform(402, 64, 48, 4, 120, 104, is_elevator=True),
            Platform(534, 64, 48, 4, 120, 104, is_elevator=True),
        ]

        self.itens = [

            #flor vermelha
            Item(160, 60, 5, 4, 90, 52), Item(250, 14, 5, 4, 90, 52), 
            
            #flor amarela
            Item(228, 14, 5, 4, 98, 52), 

            #chave e a porta
            Item(440, -25, 12, 5, 90, 34, "key"),
            Item(642, -12, 16, 14, 72, 40, "door"),

            #Caixas
            Item(100, 49, 12, 15, 72, 24, "caixa1"),
            Item(215, 3, 12, 15, 72, 24, "caixa2")

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
                item.holder_id = player.id
                client.send_level_update(player.level, "key_picked", item.x, item.y, item.holder_id, item.collected)
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        game_state.esta_level3_2 = False
                        game_state.esta_levels_pushjump = True
                        game_state.option_level_pushjump = 3
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 440, -25
                        other_item.holder_id = None
                        client.send_level_update(player.level, "key_dropped", other_item.x, other_item.y, None, False)
                        client.send_event_door("level3_2")
                        break

    def draw(self):
        for platform in self.platforms:
            platform.draw(self.camera)
        for item in self.itens:
            item.draw(self.camera)

        # Desenha o texto na posição ajustada
        text(2, 108, "Click B", 1)
        text(2, 114, "to back", 1)

class Level3_3:
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
            Platform(388, 64, 16, 14, 32, 0),
            Platform(404, 64, 16, 14, 32, 16),
            Platform(420, 64, 16, 14, 32, 16),
            Platform(436, 64, 16, 14, 32, 16),
            Platform(452, 64, 16, 14, 32, 16),
            Platform(468, 64, 16, 14, 32, 16),
            Platform(484, 64, 16, 14, 32, 16),
            Platform(500, 64, 16, 14, 32, 16),
            Platform(516, 64, 16, 14, 32, 32),

            # Plataformas azuis verticais
            Platform(256, 64, 0, 4, 120, 80), # Plataforma 5 (horizontal, ponte)
            
        ]

        self.itens = [
            Item(10, 60, 5, 4, 90, 52),  # Flor vermelha
            Item(50, 60, 5, 4, 90, 52),
            Item(30, 60, 5, 4, 98, 52),  # Flor amarela
            Item(70, 60, 5, 4, 98, 52),
            Item(166, 20, 12, 5, 90, 34, "key"),  # Chave
            Item(500, 50, 16, 14, 72, 40, "door")  # Porta
        ]
        
        self.interactive_itens = [
            InteractiveItem(96, 61, 4, 2, 92, 45, "button8"),
            Item(95, 63, 6, 1, 91, 47),
            InteractiveItem(126, 61, 4, 2, 92, 45, "button9"),
            Item(125, 63, 6, 1, 91, 47),
            InteractiveItem(156, 61, 4, 2, 92, 45, "button10"),
            Item(155, 63, 6, 1, 91, 47),
            InteractiveItem(186, 61, 4, 2, 92, 45, "button11"),
            Item(185, 63, 6, 1, 91, 47),
            InteractiveItem(216, 61, 4, 2, 92, 45, "button12"),
            Item(215, 63, 6, 1, 91, 47),
            InteractiveItem(246, 61, 4, 2, 92, 45, "button13"),
            Item(245, 63, 6, 1, 91, 47),
            InteractiveItem(407, 61, 4, 2, 92, 45, "button14"),
            Item(406, 63, 6, 1, 91, 47),
            InteractiveItem(437, 61, 4, 2, 92, 45, "button15"),
            Item(436, 63, 6, 1, 91, 47)
        ]

        self.camera = Camera()
        self.platform_speed = 2  # Velocidade de movimento das plataformas
        self.vertical_min_y = -14  # Posição elevada das plataformas verticais
        self.vertical_max_y = 64   # Posição descida das plataformas verticais
        self.bridge_growth_speed = 2  # Velocidade de crescimento da ponte
        self.bridge_max_width = 110    # Largura máxima da ponte
        self.bridge_min_width = 0     # Largura mínima da ponte

    def update(self, player, game_state):
        self.camera.update(player)
        
        # Atualiza itens (chave, porta, etc.)
        for item in self.itens:
            item.update(player)
            if item.id == "key" and not item.collected and item.check_collision(player):
                item.collected = True
                item.holder_id = player.id
                client.send_level_update(player.level, "key_picked", item.x, item.y, item.holder_id, item.collected)
            if item.id == "door" and item.check_collision(player):
                for other_item in self.itens:
                    if other_item.id == "key" and other_item.collected:
                        game_state.esta_level3_3 = False
                        game_state.level_pushjump_achivied = True
                        game_state.esta_levels_pushjump = True
                        game_state.option_level_pushjump = 4
                        player.x, player.y = WIDTH // 2, HEIGHT // 2
                        other_item.collected = False
                        other_item.x, other_item.y = 166, 0
                        other_item.holder_id = None
                        client.send_level_update(player.level, "key_dropped", other_item.x, other_item.y, None, False)
                        client.send_event_door("level3_3")
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
            "button8": None,    # Morte
            "button9": None,    # Morte
            "button10": None,   # Morte
            "button11": self.platforms[24],   # Plataforma (ponte)
            "button12": None,   # Morte
            "button13": None,   # Morte
            "button14": self.platforms[24],   # Plataforma (ponte) 
            "button15": None,   # Morte
        }

        #Atualiza botões interativos e verifica colisões
        for item in self.interactive_itens:
            if isinstance(item, InteractiveItem):
                previous_active = item.is_active
                # Verifica colisão com o jogador local
                item.is_active = item.check_collision(player)
                if item.is_active != previous_active:
                    client.send_event_button("level3_3", item.id, item.is_active)
                # Verifica colisão com jogadores online
                if not item.is_active:
                    for online_player in players_online:
                        if item.check_collision(online_player):
                            item.is_active = True
                            if item.is_active != previous_active:
                                client.send_event_button("level3_3", item.id, item.is_active)
                            break

        # Atualiza plataforma (self.platforms[25])
        platform = self.platforms[25]
        previous_width = platform.width
        bridge_max_width = 100  # Ajuste conforme necessário
        bridge_min_width = 0   # Ajuste conforme necessário
        bridge_growth_speed = 2 # Ajuste conforme necessário
        button_active = any(
            item.is_active and item.id in ["button11", "button14"]
            for item in self.interactive_itens
            if isinstance(item, InteractiveItem)
        )
        if button_active:
            if platform.width < bridge_max_width:
                platform.width += bridge_growth_speed
                if platform.width > bridge_max_width:
                    platform.width = bridge_max_width
        else:
            if platform.width > bridge_min_width:
                platform.width -= bridge_growth_speed
                if platform.width < bridge_min_width:
                    platform.width = bridge_min_width
        if platform.width != previous_width:
            client.send_level_update("level3_3", f"bridge_{platform.x}_{platform.initial_y}", platform.x, platform.width)

        # Verifica botões de morte
        trigger_respawn = False    # Verifica se qualquer jogador está em cima de um botão de morte
        death_buttons = ["button8", "button9", "button10", "button12", "button13", "button15"]
        for item in self.interactive_itens:
            if isinstance(item, InteractiveItem) and item.id in death_buttons:
                if item.check_collision(player):
                    trigger_respawn = True
                    break
                for online_player in players_online:
                    if item.check_collision(online_player):
                        trigger_respawn = True

        # Aplica respawn a todos os jogadores se necessário
        if trigger_respawn:
            # Respawn do jogador local
            player.respawn()
            client.send_event_respawn(player.id, player.x, player.y)  # Sincroniza respawn do jogador local
            
            # Respawn de todos os jogadores online
            for online_player in players_online:
                online_player.respawn()
                client.send_event_respawn(online_player.id, online_player.x, online_player.y)  # Sincroniza respawn

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

        # Define a posição fixa do texto no mundo do jogo
        text_world_x = -60  # Posição x no mundo
        text_world_y = 50  # Posição y no mundo
        # Ajusta a posição do texto com base na câmera
        screen_x = text_world_x - self.camera.x
        screen_y = text_world_y - self.camera.y

        # Desenha o texto na posição ajustada
        text(screen_x, screen_y, "Search the", 1)
        text(screen_x+8, screen_y+10, "real button!", 1)

def collision_detect(a, b):
    return not (
        a.y + a.height - 1 < b.y or
        a.y > b.y + b.height - 1 or
        a.x + a.width - 1 < b.x or
        a.x > b.x + b.width - 1
    )

class PyxelSounds:
    def __init__(self):
        # Toca apenas a música de fundo no canal 0
        playm(0, loop=True)

# conexao com o servidor
server_ip = input("Digite o endereço do servidor: ")
server_ip = server_ip if server_ip else "10.1.40.203"

server_port = input("Digite a porta do servidor: ")
server_port = int(server_port) if server_port else 12345

# Inicialização
player = Player(WIDTH // 2, HEIGHT // 2, 1)
client = Client(server_ip, server_port, player)
client_thread = threading.Thread(target=client.start, daemon=True)
client_thread.start()

players_online = []

level1_1 = None
level1_2 = None
level1_3 = None
level2_1 = None
level2_2 = None
level2_3 = None
level3_1 = None
level3_2 = None
level3_3 = None

def update():
    global game_state, level1_1, level1_2, level1_3, level2_1, level2_2, level2_3, level3_1, level3_2, level3_3

    if game_state.esta_menu:
        if btnp(KEY_RIGHT) and game_state.option_menu < 3:
            game_state.option_menu += 1
            game_state.x_seta1 += 24
        if btnp(KEY_LEFT) and game_state.option_menu > 1:
            game_state.option_menu -= 1
            game_state.x_seta1 -= 24

        if game_state.option_menu == 1 and btnp(KEY_SPACE):
            load("levels.pyxres")
            game_state.esta_menu = False
            game_state.esta_levels = True
            player.level = None
        if game_state.option_menu == 2 and btnp(KEY_SPACE):
            load("Change_character.pyxres")
            game_state.esta_menu = False
            game_state.esta_choose_character = True
            player.level = None
        if game_state.option_menu == 3 and btnp(KEY_SPACE):
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
            game_state.x_seta1 = 46
            player.level = None

        if game_state.pode_selecionar and btnp(KEY_B):
            load("Intro.pyxres")
            game_state.esta_choose_character = False
            game_state.esta_menu = True
            game_state.option_menu = 1
            game_state.pode_selecionar = False
            game_state.x_seta1 = 46
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
            game_state.esta_levels = False
            game_state.esta_levels_hello = True
            player.level = None
            game_state.option_level_hello == 1

        if game_state.pode_selecionar and btnp(KEY_SPACE) and game_state.option_level == 1:
            game_state.esta_levels = False
            game_state.esta_levels_stopmove = True
            player.level = None
            game_state.option_level_stopmove == 1
        
        if game_state.pode_selecionar and btnp(KEY_SPACE) and game_state.option_level == 2:
            game_state.esta_levels = False
            game_state.esta_levels_pushjump = True
            player.level = None
            game_state.option_level_pushjump == 1

        if game_state.pode_selecionar and btnp(KEY_B):
            load("Intro.pyxres")
            game_state.esta_levels = False
            game_state.esta_menu = True
            game_state.option_menu = 1
            game_state.pode_selecionar = False
            game_state.x_seta1 = 46
            player.level = None

    # hello momoduo
    if game_state.esta_levels_hello:
            load("player.pyxres")
            if game_state.option_level_hello == 1:
                level1_1 = Level1_1()
                game_state.esta_levels_hello = False
                game_state.esta_level1_1 = True
                player.x = 0 + (player.id * 13 if player.id is not None else 0)
                player.y = 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x = 0 + (player.id * 13 if player.id is not None else 0)
                player.respawn_y = 50
                player.level = 'level1_1'
            elif game_state.option_level_hello == 2:
                level1_2 = Level1_2()
                game_state.esta_levels_hello = False
                game_state.esta_level1_2 = True
                player.x = 0 + (player.id * 13 if player.id is not None else 0)
                player.y = 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x = 0 + (player.id * 13 if player.id is not None else 0)
                player.respawn_y = 50
                player.level = 'level1_2'
            elif game_state.option_level_hello == 3:
                level1_3 = Level1_3()
                game_state.esta_levels_hello = False
                game_state.esta_level1_3 = True
                player.x = 0 + (player.id * 13 if player.id is not None else 0)
                player.y = 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x = 0 + (player.id * 13 if player.id is not None else 0)
                player.respawn_y = 50
                player.level = 'level1_3'

            elif game_state.option_level_hello == 4:
                load("levels.pyxres")
                game_state.esta_levels_hello = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_hello = 1

    if game_state.esta_level1_1:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level1_1.platforms, level1_1.itens, players_online)
        level1_1.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels.pyxres")
                game_state.esta_level1_1 = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_hello = 1

    if game_state.esta_level1_2:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level1_2.platforms, level1_2.itens, players_online)
        level1_2.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels.pyxres")
                game_state.esta_level1_2 = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_hello = 1
    
    if game_state.esta_level1_3:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level1_3.platforms, level1_3.itens, players_online)
        level1_3.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels.pyxres")
                game_state.esta_level1_3 = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_hello = 1

    # stop and move
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

    # stop and move
    if game_state.esta_levels_stopmove:
        
            load("player.pyxres")
            if game_state.option_level_stopmove == 1:
                level2_1 = Level2_1()
                game_state.esta_levels_stopmove= False
                game_state.esta_level2_1 = True
                player.x = 0 + (player.id * 13 if player.id is not None else 0)
                player.y = 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x = 0 + (player.id * 13 if player.id is not None else 0)
                player.respawn_y = 50
                player.level = 'level2_1'
            elif game_state.option_level_stopmove == 2:
                level2_2 = Level2_2()
                game_state.esta_levels_stopmove = False
                game_state.esta_level2_2 = True
                player.x = 0 + (player.id * 13 if player.id is not None else 0)
                player.y = 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x = 0 + (player.id * 13 if player.id is not None else 0)
                player.respawn_y = 50
                player.level = 'level2_2'
            elif game_state.option_level_stopmove == 3:
                level2_3 = Level2_3()
                game_state.esta_levels_stopmove = False
                game_state.esta_level2_3 = True
                player.x = 0 + (player.id * 13 if player.id is not None else 0)
                player.y = 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x = 0 + (player.id * 13 if player.id is not None else 0)
                player.respawn_y = 50
                player.level = 'level2_3'
            elif game_state.option_level_stopmove == 4:
                load("levels.pyxres")
                game_state.esta_levels_stopmove = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_stopmove = 1

    if game_state.esta_level2_1:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level2_1.platforms, level2_1.itens, players_online)
        level2_1.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels.pyxres")
                game_state.esta_level2_1 = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_stopmove = 1

    if game_state.esta_level2_2:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level2_2.platforms, level2_2.itens, players_online)
        level2_2.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels.pyxres")
                game_state.esta_level2_2 = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_stopmove = 1

    if game_state.esta_level2_3:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level2_3.platforms, level2_3.itens, players_online)
        level2_3.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels.pyxres")
                game_state.esta_level2_3 = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_stopmove = 1

    # push and jump
    if game_state.esta_levels_pushjump:
        
            load("player.pyxres")
            if game_state.option_level_pushjump == 1:
                level3_1 = Level3_1()
                game_state.esta_levels_pushjump= False
                game_state.esta_level3_1 = True
                player.x = 0 + (player.id * 13 if player.id is not None else 0)
                player.y = 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x = 0 + (player.id * 13 if player.id is not None else 0)
                player.respawn_y = 50
                player.level = 'level3_1'
            elif game_state.option_level_pushjump == 2:
                level3_2 = Level3_2()
                game_state.esta_levels_pushjump = False
                game_state.esta_level3_2 = True
                player.x = 0 + (player.id * 13 if player.id is not None else 0)
                player.y = 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x = 0 + (player.id * 13 if player.id is not None else 0)
                player.respawn_y = 50
                player.level = 'level3_2'
            elif game_state.option_level_pushjump == 3:
                level3_3 = Level3_3()
                game_state.esta_levels_pushjump = False
                game_state.esta_level3_3 = True
                player.x = 0 + (player.id * 13 if player.id is not None else 0)
                player.y = 64 - PLAYER_SPRITE_HEIGHT
                player.respawn_x = 0 + (player.id * 13 if player.id is not None else 0)
                player.respawn_y = 50
                player.level = 'level3_3'
            elif game_state.option_level_pushjump == 4:
                load("levels.pyxres")
                game_state.esta_levels_pushjump = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_pushjump = 1

    if game_state.esta_level3_1:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level3_1.platforms, level3_1.itens, players_online)
        level3_1.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels.pyxres")
                game_state.esta_level3_1 = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_pushjump = 1

    if game_state.esta_level3_2:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level3_2.platforms, level3_2.itens, players_online)
        level3_2.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels.pyxres")
                game_state.esta_level3_2 = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_pushjump = 1

    if game_state.esta_level3_3:
        if btnp(KEY_R):
            player.x, player.y = WIDTH // 2, 64 - PLAYER_SPRITE_HEIGHT
        player.update(level3_3.platforms, level3_3.itens, players_online)
        level3_3.update(player, game_state)  # Passa player e game_state

        if not btn(KEY_SPACE):
            game_state.pode_selecionar = True

        if game_state.pode_selecionar and btnp(KEY_B):
                load("levels.pyxres")
                game_state.esta_level3_3 = False
                game_state.esta_levels = True
                game_state.option_level = 0
                game_state.pode_selecionar = False
                player.level = None
                game_state.option_level_pushjump = 1

    # Manda para o servidor a posição do player
    if game_state.esta_level1_1 or game_state.esta_level1_2 or game_state.esta_level1_3 or game_state.esta_level2_1 or game_state.esta_level2_2 or game_state.esta_level2_3 or game_state.esta_level3_1 or game_state.esta_level3_2 or game_state.esta_level3_3:
        client.send_position(player.x, player.y, player.color, player.andando, player.level, player.facing_right)

def draw():
    cls(7)

    if game_state.esta_menu:
        blt(0, 0, 0, 0, 0, 160, 120)
        blt(game_state.x_seta1, game_state.y_seta1, 0, 0, 128, 12, 12)

        if game_state.character_color == 2:
            blt(66, 63, 0, 26, 135, 21, 12)
        if game_state.character_color == 3:
            blt(66, 63, 0, 50, 135, 21, 12)
        if game_state.character_color == 4:
            blt(66, 63, 0, 74, 135, 21, 12)
        
    if game_state.esta_choose_character:
        blt(0, 0, 0, 0, 0, 160, 120)
        blt(game_state.x_seta2, game_state.y_seta2, 1, 0, 0, 12, 12)

    if game_state.esta_levels:
        blt(0, 0, game_state.option_level, 0, 0, 160, 120)

        if game_state.level_hello_achivied:
            blt(39, 62, game_state.option_level, 26, 134, 21, 17, 1)

        if game_state.level_stopmove_achivied:
            blt(66, 62, game_state.option_level, 2, 134, 21, 17, 1)

        if game_state.level_pushjump_achivied:
            blt(93, 62, game_state.option_level, 50, 134, 21, 17, 1)

    if game_state.esta_level1_1:
        level1_1.draw()
        player.draw(level1_1.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level1_1.camera)
        
        # Desenha o nome do nivel
        text(2, 2, "1/3", 1)
  
    if game_state.esta_level1_2:
        level1_2.draw()
        player.draw(level1_2.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level1_2.camera)

        # Desenha o nome do nivel
        text(2, 2, "2/3", 1)

    if game_state.esta_level1_3:
        level1_3.draw()
        player.draw(level1_3.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level1_3.camera)

        # Desenha o nome do nivel
        text(2, 2, "3/3", 1)

    if game_state.esta_level2_1:
        level2_1.draw()
        player.draw(level2_1.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level2_1.camera)

        # Desenha o nome do nivel
        text(2, 2, "1/3", 1)
    
    if game_state.esta_level2_2:
        level2_2.draw()
        player.draw(level2_2.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level2_2.camera)

        # Desenha o nome do nivel
        text(2, 2, "2/3", 1)

    if game_state.esta_level2_3:
        level2_3.draw()
        player.draw(level2_3.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level2_3.camera)
        
        # Desenha o nome do nivel
        text(2, 2, "3/3", 1)

    if game_state.esta_level3_1:
        level3_1.draw()
        player.draw(level3_1.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level3_1.camera)

        # Desenha o nome do nivel
        text(2, 2, "1/3", 1)
    
    if game_state.esta_level3_2:
        level3_2.draw()
        player.draw(level3_2.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level3_2.camera)

        # Desenha o nome do nivel
        text(2, 2, "2/3", 1)

    if game_state.esta_level3_3:
        level3_3.draw()
        player.draw(level3_3.camera)

        for player_online in players_online:
            if player_online.level == player.level:
                player_online.draw(level3_3.camera)
        
        # Desenha o nome do nivel
        text(2, 2, "3/3", 1)

load("Intro.pyxres")
#sounds = PyxelSounds()
run(update, draw)