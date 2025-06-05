"""
Модуль реалізує наближений двоетапний алгоритм розподілу земельних ділянок
між чотирма забудовниками. Після створення початкового поділу за блоками цей
скрипт виконує коригування кордонів для мінімізації дисбалансу.
"""


def two_stage_allocation(matrix, max_iterations: int = 100):
    """
    Наближений двоетапний алгоритм розподілу земельних ділянок між 4 забудовниками.

    Args:
        matrix: список списків (n×n) з цілими вартостями ділянок
        max_iterations: максимальна кількість ітерацій другого етапу оптимізації

    Returns:
        tuple: (regions, iterations) де
            regions   – список довжини 4, де кожен елемент – список координат [(i, j), ...]
                         ділянок для відповідного забудовника (індекси 0–3 відповідають забудовникам 1–4)
            iterations – кількість виконаних ітерацій другого етапу
    """
    if not matrix or not matrix[0]:
        return [[], [], [], []], 0

    # Етап 1: Створюємо грубий початковий розподіл
    regions = create_initial_allocation(matrix)

    # Етап 2: Оптимізуємо кордони, передаючи туди max_iterations
    regions, iterations = optimize_boundaries(matrix, regions, max_iterations)

    return regions, iterations


def create_initial_allocation(matrix):
    """
    Етап 1: Створити початковий розподіл, розділивши матрицю на 4 блоки у
    рядково-стовпчиковому порядку.

    Args:
        matrix: матриця вартостей

    Returns:
        список з 4 регіонами (списками координат)
    """
    n = len(matrix)
    m = len(matrix[0])
    total_cells = n * m

    # Створити список всіх клітин у рядково-стовпчиковому порядку
    all_cells = []
    for i in range(n):
        for j in range(m):
            all_cells.append((i, j))

    # Розділити клітини на 4 приблизно рівні частини
    cells_per_region = total_cells // 4
    remainder = total_cells % 4

    regions = [[], [], [], []]
    start_idx = 0

    for dev in range(4):
        # Додати одну додаткову клітину до перших remainder регіонів
        region_size = cells_per_region + (1 if dev < remainder else 0)
        end_idx = start_idx + region_size

        regions[dev] = all_cells[start_idx:end_idx]
        start_idx = end_idx

    return regions


def optimize_boundaries(matrix, regions, max_iterations: int):
    """
    Етап 2: Оптимізувати кордони між регіонами, мінімізуючи дисбаланс вартостей.

    Args:
        matrix: матриця вартостей
        regions: початковий розподіл
        max_iterations: максимальна кількість ітерацій другого етапу

    Returns:
        tuple: (оптимізовані регіони, кількість виконаних ітерацій)
    """
    n = len(matrix)
    m = len(matrix[0])
    iterations = 0

    while iterations < max_iterations:
        current_imbalance = calculate_current_imbalance(matrix, regions)
        improvement_found = False

        best_improvement = 0
        best_move = None

        # Перебираємо усі пари регіонів для пошуку можливого переміщення кордонної клітини
        for dev1 in range(4):
            for dev2 in range(4):
                if dev1 == dev2:
                    continue

                # Знайти межеві клітини між регіонами dev1 і dev2
                boundary_cells = find_boundary_cells(regions[dev1], regions[dev2], n, m)

                for cell in boundary_cells:
                    from_dev = dev1 if cell in regions[dev1] else dev2
                    to_dev = dev2 if from_dev == dev1 else dev1

                    # Симулювати переміщення клітини
                    new_imbalance = simulate_move(
                        matrix, regions, cell, from_dev, to_dev
                    )
                    improvement = current_imbalance - new_imbalance

                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_move = (cell, from_dev, to_dev)

        # Якщо знайдено покращення, виконати переміщення
        if best_move:
            cell, from_dev, to_dev = best_move
            regions[from_dev].remove(cell)
            regions[to_dev].append(cell)
            improvement_found = True

        iterations += 1
        if not improvement_found:
            break

    return regions, iterations


def find_boundary_cells(region1, region2, n, m):
    """
    Знайти межеві клітини між двома регіонами.

    Args:
        region1, region2: списки координат клітин двох регіонів
        n, m: розміри матриці

    Returns:
        список межевих клітин
    """
    boundary_cells = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # вверх, вниз, вліво, вправо

    region1_set = set(region1)
    region2_set = set(region2)

    # Перевірити клітини region1, які мають сусідів у region2
    for i, j in region1:
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < m and (ni, nj) in region2_set:
                boundary_cells.add((i, j))
                break

    # Перевірити клітини region2, які мають сусідів у region1
    for i, j in region2:
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < m and (ni, nj) in region1_set:
                boundary_cells.add((i, j))
                break

    return list(boundary_cells)


def simulate_move(matrix, regions, cell, from_dev, to_dev):
    """
    Симулювати переміщення клітини і обчислити новий дисбаланс.

    Args:
        matrix: матриця вартостей
        regions: поточні регіони
        cell: координати клітини для переміщення
        from_dev, to_dev: індекси забудовників

    Returns:
        новий дисбаланс після переміщення
    """
    sums = [0, 0, 0, 0]
    for dev in range(4):
        for i, j in regions[dev]:
            sums[dev] += matrix[i][j]

    i, j = cell
    cell_value = matrix[i][j]
    sums[from_dev] -= cell_value
    sums[to_dev] += cell_value

    return max(sums) - min(sums)


def calculate_current_imbalance(matrix, regions):
    """
    Обчислити поточний дисбаланс.

    Args:
        matrix: матриця вартостей
        regions: поточні регіони

    Returns:
        значення дисбалансу
    """
    sums = [0, 0, 0, 0]
    for dev in range(4):
        for i, j in regions[dev]:
            sums[dev] += matrix[i][j]

    return max(sums) - min(sums)


def print_allocation_info_two_stage(matrix, regions, iterations):
    """
    Вивести інформацію про розподіл для двоетапного алгоритму.

    Args:
        matrix: матриця вартостей
        regions: результат розподілу
        iterations: кількість ітерацій другого етапу
    """
    print("\n=== РЕЗУЛЬТАТИ ДВОЕТАПНОГО АЛГОРИТМУ ===")
    sums = [0, 0, 0, 0]
    for dev in range(4):
        for i, j in regions[dev]:
            sums[dev] += matrix[i][j]
        print(f"Забудовник {dev + 1}: {sums[dev]}")

    objective_value = max(sums) - min(sums)
    print(f"Значення цільової функції: {objective_value}")
    print(f"Кількість ітерацій (етап 2): {iterations}")


def visualize_allocation_two_stage(matrix, regions):
    """
    Візуалізувати розподіл двоетапного алгоритму.

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

    print("\n=== ВІЗУАЛІЗАЦІЯ РОЗПОДІЛУ (ДВОЕТАПНИЙ) ===")
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
    # Тест 1: Маленька матриця 3×3
    print("=== ТЕСТ 1: Матриця 3×3 ===")
    test_matrix_3x3 = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    result, iter_count = two_stage_allocation(test_matrix_3x3, max_iterations=50)
    visualize_allocation_two_stage(test_matrix_3x3, result)
    print_allocation_info_two_stage(test_matrix_3x3, result, iter_count)

    # Тест 2: Матриця 4×4 з різними значеннями
    print("\n=== ТЕСТ 2: Матриця 4×4 ===")
    test_matrix_4x4 = [
        [10, 15, 20, 25],
        [30, 35, 40, 45],
        [50, 55, 60, 65],
        [70, 75, 80, 85],
    ]
    result, iter_count = two_stage_allocation(test_matrix_4x4, max_iterations=100)
    visualize_allocation_two_stage(test_matrix_4x4, result)
    print_allocation_info_two_stage(test_matrix_4x4, result, iter_count)

    # Тест 3: Матриця з однаковими значеннями
    print("\n=== ТЕСТ 3: Однакові значення ===")
    test_matrix_uniform = [
        [5, 5, 5, 5],
        [5, 5, 5, 5],
        [5, 5, 5, 5],
        [5, 5, 5, 5],
    ]
    result, iter_count = two_stage_allocation(test_matrix_uniform, max_iterations=100)
    visualize_allocation_two_stage(test_matrix_uniform, result)
    print_allocation_info_two_stage(test_matrix_uniform, result, iter_count)
