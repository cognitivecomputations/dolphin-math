import uuid

DELIM = "|"  # Use standard vertical bar delimiter

def step(op, x="", y="", z="", o=""):
    """Formats a step into a delimited string."""
    parts = [op, str(x), str(y), str(z), str(o)]
    while parts and parts[-1] == "":  # trim empties
        parts.pop()
    return DELIM.join(parts)

def jid() -> str:
    """Generates a unique job ID."""
    return str(uuid.uuid4())
