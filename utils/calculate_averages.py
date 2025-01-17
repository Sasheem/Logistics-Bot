from math import ceil

def calculate_averages(players_info, headers, suffixes):
    averages = {header: {suffix: 0 for suffix in suffixes} for header in headers}
    for header in headers:
        for suffix in suffixes:
            key = f"{header} ({suffix})"
            values = [float(player.get(key, 0)) for player in players_info]
            if values:
                averages[header][suffix] = ceil(sum(values) / len(values))
    return averages