from myhdl import Signal, Simulation, instance

from hdmi.interfaces import VideoInterface
from hdmi.utils import clock_driver


def test_video_interface():

    # resolution is kept low to minimize run time
    res = (50, 50)

    # a sample frame
    frame = [[1, 0, 0]]*(res[0] * res[1])

    clock = Signal(0)
    clock_drive = clock_driver(clock)

    video_interface = VideoInterface(clock, res)

    @instance
    def test():

        video_interface.reset_cursor()
        video_interface.enable_video()

        # Sending a frame
        yield video_interface.write_frame(frame), \
              video_interface.read_frame()
        assert video_interface.get_frame() == frame

        # Frame can be updated here
        yield video_interface.write_frame(frame), \
              video_interface.read_frame()
        assert video_interface.get_frame() == frame

        video_interface.disable_video()

    return clock_drive, test

test_inst = test_video_interface()

sim = Simulation(test_inst)
sim.run(10000)
sim.quit()

