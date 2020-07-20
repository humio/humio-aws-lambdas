import jsonpickle
from S3Lambda import S3Lambda

class GuardDutyViaS3(S3Lambda):
    def invoke(self, event, context):
        ## parse Guard Duty event records
        S3Lambda.invoke(self, event, context)
