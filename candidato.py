# NOME DO CANDIDATO: Pedro Henrique Fujinami Nishida
# CURSO DO CANDIDATO: Engenharia da Computação
# AREAS DE INTERESSE: Visão e Behaviour

# Você pode importar as bibliotecas que julgar necessárias.
#-----------------------------CÓDIGO DO CANDIDATO---------------------#
from typing import List, Tuple, Dict, Set # estruturas para criação de nós
import numpy as np # básico para calculos
import heapq # estrutura
from math import sqrt
#---------------------------------------------------------------------#

def encontrar_caminho(pos_inicial, pos_objetivo, obstaculos, largura_grid, altura_grid, tem_bola=False):
    """
    Esta é a função principal que você deve implementar para o desafio EDROM.
    Seu objetivo é criar um algoritmo de pathfinding (como o A*) que encontre o
    caminho ótimo para o robô, considerando os diferentes níveis de complexidade.

    Args:
        pos_inicial (tuple): A posição (x, y) inicial do robô.
        pos_objetivo (tuple): A posição (x, y) do objetivo (bola ou gol).
        obstaculos (list): Uma lista de tuplas (x, y) com as posições dos obstáculos.
        largura_grid (int): A largura do campo em células.
        altura_grid (int): A altura do campo em células.
        tem_bola (bool): Um booleano que indica o estado do robô.
                         True se o robô está com a bola, False caso contrário.
                         Este parâmetro é essencial para o Nível 2 do desafio.

    Returns:
        list: Uma lista de tuplas (x, y) representando o caminho do início ao fim.
              A lista deve começar com o próximo passo após a pos_inicial e terminar
              na pos_objetivo. Se nenhum caminho for encontrado, retorna uma lista vazia.
              Exemplo de retorno: [(1, 2), (1, 3), (2, 3)]

    ---------------------------------------------------------------------------------
    REQUISITOS DO DESAFIO (AVALIADOS EM NÍVEIS):
    ---------------------------------------------------------------------------------
    [NÍVEL BÁSICO: A* Comum com Diagonal]
    O Algoritmo deve chegar até a bola e depois ir até o gol (desviando dos adversários) 
    considerando custos diferentes pdra andar reto (vertical e horizontal) e para andar em diagonal

    [NÍVEL 1: Custo de Rotação]
    O custo de um passo não é apenas a distância. Movimentos que exigem que o robô
    mude de direção devem ser penalizados. Considere diferentes penalidades para:
    - Curvas suaves (ex: reto -> diagonal).
    - Curvas fechadas (ex: horizontal -> vertical).
    - Inversões de marcha (180 graus).

    [NÍVEL 2: Custo por Estado]
    O comportamento do robô deve mudar se ele estiver com a bola. Quando `tem_bola`
    for `True`, as penalidades (especialmente as de rotação do Nível 1) devem ser
    AINDA MAIORES. O robô precisa ser mais "cuidadoso" ao se mover com a bola.

    [NÍVEL 3: Zonas de Perigo]
    As células próximas aos `obstaculos` são consideradas perigosas. Elas não são
    proibidas, mas devem ter um custo adicional para desencorajar o robô de passar
    por elas, a menos que seja estritamente necessário ou muito vantajoso.

    DICA: Um bom algoritmo A* é flexível o suficiente para que os custos de movimento
    (g(n)) possam ser calculados dinamicamente, incorporando todas essas regras.
    """

    # -------------------------------------------------------- #
    # Initialize start node
    start_node = create_node(
        position=pos_inicial,
        g=0,
        h=euclidean_distance(pos_inicial, pos_objetivo)
    )
    
    # Initialize open and closed sets
    open_list = [(start_node['f'], pos_inicial)]  # Priority queue
    open_dict = {pos_inicial: start_node}         # For quick node lookup
    closed_set = set()                      # Explored nodes
    
    while open_list:
        # Get node with lowest f value
        _, current_pos = heapq.heappop(open_list)
        current_node = open_dict[current_pos]
        
        # Check if we've reached the goal
        if current_pos == pos_objetivo:
            return reconstruct_path(current_node)
            
        closed_set.add(current_pos)
        
        # Explore neighbors
        for neighbor_pos in get_avaiable_neighbors([largura_grid, altura_grid], current_pos, obstaculos):
            # Skip if already explored
            if neighbor_pos in closed_set:
                continue
            
            # NOVO: Calcula custo considerando todos os fatores
            movement_cost = calculate_movement_cost(
                current_pos=current_pos,
                next_pos=neighbor_pos,
                previous_pos=current_node['parent']['position'] if current_node['parent'] else None,
                tem_bola=tem_bola,
                obstaculos=obstaculos
            )
            
            tentative_g = current_node['g'] + movement_cost
            
            # Create or update neighbor
            if neighbor_pos not in open_dict:
                neighbor = create_node(
                    position=neighbor_pos,
                    g=tentative_g,
                    h=euclidean_distance(neighbor_pos, pos_objetivo),
                    parent=current_node
                )
                heapq.heappush(open_list, (neighbor['f'], neighbor_pos))
                open_dict[neighbor_pos] = neighbor
            elif tentative_g < open_dict[neighbor_pos]['g']:
                # Found a better path to the neighbor
                neighbor = open_dict[neighbor_pos]
                neighbor['g'] = tentative_g
                neighbor['f'] = tentative_g + neighbor['h']
                neighbor['parent'] = current_node
    
    return []  # No path found

def create_node(position: Tuple[int, int], g: float = float('inf'), 
                h: float = 0.0, parent: dict = None) -> dict:
    return {
        'position': position,
        'g': g,
        'h': h,
        'f': g + h,
        'parent': parent
    }

def euclidean_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    x1, y1 = pos1
    x2, y2 = pos2
    return sqrt((x2-x1)**2 + (y2 - y1)**2)

def get_avaiable_neighbors(grid_dims: List[int], position: Tuple[int,int], obstaculos: List[Tuple[int,int]] = None) -> List[Tuple[int,int]]:
    """
    Retorna as posições vizinhas válidas (dentro dos limites e sem obstáculos)
    
    Args:
        grid_dims: [largura, altura] do grid
        position: posição atual (x, y)
        obstaculos: lista de posições com obstáculos
    """
    x, y = position
    largura, altura = grid_dims
    
    if obstaculos is None:
        obstaculos = []
    
    possible_moves = [
        (x+1, y), (x-1, y),    # Direita, Esquerda
        (x, y+1), (x, y-1),    # Cima, Baixo
        (x+1, y+1), (x-1, y-1), # Diagonais: Nordeste e Sudoeste
        (x+1, y-1), (x-1, y+1)  #           Sudeste e Noroeste
    ]

    return [
        (nx, ny) for nx, ny in possible_moves
        if 0 <= nx < largura and 0 <= ny < altura
        and (nx, ny) not in obstaculos
    ]

def reconstruct_path(goal_node: Dict) -> List[Tuple[int,int]]:

    path = []
    current = goal_node
    while current is not None:
        path.append(current['position'])
        current = current['parent']

    return path[::-1]

def calculate_movement_cost(current_pos: Tuple[int, int], next_pos: Tuple[int, int], 
                          previous_pos: Tuple[int, int] = None, tem_bola: bool = False,
                          obstaculos: List[Tuple[int, int]] = None) -> float:
    """
    Calcula o custo de movimento considerando:
    - Custo básico de deslocamento (vertical/horizontal vs diagonal)
    - Custo de rotação baseado na mudança de direção
    - Multiplicadores para quando tem bola
    - Zona de perigo próxima a obstáculos
    """
    
    # NÍVEL BÁSICO: Custo base do movimento
    dx = abs(next_pos[0] - current_pos[0])
    dy = abs(next_pos[1] - current_pos[1])
    
    # Movimento diagonal custa mais que reto
    if dx == 1 and dy == 1:
        base_cost = 1.414  # sqrt(2) - custo diagonal
    else:
        base_cost = 1.0    # custo vertical/horizontal
    
    # NÍVEL 1: Custo de rotação
    rotation_cost = 0.0
    if previous_pos is not None:
        rotation_cost = calculate_rotation_penalty(previous_pos, current_pos, next_pos)
    
    # NÍVEL 2: Multiplicador por estado (com bola)
    state_multiplier = 1.0
    if tem_bola:
        state_multiplier = 1.5  # Robô mais cuidadoso com a bola
        rotation_cost *= 2.0    # Penalidade de rotação ainda maior
    
    # NÍVEL 3: Zona de perigo
    danger_cost = calculate_danger_zone_cost(next_pos, obstaculos) if obstaculos else 0.0
    
    total_cost = (base_cost + rotation_cost + danger_cost) * state_multiplier
    return total_cost

def calculate_rotation_penalty(prev_pos: Tuple[int, int], current_pos: Tuple[int, int], 
                             next_pos: Tuple[int, int]) -> float:
    """
    Calcula a penalidade de rotação baseada na mudança de direção
    """
    # Calcula os vetores de direção
    dir1 = (current_pos[0] - prev_pos[0], current_pos[1] - prev_pos[1])
    dir2 = (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])
    
    # Se é o primeiro movimento, não há penalidade
    if dir1 == (0, 0):
        return 0.0
    
    # Calcula o produto escalar para determinar o ângulo
    dot_product = dir1[0] * dir2[0] + dir1[1] * dir2[1]
    
    # Normaliza baseado no tipo de movimento
    magnitude1 = sqrt(dir1[0]**2 + dir1[1]**2)
    magnitude2 = sqrt(dir2[0]**2 + dir2[1]**2)
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    cos_angle = dot_product / (magnitude1 * magnitude2)
    
    # Penalidades baseadas no ângulo de rotação
    if cos_angle > 0.9:      # ~0° - movimento reto
        return 0.0
    elif cos_angle > 0.7:    # ~45° - curva suave
        return 0.3
    elif cos_angle > 0:      # 45°-90° - curva média
        return 0.6
    elif cos_angle > -0.7:   # 90°-135° - curva fechada
        return 1.0
    else:                    # 135°-180° - inversão de marcha
        return 2.0

def calculate_danger_zone_cost(position: Tuple[int, int], 
                              obstaculos: List[Tuple[int, int]]) -> float:
    """
    Calcula o custo adicional por estar em zona de perigo (próximo a obstáculos)
    """
    if not obstaculos:
        return 0.0
    
    min_distance = float('inf')
    
    for obs_pos in obstaculos:
        distance = euclidean_distance(position, obs_pos)
        min_distance = min(min_distance, distance)
    
    # Zona de perigo: quanto mais próximo do obstáculo, maior o custo
    if min_distance <= 1.0:        # Adjacente ao obstáculo
        return 3.0
    elif min_distance <= 1.414:    # Diagonal do obstáculo
        return 2.0
    elif min_distance <= 2.0:      # 2 células de distância
        return 1.0
    elif min_distance <= 2.5:      # ~2.5 células de distância
        return 0.5
    else:
        return 0.0

    # -------------------------------------------------------- #
    # O código abaixo é um EXEMPLO SIMPLES de um robô que apenas anda para frente.
    # Ele NÃO desvia de obstáculos e NÃO busca o objetivo.
    # Sua tarefa é substituir esta lógica simples pelo seu algoritmo A* completo.

"""
    print("Usando a função de exemplo: robô andando para frente.")
    
    caminho_exemplo = []
    x_atual, y_atual = pos_inicial

    # Gera um caminho de até 10 passos para a direita (considerado "frente" no campo)
    for i in range(1, 11):
        proximo_x = x_atual + i
        
        # Garante que o robô não tente andar para fora dos limites do campo
        if proximo_x < largura_grid:
            caminho_exemplo.append((proximo_x, y_atual))
        else:
            # Para o loop se o robô chegar na borda do campo
            break

    # Retorna o caminho
    return caminho_exemplo
"""