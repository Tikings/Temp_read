import time
import tkinter as tk
import serial
from tkinter import ttk, font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import threading
import sv_ttk


class GUI(tk.Tk):
    '''
    '''

    def __init__(self, *, path : str ,title: str = 'Temperature in real time', min_size: 'tuple[int, int]' = (300, 100), port : str = "/dev/cu.usbserial-0001",baudrate : int = 115200) -> None:
        
        #Colors 
        
        
        super().__init__()
        
        self.ON_BUTTON_STR = 'ON'
        self.OFF_BUTTON_STR = 'OFF'
        self.ON_COLOR = '#03fc24'
        self.OFF_COLOR = '#fc0303'
        
        #Definition od the serial communication
        self._ser = serial.Serial(baudrate = baudrate,port = port,timeout = 1)
        
        self._recording = False # We don't record at the beginning
        
        self.start = time.time()
        self.path = path #To save the data
        self._data_saved = False # Data have been saved
        
        # Initialize the application
        
        self.__initialise_window(title, min_size)
        self.__create_widgets()
        
        #Dataframe to store the data
        self._data : type[pd.DataFrame] = pd.DataFrame(columns = ['hour',"time","resistance"])
        
        
        # Keep alive the GUI and do whatever periodic update to the screen
        self.after(30, self.__update)

    def __initialise_window(self, title, min_size):
        self.title(title)
        self.minsize(*min_size)
        
    def __create_widgets(self):
        '''
        Create all graphical elements
        '''
        self.__create_recording_button()  #To start end recording
        self.__create_received_msg_label() #To display the last recorded value 
        self.__create_save_button() #To save the data
        self.__create_reset_button() #To reset the data
        

    def __create_recording_button(self):
        
        self._btn_state_txt = tk.StringVar(value=self.OFF_BUTTON_STR)
        self._on_off_btn = tk.Button(self, textvariable=self._btn_state_txt, bg=self.OFF_COLOR, command=self.__on_led_btn_click_cb)
        self._on_off_btn.place(relx=0.3, rely=0.2, relwidth=0.4)
    
    def __create_save_button(self):
        self._btn_save_txt = tk.StringVar(value="Save")
        self._save_btn = tk.Button(self, textvariable=self._btn_save_txt, bg="red", command=self._save_data)
        self._save_btn.place(relx=0.1,rely=0.9,relwidth=0.4)
    
    def __create_reset_button(self): 
        
        self._btn_reset_txt = tk.StringVar(value="Reset")
        self._reset_btn = tk.Button(self, textvariable=self._btn_reset_txt, bg="red", command=self._reset_data)
        self._reset_btn.place(relx=0.5,rely=0.9,relwidth=0.4)

    def __create_received_msg_label(self):
        self._received_msg_label = tk.StringVar(value='Nothing yet...')
        tk.Label(self, textvariable=self._received_msg_label).place(relx=0.01, rely=0.7, relwidth=0.98)
        
    def _recorded_data(self):
        return not self._data == pd.DataFrame(columns = ["hour","time","resistance"])

    def _save_data(self):
        #Measuring the time at which the time have been saved
        if self._recorded_data:
            time_read = time.localtime()
            save_time = str(time_read.tm_hour) + str(time_read.tm_min) + str(time_read.tm_sec)   # Ex: 12:36:34 -> 123634    
            self._data.to_json(self.path+"data_temp_{}.json".format(save_time))
            self._data_saved = True
            print(f"Data saved at : {self.path!s}")
        else: 
            print("Nothing to save...")
        
        
    def _reset_data(self):
        if self._data_saved : 
            self._data : type[pd.DataFrame] = pd.DataFrame(columns = ["hour","time","resistance"])
            print(f"{self._data = !s} Reset")
        elif self._recorded_data and not self._data_saved : 
            print(f"Data not saved you fucking idiot")


    # -------------------- #
    #  On events callbacks #
    # -------------------- #

    def __on_closing_cb(self):
        '''
        Callback to the click on (X) event
        '''
        self._ser.close()
        #self._end_signal = True
        #self._msgs_thread_handle.join(0.1)
        self.destroy()

    def __on_led_btn_click_cb(self, *args):
        '''
        '''
        led_on = self._btn_state_txt.get() == self.OFF_BUTTON_STR

        # Update the button text
        self._btn_state_txt.set(self.ON_BUTTON_STR if led_on else self.OFF_BUTTON_STR)
        self._on_off_btn['bg'] = self.ON_COLOR if led_on else self.OFF_COLOR

        # This should be in accordance to what the other end is expecting
        self._recording = True if self._btn_state_txt.get() == "ON" else False
        self.start = time.time() if self._btn_state_txt.get() == "ON" else self.start
        
        self._state_read = self._btn_state_txt.get()[1] # N : 78 or F : 70 
        b = bytes(self._state_read,encoding = "utf-8")
        with self._ser as ser :
            ser.write(b)


    # ------------------------------- #
    #  Update the screen periodically #
    # ------------------------------- #


    #def __create_canvas(self):
        
        ## To create a tk inter box
        
     #   self.canvas = tk.Canvas(self)
      #  self.figure = plt.figure()
       # self.ax = plt.axes(self.figure)
       # self.fig_canvas = FigureCanvasTkAgg(self.figure, master=self.canvas)
       # self.fig_canvas.draw()
       # self.fig_canvas.get_tk_widget().pack()
       # self.canvas.place(relx=0.5,rely=0.5,relwidth=0.4,relheight=0.4)
        
    #def __update_tk_canvas(self):
        
    #    self.fig_canvas.get_tk_widget.destroy()
    #    self.ax.clear()
        
    #    self._data.plot(kind="line",ax=self.ax)
        
    #    self.fig_canvas = FigureCanvasTkAgg(self.figure, master=self.canvas)
    #    self.fig_canvas.draw()
    #    self.fig_canvas.get_tk_widget().pack()
    #    self.fig_canvas.draw()
    #    self.fig_canvas.get_tk_widget().pack()
    #    self.canvas.place(relx=0.5,rely=0.5,relwidth=0.4,relheight=0.4)
        
    def _record_temp_read(self,string):
        
        time_recorded = time.time()
        diff_time = time_recorded - self.start
        time_read = time.localtime()
        to_insert_read_time = str(time_read.tm_hour) + str(time_read.tm_min) + str(time_read.tm_sec)  
        string = string.replace("\r","")
        line_to_insert = pd.DataFrame(
            {   "hour" : [to_insert_read_time],
                "time" : [diff_time],
                "resistance" : [string]
            }
        )
        print(line_to_insert)
        self._data = pd.concat([self._data,line_to_insert],ignore_index=True)
        
        
    def _asking_temperature(self) -> None | str : 
        
        string = None
        pattern = br"R = [0-9]{4}.[0-9]{2}"
        with self._ser as ser:
            read = ser.readline()
        if read:
            
            string = read.decode(errors = "ignore")
            print(string)
            string = string.replace("R = ","")
            string = string.replace("\n","")
        return string
        
    def __update(self):
        
        resistance = self._asking_temperature()
        
        if resistance and self._recording : 
            self._record_temp_read(resistance)
        prt = f"{resistance = !s}"
        self._received_msg_label.set(prt)
        print(prt)
        
        self.after(30,self.__update)
        
        '''
        This is called each 1ms to update the GUI elements and do periodic actions
        '''
        return