# -*- coding: utf-8 -*-
import os
import sys

import boto3
import pytest
from moto import mock_dynamodb, mock_sns, mock_sqs, mock_ssm


@pytest.fixture(scope="module")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture()
def ssm_client(aws_credentials):
    with mock_ssm():
        yield boto3.client("ssm")


@pytest.fixture()
def sqs_client(aws_credentials):
    with mock_sqs():
        yield boto3.client("sqs")


@pytest.fixture()
def sns_client(aws_credentials):
    with mock_sns():
        yield boto3.client("sns")


@pytest.fixture()
def ddb_client(aws_credentials):
    with mock_dynamodb():
        yield boto3.client("dynamodb")


@pytest.fixture
def arc_reflection(ssm_client):
    os.environ["ARC_CLOUDFORMATION"] = "TestPythonStaging"

    def mock_reflect(params):
        for k, v in params.items():
            ssm_client.put_parameter(
                Name=f"/TestPythonStaging/{k}",
                Description="A test parameter",
                Value=v,
                Type='String',
            )

    return mock_reflect
