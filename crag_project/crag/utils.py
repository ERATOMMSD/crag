import os.path
import random as ra
import subprocess


def has_m_match(array, other_arrays, m):
    """Checks if array and any one of other_arrays have at least
    m number of same elements"""
    for other_array in other_arrays:
        count = 0
        for i in range(len(array)):
            if other_array[i] == array[i]:
                count += 1
            if count >= m:
                return True
    return False


def get_fullpath(filename):
    """Given a filename with a local path, this method returns
    the global filepath of the file."""
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, filename)


def call_command(command):
    """Calls a given shell command and returns the output string."""
    return subprocess.getoutput(command).strip()


def line_index(text, begin_str):
    """Returns the index of line that starts with begin_str,
    if there is such a line. Otherwise returns -1."""
    for index, line in enumerate(text.split("\n")):
        if line.startswith(begin_str):
            return index
    return -1


def divide_and_sample(min_value, max_value, n, i):
    """Divide the interval [min_value, max_value) to n smaller intervals
       and sample a uniformly distributed random number from the ith
       subinterval
    """
    size = (max_value - min_value) / n
    return min_value + ra.uniform(i * size, (i + 1) * size)


def update_average(average_dict, key_list, new_value):
    """This method provides a mechanism to aggregate fitness values
    (by averaging) for multiple roads generated with the same configuration."""
    key_tuple = tuple(key_list)
    if key_tuple in average_dict:
        old_average, n = average_dict[key_tuple]
        new_average = (old_average * n + new_value) / (n + 1)
        average_dict[key_tuple] = (new_average, n + 1)
        return new_average
    else:
        average_dict[key_tuple] = (new_value, 1)
        return new_value


def update_minimum(minimum_dict, key_list, new_value):
    """This method provides a mechanism to aggregate fitness values
    (by taking minimum) for multiple roads generated with the same configuration."""
    key_tuple = tuple(key_list)
    if key_tuple in minimum_dict:
        old_minimum, n = minimum_dict[key_tuple]
        new_minimum = min([old_minimum, new_value])
        minimum_dict[key_tuple] = (new_minimum, n + 1)
        return new_minimum
    else:
        minimum_dict[key_tuple] = (new_value, 1)
        return new_value


def update_first(first_dict, key_list, new_value):
    """This method provides a mechanism to aggregate fitness values
    (by locking in the first value) for multiple roads generated with the same
    configuration."""
    key_tuple = tuple(key_list)
    if key_tuple in first_dict:
        return first_dict[key_tuple][0]
    else:
        first_dict[key_tuple] = (new_value, 1)
        return new_value


def take_best(lst, fun, best_size):
    """Given a list of numeric values lst, a function fun, and a size
    constant best_size, this function sorts the list of values lst based
    on the value that they generate when they are passed to the function fun.
    Then the top best_size of the sorted list is returned."""
    size = len(lst)
    return [lst[j] for j in sorted(list(range(size)), key=fun)[:best_size]]
