import os
import jsonpickle
import boto3
import importlib
import json
import base64
from BaseHumioLambda import BaseHumioLambda

class SQS(BaseHumioLambda):
    def invoke(self, event, context):

        batch_size = 10000
        if 'HumioSQSBatchSize' in os.environ:
            batch_size = int(os.environ['HumioSQSBatchSize'])
            print ("SQS: set: HumioSQSBatchSize = " + str(batch_size))
        else:
            print ("SQS: using default HumioSQSBatchSize = " + str(batch_size))

        data_type = "raw" # or json
        if 'HumioSQSDataType' in os.environ:
            env_dt = os.environ['HumioSQSDataType'].lower()
            if env_dt == "raw" or env_dt == "json":
                data_type = env_dt
            else:
                print("invalid data type specified in environment variable 'HumioSQSDataType': '" + 
                    str(os.environ['HumioSQSDataType']) + "', defaulting to 'raw'")

        batch = []
        for record in event['Records']:
            decoded_data = record["body"]
            if data_type == "json":
                record["body"] = json.loads(decoded_data)
            batch.append(jsonpickle.encode(record))
            if len(batch) == batch_size:
                print("SQS: sending batch, size = " + str(len(batch)))
                self.log(batch)
                batch.clear()
        
        # grab any stragglers
        if len(batch) > 0:
            print("SQS: sending final batch, size = " + str(len(batch)))
            self.log(batch)

        BaseHumioLambda.invoke(self, event, context)
