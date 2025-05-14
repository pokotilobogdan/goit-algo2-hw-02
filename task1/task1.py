import random
from classes import *
from colorama import Fore


# Генеруємо окреме завдання для принтера
def create_printer_job(id: str, volume: float = None, priority: int = None, print_time: int = None, productivity : float = None) -> PrintJob:

    job = PrintJob(id=id)

    if not volume:
        min_volume = 0.01
        max_volume = 100
        volume = random.uniform(min_volume, max_volume)
    job.volume = round(volume, 2)
    
    if not priority:
        priority = random.choice([1, 2, 3])
    job.priority = priority
    
    if not print_time:
        min_time = 1
        max_time = 10
        print_time = random.randint(min_time, max_time)
    job.time = print_time
    
    job.calculate_job_productivity()

    return job

# Генеруємо список завдань для принтера
def generate_jobs(number: int):
    jobs = []
    for i in range(number):
        jobs.append(create_printer_job(id=f"M{i}"))
    
    return jobs

# def calculate_productivity(job_list):
#     t_group = reduce(max, [job.print_time for job in job_list])           # завдання з найдовшим часом задає час роботи над всією групою
#     V_sum = reduce(lambda x, y: x + y, [job.volume for job in job_list])    # рахуємо загальний об'єм роботи
#     return V_sum / t_group

# Функція перераховує продуктивність, якщо до існуючої групи додати нове завдання
def calculate_new_productivity(job_group: JobGroup, new_job: PrintJob):
    if job_group.t_group >= new_job.time:
        # Знаменник дробу не змінюється, бо час для групи залишається тим самим,
        # тому просто додаємо продуктивність нового завдання всередині групи (об'єм додаткової роботи / час для групи)
        return job_group.productivity + new_job.volume / job_group.t_group
    else:
        # Якщо час для групи збільшився, а саме став рівним часу для нового завдання, то треба поділити сумарну роботу на новий час
        return (job_group.V_sum + new_job.volume) / new_job.time


def optimize_printing(job_list, printer_constraints: PrinterConstraints):
    '''
    Функція приймає на вхід список завдань для прінтера, та власне обмеження самого прінтера.
    Повертає групу робіт, що виконуються одночасно та (щонайменш локально) оптимізованим чином.

    Жадібний алгоритм, тому кожен раз обираємо найоптимальніший локально варіант.
    
    Якість вибору групи завдань будемо оцінювати через кількість роботи за час:
    До групи будемо додавати те завдання, котре дає максимальне значення нового відношення робота/час для всієї групи.
    '''
    job_group = JobGroup(t_group=0, V_sum=0, productivity=float('-inf'))

    # Поки можливо та поки обмеження принтера дозволяють, будемо обирати з завдань з найвищим пріоритетом.
    # Як тільки залишкові завдання в, наприклад, першому пріоритеті не влазять в прінтер, будемо підбирати найкращий
    # варіант з наступного пріоритета.

    # Для цього доцільно буде розділити завдання на списки по пріоритетах
    first_priority = filter(lambda job: job.priority == 1, job_list)
    second_priority = filter(lambda job: job.priority == 2, job_list)
    third_priority = filter(lambda job: job.priority == 3, job_list)

    # Впорядочимо ці списки за спаданням затребуваної потужності. Так буде зручніше далі проходити по спискам.
    # Це ніби необов'язково для даної задачі, проте логічним здається виконати якомога більше роботи за виокремлений час.
    first_priority = sorted(first_priority, key=lambda job: job.productivity, reverse=True)
    second_priority = sorted(second_priority, key=lambda job: job.productivity, reverse=True)
    third_priority = sorted(third_priority, key=lambda job: job.productivity, reverse=True)

    # Об'єднаємо ці списки в один. Таким чином код буде простіше, і при цьому порядок проходження по завданнях не зміниться
    # (Тут змінили входящий список in-place ось таким цікавим чином)
    job_list[:] = [job for job in first_priority + second_priority + third_priority]

    left_volume = printer_constraints.max_volume

    # Починаємо додавати завдання до групи, враховуючи обмеження ресурсів прінтера:

    curr_index = 0

    # Якщо ресурси прінтера закінчаться, припиняємо додавати нові завдання
    while len(job_group.members) < printer_constraints.max_items and left_volume > 0:

        flag = 1

        # Проходимось по вже впорядоченому за пріоритетами та затребуваними потужностями списку завдань
        for i in range(curr_index, len(job_list)):
            # Якщо місця в прінтері вистачає - додаємо завдання в JobGroup
            if job_list[i].volume <= left_volume:
                job_group.members.append(job_list[i])
                left_volume -= job_list[i].volume
                curr_index = i

                # Позначаємо, що відбулось додавання завдання до групи
                flag = 0

                break
        if flag:
            # Якщо жодне з завдань не додалось - завершуємо пошук для даної групи
            return job_group

        # Видаляємо завдання зі списку, щоб більше його не повторювати
        # На місце цього завдання стане наступне, котре ми ще не перевіряли, тому for й починається з curr_index
        job_list.pop(curr_index)

    return job_group


if __name__ == "__main__":
    jobs = generate_jobs(10)

    # Виведемо гарним чином на екран згенеровані роботи (в даному випадку не треба буде дивитись на рядок Summary - то для фінального результату)
    job_group = JobGroup()

    for job in jobs:
        job_group.members.append(job)

    print(Fore.YELLOW + "Згенеровані завдання:" + Fore.RESET)
    print(job_group)
    print()

    # Тепер введемо обмеження на ресурси принтера та виконаємо групування через жадібний алгоритм
    max_items = 3
    max_volume = 100
    printer_constraints = PrinterConstraints(max_volume=max_volume, max_items=max_items)

    counter = 1

    while len(jobs) > 0:
        print(Fore.YELLOW + f"Група завдань {counter}:" + Fore.RESET)
        counter += 1
        print(optimize_printing(jobs, printer_constraints))
        print()




    
