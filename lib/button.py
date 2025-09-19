import machine
import utime as time
import micropython
from machine import Pin


class Button:
    PRESS = 1
    RELEASE = 2

    def __init__(self, pin, debounce_ms=20, handler=None):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.debounce_ms = debounce_ms
        self.last_time = time.ticks_ms()
        self.last_state = self.pin.value()
        self.handlers = []

        self.pin.irq(handler=self._irq_handler,
                     trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        if handler:
            self.add_handler(handler)

    def _irq_handler(self, pin):
        print("pin down registered")
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_time) < self.debounce_ms:
            return  # ignore bounce

        self.last_time = now
        state = self.pin.value()
        if state != self.last_state:
            self.last_state = state
            if state == 0:  # pulled low → pressed
                micropython.schedule(self._call_handlers, Button.PRESS)
            else:
                micropython.schedule(self._call_handlers, Button.RELEASE)

    def add_handler(self, handler):
        self.handlers.append(handler)

    def _call_handlers(self, event):
        for h in self.handlers:
            h(event)
