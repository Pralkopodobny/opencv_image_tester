from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from tkinter.scrolledtext import ScrolledText
from PIL import Image
from PIL import ImageTk


class LabeledScale(ttk.Frame):
    def __init__(self, master=None, text='', from_=0, to=10, variable=None, round_value=False, **kw):
        super().__init__(master, **kw)
        self.__text = StringVar()
        self.__variable = variable
        self.__round_value = round_value

        label = ttk.Label(self, text=text, anchor='w')
        label.grid(row=0, column=0, sticky=W)

        self.__slider = ttk.Scale(self, variable=variable, from_=from_, to=to, command=self.__update_label)
        self.__slider.grid(row=1, column=0, sticky=(W, E))

        value_label = ttk.Label(self, textvariable=self.__text, anchor='e')
        value_label.grid(row=1, column=1, sticky=E)

        if variable is not None:
            self.__text.set(variable.get())
            self.__slider.set(variable.get())

    def __update_label(self, scale):
        if self.__variable is None:
            self.__text.set(round(getdouble(scale), 2))
        elif self.__round_value:
            self.__text.set(round(self.__variable.get(), 2))
        else:
            self.__text.set(self.__variable.get())

    def set(self, value):
        self.__slider.set(value)


class LabeledCheckButton(ttk.Frame):
    def __init__(self, master=None, text='', variable=None, **kw):
        super().__init__(master, **kw)

        label = ttk.Label(self, text=text)
        label.grid(row=0, column=0)

        checkbox = ttk.Checkbutton(self, variable=variable)
        checkbox.grid(row=0, column=1)


class PreviewAcceptButtons(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.preview_button = ttk.Button(self, text='Preview')
        self.preview_button.grid(row=0, column=0, sticky=(W, E))
        self.accept_button = ttk.Button(self, text='Accept')
        self.accept_button.grid(row=0, column=1, sticky=(W, E))


class LabeledSpinBox(ttk.Frame):
    def __init__(self, master=None, text='', textvariable=None, values=range(100), validate_function=None, **kw):
        super().__init__(master, **kw)
        self.__values = values

        label = ttk.Label(self, text=text, anchor='e')
        label.grid(row=0, column=0, sticky=W, pady=2)

        self.__spinbox = ttk.Spinbox(self, textvariable=textvariable, values=values, validate='key')
        if values is not None:
            self.__spinbox.set(values[0])
        if validate_function is not None:
            data_validation = self.register(validate_function)
            self.__spinbox.config(validate='key', validatecommand=(data_validation, '%P'))
        else:
            data_validation = self.register(self.__default_validate)
            self.__spinbox.config(validate='key', validatecommand=(data_validation, '%P'))
        self.__spinbox.grid(row=1, column=0)

    def __default_validate(self, user_input):
        if user_input.isdigit():
            return int(user_input) % 2 == 1 and int(user_input) >= 1
        return False

    def set(self, value):
        self.__spinbox.set(value)


class ParametersMenu(ttk.Frame):
    def __init__(self, master=None, name='', **kw):
        super().__init__(master, **kw)
        self._callback_function = print
        self._accept_function = print
        self.columnconfigure(0, weight=1)

        name_label = ttk.Label(self, text=name, anchor='center')
        name_label.grid(row=0, column=0, sticky=(W, E))
        separator = ttk.Separator(self, orient='horizontal')
        separator.grid(row=1, column=0, sticky=(W, E))

        self._main_frame = ttk.Frame(self)
        self._main_frame.grid(row=2, column=0, sticky=(W, E), padx=5)
        self._main_frame.columnconfigure(0, weight=1)

        self._buttons = PreviewAcceptButtons(self)
        self._buttons.grid(row=3, column=0, sticky=(W, E), pady=10, padx=5)


class FaceDetectionMenu(ttk.Frame):
    def __init__(self, master=None, name='', **kw):
        super().__init__(master, **kw)
        self._color_types = ['green', 'blue', 'red', 'yellow', 'pink', 'aqua']
        self._color_to_bgr = {'green': (0, 255, 0), 'blue': (255, 0, 0), 'red': (0, 0, 255), 'yellow': (0, 255, 255),
                              'pink': (255, 0, 255), 'aqua': (255, 255, 0)}
        self._callback_function = print
        self._accept_function = print
        self.columnconfigure(0, weight=1)

        name_label = ttk.Label(self, text=name, anchor='center')
        name_label.grid(row=0, column=0, sticky=(W, E), padx=5)
        separator = ttk.Separator(self, orient='horizontal')
        separator.grid(row=1, column=0, sticky=(W, E))

        self._main_frame = ttk.Frame(self)
        self._main_frame.grid(row=2, column=0, sticky=(W, E), padx=5)
        self._main_frame.columnconfigure(0, weight=1)

        self._button = ttk.Button(self, text='Apply')
        self._button.grid(row=3, column=0, sticky=(W, E), pady=10)


class CannyMenu(ParametersMenu):
    def __init__(self, master=None, **kw):
        super().__init__(master, 'Canny Edge Detection', **kw)
        self.__thresh1 = IntVar()
        self.__thresh2 = IntVar()
        self.__l2_gradient = BooleanVar()

        thresh1_ls = LabeledScale(self._main_frame, "Threshold 1:", 0, 255, self.__thresh1)
        thresh1_ls.grid(row=0, column=0, sticky=(W, E), pady=10)

        thresh2_ls = LabeledScale(self._main_frame, "Threshold 2:", 0, 255, self.__thresh2)
        thresh2_ls.grid(row=1, column=0, sticky=(W, E), pady=10)

        l2_gradient_lch = LabeledCheckButton(self._main_frame, 'L2gradient:', self.__l2_gradient)
        l2_gradient_lch.grid(row=3, column=0, sticky=(W, E), pady=10)

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._buttons.preview_button.configure(command=lambda: self._callback_function(self.__thresh1.get(),
                                                                                       self.__thresh2.get(),
                                                                                       self.__l2_gradient.get()))
        self._buttons.accept_button.configure(command=lambda: self._callback_function(self.__thresh1.get(),
                                                                                      self.__thresh2.get(),
                                                                                      self.__l2_gradient.get(),
                                                                                      True))


class MedianBlur(ParametersMenu):
    def __init__(self, master=None, **kw):
        super().__init__(master, 'Median Blur', **kw)
        self.__ksize = StringVar()

        ksize_lsb = LabeledSpinBox(self._main_frame, 'Ksize:', self.__ksize, [3, 5, 7, 9, 11])
        ksize_lsb.grid(row=0, column=0, sticky=(W, E), pady=10)

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._buttons.preview_button.configure(command=lambda: self._callback_function(int(self.__ksize.get())))
        self._buttons.accept_button.configure(command=lambda: self._callback_function(int(self.__ksize.get()), True))


class GeneralBlurMenu(ParametersMenu):
    def __init__(self, master=None, name='General Blur', **kw):
        super().__init__(master, name, **kw)
        self.__ksize_x = StringVar()
        self.__ksize_y = StringVar()

        ksize_x_lsb = LabeledSpinBox(self._main_frame, 'Ksize x:', self.__ksize_x, [3, 5, 7, 9, 11])
        ksize_x_lsb.grid(row=0, column=0, sticky=(W, E), pady=10)
        ksize_y_lsb = LabeledSpinBox(self._main_frame, 'Ksize y:', self.__ksize_y, [3, 5, 7, 9, 11])
        ksize_y_lsb.grid(row=1, column=0, sticky=(W, E), pady=10)

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._buttons.preview_button.configure(command=lambda: self._callback_function(int(self.__ksize_x.get()),
                                                                                       int(self.__ksize_y.get())))
        self._buttons.accept_button.configure(command=lambda: self._callback_function(int(self.__ksize_x.get()),
                                                                                      int(self.__ksize_y.get()),
                                                                                      True))


class BilateralFilterMenu(ParametersMenu):
    def __init__(self, master=None, **kw):
        super().__init__(master, 'Median Blur', **kw)
        self.__ksize = StringVar()
        self.__sigma = DoubleVar()

        ksize_lsb = LabeledSpinBox(self._main_frame, 'Ksize:', self.__ksize, [3, 5, 7, 9, 11])
        ksize_lsb.grid(row=0, column=0, sticky=(W, E), pady=10)
        sigma_ls = LabeledScale(self._main_frame, 'Sigma:', 1, 200, self.__sigma, True)
        sigma_ls.grid(row=1, column=0, sticky=(W, E), pady=10)

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._buttons.preview_button.configure(command=lambda: self._callback_function(int(self.__ksize.get()),
                                                                                       round(self.__sigma.get(), 2)))
        self._buttons.accept_button.configure(command=lambda: self._callback_function(int(self.__ksize.get()),
                                                                                      round(self.__sigma.get(), 2),
                                                                                      True))


class GlobalThresholdMenu(ParametersMenu):
    def __init__(self, master=None, **kw):
        super().__init__(master, 'Global Threshold', **kw)
        self.__max_val = IntVar()
        self.__thresh = IntVar()

        max_val_ls = LabeledScale(self._main_frame, 'Maxval:', 1, 255, self.__max_val)
        max_val_ls.grid(row=0, column=0, sticky=(E, W), pady=10)
        max_val_ls.set(255)

        thresh_ls = LabeledScale(self._main_frame, 'Threshold:', 1, 255, self.__thresh)
        thresh_ls.grid(row=1, column=0, sticky=(E, W), pady=10)
        thresh_ls.set(150)

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._buttons.preview_button.configure(command=lambda: self._callback_function(self.__max_val.get(),
                                                                                       self.__thresh.get()))

        self._buttons.accept_button.configure(command=lambda: self._callback_function(self.__max_val.get(),
                                                                                      self.__thresh.get(),
                                                                                      True))


class AdaptiveThresholdMenu(ParametersMenu):
    def __init__(self, master=None, name='Adaptive Threshold', **kw):
        super().__init__(master, name, **kw)
        self.__max_val = IntVar()
        self.__c = IntVar()
        self.__block_size = StringVar()

        max_val_ls = LabeledScale(self._main_frame, 'Maxval:', 1, 255, self.__max_val)
        max_val_ls.grid(row=0, column=0, sticky=(E, W), pady=10)
        max_val_ls.set(255)

        c_ls = LabeledScale(self._main_frame, 'C:', -255, 255, self.__c)
        c_ls.grid(row=1, column=0, sticky=(E, W), pady=10)
        c_ls.set(10)

        block_size_lsb = LabeledSpinBox(self._main_frame, 'Block size:', self.__block_size, [3, 5, 7, 9, 11])
        block_size_lsb.grid(row=2, column=0, sticky=(W, E), pady=10)

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._buttons.preview_button.configure(command=lambda: self._callback_function(self.__max_val.get(),
                                                                                       int(self.__block_size.get()),
                                                                                       self.__c.get()))

        self._buttons.accept_button.configure(command=lambda: self._callback_function(self.__max_val.get(),
                                                                                      int(self.__block_size.get()),
                                                                                      self.__c.get(),
                                                                                      True))


class GradientMenu(ParametersMenu):
    def __init__(self, master=None, name='Gradient', **kw):
        super().__init__(master, name, **kw)
        self.__delta = IntVar()
        self.__ksize = StringVar()

        delta_ls = LabeledScale(self._main_frame, 'Delta:', -255, 255, self.__delta)
        delta_ls.grid(row=0, column=0, sticky=(W, E), pady=10)

        ksize_lsb = LabeledSpinBox(self._main_frame, 'Ksize:', self.__ksize, [1, 3, 5, 7, 9, 11])
        ksize_lsb.grid(row=1, column=0, sticky=(W, E), pady=10)

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._buttons.preview_button.configure(command=lambda: self._callback_function(self.__delta.get(),
                                                                                       int(self.__ksize.get())))

        self._buttons.accept_button.configure(command=lambda: self._callback_function(self.__delta.get(),
                                                                                      int(self.__ksize.get()),
                                                                                      True))


class HaarCascadeMenu(FaceDetectionMenu):
    def __init__(self, master=None, **kw):
        super().__init__(master, 'Haar Cascade', **kw)
        self.__color = StringVar()
        self.__scale_factor = StringVar()
        self.__min_neighbours = IntVar()
        self.__thickness = IntVar()

        def scale_validate(user_input):
            return user_input.isdigit and getdouble(user_input) >= 1.1

        scale_factor_ls = LabeledSpinBox(self._main_frame, 'Scale factor:', self.__scale_factor,
                                         [x / 10 for x in range(11, 1000)], validate_function=scale_validate)
        scale_factor_ls.grid(row=0, column=0, sticky=(W, E), pady=10)

        min_neighbours = LabeledScale(self._main_frame, 'Min neighbours:', 3, 20, self.__min_neighbours)
        min_neighbours.set(10)
        min_neighbours.grid(row=1, column=0, sticky=(W, E), pady=10)

        thickness = LabeledScale(self._main_frame, 'Thickness:', 1, 20, self.__thickness)
        thickness.set(2)
        thickness.grid(row=2, column=0, sticky=(W, E), pady=10)

        def always_reject(user_input):
            return False

        color_lbx = LabeledSpinBox(self._main_frame, 'color:', self.__color,
                                   self._color_types, validate_function=always_reject)
        color_lbx.grid(row=3, column=0, sticky=(W, E), pady=10)

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._button.configure(command=lambda: self._callback_function(getdouble(self.__scale_factor.get()),
                                                                       self.__min_neighbours.get(),
                                                                       self.__thickness.get(),
                                                                       self._color_to_bgr[self.__color.get()]))


class ShapePredictorMenu(FaceDetectionMenu):
    def __init__(self, master=None, **kw):
        super().__init__(master, 'Shape Predictor', **kw)

        self.__eye_color = StringVar()
        self.__mouth_color = StringVar()
        self.__face_color = StringVar()
        self.__frame_color = StringVar()
        self.__thickness = IntVar()

        thickness = LabeledScale(self._main_frame, 'Thickness:', 1, 20, self.__thickness)
        thickness.set(2)
        thickness.grid(row=0, column=0, sticky=(W, E), pady=10)

        def always_reject(user_input):
            return False

        eye_color_lbx = LabeledSpinBox(self._main_frame, 'Eye color:', self.__eye_color, self._color_types,
                                       validate_function=always_reject)
        eye_color_lbx.grid(row=1, column=0, sticky=(W, E), pady=10)
        eye_color_lbx.set(self._color_types[0])

        mouth_color_lbx = LabeledSpinBox(self._main_frame, 'Mouth color:', self.__mouth_color, self._color_types,
                                         validate_function=always_reject)
        mouth_color_lbx.grid(row=2, column=0, sticky=(W, E), pady=10)
        mouth_color_lbx.set(self._color_types[1])

        face_color_lbx = LabeledSpinBox(self._main_frame, 'Face color:', self.__face_color, self._color_types,
                                        validate_function=always_reject)
        face_color_lbx.grid(row=3, column=0, sticky=(W, E), pady=10)
        face_color_lbx.set(self._color_types[2])

        frame_color_lbx = LabeledSpinBox(self._main_frame, 'Frame color:', self.__frame_color, self._color_types,
                                         validate_function=always_reject)
        frame_color_lbx.grid(row=4, column=0, sticky=(W, E), pady=10)
        frame_color_lbx.set(self._color_types[3])

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._button.configure(command=lambda: self._callback_function(self._color_to_bgr[self.__eye_color.get()],
                                                                       self._color_to_bgr[self.__mouth_color.get()],
                                                                       self._color_to_bgr[self.__face_color.get()],
                                                                       self._color_to_bgr[self.__frame_color.get()],
                                                                       self.__thickness.get()))
