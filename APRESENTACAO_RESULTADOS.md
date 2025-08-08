# Mochila Quadrática com Simulated Annealing
## Apresentação dos Resultados e Metodologia

---

## Slide 1: Dados Usados para os Testes

### 📊 **Características da Instância de Teste**

- **Fonte dos Dados:** Arquivo Excel `Base de Dados.xlsx` com dados reais de cardápio
- **Número de Itens:** 20 produtos alimentícios
- **Orçamento Disponível:** R$ 100,00
- **Estrutura dos Dados:**
  - **Aba 'itens':** Nome, Custo (R$), Popularidade (1-10)
  - **Aba 'inter':** Matriz de sinergias 10x10 (expandida para 20x20)

### 🍽️ **Cardápio Completo Utilizado:**

| ID | Item | Custo (R$) | Popularidade |
|----|------|------------|--------------|
| 0 | Arroz (5kg) | 25.00 | 9.0 |
| 1 | Feijão (1kg) | 10.00 | 8.0 |
| 2 | Carne Moída (1kg) | 35.00 | 7.0 |
| 3 | Frango (1kg) | 20.00 | 8.0 |
| 4 | Ovos (dz) | 12.00 | 6.0 |
| 5 | Batata (1kg) | 8.00 | 8.0 |
| 6 | Cebola (1kg) | 5.00 | 5.0 |
| 7 | Alho (250g) | 7.00 | 5.0 |
| 8 | Macarrão (500g) | 6.00 | 7.0 |
| 9 | Molho de Tomate (grd) | 4.00 | 6.0 |
| 10 | Leite (1L) | 5.00 | 8.0 |
| 11 | Pão Francês (1kg) | 12.00 | 9.0 |
| 12 | Queijo Mussarela (kg) | 40.00 | 7.0 |
| 13 | Tomate (kg) | 8.00 | 7.0 |
| 14 | Batata (kg) | 6.00 | 8.0 |
| 15 | Cebola (kg) | 5.00 | 6.0 |
| 16 | Açúcar (1kg) | 4.00 | 9.0 |
| 17 | Café (500g) | 15.00 | 8.0 |
| 18 | Macarrão (500g) | 6.00 | 8.0 |
| 19 | Manteiga (200g) | 9.00 | 7.0 |

### 📈 **Estatísticas dos Dados:**
- **Custo médio:** R$ 12.10 ± 10.02
- **Popularidade média:** 7.30 ± 1.19
- **Taxa de cobertura orçamentária:** 41.3%
- **Densidade da matriz de sinergias:** 8.5%

---

## Slide 2: Representação Gráfica da Estrutura de Dados

### 🗂️ **Estrutura de uma Solução**

```
Solução = [x₀, x₁, x₂, ..., x₁₉]
```

**Onde cada xᵢ ∈ {0, 1}:**
- **0:** Item não selecionado
- **1:** Item selecionado

### 📋 **Exemplo Visual:**

```
Índices:  [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19]
Solução:  [ 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1]
Items:    [🍚,❌,🥩,🍗,❌,🥔,🧅,🧄,🍝,🍅,❌,❌,❌,❌,🥔,❌,🍯,❌,🍝,🧈]
```

### 💻 **Definição em Código Python:**

```python
# Estrutura básica da solução
solucao = [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1]

# Arrays auxiliares (indexados pela posição)
custos_np = np.array([25.0, 10.0, 35.0, 20.0, ...])      # Custos dos itens
popularidade_np = np.array([9.0, 8.0, 7.0, 8.0, ...])   # Popularidades
matriz_interacao_np = np.array([[0, 5, 10, ...], ...])   # Matriz 20x20 de sinergias

# Função para extrair itens selecionados
itens_selecionados = [i for i, x in enumerate(solucao) if x == 1]
```

---

## Slide 3: Explicação do Cálculo do Valor da Solução

### 🎯 **Função Objetivo - Mochila Quadrática**

A função avalia a qualidade de uma solução considerando dois componentes:

#### **1️⃣ Termo Linear (Popularidades):**
```
Valor_Linear = Σ (popularidade_i × x_i)
```
- Soma as popularidades dos itens selecionados
- Representa o valor individual de cada item

#### **2️⃣ Termo Quadrático (Sinergias):**
```
Valor_Quadrático = ΣΣ (sinergia_ij × x_i × x_j)
```
- Soma as sinergias entre todos os pares de itens selecionados
- Representa interações benéficas/prejudiciais entre itens

#### **3️⃣ Restrição Orçamentária:**
```
Σ (custo_i × x_i) ≤ Orçamento
```

### 🏆 **Função Objetivo Final:**
```
Maximizar: f(x) = Σ(popularidade_i × x_i) + ΣΣ(sinergia_ij × x_i × x_j)
Sujeito a: Σ(custo_i × x_i) ≤ 100.00
```

**Retorna:** `-∞` se inviável, senão `Valor_Linear + Valor_Quadrático`

---

## Slide 4: Código da Função de Avaliação

```python
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
```

---

## Slide 5: Explicação da Meta-heurística Simulated Annealing

### 🔥 **Componentes do Algoritmo:**

#### **1️⃣ Inicialização:**
- Gera solução inicial aleatória
- Garante viabilidade (tentativas até encontrar solução válida)
- Define temperatura inicial e parâmetros de controle

#### **2️⃣ Loop Principal:**
```python
while temperatura > temp_final and iteracao < max_iteracoes:
    # Gera vizinho com operador Add/Remove
    nova_solucao = add_remove_perturbacao(solucao_atual)
    
    # Critério de aceitação de Metropolis
    if novo_valor > valor_atual:  # Melhoria
        aceitar = True
    else:  # Piora
        probabilidade = exp(diferenca / temperatura)
        aceitar = (random() < probabilidade)
    
    # Resfriamento geométrico
    temperatura = temperatura * alpha
```

#### **3️⃣ Heurística Add/Remove:**
- **Estado vazio:** ADICIONA item aleatório
- **Estado cheio:** REMOVE item aleatório  
- **Estado misto:** 50% ADICIONAR, 50% REMOVER

#### **4️⃣ Parâmetros de Controle:**
- **Temperatura inicial:** Controla exploration vs exploitation
- **Taxa de resfriamento (α):** Velocidade de convergência
- **Critério de parada:** Temperatura mínima ou máximo de iterações

---

## Slide 6: Resultados dos Testes do Código

### 🧪 **EXPERIMENTAÇÃO COMPUTACIONAL**

Foram realizados **3 experimentos** com diferentes configurações de parâmetros:

---

### **📊 EXPERIMENTO 1: Configuração Clássica**
**Parâmetros:** T₀=1000, α=0.95, max_iter=1000

#### **Resultados:**
- **🏆 Valor final:** 86.00 pontos
- **⏱️ Iterações:** 135 iterações
- **📈 Taxa de aceitação:** 61.5%
- **💰 Custo:** R$ 99.00 / R$ 100.00 (99.0%)

#### **Solução Encontrada:**
- **Items selecionados:** [0, 2, 3, 6, 8, 9, 16] (7 itens)
- **Composição:** Arroz, Carne Moída, Frango, Cebola, Macarrão, Molho, Açúcar
- **Valor linear:** 51.00 pontos
- **Sinergias:** +35.00 pontos

---

### **📊 EXPERIMENTO 2: Resfriamento Cauteloso**
**Parâmetros:** T₀=1000, α=0.99, max_iter=1500

#### **Resultados:**
- **🥇 Valor final:** 180.00 pontos ⭐ **MELHOR RESULTADO**
- **⏱️ Iterações:** 688 iterações
- **📈 Taxa de aceitação:** 49.0%
- **💰 Custo:** R$ 100.00 / R$ 100.00 (100.0%)

#### **Solução Encontrada:**
- **Items selecionados:** [0, 3, 5, 6, 7, 8, 9, 14, 16, 18, 19] (11 itens)
- **Composição:** Arroz, Frango, Batata, Cebola, Alho, Macarrão, Molho, Batata, Açúcar, Macarrão, Manteiga
- **Valor linear:** 80.00 pontos
- **Sinergias:** +100.00 pontos

#### **Principais Sinergias Identificadas:**
- 🔥 Arroz + Frango: +10.0
- 🔥 Frango + Batata: +15.0
- 🔥 Cebola + Alho: +20.0
- 🔥 Macarrão + Molho: +15.0

---

### **📊 EXPERIMENTO 3: Exploração Intensiva**
**Parâmetros:** T₀=2000, α=0.95, max_iter=1000

#### **Resultados:**
- **🏆 Valor final:** 109.00 pontos
- **⏱️ Iterações:** 149 iterações
- **📈 Taxa de aceitação:** 59.1%
- **💰 Custo:** R$ 98.00 / R$ 100.00 (98.0%)

#### **Solução Encontrada:**
- **Items selecionados:** [2, 5, 7, 10, 13, 14, 15, 17, 19] (9 itens)
- **Composição:** Carne Moída, Batata, Alho, Leite, Tomate, Batata, Cebola, Café, Manteiga
- **Valor linear:** 64.00 pontos
- **Sinergias:** +45.00 pontos

---

### **🏆 ANÁLISE COMPARATIVA FINAL**

| Experimento | Configuração | Valor Final | Iterações | Taxa Aceitação | Uso Orçamento |
|-------------|--------------|-------------|-----------|----------------|---------------|
| **1 - Clássico** | T₀=1000, α=0.95 | 86.00 | 135 | 61.5% | 99.0% |
| **2 - Cauteloso** | T₀=1000, α=0.99 | **180.00** ⭐ | 688 | 49.0% | 100.0% |
| **3 - Intensivo** | T₀=2000, α=0.95 | 109.00 | 149 | 59.1% | 98.0% |

### **🥇 SOLUÇÃO ÓTIMA ENCONTRADA - EXPERIMENTO 2**

#### **📋 Cardápio Otimizado:**
1. **Arroz (5kg)** - R$ 25.00 (⭐9.0)
2. **Frango (1kg)** - R$ 20.00 (⭐8.0)
3. **Batata (1kg)** - R$ 8.00 (⭐8.0)
4. **Cebola (1kg)** - R$ 5.00 (⭐5.0)
5. **Alho (250g)** - R$ 7.00 (⭐5.0)
6. **Macarrão (500g)** - R$ 6.00 (⭐7.0)
7. **Molho de Tomate** - R$ 4.00 (⭐6.0)
8. **Batata (kg)** - R$ 6.00 (⭐8.0)
9. **Açúcar (1kg)** - R$ 4.00 (⭐9.0)
10. **Macarrão (500g)** - R$ 6.00 (⭐8.0)
11. **Manteiga (200g)** - R$ 9.00 (⭐7.0)

#### **💡 Insights dos Resultados:**
- **Resfriamento mais lento** (α=0.99) permitiu melhor exploração
- **Sinergias** representaram 55.6% do valor total (100/180)
- **Utilização completa** do orçamento maximizou eficiência
- **Combinações inteligentes:** Ingredientes complementares (temperos + carnes + carboidratos)

#### **🔬 CONCLUSÕES METODOLÓGICAS:**
- ✅ **Algoritmo eficaz:** SA encontrou soluções de alta qualidade
- ✅ **Heurística robusta:** Add/Remove explorou bem o espaço de soluções
- ✅ **Parâmetros críticos:** Taxa de resfriamento impacta significativamente a qualidade
- ✅ **Problema realista:** Sinergias entre alimentos refletem combinações culinárias reais
