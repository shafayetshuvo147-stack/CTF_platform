"""
Dynamic scoring calculation: a challenge's effective point value decreases as
more distinct users solve it, matching HackTheBox / CTFd dynamic scoring curves.
"""

MIN_POINTS_FLOOR_RATIO = 0.3  # Points never decay below 30% of base value
DECAY_PER_SOLVE = 0.03        # Each solve reduces value by 3% of initial base


def effective_points(base_points: int, solve_count: int) -> int:
    """
    Calculates current points for a challenge given the number of solves.
    """
    if solve_count <= 1:
        return base_points
    floor = max(10, int(base_points * MIN_POINTS_FLOOR_RATIO))
    decayed = int(base_points * (1.0 - DECAY_PER_SOLVE * (solve_count - 1)))
    return max(floor, min(base_points, decayed))

