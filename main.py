import machine, neopixel
from machine import Pin
from SSD1306_Custom_Font import SSD1306
from rotary_irq_rp2 import RotaryIRQ
from button import Button
from dht import DHT22
import utime as time
from machine import Timer, I2C
from PID import PID
import _thread


class Display:
    """
    Writes the temperature, humidity and time to the display and handles animation of it.
    """
    def __init__(self):
        i2c = I2C(sda=0, scl=1)
        self.display=SSD1306(i2c)
        self.display.load_fonts("digits-30", "icons-32", "text-16")
        self.temp = 0
        self.hum = 0
        self.visible = {'temp': True, 'hum': True, 'time': True} # Used for animations
        self.selected = 'none'
        self.time_m = 0
        self.blink_speed = 2 # lowest is fastest from 1 to infinity
        self.switch_counter = 0

    def _clear(self):
        self.display.fill(0)
    
    def _display_temp(self):
        self.display.select_font('digits-30')
        degrees = '\u00b0'  # Character code for the degrees symbol
        self.display.text(f'{self.temp:.1f}{degrees}', 0, 0)        
        self.display.select_font('icons-32')
        if self.visible['temp']:
            self.display.text('t', 100, 0)          # The 't' character contains the temperature icon                

    def _display_hum(self):
        self.display.select_font('digits-30')                
        self.display.text(f'{self.hum:.0f}', 0, 33)
        self.display.select_font('icons-32')     
        if self.visible['hum']:   
            self.display.text('h', 46, 33)         # The 'h' character contains the humidity icon
    
    def _display_time_left(self):
        self.display.select_font('text-16')        
        time_string = f'{self.time_m//60}'
        time_string += ':' if self.visible['time'] else ' '
        time_string += f'{self.time_m%60:02}h'
        self.display.text(time_string, 80,42)      

    def _update(self):
        self._clear()
        
        if self.selected == 'temp':
            self.switch_counter +=1
            if self.switch_counter == self.blink_speed:
                self.visible['temp'] = not self.visible['temp'] 
                self.switch_counter = 0
        self._display_temp()                   
        
        if self.selected == 'hum':
            self.switch_counter +=1
            if self.switch_counter == self.blink_speed:
                self.visible['hum'] = not self.visible['hum'] 
                self.switch_counter = 0
        self._display_hum()
        
        if self.selected == 'time':
            self.switch_counter +=1
            if self.switch_counter == self.blink_speed:
                self.visible['time'] = not self.visible['time'] 
                self.switch_counter = 0
        self._display_time_left()
        self.display.show()

    def select(self, item):
        assert item in ['temp', 'hum', 'time', 'none'], f"unkown item {item}"
        self.visible[self.selected] = True # make sure the previously selected item is visible
        self.selected = item
        if self.selected == 'none':
            self.visible = {'temp': True, 'hum': True, 'time': True}
            self.switch_counter = 0

    def set_temp(self, temp):
        self.temp = temp

    def set_hum(self, hum):
        self.hum = hum

    def set_time(self, minutes):
        self.time_m = minutes 

    def get_time_minutes(self):
        return self.time_m


class PID_controller:
    # controls the heater via PID and time power modulation, controls the fan via hysteresis
    def __init__(self,p,i,d,control_window_size=10,sensor_read_interval=1, hum_hyst =1) -> None:
        self.sensor = DHT22(Pin(8))      
        self.blower_fan  = Pin(6, Pin.OUT)
        self.heater      = Pin(7, Pin.OUT)

        self.target_hum = 20
        self.target_temp = 60
        self.hum_hyst = hum_hyst
        
        self.control_window_size = control_window_size # control window size in ms        

        self.temp_pid = PID(Kp=p, Ki=i, Kd=d, setpoint=self.target_temp) # PID for temperature
        self.temp_pid.output_limits = (0, control_window_size//2) # ms to turn on the heater
        self.next_heating_cycle_duration = 0 # How long the heater will be on in the next cycle (in seconds)
        self.last_temp = 0
        self.last_hum = 0

        self.thread_exited = False
        self._running =False
        self._heatup=False

        self.sensor_read_interval = sensor_read_interval
        
    def _measure(self):    
        self.sensor.measure()    
        self.last_temp = self.sensor.temperature()
        self.last_hum = self.sensor.humidity()
        print(f"measured {self.last_temp}C, {self.last_hum}%")
        self.next_heating_cycle_duration = self.temp_pid(self.last_temp)
        print(self.next_heating_cycle_duration)
        self.next_heating_cycle_duration = int(self.next_heating_cycle_duration)

    def set_target_temp(self, target_temp):
        self.temp_pid.setpoint = target_temp
        self.target_temp = target_temp
        
    def set_target_hum(self, target_hum):
        self.target_hum = target_hum

    # starts the control thread
    def start(self):
        """Starts the control loop in a new thread."""
        if self._running:
            print("already running. So ignored. self._running=",self._running)
            return
        self._running = True
        print("pid thread started")
        self._thread_id = _thread.start_new_thread(self._control_loop, ())

    # stops the control thread
    def stop(self):
        """Stops the control loop thread."""
        self._running = False
        # only return when the thread has actually exited
        while not self.thread_exited:
            time.sleep_ms(10)

    # allows us to sleep but wake up if the thread is stopped
    def _measure_and_sleep(self, duration_s):
        end_time = time.ticks_add(time.ticks_ms(), duration_s * 1000)
        while time.ticks_diff(end_time, time.ticks_ms()) > 0 and self._running:
            self._measure()
            time.sleep(self.sensor_read_interval)

    def start_heating(self):
        self._heatup=True

    def stop_heating(self):
        self._heatup=False

    def _control_loop(self):
        try:
            while self._running:
                # Turn on the heater for the duration specified by the PID controller
                if self._heatup and self.next_heating_cycle_duration > 0: # only turn on if more than 1 second
                    self.heater.value(1)
                    print(f"turning on heater for {self.next_heating_cycle_duration} seconds.")
                    if self.last_hum > self.target_hum + self.hum_hyst and self.target_temp - self.last_temp < 5: # pull in some air to reduce humidity only if temp is not too far from target to avoid a kind of deadlock                        
                        print("pulling air with blower")
                        self.blower_fan.value(1)
                    self._measure_and_sleep(self.next_heating_cycle_duration)
                    self.heater.value(0)                        
                # Wait for the remainder of the control window            
                sleep_duration = self.control_window_size - self.next_heating_cycle_duration
                self._measure_and_sleep(sleep_duration)
                self.blower_fan.value(0)
        except Exception as e:
            print("Error reading sensor:", e)
        finally:
            # Safety: turn off heater and fan if there is an error
            self.blower_fan.value(0)
            self.heater.value(0)
            self.next_heating_cycle_duration = 0        
            self.thread_exited = True
            self._running =False
            print("PID thread exited")

class Controller:
    def __init__(self):
        self.pid_controller = PID_controller(p=5,i=0, d=20, control_window_size=10, sensor_read_interval=1)
        self.pid_controller.start()
        self.display = Display()   
        self.rotary_sw = Button(pin=2, debounce_ms=5, handler=self._rotary_button_handler)
        self.start_sw = Button(pin=5, debounce_ms=5, handler=self._start_button_handler)
        self.rotary = RotaryIRQ(pin_num_clk=4, pin_num_dt=3,min_val=0, 
              max_val=5, 
              reverse=False, 
              range_mode=RotaryIRQ.RANGE_WRAP)
        self.rotary.add_listener(self._rotary_handler)
        self.mode = 'idle' # idle, running
        self.selected = 'none' # none, temp, hum, time        
        self.cycle_mapping = { 'none': 'temp',
                               'temp': 'hum',
                               'hum': 'time',
                               'time': 'none' }      # cycles through the setting modes           
        self.value_ranges = {
            'temp': (20, 90), # degrees C
            'hum': (0, 100),  # percent
            'time': (1, 5959),  # 1 minute to 99:59 hours (avoid display overflow)
            'none': (0, 0)  # not used
        }
        self.target_duration = 120 # in minutes
        self.last_time_update = 0
        self.selection_stop_timer = Timer(-1) # Timer to stop selection after a while automatically
  
    def deinit(self):
        self.pid_controller.stop()
        print("PID stopped")
        self.display._clear()
        self.display.display.show()
        print("screen cleared")

    def _set_selected_target_value(self, value):
        if self.selected == 'temp':
            self.pid_controller.set_target_temp(value)
        elif self.selected == 'hum':
            self.pid_controller.set_target_hum(value)
        elif self.selected == 'time':
            self.target_duration = value
            self.display.set_time(value)

    def _get_selected_target_value(self):
        if self.selected == 'temp':
            return self.pid_controller.target_temp
        elif self.selected == 'hum':
            return self.pid_controller.target_hum
        elif self.selected == 'time':
            return self.target_duration
        return 0

    def _stop_selection(self, timer):
        self.selected = 'none'
        self.display.select('none')

    def _update_display_with_targets(self):        
        self.display.set_temp(self.pid_controller.target_temp)
        self.display.set_hum(self.pid_controller.target_hum)
        self.display.set_time(self.target_duration)

    def _update_display_with_measurements(self):
        self.display.set_temp(self.pid_controller.last_temp)
        self.display.set_hum(self.pid_controller.last_hum)
        self.display.set_time(self.target_duration)

    def _start_button_handler(self, event):
        if event == Button.PRESS:
            print("start button pressed")
            self.selected = 'none'
            self.display.select('none')
            if self.mode == 'idle':
                self.mode = 'running'
                self.last_time_update = time.ticks_ms()
                print("starting pid")
                self.pid_controller.start_heating()                    
            elif self.mode == 'running':
                self.mode = 'idle'
                self.pid_controller.stop_heating()
    
    # Cycles through the settings only
    def _rotary_button_handler(self, event):
        if event == Button.PRESS:
            self.selected = self.cycle_mapping[self.selected]
            self.display.select(self.selected)
            min_val, max_val = self.value_ranges[self.selected]
            self.rotary.set(min_val=min_val, max_val=max_val, value=self._get_selected_target_value())
            

    # simply set the selected value to the rotary value and min max
    def _rotary_handler(self):
        if self.selected == 'none':
            return # ignore if not in selection mode
        value = self.rotary.value()
        self._set_selected_target_value(value)
        self._update_display_with_targets()

    def start(self):
        self._control_loop()

    def _control_loop(self):
        while(True):
            if self.pid_controller.thread_exited:
                print("main thread exiting")
                return
            if self.mode == 'running':
                elapsed_minutes = (time.ticks_ms() - self.last_time_update) // 60000
                if elapsed_minutes >= 1:
                    self.target_duration -= elapsed_minutes
                    self.last_time_update = time.ticks_ms()
                    if self.target_duration <= 0:
                        self.target_duration = 0
                        self.mode = 'idle'
                        self.pid_controller._heatup = False

            if self.selected == 'none':
                self._update_display_with_measurements()
            else:
                self._update_display_with_targets()

            self.display._update()
            time.sleep_ms(50)
            

if __name__ == "__main__":    
    controller = None
    try:        
        controller = Controller()
        pixel_pin = 16
        pixel = neopixel.NeoPixel(machine.Pin(pixel_pin), 1)
        pixel[0] = (0, 0, 0) # turn off onboard LED
        del pixel # don't need it anymore
        controller.start()
    except Exception as e:
        import sys
        sys.print_exception(e)
        if controller is not None:
            controller.deinit()
    finally:
        if controller is not None:
            controller.deinit()
        else:
            Pin(6,Pin.OUT).value(0) # something went wrong in the controller. Make sure the heater and fan are off
            Pin(7,Pin.OUT).value(0)
        print("Program stopped")


