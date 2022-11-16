import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

class Data():
    # data (new data is appended to arrays, first item popped when full)
    temperature = []
    humidity = []
    distance = []

    LIMIT = 100     # limit for number of data points
    t_0 = 0          # initial time
    t_h = 0

    # state machine variables
    state = "safe"                  # states: safe, warning, danger
    safe_temp = 19.68               # calibrate at the beginning of demo, should be room temperature
    hot_temp_diff = 1.5             # the amount over room_temp to be considered "hot"
    hot_temp = safe_temp + hot_temp_diff    # temperature considered to be "hot"
    time_hot = 0                    # variable for keeping track how long the temp has been recorded as hot
    acceptable_time_hot = 5         # parameter for how long the temp can be hot before going to danger state

    # visualization
    visualized = False

    def __init__(self) -> None:
        self.t0 = time.time()

    def visualization(self):
        # create and format the plot
        self.fig, self.ax = plt.subplots(3)
        title = ["Temperature", "Humidity", "Distance"]
        for i in range(3):
            self.ax[i].set_title(title[i])
            self.ax[i].get_xaxis().set_visible(False)

        print(len(self.temperature))
        # create plot
        self.time = range(len(self.temperature))
        self.lt, = self.ax[0].plot(self.time, self.temperature, color="red")
        self.lh, = self.ax[1].plot(self.time, self.humidity, color="blue")
        self.ld, = self.ax[2].plot(self.time, self.distance, color="green")

        self.fig.canvas.mpl_connect('close_event', self.on_close)
        self.visualized = True

        plt.show(block=False)
        plt.pause(0.001)

    def updateData(self, t, h, d):
        # remove excess data if necessary
        if(len(self.temperature) == self.LIMIT):
            self.temperature.pop(0)
            self.humidity.pop(0)
            self.distance.pop(0)

        # append new data
        self.temperature.append(t)
        self.humidity.append(h)
        self.distance.append(d)

        # resume animation
        if (self.visualized):
            self.updateGraph()

    def updateGraph(self):
        # update graph
        self.time = range(len(self.temperature))
        self.lt.set_xdata(self.time)
        self.lt.set_ydata(self.temperature)
        self.lh.set_xdata(self.time)
        self.lh.set_ydata(self.humidity)
        self.ld.set_xdata(self.time)
        self.ld.set_ydata(self.distance)

        # update x,y bound
        self.ax[0].relim() 
        self.ax[0].autoscale_view(True,True,True) 
        self.ax[1].relim() 
        self.ax[1].autoscale_view(True,True,True) 
        self.ax[2].relim() 
        self.ax[2].autoscale_view(True,True,True) 

        #print("updated")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_close(self, event):
        self.visualization = False


    def alarmLevel(self):
        latest_temp = self.temperature[-1]
        temp_is_low = (latest_temp < self.hot_temp)
        temp_is_high = (latest_temp >= self.hot_temp)

        # if in safe state, we can just check if temp still low or not
        if (self.state == "safe"):
            if (temp_is_low):
                self.state = "safe"
            elif (temp_is_high):
                # when temp is first recorded to be high, mark the time by resetting timer (time_hot)
                self.state = "warning"
                self.time_hot = 0
        
        # if we are in warning state for 5s, then change to danger
        elif (self.state == "warning"):
            self.time_hot += 1

            # if the temperature is low, move back to safe state
            if (temp_is_low):
                self.state = "safe"
                self.time_hot = 0
            # if the temperature is high, check how long the timer has been since we are in warning state
                # if less than threshold, stay in this state
                # if more than threshold, then move to danger state
            elif (temp_is_high):
                if (self.time_hot <= self.acceptable_time_hot):
                    self.state = "warning"
                elif (self.time_hot > self.acceptable_time_hot):
                    self.state = "danger"

        # if temp low, move straight back to safe state and reset timer
        elif (self.state == "danger"):
            self.time_hot += 1

            if (temp_is_low):
                self.state = "safe"
                self.time_hot = 0
            
            elif (temp_is_high):
                self.state = "danger"


        # for return value:
        if (self.state == "safe"):
            return 0
        if (self.state == "warning"):
            return 1
        if (self.state == "danger"):
            return 2
        
        
        return -1