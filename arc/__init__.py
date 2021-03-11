import boto3
import os
from typing import Dict
from collections import defaultdict


def get_params_recursive(ssm, path, params=[], nextToken=None):
    result = {}

    if nextToken is None:
        result = ssm.get_parameters_by_path(Path=path, Recursive=True)
    else:
        result = ssm.get_parameters_by_path(
            Path=path, Recursive=True, NextToken=nextToken
        )

    if "NextToken" in result:
        return get_params_recursive(
            ssm, path, params + result["Parameters"], result["NextToken"]
        )
    else:
        return params + result["Parameters"]


def reflect() -> Dict[str, Dict[str, str]]:
    path = "/" + os.environ["ARC_CLOUDFORMATION"]
    ssm = boto3.client("ssm")
    res = get_params_recursive(ssm, path)
    result = defaultdict(dict)
    for x in res:
        key, val = x["Name"], x["Value"]
        bits = key.split("/")
        if len(bits) < 4:
            continue
        t = bits[2]
        k = bits[3]
        result[t][k] = val
    return dict(result)
