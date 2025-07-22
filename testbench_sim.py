# SIMULADOR DEBUG AVANÇADO - EDROM 2025
import os
import pygame
import sys

# Adicionar o diretório pai ao path para encontrar candidato.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import candidato

import random
import math
from typing import Dict, List, Tuple, Optional

# Configurações visuais
COR_FUNDO = (15, 60, 30)
COR_LINHA = (200, 200, 200)
COR_ROBO = (0, 0, 255)
COR_ROBO_COM_BOLA = (100, 140, 255)
COR_BOLA = (255, 165, 0)
COR_OBSTACULO = (255, 0, 0)
COR_CAMINHO = (0, 255, 255)
COR_GOL = (255, 255, 0)
COR_PAINEL = (30, 30, 30)
COR_BOTAO = (70, 70, 70)
COR_TEXTO_BOTAO = (255, 255, 255)

#Adicionado
COR_TEXTO_INFO = (220, 220, 220)
COR_CUSTO_BAIXO = (0, 255, 0)
COR_CUSTO_MEDIO = (255, 255, 0)
COR_CUSTO_ALTO = (255, 0, 0)
COR_ZONA_PERIGO = (255, 100, 100, 100)
COR_EXPLORADO = (100, 100, 255, 150)

# Dimensões
LARGURA_GRID = 20
ALTURA_GRID = 15
TAMANHO_CELULA = 40
ALTURA_PAINEL_SUPERIOR = 100
LARGURA_PAINEL_LATERAL = 400
ALTURA_PAINEL_INFERIOR = 100

LARGURA_TELA = LARGURA_GRID * TAMANHO_CELULA + LARGURA_PAINEL_LATERAL
ALTURA_TELA = ALTURA_GRID * TAMANHO_CELULA + ALTURA_PAINEL_SUPERIOR + ALTURA_PAINEL_INFERIOR

class DebugInfo:
    """Classe para armazenar informações de debug do A*"""
    def __init__(self):
        self.nodes_explored = {}  # posição -> node info
        self.open_list_history = []
        self.path_costs = {}
        self.movement_explanations = {}
        self.current_step = 0
        self.total_cost = 0

def carregar_imagem_com_fallback(nome_arquivo, tamanho_fallback=(40, 40)):
    """Carrega uma imagem com fallback para uma imagem padrão."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_imagem = os.path.join(script_dir, nome_arquivo)
        
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_imagem}")
        
        imagem = pygame.image.load(caminho_imagem)
        return imagem, None
        
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível carregar '{nome_arquivo}': {e}")
        print(f"📁 Caminho tentado: {caminho_imagem if 'caminho_imagem' in locals() else nome_arquivo}")
        print(f"📂 Diretório do script: {os.path.dirname(os.path.abspath(__file__))}")
        
        imagem_fallback = pygame.Surface(tamanho_fallback, pygame.SRCALPHA)
        centro = (tamanho_fallback[0] // 2, tamanho_fallback[1] // 2)
        raio = min(tamanho_fallback) // 2 - 2
        pygame.draw.circle(imagem_fallback, (0, 120, 200), centro, raio)
        pygame.draw.circle(imagem_fallback, (255, 255, 255), centro, raio, 2)
        
        return imagem_fallback, str(e)

def encontrar_caminho_com_debug(pos_inicial, pos_objetivo, obstaculos, largura_grid, altura_grid, tem_bola=False):
    """
    Versão modificada do A* que retorna informações de debug
    """
    debug_info = DebugInfo()
    
    # Usar o algoritmo do candidato mas capturar informações de debug
    caminho = candidato.encontrar_caminho(pos_inicial, pos_objetivo, obstaculos, largura_grid, altura_grid, tem_bola)
    
    # Calcular custos para cada célula do caminho
    if caminho:
        custo_total = 0
        for i in range(len(caminho)):
            current_pos = caminho[i]
            prev_pos = caminho[i-1] if i > 0 else pos_inicial
            next_pos = caminho[i+1] if i < len(caminho)-1 else None
            
            if hasattr(candidato, 'calculate_movement_cost'):
                custo = candidato.calculate_movement_cost(
                    prev_pos, current_pos, 
                    caminho[i-2] if i > 1 else None,
                    tem_bola, obstaculos
                )
            else:
                # Fallback para distância euclidiana simples
                custo = candidato.euclidean_distance(prev_pos, current_pos)
            
            custo_total += custo
            debug_info.path_costs[current_pos] = custo
            
            # Explicação do movimento
            explicacao = gerar_explicacao_movimento(prev_pos, current_pos, next_pos, tem_bola, obstaculos)
            debug_info.movement_explanations[current_pos] = explicacao
        
        debug_info.total_cost = custo_total
    
    return caminho, debug_info

def gerar_explicacao_movimento(prev_pos, current_pos, next_pos, tem_bola, obstaculos):
    """Gera explicação textual do custo de movimento"""
    explicacoes = []
    
    # Tipo de movimento
    if prev_pos:
        dx = abs(current_pos[0] - prev_pos[0])
        dy = abs(current_pos[1] - prev_pos[1])
        
        if dx == 1 and dy == 1:
            explicacoes.append("Movimento diagonal (+1.41)")
        else:
            explicacoes.append("Movimento reto (+1.0)")
    
    # Estado do robô
    if tem_bola:
        explicacoes.append("Com bola (×1.5)")
    
    # Zona de perigo
    if obstaculos:
        min_dist = min(candidato.euclidean_distance(current_pos, obs) for obs in obstaculos)
        if min_dist <= 1.0:
            explicacoes.append("Zona de perigo extrema (+3.0)")
        elif min_dist <= 1.414:
            explicacoes.append("Zona de perigo alta (+2.0)")
        elif min_dist <= 2.0:
            explicacoes.append("Zona de perigo média (+1.0)")
        elif min_dist <= 2.5:
            explicacoes.append("Zona de perigo baixa (+0.5)")
    
    # Rotação
    if prev_pos and next_pos:
        explicacoes.append("Custo de rotação calculado")
    
    return " | ".join(explicacoes) if explicacoes else "Movimento padrão"

def desenhar_grade(tela):
    """Desenha a grade do campo"""
    offset_x = 0
    offset_y = ALTURA_PAINEL_SUPERIOR
    
    for x in range(0, LARGURA_GRID * TAMANHO_CELULA + 1, TAMANHO_CELULA):
        pygame.draw.line(tela, COR_LINHA, 
                        (x + offset_x, offset_y), 
                        (x + offset_x, offset_y + ALTURA_GRID * TAMANHO_CELULA))
    
    for y in range(0, ALTURA_GRID * TAMANHO_CELULA + 1, TAMANHO_CELULA):
        pygame.draw.line(tela, COR_LINHA, 
                        (offset_x, y + offset_y), 
                        (LARGURA_GRID * TAMANHO_CELULA + offset_x, y + offset_y))

def desenhar_retangulo(tela, pos_grid, cor):
    """Desenha um retângulo na posição da grade"""
    x, y = pos_grid
    offset_x = 0
    offset_y = ALTURA_PAINEL_SUPERIOR
    
    rect = pygame.Rect(
        x * TAMANHO_CELULA + offset_x, 
        y * TAMANHO_CELULA + offset_y, 
        TAMANHO_CELULA, 
        TAMANHO_CELULA
    )
    pygame.draw.rect(tela, cor, rect)

def desenhar_circulo(tela, pos_grid, cor, raio_fator=0.4):
    """Desenha um círculo na posição da grade"""
    x, y = pos_grid
    offset_x = 0
    offset_y = ALTURA_PAINEL_SUPERIOR
    
    centro_x = int(x * TAMANHO_CELULA + TAMANHO_CELULA / 2 + offset_x)
    centro_y = int(y * TAMANHO_CELULA + TAMANHO_CELULA / 2 + offset_y)
    raio = int(TAMANHO_CELULA * raio_fator)
    pygame.draw.circle(tela, cor, (centro_x, centro_y), raio)

def desenhar_texto_celula(tela, pos_grid, texto, cor=COR_TEXTO_INFO, tamanho_fonte=16):
    """Desenha texto em uma célula da grade"""
    fonte = pygame.font.Font(None, tamanho_fonte)
    x, y = pos_grid
    offset_x = 0
    offset_y = ALTURA_PAINEL_SUPERIOR
    
    superficie_texto = fonte.render(str(texto), True, cor)
    pos_x = x * TAMANHO_CELULA + offset_x + 2
    pos_y = y * TAMANHO_CELULA + offset_y + 2
    tela.blit(superficie_texto, (pos_x, pos_y))

def desenhar_caminho_com_custos(tela, caminho, debug_info):
    """Desenha o caminho com informações de custo"""
    for i, passo in enumerate(caminho):
        # Cor baseada no custo
        if passo in debug_info.path_costs:
            custo = debug_info.path_costs[passo]
            if custo <= 1.5:
                cor = COR_CUSTO_BAIXO
            elif custo <= 3.0:
                cor = COR_CUSTO_MEDIO
            else:
                cor = COR_CUSTO_ALTO
        else:
            cor = COR_CAMINHO
        
        desenhar_circulo(tela, passo, cor, raio_fator=0.25)
        
        # Mostrar custo na célula
        if passo in debug_info.path_costs:
            custo_texto = f"{debug_info.path_costs[passo]:.1f}"
            desenhar_texto_celula(tela, passo, custo_texto, cor, 14)

def desenhar_zonas_perigo(tela, obstaculos):
    """Desenha zonas de perigo ao redor dos obstáculos"""
    offset_x = 0
    offset_y = ALTURA_PAINEL_SUPERIOR
    
    superficie_perigo = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
    
    for obs in obstaculos:
        obs_x, obs_y = obs
        
        # Zona de perigo ao redor do obstáculo
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                px, py = obs_x + dx, obs_y + dy
                
                if 0 <= px < LARGURA_GRID and 0 <= py < ALTURA_GRID:
                    distancia = math.sqrt(dx*dx + dy*dy)
                    
                    if distancia <= 2.5 and distancia > 0:
                        # Intensidade baseada na distância
                        if distancia <= 1.0:
                            alpha = 150
                        elif distancia <= 1.414:
                            alpha = 100
                        elif distancia <= 2.0:
                            alpha = 60
                        else:
                            alpha = 30
                        
                        superficie_perigo.fill((*COR_ZONA_PERIGO[:3], alpha))
                        pos_x = px * TAMANHO_CELULA + offset_x
                        pos_y = py * TAMANHO_CELULA + offset_y
                        tela.blit(superficie_perigo, (pos_x, pos_y))

def desenhar_painel_info(tela, estado_jogo, debug_info, fonte):
    """Desenha painel lateral com informações detalhadas"""
    painel_x = LARGURA_GRID * TAMANHO_CELULA
    painel_width = LARGURA_PAINEL_LATERAL
    
    # Fundo do painel
    painel_rect = pygame.Rect(painel_x, 0, painel_width, ALTURA_TELA)
    pygame.draw.rect(tela, COR_PAINEL, painel_rect)
    
    y_pos = 20
    linha_altura = 25
    
    # Título
    titulo = fonte.render("🔍 DEBUG A*", True, COR_TEXTO_INFO)
    tela.blit(titulo, (painel_x + 10, y_pos))
    y_pos += linha_altura * 2
    
    # Informações gerais
    info_texts = [
        f"Estado: {'Com bola' if estado_jogo['tem_bola'] else 'Sem bola'}",
        f"Robô: {estado_jogo['pos_robo']}",
        f"Objetivo: {estado_jogo['pos_bola'] if not estado_jogo['tem_bola'] else estado_jogo['pos_gol']}",
        f"Obstáculos: {len(estado_jogo['obstaculos'])}",
        "",
        f"🎯 Custo Total: {debug_info.total_cost:.2f}",
        f"📏 Passos: {len(estado_jogo['caminho_atual'])}",
        ""
    ]
    
    for texto in info_texts:
        if texto:  # Pular linhas vazias
            superficie = fonte.render(texto, True, COR_TEXTO_INFO)
            tela.blit(superficie, (painel_x + 10, y_pos))
        y_pos += linha_altura
    
    # Legenda de custos
    legenda_titulo = fonte.render("💰 Legenda de Custos:", True, COR_TEXTO_INFO)
    tela.blit(legenda_titulo, (painel_x + 10, y_pos))
    y_pos += linha_altura
    
    legenda_items = [
        ("🟢 Baixo (≤1.5)", COR_CUSTO_BAIXO),
        ("🟡 Médio (1.5-3.0)", COR_CUSTO_MEDIO),
        ("🔴 Alto (>3.0)", COR_CUSTO_ALTO),
    ]
    
    for texto, cor in legenda_items:
        superficie = fonte.render(texto, True, cor)
        tela.blit(superficie, (painel_x + 20, y_pos))
        y_pos += linha_altura
    
    y_pos += linha_altura
    
    # Explicações detalhadas do movimento atual
    if estado_jogo['pos_robo'] in debug_info.movement_explanations:
        explicacao_titulo = fonte.render("📋 Movimento Atual:", True, COR_TEXTO_INFO)
        tela.blit(explicacao_titulo, (painel_x + 10, y_pos))
        y_pos += linha_altura
        
        explicacao = debug_info.movement_explanations[estado_jogo['pos_robo']]
        
        # Quebrar texto longo em múltiplas linhas
        palavras = explicacao.split(' | ')
        for palavra in palavras:
            if len(palavra) > 35:  # Quebrar se muito longo
                palavra = palavra[:32] + "..."
            superficie = fonte.render(f"• {palavra}", True, COR_TEXTO_INFO)
            tela.blit(superficie, (painel_x + 20, y_pos))
            y_pos += linha_altura

def desenhar_painel_superior(tela, estado_jogo, fonte):
    """Desenha painel superior com controles"""
    painel_rect = pygame.Rect(0, 0, LARGURA_GRID * TAMANHO_CELULA, ALTURA_PAINEL_SUPERIOR)
    pygame.draw.rect(tela, COR_PAINEL, painel_rect)
    
    # Título principal
    titulo = fonte.render("🤖 EDROM A* DEBUG SIMULATOR", True, COR_TEXTO_INFO)
    tela.blit(titulo, (20, 20))
    
    # Status da simulação
    status = "▶️ RODANDO" if estado_jogo["simulacao_rodando"] else "⏸️ PAUSADO"
    status_surface = fonte.render(status, True, COR_TEXTO_INFO)
    tela.blit(status_surface, (20, 50))
    
    # Mensagem atual
    msg_surface = fonte.render(estado_jogo["mensagem"], True, COR_TEXTO_INFO)
    tela.blit(msg_surface, (200, 50))

def desenhar_botao(tela, fonte, rect, texto, cor_fundo, cor_texto):
    """Desenha um botão com texto"""
    pygame.draw.rect(tela, cor_fundo, rect, border_radius=8)
    pygame.draw.rect(tela, COR_TEXTO_INFO, rect, 2, border_radius=8)
    superficie_texto = fonte.render(texto, True, cor_texto)
    rect_texto = superficie_texto.get_rect(center=rect.center)
    tela.blit(superficie_texto, rect_texto)

def resetar_cenario():
    """Gera um novo cenário aleatório"""
    pos_robo = (2, ALTURA_GRID // 2)
    pos_gol = (LARGURA_GRID - 1, ALTURA_GRID // 2)

    # Posição da Bola
    while True:
        pos_bola_x = random.randint(LARGURA_GRID // 2, LARGURA_GRID - 1)
        pos_bola_y = random.randint(0, ALTURA_GRID - 1)
        pos_bola = (pos_bola_x, pos_bola_y)
        if pos_bola != pos_gol and pos_bola != pos_robo:
            break

    # Gerar obstáculos
    MAX_OBSTACULOS = 15
    obstaculos = []
    posicoes_ocupadas = {pos_robo, pos_gol, pos_bola}
    
    tentativas = 0
    while len(obstaculos) < MAX_OBSTACULOS and tentativas < 1000:
        obs_x = random.randint(3, LARGURA_GRID - 1)
        obs_y = random.randint(0, ALTURA_GRID - 1)
        pos_obs = (obs_x, obs_y)

        dist_do_robo = abs(pos_obs[0] - pos_robo[0]) + abs(pos_obs[1] - pos_robo[1])
        dist_do_gol = abs(pos_obs[0] - pos_gol[0]) + abs(pos_obs[1] - pos_gol[1])

        if pos_obs not in posicoes_ocupadas and dist_do_robo >= 3 and dist_do_gol > 1:
            obstaculos.append(pos_obs)
            posicoes_ocupadas.add(pos_obs)
        else:
            tentativas += 1

    return {
        "pos_robo": pos_robo, "pos_bola": pos_bola, "pos_gol": pos_gol, 
        "obstaculos": obstaculos, "tem_bola": False, "caminho_atual": [], 
        "debug_info": DebugInfo(), "simulacao_rodando": False,
        "mensagem": "🎮 Cenário gerado! Pressione Play para iniciar."
    }

def main():
    """Loop principal do simulador"""
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("EDROM A* Debug Simulator")
    clock = pygame.time.Clock()
    fonte = pygame.font.Font(None, 20)
    fonte_botao = pygame.font.Font(None, 24)
    
    # Carregar ícone
    icone_imagem, _ = carregar_imagem_com_fallback("icone_edrom.png", (32, 32))
    pygame.display.set_icon(icone_imagem)
    
    # Botões
    botao_play_pause = pygame.Rect(20, ALTURA_TELA - 80, 120, 40)
    botao_reset = pygame.Rect(160, ALTURA_TELA - 80, 120, 40)
    botao_step = pygame.Rect(300, ALTURA_TELA - 80, 120, 40)
    
    estado_jogo = resetar_cenario()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if botao_play_pause.collidepoint(event.pos):
                    estado_jogo["simulacao_rodando"] = not estado_jogo["simulacao_rodando"]
                    estado_jogo["mensagem"] = "▶️ Simulação rodando..." if estado_jogo["simulacao_rodando"] else "⏸️ Simulação pausada."
                
                if botao_reset.collidepoint(event.pos):
                    estado_jogo = resetar_cenario()
                
                if botao_step.collidepoint(event.pos) and not estado_jogo["simulacao_rodando"]:
                    # Modo passo a passo
                    if not estado_jogo["caminho_atual"]:
                        objetivo_atual = estado_jogo["pos_bola"] if not estado_jogo["tem_bola"] else estado_jogo["pos_gol"]
                        caminho, debug_info = encontrar_caminho_com_debug(
                            estado_jogo["pos_robo"], objetivo_atual, estado_jogo["obstaculos"],
                            LARGURA_GRID, ALTURA_GRID, estado_jogo["tem_bola"]
                        )
                        estado_jogo["caminho_atual"] = caminho
                        estado_jogo["debug_info"] = debug_info
                    
                    if estado_jogo["caminho_atual"]:
                        estado_jogo["pos_robo"] = estado_jogo["caminho_atual"].pop(0)
                        estado_jogo["mensagem"] = f"👣 Passo executado. Restam {len(estado_jogo['caminho_atual'])} passos."

        # Lógica de simulação automática
        if estado_jogo["simulacao_rodando"]:
            if not estado_jogo["caminho_atual"]:
                objetivo_atual = estado_jogo["pos_bola"] if not estado_jogo["tem_bola"] else estado_jogo["pos_gol"]
                caminho, debug_info = encontrar_caminho_com_debug(
                    estado_jogo["pos_robo"], objetivo_atual, estado_jogo["obstaculos"],
                    LARGURA_GRID, ALTURA_GRID, estado_jogo["tem_bola"]
                )
                estado_jogo["caminho_atual"] = caminho
                estado_jogo["debug_info"] = debug_info
            
            if estado_jogo["caminho_atual"]:
                estado_jogo["pos_robo"] = estado_jogo["caminho_atual"].pop(0)
            
            # Verificar se pegou a bola
            if not estado_jogo["tem_bola"] and estado_jogo["pos_robo"] == estado_jogo["pos_bola"]:
                estado_jogo["tem_bola"] = True
                estado_jogo["caminho_atual"] = []
                estado_jogo["mensagem"] = "⚽ Bola capturada! Calculando rota para o gol..."
            
            # Verificar se fez gol
            if estado_jogo["tem_bola"] and estado_jogo["pos_robo"] == estado_jogo["pos_gol"]:
                estado_jogo["mensagem"] = "🎉 GOOOL! Cenário será resetado em 3 segundos..."
                pygame.display.flip()
                pygame.time.wait(3000)
                estado_jogo = resetar_cenario()

        # Desenhar tudo
        tela.fill(COR_FUNDO)
        
        # Desenhar painel superior
        desenhar_painel_superior(tela, estado_jogo, fonte)
        
        # Desenhar grade
        desenhar_grade(tela)
        
        # Desenhar zonas de perigo
        desenhar_zonas_perigo(tela, estado_jogo["obstaculos"])
        
        # Desenhar caminho com custos
        if estado_jogo["caminho_atual"]:
            desenhar_caminho_com_custos(tela, estado_jogo["caminho_atual"], estado_jogo["debug_info"])

        # Desenhar elementos do jogo
        desenhar_retangulo(tela, estado_jogo["pos_gol"], COR_GOL)
        
        for obs in estado_jogo["obstaculos"]:
            desenhar_retangulo(tela, obs, COR_OBSTACULO)

        if estado_jogo["tem_bola"]:
            desenhar_retangulo(tela, estado_jogo["pos_robo"], COR_ROBO_COM_BOLA)
            desenhar_circulo(tela, estado_jogo["pos_robo"], COR_BOLA, raio_fator=0.3)
        else:
            desenhar_retangulo(tela, estado_jogo["pos_robo"], COR_ROBO)
            desenhar_circulo(tela, estado_jogo["pos_bola"], COR_BOLA)
        
        # Desenhar painel de informações
        desenhar_painel_info(tela, estado_jogo, estado_jogo["debug_info"], fonte)
            
        # Desenhar painel inferior com botões
        painel_inferior = pygame.Rect(0, ALTURA_TELA - ALTURA_PAINEL_INFERIOR, LARGURA_GRID * TAMANHO_CELULA, ALTURA_PAINEL_INFERIOR)
        pygame.draw.rect(tela, COR_PAINEL, painel_inferior)
        
        texto_play = "⏸️ Pause" if estado_jogo["simulacao_rodando"] else "▶️ Play"
        desenhar_botao(tela, fonte_botao, botao_play_pause, texto_play, COR_BOTAO, COR_TEXTO_BOTAO)
        desenhar_botao(tela, fonte_botao, botao_reset, "🔄 Reset", COR_BOTAO, COR_TEXTO_BOTAO)
        desenhar_botao(tela, fonte_botao, botao_step, "👣 Step", COR_BOTAO, COR_TEXTO_BOTAO)

        pygame.display.flip()
        clock.tick(3)  # Mais lento para análise

if __name__ == '__main__':
    main()