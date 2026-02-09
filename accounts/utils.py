import hashlib

def hash_pin(pin):
    if pin is None:
        return None
    return hashlib.sha256(str(pin).encode()).hexdigest()


def verify_pin(stored_hash, entered_pin):
    # if user didn't type PIN
    if not entered_pin:
        return False

    entered_hash = hashlib.sha256(str(entered_pin).encode()).hexdigest()
    return stored_hash == entered_hash
