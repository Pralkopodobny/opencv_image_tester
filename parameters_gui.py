from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from tkinter.scrolledtext import ScrolledText
from PIL import Image
from PIL import ImageTk


class LabeledScale(ttk.Frame):
    def __init__(self, master=None, text='', from_=0, to=10, variable=None, **kw):
        super().__init__(master, **kw)
        self.__text = StringVar()
        self.__variable = variable

        label = ttk.Label(self, text=text)
        label.grid(row=0, column=0)

        self.__slider = ttk.Scale(self, variable=variable, from_=from_, to=to, command=self.__update_label)
        self.__slider.grid(row=0, column=1)

        value_label = ttk.Label(self, textvariable=self.__text, anchor='e')
        value_label.grid(row=0, column=2, sticky=(E, W))

        if variable is not None:
            self.__text.set(variable.get())
            self.__slider.set(variable.get())

    def __update_label(self, scale):
        if self.__variable is None:
            self.__text.set(round(scale, 2))
        else:
            self.__text.set(self.__variable.get())


class LabeledCheckButton(ttk.Frame):
    def __init__(self, master=None, text='', variable=None, **kw):
        super().__init__(master, **kw)

        label = ttk.Label(self, text=text)
        label.grid(row=0, column=0)

        checkbox = ttk.Checkbutton(self, variable=variable)
        checkbox.grid(row=0, column=1)


class CannyMenu(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.__thresh1 = IntVar()
        self.__thresh2 = IntVar()
        self.__aperture_size = IntVar()
        self.__l2_gradient = BooleanVar()
        self.__callback = print

        self.columnconfigure(2, weight=1)

        thresh1_ls = LabeledScale(self, "Threshold 1:", 0, 255, self.__thresh1)
        thresh1_ls.grid(row=0, column=0, sticky=W)

        thresh2_ls = LabeledScale(self, "Threshold 2:", 0, 255, self.__thresh2)
        thresh2_ls.grid(row=1, column=0, sticky=W)

        aperture_size_ls = LabeledScale(self, "Aperture Size:", 1, 10, self.__aperture_size)
        aperture_size_ls.grid(row=2, column=0, sticky=W)

        l2_gradient_lch = LabeledCheckButton(self, 'L2gradient:', self.__l2_gradient)
        l2_gradient_lch.grid(row=3, column=0, sticky=W)

        self.__button = ttk.Button(self, text='preview')
        self.__button.grid(row=4, column=0)
        self.callback = print

    @property
    def callback(self):
        return self.__callback

    @callback.setter
    def callback(self, callback_function):
        self.__callback = callback_function
        self.__button.configure(command=lambda: self.__callback(self.__thresh1.get(), self.__thresh2.get(),
                                                                self.__aperture_size.get(), self.__l2_gradient.get()))
