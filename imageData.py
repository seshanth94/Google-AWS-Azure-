class imageData(object):

    def __init__(self,imageID, imageComments, imageBinData):
        self.imageID = imageID
        self.imageComments = imageComments
        self.imageBinData = imageBinData

    def set_imageComments(self,comments):
        self.imageComments = comments

    def set_imageBinData(self,bindata):
        self.imageBinData = bindata