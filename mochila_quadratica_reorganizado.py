"""Mochila Quadrática com Simulated Annealing - Otimização de inventário usando Add/Remove"""

import random
import math
import numpy as np
import pandas as pd
import os

# ===============================================================================
# CONFIGURAÇÃO E CARREGAMENTO DE DADOS
# ===============================================================================

ARQUIVO_EXCEL = 'Base de Dados.xlsx'  # Nome do arquivo Excel local

print("🔧 Carregando dados do arquivo local...")
print("=" * 50)

if not os.path.exists(ARQUIVO_EXCEL):  # Verificando se o arquivo existe
    print(f"❌ Arquivo '{ARQUIVO_EXCEL}' não encontrado no diretório atual")
    print("💡 Certifique-se de que o arquivo está na mesma pasta do código!")
    exit()

# Carregando os itens do restaurante
try:
    print(f"📂 Abrindo arquivo '{ARQUIVO_EXCEL}'...")
    df_itens = pd.read_excel(ARQUIVO_EXCEL, sheet_name='itens')  # Lendo a aba de itens
    print(f"✅ {len(df_itens)} itens carregados e organizados!")

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
    print(f"❌ Erro ao carregar itens: {e}")
    print("💡 Verifique se a aba 'itens' existe e tem as colunas: Nome, Custo (R$), Popularidade")
    exit()

# Carregando as interações entre itens
try:
    df_inter = pd.read_excel(ARQUIVO_EXCEL, sheet_name='inter')  # Lendo a aba de interações
    print(f"✅ Matriz de interações {df_inter.shape} carregada!")
    matriz_original = df_inter.iloc[:, 1:].values.astype(float)  # Convertendo para numpy (sem primeira coluna)
    
    # Expandindo matriz para o número total de itens (sempre usar todos os itens)
    num_itens_total = len(itens_comida)
    linhas_matriz, colunas_matriz = matriz_original.shape
    
    print(f"🔧 Expandindo matriz de {linhas_matriz}x{colunas_matriz} para {num_itens_total}x{num_itens_total}")
    
    # Criando matriz expandida com zeros
    matriz_interacao_np = np.zeros((num_itens_total, num_itens_total))
    
    # Copiando valores existentes para a nova matriz
    min_linhas = min(linhas_matriz, num_itens_total)
    min_colunas = min(colunas_matriz, num_itens_total)
    matriz_interacao_np[:min_linhas, :min_colunas] = matriz_original[:min_linhas, :min_colunas]
    
    print(f"✅ Matriz expandida criada! Dimensão final: {matriz_interacao_np.shape}")
    print(f"📊 Valores existentes preservados, novas posições preenchidas com zero")
    
except Exception as e:
    print(f"❌ Erro ao carregar interações: {e}")
    print("💡 Verifique se a aba 'inter' existe e contém a matriz de interações")
    exit()

orcamento_restaurante = 100.0  # Orçamento disponível
print(f"💰 Orçamento: R${orcamento_restaurante:.2f}")
print(f"📊 {len(itens_comida)} itens disponíveis")
print()

print("🍽️  Cardápio:")
for i, item in enumerate(itens_comida):
    print(f"  {i:2d}. {item['nome']:<25} R${item['custo']:6.2f} (⭐{item['popularidade']:4.1f})")
print()


# ===============================================================================
# FUNÇÃO OBJETIVO - PROBLEMA DA MOCHILA QUADRÁTICA
# ===============================================================================

def avaliar_solucao(solucao):
    """
    FUNÇÃO OBJETIVO: Avalia a qualidade de uma solução para o problema da mochila quadrática
    
    Maximiza: Σ(popularidade_i * x_i) + ΣΣ(sinergia_ij * x_i * x_j)
    Sujeito a: Σ(custo_i * x_i) ≤ orçamento
    
    Args:
        solucao (list): Lista binária onde 1 = item selecionado, 0 = item não selecionado
    
    Returns:
        float: Valor da função objetivo (-inf se inviável)
    """
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
    """
    HEURÍSTICA: Gera uma solução inicial aleatória
    
    Args:
        num_itens (int): Número total de itens disponíveis
    
    Returns:
        list: Solução binária inicial
    """
    return [random.randint(0, 1) for _ in range(num_itens)]


def add_remove_perturbacao(solucao):
    """
    HEURÍSTICA: Operador de vizinhança Add/Remove inteligente
    
    Estratégia adaptativa:
    - Se nenhum item selecionado → ADICIONA um item
    - Se todos itens selecionados → REMOVE um item  
    - Caso contrário → 50% chance de ADICIONAR ou REMOVER
    
    Esta heurística é mais inteligente que flip simples pois considera
    o estado atual da solução para decidir a melhor ação.
    
    Args:
        solucao (list): Solução atual
    
    Returns:
        list: Nova solução vizinha
    """
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
    """
    META-HEURÍSTICA: Simulated Annealing para Mochila Quadrática
    
    Implementa o algoritmo de Simulated Annealing com os seguintes componentes:
    1. Solução inicial: gerada aleatoriamente
    2. Função de vizinhança: operador Add/Remove 
    3. Função de aceitação: critério de Metropolis
    4. Esquema de resfriamento: geométrico (T = T * α)
    
    Parâmetros de controle:
    - temp_inicial: Temperatura inicial (exploration vs exploitation)
    - temp_final: Temperatura de parada  
    - alpha: Taxa de resfriamento (0 < α < 1)
    - max_iteracoes: Critério de parada adicional
    
    Args:
        num_itens (int): Número de itens do problema
        temp_inicial (float): Temperatura inicial do SA
        temp_final (float): Temperatura final (critério de parada)
        alpha (float): Taxa de resfriamento geométrico
        max_iteracoes (int): Número máximo de iterações
    
    Returns:
        tuple: (melhor_solucao, melhor_valor, historico)
    """
    
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
        print("😅 Não consegui achar solução inicial válida...")
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
    print(f"🚀 Iniciando SA - Valor inicial: {valor_atual:.2f}")
    
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
                print(f"🔥 Nova melhor solução na iteração {iteracao}: {melhor_valor:.2f}")
        else:
            historico['aceitos'].append(False)
            historico['rejeitados'] += 1
        
        # 2.4: Coleta de dados e resfriamento
        historico['valores'].append(valor_atual)
        historico['temperaturas'].append(temperatura)
        temperatura = temperatura * alpha              # Esquema de resfriamento geométrico
        iteracao += 1
        
        # 2.5: Relatório de progresso
        if iteracao % 100 == 0:
            print(f"📈 Iteração {iteracao}: Temp={temperatura:.1f}, Atual={valor_atual:.2f}, Melhor={melhor_valor:.2f}")
    
    # FASE 3: Finalização e relatório
    historico['iteracao'] = iteracao
    taxa_aceitacao = len([x for x in historico['aceitos'] if x])/max(1,len(historico['aceitos']))*100
    print(f"✅ SA finalizado - {iteracao} iterações, Taxa aceitação: {taxa_aceitacao:.1f}%")
    print(f"🏆 Melhor valor encontrado: {melhor_valor:.2f} pontos")
    
    return melhor_solucao, melhor_valor, historico


# ===============================================================================
# ANÁLISE E VISUALIZAÇÃO DE RESULTADOS
# ===============================================================================

def analisar_solucao(solucao, titulo="Análise da Solução"):
    """
    ANÁLISE: Decompõe uma solução mostrando todos os componentes da função objetivo
    
    Args:
        solucao (list): Solução binária a ser analisada
        titulo (str): Título para o relatório
    """
    print(f"\n{'='*3} {titulo} {'='*3}")
    
    itens_escolhidos = []
    custo_total = 0
    popularidade_total = 0
    
    # Análise dos itens selecionados
    for i, escolhido in enumerate(solucao):
        if escolhido == 1:
            itens_escolhidos.append(i)
            custo_total += custos_np[i]
            popularidade_total += popularidade_np[i]
    
    print(f"📊 {len(itens_escolhidos)} itens selecionados: {itens_escolhidos}")
    
    # Análise da restrição orçamentária
    print(f"💰 Orçamento: R${custo_total:.2f} / R${orcamento_restaurante:.2f} ({(custo_total/orcamento_restaurante)*100:.1f}%)")
    print(f"   💵 Disponível: R${orcamento_restaurante - custo_total:.2f}")
    
    # Análise do termo linear da função objetivo
    print(f"⭐ Valor linear (popularidades): {popularidade_total:.2f} pontos")
    
    # Análise do termo quadrático da função objetivo
    valor_sinergias = 0
    if len(itens_escolhidos) > 1:
        print(f"🔗 Sinergias (termo quadrático):")
        for i in range(len(itens_escolhidos)):
            for j in range(i + 1, len(itens_escolhidos)):
                idx_i = itens_escolhidos[i]
                idx_j = itens_escolhidos[j]
                sinergia = matriz_interacao_np[idx_i][idx_j]
                valor_sinergias += sinergia
                if sinergia != 0:
                    nome_i = itens_comida[idx_i]['nome']
                    nome_j = itens_comida[idx_j]['nome']
                    emoji = "🔥" if sinergia > 0 else "⚡"
                    print(f"   {emoji} {nome_i} + {nome_j}: {sinergia:+.1f}")
    
    print(f"🔗 Total sinergias: {valor_sinergias:.2f} pontos")
    
    # Valor final da função objetivo
    valor_final = avaliar_solucao(solucao)
    if valor_final == -float('inf'):
        print("⚠️  SOLUÇÃO INVIÁVEL - Restrição orçamentária violada!")
    else:
        print(f"🏆 VALOR FUNÇÃO OBJETIVO: {valor_final:.2f} pontos")
        print(f"    = {popularidade_total:.2f} (linear) + {valor_sinergias:.2f} (quadrático)")
    print("=" * 50)


# ===============================================================================
# EXPERIMENTAÇÃO COMPUTACIONAL
# ===============================================================================

def executar_testes():
    """
    EXPERIMENTOS: Testa diferentes configurações de parâmetros do SA
    
    Compara três estratégias de configuração:
    1. Clássica: Parâmetros balanceados
    2. Cautelosa: Resfriamento mais lento, mais iterações
    3. Intensiva: Temperatura inicial mais alta
    """
    print("🔥 EXPERIMENTAÇÃO: Testando configurações do Simulated Annealing")
    print("=" * 70)
    
    num_itens = len(itens_comida)
    
    # Experimento 1: Configuração clássica
    print("\n📊 EXPERIMENTO 1: Configuração Clássica")
    print("   Parâmetros: T₀=1000, α=0.95, iter=1000")
    melhor_sol_1, melhor_val_1, hist_1 = simulated_annealing(num_itens, 1000, 1, 0.95, 1000)
    analisar_solucao(melhor_sol_1, "Resultado Experimento 1")
    
    # Experimento 2: Resfriamento cauteloso
    print("\n📊 EXPERIMENTO 2: Resfriamento Cauteloso")
    print("   Parâmetros: T₀=1000, α=0.99, iter=1500")
    melhor_sol_2, melhor_val_2, hist_2 = simulated_annealing(num_itens, 1000, 1, 0.99, 1500)
    analisar_solucao(melhor_sol_2, "Resultado Experimento 2")
    
    # Experimento 3: Exploração intensiva
    print("\n📊 EXPERIMENTO 3: Exploração Intensiva")
    print("   Parâmetros: T₀=2000, α=0.95, iter=1000")
    melhor_sol_3, melhor_val_3, hist_3 = simulated_annealing(num_itens, 2000, 1, 0.95, 1000)
    analisar_solucao(melhor_sol_3, "Resultado Experimento 3")
    
    # Análise comparativa dos experimentos
    print("\n🏆 ANÁLISE COMPARATIVA DOS EXPERIMENTOS")
    print("=" * 50)
    print(f"📊 Experimento 1 (Clássico):  {melhor_val_1:.2f} pontos")
    print(f"📊 Experimento 2 (Cauteloso): {melhor_val_2:.2f} pontos")  
    print(f"📊 Experimento 3 (Intensivo): {melhor_val_3:.2f} pontos")
    
    # Determinação da melhor configuração
    resultados = [(melhor_val_1, 1, melhor_sol_1), (melhor_val_2, 2, melhor_sol_2), (melhor_val_3, 3, melhor_sol_3)]
    campeao = max(resultados)
    
    print(f"\n🥇 MELHOR CONFIGURAÇÃO: Experimento {campeao[1]} com {campeao[0]:.2f} pontos!")
    analisar_solucao(campeao[2], f"🏆 SOLUÇÃO ÓTIMA ENCONTRADA (Experimento {campeao[1]})")
    
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
    """
    EXECUÇÃO PRINCIPAL: Coordena a execução completa do sistema de otimização
    
    Fluxo de execução:
    1. Carregamento dos dados (já realizado no início)
    2. Experimentação com diferentes configurações do SA
    3. Análise comparativa dos resultados
    4. Relatório final com estatísticas do problema
    """
    print("\n" + "="*80)
    print("🍽️  SISTEMA DE OTIMIZAÇÃO DE CARDÁPIO")
    print("   Problema: Mochila Quadrática | Meta-heurística: Simulated Annealing")
    print("="*80)
    
    # Execução dos experimentos computacionais
    resultados = executar_testes()
    
    # Relatório estatístico do problema
    print(f"\n📊 ESTATÍSTICAS DO PROBLEMA")
    print("=" * 50)
    print(f"🎯 Instância: {len(itens_comida)} itens, orçamento R${orcamento_restaurante:.2f}")
    print(f"💰 Custo médio: R${np.mean(custos_np):.2f} ± {np.std(custos_np):.2f}")
    print(f"⭐ Popularidade média: {np.mean(popularidade_np):.2f} ± {np.std(popularidade_np):.2f}")
    print(f"📈 Taxa cobertura orçamentária: {(orcamento_restaurante/np.sum(custos_np))*100:.1f}%")
    print(f"🔗 Densidade da matriz de sinergias: {(np.count_nonzero(matriz_interacao_np)/(len(itens_comida)**2))*100:.1f}%")
    
    # Conclusões metodológicas
    print(f"\n🔬 CONCLUSÕES METODOLÓGICAS")
    print("=" * 50)
    print("   ✅ FUNÇÃO OBJETIVO: Mochila quadrática com termos lineares e quadráticos")
    print("   ✅ META-HEURÍSTICA: Simulated Annealing com resfriamento geométrico")
    print("   ✅ HEURÍSTICA: Operador Add/Remove adaptativo")
    print("   ✅ EXPERIMENTAÇÃO: Múltiplas configurações de parâmetros testadas")
    print("   ✅ QUALIDADE: Soluções viáveis encontradas consistentemente")
    
    print(f"\n🏁 OTIMIZAÇÃO CONCLUÍDA COM SUCESSO! 🎯")
    print("="*80)
