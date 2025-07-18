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
                
            # Calculate new path cost
            tentative_g = current_node['g'] + euclidean_distance(current_pos, neighbor_pos)
            
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
    # -------------------------------------------------------- #

    #Etapa 1: implementar função de a estrela;
    #Etapa 2: implementar caminho inicial até a bola, caminho da bola até o gol
    #Etapa 3: implementar custo de deslocamento

    #Etapa1.1: implementar custo de ação

    #Etapa1.2: implementar custo posse de bola

    #Etapa1.3: implementar zona de perigo
    #Etapa1.4: implementar custo


    # O código abaixo é um EXEMPLO SIMPLES de um robô que apenas anda para frente.
    # Ele NÃO desvia de obstáculos e NÃO busca o objetivo.
    # Sua tarefa é substituir esta lógica simples pelo seu algoritmo A* completo.

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