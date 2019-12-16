import uuid

class BatchGenerator:

    def __init__(self,initBatchId=None):
        self.batchID=initBatchId
        self.startOfBatch=False

    # pass a function that defines if the batch is started
    def getBatchID(self,startOfBatch):
        if(not(isinstance(startOfBatch,bool))):
            if(startOfBatch):
                if(self.batchID is int):
                    self.batchID=self.batchId+1
                else:
                    self.batchID=uuid.uuid1()
        else:
            raise(ValueError("startOfBatch must be a bool"))
        return self.batchID
