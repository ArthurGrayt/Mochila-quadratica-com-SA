import random  # módulo 'random', que permite embaralhar listas aleatoriamente


def mochila(valores, pesos_itens, capacidade, ordem_itens):
    valor_total = 0  # valor total acumulado da mochila com 0
    peso_total = 0   # peso total acumulado da mochila com 0
    itens_mochila = []  # lista para guardar os itens que foram escolhidos
    for i in ordem_itens:
        if peso_total + pesos_itens[i] <= capacidade:
            peso_total += pesos_itens[i]  # Add o peso do item ao peso total
            valor_total += valores[i]   # Add o valor do item ao valor total
            itens_mochila.append(i)  # add no fim da lista itens_mochila
    return valor_total, peso_total, itens_mochila  # retornando resultados


valores = [60, 100, 120, 80, 20]  # Lista com os valores dos itens
pesos_itens = [40, 30, 80, 40, 50]  # Lista com os pesos dos itens
capacidade = 120  # Capacidade máxima da mochila

# Criamos uma lista de eficiência para cada item,
# onde: eficiência = (valor / peso)
eficiencia_itens = [valor / peso for valor, peso in zip(valores, pesos_itens)]

# Criamos uma lista com os índices dos itens
# e ordenamos pela eficiência do maior para o menor
indices_itens = sorted(range(len(valores)),
                       key=lambda i: eficiencia_itens[i], reverse=True)

# Teste com ordem baseada em eficiência
valor, peso, itens = mochila(valores, pesos_itens, capacidade, indices_itens)
print("Resultado com eficiência:")
print("Valor total:", valor)
print("Peso total:", peso)
print("Itens na mochila:", itens)

valor_melhor = 0  # variavel pra guardar o melhor valor até agora
melhor_solucao = 0  # variavel pra guardar a melhor solução até agora
tentativas = 1000  # vezes que vamos tentar solucionar

# Loop para tentar 1000 vezes
for _ in range(tentativas):
    ordem_random = list(range(len(valores)))  # Embaralhamos os itens
    random.shuffle(ordem_random)  # Embaralha a ordem dos itens
    valor, peso, itens = mochila(valores, pesos_itens,
                                 capacidade, ordem_random)
    if valor > valor_melhor:
        valor_melhor = valor  # se for melhor, atualiza o valor
        melhor_solucao = (valor, peso, itens)  # atualiza a melhor solução

# Mostrando a melhor solução encontrada apos as 1000 tentativas
print("\nMelhor solução encontrada (Multistart):")
print("Valor total:", melhor_solucao[0])
print("Peso total:", melhor_solucao[1])
print("Itens na mochila:")
for item in melhor_solucao[2]:
    print(f"Item {item}: Valor = {valores[item]}, Peso = {pesos_itens[item]}")
print("Total de itens escolhidos:", len(melhor_solucao[2]))
