from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from tkinter.scrolledtext import ScrolledText
from PIL import Image
from PIL import ImageTk
import cv2
from image_manager import ImageManager
from parameters_gui import CannyMenu, MedianBlur, GeneralBlurMenu, BilateralFilterMenu, GlobalThresholdMenu, AdaptiveThresholdMenu, GradientMenu, HaarCascadeMenu, ShapePredictorMenu


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

        self.__list_box.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

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

        self.__face_detected = False
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
        edit_menu.add_command(label='Undo', command=self.undo)
        edit_menu.add_command(label='Rotate 90° ↷', command=self.gui_update_wrapper(self.__image_manager.rotate_by_90, True))
        edit_menu.add_command(label='Rotate 180° ↷', command=self.gui_update_wrapper(self.__image_manager.rotate_by_180, True))
        edit_menu.add_command(label='Rotate -90° ↶', command=self.gui_update_wrapper(self.__image_manager.rotate_by_270, True))
        edit_menu.add_command(label="Grayscale", command=self.gui_update_wrapper(self.__image_manager.to_grayscale, True))
        menu_bar.add_cascade(menu=edit_menu, label='Edit')

        blurs_menu = Menu(menu_bar)
        blurs_menu.add_command(label='Median Blur', command=lambda: self.show_parameters_panel(self.__median_blur_menu))
        blurs_menu.add_command(label="Gaussian Blur", command=lambda: self.show_parameters_panel(self.__gaussian_blur_menu))
        blurs_menu.add_command(label='Averaging', command=lambda: self.show_parameters_panel(self.__averaging_blur_menu))
        blurs_menu.add_command(label='Bilateral Filter', command=lambda: self.show_parameters_panel(self.__bilateral_filter_menu))
        menu_bar.add_cascade(menu=blurs_menu, label='Blurs')

        threshold_menu = Menu(menu_bar)
        threshold_menu.add_command(label='Global Threshold', command=lambda: self.show_parameters_panel(self.__global_threshold_menu))
        threshold_menu.add_command(label='Adaptive Mean Threshold', command=lambda: self.show_parameters_panel(self.__adaptive_mean_threshold_menu))
        threshold_menu.add_command(label='Adaptive Gaussian Threshold', command=lambda: self.show_parameters_panel(self.__adaptive_gauss_threshold_menu))
        menu_bar.add_cascade(menu=threshold_menu, label='Threshold')

        gradient_menu = Menu(menu_bar)
        gradient_menu.add_command(label='Sobel X', command=lambda: self.show_parameters_panel(self.__sobel_x_menu))
        gradient_menu.add_command(label='Sobel Y', command=lambda: self.show_parameters_panel(self.__sobel_y_menu))
        gradient_menu.add_command(label='Laplacian', command=lambda: self.show_parameters_panel(self.__laplacian_menu))
        menu_bar.add_cascade(menu=gradient_menu, label='Gradient')

        advanced_menu = Menu(menu_bar)
        advanced_menu.add_command(label='Canny', command=lambda: self.show_parameters_panel(self.__canny_menu))
        advanced_menu.add_command(label='Histogram', command=self.show_histogram)
        face_detection_menu = Menu(advanced_menu)
        face_detection_menu.add_command(label='Haar Cascade Face Detection', command=lambda: self.show_parameters_panel(self.__haar_menu))
        face_detection_menu.add_command(label='Facial Landmarks Detection', command=lambda: self.show_parameters_panel(self.__shape_predictor_menu))
        advanced_menu.add_cascade(menu=face_detection_menu, label='Face Detection')
        menu_bar.add_cascade(menu=advanced_menu, label='Advanced')

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

        main_window.columnconfigure(2, minsize=180)
        right_panel = ttk.Notebook(main_window)
        right_panel.grid(row=0, column=2, sticky=(N, S, W, E))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        #       Create parameters menu (notebook)
        self.__active_menu = None

        self.__parameters_menu = ttk.Frame(right_panel)
        right_panel.add(self.__parameters_menu, text='parameters')

        parameters_separator = ttk.Separator(self.__parameters_menu, orient='horizontal')
        parameters_separator.grid(row=0, column=0, sticky=(W, E))
        self.__parameters_menu.columnconfigure(0, weight=1)

        self.__canny_menu = CannyMenu(self.__parameters_menu)
        self.__canny_menu.callback = self.gui_update_wrapper(self.__image_manager.canny)

        self.__median_blur_menu = MedianBlur(self.__parameters_menu)
        self.__median_blur_menu.callback = self.gui_update_wrapper(self.__image_manager.median_blur)

        self.__gaussian_blur_menu = GeneralBlurMenu(self.__parameters_menu, 'Gaussian blur')
        self.__gaussian_blur_menu.callback = self.gui_update_wrapper(self.__image_manager.gaussian_blur)

        self.__averaging_blur_menu = GeneralBlurMenu(self.__parameters_menu, 'Averaging')
        self.__averaging_blur_menu.callback = self.gui_update_wrapper(self.__image_manager.averaging_blur)

        self.__bilateral_filter_menu = BilateralFilterMenu(self.__parameters_menu)
        self.__bilateral_filter_menu.callback = self.gui_update_wrapper(self.__image_manager.bilateral_filter)

        self.__global_threshold_menu = GlobalThresholdMenu(self.__parameters_menu)
        self.__global_threshold_menu.callback = self.gui_update_wrapper(self.__image_manager.global_threshold)

        self.__adaptive_mean_threshold_menu = AdaptiveThresholdMenu(self.__parameters_menu, 'Adaptive Mean Threshold')
        self.__adaptive_mean_threshold_menu.callback = self.gui_update_wrapper(self.__image_manager.mean_threshold)

        self.__adaptive_gauss_threshold_menu = AdaptiveThresholdMenu(self.__parameters_menu, 'Adaptive Gauss Threshold')
        self.__adaptive_gauss_threshold_menu.callback = self.gui_update_wrapper(self.__image_manager.gaussian_threshold)

        self.__sobel_x_menu = GradientMenu(self.__parameters_menu, 'Sobel X')
        self.__sobel_x_menu.callback = self.gui_update_wrapper(self.__image_manager.sobel_x)

        self.__sobel_y_menu = GradientMenu(self.__parameters_menu, 'Sobel Y')
        self.__sobel_y_menu.callback = self.gui_update_wrapper(self.__image_manager.sobel_y)

        self.__laplacian_menu = GradientMenu(self.__parameters_menu, 'Laplacian')
        self.__laplacian_menu.callback = self.gui_update_wrapper(self.__image_manager.laplacian)

        self.__haar_menu = HaarCascadeMenu(self.__parameters_menu)
        self.__haar_menu.callback = self.gui_detect_wrapper(self.__image_manager.haar_face_detection)

        self.__shape_predictor_menu = ShapePredictorMenu(self.__parameters_menu)
        self.__shape_predictor_menu.callback = self.gui_detect_wrapper(self.__image_manager.dlib_face_shape_prediction)

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

        #       binds

        root.bind('<Control-z>', self.undo)

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
            self.__left_image_window.image = self.__image_manager.image if not self.__face_detected else self.__image_manager.image_with_faces
            if self.__queue.get_selection() == ():
                self.__right_image_window.image = self.__image_manager.manipulated_image
            else:
                self.__right_image_window.image = self.__image_manager.get_prev_image(self.__queue.get_selection()[0])

    def show_prev_image(self, i):
        self.__right_image_window.image = self.__image_manager.get_prev_image(i)

    def refresh_image_and_commands(self):
        if self.__face_detected:
            self.__left_image_window.image = self.__image_manager.image
            self.__face_detected = False
        self.__right_image_window.image = self.__image_manager.manipulated_image
        self.__queue.list = self.__image_manager.prev_commands

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
                scale = messagebox.askyesno(title="Scale Image?", message="Do you want to save image with CUSTOM "
                                                                          "scale? If so you may expect decrease of"
                                                                          " quality")
                self.__image_manager.save_image(filename, scale, self.__queue.get_selection())
            else:
                self.__image_manager.save_image(filename, False, self.__queue.get_selection())

    def show_parameters_panel(self, panel):
        if self.__active_menu is not None:
            self.__active_menu.grid_forget()
        self.__active_menu = panel
        panel.grid(row=1, column=0, sticky=(N, S, W, E))

    def gui_update_wrapper(self, function, always_accept=False):
        def wrapper(*args):
            success, error_message = function(*args)
            self.__status_bar.configure(text=f"status: {error_message}")
            self.refresh_image_and_commands()

        def always_accept_wrapper(*args):
            success, error_message = function(*args, accept=True)
            self.__status_bar.configure(text=f"status: {error_message}")
            self.refresh_image_and_commands()

        if always_accept:
            return always_accept_wrapper
        else:
            return wrapper

    def gui_detect_wrapper(self, function):
        def wrapper(*args):
            success, error_message = function(*args)
            self.__status_bar.configure(text=f"status: {error_message}")
            if success:
                self.__face_detected = True
                self.__left_image_window.image = self.__image_manager.image_with_faces
                self.__right_image_window.image = self.__image_manager.get_prev_image(-1)
        return wrapper

    def undo(self, event=None):
        success, error_message = self.__image_manager.undo()
        if success:
            self.__face_detected = False
            self.refresh_image_and_commands()
        self.__status_bar.configure(text=f"status: {error_message}")

    def show_histogram(self):
        selection = self.__queue.get_selection()
        num = None if selection == () else selection[0]
        self.__image_manager.display_histogram(num)
