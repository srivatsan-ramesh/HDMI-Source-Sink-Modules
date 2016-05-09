from myhdl import Signal, Simulation, instance
from clock_driver import clock_driver
from video_interface import VideoInterface


def test_video_interface():

    # resolution is kept low to minimize run time
    res = (50, 50)

    # a sample frame
    frame = [[1, 0, 0]]*(res[0] * res[1])

    clock = Signal(0)
    clock_drive = clock_driver(clock)

    video_interface = VideoInterface(clock, res)
    video_interface.reset_cursor()

    @instance
    def test():

        yield video_interface.write_frame(frame)
        # Frame can be updated here
        yield video_interface.write_frame(frame)

    return clock_drive, test

test_inst = test_video_interface()

sim = Simulation(test_inst)
sim.run(10000)
