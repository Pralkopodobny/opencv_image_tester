import cv2
from PIL import Image
from PIL import ImageTk


class ImageManager:
    def __init__(self):
        #  image in BGR
        self.__image = cv2.imread("C:/Users/HP/Pictures/azunya.png")
        # manipulated image by our functions
        self.__manipulated_image = cv2.imread("C:/Users/HP/Pictures/azunya.png")
        self.__is_grayscale = False

        # stack of images
        self.__prev_images = [(self.__image, False)]
        # stack of strings each containing description of used command
        self.__prev_commands = ["Initial state"]
        # scale of images showed to user. Note: images are stored in original size.
        self.__scale = 100

    @property
    def image(self):
        return self.image_to_tk(self.__image, False)

    @property
    def manipulated_image(self):
        return self.image_to_tk(self.__manipulated_image, self.__is_grayscale)

    @property
    def scale(self):
        return self.__scale

    @scale.setter
    def scale(self, new_scale):
        self.__scale = new_scale

    @property
    def prev_commands(self):
        return self.__prev_commands

    def __scale_image(self, image):
        if self.__scale != 100:
            width = int(image.shape[1] * self.__scale / 100)
            height = int(image.shape[0] * self.__scale / 100)
            return cv2.resize(image, (width, height))
        else:
            return image

    def image_to_tk(self, cv_image, is_grayscale):
        if not is_grayscale:
            tk_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            tk_image = self.__scale_image(tk_image)
        else:
            tk_image = self.__scale_image(cv_image)
        tk_image = Image.fromarray(tk_image)
        tk_image = ImageTk.PhotoImage(tk_image)
        return tk_image

    def get_prev_image(self, i):
        image, gray = self.__prev_images[i]
        return self.image_to_tk(image, gray)

    def open_image_from_path(self, path):
        self.__image = cv2.imread(path, cv2.IMREAD_COLOR)
        self.__manipulated_image = cv2.imread(path, cv2.IMREAD_COLOR)
        self.__prev_images = [(self.__image, False)]
        self.__prev_commands = ["Initial state"]
        self.__is_grayscale = False

    def rotate_by_90(self):
        self.__prev_commands.append("Rotate by 90 degrees")
        self.__manipulated_image = cv2.rotate(self.__manipulated_image, cv2.ROTATE_90_CLOCKWISE)
        self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))

    def rotate_by_180(self):
        self.__prev_commands.append("Rotate by 180 degrees")
        self.__manipulated_image = cv2.rotate(self.__manipulated_image, cv2.ROTATE_180)
        self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))

    def rotate_by_270(self):
        self.__prev_commands.append("Rotate by -90 degrees")
        self.__manipulated_image = cv2.rotate(self.__manipulated_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))

    def save_image(self, path: str, scale: bool, number=None):
        if number == ():
            if scale:
                print("nn s")
                cv2.imwrite(path, self.__scale_image(self.__manipulated_image))
            else:
                print("nn ns")

                cv2.imwrite(path, self.__manipulated_image)

        else:
            if scale:
                cv2.imwrite(path, self.__prev_images[number][0])
                print("n s")
            else:
                cv2.imwrite(path, self.__prev_images[number][0])
                print("nn s")
