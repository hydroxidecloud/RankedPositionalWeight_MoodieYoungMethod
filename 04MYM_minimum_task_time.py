# 莫迪和杨法 元素分配阶段优先选择任务时间最小
import csv
import numpy as np


class Task:
    def __init__(self, id, name, time, predecessors=None, successors=None, chain_successors=None, rpw=None,
                 temp_predecessors=None):
        self.id = id
        self.name = name
        self.time = time
        self.predecessors = predecessors
        self.successors = successors
        self.chain_successors = chain_successors
        self.rpw = rpw
        # temp_predecessors是莫迪和杨法中的变量，初始值与predecessors一致，期间逐渐置为[]。predecessors设定后保持只读
        self.temp_predecessors = temp_predecessors


def read_tasks_from_csv(csv_file):
    # 读取csv，设定每个task的基本属性id, name, time, predecessors，得到列表tasks
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
    # 找到紧接的后置任务，设定tasks中每个task的紧接后置任务
    tasks = non_successors_tasks
    for object_task in tasks:
        temp_successors = []
        for observed_task in tasks:
            if object_task.id in observed_task.predecessors:
                temp_successors.append(observed_task.id)
                # print(object_task.id, observed_task.id)
        object_task.successors = temp_successors


def find_chain_successors(with_successors_tasks):
    # 找到后续链上的所有后置任务，设定tasks中每个task的链后置任务（包括自身）
    def find_object_chain_successors(with_successors_tasks, id):
        # 找到一个指定任务的链后置任务，设定该task的链后置任务（包括自身）
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
    # 计算tasks中每个task的rpw，设定tasks中每个task的rpw
    def calculate_object_rpw(with_chain_successors_tasks, id):
        # 计算一个指定任务的rpw，并返回值
        object_task = next((obj for obj in with_chain_successors_tasks if obj.id == id), None)
        object_rpw = 0
        for observed_id in object_task.chain_successors:
            observed_task = next((obj for obj in with_chain_successors_tasks if obj.id == observed_id), None)
            object_rpw = object_rpw + observed_task.time
        return object_rpw

    for task in with_chain_successors_tasks:
        task.rpw = calculate_object_rpw(with_chain_successors_tasks, task.id)


def duplicate_predecessors(non_temp_predecessors_tasks):
    for task in non_temp_predecessors_tasks:
        task.temp_predecessors = task.predecessors


def calculate_station_time(stations, j):
    # 计算工位j的时间
    station_time = 0
    for task in stations[j - 1]:
        station_time = station_time + task.time
    return station_time


def check_task_order_validity(stations, j, object_task):
    # 对于即将在工位j上分配的任务object_task，判断紧前任务是否在工位j及之前已存在
    # previous_j_tasks_id是工位j及之前工位上已分配任务id的列表
    previous_j_tasks_id = []
    for station_number in range(1, j + 1):
        # print(j)
        # print(station_number)
        previous_j_tasks_id = previous_j_tasks_id + [task.id for task in stations[station_number - 1]]
    # print(previous_j_tasks_id)
    validity = set(object_task.predecessors).issubset(set(previous_j_tasks_id))
    # print(validity)
    return validity


def check_task_redeploy_validity(stations, j, object_task):
    # 对于已经完成分配的stations，任务object_task如果改置于工位j，判断链后置任务是否都在工位j及之后
    # subsequent_j_tasks_id是工位j及之后工位上已分配任务id的列表
    subsequent_j_tasks_id = []
    for station_number in range(len(stations), j - 1, -1):
        # print(j)
        # print(station_number)
        subsequent_j_tasks_id = subsequent_j_tasks_id + [task.id for task in stations[station_number - 1]]
    validity = set(object_task.chain_successors).issubset(set(subsequent_j_tasks_id))
    # print(validity)
    return validity


def print_final_result(stations):
    if len(stations[-1]) == 0:
        stations.pop()
    stations_time = []
    for station_number in range(1, len(stations) + 1):
        stations_time.append(calculate_station_time(stations, station_number))
    print("编程实现莫迪和杨法（优先选择任务时间最小），解决装配线平衡问题，得到以下结果")
    print("工位的数量是", len(stations))
    for index, station in enumerate(stations):
        print("工位", index + 1, "上进行的任务有", [(task.id, task.name) for task in station])
    print("每个工位的时间分别是", stations_time)
    print()


def find_transfer(stations, time_max, j_max, time_min, j_min, g):
    for object_task in stations[j_max - 1]:
        # print("find_transfer", j_min)
        if (object_task.time < 2 * g
                and check_task_redeploy_validity(stations, j_min, object_task)):
            expected_g = 0.5 * ((time_max - object_task.time) - (time_min + object_task.time))
            # 将transfer操作添加至候选集合，元组中“1”指transfer，expected_g指操作后的原j_max和原j_min工位时间之差的1/2
            candidate_set.add((1, expected_g, object_task, j_max, j_min))
            print("FIND: transfer", object_task.id, "from", j_max, "to", j_min)


def find_trade(stations, time_max, j_max, time_min, j_min, g):
    for object1_task in stations[j_max - 1]:
        # print("j_max:", j_max, "object_task.id：", object1_task.id, "full-ids:",
        #       [task.id for task in stations[j_max - 1]])
        for object2_task in stations[j_min - 1]:
            if (object1_task.time < 2 * g
                    and object2_task.time < 2 * g
                    and check_task_redeploy_validity(stations, j_min, object1_task)
                    and check_task_redeploy_validity(stations, j_max, object2_task)):
                expected_g = ((time_max - object1_task.time + object2_task.time)
                              - (time_min + object1_task.time - object2_task.time))
                # 将trade操作添加至候选集合，元组中“2”指trade，expected_g指操作后的原j_max和原j_min工位时间之差的1/2
                candidate_set.add((2, expected_g, object1_task, j_max, object2_task, j_min))
                print("FIND: trade", object1_task.id, "in", j_max, "and", object2_task.id, "in", j_min)


def select_command(candidate_set):
    if not candidate_set:
        return None
    return min(candidate_set, key=lambda command: command[1])


def execute_transfer(original_stations, command_transfer):
    original_stations[command_transfer[3] - 1].remove(command_transfer[2])
    original_stations[command_transfer[4] - 1].append(command_transfer[2])


def execute_trade(original_stations, command_trade):
    original_stations[command_trade[3] - 1].remove(command_trade[2])
    original_stations[command_trade[5] - 1].append(command_trade[2])
    original_stations[command_trade[5] - 1].remove(command_trade[4])
    original_stations[command_trade[3] - 1].append(command_trade[4])


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


if __name__ == "__main__":
    beat = 54

    tasks = read_tasks_from_csv('tasks.csv')
    find_successors(tasks)
    find_chain_successors(tasks)
    # write_rpw(tasks)
    duplicate_predecessors(tasks)

    # sorted_tasks = sorted(tasks, key=lambda task: task.rpw, reverse=True)
    arranged_tasks = []

    stations = [[]]

    # 作业元素分配阶段
    while len(arranged_tasks) < len(tasks):
        j = 1

        # 得到pending_tasks（按任务时间从小到大排序的无前置任务的本轮待分配任务列表）
        non_predecessors_tasks = [task for task in tasks if len(task.temp_predecessors) == 0]
        sorted_non_predecessors_tasks = sorted(non_predecessors_tasks, key=lambda task: task.time, reverse=False)
        pending_tasks = [task for task in sorted_non_predecessors_tasks if task not in arranged_tasks]
        object_task = pending_tasks[0]

        # 分配任务。如果待分配任务未分配，则保持循环
        while True:
            if len(stations[-1]) >= 1:
                stations.append([])
            if (calculate_station_time(stations, j) + object_task.time <= beat and
                    check_task_order_validity(stations, j, object_task)):
                # 如果添加了本任务，与原有任务时间之和不超过节拍；对于即将在工位j上分配的任务object_task，判断紧前任务是否在工位j及之前已存在
                arranged_tasks.append(object_task)
                # print("obj", object_task.id)
                stations[j - 1].append(object_task)
                break
            j = j + 1
            # print("arranged_tasks", len(arranged_tasks))

        # 更新tasks，将已分配作业的id从每个任务的temp_predecessors中移除
        arranged_tasks_id = [task.id for task in arranged_tasks]
        for object_task in tasks:
            object_task.temp_predecessors = [id for id in object_task.temp_predecessors if id not in arranged_tasks_id]

    # print("arranged_tasks", len(arranged_tasks))
    # print("tasks", len(tasks))

    # 去除可能存在的未安排任务的空工位
    if len(stations[-1]) == 0:
        stations.pop()

    # 输出未进行Trade and transfer的结果
    # print("未进行Trade and transfer：")
    # print_final_result(stations)
    # print()

    # Trade and transfer阶段
    while True:
        stations_time = []
        for station_number in range(1, len(stations) + 1):
            stations_time.append(calculate_station_time(stations, station_number))
        # print(stations_time)

        time_max = max(stations_time)
        j_max = stations_time.index(max(stations_time)) + 1
        time_min = min(stations_time)
        j_min = stations_time.index(min(stations_time)) + 1
        # print(time_max, j_max, time_min, j_min)
        g = 0.5 * (time_max - time_min)

        # 清空候选集合
        candidate_set = set()

        # 找到transfer和trade的可行操作，生成操作元组，并加入候选集合
        find_transfer(stations, time_max, j_max, time_min, j_min, g)
        find_trade(stations, time_max, j_max, time_min, j_min, g)
        # print(candidate_set)

        # 候选集合为空，则退出
        if len(candidate_set) == 0:
            break

        # print(select_command(candidate_set))

        if select_command(candidate_set)[0] == 1:
            print("EXECUTE: transfer", select_command(candidate_set)[2].id,
                  "from", select_command(candidate_set)[3], "to", select_command(candidate_set)[4])
            execute_transfer(stations, select_command(candidate_set))
        elif select_command(candidate_set)[0] == 2:
            print("EXECUTE: trade", select_command(candidate_set)[2].id, "in", select_command(candidate_set)[3],
                  "and", select_command(candidate_set)[4].id, "in", select_command(candidate_set)[5])
            execute_trade(stations, select_command(candidate_set))

        print_final_result(stations)
        candidate_set = set()

    # 输出已进行Trade and transfer的最终结果
    print("已进行Trade and transfer：")
    print_final_result(stations)

    print("平衡率eta =", calculate_balance_rate(stations))
    print("平滑指数SI =", calculate_smoothing_index(stations))
