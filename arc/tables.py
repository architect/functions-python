import os
import boto3

from . import reflect

def name(tablename):
    """Get generated DynamoDB table name.

    Keyword arguments:
    tablename -- the name defined in .arc
    """
    if os.environ.get('NODE_ENV') == 'testing':
        db = boto3.client('dynamodb', endpoint_url='http://localhost:5000')
        res = db.list_tables()['TableNames']
        tidy = [tbl for tbl in res if tbl != 'arc-sessions']
        stage = [tbl for tbl in tidy if 'production' not in tbl]
        name = [tbl for tbl in stage if tablename in tbl]
        if len(name) == 0:
            raise NameError('tablename "' + tablename + '" not found') 
        else:
            return name[0]
    else:
        arc = reflect()
        return arc['tables'][tablename]

def table(tablename):
    """Get a DynamoDB.Table client for given table name.

    Keyword arguments:
    tablename -- the name defined in .arc

    Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#table
    """
    if os.environ.get('NODE_ENV') == 'testing':
        db = boto3.resource('dynamodb', endpoint_url='http://localhost:5000')
        return db.Table(name(tablename))
    else:
        db = boto3.resource('dynamodb')
        return db.Table(name(tablename))
