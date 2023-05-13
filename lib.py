import os
import time


def simple_hash(s, range_size):
    # Compute the sum of ASCII values of the characters in the string
    ascii_sum = sum(ord(c) for c in s)
    # Take the modulo of the sum with the size of the range
    return ascii_sum % range_size


def logger(filename, message):
    if os.path.exists(filename):
        logFile = open(filename, "a")
    else:
        with open(filename, "w") as logFile:
            logFile.write("Server Log")
    logFile.write(message)
    logFile.close()


def berkeley(storageNodeClocks):
    masterClock = time.time()
    totalTime = sum(storageNodeClocks) + masterClock
    totalClocks = len(storageNodeClocks) + 1.0
    averageTime = totalTime / totalClocks
    return averageTime


def compute_formatted_time(offset):
    currentTime = offset + time.time()
    timeStruct = time.localtime(currentTime)
    milliseconds = str(currentTime).split('.')[1][:3]
    formattedTime = time.strftime("%Y-%m-%d %H:%M:%S", timeStruct)
    preciseTime = f"{formattedTime}.{milliseconds}"
    return preciseTime
