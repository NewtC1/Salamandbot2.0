import time
import threading

class Clock(threading.Thread):
    """
    This is a simple clock that executes functions that it's been given based on frequency. By default this is every
    minute.
    """

    def __init__(self, logger, tick_frequency=60, function_dict=None):
        super(Clock, self).__init__()
        self.logger = logger
        self.tick_frequency = tick_frequency
        self.function_dict = function_dict
        self.last_tick = time.time()
        self.next_tick = self.last_tick + self.tick_frequency
        self.running = False
        pass

    def run(self):
        while True:
            self.tick()
            time.sleep(self.tick_frequency)

    def tick(self):
        for function in self.function_dict.keys():
            # if the function has arguments to input, pull them from the dict. If not, run the function with nothing.
            if self.function_dict[function]:
                function(self.function_dict[function])
            else:
                function()

        self.last_tick = time.time()
        self.next_tick = self.last_tick + self.tick_frequency

    def add_function(self, function_to_add, arguments):
        self.function_dict[function_to_add] = arguments

    def remove_function(self, function_to_remove):
        del self.function_dict[function_to_remove]
