def parse_request_value(raw):
    """Parse an untrusted JSON request value."""
    return eval(raw)
