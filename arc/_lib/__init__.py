import json
import os
import re
import arc


def get_ports():
    sandbox = os.environ.get("ARC_SANDBOX")
    not_found = TypeError("Sandbox internal port not found")
    # Sandbox env var is the happy path for Lambda runs
    if sandbox:
        sandbox_config = json.loads(sandbox)
        if not sandbox_config.get("ports"):
            raise not_found
        return sandbox_config["ports"]
    # Fall back to an internal SSM query in case Functions is running as a bare module
    else:
        services = arc.services()
        if not services.get("ARC_SANDBOX", {}).get("ports"):
            raise not_found
        ports = json.loads(services["ARC_SANDBOX"]["ports"])
        return ports


def to_logical_id(string):
    string = re.sub(r"([A-Z])", r" \1", string)
    if len(string) == 1:
        return string.upper()
    string = re.sub(r"^[\W_]+|[\W_]+$", "", string).lower()
    string = string[0].upper() + string[1:]
    string = re.sub(r"[\W_]+(\w|$)", lambda m: m.group(1).upper(), string)
    if string == "Get":
        return "GetIndex"
    return string


def use_aws():
    env = os.environ.get("ARC_ENV")
    is_local = os.environ.get("ARC_LOCAL")
    in_sandbox = os.environ.get("ARC_SANDBOX")
    non_local_envs = ["staging", "production"]

    # Testing is always local
    if env == "testing":
        return False

    # Local, but using AWS resources
    if env in non_local_envs and in_sandbox and not is_local:
        return False

    # Assumed to be AWS
    return True


def get_session_table():
    return os.environ.get(
        "ARC_SESSION_TABLE_NAME", os.environ.get("SESSION_TABLE_NAME")
    )
