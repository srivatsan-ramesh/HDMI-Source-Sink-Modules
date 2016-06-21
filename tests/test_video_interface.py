from myhdl import Signal, Simulation, instance, instances

from hdmi.interfaces import VideoInterface
from hdmi.utils import clock_driver


def test_video_interface():

    # resolution of the video is kept low to reduce simulation time
    res = (50, 50)

    # a sample pixel
    pixel = [1, 0, 0]

    clock = Signal(bool(0))
    clock_drive = clock_driver(clock)

    video_interface = VideoInterface(clock, res)

    @instance
    def test():

        video_interface.reset_cursor()
        yield video_interface.enable_video()

        # iterating over the frame
        for _ in range(res[0]*res[1]):
            # Sending a pixel
            yield video_interface.write_pixel(pixel), \
                video_interface.read_pixel()
            assert video_interface.get_pixel() == pixel

        yield video_interface.disable_video()

    return instances()

test_inst = test_video_interface()

sim = Simulation(test_inst)
sim.run(10000)
sim.quit()

