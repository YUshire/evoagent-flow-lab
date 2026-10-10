import json

def parse_value(value):
    """Parse an untrusted JSON request value."""
    return json.loads(value)
