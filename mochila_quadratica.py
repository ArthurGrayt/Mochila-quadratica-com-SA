import random
import math
import numpy as np
import pandas as pd
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
    print("Verifique se 'credenciais.json' está na pasta correta "
          "e se a API foi configurada no Google Cloud.")
    exit()

# 2. Verificar se a PLANILHA_ID foi carregada corretamente e abrir a planilha
if PLANILHA_ID is None:
    print(
        ("Erro: A variável 'PLANILHA_ID_REAL' não foi "
         "encontrada no arquivo .env "
         "ou no ambiente.")
    )
    print(
        "Certifique-se que você criou o arquivo .env e definiu "
        "PLANILHA_ID_REAL=SUA_ID_DA_PLANILHA_AQUI."
    )
    exit()

try:
    planilha = gc.open_by_key(PLANILHA_ID)
    print(f"Planilha '{planilha.title}' aberta com sucesso!")
except Exception as e:
    print(f"Erro ao abrir a planilha: {e}")
    print("Verifique se a ID da planilha está correta no código e "
          "se a planilha foi compartilhada com o e-mail da conta de serviço.")
    exit()

# 3. Ler a aba 'itens' para criar a lista de dicionários e arrays NumPy
try:
    aba_itens = planilha.worksheet('itens')
    print("Aba 'itens' selecionada com sucesso!")

    registros_itens = aba_itens.get_all_records()
    print(f"Total de {len(registros_itens)} registros lidos da aba 'itens'.")

    itens_comida = []
    for record in registros_itens:
        itens_comida.append({
            "nome": record['Nome'],
            "peso": float(record['Peso (kg/porção)']),
            "valor_linear": float(record['Custo (R$)'])
        })
    print("Estrutura 'itens_comida' criada.")

    pesos_np = np.array([item["peso"] for item in itens_comida])
    custos_np = np.array([item["valor_linear"] for item in itens_comida])
    
    print("Arrays NumPy 'pesos_np' e 'custos_np' criados.")

except Exception as e:
    print(f"Erro ao ler a aba 'itens': {e}")
    print("Verifique se a aba 'itens' existe na sua planilha e se os "
          "cabeçalhos das colunas "
          "(ID Item, Nome, Peso (kg/porção), Custo (R$)) "
          "estão EXATAMENTE iguais, incluindo "
          "maiúsculas/minúsculas e espaços.")
    exit()

# 4. Ler a aba 'interacoes' para criar a matriz de interação NumPy
try:
    aba_interacoes = planilha.worksheet('inter')
    print("Aba 'interacoes' selecionada com sucesso!")

    dados_interacoes = aba_interacoes.get_all_values()
    print(f"Total de {len(dados_interacoes)} linhas (incluindo cabeçalhos) "
          f"lidas da aba 'interacoes'.")

    # [row[1:] for row in dados_interacoes[1:]] -> Ignora a primeira linha e
    # a primeira coluna da matriz de interação da planilha.
    matriz_interacao_np = np.array(
        [row[1:] for row in dados_interacoes[1:]], dtype=float
    )
    print("Matriz de interação NumPy 'matriz_interacao_np' criada.")

except Exception as e:
    print(f"Erro ao ler a aba 'interacoes': {e}")
    print("Verifique se a aba 'interacoes' existe na sua planilha e se a "
          "estrutura da matriz está correta (IDs de linha e cabeçalhos "
          "de coluna corretos, e todos os valores são numéricos).")
    exit()

# 5. Definir a Capacidade da "Mochila" (Orçamento do Restaurante)
orcamento_restaurante = 100.0
print(f"Orçamento do Restaurante definido: R${orcamento_restaurante:.2f}")


# --- IMPRIMIR TODOS OS DADOS CARREGADOS PARA VERIFICAÇÃO FINAL ---
print("\n--- Todos os Dados do Problema (Restaurante) "
      "Carregados da Planilha ---")
print(f"Total de itens disponíveis: {len(itens_comida)}")
print(f"Orçamento do Restaurante: R${orcamento_restaurante:.2f}\n")

print("Detalhes dos Itens de Comida:")
for i, item in enumerate(itens_comida):
    print(f"  Item {i}: {item['nome']} (Custo: R${item['valor_linear']:.2f}, "
          f"Peso/Porção: {item['peso']}kg)")

print("\nCustos dos itens (NumPy Array):")
print(custos_np)

print("\nPesos dos itens (NumPy Array):")
print(pesos_np)

print("\nMatriz de Interação (NumPy Array - Bônus/Penalidades):")
print(matriz_interacao_np)

# --- FIM DA CARGA DE DADOS. O PRÓXIMO PASSO SERÁ A FUNÇÃO DE CÁLCULO ---