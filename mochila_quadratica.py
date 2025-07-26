import random
import math
import numpy as np
import gspread

from dotenv import load_dotenv
import os

# Carregando variáveis de arquivo .env no ambiente do sistema
load_dotenv()

# --- CONFIGURAÇÃO DA PLANILHA ---
PLANILHA_ID = os.getenv('PLANILHA_ID_REAL')
ARQUIVO_CREDENCIAS = 'credenciais.json'

# --- DADOS DO PROBLEMA DE COMIDA E ORÇAMENTO ---

# 1. Autenticar com o Google Sheets
try:
    gc = gspread.service_account(filename=ARQUIVO_CREDENCIAS)
    print("Autenticação com Google Sheets bem-sucedida!")
except Exception as e:
    print(f"Erro ao autenticar com Google Sheets: {e}")
    print("Verifique se 'credenciais.json' está na pasta correta e "
          "se a API foi configurada no Google Cloud.")
    exit()

# 2. Verificar se a PLANILHA_ID foi carregada corretamente e abrir a planilha
if PLANILHA_ID is None:
    print("Erro: A variável 'PLANILHA_ID_REAL' não"
          "foi encontrada no arquivo .env "
          "ou no ambiente.")
    print("Certifique-se que você criou o arquivo .env e definiu "
          "PLANILHA_ID_REAL=SUA_ID_DA_PLANILHA_AQUI.")
    exit()

try:
    planilha = gc.open_by_key(PLANILHA_ID)
    print(f"Planilha '{planilha.title}' aberta com sucesso!")
except Exception as e:
    print(f"Erro ao abrir a planilha: {e}")
    print("Verifique se a ID da planilha está correta"
          "no código e se a planilha foi "
          "compartilhada com o e-mail da conta de serviço.")
    exit()

# --- INÍCIO DAS MODIFICAÇÕES PARA LER A POPULARIDADE ---

# 3. Ler a aba 'itens' para criar a lista de dicionários e arrays NumPy
try:
    aba_itens = planilha.worksheet('itens')
    print("Aba 'itens' selecionada com sucesso!")

    registros_itens = aba_itens.get_all_records()
    print(f"Total de {len(registros_itens)} registros lidos da aba 'itens'.")

    itens_comida = []
    custos_np = np.array([float(record['Custo (R$)']) 
                          for record in registros_itens])
    popularidade_np = np.array([float(record['Popularidade']) 
                                for record in registros_itens])

    for record in registros_itens:
        itens_comida.append({
            "nome": record['Nome'],
            "custo": float(record['Custo (R$)']),
            "popularidade": float(record['Popularidade'])
        })
    print("Arrays NumPy 'custos_np' e 'popularidade_np' criados.")

except Exception as e:
    print(f"Erro ao ler a aba 'itens': {e}")
    print("Verifique se a aba 'itens' existe na sua planilha"
          "e se os cabeçalhos das "
          "colunas (ID Item, Nome, Custo (R$),"
          "Popularidade) estão EXATAMENTE iguais, "
          "incluindo maiúsculas/minúsculas e espaços.")
    exit()

# --- FIM DAS MODIFICAÇÕES PARA LER A POPULARIDADE ---

# 4. Ler a aba 'inter' para criar a matriz de interação NumPy
try:
    aba_inter = planilha.worksheet('inter')
    print("Aba 'inter' selecionada com sucesso!")

    dados_inter = aba_inter.get_all_values()
    print(f"Total de {len(dados_inter)} linhas (incluindo cabeçalhos) "
          "lidas da aba 'inter'.")

    matriz_interacao_np = np.array([row[1:] for row in dados_inter[1:]],
                                   dtype=float)
    print("Matriz de interação NumPy 'matriz_interacao_np' criada.")

except Exception as e:
    print(f"Erro ao ler a aba 'inter': {e}")
    print("Verifique se a aba 'inter' existe"
          "na sua planilha e se a estrutura da "
          "matriz está correta (IDs de linha e" 
          "cabeçalhos de coluna corretos, e todos "
          "os valores são numéricos).")
    exit()

# 5. Definir a Capacidade da "Mochila" (Orçamento do Restaurante)
orcamento_restaurante = 100.0
print(f"Orçamento do Restaurante definido: R${orcamento_restaurante:.2f}")

# --- IMPRIMIR TODOS OS DADOS CARREGADOS PARA VERIFICAÇÃO FINAL ---
print("\n--- Todos os Dados do Problema"
      "(Restaurante) Carregados da Planilha ---")
print(f"Total de itens disponíveis: {len(itens_comida)}")
print(f"Orçamento do Restaurante: R${orcamento_restaurante:.2f}\n")

print("Detalhes dos Itens de Comida:")
for i, item in enumerate(itens_comida):
    print(f"  Item {i}: {item['nome']} (Custo: R${item['custo']:.2f}, "
          f"Popularidade: {item['popularidade']:.1f})")

print("\nCustos dos itens (NumPy Array):")
print(custos_np)

print("\nPopularidade dos itens (NumPy Array):")
print(popularidade_np)

print("\nMatriz de Interação (NumPy Array - Bônus/Penalidades):")
print(matriz_interacao_np)

# --- FIM DA CARGA DE DADOS. O PRÓXIMO PASSO SERÁ A FUNÇÃO DE CÁLCULO --


def avaliar_solucao(solucao):
    # variavel pra acumulador do valor total da solução
    # como se fosse um medidor de popularidade iniciado em 0
    valorTotal = 0.0
    
    # variavel para o peso total da solução
    #  como se fosse um contador de gastos
    pesoTotal = 0.0
    
    # pega o numero de itens da solução
    # qtde de itens disponiveis para escolher
    numItens = len(solucao)

    #  iterando sobre cada item disponivel
    for each in range(numItens):
        
        # verifica se o item "each" está incluído na solução atual
        if solucao[each] == 1:
            
            # se o item tiver na mochila
            # add sua popularidade individual 
            # (que tá no array 'popularidade_np')
            # ao valorTotal
            
            valorTotal += popularidade_np[each]
            
            # e add o custo(está no 'custos_np') ao pesoTotal
            pesoTotal += custos_np[each]
            
    # Cálculo da parte quadrática(interações)
    # dois loops para percorrer todos os pares de itens
    # loop i e j 
    
    # Primeiro loop 
    for i in range(numItens):
        
        # item pode interagir com outros se tiver na mochila
        if solucao[i] == 1:
            for j in range(i + 1, numItens):
                # se j tbm está  entao i e j existem como par
                if solucao[j] == 1:
                    # se ambos tem,adiciona o valor de interação
                    valorTotal += matriz_interacao_np[i][j]
            
    if pesoTotal > orcamento_restaurante:
        # se o peso for maior que o orçamento,é inviavel
        return - float('inf')
    else:
        # se for valida o peso ta dentro do orçamento
        return valorTotal    
    
