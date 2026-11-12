def check_key(user_input, secret_key):
    if len(user_input) != len(secret_key):
        return False
    
    for x, y in zip(user_input, secret_key):
        if x != y:
            return False # Early exit
            
    return True