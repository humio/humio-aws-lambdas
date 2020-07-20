from humiolib.HumioClient import HumioIngestClient

class BaseHumioLambda:
    humio_client = None

    def set_humio_client(self, client):
        self.humio_client = client

    def log(self, logs):
        self.humio_client.ingest_messages(logs)

    def invoke(self, event, context):
        pass
