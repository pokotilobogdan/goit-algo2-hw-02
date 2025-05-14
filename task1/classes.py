from dataclasses import dataclass, field
from functools import reduce
from tabulate import tabulate


# Оголошуємо класи, необхідні для роботи скрипта
@dataclass
class PrintJob:
    id: str = None
    volume: float = None
    priority: int = None
    time: int = None
    productivity: float = None

    def calculate_job_productivity(self):
        self.productivity = self.volume / self.time

    def __str__(self):
        return f'''
                ID: {self.id},
                Priority: {self.priority},
                Volume: {self.volume},
                Time: {self.time},
                Productivity: {self.productivity}
                '''

@dataclass
class PrinterConstraints:
    max_volume: float
    max_items: int

@dataclass
class JobGroup:
    members: list = field(default_factory=list)
    t_group: int = None
    V_sum: float = None
    productivity: float = None

    def calculate_group_time(self) -> int:
        # Завдання з найдовшим часом задає час роботи над всією групою
        self.t_group = reduce(max, [job.time for job in self.members])

    def calculate_sum_work(self) -> float:
        self.V_sum = reduce(lambda x, y: x + y, [job.volume for job in self.members])

    def calculate_group_productivity(self) -> float:
        self.productivity = self.V_sum / self.t_group

    def __str__(self):
        table = []
        headers = [key for key, value in PrintJob.__dict__.items() if not key.startswith('__') and not callable(value)]
        
        for job in self.members:
            table.append([value for key, value in job.__dict__.items() if not key.startswith('__') and not callable(value)])
        
        self.calculate_sum_work()
        self.calculate_group_time()
        self.calculate_group_productivity()
        table.append(["Summary", self.V_sum, None, self.t_group, self.productivity])

        print(tabulate(table, headers=headers, tablefmt="rst"))
        
        return ""


if __name__ == "__main__":
    test_job = PrintJob(id="TEST_JOB1", volume=10, priority=1, time=5)

    print(test_job)

    test_job.calculate_job_productivity()

    print(test_job)

    test_group = JobGroup()

    test_job2 = PrintJob(id="TEST_JOB2", volume=8, priority=1, time=4)
    test_job3 = PrintJob(id="TEST_JOB3", volume=24, priority=2, time=6)

    for job in [test_job, test_job2, test_job3]:
        job.calculate_job_productivity()
        test_group.members.append(job)

    print(test_group.members)
    # print([key for key, value in test_group.__dict__.items() if not key.startswith('__') and not callable(key)])
    print(test_group)

    # print()
    # # pprint(PrintJob.__dict__)
    # # print([key for key, value in PrintJob.__dict__.items()])
    # print({key:value for key, value in PrintJob.__dict__.items() if not key.startswith("__")})

    # for key, value in [(key, value) for key, value in PrintJob.__dict__.items() if not key.startswith("__")]:
    #     print(key, callable(value))