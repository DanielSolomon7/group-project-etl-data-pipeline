from src.week1_lambda import lambda_handler
from src.utils import get_rows, get_columns, write_to_s3, get_tables, fetch_last_timestamps_from_db, read_timestamps_table_from_s3
from src.connection import db_connection, get_db_creds
from testfixtures import LogCapture
from moto import mock_aws
import json
import boto3

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

class TestGetTables:
    def test_get_tables_returns_list(self):
        conn = db_connection()
        tables = get_tables(conn)
        assert isinstance(tables, list)

    def test_get_tables_returns_tables(self):
        conn = db_connection()
        tables = get_tables(conn)
        assert tables == ['sales_order', 'transaction', 'department', 'staff', 'purchase_order', 'counterparty', 'payment', 'currency', 'payment_type', 'address', 'design']

class TestFetchLastTimestamp:
    def test_returns_dict(self):
        conn = db_connection()
        output = fetch_last_timestamps_from_db(conn)
        assert isinstance(output, dict)

    def test_all_tables_in_output(self):
        conn = db_connection()
        output = fetch_last_timestamps_from_db(conn)
        tables = get_tables(conn)
        for table in tables:
            assert table in list(output.keys())

    
class TestWritingTimestampTableToCSV:
    def test_file_created_and_readable_to_dict(self):
        conn = db_connection()
        timestamp_dict = fetch_last_timestamps_from_db(conn)
        with open('test/test_timestamp_table.json', 'w') as f:
            f.write(json.dumps(timestamp_dict))
        with open('test/test_timestamp_table.json', 'r') as f:
            contents = json.load(f)
        assert type(contents) == type(timestamp_dict)

class TestReadTimestampsFromS3:
    @mock_aws
    def test_returns_inputted_data(self):
        data = json.dumps({'sales_order': '2024-11-14 10:19:09.990000', 'transaction': '2024-11-14 10:19:09.990000', 'department': '2022-11-03 14:20:49.962000', 'staff': '2022-11-03 14:20:51.563000', 'purchase_order': '2024-11-14 09:11:09.922000', 'counterparty': '2022-11-03 14:20:51.563000', 'payment': '2024-11-14 10:19:09.990000', 'currency': '2022-11-03 14:20:49.962000', 'payment_type': '2022-11-03 14:20:49.962000', 'address': '2022-11-03 14:20:49.962000', 'design': '2024-11-14 09:41:09.839000'})
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket', CreateBucketConfiguration={
        'LocationConstraint': 'eu-west-2'})
        s3 = boto3.resource('s3')
        write_to_s3(s3, 'test-bucket', 'timestamp_table', 'json', data)
        output = read_timestamps_table_from_s3(client, 'test-bucket', 'timestamp_table.json')
        assert output == json.loads(data)
        assert isinstance(output, dict)

    def test_handles_error(self):
        pass
           
