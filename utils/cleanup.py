import os
from os.path import exists
import shutil


def _listdir(d):  # listdir with full path
    return [os.path.join(d, f) for f in os.listdir(d)]


def cleanup(reddit_id=None) -> int:
    """Deletes all temporary assets in assets/temp

    Returns:
        int: How many files were deleted
    """
    if reddit_id is None:
        directory = "../assets/temp/"
        if exists(directory):
            shutil.rmtree(directory)

            return 1

    directory = f"../assets/temp/{reddit_id}/"
    if exists(directory):
        shutil.rmtree(directory)

        return 1
