"""
Алгоритм повного перебору для розподілу земельних ділянок між забудовниками.
Перебирає всі можливі варіанти розподілу та знаходить оптимальний.
"""

import itertools
from collections import deque


def brute_force_allocation(matrix):
    """
    Алгоритм повного перебору для розподілу земельних ділянок між 4 забудовниками.

    Args:
        matrix: список списків (n×n) з цілими вартостями ділянок

    Returns:
        tuple: (regions, combinations_checked) де
            regions               
            – список довжини 4, де кожен елемент — список координат [(i, j), ...]
            ділянок для відповідного забудовника (індекси 0–3 відповідають забудовникам 1–4)
            combinations_checked  – кількість перевірених комбінацій
    """
    if not matrix or not matrix[0]:
        return [[], [], [], []], 0

    n = len(matrix)
    m = len(matrix[0])
    total_cells = n * m

    # Обмеження для практичності
    if total_cells > 16:
        print(
            f"Попередження: матриця {n}×{m} ({total_cells} клітин) занадто велика для brute force!"
        )
        print("Рекомендується використовувати матриці до 4×4 включно.")
        return [[], [], [], []], 0

    best_regions = None
    best_objective = float("inf")
    combinations_checked = 0
    total_combinations = 4**total_cells

    print(f"Перевіряємо {total_combinations:,} можливих комбінацій...")

    # Генерувати всі можливі комбінації labels
    for labels in itertools.product(range(4), repeat=total_cells):
        combinations_checked += 1

        # Показувати прогрес кожні 10000 комбінацій
        if combinations_checked % 10000 == 0:
            progress = (combinations_checked / total_combinations) * 100
            print(
                f"Прогрес: {progress:.1f}% ({combinations_checked:,}/{total_combinations:,})"
            )

        # Конвертувати labels у regions
        regions = labels_to_regions(labels, n, m)

        # Оптимізація: пропустити, якщо якийсь забудовник не отримав клітин
        if any(len(region) == 0 for region in regions):
            continue

        # Перевірити зв'язність всіх регіонів
        if not all_regions_connected(regions, n, m):
            continue

        # Обчислити objective value
        objective_value = calculate_objective_value(matrix, regions)

        # Зберегти найкращий результат
        if objective_value < best_objective:
            best_objective = objective_value
            best_regions = [region.copy() for region in regions]

    if best_regions is None:
        print("Не знайдено жодного валідного розподілу!")
        return [[], [], [], []], combinations_checked

    print(f"Перевірено {combinations_checked:,} комбінацій")
    print(f"Найкраще значення цільової функції: {best_objective}")

    return best_regions, combinations_checked


def labels_to_regions(labels, _n, m):
    """
    Конвертувати список labels у regions (координати).

    Args:
        labels: список довжини n*m з значеннями 0–3
        _n: (unused) кількість рядків
        m: кількість стовпців матриці

    Returns:
        список з 4 регіонами (списками координат)
    """
    regions = [[], [], [], []]

    for idx, dev in enumerate(labels):
        i = idx // m
        j = idx % m
        regions[dev].append((i, j))

    return regions


def all_regions_connected(regions, n, m):
    """
    Перевірити зв'язність всіх регіонів.

    Args:
        regions: список з 4 регіонами
        n, m: розміри матриці

    Returns:
        True якщо всі регіони зв'язані, False інакше
    """
    for region in regions:
        if len(region) > 0 and not check_connected(region, n, m):
            return False
    return True


def check_connected(region_coords, n, m):
    """
    Перевірити зв'язність регіону за допомогою BFS.

    Args:
        region_coords: список координат клітин регіону
        n, m: розміри матриці

    Returns:
        True якщо регіон зв'язаний, False інакше
    """
    if len(region_coords) <= 1:
        return True

    region_set = set(region_coords)
    visited = set()
    queue = deque([region_coords[0]])  # Почати з першої клітини
    visited.add(region_coords[0])

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # вгору, вниз, ліворуч, праворуч

    while queue:
        i, j = queue.popleft()

        for di, dj in directions:
            ni, nj = i + di, j + dj

            # Перевірити: сусід в межах матриці, належить регіону й не відвіданий
            if (
                0 <= ni < n
                and 0 <= nj < m
                and (ni, nj) in region_set
                and (ni, nj) not in visited
            ):
                visited.add((ni, nj))
                queue.append((ni, nj))

    # Регіон зв'язаний, якщо відвідали всі його клітини
    return len(visited) == len(region_coords)


def calculate_objective_value(matrix, regions):
    """
    Обчислити значення цільової функції (дисбаланс).

    Args:
        matrix: матриця вартостей
        regions: список регіонів

    Returns:
        значення цільової функції
    """
    sums = [0, 0, 0, 0]

    for dev in range(4):
        for i, j in regions[dev]:
            sums[dev] += matrix[i][j]

    return max(sums) - min(sums)


def print_allocation_info_brute_force(matrix, regions, combinations_checked):
    """
    Вивести інформацію про розподіл для brute force алгоритму.

    Args:
        matrix: матриця вартостей
        regions: результат розподілу
        combinations_checked: кількість перевірених комбінацій
    """
    print("\n=== РЕЗУЛЬТАТИ BRUTE FORCE АЛГОРИТМУ ===")

    sums = [0, 0, 0, 0]
    for dev in range(4):
        for i, j in regions[dev]:
            sums[dev] += matrix[i][j]
        print(f"Забудовник {dev + 1}: {sums[dev]}")

    objective_value = max(sums) - min(sums)
    print(f"Значення цільової функції: {objective_value}")
    print(f"Перевірено комбінацій: {combinations_checked:,}")


def visualize_allocation_brute_force(matrix, regions):
    """
    Візуалізувати розподіл brute force алгоритму.

    Args:
        matrix: матриця вартостей
        regions: результат розподілу
    """
    if not matrix or not regions:
        return

    n = len(matrix)
    m = len(matrix[0])

    allocation_matrix = [[-1 for _ in range(m)] for _ in range(n)]
    for dev in range(4):
        for i, j in regions[dev]:
            allocation_matrix[i][j] = dev + 1  # Показувати номери 1–4

    print("\n=== ВІЗУАЛІЗАЦІЯ РОЗПОДІЛУ (BRUTE FORCE) ===")
    print("Номери забудовників для кожної ділянки:")
    for i in range(n):
        row = ""
        for j in range(m):
            if allocation_matrix[i][j] == -1:
                row += "  - "
            else:
                row += f"  {allocation_matrix[i][j]} "
        print(row)

    print("\nВартості ділянок:")
    for i in range(n):
        row = ""
        for j in range(m):
            row += f"{matrix[i][j]:4}"
        print(row)


if __name__ == "__main__":
    # Тест 1: Маленька матриця 2×2 (швидкий тест)
    print("=== ТЕСТ 1: Матриця 2×2 ===")
    test_matrix_2x2 = [[1, 2], [3, 4]]
    result, combinations = brute_force_allocation(test_matrix_2x2)
    visualize_allocation_brute_force(test_matrix_2x2, result)
    print_allocation_info_brute_force(test_matrix_2x2, result, combinations)

    # Тест 2: Матриця 3×3 (основний тест)
    print("\n=== ТЕСТ 2: Матриця 3×3 ===")
    test_matrix_3x3 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    result, combinations = brute_force_allocation(test_matrix_3x3)
    visualize_allocation_brute_force(test_matrix_3x3, result)
    print_allocation_info_brute_force(test_matrix_3x3, result, combinations)

    # Тест 3: Матриця з однаковими значеннями 3×3
    print("\n=== ТЕСТ 3: Однакові значення 3×3 ===")
    test_matrix_uniform = [[5, 5, 5], [5, 5, 5], [5, 5, 5]]
    result, combinations = brute_force_allocation(test_matrix_uniform)
    visualize_allocation_brute_force(test_matrix_uniform, result)
    print_allocation_info_brute_force(test_matrix_uniform, result, combinations)
