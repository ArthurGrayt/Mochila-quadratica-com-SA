# 🎯 GUIA DE CONFIGURAÇÃO RÁPIDA - ADD/REMOVE

## ⚡ Setup em 3 Passos

### 1️⃣ **Instalar Dependências**
```bash
pip install numpy gspread python-dotenv
```

### 2️⃣ **Configurar Google Sheets API**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie projeto e ative Google Sheets API
3. Crie conta de serviço e baixe `credencias.json`
4. Copie arquivo para a pasta do projeto

### 3️⃣ **Configurar Ambiente**
```bash
# Copie o template
cp .env.exemplo .env

# Edite .env e adicione sua PLANILHA_ID
PLANILHA_ID_REAL=1A2B3C4D5E6F7G8H9I0J...
```

## 🏃‍♂️ Executar
```bash
python mochila_quadratica.py
```

## ➕➖ **Novidade: Operador Add/Remove**

Este projeto utiliza um operador de perturbação **inteligente** que:
- ✅ **Adiciona** itens quando há espaço disponível
- ✅ **Remove** itens quando necessário
- ✅ **Adapta-se** ao estado atual da solução
- ✅ **Evita** soluções extremas (vazia ou completa)

**Diferencial**: Mais eficiente que o tradicional swap/flip-bit!

## 📊 **Estrutura da Planilha Google Sheets**

### Aba "itens"
```
| ID Item | Nome                | Custo (R$) | Popularidade |
|---------|--------------------|-----------  |-------------|
| 0       | Item 1             | 25.00      | 9.0          |
| 1       | Item 2             | 10.00      | 8.0          |
```

### Aba "inter"
```
|        | Item0 | Item1 | Item2 |
|--------|-------|-------|-------|
| Item0  |  0.0  | 30.0  |  0.0  |
| Item1  | 30.0  |  0.0  | -8.0  |
| Item2  |  0.0  | -8.0  |  0.0  |
```

## ✅ **Pronto!**
O algoritmo irá executar 3 testes com o novo operador Add/Remove e encontrar a solução ótima.

---
**📝 Para documentação completa, veja `README.md`**
