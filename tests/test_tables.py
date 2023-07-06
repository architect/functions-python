# # -*- coding: utf-8 -*-
import arc.tables


def test_tables(arc_reflection, ddb_client):
    tablename = "noises"
    ddb_client.create_table(
        TableName=tablename,
        KeySchema=[{"AttributeName": "foo", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "foo", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    tables = ddb_client.list_tables()
    arc_reflection(params={f"tables/{tablename}": tables["TableNames"][0]})

    val = arc.tables.name(tablename=tablename)
    assert val == tables["TableNames"][0]

    tbl = arc.tables.table(tablename=tablename)
    assert str(tbl.__class__) == "<class 'boto3.resources.factory.dynamodb.Table'>"
