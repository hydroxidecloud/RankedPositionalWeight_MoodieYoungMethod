# Ranked Positional Weights Method
import csv
import numpy as np


class Task:
    def __init__(self, id, name, time, predecessors=None, successors=None, chain_successors=None, rpw=None):
        self.id = id
        self.name = name
        self.time = time
        self.predecessors = predecessors
        self.successors = successors
        self.chain_successors = chain_successors
        self.rpw = rpw


def read_tasks_from_csv(csv_file):
    # read csv，set id, name, time, predecessors of every single task, generate tasks
    tasks = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            task_id = int(row[0])
            task_name = row[1]
            task_time = int(row[2])
            predecessors = [int(predecessor) for predecessor in row[3].split(';')] if row[3] else []
            task = Task(task_id, task_name, task_time, predecessors)
            tasks.append(task)
    return tasks


def find_successors(non_successors_tasks):
    # find following successors，set the succesors of every task in tasks
    tasks = non_successors_tasks
    for object_task in tasks:
        temp_successors = []
        for observed_task in tasks:
            if object_task.id in observed_task.predecessors:
                temp_successors.append(observed_task.id)
                # print(object_task.id, observed_task.id)
        object_task.successors = temp_successors


def find_chain_successors(with_successors_tasks):
    # find all the successors on the chain，set chain successors of every task in tasks（inclunding self）
    def find_object_chain_successors(with_successors_tasks, id):
        # find the chain sussessors of a specific task, set chain successors of this task（including self）
        object_task = next((obj for obj in with_successors_tasks if obj.id == id), None)
        if object_task:
            def dfs(node, chain_successors):
                chain_successors.append(node.id)
                for child in node.successors:
                    dfs(next((task for task in with_successors_tasks if task.id == child), None), chain_successors)

            chain_successors = []
            dfs(object_task, chain_successors)
            object_task.chain_successors = chain_successors

    for task in with_successors_tasks:
        find_object_chain_successors(with_successors_tasks, task.id)


def write_rpw(with_chain_successors_tasks):
    # calculate and set rpw of every task in tasks
    def calculate_object_rpw(with_chain_successors_tasks, id):
        # calculate the rpw of a specific task and return it
        object_task = next((obj for obj in with_chain_successors_tasks if obj.id == id), None)
        object_rpw = 0
        for observed_id in object_task.chain_successors:
            observed_task = next((obj for obj in with_chain_successors_tasks if obj.id == observed_id), None)
            object_rpw = object_rpw + observed_task.time
        return object_rpw

    for task in with_chain_successors_tasks:
        task.rpw = calculate_object_rpw(with_chain_successors_tasks, task.id)


def calculate_station_time(stations, j):
    # calculate station j's time
    station_time = 0
    for task in stations[j - 1]:
        station_time = station_time + task.time
    return station_time


def calculate_balance_rate(stations):
    stations_time = []
    for station_number in range(1, len(stations) + 1):
        stations_time.append(calculate_station_time(stations, station_number))
    actual_beat = max(stations_time)
    station_quantity = len(stations) + 1
    eta = np.sum(np.array(stations_time)) / (actual_beat * station_quantity)
    return eta


def calculate_smoothing_index(stations):
    stations_time = []
    for station_number in range(1, len(stations) + 1):
        stations_time.append(calculate_station_time(stations, station_number))
    time_max = max(stations_time)
    stations_time_delta = np.array(stations_time) - time_max
    SI = np.sqrt(np.sum(np.square(stations_time_delta)))
    return SI



def print_final_result(stations):
    if len(stations[-1]) == 0:
        stations.pop()
    stations_time = []
    for station_number in range(1, len(stations) + 1):
        stations_time.append(calculate_station_time(stations, station_number))
    print("Programming to implement the hierarchical position weight method, solve the assembly line balance problem, and get the following results.")
    print("The Number of stations is", len(stations))
    for index, station in enumerate(stations):
        print("Station", index + 1, "operates task", [(task.id, task.name) for task in station])
    print("The time of the stations are", stations_time)
    print()


if __name__ == "__main__":
    beat = 54

    tasks = read_tasks_from_csv('tasks.csv')
    find_successors(tasks)
    find_chain_successors(tasks)
    write_rpw(tasks)

    # for t in tasks:
    #     print(t.id, t.time, t.chain_successors, t.rpw)
    # # print(calculate_object_rpw(tasks, 27)
    # print()

    sorted_tasks = sorted(tasks, key=lambda task: task.rpw, reverse=True)
    arranged_tasks = []

    # for t in sorted_tasks:
    #     print(t.id, t.rpw)

    j = 1
    stations = []

    while len(arranged_tasks) < len(tasks):
        stations.append([])
        pending_tasks = [task for task in sorted_tasks if task not in arranged_tasks]
        for object_task in pending_tasks:
            if (calculate_station_time(stations, j) + object_task.time <= beat and
                    set(object_task.predecessors).issubset(set([task.id for task in arranged_tasks]))):
                arranged_tasks.append(object_task)
                stations[j - 1].append(object_task)
                # print_final_result(stations)
        j = j + 1
        # print(len(arranged_tasks))
    # print(j)

    print_final_result(stations)

    # stations_time = []
    # for station_number in range(1, len(stations) + 1):
    #     stations_time.append(calculate_station_time(stations, station_number))
    # print(stations_time)

    print("Balance Rate eta =", calculate_balance_rate(stations))
    print("Smoothing Index SI =", calculate_smoothing_index(stations))
