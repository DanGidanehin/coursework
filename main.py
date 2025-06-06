"""
Головний модуль для взаємодії з програмою розподілу земельних ділянок.
- Покращений інтерфейс із чіткими меню та форматуванням.
- Підтримка введення матриці (ручне, випадкове, з файлу).
- Запуск алгоритмів: Жадібний, Двоетапний, Повний перебір.
- Проведення експериментів із збереженням графіків.
- Логування результатів у result_output.txt.
- Вимірювання та вивід часу виконання кожного алгоритму.
"""

import sys
import time
from typing import Optional, Tuple, List
from greedy import greedy_allocation, visualize_allocation, print_allocation_info
from two_stage import (
    two_stage_allocation,
    visualize_allocation_two_stage,
    print_allocation_info_two_stage,
)
from brute_force import (
    brute_force_allocation,
    visualize_allocation_brute_force,
    print_allocation_info_brute_force,
)
from helper_functions import generate_random_matrix, read_input_matrix, display_matrix
import experiments


# ANSI-коди для кольорового виводу (опціонально)
class Colors:
    HEADER = "\033[95m"
    PROMPT = "\033[94m"
    ERROR = "\033[91m"
    SUCCESS = "\033[92m"
    WARNING = "\033[93m"
    INFO = "\033[96m"
    RESET = "\033[0m"


# Налаштування для терміналів, що не підтримують ANSI
USE_COLORS = sys.stdout.isatty()


def format_text(text: str, color: str = "") -> str:
    """Форматує текст із кольором, якщо підтримується."""
    return f"{color}{text}{Colors.RESET}" if USE_COLORS else text


class Logger:
    """Клас для дублювання виводу в консоль і лог-файл."""

    def __init__(self, filename: str):
        self.terminal = sys.__stdout__
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message: str):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


def logged_input(prompt: str = "") -> str:
    """
    Зчитує введення користувача та дублює в лог.
    Якщо згенерований рядок виводу, показує тільки один раз.
    """
    # Виводимо prompt один раз (пофарбованим, якщо можливо)
    sys.stdout.write(format_text(prompt, Colors.PROMPT))
    value = input()
    # Записуємо в лог-файл те, що ввів користувач (prompt + введене)
    sys.stdout.write(f"{prompt}{value}\n")
    return value


def print_header(title: str):
    """Виводить форматований заголовок."""
    print(f"\n{format_text('=' * 60, Colors.HEADER)}")
    print(format_text(f" {title} ", Colors.HEADER))
    print(f"{format_text('=' * 60, Colors.HEADER)}\n")


def print_subheader(title: str):
    """Виводить форматований підзаголовок."""
    print(f"\n{format_text('-' * 40, Colors.HEADER)}")
    print(format_text(f" {title} ", Colors.HEADER))
    print(f"{format_text('-' * 40, Colors.HEADER)}\n")


def print_timing_info(algorithm_name: str, execution_time: float):
    """Виводить інформацію про час виконання алгоритму."""
    if execution_time < 0.001:
        time_str = f"{execution_time * 1000000:.2f} мкс"
        color = Colors.SUCCESS
    elif execution_time < 1.0:
        time_str = f"{execution_time * 1000:.2f} мс"
        color = Colors.INFO
    elif execution_time < 60.0:
        time_str = f"{execution_time:.4f} сек"
        color = Colors.WARNING
    else:
        minutes = int(execution_time // 60)
        seconds = execution_time % 60
        time_str = f"{minutes} хв {seconds:.2f} сек"
        color = Colors.ERROR

    print(format_text(f"⏱️  Час виконання {algorithm_name}: {time_str}", color))


def input_manual() -> Optional[Tuple[int, int, List[List[int]]]]:
    """Зчитує матрицю вручну."""
    print_subheader("Ручне введення матриці")
    try:
        m = int(logged_input("Введіть кількість рядків (m): "))
        n = int(logged_input("Введіть кількість стовпців (n): "))
        if m < 1 or n < 1:
            print(
                format_text(
                    "Помилка: розміри матриці мають бути додатними.", Colors.ERROR
                )
            )
            return None

        print("Введіть матрицю вартості (по одному рядку з n чисел):")
        matrix: List[List[int]] = []
        for i in range(m):
            row = list(map(int, logged_input(f"Рядок {i + 1}: ").split()))
            if len(row) != n:
                print(
                    format_text(f"Помилка: очікується {n} чисел у рядку.", Colors.ERROR)
                )
                return None
            matrix.append(row)

        print_subheader("Введена матриця")
        display_matrix(matrix)
        return m, n, matrix

    except ValueError:
        print(format_text("Помилка: введіть коректні числа.", Colors.ERROR))
        return None


def input_random() -> Optional[Tuple[int, int, List[List[int]]]]:
    """Генерує випадкову матрицю."""
    print_subheader("Випадкова генерація матриці")
    try:
        m = int(logged_input("Введіть кількість рядків (m): "))
        n = int(logged_input("Введіть кількість стовпців (n): "))
        c = int(logged_input("Введіть верхню межу вартості ділянки (c): "))
        if m < 1 or n < 1 or c < 1:
            print(
                format_text("Помилка: усі значення мають бути додатними.", Colors.ERROR)
            )
            return None

        matrix = generate_random_matrix(m, n, 1, c)
        print_subheader("Згенерована матриця")
        display_matrix(matrix)
        return m, n, matrix

    except ValueError:
        print(format_text("Помилка: введіть коректні числа.", Colors.ERROR))
        return None


def input_from_file() -> Optional[Tuple[int, int, List[List[int]]]]:
    """Зчитує матрицю з файлу input.txt."""
    print_subheader("Зчитування матриці з файлу")
    data = read_input_matrix("input.txt")
    if data is None:
        print(format_text("Помилка: не вдалося зчитати input.txt.", Colors.ERROR))
        return None

    m, n, matrix = data
    print_subheader("Зчитана матриця")
    display_matrix(matrix)
    return m, n, matrix


def run_algorithms(m: int, n: int, matrix: List[List[int]]):
    """Запускає всі алгоритми та виводить результати з вимірюванням часу."""
    print_subheader("Результати алгоритмів")

    total_time = 0.0
    algorithm_times = {}

    # Жадібний алгоритм
    print("\nЗапуск Жадібного алгоритму...")
    try:
        start_time = time.time()
        regions, iterations = greedy_allocation(matrix)
        end_time = time.time()

        execution_time = end_time - start_time
        algorithm_times["Жадібний"] = execution_time
        total_time += execution_time

        visualize_allocation(matrix, regions)
        print_allocation_info(matrix, regions, iterations)
        print_timing_info("Жадібного алгоритму", execution_time)

    except Exception as e:
        print(format_text(f"Помилка в Жадібному алгоритмі: {e}", Colors.ERROR))

    # Двоетапний алгоритм
    print("\nЗапуск Двоетапного алгоритму...")
    try:
        start_time = time.time()
        regions, iterations = two_stage_allocation(matrix)
        end_time = time.time()

        execution_time = end_time - start_time
        algorithm_times["Двоетапний"] = execution_time
        total_time += execution_time

        visualize_allocation_two_stage(matrix, regions)
        print_allocation_info_two_stage(matrix, regions, iterations)
        print_timing_info("Двоетапного алгоритму", execution_time)

    except Exception as e:
        print(format_text(f"Помилка в Двоетапному алгоритмі: {e}", Colors.ERROR))

    # Повний перебір (тільки для малих матриць)
    if m * n <= 16:
        print("\nЗапуск алгоритму Повного перебору...")
        try:
            start_time = time.time()
            regions, combinations = brute_force_allocation(matrix)
            end_time = time.time()

            execution_time = end_time - start_time
            algorithm_times["Повний перебір"] = execution_time
            total_time += execution_time

            visualize_allocation_brute_force(matrix, regions)
            print_allocation_info_brute_force(matrix, regions, combinations)
            print_timing_info("алгоритму Повного перебору", execution_time)

        except Exception as e:
            print(
                format_text(f"Помилка в алгоритмі Повного перебору: {e}", Colors.ERROR)
            )
    else:
        print(
            format_text(
                "Розмір матриці перевищує 4×4, Повний перебір пропущено.",
                Colors.WARNING,
            )
        )

    # Підсумкова статистика
    print_subheader("Підсумкова статистика часу виконання")

    if algorithm_times:
        fastest = min(algorithm_times.items(), key=lambda x: x[1])
        slowest = max(algorithm_times.items(), key=lambda x: x[1])

        print(
            f"📊 Загальний час виконання всіх алгоритмів: {format_text(f'{total_time:.4f} сек', Colors.INFO)}"
        )
        print(
            f"🚀 Найшвидший алгоритм: {format_text(fastest[0], Colors.SUCCESS)} ({fastest[1]:.4f} сек)"
        )
        print(
            f"🐌 Найповільніший алгоритм: {format_text(slowest[0], Colors.WARNING)} ({slowest[1]:.4f} сек)"
        )

        # Детальна таблиця часів
        print("\n📋 Детальна статистика:")
        for name, exec_time in sorted(algorithm_times.items(), key=lambda x: x[1]):
            percentage = (exec_time / total_time) * 100
            print(f"   {name:15}: {exec_time:.4f} сек ({percentage:.1f}%)")


def solve_task():
    """Обробляє введення матриці та запускає алгоритми."""
    print_header("Розв'язання задачі розподілу")
    print("Оберіть спосіб введення матриці:")
    print("1 - Ручне введення")
    print("2 - Випадкова генерація")
    print("3 - Зчитування з файлу input.txt")
    print("0 - Повернутися до головного меню")
    choice = logged_input("Ваш вибір: ").strip()

    input_methods = {
        "1": input_manual,
        "2": input_random,
        "3": input_from_file,
    }

    if choice == "0":
        return
    if choice not in input_methods:
        print(format_text("Невірний вибір способу введення.", Colors.ERROR))
        return

    result = input_methods[choice]()
    if result is None:
        return

    m, n, matrix = result
    run_algorithms(m, n, matrix)
    print(format_text("\nРозв'язання завершено.", Colors.SUCCESS))


def run_experiments():
    """Виконує обраний експеримент."""
    print_header("Проведення експериментів")
    print("Оберіть експеримент:")
    print("1 - Вплив кількості ітерацій Двоетапного алгоритму на точність і час")
    print("2 - Залежність цільової функції від різниці max та min вартості")
    print("3 - Залежність часу виконання від розмірності матриці")
    print("4 - Залежність точності від розмірності матриці")
    print("0 - Повернутися до головного меню")
    choice = logged_input("Ваш вибір: ").strip()

    experiment_mapping = {
        "1": (experiments.experiment_3_4_1_1, "experiment_plots/experiment_3_4_1.png"),
        "2": (experiments.experiment_3_4_2, "experiment_plots/experiment_3_4_2.png"),
        "3": (
            experiments.experiment_3_4_3_1,
            "experiment_plots/experiment_3_4_3_1.png",
        ),
        "4": (
            experiments.experiment_3_4_3_2,
            "experiment_plots/experiment_3_4_3_2.png",
        ),
    }

    if choice == "0":
        return
    if choice not in experiment_mapping:
        print(format_text("Невірний вибір експерименту.", Colors.ERROR))
        return

    print_subheader(f"Запуск експерименту {choice}")
    func, plot_file = experiment_mapping[choice]
    try:
        start_time = time.time()
        func()
        end_time = time.time()

        experiment_time = end_time - start_time

        print(
            format_text(
                f"\nЕксперимент завершено. Графік збережено у {plot_file}",
                Colors.SUCCESS,
            )
        )
        print_timing_info("експерименту", experiment_time)

    except Exception as e:
        print(format_text(f"Помилка під час експерименту: {e}", Colors.ERROR))


def main():
    """Головна функція програми."""
    # Перенаправляємо stdout/stderr у Logger, щоб усе писалося і в консоль, і в result_output.txt
    sys.stdout = Logger("result_output.txt")
    sys.stderr = sys.stdout

    try:
        print_header("Розподіл земельних ділянок між 4 забудовниками")
        while True:
            print("\nГоловне меню:")
            print("1 - Розв'язати задачу")
            print("2 - Провести експерименти")
            print("0 - Вийти")
            choice = logged_input("Ваш вибір: ").strip()
            if choice == "0":
                print(format_text("Вихід з програми.", Colors.SUCCESS))
                break
            elif choice == "1":
                solve_task()
            elif choice == "2":
                run_experiments()
            else:
                print(format_text("Невірний вибір, спробуйте ще раз.", Colors.ERROR))
    finally:
        sys.stdout.close()


if __name__ == "__main__":
    main()
