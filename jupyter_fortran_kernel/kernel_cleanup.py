import os


def cleanup_files(files):
    """ Remove all temporary files created by the kernel

    Args:
        files (:obj:`list` of :obj:`str`): temporary file names
    """
    for file in files:
        try:
            os.remove(file)
        except:
            pass
