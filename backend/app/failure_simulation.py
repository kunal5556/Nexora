ALLOWED_SIMULATED_STATUSES = {429, 500, 502, 503}


def parse_simulation_header(header_value, key_ids):
    if not header_value:
        return {}

    wildcard_status = None
    explicit_statuses = {}
    for pair in header_value.split(","):
        if "=" not in pair:
            continue
        key_id, status_text = (part.strip() for part in pair.split("=", 1))
        if not status_text.isdigit() or int(status_text) not in ALLOWED_SIMULATED_STATUSES:
            continue
        if key_id == "*":
            wildcard_status = int(status_text)
        elif key_id in key_ids:
            explicit_statuses[key_id] = int(status_text)

    simulated_failures = {}
    for key_id in key_ids:
        status = explicit_statuses.get(key_id, wildcard_status)
        if status:
            simulated_failures[key_id] = status
    return simulated_failures
