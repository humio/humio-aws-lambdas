import os
import jsonpickle
import boto3
import importlib
import json
import base64
from BaseHumioLambda import BaseHumioLambda

class Kinesis(BaseHumioLambda):
    def invoke(self, event, context):

        batch_size = 10000
        if 'HumioKinesisBatchSize' in os.environ:
            batch_size = int(os.environ['HumioKinesisBatchSize'])
            print ("Kinesis: set: HumioKinesisBatchSize = " + str(batch_size))
        else:
            print ("Kinesis: using default HumioKinesisBatchSize = " + str(batch_size))

        data_type = "raw" # or json
        if 'HumioKinesisDataType' in os.environ:
            env_dt = os.environ['HumioKinesisDataType'].lower()
            if env_dt == "raw" or env_dt == "json":
                data_type = env_dt
            else:
                print("invalid data type specified in environment variable 'HumioKinesisDataType': '" + 
                    str(os.environ['HumioKinesisDataType']) + "', defaulting to 'raw'")

        batch = []
        for record in event['Records']:
            decoded_data = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
            if data_type == "json":
                decoded_data = json.loads(decoded_data)
            record["kinesis"]["data"] = decoded_data
            batch.append(jsonpickle.encode(record))
            if len(batch) == batch_size:
                print("Kinesis: sending batch, size = " + str(len(batch)))
                self.log(batch)
                batch.clear()
            
        # grab any stragglers
        if len(batch) > 0:
            print("Kinesis: sending final batch, size = " + str(len(batch)))
            self.log(batch)

        BaseHumioLambda.invoke(self, event, context)
