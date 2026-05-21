import random
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class Zone:
    def __init__(self, i, x, y, a, b, w):
        self.id = i
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.w = w

    def cross(self, o):
        if (self.x >= o.x + o.a or
                self.x + self.a <= o.x or
                self.y >= o.y + o.b or
                self.y + self.b <= o.y):
            return False
        return True


class App:
    def __init__(self, A=100, B=100):
        self.A = A
        self.B = B
        self.zones = []

    def cnt_cross(self):
        m = 0
        n = len(self.zones)
        for i in range(n):
            for j in range(i + 1, n):
                if self.zones[i].cross(self.zones[j]):
                    m += 1
        return m

    def verify_no_cross(self, selected_ids=None):
        zones_to_check = self.zones
        if selected_ids is not None:
            zones_to_check = [z for z in self.zones if z.id in selected_ids]
        n = len(zones_to_check)
        if n == 0:
            print("Немає зон для перевірки.")
            return
        print(f"\n--- Детальна перевірка перетинів ({n} зон) ---")
        conflict_found = False
        for i in range(n):
            for j in range(i + 1, n):
                z1 = zones_to_check[i]
                z2 = zones_to_check[j]
                if z1.cross(z2):
                    print(f"[ПОМИЛКА] Зона {z1.id} (x:{z1.x}, y:{z1.y}, a:{z1.a}, b:{z1.b}) "
                          f"ПЕРЕТИНАЄТЬСЯ із Зоною {z2.id} (x:{z2.x}, y:{z2.y}, a:{z2.a}, b:{z2.b})!")
                    conflict_found = True

        if not conflict_found:
            print("[УСПІХ] Жодного перетину не виявлено! Всі зони розміщені коректно.")
            print(f"Загальна кількість перевірених унікальних пар: {n * (n - 1) // 2}")
        print("---------------------------------------------")

    # ОНОВЛЕНО: додано параметр selected_ids для фільтрації зон при малюванні
    def plot_zones(self, title="Розміщення зон на площині", selected_ids=None):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlim(0, self.A)
        ax.set_ylim(0, self.B)

        # Відбираємо зони для малювання
        zones_to_plot = self.zones
        if selected_ids is not None:
            zones_to_plot = [z for z in self.zones if z.id in selected_ids]

        for z in zones_to_plot:
            rect = patches.Rectangle((z.x, z.y), z.a, z.b, linewidth=1.5, edgecolor='blue', facecolor='lightblue',
                                     alpha=0.5)
            ax.add_patch(rect)
            ax.text(z.x + z.a / 2, z.y + z.b / 2, str(z.id), color='black', ha='center', va='center', fontweight='bold')

        plt.title(title)
        plt.xlabel("Довжина (X)")
        plt.ylabel("Ширина (Y)")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.show()

    def del_cross(self, t_m, a_n, a_v, b_n, b_v, w_n, w_v):
        m = self.cnt_cross()
        iters = 0
        while m > t_m and iters < 100:
            for _ in range(m - t_m):
                i = random.randint(0, len(self.zones) - 1)
                self.zones[i].a = min(random.randint(a_n, a_v), self.A)
                self.zones[i].b = min(random.randint(b_n, b_v), self.B)
                self.zones[i].w = random.randint(w_n, w_v)
                self.zones[i].x = random.randint(0, max(0, self.A - self.zones[i].a))
                self.zones[i].y = random.randint(0, max(0, self.B - self.zones[i].b))
            m = self.cnt_cross()
            iters += 1

    def add_cross(self, t_m, a_n, a_v, b_n, b_v, w_n, w_v):
        m = self.cnt_cross()
        iters = 0
        while m < t_m and iters < 100:
            for _ in range(t_m - m):
                i = random.randint(0, len(self.zones) - 1)
                self.zones[i].a = min(random.randint(a_n, a_v), self.A)
                self.zones[i].b = min(random.randint(b_n, b_v), self.B)
                self.zones[i].w = random.randint(w_n, w_v)
                self.zones[i].x = random.randint(0, max(0, self.A - self.zones[i].a))
                self.zones[i].y = random.randint(0, max(0, self.B - self.zones[i].b))
            m = self.cnt_cross()
            iters += 1

    def gen_rand(self, n, t_m=0, a_n=5, a_v=20, b_n=5, b_v=20, w_n=10, w_v=50):
        self.zones = []
        for i in range(1, n + 1):
            a = min(random.randint(a_n, a_v), self.A)
            b = min(random.randint(b_n, b_v), self.B)
            x = random.randint(0, max(0, self.A - a))
            y = random.randint(0, max(0, self.B - b))
            w = random.randint(w_n, w_v)
            self.zones.append(Zone(i, x, y, a, b, w))

        self.del_cross(t_m, a_n, a_v, b_n, b_v, w_n, w_v)
        self.add_cross(t_m, a_n, a_v, b_n, b_v, w_n, w_v)

    def load(self, fn):
        self.zones = []
        try:
            with open(fn, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.A, self.B = map(int, lines[0].strip().split())
                for i, line in enumerate(lines[1:], 1):
                    x, y, a, b, w = map(int, line.strip().split())
                    self.zones.append(Zone(i, x, y, a, b, w))
            return True
        except:
            return False


def greedy(app):
    sz = sorted(app.zones, key=lambda z: z.w, reverse=True)
    res = []
    tw = 0
    for cz in sz:
        conf = False
        for s in res:
            if cz.cross(s):
                conf = True
                break
        if not conf:
            res.append(cz)
            tw += cz.w
    return [z.id for z in res], tw


def genetic(app, p_sz=50, m_g=100, p_m=0.1, show_steps=False):
    n = len(app.zones)
    if n == 0: return [], 0

    c_m = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if app.zones[i].cross(app.zones[j]):
                c_m[i][j] = True
                c_m[j][i] = True

    def rep(ind):
        for i in range(n):
            if ind[i] == 1:
                for j in range(i + 1, n):
                    if ind[j] == 1 and c_m[i][j]:
                        if app.zones[i].w >= app.zones[j].w:
                            ind[j] = 0
                        else:
                            ind[i] = 0
        return ind

    def fit(ind):
        return sum(app.zones[i].w for i in range(n) if ind[i] == 1)

    pop = [rep([random.choice([0, 1]) for _ in range(n)]) for _ in range(p_sz)]
    b_ind, b_fit = None, -1

    for gen in range(m_g):
        improved = False
        for ind in pop:
            f = fit(ind)
            if f > b_fit:
                b_fit = f
                b_ind = list(ind)
                improved = True

        if show_steps and improved:
            print(f"   [ГА] Покоління {gen + 1}: нове краще значення ЦФ = {b_fit}")

        n_pop = []
        for _ in range(p_sz):
            i1, i2 = random.sample(range(p_sz), 2)
            n_pop.append(list(pop[i1] if fit(pop[i1]) > fit(pop[i2]) else pop[i2]))

        for ind in n_pop:
            for i in range(n):
                if random.random() < p_m:
                    ind[i] = 1 - ind[i]
            rep(ind)
        pop = n_pop

    return [app.zones[i].id for i in range(n) if b_ind[i] == 1], b_fit


def exp_max_gen(app):
    print("\nЗапуск експерименту: Вплив maxGen...")
    mg_vals = [10, 20, 30, 40, 50]
    print("Генерація тестових наборів...")
    test_apps = []
    for _ in range(20):
        p = App(app.A, app.B)
        p.gen_rand(20, t_m=10)
        test_apps.append(p)

    res = []
    for mg in mg_vals:
        f_sum = 0
        for p in test_apps:
            _, f = genetic(p, p_sz=20, m_g=mg)
            f_sum += f
        res.append(f_sum / len(test_apps))

    plt.plot(mg_vals, res, marker='o')
    plt.title("Вплив maxGen")
    plt.xlabel("maxGen")
    plt.ylabel("Середнє значення ЦФ")
    plt.grid()
    plt.show()


def exp_pop_size(app):
    print("\nЗапуск експерименту: Вплив popSize...")
    ps_vals = [10, 20, 30, 40, 50]

    print("Генерація тестових наборів...")
    test_apps = []
    for _ in range(20):
        p = App(app.A, app.B)
        p.gen_rand(20, t_m=10)
        test_apps.append(p)

    res = []
    for ps in ps_vals:
        f_sum = 0
        for p in test_apps:
            _, f = genetic(p, p_sz=ps, m_g=30)
            f_sum += f
        res.append(f_sum / len(test_apps))

    plt.plot(ps_vals, res, marker='o', color='orange')
    plt.title("Вплив popSize")
    plt.xlabel("popSize")
    plt.ylabel("Середнє значення ЦФ")
    plt.grid()
    plt.show()


def exp_compare(app):
    print("\nНалаштування порівняльного експерименту:")
    min_n = int(input("Мін n: ") or 10)
    max_n = int(input("Макс n: ") or 100)
    step = int(input("Крок: ") or 10)
    n_vals = list(range(min_n, max_n + 1, step))
    t_gr, t_gn, errs = [], [], []

    print("Проведення розрахунків, зачекайте...")
    for n in n_vals:
        tg_s = tgn_s = err_s = 0
        for _ in range(20):
            p = App(app.A, app.B)
            p.gen_rand(n, t_m=n // 2)

            s1 = time.time()
            _, wg = greedy(p)
            tg_s += time.time() - s1

            s2 = time.time()
            _, wgn = genetic(p, p_sz=20, m_g=20)
            tgn_s += time.time() - s2

            m_w = max(wg, wgn)
            err_s += abs(wg - wgn) / m_w * 100 if m_w > 0 else 0

        t_gr.append(tg_s / 20)
        t_gn.append(tgn_s / 20)
        errs.append(err_s / 20)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    a1.plot(n_vals, t_gr, label='Жадібний')
    a1.plot(n_vals, t_gn, label='Генетичний')
    a1.set_title("Час виконання")
    a1.set_xlabel("Кількість зон (n)")
    a1.set_ylabel("Час (сек)")
    a1.legend()
    a1.grid()

    a2.plot(n_vals, errs, color='red', label='Похибка (%)')
    a2.set_title("Відносна похибка ЖА відносно ГА")
    a2.set_xlabel("Кількість зон (n)")
    a2.set_ylabel("Похибка (%)")
    a2.legend()
    a2.grid()
    plt.show()


def main():
    app = App(A=16, B=10)
    last_res = {}

    while True:
        st = "Немає даних" if not app.zones else "Задача задана"
        print(f"\n--- Головне меню ({st}) ---")
        print("1 - Введення даних задачі")
        print("2 - Розв'язати задачу всіма алгоритмами")
        print("3 - Провести експерименти")
        print("4 - Вивести дані задачі")
        print("5 - Вивести розв'язки задачі")
        print("6 - Візуалізувати зони на площині")
        print("7 - Детальна перевірка перетинів (Логи)")
        print("0 - Завершити роботу")

        ch = input("Вибір: ")

        if ch == '1':
            print("\n1. Самостійно\n2. З файлу\n3. Випадково")
            s_ch = input("Вибір: ")

            if s_ch == '1':
                app.A = int(input("Довжина (A): "))
                app.B = int(input("Ширина (B): "))
                n = int(input("Кількість зон (n): "))
                app.zones = []
                for i in range(1, n + 1):
                    x = int(input(f"Зона {i} X: "))
                    y = int(input(f"Зона {i} Y: "))
                    a = int(input(f"Зона {i} Довжина: "))
                    b = int(input(f"Зона {i} Висота: "))
                    w = int(input(f"Зона {i} Вага: "))
                    app.zones.append(Zone(i, x, y, a, b, w))
            elif s_ch == '2':
                fn = input("Файл: ")
                app.load(fn)
            elif s_ch == '3':
                app.A = int(input("Довжина (A): "))
                app.B = int(input("Ширина (B): "))
                n = int(input("Кількість (n): "))
                m = int(input("Перетинів (m): "))

                a_n = int(input("Нижня межа довжини зон (a_н) [5]: ") or 5)
                a_v = int(input("Верхня межа довжини зон (a_в) [20]: ") or 20)
                b_n = int(input("Нижня межа висоти зон (b_н) [5]: ") or 5)
                b_v = int(input("Верхня межа висоти зон (b_в) [20]: ") or 20)
                w_n = int(input("Нижня межа ваги зон (w_н) [10]: ") or 10)
                w_v = int(input("Верхня межа ваги зон (w_в) [50]: ") or 50)

                app.gen_rand(n, t_m=m, a_n=a_n, a_v=a_v, b_n=b_n, b_v=b_v, w_n=w_n, w_v=w_v)

        elif ch == '2':
            if not app.zones: continue
            print("\n--- Жадібний алгоритм ---")
            gr_ids, gr_w = greedy(app)
            print(f"Результат ЖА: {gr_ids}, ЦФ: {gr_w}")

            print("\n--- Генетичний алгоритм (покроковий пошук) ---")
            gn_ids, gn_w = genetic(app, show_steps=True)
            print(f"Результат ГА: {gn_ids}, ЦФ: {gn_w}")

            last_res = {'gr': (gr_ids, gr_w), 'gn': (gn_ids, gn_w)}

        elif ch == '3':
            print("\n1 - maxGen\n2 - popSize\n3 - Порівняння")
            e_ch = input("Вибір: ")

            if e_ch == '1':
                exp_max_gen(app)
            elif e_ch == '2':
                exp_pop_size(app)
            elif e_ch == '3':
                exp_compare(app)

        elif ch == '4':
            if not app.zones: continue
            for z in app.zones:
                print(f"[{z.id}] X:{z.x} Y:{z.y} A:{z.a} B:{z.b} W:{z.w}")

        elif ch == '5':
            if last_res:
                print(f"Жад: {last_res['gr'][0]} | {last_res['gr'][1]}")
                print(f"Ген: {last_res['gn'][0]} | {last_res['gn'][1]}")

        # ОНОВЛЕНО: Тепер пункт 6 має підменю, як і пункт 7
        elif ch == '6':
            if not app.zones:
                print("Спочатку згенеруйте або завантажте зони!")
                continue

            print("\n1. Візуалізувати ВСІ згенеровані зони (початкові дані)")
            print("2. Візуалізувати розв'язок Жадібного алгоритму")
            print("3. Візуалізувати розв'язок Генетичного алгоритму")
            vis_ch = input("Вибір: ")

            if vis_ch == '1':
                app.plot_zones(title="Всі згенеровані зони")
            elif vis_ch == '2':
                if 'gr' in last_res:
                    app.plot_zones(title="Розв'язок Жадібного алгоритму", selected_ids=last_res['gr'][0])
                else:
                    print("Спочатку запустіть алгоритми (Пункт 2)!")
            elif vis_ch == '3':
                if 'gn' in last_res:
                    app.plot_zones(title="Розв'язок Генетичного алгоритму", selected_ids=last_res['gn'][0])
                else:
                    print("Спочатку запустіть алгоритми (Пункт 2)!")

        elif ch == '7':
            if not app.zones:
                print("Спочатку згенеруйте або завантажте зони!")
                continue

            print("\n1. Перевірити ВСІ згенеровані зони (початкові дані)")
            print("2. Перевірити розв'язок Жадібного алгоритму")
            print("3. Перевірити розв'язок Генетичного алгоритму")
            chk_ch = input("Вибір: ")

            if chk_ch == '1':
                app.verify_no_cross()
            elif chk_ch == '2':
                if 'gr' in last_res:
                    print("Перевірка зон, що ввійшли у розв'язок Жадібного алгоритму:")
                    app.verify_no_cross(last_res['gr'][0])
                else:
                    print("Спочатку запустіть алгоритми (Пункт 2)!")
            elif chk_ch == '3':
                if 'gn' in last_res:
                    print("Перевірка зон, що ввійшли у розв'язок Генетичного алгоритму:")
                    app.verify_no_cross(last_res['gn'][0])
                else:
                    print("Спочатку запустіть алгоритми (Пункт 2)!")
        elif ch == '0':
            break


if __name__ == "__main__":
    main()