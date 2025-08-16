# Write a list comprehension that generates squares of all even numbers from 1 to 20.
squares_of_evens = [x**2 for x in range(1, 21) if x % 2 == 0]
print(squares_of_evens)

# Using a set comprehension, extract unique vowels from the string "assessment".
unique_vowels = set()
unique_vowels = {char for char in "assessment" if char in 'aeiou' and char not in unique_vowels}
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

