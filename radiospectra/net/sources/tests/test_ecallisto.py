import pytest
import zlib
from unittest.mock import patch, MagicMock
from astropy.io import fits
from radiospectra.net.sources.ecallisto import eCALLISTOClient

# 1. MOCK TEST: 
@patch('urllib.request.urlopen')
def test_fetch_remote_header_mock(mock_urlopen):
    mock_response = MagicMock()
    mock_response.getcode.return_value = 206
    
    # Create a VALID fake FITS header using astropy
    hdr = fits.Header()
    hdr['SIMPLE'] = True
    hdr['DATE-OBS'] = '2026-03-30'
    hdr['TIME-OBS'] = '10:00:00'
    hdr['DATE-END'] = '2026-03-30'
    hdr['TIME-END'] = '10:15:00'
    
    header_bytes = hdr.tostring().encode('ascii')
    
    gzip_compressor = zlib.compressobj(wbits=16+zlib.MAX_WBITS)
    fake_gz_data = gzip_compressor.compress(header_bytes) + gzip_compressor.flush()
    
    mock_response.read.return_value = fake_gz_data
    mock_urlopen.return_value.__enter__.return_value = mock_response

    client = eCALLISTOClient()
    start, end = client._fetch_remote_header("http://fake-url.fit.gz")

    assert start == "2026-03-30 10:00:00"
    assert end == "2026-03-30 10:15:00"
    
    args, kwargs = mock_urlopen.call_args
    assert args[0].headers['Range'] == 'bytes=0-15360'

# 2. REAL SERVER TEST: 
@pytest.mark.remote_data
def test_fetch_remote_header_real_server():
    client = eCALLISTOClient()
    # Using a known stable URL from the archive
    url = "http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/2019/10/05/ALASKA_20191005_230000_59.fit.gz"
    
    start, end = client._fetch_remote_header(url)
    
    
    assert start == "2019/10/05 23:00:00.757"
    assert end is not None