import os
import jsonpickle
import boto3
import importlib
import json
from BaseHumioLambda import BaseHumioLambda

class S3JSONToHEC(BaseHumioLambda):
    def invoke(self, event, context):
        ## parse s3 event records
        s3_client = boto3.resource('s3')

        batch_size = 10000
        if 'HumioS3JSONToHECBatchSize' in os.environ:
            batch_size = int(os.environ['HumioS3JSONToHECBatchSize'])
            print ("S3JSONToHEC: set: HumioS3JSONToHECBatchSize = " + str(batch_size))
        else:
            print ("S3JSONToHEC: using default HumioS3JSONToHECBatchSize = " + str(batch_size))

        for record in event['Records']:
            s3_bucket = record["s3"]["bucket"]["name"]
            s3_key = record["s3"]["object"]["key"]
            print("S3JSONToHEC: processing S3 object, bucket = " + s3_bucket + ", key = " + s3_key)
            obj = s3_client.Object(s3_bucket, s3_key)
            body = obj.get()['Body']
            batch = []
            for log_line_bytes in body.iter_lines():
                log_line = log_line_bytes.decode("utf-8")
                batch.append(log_line)
                if len(batch) == batch_size:
                    print("S3JSONToHEC: sending batch, size = " + str(len(batch)))
                    self.log(batch)
                    batch.clear()
            
            # grab any stragglers
            if len(batch) > 0:
                print("S3JSONToHEC: sending final batch, size = " + str(len(batch)))
                self.log(batch)

        BaseHumioLambda.invoke(self, event, context)
