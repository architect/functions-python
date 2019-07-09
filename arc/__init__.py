import boto3
import os

def reflect():
    path = '/' + os.environ['ARC_CLOUDFORMATION']
    ssm = boto3.client('ssm')
    res = ssm.get_parameters_by_path(Path=path, Recursive=True)
    params = dict((x['Name'], x['Value']) for x in res['Parameters'])
    result = {}
    for key in params:
        bits = key.split('/')
        t = bits[2]
        k = bits[3]
        val = params[key]
        if t not in result:
            result[t] = {}
        result[t][k] = val
    return result
