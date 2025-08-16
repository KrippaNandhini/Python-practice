# Write a list comprehension that generates squares of all even numbers from 1 to 20.
squares_of_evens = [x**2 for x in range(1, 21) if x % 2 == 0]
print(squares_of_evens)

# Using a set comprehension, extract unique vowels from the string "assessment".
unique_vowels = {char for char in "assessment" if char in 'aeiou'}
print(unique_vowels)

# Write a dictionary comprehension that maps each character in "data" to its ASCII value.
ascii_mapping = {char: ord(char) for char in "data"}
print(ascii_mapping)

# What is the difference between *args and **kwargs in function definitions?
"""*args: packs extra positional args into a tuple.

**kwargs: packs extra keyword args into a dict.

Order in signature: positional, *args, keyword-only, **kwargs."""

# Show how to unpack a, b, *rest, c = [10, 20, 30, 40, 50, 60]. What will rest contain?
a, b, *rest, c = [10, 20, 30, 40, 50, 60]
print(f"a: {a}, b: {b}, rest: {rest}, c: {c}")

# When would you use a dict comprehension instead of looping with .update()? Give a concrete scenario.
"""Use a dict comprehension when you can define the mapping in a single, pure expression—e.g., filter + transform in one pass:"""

temp_dict = {'w1': '  hello ', 'w2': 'world', 'w3': '  python  '}
clean = {k: v.strip() for k, v in temp_dict.items() if v}
print(clean)

"""A loop with .update() is noisier, easier to leak bugs, and often slower."""

# How do starred expressions in assignment differ from in function calls?
"""In assignment, starred expressions unpack iterables into variables. In function calls, they unpack iterables into positional arguments."""

# Why does Python allow only one starred target on the left-hand side of unpacking? (e.g. a, *b, c works but *a, *b, c does not).
"""To avoid ambiguity in unpacking, as multiple starred targets could lead to confusion about which elements belong to which variable. It ensures clarity in the assignment process."""

# Given def f(a, *b, c=10, **d): ..., what arguments go into a, b, c, d if you call f(1,2,3,x=99)?
def f(a, *b, c=10, **d):
    print(f"a: {a}, b: {b}, c: {c}, d: {d}")

f(1, 2, 3, x=99)

# From a list of dicts:
users = [
    {"id": 1, "name": "Alice", "active": True},
    {"id": 2, "name": "Bob", "active": False},
    {"id": 3, "name": "Carol", "active": True}
]
# Use a dict comprehension to map only active users’ IDs to names.
active_users = {user['id']: user['name'] for user in users if user['active']}
print(active_users)

# Given numbers = [3, -1, 5, 0, -7, 8], use a list comprehension to create a list of absolute values, but only for negatives.
numbers = [3, -1, 5, 0, -7, 8]
absolute_negatives = [abs(x) for x in numbers if x < 0]
print(absolute_negatives)

# You receive CSV rows as tuples:
rows = [("id", "name", "age"), (1,"A",20), (2,"B",25)]
# Unpack to separate header and data using extended unpacking.
header, *data = rows
print(f"Header: {header}") 
print(f"Data: {data}")

# Write a comprehension that generates all (i, j) coordinate pairs where i < j, for i, j in [1,2,3,4].
coordinate_pairs = [(i, j) for i in range(1, 5) for j in range(1, 5) if i < j]
print(coordinate_pairs)

# Use *args to write a function multiply_all that multiplies any number of arguments together.
def multiply_all(*args):
    result = 1
    for num in args:
        result *= num
    return result

print(multiply_all(2, 3, 4))

# Write a function print_user(**kwargs) that prints keys/values neatly. Call it with print_user(id=1, name="Neo", role="Admin")
def print_user(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")
print_user(id=1, name="Neo", role="Admin")

# Given nested list [[1,2],[3,4],[5,6]], flatten it using a comprehension.
nested_list = [[1, 2], [3, 4], [5, 6]]
flattened = [item for sublist in nested_list for item in sublist]
print(flattened)

# Using unpacking, split nums = [1,2,3,4,5] into head, *middle, tail.
nums = [1, 2, 3, 4, 5]
head, *middle, tail = nums
print(f"Head: {head}, Middle: {middle}, Tail: {tail}")

# Compare memory footprint: list comprehension vs generator expression. Which is better for streaming 10M rows?
import sys
def list_comprehension():
    return [x for x in range(10000000)]
def generator_expression():
    return (x for x in range(10000000))
list_comp = list_comprehension()
gen_exp = generator_expression()
print(f"List comprehension size: {sys.getsizeof(list_comp)} bytes") #89095160 bytes
print(f"Generator expression size: {sys.getsizeof(gen_exp)} bytes") #192 bytes
# Generator expressions are better for memory efficiency when streaming large datasets, as they yield items one at a time without storing the entire list in memory.

# Someone used set([x for x in nums]) instead of {x for x in nums}. Any difference? Why might one be slower?
nums = [1, 2, 3, 4, 5]
set_comprehension = {x for x in nums}
set_conversion = set([x for x in nums])
print(f"Set comprehension: {set_comprehension}")
print(f"Set conversion: {set_conversion}")
# The set comprehension is generally faster because it directly constructs the set without creating an intermediate list, while the set conversion first creates a list and then converts it to a set, which adds overhead.
# The comprehension is more efficient in terms of both time and space complexity.

# Is there ever a readability trade-off between using comprehensions and for-loops? Give a rule of thumb you’d apply in production code.
def readability_tradeoff():
    """Use comprehensions for simple transformations or filters. For complex logic, prefer for-loops."""
    # Example of a simple comprehension
    squares = [x**2 for x in range(10)]
    
    # Example of a complex logic that is clearer with a for-loop
    result = []
    for x in range(10):
        if x % 2 == 0:
            result.append(x**2)
        else:
            result.append(x**3)
    
    return squares, result
readability_squares, readability_result = readability_tradeoff()
print(f"Readability squares: {readability_squares}")
print(f"Readability result: {readability_result}")
# The rule of thumb is to use comprehensions for simple, readable transformations and filters, while for-loops should be used for more complex logic that requires multiple steps or conditions, as they enhance clarity and maintainability in production code.

# Build a function filter_dict that takes a dict and a condition function, and returns a filtered dict using comprehension.
def filter_dict(data, condition):
    return {k: v for k, v in data.items() if condition(k, v)}

def is_active_user(key, value):
    return value.get('active', False)

data = {'user1': {'active': True, 'name': 'Alice'},
    'user2': {'active': False, 'name': 'Bob'},
    'user3': {'active': True, 'name': 'Charlie'}}
filtered_data = filter_dict(data, is_active_user)
print(filtered_data)

# Given log lines:
logs = ["INFO: start", "ERROR: disk full", "INFO: ok", "ERROR: mem leak"]
# Use comprehension to group logs by level into a dict:
"""{
  "INFO": ["start","ok"],
  "ERROR": ["disk full","mem leak"]
}"""
log_dict = {}
for log in logs:
    level, message = log.split(": ")
    if level not in log_dict:
        log_dict[level] = []
    log_dict[level].append(message)
log_dict = {level: [message.strip() for message in messages] for level, messages in log_dict.items()}
print(log_dict)

### END OF FILE ###