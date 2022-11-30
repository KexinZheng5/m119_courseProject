import matplotlib.pyplot as plt
import datetime

class Data():
    # data (new data is appended to arrays, first item popped when full)
    temperature = []
    distance = []

    # timers
    t_snooze = datetime.timedelta(seconds = 0) # snooze count down
    t_yellow = datetime.timedelta(seconds = 0)    # timer starts when state is yellow
    calibrated = False                          # indicate whether the device has been calibrated

    LIMIT = 100     # limit for number of data points

    # state machine variables
    state = "safe"                                          # states: safe, warning, danger
    safe_temp = 0                                          # calibrate at the beginning of demo, should indicate what temperature is considered safe
    yellow_hot_temp_diff = 8                                # the amount over room_temp to transition from green -> yellow
    yellow_hot_temp = 0      # temperature considered to be enough to transition from green -> yellow
    red_hot_temp_diff = 13                                  # the amount over room_temp to transition from yellow -> red
    red_hot_temp = 0            # temperature considered to be enough to transition from yellow -> red
    
    acceptable_time_hot = datetime.timedelta(seconds = 10*60)                 # parameter for how long the temp can be hot before going to danger state
    safe_time_after_movement = datetime.timedelta(seconds = 3*60)             # parameter for how long the danger level is "safe" after movement detected
    safe_time_start = datetime.datetime.now()                          # variable for keeping track how long to be "safe" for after movement detected
    movement_threshold = 30                     # parameter for how much change in distance should be considered movement

    # visualization
    visualized = False


    # set, update, and get snooze countdown
    def setSnooze(self, time):
        self.t_snooze = datetime.timedelta(seconds = time * 60)

    def updateSnooze(self):
        self.t_snooze = self.t_snooze - datetime.timedelta(seconds = 1)

    def getSnooze(self):
        return self.t_snooze

    # set, update, and get yellow state timer
    def resetYellow(self):
        self.t_yellow = datetime.timedelta(seconds = 0)

    def updateYellow(self):
        self.t_yellow = self.t_yellow + datetime.timedelta(seconds = 1)

    def getYellow(self):
        return self.t_yellow

    def visualization(self):
        # create and format the plot
        self.fig, self.ax = plt.subplots(2)
        title = ["Temperature", "Distance"]
        for i in range(2):
            self.ax[i].set_title(title[i])
            self.ax[i].get_xaxis().set_visible(False)

        # create plot
        self.lt, = self.ax[0].plot(range(len(self.temperature)), self.temperature, color="red")
        self.ld, = self.ax[1].plot(range(len(self.distance)), self.distance, color="green")

        self.fig.canvas.mpl_connect('close_event', self.on_close)
        self.visualized = True

        plt.show(block=False)
        plt.pause(0.001)

    def updateTemperature(self, t):
        # remove excess data if necessary
        if(len(self.temperature) == self.LIMIT):
            self.temperature.pop(0)

        # append new data
        self.temperature.append(t)

        # resume animation
        if (self.visualized):
            self.updateGraph()

    def updateDistance(self, d):
        # remove excess data if necessary
        if(len(self.distance) == self.LIMIT):
            self.distance.pop(0)

        # append new data
        self.distance.append(d)

        # resume animation
        if (self.visualized):
            self.updateGraph()

    def updateGraph(self):
        # update graph
        self.lt.set_xdata(range(len(self.temperature)))
        self.lt.set_ydata(self.temperature)
        self.ld.set_xdata(range(len(self.distance)))
        self.ld.set_ydata(self.distance)

        # update x,y bound
        self.ax[0].relim() 
        self.ax[0].autoscale_view(True,True,True) 
        self.ax[1].relim() 
        self.ax[1].autoscale_view(True,True,True) 

        #print("updated")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_close(self, event):
        self.visualization = False


    # Runs the state machine to determine what level of danger
    def alarmLevel(self):
        # latest temperature recorded
        if((len(self.temperature)) > 0):
            # record room temperature if the device is not calibrated
            if(not self.calibrated):
                self.safe_temp = self.temperature[-1]
                self.yellow_hot_temp = self.safe_temp + self.yellow_hot_temp_diff
                self.red_hot_temp = self.safe_temp + self.red_hot_temp_diff   
                self.calibrated = True
            latest_temp = self.temperature[-1]
        else:
            return 0
        

        # distance_diff is 0 if there is only 1 data point and then it becomes the difference between most recent two points
        distance_diff = 0
        if(len(self.distance) > 1):
            distance_diff = abs(self.distance[-1] - self.distance[-2])
        
        # bool to determine whether the temp is currently "low" or "high"
        temp_is_safe = (latest_temp < self.yellow_hot_temp)
        temp_is_warning = (latest_temp >= self.yellow_hot_temp and latest_temp < self.red_hot_temp)
        temp_is_danger = (latest_temp >= self.red_hot_temp)

        # update safe_time_start if there is distance detected
        if (distance_diff > self.movement_threshold):
            self.safe_time_start = datetime.datetime.now()
        # if no distance detected, then decrement safe_time_after_movement if decrementable
        #else:
        #    if (self.safe_time_left > datetime.timedelta(seconds = 0)):
        #        self.safe_time_left = self.safe_time_left - datetime.timedelta(seconds = 1)

        # helper variable representing if someone is there
        movement_detected = self.safe_time_after_movement > datetime.datetime.now() - self.safe_time_start
        
        # if in safe state, we can just check if temp still low or not
        if (self.state == "safe"):
            if (temp_is_safe):
                self.state = "safe"
            elif (temp_is_warning or temp_is_danger):
                # when temp is first recorded to be high, change state to warning
                self.state = "warning"

        # if we are in warning state for > acceptable_time_hot amount of time change to danger
        elif (self.state == "warning"):
            # increment time yellow

            # if the temperature is low, move back to safe state
            if (temp_is_safe):
                self.state = "safe"
            # if the temperature is medium, check how long the timer has been since we are in warning state
                # if less than threshold, stay in this state
                # if more than threshold, then move to danger state
            if (temp_is_warning):
                if (self.getYellow() <= self.acceptable_time_hot):
                    self.state = "warning"
                elif (self.getYellow() > self.acceptable_time_hot):
                    self.state = "danger"
            # if temperature is too high, move to danger state immediately
            if (temp_is_danger):
                self.state = "danger"

        # in danger state
        elif (self.state == "danger"):
            # continue adding to yellow time

            # if temp low, move straight back to safe state and reset timer
            if (temp_is_safe):
                self.state = "safe"
            
            # ONLY if there was movement detected do we move down to warning state
            elif (movement_detected):
                self.state = "warning"

            # if temp is not safe and also there is no safe time, then stay in danger state
            else:
                self.state = "danger"

        # if movement detected, leave state as safe if safe, else change state to warning
        if (movement_detected):
            if (self.state == "safe"):
                self.state = "safe"
            elif (self.state == "warning" or self.state == "danger"):
                self.state = "warning"

        # for return value:
        if (self.state == "safe"):
            return 0
        if (self.state == "warning"):
            return 1
        if (self.state == "danger"):
            return 2
        
        return -1
