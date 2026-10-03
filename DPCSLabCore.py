import networkx as nx
import pandas as pd
from typing import Callable

'''
Реплікація кластеру
Повертає граф H, що містить n незв'язаних копій кластеру G
Може використовувати як аргумент або параметр n (число кластерів) або seq (послідовність унікальних міток для кластерів). Пріопитет - за seq.
Намагається зберігти всі параметри ребер.
Результуючий граф має нумерацію виду (p, q), де p - номер/мітка кластеру, q - мітка вершини у кластері.
'''
def replicate(G: nx.Graph, n:int = 1, seq:dict = None) -> nx.Graph:
    if n<=1 and seq == None: return G # обробка неприпустимих значень
        
    H = nx.Graph() # створення порожнього результуючого графу
    edges_data = {e: G.get_edge_data(*e) for e in G.edges} # отримання характеристик ребер кластеру
    
    if seq == None:
        seq = [i for i in range(n)] # якщо ми використовуємо n - створюємо послідовність штучно
        
    for p in seq:                                  # для кожного p-го кластеру...
        map = {q: (p, q) for q in G.nodes}         # задаємо мапу нумерації (в нашому випадку це подвійна нумерація)
        g = nx.relabel_nodes(G, map, copy=True)    # створюємо проміжний кластер g, в якому використовується нова нумерація. Оригінальний G не чіпаємо!
        H.update(nodes = g.nodes, edges = g.edges) # додаємо цей проміжний кластер до результуючого графу. За рахунок перейменування всі мітки унікальні.
        for e in edges_data: # копіюємо дані ребер
            H.get_edge_data((p, e[0]), (p, e[1])).update(edges_data[*e]) 
            
    return H 

'''
Побудова графа з нуля
Зручно використовувати, коли ваш граф простіше створити "з нуля", ніж масштабувати попередню версію
'''
def build(cluster: nx.Graph, rank: int) -> nx.Graph:
    if rank<=0: return nx.Graph()      # некоректний ранг повертає порожній граф
    if rank==1: return cluster         # ранг 1 - це сам кластер
    return None

'''
Побудова графа на основі попереднього кроку
Зручно використовувати, коли ваш граф краще масштабувати з попередної версії, ніж генерувати з нуля
'''
def scale(cluster: nx.Graph, G_previous: nx.Graph) -> nx.Graph:
    return None

'''
Вимірювання топологічних характеристик конкретного графа
'''
def characteristics(G: nx.Graph) -> dict:
    N = G.number_of_nodes()                        # число вершин
    E = G.number_of_edges()                        # число ребер
    degs = G.degree()                              # власні ступені вершин у форматі (node, value)
    s_vals = [s[1] for s in degs]                  # значення власних ступенів
    S = max(s_vals)                                # ступінь - максимум властих ступенів
    D = nx.diameter(G)                             # діаметр
    D_average = nx.average_shortest_path_length(G) # середній діаметр
    Q = N*D_average/E                              # топологічний трафік (версія для довільних графів)
    C = N*D*S                                      # вартість (версія з урахуванням діаметру)
    return {'N':N, 'E':E, 'Ступінь':S, 'Діаметр':D, 'Середній діаметр': D_average, 'Топологічний трафік':Q, 'Вартість':C, 'Graph': G.copy()}


'''
Робимо аналіз і збираємо наш результат в DataFrame
'''
def build_table(cluster: nx.Graph, 
                Nmax: int = 1000, 
                ranks: list = None,    # якщо нас цікавлять конкретні ранги масштабування - нам сюди
                rank_step: int = 1,    #
                builder:Callable[[nx.Graph, int], nx.Graph] = None,     # функція для побудови графу
                scaler:Callable[[nx.Graph, nx.Graph], nx.Graph] = None   # функція для масштабування графу
               ) -> pd.DataFrame:
    if Nmax<=0: Nmax = 1000
    if builder==None and scaler==None: raise Exception('Неможливо виконувати побудову таблиці без функції для побудови чи масштабування топології!')
    
    frame = pd.DataFrame(columns = ['N', 'E', 'Ступінь', 'Діаметр', 'Середній діаметр', 'Топологічний трафік', 'Вартість', 'Graph'])
    
    G = cluster.copy()    # перший ранг - це сам кластер
    rank = 1              # оскільки ми йдемо по Nmax - ітеруватись по рангам ми не можемо, тому маємо відслідковувати їх окремо

    while G.number_of_nodes() < Nmax:
        chars = characteristics(G)                               # вимірюємо характеристики
        frame.loc[rank] = chars                                  # додаємо дані в датафрейм (обережно! Ключі колонок мають співпадати)
        rank = ranks.pop(0) if ranks != None else rank+rank_step # дізнаємось черговий ранг, який ми маємо згенерувати
        G = builder(cluster, rank+1) if builder!=None else scaler(cluster, G) # генеруємо граф потрібного нам рангу

    return frame
