# Step 1: Build the graph and calculate indegrees
def build_graph_and_indegrees(rows):
    graph = {}
    indegree = {}
    for row in rows:
        current_holder = row["Current Holder"]
        new_holder = row["New Holder"]

        # Initialize graph and indegree for current and new holders
        if current_holder not in graph:
            graph[current_holder] = []
        if new_holder not in graph:
            graph[new_holder] = []

        # Add edge from current_holder to new_holder
        graph[current_holder].append(new_holder)
        indegree[new_holder] = indegree.get(new_holder, 0) + 1
        if current_holder not in indegree:
            indegree[current_holder] = 0

    return graph, indegree

# Step 2: Perform topological sorting
def topological_sort(graph, indegree):
    queue = [node for node in graph if indegree[node] == 0]
    sorted_order = []
    while queue:
        node = queue.pop(0)
        sorted_order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    return sorted_order

# Step 3: Reorder rows based on topological sort
def reorder_rows(rows, sorted_order):
    ordered_seats_sorted = []
    visited_indices = set()

    for node in sorted_order:
        for idx, row in enumerate(rows):
            if row["Current Holder"] == node and idx not in visited_indices:
                ordered_seats_sorted.append(row)
                visited_indices.add(idx)
                # Ensure the row with the player's name in the new holder appears directly after
                for dep_idx, dependent_row in enumerate(rows):
                    if dependent_row["Current Holder"] == row["New Holder"] and dep_idx not in visited_indices:
                        ordered_seats_sorted.append(dependent_row)
                        visited_indices.add(dep_idx)
    return ordered_seats_sorted

# Step 4: Ensure the correct order for specific cases
def ensure_correct_order(ordered_seats):
    special_values = ["DROP", "X", "KL Raffle", "ANY RCA", "Fairy Alt"]

    # Separate rows with special values (except those in dependency chains)
    special_rows = []
    regular_rows = []
    for row in ordered_seats:
        if row["New Holder"] in special_values:
            # Check if this row is part of a dependency chain
            is_dependency = any(
                dep_row["New Holder"] == row["Current Holder"]
                for dep_row in ordered_seats
            )
            if not is_dependency:
                special_rows.append(row)
            else:
                regular_rows.append(row)
        else:
            regular_rows.append(row)

    # Combine regular rows and special rows
    return regular_rows + special_rows

# Step 5: Cycle detection
def detect_cycles(graph):
    def dfs(node, visited, stack):
        visited.add(node)
        stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, visited, stack):
                    return True
            elif neighbor in stack:
                return True
        stack.remove(node)
        return False

    visited = set()
    for node in graph:
        if node not in visited:
            if dfs(node, visited, set()):
                return True
    return False