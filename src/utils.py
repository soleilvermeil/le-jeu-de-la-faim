import random
from typing import List, Dict, Any, Literal, Tuple
import warnings
import hashlib


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
    n = y
    w = -x
    return f"({n:+}°N {w:+}°W)"


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


def bootstrap(lst: list, iterations: int | Literal["inf"] = "inf") -> Dict[str, Dict[str, float]]:
    """
    Perform a bootstrap analysis on a list. Returns a dictionnary, where the
    keys are the unique elements of the list and the values are also
    dictionnaries with the mean and the standard deviation of the ratios.
    """
    # Caching some values
    len_lst = len(lst)
    unique_lst = unique(lst)

    if iterations == "inf":

        result = {}
        for element in unique_lst:
            exact_mean = lst.count(element) / len_lst
            exact_variance = exact_mean * (1 - exact_mean) / len_lst
            exact_std = exact_variance**0.5
            result[element] = {
                "mean": exact_mean,
                "std": exact_std,
            }
        return result
    
    else:

        # Deprecation warning
        warnings.warn("Using a finite number of iterations is deprecated. Use 'inf' instead for better results and performance.", DeprecationWarning)

        # Define ratios
        sample_ratios = {
            element: [] for element in unique_lst
        }

        for _ in range(iterations):

            # Sample `total_count` elements from `lst` with replacement
            sample = random.choices(lst, k=len_lst)

            # Add ratios to the dictionary
            for element in unique_lst:
                sample_ratios[element].append(sample.count(element) / len_lst)
        
        # Put data in the right format
        result = {
            element: {
                "mean": mean(sample_ratios[element]),
                "std": std(sample_ratios[element]),
            } for element in unique_lst
        }
        
        # Return
        return result


def smart_join(lst: List[str], sep: str = ", ", last_sep: str = " and ") -> str:
    """
    Joins a list of strings with a separator and a last separator.
    """
    if len(lst) == 0:
        return ""
    elif len(lst) == 1:
        return lst[0]
    elif len(lst) == 2:
        return lst[0] + last_sep + lst[1]
    else:
        return sep.join(lst[:-1]) + last_sep + lst[-1]
    

def flatten_dict(dct: dict, sep: str = "_", parent_key: Any = "") -> dict:
    """
    Flattens a dictionary that has nested dictionaries as values.
    For example, if `dct` is:
    ```
    {
        "a": 1,
        "b": {
            "c": 2,
            "d": 3,
        }
    }
    ```
    the flattened dict is going to be:
    ```
    {
        "a": 1,
        "b_c": 2,
        "b_d": 3,
    }
    ```
    """
    items = []
    for key, value in dct.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(dct=value, sep=sep, parent_key=new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


def transform_dict_values(dct: dict, transformations: Tuple[type, callable]) -> dict:
    """
    Transforms the values of a dictionary according to a list of
    transformations. The transformations are tuples where the first element is
    the type of the value and the second element is a function that takes the
    value as input and returns the transformed value.
    """
    new_dct = dct.copy()

    for key, value in new_dct.items():
        for transformation in transformations:
            if isinstance(value, transformation[0]):
                new_dct[key] = transformation[1](value)
    
    return new_dct


def wrap_text(text, width=50):
    """
    Splits the input string into substrings of length <= threshold,
    ensuring splits occur only at spaces to avoid breaking words.

    Args:
        text (str): The input string to wrap.
        threshold (int): The maximum length of each line. Default is 50.

    Returns:
        str: The wrapped text with substrings joined by newlines.
    """
    if width <= 0:
        raise ValueError("Threshold must be greater than 0.")
    
    if "\n" in text:
        return "\n".join(wrap_text(line, width) for line in text.split("\n"))

    words = text.split()  # Split text into words
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)

        # Check if adding the word exceeds the threshold
        if current_length + word_length + len(current_line) >= width:
            lines.append(" ".join(current_line))
            current_line = []
            current_length = 0

        current_line.append(word)
        current_length += word_length

    # Add the last line if it exists
    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


def remove_emojis(text: str) -> str:
    """
    Removes emojis from a string.
    """
    return text.encode('ascii', 'ignore').decode('ascii')


def replace_all(s: str, old_str: str, new_str: str) -> str:
    """
    Replaces all occurrences of a substring in a string.
    """
    assert old_str not in new_str, "The new string should not contain the old string."
    while old_str in s:
        s = s.replace(old_str, new_str)
    return s


def smart_input(
    prompt: str,
    validator: callable,
    error_message: str = "Invalid input. Please try again.",
    default: Any | None = None,
) -> Any:
    
    while True:

        # Get user input
        user_input = input(prompt)

        # Check if default value should be returned
        if not user_input and default is not None:
            return default

        try:
            if validator(user_input):
                return user_input
        except:
            print(error_message)


def str2random(s: str, N: int) -> tuple:
    """
    Generates a reproducible list of N random floats in the range (0, 1) from a
    given string.
    """
    # Hash the string using SHA-256
    hash_object = hashlib.sha256(s.encode())
    hash_digest = hash_object.hexdigest()
    
    # Convert the hash to an integer to use as a seed
    hash_int = int(hash_digest, 16)
    
    # Seed the random number generator
    random.seed(hash_int)
    
    # Generate N random floats in the range (0, 1)
    return tuple([random.random() for _ in range(N)])


def clamp(n: float, min_value: float, max_value: float) -> float:
    """
    Clamps a number between a minimum and a maximum value.
    """
    return max(min(n, max_value), min_value)


def sign(x: float) -> int:
    """
    Returns the sign of a number.
    """
    if x != 0:
        return abs(x) // x
    else:
        return 0