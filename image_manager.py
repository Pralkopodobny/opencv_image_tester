import cv2
from PIL import Image
from PIL import ImageTk


class ImageManager:
    def __init__(self):
        #  image in BGR
        self.__image = cv2.imread("./azunya.png")
        # manipulated image by our functions
        self.__manipulated_image = cv2.imread("./azunya.png")
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

    def rotate_by_90(self, accept=False):
        self.__manipulated_image = cv2.rotate(self.__prev_images[-1][0], cv2.ROTATE_90_CLOCKWISE)
        if accept:
            self.__prev_commands.append("Rotate by 90 degrees")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def rotate_by_180(self, accept=False):
        self.__manipulated_image = cv2.rotate(self.__prev_images[-1][0], cv2.ROTATE_180)
        if accept:
            self.__prev_commands.append("Rotate by 180 degrees")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def rotate_by_270(self, accept=False):
        self.__manipulated_image = cv2.rotate(self.__prev_images[-1][0], cv2.ROTATE_90_COUNTERCLOCKWISE)
        if accept:
            self.__prev_commands.append("Rotate by -90 degrees")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def save_image(self, path: str, scale: bool, number=()):
        if number == ():
            if scale:
                cv2.imwrite(path, self.__scale_image(self.__manipulated_image))
            else:

                cv2.imwrite(path, self.__manipulated_image)

        else:
            image, gray = self.__prev_images[number[0]]
            if scale:
                cv2.imwrite(path, self.__scale_image(image))
            else:
                cv2.imwrite(path, image)

    def median_blur(self, ksize, accept=False):
        self.__manipulated_image = cv2.medianBlur(self.__prev_images[-1][0], ksize=ksize)
        if accept:
            self.__prev_commands.append(f"Median blur ksize={ksize}")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def gaussian_blur(self, ksize_x, ksize_y, accept=False):
        self.__manipulated_image = cv2.GaussianBlur(self.__prev_images[-1][0], (ksize_x, ksize_y), 0)
        if accept:
            self.__prev_commands.append(f"Gaussian blur ksize={ksize_x, ksize_y}")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def averaging_blur(self, ksize_x, ksize_y, accept=False):
        self.__manipulated_image = cv2.blur(self.__prev_images[-1][0], (ksize_x, ksize_y))
        if accept:
            self.__prev_commands.append(f"Averaging blur ksize={ksize_x, ksize_y}")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def bilateral_filter(self, ksize, sigma, accept=False):
        self.__manipulated_image = cv2.bilateralFilter(self.__prev_images[-1][0], ksize, sigma, sigma)
        if accept:
            self.__prev_commands.append(f"Bilateral filter ksize={ksize} sigma={sigma}")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def global_threshold(self, maxval, threshold, accept=False):
        ret, self.__manipulated_image = cv2.threshold(self.__prev_images[-1][0], threshold, maxval, cv2.THRESH_BINARY)
        if accept:
            self.__prev_commands.append(f"Global Threshold threshold={threshold} maxval={maxval}")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def mean_threshold(self, maxval, block_size, c, accept=False):
        if not self.__prev_images[-1][1]:
            return False, 'Image must be in grayscale'
        self.__manipulated_image = cv2.adaptiveThreshold(self.__prev_images[-1][0], maxval, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, c)
        if accept:
            self.__prev_commands.append(f"Global Threshold maxval={maxval} blocksize={block_size} C={c}")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def gaussian_threshold(self, maxval, block_size, c, accept=False):
        if not self.__prev_images[-1][1]:
            return False, 'Image must be in grayscale'
        self.__manipulated_image = cv2.adaptiveThreshold(self.__prev_images[-1][0], maxval, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                         cv2.THRESH_BINARY, block_size, c)
        if accept:
            self.__prev_commands.append(f"Global Threshold maxval={maxval} blocksize={block_size} C={c}")
            self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
        return True, ''

    def to_grayscale(self, accept=False):
        if self.__prev_images[-1][1]:
            return False, "An Image is already in grayscale"
        else:
            self.__manipulated_image = cv2.cvtColor(self.__prev_images[-1][0], cv2.COLOR_BGR2GRAY)
            if accept:
                self.__prev_commands.append("Convert to grayscale")
                self.__is_grayscale = True
                self.__prev_images.append((self.__manipulated_image, self.__is_grayscale))
            return True, ''
