import pdb
import heapq
import logging

# Good luck in understanding the nuances of this implementation. The
# significance of statement ordering, lt vs. lte and the sequencing of
# function calls are not obvious.

logging.basicConfig(level=logging.ERROR)

UP = 1
DOWN = 2
FLOOR_COUNT = 6

class ElevatorLogic(object):
    """
    An incorrect implementation. Can you make it pass all the tests?

    Fix the methods below to implement the correct logic for elevators.
    The tests are integrated into `README.md`. To run the tests:
    $ python -m doctest -v README.md

    To learn when each method is called, read its docstring.
    To interact with the world, you can get the current floor from the
    `current_floor` property of the `callbacks` object, and you can move the
    elevator by setting the `motor_direction` property. See below for how this is done.
    """

    def __init__(self):
        # Feel free to add any instance variables you want.
        self.callbacks = None
        self.reqs = []
        self.lastdir = None

    def __repr__(self):
        return "%s, dir:%s, motor:%s, %s" % (repr(self.reqs), repr(self.lastdir), repr(self.callbacks.motor_direction), repr(""))

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        md = self.callbacks.motor_direction
        cf = self.callbacks.current_floor

        # Do not append if we are being called from current floor
        # where we are stopped and in current direction of travel
        if not (md == None and cf == floor and self.lastdir == direction):
            self.reqs.append((floor,direction))
        logging.debug("------>>>>>>> on_called")
        logging.debug(self)

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """

        self.reqs.append((floor, None))
        logging.debug("------>>>>>>> on_floor_selected")
        logging.debug(self)

    def prune_selects(self, dcur):
        ns = []
        if dcur == None:
            return
        for floor,d in self.reqs:
            if d != None:
                ns.append((floor,d))
            elif dcur == UP and floor > self.callbacks.current_floor:
                ns.append((floor,d))
            elif dcur == DOWN and floor < self.callbacks.current_floor:
                ns.append((floor,d))
        self.reqs = ns

    def reqs_in_dir(self, d):
        if d == UP:
            return [x for x in self.reqs if x[0] > self.callbacks.current_floor]
        elif d == DOWN:
            return [x for x in self.reqs if x[0] < self.callbacks.current_floor]

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """

        d = self.callbacks.motor_direction # Never None when on_floor_changed is called
        drev = {UP: DOWN, DOWN: UP}[d]
        floor = self.callbacks.current_floor
        dostop = None

        # We stop if direction and floor match
        if (floor,d) in self.reqs:
            dostop = (floor,d)
        # or if opposite direction matches and no more floors in same direction
        elif d == UP and (floor,DOWN) in self.reqs:
            if not any(self.reqs_in_dir(UP)):
                dostop = (floor, DOWN)
        elif d == DOWN and (floor,UP) in self.reqs:
            if not any(self.reqs_in_dir(DOWN)):
                dostop = (floor, UP)
        # or if floor is requested and hasn't been pruned
        elif (floor, None) in self.reqs:
            dostop = (floor, None)

        self.prune_selects(d)
        if dostop:
            self.callbacks.motor_direction = None
            self.remove_req(dostop)
            dnext = dostop[1]
            if dnext and dnext != self.lastdir:
                self.lastdir = dnext

    def reverse_direction(self):
        self.callbacks.motor_direction = {UP: DOWN, DOWN: UP, None: None}[self.dir]
        self.dir = self.callbacks.motor_direction

    def remove_req(self, x):
        while x in self.reqs:
            self.reqs.remove(x)
        z = (x[0], None)
        while z in self.reqs:
            self.reqs.remove(z)

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """

        # remove all selects for current floor
        self.reqs = [x for x in self.reqs if x != (self.callbacks.current_floor, None)]
        self.prune_selects(self.lastdir)

        if not self.reqs:
            self.callbacks.motor_direction = None
            self.lastdir = None
        else:
            if self.lastdir == None:
                nxtf, nxtd = self.reqs[0]
                if nxtf > self.callbacks.current_floor:
                    self.lastdir = UP
                else:
                    self.lastdir = DOWN
            if self.lastdir == UP:
                if any(self.reqs_in_dir(UP)):
                    self.callbacks.motor_direction = UP
                elif (self.callbacks.current_floor, DOWN) in self.reqs:
                    self.callbacks.motor_direction = None
                    self.lastdir = DOWN
                    self.remove_req((self.callbacks.current_floor, DOWN))
                elif any(self.reqs_in_dir(DOWN)):
                    self.callbacks.motor_direction = DOWN

            elif self.lastdir == DOWN:
                if any(self.reqs_in_dir(DOWN)):
                    self.callbacks.motor_direction = DOWN
                elif (self.callbacks.current_floor, UP) in self.reqs:
                    self.callbacks.motor_direction = None
                    self.lastdir = UP
                    self.remove_req((self.callbacks.current_floor, UP))
                elif any(self.reqs_in_dir(UP)):
                    self.callbacks.motor_direction = UP


        if self.callbacks.motor_direction:
            self.lastdir = self.callbacks.motor_direction

        logging.debug("------>>>>>>> on_ready")
        logging.debug(self)

# some examples from the doctests for debugging.
def foo():
    e = Elevator(ElevatorLogic())
    e.call(2, DOWN)
    e.call(4, UP)
    e.run_until_stopped()
    e.select_floor(5)
    e.run_until_stopped()
    return e

def bar():
    e = Elevator(ElevatorLogic())
    e.call(5, DOWN)
    e.run_until_stopped()
    e.select_floor(1)
    e.call(3, DOWN)
    e.run_until_stopped()
    e.run_until_stopped()
    return e

def baz():
    e = Elevator(ElevatorLogic())
    e.select_floor(5)
    e.call(5, UP)
    e.call(5, DOWN)
    e.run_until_stopped()
    e.select_floor(4)
    return e

def qux():
    e = Elevator(ElevatorLogic())
    e.select_floor(5)
    e.call(5, UP)
    e.call(5, DOWN)
    e.run_until_stopped()
    e.select_floor(4)
    e.run_until_stopped()
    e.select_floor(6)
    return e

def za():
    e = Elevator(ElevatorLogic())
    e.select_floor(3)
    e.select_floor(5)
    e.run_until_stopped() # 3
    e.select_floor(2)
    e.run_until_stopped() # 5
    e.run_until_stopped() # stay on 5
    e.select_floor(2)
    e.run_until_stopped() # 2
    return e