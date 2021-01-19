from tkinter import Tk
from gui import MainWindow
if __name__ == '__main__':
    root = Tk()
    root.title('Image tester')
    app = MainWindow(root)
    root.minsize(1000, 500)
    root.geometry("1000x500")
    root.mainloop()
