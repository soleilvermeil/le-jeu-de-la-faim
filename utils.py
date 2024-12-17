import random
from typing import List, Dict


def map_range(x, x1, x2, y1, y2):
    """
    Maps a value from one range to another.
    """
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)


def random_bool(probability: float) -> bool:
    """
    Returns True with the given probability.
    """
    return random.random() < probability


def progress_bar(
    label: str,
    value: int,
    max_value: int,
    bar_length: int = 10,
    show_percentage: bool = False,
    end: str = "\n",
) -> str:
    """
    Returns a progress bar as a string.
    """
    slots_filled = int(bar_length * value / max_value)
    slots_empty = bar_length - slots_filled
    bar = "=" * slots_filled + " " * slots_empty
    if show_percentage:
        return f"{label}: [{bar}] {value/max_value:>4.0%}" + end
    else:
        return f"{label}: [{bar}] {value}/{max_value}" + end


def coords(x: int | tuple, y: int = None) -> str:
    """
    Returns a string representation of coordinates.
    """
    if y is None:
        x, y = x
    return f"({y:+}°N {x:+}°W)"



def unique(lst: list) -> list:
    """
    Return a list with unique elements.
    """
    return list(set(lst))


def mean(lst: list) -> float:
    """
    Returns the mean of a list.
    """
    return sum(lst) / len(lst)


def std(lst: list) -> float:
    """
    Returns the standard deviation of a list.
    """
    mean = sum(lst) / len(lst)
    return (sum((x - mean)**2 for x in lst) / len(lst))**0.5


def bootstrap(lst: list, iterations: int = 10000) -> Dict[str, Dict[str, float]]:
    """
    Perform a bootstrap analysis on a list. Returns a dictionnary, where the
    keys are the unique elements of the list and the values are also
    dictionnaries with the mean and the standard deviation of the ratios.
    """
    # Define ratios
    ratios = {
        element: [] for element in unique(lst)
    }

    for _ in range(iterations):

        # Sample `total_count` elements from `lst` with replacement
        sample = random.choices(lst, k=len(lst))

        # Add ratios to the dictionary
        for element in unique(lst):
            ratios[element].append(sample.count(element) / len(lst))
    
    # Put data in the right format
    result = {
        element: {
            "mean": mean(ratios[element]),
            "std": std(ratios[element]),
        } for element in unique(lst)
    }
    
    # Return
    return result


# def jackknife(lst: list) -> Dict[str, Dict[str, float]]:
#     """
#     Perform a jackknife analysis on a list. Returns a dictionnary, where the
#     keys are the unique elements of the list and the values are also
#     dictionnaries with the mean and the standard deviation of the ratios.
#     """
#     # Define ratios
#     ratios = {
#         element: [] for element in unique(lst)
#     }

#     for i in range(len(lst)):

#         # Remove element at index `i`
#         sample = lst[:i] + lst[i+1:]

#         # Add ratios to the dictionary
#         for element in unique(lst):
#             ratios[element].append(sample.count(element) / len(lst))
    
#     # Put data in the right format
#     result = {
#         element: {
#             "mean": mean(ratios[element]),
#             "std": std(ratios[element]),
#         } for element in unique(lst)
#     }
    
#     # Return
#     return result


if __name__ == "__main__":
    lst = ["likes"] * 30 + ["dislikes"] * 10 + ["neutral"] * 10
    print(bootstrap(lst))