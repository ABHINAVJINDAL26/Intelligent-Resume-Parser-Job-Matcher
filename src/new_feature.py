"""Small incremental feature file used to produce 10 commits."""

def feature_part_1():
    """Part 1: return greeting."""
    return "Feature part 1: greeting"

def feature_part_2():
    """Part 2: return a short status."""
    return "Feature part 2: status OK"

def feature_part_3(x):
    """Part 3: simple transformer - multiply by 2."""
    return x * 2

def feature_part_4(items):
    """Part 4: return list length."""
    return len(items)

def feature_part_5(text):
    """Part 5: return lowercase of text."""
    return text.lower()

def feature_part_6(nums):
    """Part 6: return sum of numbers."""
    return sum(nums)

def feature_part_7(d):
    """Part 7: get keys of dict as list."""
    return list(d.keys())

def feature_part_8(a, b):
    """Part 8: return concatenation of two strings."""
    return f"{a}{b}"

def feature_part_9(n):
    """Part 9: return whether number is even."""
    return (n % 2) == 0

def feature_part_10():
    """Part 10: a small summary of available parts."""
    return [
        "part_1", "part_2", "part_3", "part_4", "part_5",
        "part_6", "part_7", "part_8", "part_9"
    ]

