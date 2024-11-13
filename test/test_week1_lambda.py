from src.week1_lambda import lambda_handler
from src.utils import get_rows, get_columns, write_to_s3
from src.connection import db_connection, get_db_creds
from testfixtures import LogCapture
from moto import mock_aws
import json
import boto3
import pytest
import os

@pytest.fixture()
def aws_cred():
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

class TestGetDBCreds:
    def test_correct_keys_in_dict(self):
        creds = get_db_creds()
        keys = list(creds.keys())
        assert 'username' in keys
        assert 'password' in keys
        assert 'host' in keys
        assert 'port' in keys
        assert 'dbname' in keys

    def test_values_are_strings(self):
        creds = get_db_creds()
        for cred in creds:
            assert isinstance(creds[cred], str)

class TestGetRows:
    def test_returns_list(self):
        conn = db_connection()
        assert isinstance(get_rows(conn, "staff"), list)

    def test_contains_lists(self):
        conn = db_connection()
        result = get_rows(conn, "staff")
        for row in result:
            assert isinstance(row, list)

    def test_correct_no_of_columns(self):
        conn = db_connection()
        result = get_rows(conn, "staff")
        for row in result:
            assert len(row) == 7

class TestGetColumns:
    def test_returns_list(self):
        conn = db_connection()
        assert isinstance(get_columns(conn, "staff"), list)

    def test_correct_no_of_columns(self):
        conn = db_connection()
        result = get_columns(conn, "staff")
        assert len(result) == 7

class TestLogger:
    def test_token_logger(self):
        with LogCapture() as l:
            lambda_handler([],{})
            l.check_present(('root', 'ERROR', 'Houston, we have a major problem'))

class TestWriteToS3:
    @mock_aws
    def test_returns_dict(self):
        s3 = boto3.resource('s3')
        data = json.dumps({'test':'data'})
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket', CreateBucketConfiguration={
        'LocationConstraint': 'eu-west-2'})
        assert isinstance(write_to_s3(s3, 'test-bucket', 'test-file', 'csv', data), dict)

    @mock_aws
    def test_writes_file(self):
        s3 = boto3.resource('s3')
        data = json.dumps({'test':'data'})
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket', CreateBucketConfiguration={
        'LocationConstraint': 'eu-west-2'})
        output = write_to_s3(s3, 'test-bucket', 'test-file', 'csv', data)
        objects = client.list_objects(Bucket='test-bucket')
        assert objects['Contents'][0]['Key'] == 'test-file.csv'
        assert output['result'] == "Success"

    @mock_aws
    def test_handles_no_such_bucket_error(self):
        s3 = boto3.resource('s3')
        data = json.dumps({'test':'data'})
        with LogCapture() as l:
            output = write_to_s3(s3, 'non-existant-bucket', 'test-file', 'csv', data)
            assert output['result'] == "Failure"
            assert """root ERROR
  An error occurred (NoSuchBucket) when calling the PutObject operation: The specified bucket does not exist""" in (str(l))

    @mock_aws
    def test_handles_filename_error(self):
        s3 = boto3.resource('s3')
        data = True
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket', CreateBucketConfiguration={
        'LocationConstraint': 'eu-west-2'})
        with LogCapture() as l:
            output = write_to_s3(s3, 'test-bucket', 'test-file', 'csv', data)
            assert output['result'] == "Failure"
            assert """root ERROR
  Parameter validation failed:
Invalid type for parameter Body, value: True, type: <class 'bool'>, valid types: <class 'bytes'>, <class 'bytearray'>, file-like object""" in str(l)




           