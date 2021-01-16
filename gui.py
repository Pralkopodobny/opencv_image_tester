from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from tkinter.scrolledtext import ScrolledText
from PIL import Image
from PIL import ImageTk
import cv2
from image_manager import ImageManager
from parameters_gui import CannyMenu


class ScrollableImage(ttk.Frame):
    def __init__(self, master=None, **kw):
        self.__image = kw.pop('image', None)
        super(ScrollableImage, self).__init__(master=master, **kw)
        self.cnvs = Canvas(self, highlightthickness=0, **kw)
        self.__shape = self.cnvs.create_image(0, 0, anchor='nw', image=self.__image)
        self.v_scroll = ttk.Scrollbar(self, orient='vertical')
        self.h_scroll = ttk.Scrollbar(self, orient='horizontal')
        self.cnvs.grid(row=0, column=0, sticky='nsew')
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

        self.__list_box = Listbox(self, listvariable=self.__elements_var)
        self.__list_box.grid(row=0, column=0, sticky=(N, S, W, E))

        v_scroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.__list_box.yview)
        v_scroll.grid(row=0, column=1, sticky=(N, S))

        h_scroll = ttk.Scrollbar(self, orient=HORIZONTAL, command=self.__list_box.xview)
        h_scroll.grid(row=1, column=0, sticky=(W, E))

        self.__list_box.bind("<<ListboxSelect>>", self.__callback)

    @property
    def list(self):
        return self.__elements

    @list.setter
    def list(self, new_list):
        self.__elements = new_list
        self.__elements_var.set(self.__elements)
        self.clear_selection()

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

    def clear_selection(self):
        self.__list_box.selection_clear(0, END)

    # returns () if nothing selected
    def get_selection(self):
        return self.__list_box.curselection()


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

        #       Create scrollable images

        self.__left_image_window = ScrollableImage(main_window, image=self.__image_manager.image)
        self.__left_image_window.grid(row=0, column=0, sticky=(N, S, W, E))

        self.__right_image_window = ScrollableImage(main_window, image=self.__image_manager.manipulated_image)
        self.__right_image_window.grid(row=0, column=1, sticky=(N, S, W, E))

        #       Create menu bar

        root.option_add('*tearOff', FALSE)

        menu_bar = Menu(root)

        file_menu = Menu(menu_bar)
        file_menu.add_command(label='Open', command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_image_as)
        menu_bar.add_cascade(menu=file_menu, label='File')

        edit_menu = Menu(menu_bar)
        edit_menu.add_command(label='Rotate 90° ↷', command=self.rotate_by_90)
        edit_menu.add_command(label='Rotate 180° ↷', command=self.rotate_by_180)
        edit_menu.add_command(label='Rotate -90° ↶', command=self.rotate_by_270)
        menu_bar.add_cascade(menu=edit_menu, label='Edit')

        simple_filters_menu = Menu(menu_bar)
        simple_filters_menu.add_command(label='Canny')
        menu_bar.add_cascade(menu=simple_filters_menu, label='Simple filters')

        root['menu'] = menu_bar

        #       Create status bar with scale

        self.__scale_var = StringVar()
        self.__scale_val = 100
        self.__scale_var.set("100%")

        bottom_panel = ttk.Frame(main_window)
        bottom_panel.columnconfigure(0, weight=1)
        bottom_panel.grid(row=1, column=0, sticky=(W, E), columnspan=3)

        self.__status_bar = ttk.Label(bottom_panel, text="status:", anchor="w")
        self.__status_bar.grid(row=0, column=0, sticky=(E, W))

        scale_label = ttk.Label(bottom_panel, textvariable=self.__scale_var)
        scale_label.grid(row=0, column=1)

        scale = ttk.Scale(bottom_panel, from_=1, to=200, orient=HORIZONTAL, command=self.scale_image)
        scale.set(100)
        scale.grid(row=0, column=2)

        #       Create right panel (notebook)

        #main_window.columnconfigure(2, weight=1)
        right_panel = ttk.Notebook(main_window)
        right_panel.grid(row=0, column=2, sticky=(N, S, W, E))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        #       Create parameters menu (notebook)

        parameters_menu = ttk.Frame(right_panel)
        right_panel.add(parameters_menu, text='parameters')

        parameters_label = ttk.Label(parameters_menu, text='Parameters menu', anchor='center')
        parameters_label.grid(row=0, column=0, sticky=(W, E))

        parameters_separator = ttk.Separator(parameters_menu, orient='horizontal')
        parameters_separator.grid(row=1, column=0, sticky=(W, E))
        parameters_menu.columnconfigure(0, weight=1)

        self.__canny_menu = CannyMenu(parameters_menu)
        self.__canny_menu.grid(row=2, column=0, sticky=(N, S, W, E))
        parameters_menu.rowconfigure(2, weight=1)

        #       Create queue menu (notebook)

        queue_panel = ttk.Frame(right_panel)
        right_panel.add(queue_panel, text='commands')

        queue_label = ttk.Label(queue_panel, text='Queue menu', anchor='center')
        queue_label.grid(row=0, column=0, sticky=(W, E))

        queue_separator = ttk.Separator(queue_panel, orient='horizontal')
        queue_separator.grid(row=1, column=0, sticky=(W, E))
        queue_panel.columnconfigure(0, weight=1)
        queue_panel.rowconfigure(2, weight=1)

        self.__queue = ScrollableList(queue_panel)
        self.__queue.callback_function = self.show_prev_image
        self.__queue.list = self.__image_manager.prev_commands
        self.__queue.grid(row=2, column=0, sticky=(N, S, W, E))

    def open_file(self):
        filename = fd.askopenfilename(title="Select image", filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png")))
        if filename != "":
            if re.match(r".*?((\.jpg)|(\.png))", filename) is None:
                print(re.match(r".*?((\.jpg)|(\.png))", filename))
                messagebox.showerror(title="Error", message="File format is incorrect\nFilename must "
                                                            "end with .png or .jpg")
                return
            answer = messagebox.askyesno(title="Open Image", message="Do you want to open new Image? "
                                                                     "All unsaved work will be lost!")
            if answer is True:
                self.__image_manager.open_image_from_path(filename)
                self.__left_image_window.image = self.__image_manager.image
                self.__right_image_window.image = self.__image_manager.manipulated_image
                self.__queue.list = self.__image_manager.prev_commands
                self.__queue.clear_selection()

    def scale_image(self, scale):
        scale_temp_int = int(getdouble(scale))
        if scale_temp_int != self.__scale_val:
            self.__scale_val = scale_temp_int
            self.__scale_var.set(str(self.__scale_val) + "%")
            self.__image_manager.scale = scale_temp_int
            self.__left_image_window.image = self.__image_manager.image
            if self.__queue.get_selection() == ():
                self.__right_image_window.image = self.__image_manager.manipulated_image
            else:
                self.__right_image_window.image = self.__image_manager.get_prev_image(self.__queue.get_selection()[0])

    def rotate_by_90(self):
        self.__image_manager.rotate_by_90()
        self.__right_image_window.image = self.__image_manager.manipulated_image
        self.__queue.list = self.__image_manager.prev_commands

    def rotate_by_180(self):
        self.__image_manager.rotate_by_180()
        self.__right_image_window.image = self.__image_manager.manipulated_image
        self.__queue.list = self.__image_manager.prev_commands

    def rotate_by_270(self):
        self.__image_manager.rotate_by_270()
        self.__right_image_window.image = self.__image_manager.manipulated_image
        self.__queue.list = self.__image_manager.prev_commands

    def show_prev_image(self, i):
        self.__right_image_window.image = self.__image_manager.get_prev_image(i)

    def save_image_as(self):
        filename = fd.asksaveasfile(title="Save as...", filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png")))

        if filename is not None:
            filename = filename.name
            if re.match(r".*?((\.jpg)|(\.png))", filename) is None:
                print(re.match(r".*?((\.jpg)|(\.png))", filename))
                messagebox.showerror(title="Incorrect name", message=f"Path:{filename} is incorrect\nFilename must end "
                                                                     f"with .png or .jpg")
                return
            if self.__scale_val != 100:
                scale = messagebox.askyesno(title="Scale Image?", message="Do you want to save image with default "
                                                                          "scale? If not you may expect decrease of"
                                                                          " quality")
                self.__image_manager.save_image(filename, scale, self.__queue.get_selection())
            else:
                self.__image_manager.save_image(filename, False, self.__queue.get_selection())


if __name__ == '__main__':
    root = Tk()
    app = MainWindow(root)
    root.minsize(1000, 500)
    root.geometry("1000x500")
    root.mainloop()
