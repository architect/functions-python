import os
import re

non_local_envs = ["staging", "production"]


def use_aws():
    env = os.environ.get("ARC_ENV")
    is_local = os.environ.get("ARC_LOCAL")
    in_sandbox = os.environ.get("ARC_SANDBOX")

    # Testing is always local
    if env == "testing":
        return False

    # Local, but using AWS resources
    if env in non_local_envs and in_sandbox and not is_local:
        return False

    # Assumed to be AWS
    return True


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
