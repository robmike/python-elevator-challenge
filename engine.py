class Elevator(object):
    def call(self, floor, direction):
        self._logic_delegate.on_called(floor, direction)

    def select_floor(self, floor):
        self._logic_delegate.on_floor_selected(floor)

class Elevator(Elevator):
    def __init__(self, logic_delegate, starting_floor=1):
        self._current_floor = starting_floor
        print "%s..." % starting_floor,
        self._motor_direction = None
        self._logic_delegate = logic_delegate
        self._logic_delegate.callbacks = self.Callbacks(self)

    class Callbacks(object):
        def __init__(self, outer):
            self._outer = outer

        @property
        def current_floor(self):
            return self._outer._current_floor

        @property
        def motor_direction(self):
            return self._outer._motor_direction

        @motor_direction.setter
        def motor_direction(self, direction):
            self._outer._motor_direction = direction

class Elevator(Elevator):
    def step(self):
       delta = 0
       if self._motor_direction == UP: delta = 1
       elif self._motor_direction == DOWN: delta = -1

       if delta:
           self._current_floor = self._current_floor + delta
           print "%s..." % self._current_floor,
           self._logic_delegate.on_floor_changed()
       else:
           self._logic_delegate.on_ready()

       assert self._current_floor >= 1
       assert self._current_floor <= FLOOR_COUNT
    
    def run_until_stopped(self):
        self.step()
        while self._motor_direction is not None: self.step()
    
    def run_until_floor(self, floor):
        for i in range(100):
            self.step()
            if self._current_floor == floor: break
        else: assert False
