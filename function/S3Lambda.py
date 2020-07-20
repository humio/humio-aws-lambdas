import jsonpickle
from BaseHumioLambda import BaseHumioLambda

class S3Lambda(BaseHumioLambda):
    def invoke(self, event, context):
        ## parse s3 event records
        #self.log([jsonpickle.encode(event), jsonpickle.encode(context)])
        BaseHumioLambda.invoke(self, event, context)
