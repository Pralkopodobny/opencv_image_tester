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
        self.__round_value=round_value
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, minsize=30)

        label = ttk.Label(self, text=text, anchor='w')
        label.grid(row=0, column=0, sticky=W)

        self.__slider = ttk.Scale(self, variable=variable, from_=from_, to=to, command=self.__update_label)
        self.__slider.grid(row=0, column=1, sticky=E)

        value_label = ttk.Label(self, textvariable=self.__text, anchor='e')
        value_label.grid(row=0, column=2, sticky=E)

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
    def __init__(self, master=None, text='', textvariable=None, values=range(100), **kw):
        super().__init__(master, **kw)
        self.__values = values

        label = ttk.Label(self, text=text)
        label.grid(row=0, column=0)

        spinbox = ttk.Spinbox(self, textvariable=textvariable, values=values, validate='key')
        data_validation = self.register(self.__validate)
        if values is not None:
            spinbox.set(values[0])
        spinbox.config(validate='key', validatecommand=(data_validation, '%P'))
        spinbox.grid(row=0, column=1)

    def __validate(self, user_input):
        if user_input.isdigit():
            return int(user_input) % 2 == 1 and int(user_input) >= 1
        return False


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
        self._main_frame.grid(row=2, column=0, sticky=(W, E))

        self._buttons = PreviewAcceptButtons(self)
        self._buttons.grid(row=3, column=0, sticky=(W, E), pady=10)


class CannyMenu(ParametersMenu):
    def __init__(self, master=None, **kw):
        super().__init__(master, 'Canny Edge Detection', **kw)
        self.__thresh1 = IntVar()
        self.__thresh2 = IntVar()
        self.__aperture_size = IntVar()
        self.__l2_gradient = BooleanVar()

        thresh1_ls = LabeledScale(self._main_frame, "Threshold 1:", 0, 255, self.__thresh1)
        thresh1_ls.grid(row=2, column=0, sticky=(W, E), pady=10)

        thresh2_ls = LabeledScale(self._main_frame, "Threshold 2:", 0, 255, self.__thresh2)
        thresh2_ls.grid(row=3, column=0, sticky=(W, E), pady=10)

        aperture_size_ls = LabeledScale(self._main_frame, "Aperture Size:", 1, 10, self.__aperture_size)
        aperture_size_ls.grid(row=4, column=0, sticky=(W, E), pady=10)

        l2_gradient_lch = LabeledCheckButton(self._main_frame, 'L2gradient:', self.__l2_gradient)
        l2_gradient_lch.grid(row=5, column=0, sticky=(W, E), pady=10)

    @property
    def callback(self):
        return self._callback_function

    @callback.setter
    def callback(self, callback_function):
        self._callback_function = callback_function
        self._buttons.preview_button.configure(command=lambda: self._callback_function(self.__thresh1.get(),
                                                                                       self.__thresh2.get(),
                                                                                       self.__aperture_size.get(),
                                                                                       self.__l2_gradient.get()))
        self._buttons.accept_button.configure(command=lambda: self._callback_function(self.__thresh1.get(),
                                                                                      self.__thresh2.get(),
                                                                                      self.__aperture_size.get(),
                                                                                      self.__l2_gradient.get(),
                                                                                      True))


class MedianBlur(ParametersMenu):
    def __init__(self, master=None, **kw):
        super().__init__(master, 'Median Blur', **kw)
        self.__ksize = StringVar()

        ksize_lsb = LabeledSpinBox(self._main_frame, 'ksize:', self.__ksize, [3, 5, 7, 9, 11])
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

        ksize_x_lsb = LabeledSpinBox(self._main_frame, 'ksize x:', self.__ksize_x, [3, 5, 7, 9, 11])
        ksize_x_lsb.grid(row=0, column=0, sticky=(W, E), pady=10)
        ksize_y_lsb = LabeledSpinBox(self._main_frame, 'ksize y:', self.__ksize_y, [3, 5, 7, 9, 11])
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

        ksize_lsb = LabeledSpinBox(self._main_frame, 'ksize:', self.__ksize, [3, 5, 7, 9, 11])
        ksize_lsb.grid(row=0, column=0, sticky=(W, E), pady=10)
        sigma_ls = LabeledScale(self._main_frame, 'sigma:', 1, 200, self.__sigma, True)
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