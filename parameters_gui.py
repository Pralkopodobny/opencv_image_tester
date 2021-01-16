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


class PreviewAcceptButtons(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.preview_button = ttk.Button(self, text='Preview')
        self.preview_button.grid(row=0, column=0, sticky=(W, E))
        self.accept_button = ttk.Button(self, text='Accept')
        self.accept_button.grid(row=0, column=1, sticky=(W, E))


class CannyMenu(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.__thresh1 = IntVar()
        self.__thresh2 = IntVar()
        self.__aperture_size = IntVar()
        self.__l2_gradient = BooleanVar()
        self.__preview_function = print

        self.columnconfigure(0, weight=1)

        thresh1_ls = LabeledScale(self, "Threshold 1:", 0, 255, self.__thresh1)
        thresh1_ls.grid(row=0, column=0, sticky=(W, E), pady=10)

        thresh2_ls = LabeledScale(self, "Threshold 2:", 0, 255, self.__thresh2)
        thresh2_ls.grid(row=1, column=0, sticky=(W, E), pady=10)

        aperture_size_ls = LabeledScale(self, "Aperture Size:", 1, 10, self.__aperture_size)
        aperture_size_ls.grid(row=2, column=0, sticky=(W, E), pady=10)

        l2_gradient_lch = LabeledCheckButton(self, 'L2gradient:', self.__l2_gradient)
        l2_gradient_lch.grid(row=3, column=0, sticky=(W, E), pady=10)

        self.__buttons = PreviewAcceptButtons(self)
        self.__buttons.grid(row=4, column=0, sticky=(W, E), pady=10)
        self.on_preview = print

    @property
    def on_preview(self):
        return self.__preview_function

    @on_preview.setter
    def on_preview(self, preview_function):
        self.__preview_function = preview_function
        self.__buttons.preview_button.configure(command=lambda: self.__preview_function(self.__thresh1.get(),
                                                                                        self.__thresh2.get(),
                                                                                        self.__aperture_size.get(),
                                                                                        self.__l2_gradient.get()))
