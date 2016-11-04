import struct
import sys

# we require 2.7.9, as it comes with pip built-in
_PYTHON_MIN_VERSION = (2, 7, 9)


def _get_recommended_version_message():
    return "python 2, version {0} or better".format(
        ".".join(map(str,_PYTHON_MIN_VERSION)))

def python_version_is_suitable():
    print("...looking for {0}".format(_get_recommended_version_message()))

    detected_version = sys.version_info
    bitness = struct.calcsize("P") * 8

    print("Detected python version {0}.{1}.{2} ({3}-bit)".format(
        detected_version.major,
        detected_version.minor,
        detected_version.micro,
        bitness
    ))

    if detected_version.major == 3 or detected_version < _PYTHON_MIN_VERSION:
        print(
        "Error. Bad python version. To fix this issue, please install {0}".format(_get_recommended_version_message()))
        return False

    print("Success. Your python version meets the minimum requirements")
    return True


if __name__ == "__main__":
    exit_code = 0 if python_version_is_suitable() else 1
    exit(exit_code)
