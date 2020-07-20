import jsonpickle
from BaseHumioLambda import BaseHumioLambda

class CloudWatchLambda(BaseHumioLambda):
    def invoke(self, event, context):
        ## parse cloudwatch event records
        # self.log([jsonpickle.encode(event), jsonpickle.encode(context)])
        BaseHumioLambda.invoke(self, event, context)
