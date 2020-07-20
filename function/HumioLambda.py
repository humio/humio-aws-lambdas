## base lambda that all other humio lambdas will be built up from

import os
import logging
import jsonpickle
import boto3
import importlib
import json
from humiolib.HumioClient import HumioIngestClient
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()

client = boto3.client('lambda')
client.get_account_settings()

## if Amazon Secrets Manager ARN detected, use that, otherwise assume plaintext

if 'HumioIngestTokenArn' in os.environ and 'HumioIngestTokenSecret' in os.environ:
        secrets_client = boto3.client('secretsmanager')
        secret_arn = os.environ['HumioIngestTokenArn']
        secret_name = os.environ['HumioIngestTokenSecret']
        print("using HumioIngestTokenArn '" + secret_arn + "' to derive humio ingest token")
        humio_ingest_token_response = secrets_client.get_secret_value(SecretId=secret_arn)
        if 'SecretString' in humio_ingest_token_response:
                humio_ingest_token = json.loads(humio_ingest_token_response['SecretString']).get(secret_name)
        else:
                print("SecretString not found, please refer to the integration documentation")
                humio_ingest_token = "not found"
else:
        print("using plaintext HumioIngestToken")
        humio_ingest_token = os.environ['HumioIngestToken']

humio_module = os.environ['HumioAWSModule']
humio_base_url = os.environ['HumioBaseURL']

## if first invocation, read context variables to set up dynamic module imports &
##  create a universal aws service object

print("importing humio aws module: " + humio_module)
imported_module = importlib.import_module(humio_module)
importlib.invalidate_caches()

## get class & instantiate
obj = getattr(imported_module, humio_module)
module_obj = obj()

## build global humio ingest client
humio_client = HumioIngestClient(
        base_url = humio_base_url,
        ingest_token = humio_ingest_token)

## set the ingest client via base lambda method
module_obj.set_humio_client(humio_client)

def lambda_handler(event, context):
    ## call parameterized universal object with event, context
    module_obj.invoke(event, context)
    
    ## TODO: log basic lambda metrics

    return 1
