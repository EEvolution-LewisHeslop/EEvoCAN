from PIL import ImageTk
from PIL.Image import Image
from tkinter import Canvas, Frame
from math import ceil


# Takes an image and displays it on a canvas, supports resizing with following modes
# (stretch, preserve, TODO: fitheight, fitwidth, custom, anchored, tiled, mirror)
class ResponsiveImage(Canvas):
    def __init__(
             self,
             master: Frame,
             image: Image,
             resizeMode='preserve',
             customRatioWidth=None,
             customRatioHeight=None,
             anchorpointX=None,
             anchorpointY=None):
        super().__init__(
            master,
            background=master.background,
            highlightthickness=0)
        image.load()
        self._image = image
        width, height = image.size
        self._imageRatio = width / height
        self._resizeMode = resizeMode
        self._customRatioWidth = customRatioWidth
        self._customRatioHeight = customRatioHeight
        self._anchorpointX = anchorpointX
        self._anchorpointY = anchorpointY
        self.bind('<Configure>', self.resize_event)
        self.redraw()

    # Reconfigure the stretchyimage based on the given
    def configure(
            self,
            image: Image = None,
            resizeMode=None,
            customRatioWidth=None,
            customRatioHeight=None,
            anchorpointX=None,
            anchorpointY=None):
        if (image):
            self._image = image
            width, height = image.size
            self._imageRatio = width / height
        if (resizeMode):
            self._resizeMode = resizeMode
        if (customRatioWidth):
            self._customRatioWidth = customRatioWidth
        if (customRatioHeight):
            self._customRatioHeight = customRatioHeight
        if (anchorpointX):
            self._anchorpointX = anchorpointX
        if (anchorpointY):
            self._anchorpointY = anchorpointY
        self.redraw()

    # Redraws the image.
    def redraw(self):
        self.resize(width=self.winfo_width(), height=self.winfo_height())

    # Handles resized events
    def resize_event(self, event):
        width = event.width
        height = event.height
        self.resize(width=width, height=height)

    # Resizes the image based on the received window heights and resizeMode
    def resize(self, width=30, height=30):
        self.delete('image')
        if (self._resizeMode == 'stretch'):
            self.resize_stretch(width, height)
        elif (self._resizeMode == 'preserve'):
            self.resize_preserve(width, height)
        else:
            print("Unexpected resizeMode, reverting to stretch.")
            self.resize_stretch(width, height)

    # Resizes the image with stretching to the given width and height.
    def resize_stretch(self, width, height):
        imageResized = self._image.resize(size=(width, height))
        self.imageTk = ImageTk.PhotoImage(imageResized)
        self.create_image(0, 0, image=self.imageTk, anchor='nw', tags='image')

    # Resizes the image with stretching to the given width and height.
    def resize_preserve(self, width, height):
        canvasRatio = width / height

        if (canvasRatio > self._imageRatio):
            scaledHeight = height
            scaledWidth = ceil(height * self._imageRatio)
        else:
            scaledHeight = ceil(width / self._imageRatio)
            scaledWidth = width

        imageResized = self._image.resize(size=(scaledWidth, scaledHeight))
        self.imageTk = ImageTk.PhotoImage(imageResized)
        self.create_image(
            width / 2,
            height / 2,
            image=self.imageTk,
            anchor='center',
            tags='image')