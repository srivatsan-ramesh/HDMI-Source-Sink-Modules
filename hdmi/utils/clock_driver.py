from myhdl import delay, always


def clock_driver(clock, d=1):

    half_period = delay(d)

    @always(half_period)
    def drive_clock():
        clock.next = not clock

    return drive_clock
