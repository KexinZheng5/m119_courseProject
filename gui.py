from tkinter import *
import data
 
class GUI():
    # window size
    window_width = 500
    window_height = 500

    d = data.Data()


    def __init__(self):
        self.exit = False
        self.root = Tk()
        self.root.title("stove alarm")
        self.root.geometry(f'{self.window_width}x{self.window_height}')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # add visualization button
        btn = Button(self.root, text="Data Visualization", command=self.d.visualization)
        btn.pack()

    def updateData(self, t, h, d):
        self.d.updateData(t, h, d)
        al = self.d.alarmLevel()
        match al:
            case 0:
                self.root.configure(bg='green')
            case 1:
                self.root.configure(bg='yellow')
            case 2:
                self.root.configure(bg='red')
            case _:
                self.root.configure(bg='grey')
        self.root.update()

    def on_close(self):
        print("exiting...")
        self.exit = True
        self.root.destroy()