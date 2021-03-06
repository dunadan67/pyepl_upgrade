import os
import tempfile
import warnings

import numpy as np
from numpy.testing import *
from scipy.io import wavfile


def datafile(fn):
    return os.path.join(os.path.dirname(__file__), 'data', fn)

def test_read_1():
    rate, data = wavfile.read(datafile('test-44100-le-1ch-4bytes.wav'))
    assert rate == 44100
    assert np.issubdtype(data.dtype, np.int32)
    assert data.shape == (4410,)

def test_read_2():
    rate, data = wavfile.read(datafile('test-8000-le-2ch-1byteu.wav'))
    assert rate == 8000
    assert np.issubdtype(data.dtype, np.uint8)
    assert data.shape == (800, 2)

def test_read_fail():
    assert_raises(ValueError, wavfile.read, datafile('example_1.nc'))

def _check_roundtrip(rate, dtype, channels):
    fd, tmpfile = tempfile.mkstemp(suffix='.wav')
    try:
        os.close(fd)

        data = np.random.rand(100, channels)
        if channels == 1:
            data = data[:,0]
        data = (data*128).astype(dtype)

        wavfile.write(tmpfile, rate, data)
        rate2, data2 = wavfile.read(tmpfile)

        assert rate == rate2
        assert data2.dtype.byteorder in ('<', '=', '|'), data2.dtype
        assert_array_equal(data, data2)
    finally:
        os.unlink(tmpfile)

def test_write_roundtrip():
    for signed in ('i', 'u'):
        for size in (1, 2, 4, 8):
            if size == 1 and signed == 'i':
                # signed 8-bit integer PCM is not allowed
                continue
            for endianness in ('>', '<'):
                if size == 1 and endianness == '<':
                    continue
                for rate in (8000, 32000):
                    for channels in (1, 2, 5):
                        dt = np.dtype('%s%s%d' % (endianness, signed, size))
                        yield _check_roundtrip, rate, dt, channels


# Filter test noise in 0.8.x branch. Format of data file does not seem to be
# recognized.
warnings.filterwarnings("ignore", category=wavfile.WavFileWarning)
