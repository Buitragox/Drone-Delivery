from hashlib import sha256

def hash_pass(password: str):
    return sha256(password.encode()).hexdigest()