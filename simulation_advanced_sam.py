import pygame
import numpy as np
import random
import matplotlib.pyplot as plt

# --- CONFIGURAÇÕES GERAIS ---
LARGURA, ALTURA = 800, 800
TAMANHO_CELULA = 10
COLS = LARGURA // TAMANHO_CELULA
LINS = ALTURA // TAMANHO_CELULA
FPS = 15 

# --- DEFINIÇÃO DOS ESTADOS (IDs) ---
VAZIO = 0
SAM_PRONTA = 2      # Verde
SAM_RECARGA = 3     # Amarelo (Vulnerável)
INTERFERENCIA = 4   # Cinza
DRONE = 5           # Vermelho
CACA = 6            # Ciano
STEALTH = 7         # Cinza Escuro

# --- CONFIGURAÇÃO DE BALANCEAMENTO ---
CHANCE_SPAWN = 0.08         
PROB_DRONE = 0.60           
PROB_CACA = 0.25            
PROB_STEALTH = 0.15         

TEMPO_DURACAO_CHAFF = 8     
TEMPO_RECARGA_SAM = 15      
CHANCE_DETECCAO_STEALTH = 0.20 

# --- CORES (RGB) ---
CORES = {
    VAZIO: (10, 10, 20),           
    SAM_PRONTA: (0, 255, 0),       
    SAM_RECARGA: (200, 200, 0),    
    INTERFERENCIA: (100, 100, 100),
    DRONE: (255, 50, 50),          
    CACA: (0, 255, 255),           
    STEALTH: (40, 40, 40)          
}

# --- LISTAS PARA O GRÁFICO ---
historico_inimigos = []
historico_abatidos = []
historico_vazamento = []

def inicializar_simulacao():
    grade = np.zeros((LINS, COLS), dtype=int)
    timers = np.zeros((LINS, COLS), dtype=int)
    
    area_spawn_sam = grade[LINS//2:, :]
    rng = np.random.random(area_spawn_sam.shape)
    locais_sam = (area_spawn_sam == VAZIO) & (rng < 0.5)
    area_spawn_sam[locais_sam] = SAM_PRONTA
    
    return grade, timers

def calcular_proxima_geracao(grade, timers):
    nova_grade = grade.copy()
    novos_timers = timers.copy()
    
    # --- 1. ATUALIZAÇÃO DE TIMERS ---
    mask_timers_ativos = (novos_timers > 0)
    novos_timers[mask_timers_ativos] -= 1
    
    mask_fuma_acabou = (grade == INTERFERENCIA) & (novos_timers == 0)
    nova_grade[mask_fuma_acabou] = VAZIO
    
    mask_sam_recarregou = (grade == SAM_RECARGA) & (novos_timers == 0)
    nova_grade[mask_sam_recarregou] = SAM_PRONTA
    
    # --- 2. MOVIMENTO DOS INIMIGOS ---
    mask_drone = (grade == DRONE)
    mask_caca = (grade == CACA)
    mask_stealth = (grade == STEALTH)
    
    def mover_grupo(mask_quem, steps):
        destino_potencial = np.roll(grade, -steps, axis=0)
        
    
        # O destino é válido se for VAZIO, FUMAÇA ou SAM_RECARGA (Amarela)
        # Isso permite que o inimigo "atropele" a SAM em recarga.
        mask_destino_livre = (destino_potencial == VAZIO) | \
                             (destino_potencial == INTERFERENCIA) | \
                             (destino_potencial == SAM_RECARGA)
        
        quem_move = mask_quem & mask_destino_livre
        nova_grade[quem_move] = VAZIO 
        mask_destino = np.roll(quem_move, steps, axis=0)
        return quem_move, mask_destino

    # Movimentos
    quem_move_drone, dest_drone = mover_grupo(mask_drone, 1)
    nova_grade[dest_drone] = DRONE
    
    quem_move_stealth, dest_stealth = mover_grupo(mask_stealth, 1)
    nova_grade[dest_stealth] = STEALTH
    
    # Lógica do Caça (Pulo 2)
    destino_2 = np.roll(grade, -2, axis=0)
    
    # Caça pode pousar em cima de SAM recarregando no pulo duplo
    livre_2 = (destino_2 == VAZIO) | \
              (destino_2 == INTERFERENCIA) | \
              (destino_2 == SAM_RECARGA)
              
    move_2 = mask_caca & livre_2
    nova_grade[move_2] = VAZIO
    dest_final_caca_2 = np.roll(move_2, 2, axis=0)
    nova_grade[dest_final_caca_2] = CACA
    
    # Caça tenta pular 1 se não deu 2
    sobras_caca = mask_caca & (~move_2)
    quem_move_1, dest_caca_1 = mover_grupo(sobras_caca, 1)
    nova_grade[dest_caca_1] = CACA

    # --- 3. COMBATE E INTERFERÊNCIA ---
    mask_inimigos_ativos = (nova_grade == DRONE) | (nova_grade == CACA) | (nova_grade == STEALTH)
    
    viz_n = np.roll(nova_grade, 1, axis=0)
    viz_s = np.roll(nova_grade, -1, axis=0)
    viz_w = np.roll(nova_grade, 1, axis=1)
    viz_e = np.roll(nova_grade, -1, axis=1)
    viz_nw = np.roll(viz_n, 1, axis=1)
    viz_ne = np.roll(viz_n, -1, axis=1)
    viz_sw = np.roll(viz_s, 1, axis=1)
    viz_se = np.roll(viz_s, -1, axis=1)
    
    vizinhos_fumaça = (viz_n==INTERFERENCIA)|(viz_s==INTERFERENCIA)|(viz_w==INTERFERENCIA)|(viz_e==INTERFERENCIA)| \
                      (viz_nw==INTERFERENCIA)|(viz_ne==INTERFERENCIA)|(viz_sw==INTERFERENCIA)|(viz_se==INTERFERENCIA)
    
    sams_letais = (nova_grade == SAM_PRONTA) & (~vizinhos_fumaça)
    
    sam_n = np.roll(sams_letais, 1, axis=0)
    sam_s = np.roll(sams_letais, -1, axis=0)
    sam_w = np.roll(sams_letais, 1, axis=1)
    sam_e = np.roll(sams_letais, -1, axis=1)
    
    ameaca_sam = sam_n | sam_s | sam_w | sam_e 
    ameaca_sam |= np.roll(sam_n, 1, axis=1) | np.roll(sam_n, -1, axis=1) | \
                  np.roll(sam_s, 1, axis=1) | np.roll(sam_s, -1, axis=1)

    inimigos_na_mira = mask_inimigos_ativos & ameaca_sam
    
    fator_sorte = np.random.random(grade.shape)
    escapou_stealth = (nova_grade == STEALTH) & (fator_sorte > CHANCE_DETECCAO_STEALTH)
    
    morrem = inimigos_na_mira & (~escapou_stealth)
    
    nova_grade[morrem] = INTERFERENCIA
    novos_timers[morrem] = TEMPO_DURACAO_CHAFF
    
    num_abates = np.sum(morrem)
    
    viz_morreu_n = np.roll(morrem, 1, axis=0)
    viz_morreu_s = np.roll(morrem, -1, axis=0)
    vizinho_morreu = viz_morreu_n | viz_morreu_s | np.roll(morrem, 1, axis=1) | np.roll(morrem, -1, axis=1)
    
    sams_que_atiraram = sams_letais & vizinho_morreu
    nova_grade[sams_que_atiraram] = SAM_RECARGA
    novos_timers[sams_que_atiraram] = TEMPO_RECARGA_SAM

    # --- 4. SPAWN ---
    if np.random.random() < 1.0:
        colunas_livres = (nova_grade[0, :] == VAZIO)
        dados = np.random.random(COLS)
        spawn_mask = colunas_livres & (dados < CHANCE_SPAWN)
        
        tipos_rand = np.random.random(COLS)
        idx_drone = spawn_mask & (tipos_rand < PROB_DRONE)
        idx_caca = spawn_mask & (tipos_rand >= PROB_DRONE) & (tipos_rand < (PROB_DRONE + PROB_CACA))
        idx_stealth = spawn_mask & (tipos_rand >= (PROB_DRONE + PROB_CACA))
        
        nova_grade[0, idx_drone] = DRONE
        nova_grade[0, idx_caca] = CACA
        nova_grade[0, idx_stealth] = STEALTH
    
    return nova_grade, novos_timers, num_abates

def desenhar(win, grade):
    win.fill((0, 0, 0))
    coords = np.argwhere(grade != VAZIO)
    for r, c in coords:
        val = grade[r, c]
        cor = CORES.get(val, (255, 255, 255))
        
        if val == STEALTH:
            pygame.draw.rect(win, cor, (c*TAMANHO_CELULA+2, r*TAMANHO_CELULA+2, TAMANHO_CELULA-4, TAMANHO_CELULA-4))
        elif val == INTERFERENCIA:
             pygame.draw.circle(win, cor, (c*TAMANHO_CELULA + TAMANHO_CELULA//2, r*TAMANHO_CELULA + TAMANHO_CELULA//2), TAMANHO_CELULA//1.5)
        else:
            pygame.draw.rect(win, cor, (c*TAMANHO_CELULA, r*TAMANHO_CELULA, TAMANHO_CELULA-1, TAMANHO_CELULA-1))

    fonte = pygame.font.SysFont('Arial', 14)
    texto = [
        "VERDE: SAM Pronta | AMARELO: SAM Recarregando (Atropelável)",
        "VERMELHO: Drone | CIANO: Caça | CINZA: Stealth",
        "CINZA CLARO: Interferência",
        f"Inimigos Ativos: {len(coords)}"
    ]
    for i, t in enumerate(texto):
        img = fonte.render(t, True, (255, 255, 255))
        win.blit(img, (10, 10 + i*18))

def main():
    pygame.init()
    win = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Simulador A2/AD - SAM Recarga Atropelável")
    clock = pygame.time.Clock()
    
    grade, timers = inicializar_simulacao()
    rodando = True
    
    print("Simulação iniciada.")
    
    while rodando:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                grade, timers = inicializar_simulacao()
                historico_inimigos.clear()
                historico_abatidos.clear()
                historico_vazamento.clear()
        
        ult_linha = grade[-1, :]
        n_vazamento = np.sum((ult_linha == DRONE) | (ult_linha == CACA) | (ult_linha == STEALTH))
        n_ativos = np.sum((grade == DRONE) | (grade == CACA) | (grade == STEALTH))
        
        grade, timers, num_abates = calcular_proxima_geracao(grade, timers)
        
        historico_inimigos.append(n_ativos)
        historico_abatidos.append(num_abates)
        historico_vazamento.append(n_vazamento)

        desenhar(win, grade)
        pygame.display.flip()
        
    pygame.quit()
    
    plt.figure(figsize=(12, 6))
    plt.plot(historico_inimigos, label='Inimigos Ativos', color='blue', alpha=0.5, linewidth=1)
    plt.plot(np.cumsum(historico_abatidos), label='Total de Abates', color='orange', linewidth=2.5)
    plt.plot(np.cumsum(historico_vazamento), label='Total de Vazamentos', color='green', linestyle='--', linewidth=2.5)
    plt.title('Performance A2/AD (Com Supressão de SAM)')
    plt.xlabel('Tempo')
    plt.ylabel('Células')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()