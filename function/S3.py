import os
import jsonpickle
import boto3
import importlib
import json
from BaseHumioLambda import BaseHumioLambda

class S3(BaseHumioLambda):
    def invoke(self, event, context):
        ## parse s3 event records
        s3_client = boto3.resource('s3')

        batch_size = 10000
        if 'HumioS3BatchSize' in os.environ:
            batch_size = int(os.environ['HumioS3BatchSize'])
            print ("S3: set: HumioS3BatchSize = " + str(batch_size))
        else:
            print ("S3: using default HumioS3BatchSize = " + str(batch_size))

        data_type = "raw" # or json
        if 'HumioS3DataType' in os.environ:
            env_dt = os.environ['HumioS3DataType'].lower()
            if env_dt == "raw" or env_dt == "json" or env_dt == "metadata":
                data_type = env_dt
            else:
                print("invalid data type specified in environment variable 'HumioS3DataType': '" + 
                    str(os.environ['HumioS3DataType']) + "', defaulting to 'metadata'")

        for record in event['Records']:
            batch = []
            if data_type == "raw" or data_type == "json":
                s3_bucket = record["s3"]["bucket"]["name"]
                s3_key = record["s3"]["object"]["key"]
                obj = s3_client.Object(s3_bucket, s3_key)
                body = obj.get()['Body']
                for log_line_bytes in body.iter_lines():
                    log_line = log_line_bytes.decode("utf-8")

                    if data_type == "json":
                        record["data"] = json.loads(log_line)
                    else:
                        record["data"] = log_line
                    
                    batch.append(jsonpickle.encode(record))
                    if len(batch) == batch_size:
                        print("S3: sending batch, size = " + str(len(batch)))
                        self.log(batch)
                        batch.clear()            
            elif data_type == "metadata":
                batch.append(jsonpickle.encode(record))
            
            if len(batch) == batch_size:
                print("S3: sending batch, size = " + str(len(batch)))
                self.log(batch)
                batch.clear()
        
        # grab any stragglers
        if len(batch) > 0:
            print("S3: sending final batch, size = " + str(len(batch)))
            self.log(batch)

        BaseHumioLambda.invoke(self, event, context)
