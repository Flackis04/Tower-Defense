local_containers = [
    [(0, 0), (0, 1), (1, 0)],  # 3 containers
    [(1, 1), (2, 0), (2, 1)],  # 3 containers
    [(3, 0), (3, 1), (4, 0)],  # 3 containers
    [(4, 1)]
    ]

inventory = [[False] * len(local_containers[i]) for i in range(2)]
