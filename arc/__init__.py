import boto3
import os
from typing import Dict
from collections import defaultdict


def reflect() -> Dict[str, Dict[str, str]]:
    path = "/" + os.environ["ARC_CLOUDFORMATION"]
    ssm = boto3.client("ssm")
    res = ssm.get_parameters_by_path(Path=path, Recursive=True)
    result = defaultdict(dict)
    for x in res["Parameters"]:
        key, val = x["Name"], x["Value"]
        bits = key.split("/")
        if len(bits) < 4:
            continue
        t = bits[2]
        k = bits[3]
        result[t][k] = val
    return dict(result)
