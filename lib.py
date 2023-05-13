def simple_hash(s, range_size):
    # Compute the sum of ASCII values of the characters in the string
    ascii_sum = sum(ord(c) for c in s)
    # Take the modulo of the sum with the size of the range
    return ascii_sum % range_size
