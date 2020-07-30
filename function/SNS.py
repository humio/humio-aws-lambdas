import os
import jsonpickle
import boto3
import importlib
import json
import base64
from BaseHumioLambda import BaseHumioLambda

class SNS(BaseHumioLambda):
    def invoke(self, event, context):

        batch_size = 10000
        if 'HumioSNSBatchSize' in os.environ:
            batch_size = int(os.environ['HumioSNSBatchSize'])
            print ("SNS: set: HumioSNSBatchSize = " + str(batch_size))
        else:
            print ("SNS: using default HumioSNSBatchSize = " + str(batch_size))

        data_type = "raw" # or json
        if 'HumioSNSDataType' in os.environ:
            env_dt = os.environ['HumioSNSDataType'].lower()
            if env_dt == "raw" or env_dt == "json":
                data_type = env_dt
            else:
                print("invalid data type specified in environment variable 'HumioSNSDataType': '" + 
                    str(os.environ['HumioSNSDataType']) + "', defaulting to 'raw'")

        batch = []
        for record in event['Records']:
            decoded_data = record["Sns"]["Message"]
            if data_type == "json":
                record["Sns"]["Message"] = json.loads(decoded_data)
            batch.append(jsonpickle.encode(record))
            if len(batch) == batch_size:
                print("SNS: sending batch, size = " + str(len(batch)))
                self.log(batch)
                batch.clear()
            
        # grab any stragglers
        if len(batch) > 0:
            print("SNS: sending final batch, size = " + str(len(batch)))
            self.log(batch)

        BaseHumioLambda.invoke(self, event, context)
