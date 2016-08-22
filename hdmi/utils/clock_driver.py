from myhdl import delay, instance, block


@block
def clock_driver(clock, d=1):

    @instance
    def drive_clock():
        while True:
            yield delay(d)
            clock.next = not clock

    return drive_clock
