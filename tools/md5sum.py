import io
import hashlib


def md5sum(path):
    """
    Return the md5 hash of a provided file, reading in chunks to reduce memory usage for
    large files.
    From https://stackoverflow.com/a/40961519
    """
    length = io.DEFAULT_BUFFER_SIZE
    md5 = hashlib.md5()
    with io.open(path, mode="rb") as fd:
        for chunk in iter(lambda: fd.read(length), b''):
            md5.update(chunk)
    return md5.hexdigest()