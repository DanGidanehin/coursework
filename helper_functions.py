"""
helper_functions.py

Модуль містить допоміжні функції:
- генерація випадкової матриці,
- зчитування матриці з файлу,
- відображення матриці на екран.
"""

import random


def generate_random_matrix(
    m: int, n: int, min_val: int = 1, max_val: int = 10
) -> list[list[int]]:
    """
    Генерує випадкову матрицю розміром m×n.

    Аргументи:
        m: Кількість рядків матриці.
        n: Кількість стовпців матриці.
        min_val: Мінімальне значення елемента (включно).
        max_val: Максимальне значення елемента (включно).

    Повертає:
        Список списків (матрицю) із випадкових цілих чисел від min_val до max_val.
    """
    return [[random.randint(min_val, max_val) for _ in range(n)] for _ in range(m)]


def read_input_matrix(filename: str) -> tuple[int, int, list[list[int]]] | None:
    """
    Зчитує матрицю з текстового файлу.

    Формат файлу:
        Перша строка: два числа m та n (кількість рядків і стовпців).
        Далі m рядків по n чисел кожен.

    Аргументи:
        filename: Шлях до текстового файлу з матрицею.

    Повертає:
        Кортеж (m, n, matrix), де matrix — список списків із розмірами m×n,
        або None у разі помилки (файл не знайдено або некоректний формат).
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Перевірка наявності хоча б одного рядка
        if not lines:
            print("Помилка: файл порожній.")
            return None

        # Зчитуємо розміри матриці
        first_line = lines[0].strip().split()
        if len(first_line) != 2:
            print("Некоректний формат файлу: очікуються два числа у першому рядку.")
            return None

        m, n = map(int, first_line)
        if m < 1 or n < 1:
            print("Некоректні розміри матриці: m і n мають бути додатніми.")
            return None

        matrix: list[list[int]] = []

        # Перевірка, що у файлі є достатньо рядків
        if len(lines) < m + 1:
            print("Некоректний формат файлу: недостатньо рядків.")
            return None

        # Зчитуємо m рядків по n чисел
        for i in range(1, m + 1):
            row_str = lines[i].strip().split()
            if len(row_str) != n:
                print("Некоректний формат файлу: кількість стовпців не співпадає.")
                return None
            try:
                row = list(map(int, row_str))
            except ValueError:
                print("Некоректний формат файлу: значення мають бути цілими числами.")
                return None
            matrix.append(row)

        return m, n, matrix

    except IOError as e:
        print(f"Помилка читання файлу: {e}")
        return None
    except ValueError as e:
        print(f"Помилка обробки чисел у файлі: {e}")
        return None


def display_matrix(matrix: list[list[int]]) -> None:
    """
    Виводить матрицю на екран у зручному форматі.

    Аргументи:
        matrix: Список списків із числами, які потрібно вивести.
    """
    for row in matrix:
        print(" ".join(str(x) for x in row))
