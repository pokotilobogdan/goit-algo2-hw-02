from typing import List, Dict
from functools import reduce
from copy import deepcopy
from pprint import pprint
from colorama import Fore


class SmartDict(dict):
    '''
    Is able to add dictionaries via keys without modifying self
    '''
    def __add__(self, other):
        result = SmartDict(deepcopy(self))
        for key, value in other.items():
            if key in result:
                if isinstance(result[key], (int, float)) and isinstance(value, (int, float)):
                    result[key] += value
                elif isinstance(result[key], list) and isinstance(value, list):
                    result[key] += deepcopy(value)
                else:
                    raise TypeError(f"Unsupported types for key '{key}': {type(result[key])}, {type(value)}")
            else:
                result[key] = deepcopy(value)
        return result

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)


def cut_once(length: int | list):
    '''
    Повертає всі можливі унікальні комбінації довжин після одного розрізу.
    
    Приклад:
    4 -> [1, 3], [2, 2] ([3, 1] вже не треба повертати)
    [2, 3] -> [1, 1, 3], [1, 2, 2]
    '''
    if isinstance(length, int):
        
        if length == 1:
            return [1,]
        
        i = 1
        result = []

        while i <= length/2:
            result.append([i, length-i])
            i += 1
        return result
    elif isinstance(length, list):
        result = []
        for elem in length:
            if elem == 1:
                continue
            for cut in cut_once(elem):
                arr_to_add = sorted(length[:length.index(elem)] + length[length.index(elem) + 1:] + cut)
                if arr_to_add not in result:
                    result.append(arr_to_add)    
        return result

def optimum(length: int | list, prices: List[int], memo_table: List[SmartDict]) -> SmartDict:
    '''
    Тут знаходимо, яка комбінація розрізів та відповідна ціна оптимальні для палки довжини length.

    Якщо коротко, то ця функція порівнює вартість цілої палки з вартістю, яка належатиме палці після одного розрізу.
    Також тут використовується функція cut_once, що приймає в якості аргумента довжину або ж набор довжин, і повертає всі можливі
    унікальні комбінації довжин після додаткового розрізу.

    Окремо для зручності я використав клас SmartDict, об'єкти котрого при операції додавання повертають словник з тими ж самими ключами,
    значення котрих є сумою відповідних значень двох словників.
    Припускається, що значення в словниках між собою додаються. А саме, працюємо з int та list значеннями.
    '''

    # Якщо результат задачі вже є в таблиці - беремо відповідь звідти
    if isinstance(length, int) and memo_table[length-1]['price'] is not None:
        return memo_table[length-1]

    # В разі відсутності результату - починаємо розглядати окремі випадки

    # Якщо довжина дорівнює 1, то різати немає куди. Відповідь - оптимумом є ціна палки як вона є
    if length == 1:
        memo_table[length-1]['price'] = prices[0]
        memo_table[length-1]['cuts'] = [1,]

        return memo_table[length-1]
    
    # Обробляємо випадок, коли аргументом є список довжин

    # Якщо список складається з однієї довжини, то повертаємо оптимум для цієї довжини 
    if isinstance(length, list) and len(length) == 1:
        return optimum(length[0], prices, memo_table)
    # Якщо ж список вже складається з декількох довжин, то оптимумом буде сума оптимумів для кожного з елементів
    elif isinstance(length, list):
        return reduce(lambda x, y: x+y, [optimum(elem, prices, memo_table) for elem in length])
    
    # Дійшли до випадку, коли length це просто число, що не дорівнює 1

    # Порівняємо ціну цілої палки довжиною length, та ціну всіх інших її конфігурацій розрізів.
    # Оптимумом буде те, що має більшу ціну

    # Зручніше спочатку знайти оптимум для всіх можливих розрізів 
    opt = max([optimum(cut, prices, memo_table) for cut in cut_once(length)], key=lambda x: (x['price'], -len(x['cuts'])))

    # І тепер порівнюємо нерозрізаний шматок з найоптимальніших з розрізаного
    if opt['price'] > prices[length-1]:
        memo_table[length-1] = opt
    else:
        memo_table[length-1] = SmartDict({'price': prices[length-1], 'cuts': [length,]})
    
    return memo_table[length-1]


def rod_cutting_memo(length: int, prices: List[int]) -> Dict:
    """
    Знаходить оптимальний спосіб розрізання через мемоізацію

    Args:
        length: довжина стрижня
        prices: список цін, де prices[i] — ціна стрижня довжини i+1

    Returns:
        Dict з максимальним прибутком та списком розрізів
    """
    
    # list comprehension для створення незалежних instances класу (це я для себе)
    memo_table = [SmartDict({'price': None, 'cuts': None}) for _ in range(length)]
    
    # Весь функціонал в optimum. Тут я лише створюю мемо-таблицю, що використовується для вирішення задачі
    result = optimum(length, prices, memo_table)
    pprint(memo_table)
    return result


def rod_cutting_table(length: int, prices: List[int]) -> Dict:
    """
    Знаходить оптимальний спосіб розрізання через табуляцію

    Args:
        length: довжина стрижня
        prices: список цін, де prices[i] — ціна стрижня довжини i+1

    Returns:
        Dict з максимальним прибутком та списком розрізів
    """
    
    tab_table = []

    for part_length in range(1, length+1):
        # Here to build a table
        if part_length == 1:
            opt = SmartDict({'price': prices[0], 'cuts': [1,]})
        else:
            # Порівнюємо що вигідніше: різати палку, або ж ні

            # Визначимо спочатку нерозрізану палку як оптимальну конфігурацію, і з цим будемо порівнювати
            opt = SmartDict({'price': prices[part_length-1], 'cuts': [part_length,]})

            # Тепер перевіряємо вартість розрізаної палки
            for cut in cut_once(part_length):   # Набори довжин типу [1, 1, 3]
                
                total_price = 0

                # Рахуємо сумарну вартість конкретної розрізаної палки, користуючись даними з таблиці,
                # що вже містить найкращі прибутки з палок довжинами менше
                for small_rod_length in cut:
                    total_price += tab_table[small_rod_length-1]['price']

                # Оптимальний розріз для даної довжини:
                opt_cut = reduce(lambda x, y: x+y, [tab_table[elem-1]['cuts'] for elem in cut])

                # Якщо ціни рівні, але якась конфігурація потребує менше розрізів - обираємо ту, де менше розрізів
                if total_price == opt['price'] and len(opt['cuts']) > len(opt_cut):
                    opt['cuts'] = cut

                # Якщо ж отримана ціна вище за оптимальну, то ця конфігурація стає оптимальною
                elif total_price > opt['price']:
                    opt['price'] = total_price
                    opt['cuts'] = opt_cut

        # Нарешті додаємо оптимальний результат в таблицю
        tab_table.append(opt)

    # print(tab_table)

    return tab_table[-1]


def run_tests():
    """Функція для запуску всіх тестів"""
    test_cases = [
        # Тест 1: Базовий випадок
        {
            "length": 5,
            "prices": [2, 5, 7, 8, 10],
            "name": "Базовий випадок"
        },
        # Тест 2: Оптимально не різати
        {
            "length": 3,
            "prices": [1, 3, 8],
            "name": "Оптимально не різати"
        },
        # Тест 3: Всі розрізи по 1
        {
            "length": 4,
            "prices": [3, 5, 6, 7],
            "name": "Рівномірні розрізи"
        },
        # Тест 4: Щось випадкове
        {
            "length": 8,
            "prices": [3, 5, 7, 11, 15, 17, 21, 23],
            "name": "Рівномірні розрізи"
        }
    ]

    for test in test_cases:
        length = test['length']
        prices = test['prices']
        
        print(Fore.MAGENTA + f"\nТест: {test['name']}")
        print(Fore.YELLOW + f"Довжина стрижня: {length}")
        print(Fore.YELLOW + f"Ціни: {prices}" + Fore.RESET)

        # Тестуємо мемоізацію
        print(Fore.BLUE + 'memo table:' + Fore.RESET)   # виводиться на екран всередині самої функції
        print(Fore.GREEN + 'Result:', rod_cutting_memo(length, prices), Fore.RESET)

        # Тестуємо табуляцію
        table_result = rod_cutting_table(test['length'], test['prices'])
        print(Fore.BLUE + "\nРезультат табуляції:" + Fore.RESET)
        print(f"Максимальний прибуток: {table_result['price']}")
        print(f"Розрізи: {table_result['cuts']}")

        print("-----------------------------------------------------")

    print("\nПеревірка пройшла успішно!\n")


if __name__ == "__main__":
    run_tests()
