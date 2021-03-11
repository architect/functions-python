import boto3
import os


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


def reflect():
    path = "/" + os.environ["ARC_CLOUDFORMATION"]
    ssm = boto3.client("ssm")
    res = get_params_recursive(ssm, path)
    params = dict((x["Name"], x["Value"]) for x in res)
    result = {}
    for key in params:
        bits = key.split("/")
        t = bits[2]
        k = bits[3]
        val = params[key]
        if t not in result:
            result[t] = {}
        result[t][k] = val
    return result
