import jsonpickle
from CloudWatchLambda import CloudWatchLambda

class GuardDutyViaCloudWatch(CloudWatchLambda):
    def invoke(self, event, context):
        ## parse Guard Duty event records
        CloudWatchLambda.invoke(self, event, context)
