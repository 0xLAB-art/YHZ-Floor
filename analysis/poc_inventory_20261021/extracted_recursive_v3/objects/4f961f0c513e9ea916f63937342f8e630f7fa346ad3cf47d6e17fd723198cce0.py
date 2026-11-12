def check_password(input, secret):
    if len(input) != len(secret):
        return False
    for i in range(len(secret)):
        if input[i] != secret[i]:
            return False  # Early exit!
    return True