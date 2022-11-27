from tkinter import *
import data
 
class GUI():
    # window size
    window_width = 500
    window_height = 300
    popup_width = 400
    popup_height = 250
    popup = None
    badInput = None
    cbg = '#3d3d3d'
    ctext = '#ffffff'

    info = None

    d = data.Data()

    # timer labels
    lt1 = None
    lt2 = None
    timer_yellow = None
    timer_snooze = None


    def __init__(self):
        self.exit = False
        self.root = Tk()
        self.root.title("remote stove alarm")
        self.root.geometry(f'{self.window_width}x{self.window_height}')
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.resizable(False, False)

        frame = Frame(self.root, width=self.window_width-50, height=self.window_height-100, bg=self.cbg)
        frame.place(relx=0.5, rely=0, anchor=N)

        self.info = Label(self.root, text = "", bg=self.cbg, fg=self.ctext, font=('Arial 16'))
        self.info.place(relx=0.5, rely=0.5, anchor=CENTER)

        # add visualization button
        btn = Button(self.root, 
                    text="Data Visualization", 
                    bg=self.cbg,
                    fg=self.ctext,
                    activebackground="#5c5c5c",
                    activeforeground=self.ctext,
                    font=('Arial 13'),
                    borderwidth=0,
                    command=self.d.visualization)

        #btn2 = Button(self.root, text="popup test", command=self.popupAlert)
        btn.place(relx=0.8, rely=0.9, anchor=CENTER)
        #btn2.place(relx=0.5, rely=0.1, anchor=CENTER)

    def updateTemperature(self, t):
        self.d.updateTemperature(t)
        self.updateGUI()

    # update
    def updateDistance(self, d):
        self.d.updateDistance(d)
        self.updateGUI()
        
    def updateGUI(self):
        al = self.d.alarmLevel()
        match al:
            # safe
            case 0:
                self.root.configure(bg='#5f8733')
                self.info.configure(text="No heat detected")
            case 1:
                self.root.configure(bg='#e6b120')
                self.info.configure(text="Heat detected")
                if (self.lt1 == None):
                    self.updateYellow()
            case 2:
                self.root.configure(bg='#a8220d')
                self.info.configure(text="Unattended stove detected")
                if self.popup == None and self.lt2 == None:
                    self.popupAlert()
            case _:
                self.root.configure(bg='grey')
        self.root.update()

    # create alert popup window when temperature is high for too long
    def popupAlert(self):
        self.popup = Toplevel()
        self.popup.title("UNATTENDED STOVE!")
        self.popup.geometry(f'{self.popup_width}x{self.popup_height}')
        self.popup.resizable(False, False)
        self.popup.protocol("WM_DELETE_WINDOW", self.closePopup)

        # alert text
        msg = Label(self.popup, text = "Unattended stove detected!")
        msg.place(relx=0.5, rely=0.1, anchor=CENTER)

        # set snooze time
        msgs = Label(self.popup, text = "Set snooze time:")
        msgs.place(relx=0.5, rely=0.4, anchor=CENTER)

        # snooze time textbox
        self.minBox = Text(self.popup, height = 1, width = 5)
        self.minBox.place(relx=0.4, rely=0.5, anchor=CENTER)
        minTxt = Label(self.popup, text = "minute")
        minTxt.place(relx=0.6, rely=0.5, anchor=CENTER)

        # buttons
        snooze = Button(self.popup, text="Snooze", command=self.snooze)
        snooze.place(relx=0.5, rely=0.8, anchor=CENTER)

    def snooze(self):
        min = self.minBox.get("1.0", "end-1c")
        if min.isdigit():
            if(self.badInput != None):
                self.badInput.destroy()
            self.d.setSnooze(int(min))
            self.updateSnooze()
            self.closePopup()
        else:
            if(self.badInput == None):
                self.badInput = Label(self.popup, fg='red', text = "Please enter a valid number.")
                self.badInput.place(relx=0.5, rely=0.6, anchor=CENTER)

    def updateSnooze(self):
        # display timer
        t = str(self.d.getSnooze())
        if self.lt2 == None:
            self.lt2 = Label(self.root, text = "Snooze count down", bg=self.cbg, fg=self.ctext, font=('Arial 13'))
            self.lt2.place(relx=0.25, rely=0.1, anchor=CENTER)
            self.timer_snooze = Label(self.root, text = t, bg=self.cbg, fg=self.ctext, font=('Arial 13'))
            self.timer_snooze.place(relx=0.25, rely=0.2, anchor=CENTER)
        else:
            self.timer_snooze.config(text = t)

        # update
        if t == "0:00:00":
            self.lt2.destroy()
            self.timer_snooze.destroy()
            self.lt2 = None
        else:
            self.d.updateSnooze()
            self.root.after(1000, self.updateSnooze)


    def updateYellow(self):
        # display timer
        t = str(self.d.getYellow())
        if self.lt1 == None:
            self.lt1 = Label(self.root, text = "Time since heat detected", bg=self.cbg, fg=self.ctext, font=('Arial 13'))
            self.lt1.place(relx=0.73, rely=0.1, anchor=CENTER)
            self.timer_yellow = Label(self.root, text = t, bg=self.cbg, fg=self.ctext, font=('Arial 13'))
            self.timer_yellow.place(relx=0.73, rely=0.2, anchor=CENTER)
        else:
            self.timer_yellow.config(text = t)

        # update
        if self.d.alarmLevel() == 0: 
            self.lt1.destroy()
            self.timer_yellow.destroy()
            self.d.resetYellow()
            self.lt1 = None
        else:
            self.d.updateYellow()
            self.root.after(1000, self.updateYellow)
    
    def closePopup(self):
        self.popup.destroy()
        self.popup = None

    def onClose(self):
        print("exiting...")
        self.exit = True
        self.root.destroy()