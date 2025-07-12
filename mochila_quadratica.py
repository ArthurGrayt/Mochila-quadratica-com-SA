# import random 
# import math   
# import numpy as np
# import pandas as pd
from dotenv import load_dotenv 
import os 
import gspread

# Carregando variavéis de arquivo .env no ambiente do sistema
load_dotenv()

# Config da Planilha

PLANILHA_ID = os.getenv('PLANILHA_ID_REAL')
ARQUIVO_CREDENCIAIS = 'credenciais.json'

# Autenticando a planilha com o Google Sheets

try:
    
    gc = gspread.service_account(filename=ARQUIVO_CREDENCIAIS)
    print("Autentificação com Google Sheets foi um sucesso!")

except Exception as e:
    print(f"Erro ao autenticar com Google Sheets:{e}")
    print("Verifique se as credenciais estão na pasta correta")
    print("e a configuração da api")
    exit()

if PLANILHA_ID is None:
    print(
        (
            "Erro: A variável 'PLANILHA_ID_REAL' não foi "
            "encontrada no arquivo .env "
            "ou no ambiente."
        )
    )
    print(
        "Certifique-se que você criou o arquivo .env e definiu "
        "PLANILHA_ID_REAL=SUA_ID_DA_PLANILHA_AQUI."
    )
    exit()
    
try:
    planilha = gc.open_by_key(PLANILHA_ID)
    
    print(f"Planilha '{planilha.title}'aberta com sucesso!")
except Exception as e:
    print(f"Erro ao abrir a planilha: {e}")
    print("Verifique se o ID da planilha está correto")
    