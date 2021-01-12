from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from tkinter.scrolledtext import ScrolledText
from PIL import Image
from PIL import ImageTk
import cv2
from image_manager import ImageManager


class ScrollableImage(ttk.Frame):
    def __init__(self, master=None, **kw):
        self.__image = kw.pop('image', None)
        super(ScrollableImage, self).__init__(master=master, **kw)
        self.cnvs = Canvas(self, highlightthickness=0, **kw)
        self.__shape = self.cnvs.create_image(0, 0, anchor='nw', image=self.__image)
        self.v_scroll = ttk.Scrollbar(self, orient='vertical')
        self.h_scroll = ttk.Scrollbar(self, orient='horizontal')
        self.cnvs.grid(row=0, column=0,  sticky='nsew')
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.cnvs.config(xscrollcommand=self.h_scroll.set,
                           yscrollcommand=self.v_scroll.set)
        self.v_scroll.config(command=self.cnvs.yview)
        self.h_scroll.config(command=self.cnvs.xview)
        self.cnvs.config(scrollregion=self.cnvs.bbox('all'))

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, new_image):
        self.cnvs.delete(self.__shape)
        self.__image = new_image
        self.__shape = self.cnvs.create_image(0, 0, anchor='nw', image=self.__image)
        self.cnvs.config(scrollregion=self.cnvs.bbox('all'))


class ScrollableList(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.__elements = []
        self.__elements_var = StringVar(value=self.__elements)
        self.__callback_function = None

        list_box = Listbox(self, listvariable=self.__elements_var)
        list_box.grid(row=0, column=0, sticky=(N, S, W, E))

        v_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=list_box.yview)
        v_scroll.grid(row=0, column=1, sticky=(N, S))

        h_scroll = ttk.Scrollbar(self, orient=HORIZONTAL, command=list_box.xview)
        h_scroll.grid(row=1, column=0, sticky=(W, E))

        list_box.bind("<<ListboxSelect>>", self.__callback)

    @property
    def list(self):
        return self.__elements

    @list.setter
    def list(self, new_list):
        self.__elements = new_list
        self.__elements_var.set(self.__elements)

    @property
    def callback_function(self):
        return self.__callback_function

    @callback_function.setter
    def callback_function(self, new_callback_function):
        self.__callback_function = new_callback_function

    def __callback(self, event):
        selection = event.widget.curselection()
        if selection and self.__callback_function is not None:
            index = selection[0]
            self.__callback_function(index)


class MainWindow:
    def __init__(self, root: Tk):
        self.__root = root
        self.__image_manager = ImageManager()
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_window = ttk.Frame(root)
        main_window.rowconfigure(0, weight=1)
        main_window.columnconfigure(0, weight=2)
        main_window.columnconfigure(1, weight=2)
        main_window.grid(row=0, column=0, sticky=(N, S, W, E))

        left_image_window = ScrollableImage(main_window, image=self.__image_manager.image)
        left_image_window.grid(row=0, column=0, sticky=(N, S, W, E))

        right_image_window = ScrollableImage(main_window, image=self.__image_manager.small_image)
        right_image_window.grid(row=0, column=1, sticky=(N, S, W, E))

#       Create menu bar

        root.option_add('*tearOff', FALSE)

        menu_bar = Menu(root)

        file_menu = Menu(menu_bar)
        file_menu.add_command(label='Open')
        file_menu.add_command(label='Save')
        file_menu.add_command(label="Save as...")

        simple_filters_menu = Menu(menu_bar)
        simple_filters_menu.add_command(label='Canny')

        menu_bar.add_cascade(menu=file_menu, label='File')
        menu_bar.add_cascade(menu=simple_filters_menu, label='Simple filters')

        root['menu'] = menu_bar

#       Create right panel
        main_window.columnconfigure(2, weight=1)
        right_panel = ttk.Frame(main_window)
        right_panel.grid(row=0, column=2, sticky=(N, S, W, E))
        right_panel.columnconfigure(0, weight=1)

#       Create parameters menu

        parameters_menu = ttk.Frame(right_panel)
        right_panel.rowconfigure(0, weight=1)
        parameters_menu.grid(row=0, column=0, sticky=(N, S, W, E))

        parameters_label = ttk.Label(parameters_menu, text='Parameters menu', anchor='center')
        parameters_label.grid(row=0, column=0, sticky=(W, E))

        parameters_separator = ttk.Separator(parameters_menu, orient='horizontal')
        parameters_separator.grid(row=1, column=0, sticky=(W, E))
        parameters_menu.columnconfigure(0, weight=1)

#       Queue panel menu

        queue_panel = ttk.Frame(right_panel)
        right_panel.rowconfigure(1, weight=1)
        queue_panel.rowconfigure(2, weight=1)
        queue_panel.grid(row=1, column=0, sticky=(N, S, W, E))

        queue_label = ttk.Label(queue_panel, text='Queue menu', anchor='center')
        queue_label.grid(row=0, column=0, sticky=(W, E))

        queue_separator = ttk.Separator(queue_panel, orient='horizontal')
        queue_separator.grid(row=1, column=0, sticky=(W, E))
        queue_panel.columnconfigure(0, weight=1)

        queue = ScrollableList(queue_panel)
        queue.callback_function = print
        queue.list = ["aaaaa", "bbbbbb"]
        queue.grid(row=2, column=0, sticky=(N, S, W, E))


if __name__ == '__main__':
    root = Tk()
    app = MainWindow(root)
    root.geometry("1000x500")
    root.mainloop()