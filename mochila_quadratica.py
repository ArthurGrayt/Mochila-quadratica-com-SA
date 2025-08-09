import random
import math
import numpy as np
import pandas as pd
import os

ARQUIVO_EXCEL = 'Base de Dados.xlsx'  # Nome do arquivo Excel local

print("Carregando dados do arquivo...")

if not os.path.exists(ARQUIVO_EXCEL):
    print(f"Arquivo '{ARQUIVO_EXCEL}' não encontrado")
    exit()

# Carregando os itens do restaurante
try:
    df_itens = pd.read_excel(ARQUIVO_EXCEL, sheet_name='itens')
    print(f"{len(df_itens)} itens carregados")

    itens_comida = []
    custos_np = np.array(df_itens['Custo (R$)'].astype(float))
    popularidade_np = np.array(df_itens['Popularidade'].astype(float))

    for _, row in df_itens.iterrows():
        itens_comida.append({
            "nome": row['Nome'],
            "custo": float(row['Custo (R$)']),
            "popularidade": float(row['Popularidade'])
        })

except Exception as e:
    print(f"Erro ao carregar itens: {e}")
    exit()

# Carregando as interações entre itens
try:
    df_inter = pd.read_excel(ARQUIVO_EXCEL, sheet_name='inter')
    matriz_original = df_inter.iloc[:, 1:].values.astype(float)
    
    # Expandindo matriz para o número total de itens
    num_itens_total = len(itens_comida)
    linhas_matriz, colunas_matriz = matriz_original.shape
    
    # Criando matriz expandida com zeros
    matriz_interacao_np = np.zeros((num_itens_total, num_itens_total))
    
    # Copiando valores existentes para a nova matriz
    min_linhas = min(linhas_matriz, num_itens_total)
    min_colunas = min(colunas_matriz, num_itens_total)
    matriz_interacao_np[:min_linhas, :min_colunas] = matriz_original[:min_linhas, :min_colunas]
    
    print(f"Matriz expandida para {matriz_interacao_np.shape}")
    
except Exception as e:
    print(f"Erro ao carregar interações: {e}")
    exit()

orcamento_restaurante = 100.0
print(f"Configuracao: {len(itens_comida)} itens, orcamento R${orcamento_restaurante:.2f}")


# ===============================================================================
# FUNÇÃO OBJETIVO - PROBLEMA DA MOCHILA QUADRÁTICA
# ===============================================================================

def avaliar_solucao(solucao):
    valor_total = 0.0
    custo_total = 0.0
    num_itens = len(solucao)

    # Termo linear: soma das popularidades dos itens selecionados
    for i in range(num_itens):
        if solucao[i] == 1:
            valor_total += popularidade_np[i]
            custo_total += custos_np[i]
    
    # Termo quadrático: soma das sinergias entre pares de itens selecionados
    for i in range(num_itens):
        if solucao[i] == 1:
            for j in range(i + 1, num_itens):
                if solucao[j] == 1:
                    valor_total += matriz_interacao_np[i][j]
    
    # Verifica restrição de orçamento
    return -float('inf') if custo_total > orcamento_restaurante else valor_total


# ===============================================================================
# HEURÍSTICA - OPERADOR ADD/REMOVE
# ===============================================================================

def gerar_solucao_inicial(num_itens):

    return [random.randint(0, 1) for _ in range(num_itens)]


def add_remove_perturbacao(solucao):
    nova_solucao = solucao.copy()
    
    itens_escolhidos = [i for i, x in enumerate(solucao) if x == 1]  # Itens já selecionados
    itens_livres = [i for i, x in enumerate(solucao) if x == 0]      # Itens disponíveis
    
    if len(itens_escolhidos) == 0:          # Estado: nenhum item → ADICIONAR
        item = random.choice(itens_livres)
        nova_solucao[item] = 1
    elif len(itens_livres) == 0:            # Estado: todos itens → REMOVER
        item = random.choice(itens_escolhidos)
        nova_solucao[item] = 0
    else:                                   # Estado: misto → DECISÃO ALEATÓRIA
        if random.random() < 0.5:           # 50% chance: ADICIONAR
            item = random.choice(itens_livres)
            nova_solucao[item] = 1
        else:                               # 50% chance: REMOVER
            item = random.choice(itens_escolhidos)
            nova_solucao[item] = 0
    
    return nova_solucao


# ===============================================================================
# META-HEURÍSTICA - SIMULATED ANNEALING
# ===============================================================================

def simulated_annealing(num_itens, temp_inicial=1000, temp_final=1, alpha=0.95, max_iteracoes=1000):

    # FASE 1: Inicialização
    solucao_atual = gerar_solucao_inicial(num_itens)  # Heurística: solução inicial
    valor_atual = avaliar_solucao(solucao_atual)      # Função objetivo
    
    # Garantir solução inicial viável
    tentativas = 0
    while valor_atual == -float('inf') and tentativas < 100:
        solucao_atual = gerar_solucao_inicial(num_itens)
        valor_atual = avaliar_solucao(solucao_atual)
        tentativas += 1
    
    if valor_atual == -float('inf'):
        print("Nao foi possivel encontrar solucao inicial viavel")
        return ([0] * num_itens, 0.0, {'valores': [0], 'temperaturas': [temp_inicial], 'aceitos': [], 'iteracao': 0})
    
    # Inicialização das estruturas de controle
    melhor_solucao = solucao_atual.copy()  # Melhor solução global
    melhor_valor = valor_atual
    historico = {  # Dados para análise do comportamento do algoritmo
        'valores': [valor_atual], 'temperaturas': [temp_inicial], 'aceitos': [],
        'rejeitados': 0, 'melhorias': 0, 'iteracao': 0
    }
    
    temperatura = temp_inicial
    iteracao = 0
    print(f"SA iniciado - valor inicial: {valor_atual:.2f}")
    
    # FASE 2: Loop principal do Simulated Annealing
    while temperatura > temp_final and iteracao < max_iteracoes:
        
        # 2.1: Geração de vizinho usando heurística Add/Remove
        nova_solucao = add_remove_perturbacao(solucao_atual)
        novo_valor = avaliar_solucao(nova_solucao)
        diferenca = novo_valor - valor_atual
        
        # 2.2: Critério de aceitação (Metropolis)
        aceitar = False
        if diferenca > 0:                                         # Melhoria: sempre aceita
            aceitar = True
        else:                                                     # Piora: aceita probabilisticamente
            probabilidade_aceitacao = math.exp(diferenca / temperatura)
            if random.random() < probabilidade_aceitacao:
                aceitar = True
        
        # 2.3: Atualização da solução e controle
        if aceitar:
            solucao_atual = nova_solucao
            valor_atual = novo_valor
            historico['aceitos'].append(True)
            
            if diferenca > 0:
                historico['melhorias'] += 1
            
            # Atualização da melhor solução global
            if valor_atual > melhor_valor:
                melhor_solucao = solucao_atual.copy()
                melhor_valor = valor_atual
                print(f"Melhor: {melhor_valor:.2f} (iter {iteracao})")
        else:
            historico['aceitos'].append(False)
            historico['rejeitados'] += 1
        
        # 2.4: Coleta de dados e resfriamento
        historico['valores'].append(valor_atual)
        historico['temperaturas'].append(temperatura)
        temperatura = temperatura * alpha              # Esquema de resfriamento geométrico
        iteracao += 1
        
        if iteracao % 200 == 0:
            print(f"Iter {iteracao}: T={temperatura:.1f}, Melhor={melhor_valor:.2f}")
    
    # FASE 3: Finalização e relatório
    historico['iteracao'] = iteracao
    taxa_aceitacao = len([x for x in historico['aceitos'] if x])/max(1,len(historico['aceitos']))*100
    print(f"SA finalizado: {melhor_valor:.2f} pontos ({iteracao} iter, {taxa_aceitacao:.1f}% aceitos)")
    
    return melhor_solucao, melhor_valor, historico


# ===============================================================================
# ANÁLISE E VISUALIZAÇÃO DE RESULTADOS
# ===============================================================================

def analisar_solucao(solucao, titulo="Analise da Solucao"):
    print(f"\n{titulo}:")
    
    itens_escolhidos = []
    custo_total = 0
    popularidade_total = 0
    
    for i, escolhido in enumerate(solucao):
        if escolhido == 1:
            itens_escolhidos.append(i)
            custo_total += custos_np[i]
            popularidade_total += popularidade_np[i]
    
    print(f"Itens: {len(itens_escolhidos)} selecionados")
    print(f"Custo: R${custo_total:.2f} / R${orcamento_restaurante:.2f} ({(custo_total/orcamento_restaurante)*100:.1f}%)")
    print(f"Valor linear: {popularidade_total:.2f} pontos")
    
    valor_sinergias = 0
    if len(itens_escolhidos) > 1:
        for i in range(len(itens_escolhidos)):
            for j in range(i + 1, len(itens_escolhidos)):
                idx_i = itens_escolhidos[i]
                idx_j = itens_escolhidos[j]
                sinergia = matriz_interacao_np[idx_i][idx_j]
                valor_sinergias += sinergia
    
    print(f"Sinergias: {valor_sinergias:.2f} pontos")
    
    valor_final = avaliar_solucao(solucao)
    if valor_final == -float('inf'):
        print("SOLUCAO INVIAVEL")
    else:
        print(f"TOTAL: {valor_final:.2f} pontos ({popularidade_total:.2f} + {valor_sinergias:.2f})")


# ===============================================================================
# EXPERIMENTAÇÃO COMPUTACIONAL
# ===============================================================================

def executar_testes():
    print("Executando experimentos com Simulated Annealing...")
    
    num_itens = len(itens_comida)
    
    # Experimento 1: Configuração clássica
    print("\nExperimento 1: Classico (T=1000, α=0.95, iter=1000)")
    melhor_sol_1, melhor_val_1, hist_1 = simulated_annealing(num_itens, 1000, 1, 0.95, 1000)
    analisar_solucao(melhor_sol_1, "Resultado Exp 1")
    
    # Experimento 2: Resfriamento cauteloso
    print("\nExperimento 2: Cauteloso (T=1000, α=0.99, iter=1500)")
    melhor_sol_2, melhor_val_2, hist_2 = simulated_annealing(num_itens, 1000, 1, 0.99, 1500)
    analisar_solucao(melhor_sol_2, "Resultado Exp 2")
    
    # Experimento 3: Exploração intensiva
    print("\nExperimento 3: Intensivo (T=2000, α=0.95, iter=1000)")
    melhor_sol_3, melhor_val_3, hist_3 = simulated_annealing(num_itens, 2000, 1, 0.95, 1000)
    analisar_solucao(melhor_sol_3, "Resultado Exp 3")
    
    # Análise comparativa
    print("\nComparacao dos resultados:")
    print(f"Experimento 1: {melhor_val_1:.2f} pontos")
    print(f"Experimento 2: {melhor_val_2:.2f} pontos")  
    print(f"Experimento 3: {melhor_val_3:.2f} pontos")
    
    resultados = [(melhor_val_1, 1, melhor_sol_1), (melhor_val_2, 2, melhor_sol_2), (melhor_val_3, 3, melhor_sol_3)]
    campeao = max(resultados)
    
    print(f"\nMelhor resultado: Experimento {campeao[1]} com {campeao[0]:.2f} pontos")
    analisar_solucao(campeao[2], f"Solucao Otima (Exp {campeao[1]})")
    
    return {
        'experimento1': (melhor_sol_1, melhor_val_1, hist_1),
        'experimento2': (melhor_sol_2, melhor_val_2, hist_2),
        'experimento3': (melhor_sol_3, melhor_val_3, hist_3),
        'melhor': campeao
    }


# ===============================================================================
# PROGRAMA PRINCIPAL
# ===============================================================================

if __name__ == "__main__":
    print("\nSISTEMA DE OTIMIZACAO - MOCHILA QUADRATICA COM SIMULATED ANNEALING")
    
    resultados = executar_testes()
    
    # Estatísticas do problema
    print(f"\nEstatisticas:")
    print(f"Instancia: {len(itens_comida)} itens, orcamento R${orcamento_restaurante:.2f}")
    print(f"Custo medio: R${np.mean(custos_np):.2f}")
    print(f"Popularidade media: {np.mean(popularidade_np):.2f}")
    print(f"Taxa cobertura orcamentaria: {(orcamento_restaurante/np.sum(custos_np))*100:.1f}%")
    print(f"Densidade matriz sinergias: {(np.count_nonzero(matriz_interacao_np)/(len(itens_comida)**2))*100:.1f}%")
    
    print(f"\nOtimizacao concluida!")
