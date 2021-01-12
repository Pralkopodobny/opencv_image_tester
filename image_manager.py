import cv2
from PIL import Image
from PIL import ImageTk


class ImageManager:
    def __init__(self):
        self.__image = cv2.imread("C:/Users/HP/Pictures/profile.png")
        self.__small_image = cv2.imread("C:/Users/HP/Pictures/azunya.png")

    @property
    def image(self):
        image = cv2.cvtColor(self.__image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        return image

    @property
    def small_image(self):
        image = cv2.cvtColor(self.__small_image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        return image
