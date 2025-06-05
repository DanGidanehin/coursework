import os
import time
import matplotlib.pyplot as plt

from helper_functions import generate_random_matrix
from greedy import greedy_allocation
from two_stage import two_stage_allocation
from brute_force import brute_force_allocation


def calculate_sums(matrix, regions):
    sums = [0] * 4
    for dev in range(4):
        for i, j in regions[dev]:
            sums[dev] += matrix[i][j]
    return sums


def calculate_objective_value(sums):
    return max(sums) - min(sums)


def get_max_min_difference(matrix):
    return max(map(max, matrix)) - min(map(min, matrix))


def experiment_3_4_1_1():
    iteration_values = list(range(1, 21))  # 1–100 ітерацій
    sizes = list(range(3, 21))  # матриці 3x3 до 10x10
    num_tasks_per_size = 10  # задач на кожен розмір

    avg_objectives = []
    os.makedirs("experiment_plots", exist_ok=True)

    for iterations in iteration_values:
        total_obj = 0
        total_cases = 0
        for size in sizes:
            for _ in range(num_tasks_per_size):
                matrix = generate_random_matrix(size, size, min_val=0, max_val=100)
                regions, _ = two_stage_allocation(matrix, max_iterations=iterations)
                obj_val = calculate_objective_value(calculate_sums(matrix, regions))
                total_obj += obj_val
                total_cases += 1

        average = total_obj / total_cases
        avg_objectives.append(average)
        print(f"  Ітерацій: {iterations:3d} | Δ = {average:.2f}")

    plt.figure()
    plt.plot(iteration_values, avg_objectives, marker="o", markersize=3)
    plt.title("Залежність цільової функції від кількості ітерацій")
    plt.xlabel("Кількість ітерацій")
    plt.ylabel("Середнє значення цільової функції")
    plt.grid(True)
    plt.savefig("experiment_plots/experiment_3_4_1.png")
    plt.close()


def experiment_3_4_2():
    m, n = 5, 5
    num_tasks = 50
    ranges = [
        (0, 10),
        (0, 20),
        (0, 30),
        (0, 40),
        (0, 50),
        (0, 60),
        (0, 70),
        (0, 80),
        (0, 90),
        (0, 100),
    ]
    differences, greedy_vals, two_stage_vals, brute_vals = [], [], [], []

    print("\n3.4.2.1 — Залежність цільової функції від різниці max-min")
    for r_min, r_max in ranges:
        g_sum, t_sum, b_sum, diff_sum = 0, 0, 0, 0
        for _ in range(num_tasks):
            matrix = generate_random_matrix(m, n, r_min, r_max)
            diff_sum += get_max_min_difference(matrix)

            g_r, _ = greedy_allocation(matrix)
            t_r, _ = two_stage_allocation(matrix)
            b_r, _ = brute_force_allocation(matrix)

            g_sum += calculate_objective_value(calculate_sums(matrix, g_r))
            t_sum += calculate_objective_value(calculate_sums(matrix, t_r))
            b_sum += calculate_objective_value(calculate_sums(matrix, b_r))

        differences.append(diff_sum / num_tasks)
        greedy_vals.append(g_sum / num_tasks)
        two_stage_vals.append(t_sum / num_tasks)
        brute_vals.append(b_sum / num_tasks)
        print(
            f"  Δ: {differences[-1]:.2f} | G: {greedy_vals[-1]:.2f}, "
            f"T: {two_stage_vals[-1]:.2f}, B: {brute_vals[-1]:.2f}"
        )

    plt.figure()
    plt.plot(differences, greedy_vals, "o-", label="Жадібний")
    plt.plot(differences, two_stage_vals, "s-", label="Двоетапний")
    plt.plot(differences, brute_vals, "^-", label="Повний перебір")
    plt.title("Цільова функція vs max-min")
    plt.xlabel("Різниця max-min")
    plt.ylabel("Середня цільова функція")
    plt.grid(True)
    plt.legend()
    plt.savefig("experiment_plots/experiment_3_4_2.png")
    plt.close()


def experiment_3_4_3_1():
    sizes = list(range(3, 21))  # 3x3 до 20x20
    num_tasks = 30
    g_times, t_times = [], []

    print("\n3.4.3.1 — Залежність часу від розмірності матриці")
    for size in sizes:
        g_total, t_total = 0, 0
        for _ in range(num_tasks):
            matrix = generate_random_matrix(size, size, 1, 30)

            start = time.time()
            greedy_allocation(matrix)
            g_total += time.time() - start

            start = time.time()
            two_stage_allocation(matrix)
            t_total += time.time() - start

        g_times.append(g_total / num_tasks)
        t_times.append(t_total / num_tasks)
        print(f"  {size}x{size}: G={g_times[-1]:.4f}s, T={t_times[-1]:.4f}s")

    plt.figure()
    plt.plot(sizes, g_times, "o-", label="Жадібний")
    plt.plot(sizes, t_times, "s-", label="Двоетапний")
    plt.title("Час виконання vs розмір матриці")
    plt.xlabel("Розмірність матриці")
    plt.ylabel("Середній час (сек")
    plt.grid(True)
    plt.legend()
    plt.savefig("experiment_plots/experiment_3_4_3_1.png")
    plt.close()


def experiment_3_4_3_2():
    sizes = list(range(3, 21))
    num_tasks = 30
    g_vals, t_vals = [], []

    print("\n3.4.3.2 — Залежність точності від розмірності матриці")
    for size in sizes:
        g_sum, t_sum = 0, 0
        for _ in range(num_tasks):
            matrix = generate_random_matrix(size, size, 1, 30)

            g_r, _ = greedy_allocation(matrix)
            t_r, _ = two_stage_allocation(matrix)

            g_sum += calculate_objective_value(calculate_sums(matrix, g_r))
            t_sum += calculate_objective_value(calculate_sums(matrix, t_r))

        g_vals.append(g_sum / num_tasks)
        t_vals.append(t_sum / num_tasks)
        print(f"  {size}x{size}: G={g_vals[-1]:.2f}, T={t_vals[-1]:.2f}")

    plt.figure()
    plt.plot(sizes, g_vals, "o-", label="Жадібний")
    plt.plot(sizes, t_vals, "s-", label="Двоетапний")
    plt.title("Якість vs розмір матриці")
    plt.xlabel("Розмірність матриці")
    plt.ylabel("Середнє значення цільової функції")
    plt.grid(True)
    plt.legend()
    plt.savefig("experiment_plots/experiment_3_4_3_2.png")
    plt.close()


if __name__ == "__main__":
    experiment_3_4_1_1()
    experiment_3_4_2()
    experiment_3_4_3_1()
    experiment_3_4_3_2()
