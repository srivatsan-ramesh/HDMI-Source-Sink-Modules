import py
import pytest

from myhdl.conversion import analyze, verify
from myhdl.conversion._verify import _simulators

xfail = pytest.mark.xfail

all_sims = list(_simulators)


def pytest_addoption(parser):
    parser.addoption("--sim", action="store", choices=all_sims,
                     help="HDL Simulator")


def pytest_configure(config):
    sim = config.getoption('sim')
    if sim is not None:
        verify.simulator = analyze.simulator = sim


def pytest_report_header(config):
    sim = config.getoption('sim')
    if config.getoption('sim') is not None:
        hdr = ['Simulator: {sim}']
        if not py.path.local.sysfind(sim):
            hdr += ['Warning: {sim} not found in PATH']
        return '\n'.join(hdr).format(sim=sim)
