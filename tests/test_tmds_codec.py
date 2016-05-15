from myhdl import instance, Simulation

from hdmi.models import EncoderModel, DecoderModel


def test_tmds_codec():

    encoder_model = EncoderModel()
    decoder_model = DecoderModel()

    @instance
    def test():

        yield encoder_model.write(), decoder_model.read()

    return test

sim = Simulation(test_tmds_codec())
sim.run()