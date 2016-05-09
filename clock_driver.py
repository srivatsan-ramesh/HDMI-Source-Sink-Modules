from myhdl import delay, always


def clock_driver(clock):

    half_period = delay(1)

    @always(half_period)
    def drive_clock():
        clock.next = not clock

    return drive_clock
