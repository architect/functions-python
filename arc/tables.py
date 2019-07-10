import os
import boto3

from . import reflect

def name(tablename):
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
