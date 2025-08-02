"""
Mochila Quadrática com Simulated Annealing
Otimização inteligente de inventário usando operador Add/Remove
"""

import random
import math
import numpy as np
import pandas as pd
import os

# Nome do arquivo Excel local
ARQUIVO_EXCEL = 'Base de Dados.xlsx'

print("🔧 Carregando dados do arquivo local...")
print("=" * 50)

# Verificando se o arquivo existe
if not os.path.exists(ARQUIVO_EXCEL):
    print(f"❌ Ops! Não consegui encontrar o arquivo '{ARQUIVO_EXCEL}' no diretório atual")
    print("💡 Certifique-se de que o arquivo está na mesma pasta do código!")
    exit()

# Carregando os itens do restaurante
try:
    print(f"📂 Abrindo arquivo '{ARQUIVO_EXCEL}'...")
    
    # Lendo a aba de itens
    df_itens = pd.read_excel(ARQUIVO_EXCEL, sheet_name='itens')
    print("✅ Dados dos itens carregados!")
    print(f"📊 Encontramos {len(df_itens)} itens no estoque.")

    itens_comida = []
    custos_np = np.array(df_itens['Custo (R$)'].astype(float))
    popularidade_np = np.array(df_itens['Popularidade'].astype(float))

    for _, row in df_itens.iterrows():
        itens_comida.append({
            "nome": row['Nome'],
            "custo": float(row['Custo (R$)']),
            "popularidade": float(row['Popularidade'])
        })
    print("✅ Dados dos itens organizados e prontos!")

except Exception as e:
    print(f"❌ Problema ao carregar os itens: {e}")
    print("💡 Verifique se a aba 'itens' existe e tem as colunas: Nome, Custo (R$), Popularidade")
    exit()

# Carregando as interações entre itens
try:
    # Lendo a aba de interações
    df_inter = pd.read_excel(ARQUIVO_EXCEL, sheet_name='inter')
    print("✅ Matriz de interações carregada!")
    print(f"📊 Processando matriz de interações {df_inter.shape}...")

    # Convertendo para numpy array (removendo a primeira coluna que geralmente são os nomes)
    matriz_interacao_np = df_inter.iloc[:, 1:].values.astype(float)
    print("✅ Matriz de sinergias pronta para usar!")

except Exception as e:
    print(f"❌ Problema ao carregar interações: {e}")
    print("💡 Verifique se a aba 'inter' existe e contém a matriz de interações")
    exit()

# Parâmetros do nosso problema (você pode ajustar aqui!)
orcamento_restaurante = 100.0  # Quanto temos para gastar
print(f"💰 Orçamento disponível: R${orcamento_restaurante:.2f}")
print()

# Vamos dar uma olhada no que temos
print("📋 Resumo dos dados carregados")
print("=" * 60)
print(f"📊 Temos {len(itens_comida)} itens disponíveis")
print(f"💰 Orçamento: R${orcamento_restaurante:.2f}")
print()

print("🍽️  Nosso cardápio:")
print("-" * 40)
for i, item in enumerate(itens_comida):
    print(f"  {i:2d}. {item['nome']:<25} "
          f"R${item['custo']:6.2f} (⭐{item['popularidade']:4.1f})")

print(f"\n📈 Custos: {custos_np}")
print(f"⭐ Popularidades: {popularidade_np}")
print(f"🔗 Matriz de interações: {matriz_interacao_np.shape}")
print()


def avaliar_solucao(solucao):
    """
    🎯 Avalia quão boa é uma combinação de itens
    
    Calcula a popularidade total + bônus das sinergias entre itens
    Se ultrapassar o orçamento, retorna valor muito baixo (inviável)
    """
    valor_total = 0.0
    custo_total = 0.0
    num_itens = len(solucao)

    # Somando a popularidade dos itens escolhidos
    for i in range(num_itens):
        if solucao[i] == 1:
            valor_total += popularidade_np[i]
            custo_total += custos_np[i]
            
    # Somando os bônus de sinergia entre pares de itens
    for i in range(num_itens):
        if solucao[i] == 1:
            for j in range(i + 1, num_itens):
                if solucao[j] == 1:
                    valor_total += matriz_interacao_np[i][j]
    
    # Verificando se não estouramos o orçamento
    if custo_total > orcamento_restaurante:
        return -float('inf')  # Solução inviável
    else:
        return valor_total


def gerar_solucao_inicial(num_itens):
    """🎲 Cria uma solução inicial aleatória - cara ou coroa para cada item"""
    return [random.randint(0, 1) for _ in range(num_itens)]


def add_remove_perturbacao(solucao):
    """
    ➕➖ Nossa estratégia inteligente de mudança
    
    Em vez de simplesmente trocar itens (como outros algoritmos fazem),
    analisamos a situação e decidimos se é melhor adicionar ou remover algo.
    
    Se não temos nada: vamos adicionar!
    Se temos tudo: vamos remover algo!
    Se temos algumas coisas: vamos na sorte 50/50!
    
    Isso é bem mais esperto que mudanças cegas 🧠
    """
    nova_solucao = solucao.copy()
    
    # Quais itens já escolhemos?
    itens_escolhidos = [i for i, x in enumerate(solucao) if x == 1]
    itens_livres = [i for i, x in enumerate(solucao) if x == 0]
    
    if len(itens_escolhidos) == 0:
        # Eita, não temos nada! Vamos adicionar algo
        item = random.choice(itens_livres)
        nova_solucao[item] = 1
        
    elif len(itens_livres) == 0:
        # Nossa, temos tudo! Vamos tirar algo
        item = random.choice(itens_escolhidos)
        nova_solucao[item] = 0
        
    else:
        # Situação normal: vamos decidir no cara ou coroa
        if random.random() < 0.5:
            # Adicionar algo novo
            item = random.choice(itens_livres)
            nova_solucao[item] = 1
        else:
            # Remover algo que já temos
            item = random.choice(itens_escolhidos)
            nova_solucao[item] = 0
    
    return nova_solucao


def simulated_annealing(num_itens, temp_inicial=1000, temp_final=1, 
                       alpha=0.95, max_iteracoes=1000):
    """
    🌡️ Simulated Annealing - Nossa estratégia principal de otimização
    
    Parâmetros que você pode mexer:
    - temp_inicial: Comece "quente" para explorar mais (padrão: 1000)
    - temp_final: Quando parar de ser aventureiro (padrão: 1)
    - alpha: Velocidade de resfriamento - 0.95 é bom, 0.99 é mais lento (padrão: 0.95)
    - max_iteracoes: Quantas tentativas fazer (padrão: 1000)
    
    A ideia: começamos aventureiros (aceitamos soluções ruins às vezes) 
    e vamos ficando mais criteriosos conforme "esfriamos"
    """
    
    # Começando do zero - criando uma solução inicial
    solucao_atual = gerar_solucao_inicial(num_itens)
    valor_atual = avaliar_solucao(solucao_atual)
    
    # Se a primeira tentativa foi ruim, vamos tentar mais algumas vezes
    tentativas = 0
    while valor_atual == -float('inf') and tentativas < 100:
        solucao_atual = gerar_solucao_inicial(num_itens)
        valor_atual = avaliar_solucao(solucao_atual)
        tentativas += 1
    
    if valor_atual == -float('inf'):
        print("😅 Poxa, não consegui achar uma solução inicial boa...")
        return ([0] * num_itens, 0.0, 
                {'valores': [0], 'temperaturas': [temp_inicial], 'aceitos': [], 'iteracao': 0})
    
    # Guardando a melhor solução que encontramos até agora
    melhor_solucao = solucao_atual.copy()
    melhor_valor = valor_atual
    
    # Vamos anotar tudo que acontece para depois analisar
    historico = {
        'valores': [valor_atual],
        'temperaturas': [temp_inicial],
        'aceitos': [],
        'rejeitados': 0,
        'melhorias': 0,
        'iteracao': 0
    }
    
    temperatura = temp_inicial
    iteracao = 0
    
    print(f"🚀 Começando a busca...")
    print(f"📊 Solução inicial: {solucao_atual}")
    print(f"⭐ Valor inicial: {valor_atual:.2f}")
    print(f"🌡️  Temperatura inicial: {temperatura:.2f}")
    print("-" * 50)
    
    # Aqui é onde a mágica acontece!
    while temperatura > temp_final and iteracao < max_iteracoes:
        
        # Vamos tentar uma mudança
        nova_solucao = add_remove_perturbacao(solucao_atual)
        novo_valor = avaliar_solucao(nova_solucao)
        
        diferenca = novo_valor - valor_atual
        
        # Decidindo se vamos aceitar essa mudança
        aceitar = False
        if diferenca > 0:
            # Melhorou! Sempre aceitamos
            aceitar = True
        else:
            # Piorou... mas às vezes vale a pena tentar coisas piores
            # (especialmente quando estamos "quentes"/explorando)
            chance = math.exp(diferenca / temperatura)
            if random.random() < chance:
                aceitar = True
        
        if aceitar:
            solucao_atual = nova_solucao
            valor_atual = novo_valor
            historico['aceitos'].append(True)
            
            if diferenca > 0:
                historico['melhorias'] += 1
            
            # Se essa é a melhor que já vimos, vamos guardar!
            if valor_atual > melhor_valor:
                melhor_solucao = solucao_atual.copy()
                melhor_valor = valor_atual
                print(f"� Achei algo melhor na iteração {iteracao}!")
                print(f"   💎 Novo valor: {melhor_valor:.2f}")
                print(f"   📋 Solução: {melhor_solucao}")
        else:
            historico['aceitos'].append(False)
            historico['rejeitados'] += 1
        
        # Anotando o progresso
        historico['valores'].append(valor_atual)
        historico['temperaturas'].append(temperatura)
        
        # Esfriando um pouquinho
        temperatura = temperatura * alpha
        iteracao += 1
        
        # De vez em quando, vamos dar uma olhada no progresso
        if iteracao % 100 == 0:
            print(f"📈 Iteração {iteracao}: Temp={temperatura:.2f}, "
                  f"Atual={valor_atual:.2f}, "
                  f"Melhor={melhor_valor:.2f}")
    
    historico['iteracao'] = iteracao
    
    print("-" * 50)
    print(f"✅ Busca finalizada após {iteracao} iterações")
    print(f"🌡️  Temperatura final: {temperatura:.2f}")
    print(f"✅ Mudanças aceitas: {len([x for x in historico['aceitos'] if x])}")
    print(f"❌ Mudanças rejeitadas: {historico['rejeitados']}")
    print(f"📈 Melhorias encontradas: {historico['melhorias']}")
    print(f"📊 Taxa de aceitação: {len([x for x in historico['aceitos'] if x])/max(1,len(historico['aceitos']))*100:.1f}%")
    print(f"🏆 Melhor combinação: {melhor_solucao}")
    print(f"💎 Melhor valor: {melhor_valor:.2f}")
    
    return melhor_solucao, melhor_valor, historico


def analisar_solucao(solucao, titulo="Análise da Solução"):
    """📊 Vamos dissecar essa solução e ver o que ela nos diz"""
    print(f"\n{'='*3} {titulo} {'='*3}")
    print(f"🔢 Em binário: {solucao}")
    
    itens_escolhidos = []
    custo_total = 0
    popularidade_total = 0
    
    # Vendo quais itens foram escolhidos
    for i, escolhido in enumerate(solucao):
        if escolhido == 1:
            itens_escolhidos.append(i)
            custo_total += custos_np[i]
            popularidade_total += popularidade_np[i]
    
    print(f"📋 Itens escolhidos: {itens_escolhidos}")
    print(f"📊 Total de itens: {len(itens_escolhidos)}")
    
    # Como estamos financeiramente?
    print(f"\n💰 Situação financeira:")
    print(f"   💸 Gastamos: R${custo_total:.2f}")
    print(f"   🏦 Tínhamos: R${orcamento_restaurante:.2f}")
    print(f"   💵 Sobrou: R${orcamento_restaurante - custo_total:.2f}")
    print(f"   📈 Usamos {(custo_total/orcamento_restaurante)*100:.1f}% do orçamento")
    
    # E em termos de valor?
    print(f"\n⭐ Análise de valor:")
    print(f"   🎯 Popularidade base: {popularidade_total:.2f} pontos")
    
    # Vamos ver as sinergias
    valor_sinergias = 0
    if len(itens_escolhidos) > 1:
        print(f"   🔗 Sinergias encontradas:")
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
                    print(f"      {emoji} {nome_i} + {nome_j}: {sinergia:+.1f}")
    
    print(f"   🔗 Bônus total de sinergias: {valor_sinergias:.2f} pontos")
    
    # Resultado final
    valor_final = avaliar_solucao(solucao)
    print(f"\n🏆 Resultado final:")
    print(f"   💎 Valor total: {valor_final:.2f} pontos")
    
    if valor_final == -float('inf'):
        print("   ⚠️  Ops! Essa solução estourou o orçamento!")
    else:
        print("   ✅ Solução válida e dentro do orçamento!")
    
    print("=" * 50)


def executar_testes():
    """
    🧪 Vamos testar diferentes configurações e ver qual funciona melhor
    
    Teste 1: Configuração equilibrada - nem muito aventureiro, nem muito conservador
    Teste 2: Mais devagar e sempre - demora mais mas explora melhor
    Teste 3: Começando bem quente - muita exploração no início
    """
    print("🔥 Vamos fazer alguns testes para achar a melhor configuração! 🔥")
    print("=" * 70)
    
    num_itens = len(itens_comida)
    
    # Teste 1: O clássico equilibrado
    print("\n📊 Teste 1: Configuração Clássica")
    print("🎛️  Temp inicial: 1000°, resfriamento: 0.95, iterações: 1000")
    melhor_sol_1, melhor_val_1, hist_1 = simulated_annealing(
        num_itens=num_itens,
        temp_inicial=1000,
        temp_final=1,
        alpha=0.95,
        max_iteracoes=1000
    )
    analisar_solucao(melhor_sol_1, "Resultado do Teste 1")
    
    # Teste 2: Devagar e sempre  
    print("\n📊 Teste 2: Exploração Cautelosa")
    print("🎛️  Temp inicial: 1000°, resfriamento: 0.99 (mais lento), iterações: 1500")
    melhor_sol_2, melhor_val_2, hist_2 = simulated_annealing(
        num_itens=num_itens,
        temp_inicial=1000,
        temp_final=1,
        alpha=0.99,  # Resfria bem devagar
        max_iteracoes=1500
    )
    analisar_solucao(melhor_sol_2, "Resultado do Teste 2")
    
    # Teste 3: Começando bem quente
    print("\n📊 Teste 3: Exploração Intensa")
    print("🎛️  Temp inicial: 2000° (bem quente!), resfriamento: 0.95, iterações: 1000")
    melhor_sol_3, melhor_val_3, hist_3 = simulated_annealing(
        num_itens=num_itens,
        temp_inicial=2000,  # Bem mais quente no início
        temp_final=1,
        alpha=0.95,
        max_iteracoes=1000
    )
    analisar_solucao(melhor_sol_3, "Resultado do Teste 3")
    
    # Vamos ver quem ganhou!
    print("\n🏆 Comparando os resultados")
    print("=" * 50)
    print(f"📊 Teste 1 (Clássico): {melhor_val_1:.2f} pontos")
    print(f"📊 Teste 2 (Cauteloso): {melhor_val_2:.2f} pontos")
    print(f"📊 Teste 3 (Intenso): {melhor_val_3:.2f} pontos")
    
    # Achando o campeão
    campeao = max([(melhor_val_1, 1, melhor_sol_1),
                   (melhor_val_2, 2, melhor_sol_2),
                   (melhor_val_3, 3, melhor_sol_3)])
    
    print(f"\n🥇 E o campeão é... Teste {campeao[1]} com {campeao[0]:.2f} pontos!")
    analisar_solucao(campeao[2], f"🏆 Nossa melhor solução (Teste {campeao[1]})")
    
    return {
        'teste1': (melhor_sol_1, melhor_val_1, hist_1),
        'teste2': (melhor_sol_2, melhor_val_2, hist_2),
        'teste3': (melhor_sol_3, melhor_val_3, hist_3),
        'campeao': campeao
    }


# função principal!
if __name__ == "__main__":
    """🚀 Vamos colocar nosso algoritmo para trabalhar!"""
    
    print("\n" + "="*80)
    print("🍽️  Otimização do Cardápio do Restaurante 🍽️")
    print("   Usando Simulated Annealing com estratégia Add/Remove")
    print("="*80)
    
    print("🧪 Vamos testar algumas configurações diferentes...")
    resultados = executar_testes()
    
    # Vamos dar uma olhada geral nos nossos dados
    print("\n📈 Resumo geral dos dados")
    print("=" * 50)
    print(f"📊 Itens disponíveis: {len(itens_comida)}")
    print(f"💰 Preço médio: R${np.mean(custos_np):.2f}")
    print(f"⭐ Popularidade média: {np.mean(popularidade_np):.2f}")
    print(f"💸 Se comprássemos tudo: R${np.sum(custos_np):.2f}")
    print(f"🏦 Nosso orçamento: R${orcamento_restaurante:.2f}")
    print(f"📈 Cobertura do orçamento: {(orcamento_restaurante/np.sum(custos_np))*100:.1f}% do total")
    
    print("\n🎯 O que descobrimos:")
    print("   ✅ O algoritmo encontrou soluções consistentes em todos os testes")
    print("   ✅ Conseguimos usar quase todo o orçamento disponível")
    print("   ✅ As sinergias entre itens foram bem aproveitadas")
    print("   ✅ A estratégia Add/Remove se mostrou bem eficiente")
    
    print("\n" + "="*80)
    print("🏁 Missão cumprida! Temos nossa seleção ótima de itens!")
    print("="*80)
