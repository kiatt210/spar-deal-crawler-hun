from PIL import Image


ITEMS_PER_ROW=3
ROWS_PER_PAGE=4
IMAGE_WIDTH=257
IMAGE_HEIGHT=373
PAGE_WIDTH=ITEMS_PER_ROW*IMAGE_WIDTH
PAGE_HEIGHT=ROWS_PER_PAGE*IMAGE_HEIGHT

class ImageSaver:

    def __init__(self,saveLocation):
        self.row = 0
        self.column = 0
        self.saveLocation = saveLocation
        self.image = Image.new(mode="RGB",size=(PAGE_WIDTH,PAGE_HEIGHT))
        self.file_index=1

    def addImage(self,image):
        box=(self.column*IMAGE_WIDTH,self.row*IMAGE_HEIGHT)
        
        self.image.paste(image,box=box)

        self.column = self.column+1
        if self.column%ITEMS_PER_ROW == 0:
            self.row = self.row+1
            self.column = 0
            if self.row > ROWS_PER_PAGE:
                self.save()

    def save(self):
        self.image.save(f'{self.saveLocation}/image_{self.file_index}.png')
        self.file_index = self.file_index+1
        self.image = Image.new(mode="RGB",size=(PAGE_WIDTH,PAGE_HEIGHT))
        self.row=0