"""
Жадібний алгоритм розподілу земельних ділянок між 4 забудовниками.

Args:
    matrix: список списків (n×n) з цілими вартостями ділянок

Returns:
    tuple: (regions, iterations) де
    regions - список довжини 4, де кожен елемент - список координат [(i, j), ...]
    ділянок для відповідного забудовника (індекси 0-3 відповідають забудовникам 1-4)
    iterations - кількість ітерацій алгоритму
"""

def greedy_allocation(matrix):
    """
    Жадібний алгоритм розподілу земельних ділянок між 4 забудовниками.

    Args:
        matrix: список списків (n×n) з цілими вартостями ділянок

    Returns:
        tuple: (regions, iterations) де
        regions - список довжини 4, де кожен елемент - список координат [(i, j), ...]
        ділянок для відповідного забудовника (індекси 0-3 відповідають забудовникам 1-4)
        iterations - кількість ітерацій алгоритму
    """
    if not matrix or not matrix[0]:
        return [[], [], [], []], 0

    n = len(matrix)
    m = len(matrix[0])

    # Ініціалізація
    regions = [
        [],
        [],
        [],
        [],
    ]  # Регіони для кожного забудовника (0-3 → забудовники 1-4)
    sums = [0, 0, 0, 0]  # Суми вартостей для кожного забудовника
    assigned = [[False for _ in range(m)] for _ in range(n)]  # Матриця призначень
    allocation_iter_count = 0  # Лічильник ітерацій

    # Призначення початкових ділянок (по кутах для забезпечення розділення)
    start_positions = [
        (0, 0),  # Забудовник 1 - верхній лівий кут
        (0, m - 1),  # Забудовник 2 - верхній правий кут
        (n - 1, 0),  # Забудовник 3 - нижній лівий кут
        (n - 1, m - 1),  # Забудовник 4 - нижній правий кут
    ]

    # Ініціалізація початкових позицій
    for dev in range(4):
        i, j = start_positions[dev]
        regions[dev].append((i, j))
        sums[dev] += matrix[i][j]
        assigned[i][j] = True

    # Основний цикл алгоритму
    total_assigned = 4
    total_cells = n * m

    while total_assigned < total_cells:
        allocation_iter_count += 1

        # Знайти забудовника з найменшою сумою
        min_dev = get_developer_with_min_sum(sums)

        # Знайти всі суміжні вільні ділянки для цього забудовника
        adjacent_cells = get_adjacent_free_cells(regions[min_dev], assigned, n, m)

        target_dev = min_dev  # За замовчуванням цільовий забудовник

        if not adjacent_cells:
            # Якщо немає суміжних клітин для забудовника з мін сумою,
            # знайти забудовника, який має суміжні клітини
            target_dev, adjacent_cells = find_developer_with_adjacent_cells(
                regions, assigned, n, m
            )
            if target_dev == -1 or not adjacent_cells:
                break  # Не можемо знайти жодної суміжної клітини

        # Вибрати найкращу ділянку (мінімізувати дисбаланс)
        best_cell = choose_best_cell(adjacent_cells, matrix, sums, target_dev)

        # Призначити вибрану ділянку забудовнику
        i, j = best_cell
        regions[target_dev].append((i, j))
        sums[target_dev] += matrix[i][j]
        assigned[i][j] = True
        total_assigned += 1

    return regions, allocation_iter_count


def get_developer_with_min_sum(sums):
    """Знайти забудовника з найменшою сумою вартостей"""
    return sums.index(min(sums))


def get_adjacent_free_cells(region, assigned, n, m):
    """
    Знайти всі вільні клітини, суміжні з регіоном забудовника

    Args:
        region: список координат ділянок забудовника
        assigned: матриця призначених ділянок
        n, m: розміри матриці

    Returns:
        список координат суміжних вільних клітин
    """
    adjacent = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # вгору, вниз, ліворуч, праворуч

    for i, j in region:
        for di, dj in directions:
            ni, nj = i + di, j + dj
            # Перевірити, чи координати в межах матриці і клітина вільна
            if 0 <= ni < n and 0 <= nj < m and not assigned[ni][nj]:
                adjacent.add((ni, nj))

    return list(adjacent)


def find_developer_with_adjacent_cells(regions, assigned, n, m):
    """
    Знайти забудовника, який має суміжні вільні клітини

    Returns:
        tuple: (індекс забудовника, список суміжних клітин)
               або (-1, []) якщо нікого не знайдено
    """
    for dev in range(4):
        adjacent_cells = get_adjacent_free_cells(regions[dev], assigned, n, m)
        if adjacent_cells:
            return dev, adjacent_cells

    return -1, []


def get_any_adjacent_free_cells(regions, assigned, n, m):
    """
    Знайти суміжні вільні клітини для будь-якого забудовника
    (використовується як fallback)
    """
    all_adjacent = set()

    for region in regions:
        adjacent = get_adjacent_free_cells(region, assigned, n, m)
        all_adjacent.update(adjacent)

    return list(all_adjacent)


def choose_best_cell(adjacent_cells, matrix, sums, target_dev):
    """
    Вибрати найкращу клітину з суміжних для мінімізації дисбалансу

    Args:
        adjacent_cells: список суміжних вільних клітин
        matrix: матриця вартостей
        sums: поточні суми забудовників
        target_dev: індекс цільового забудовника

    Returns:
        координати найкращої клітини
    """
    if len(adjacent_cells) == 1:
        return adjacent_cells[0]

    best_cell = None
    min_imbalance = float("inf")

    for i, j in adjacent_cells:
        # Симулювати додавання цієї клітини
        temp_sums = sums.copy()
        temp_sums[target_dev] += matrix[i][j]

        # Обчислити дисбаланс
        imbalance = calculate_imbalance(temp_sums)

        if imbalance < min_imbalance:
            min_imbalance = imbalance
            best_cell = (i, j)

    return best_cell if best_cell else adjacent_cells[0]


def calculate_imbalance(sums):
    """
    Обчислити дисбаланс між забудовниками

    Args:
        sums: список сум вартостей для кожного забудовника

    Returns:
        значення дисбалансу (різниця між максимальною та мінімальною сумою)
    """
    return max(sums) - min(sums)


def print_allocation_info(matrix, regions, iteration_count):
    """
    Вивести інформацію про розподіл для дебагу

    Args:
        matrix: матриця вартостей
        regions: результат розподілу
        iteration_count: кількість ітерацій алгоритму
    """
    print("\n=== РЕЗУЛЬТАТИ ЖАДІБНОГО АЛГОРИТМУ ===")

    sums = [0, 0, 0, 0]
    for dev in range(4):
        for i, j in regions[dev]:
            sums[dev] += matrix[i][j]
        print(f"Забудовник {dev + 1}: {sums[dev]}")

    objective_value = calculate_imbalance(sums)
    print(f"Значення цільової функції: {objective_value}")
    print(f"Кількість ітерацій: {iteration_count}")


def visualize_allocation(matrix, regions):
    """
    Візуалізувати розподіл у вигляді матриці з номерами забудовників

    Args:
        matrix: матриця вартостей
        regions: результат розподілу
    """
    if not matrix or not regions:
        return

    n = len(matrix)
    m = len(matrix[0])

    # Створити матрицю візуалізації
    allocation_matrix = [[-1 for _ in range(m)] for _ in range(n)]

    for dev in range(4):
        for i, j in regions[dev]:
            allocation_matrix[i][j] = dev + 1  # Показувати номери 1-4

    print("\n=== ВІЗУАЛІЗАЦІЯ РОЗПОДІЛУ ===")
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
    # Тест 1: Маленька матриця 3x3
    print("=== ТЕСТ 1: Матриця 3x3 ===")
    test_matrix_3x3 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    result, iter_count = greedy_allocation(test_matrix_3x3)
    visualize_allocation(test_matrix_3x3, result)
    print_allocation_info(test_matrix_3x3, result, iter_count)

    # Тест 2: Матриця 4x4 з різними значеннями
    print("\n=== ТЕСТ 2: Матриця 4x4 ===")
    test_matrix_4x4 = [
        [10, 15, 20, 25],
        [30, 35, 40, 45],
        [50, 55, 60, 65],
        [70, 75, 80, 85],
    ]

    result, iter_count = greedy_allocation(test_matrix_4x4)
    visualize_allocation(test_matrix_4x4, result)
    print_allocation_info(test_matrix_4x4, result, iter_count)

    # Тест 3: Матриця з однаковими значеннями
    print("\n=== ТЕСТ 3: Однакові значення ===")
    test_matrix_uniform = [[5, 5, 5, 5], [5, 5, 5, 5], [5, 5, 5, 5], [5, 5, 5, 5]]

    result, iter_count = greedy_allocation(test_matrix_uniform)
    visualize_allocation(test_matrix_uniform, result)
    print_allocation_info(test_matrix_uniform, result, iter_count)
