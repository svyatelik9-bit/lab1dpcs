import math
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import DPCSLabCore as core

# 1. Функція побудови масштабованої топології

def build(cluster: nx.Graph, rank: int) -> nx.Graph:
    if rank <= 0:
        return nx.Graph()
    if rank == 1:
        return cluster.copy()

    G = core.replicate(cluster, n=rank)

    # ========================================================
    # РЕГУЛЯРНІ ЗВ'ЯЗКИ
    # Кожен кластер з'єднується з наступним.
    # Останній кластер з'єднується з першим -> кільце.
    # ========================================================
    regular_pairs = [
        (1, 1),
        (3, 3),
        (6, 6),
        (8, 8),
    ]

    for p in range(rank):
        next_p = (p + 1) % rank
        # Для неорієнтованого графа при rank=2 достатньо одного напрямку.
        if rank == 2 and p == 1:
            continue

        for v1, v2 in regular_pairs:
            G.add_edge((p, v1), (next_p, v2))

    # ========================================================
    # НЕРЕГУЛЯРНІ ЗВ'ЯЗКИ
    # ========================================================
    irregular_rules = [
        # червоні пунктирні: 7 -> 7 через 2 кластери
        (7, 7, 2),
        # зелені пунктирні: 4 -> 5 через 2 кластери
        (4, 5, 2),
        # жовті пунктирні: 2 -> 2 через 3 кластери
        (2, 2, 3),
        # бірюзові пунктирні: 5 -> 4 через 3 кластери
        (5, 4, 3),
    ]

    for v1, v2, step in irregular_rules:
        if rank <= step:
            continue

        for p in range(rank):
            next_p = (p + step) % rank
            if p != next_p:
                G.add_edge((p, v1), (next_p, v2))

    return G


# 2. Базовий кластер №23
# Точна структура з наданого рисунка: 8 вершин, 10 внутрішніх ребер.

cluster = nx.Graph()
cluster.add_nodes_from(range(1, 9))
cluster.add_edges_from([
    (1, 2),
    (2, 3),
    (1, 4),
    (4, 6),
    (3, 5),
    (5, 8),
    (2, 4),
    (2, 5),
    (4, 7),
    (7, 5),
])

print('Кластер №23')
print('Вершин:', cluster.number_of_nodes())
print('Внутрішніх ребер:', cluster.number_of_edges())
print('Ребра:', sorted(cluster.edges()))


# 3. Розрахунок характеристик одного кроку

def calculate_step(cluster: nx.Graph, rank: int) -> dict:
    G = build(cluster, rank)
    ch = core.characteristics(G)

    return {
        'Крок': rank,
        'N': ch['N'],
        'E': ch['E'],
        'Ступінь': ch['Ступінь'],
        'Діаметр': ch['Діаметр'],
        'Середній діаметр': ch['Середній діаметр'],
        'Топологічний трафік': ch['Топологічний трафік'],
        'Вартість': ch['Вартість'],
    }


# 4. Побудова таблиці для ВСІХ кроків від 1 до введеного значення

def build_table(cluster: nx.Graph, num_steps: int) -> pd.DataFrame:
    rows = []

    for rank in range(1, num_steps + 1):
        print(f'Обчислення кроку {rank}/{num_steps}...')
        rows.append(calculate_step(cluster, rank))

    return pd.DataFrame(rows).set_index('Крок')


# 5. Розташування вершин базового кластера

cluster_pos = {
    1: (-2, 2),
    2: (0, 2),
    3: (2, 2),
    4: (-2, 0),
    5: (2, 0),
    6: (-2, -2),
    7: (0, -2),
    8: (2, -2),
}


def visualize_cluster():
    # Візуалізація базового кластера №23
    plt.figure(figsize=(8, 8))

    nx.draw_networkx_edges(
        cluster,
        cluster_pos,
        edge_color='black',
        width=2,
    )

    nx.draw_networkx_nodes(
        cluster,
        cluster_pos,
        node_size=950,
        node_color='white',
        edgecolors='black',
        linewidths=2,
    )

    nx.draw_networkx_labels(
        cluster,
        cluster_pos,
        font_size=18,
        font_weight='bold',
    )

    plt.title('Кластер №23')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def visualize_graph(num_clusters=6):
    G = build(cluster, num_clusters)

    # Для великих систем автоматично збільшуємо радіус.
    if num_clusters <= 6:
        radius = 24
    elif num_clusters <= 10:
        radius = 30
    elif num_clusters <= 17:
        radius = 38
    else:
        radius = 45

    pos = {}

    for c in range(num_clusters):
        angle = 2 * math.pi * c / num_clusters
        cx = radius * math.cos(angle)
        cy = radius * math.sin(angle)
        for v, (dx, dy) in cluster_pos.items():
            pos[(c, v)] = (cx + dx, cy + dy)

    plt.figure(figsize=(18, 18))

    # Внутрішні ребра кластера.
    internal_edges = []
    for c in range(num_clusters):
        internal_edges.extend([((c, u), (c, v)) for u, v in cluster.edges()])

    nx.draw_networkx_edges(
        G, pos,
        edgelist=internal_edges,
        edge_color='black',
        width=1.2,
    )

    # Регулярні зв'язки.
    regular = [
        ('blue', 1, 1),
        ('green', 3, 3),
        ('gold', 6, 6),
        ('cyan', 8, 8),
    ]

    for color, v1, v2 in regular:
        edges = [
            ((c, v1), ((c + 1) % num_clusters, v2))
            for c in range(num_clusters)
        ]
        nx.draw_networkx_edges(
            G, pos,
            edgelist=edges,
            edge_color=color,
            width=2.5,
            connectionstyle='arc3,rad=0.10',
        )

    # Нерегулярні зв'язки.
    irregular = [
        ('red', 7, 7, 2),
        ('limegreen', 4, 5, 2),
        ('gold', 2, 2, 3),
        ('deepskyblue', 5, 4, 3),
    ]

    for color, v1, v2, step in irregular:
        if num_clusters <= step:
            continue
        edges = [
            ((c, v1), ((c + step) % num_clusters, v2))
            for c in range(num_clusters)
        ]
        nx.draw_networkx_edges(
            G, pos,
            edgelist=edges,
            edge_color=color,
            style='dashed',
            width=1.8,
            connectionstyle='arc3,rad=0.15',
        )

    nx.draw_networkx_nodes(
        G, pos,
        node_size=220,
        node_color='white',
        edgecolors='black',
    )

    labels = {(c, v): str(v) for c in range(num_clusters) for v in range(1, 9)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=6, font_weight='bold')

    for c in range(num_clusters):
        angle = 2 * math.pi * c / num_clusters
        cx = radius * math.cos(angle)
        cy = radius * math.sin(angle)
        plt.text(
            cx,
            cy - 3.7,
            f'Кластер {c + 1}',
            ha='center',
            fontsize=10,
            fontweight='bold',
        )

    plt.title(f'Кільцева топологія: {num_clusters} кластерів ({8 * num_clusters} вузлів)')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


# 6. Інтерактивний запуск

def main():
    print('\nЛабораторна робота №1')
    print('Кластер №23, кільцева міжкластерна топологія')
    print('Один кластер містить 8 процесорів.')

    while True:
        try:
            num_steps = int(input(
                '\nВведіть кількість кроків масштабування '
                '(кількість кластерів): '
            ))
            if num_steps < 1:
                print('Помилка: кількість кроків повинна бути не менше 1.')
                continue
            break
        except ValueError:
            print('Помилка: введіть ціле число.')

    # --------------------------------------------------------
    # Побудова таблиці для ВСІХ кроків: 1, 2, 3, ..., num_steps
    # --------------------------------------------------------
    results = build_table(cluster, num_steps)

    print('\n' + '=' * 90)
    print(f'ТАБЛИЦЯ РЕЗУЛЬТАТІВ ДЛЯ {num_steps} КРОКІВ МАСШТАБУВАННЯ')
    print('=' * 90)
    print(results.to_string(float_format=lambda x: f'{x:.3f}'))
    print('=' * 90)

    # Зберігаємо всю таблицю у CSV.
    filename = f'LR1_cluster23_results_1_to_{num_steps}.csv'
    results.to_csv(filename)
    print(f'\nТаблицю збережено у файл: {filename}')

    # Окремо показуємо характеристики останнього кроку.
    final_result = results.loc[num_steps]
    print(f'\nФінальний крок: {num_steps} кластерів ({8 * num_steps} процесорів)')
    print(final_result.to_string())

    # Показуємо базовий кластер і фінальну систему.
    print('\nВідкриваємо схему базового кластера №23...')
    visualize_cluster()

    print(f'\nВідкриваємо схему системи для {num_steps} кластерів...')
    visualize_graph(num_steps)


if __name__ == '__main__':
    main()
