# Authors: Joseph W Saval & Ryan Easter
# CE 484 - Internet of Things
# Final Project
# Protocol Functions for Access Layer Communication
#
# This file provides custom protocol functions for the access layer of
# the IoT Final Project.

from microbit import *
import radio
import time

# -------------------------
# Message Log Functions
# -------------------------

# Casts a binary array to a string then prints the result
# This function is intended to log invalid messages received by a micro:bit
def logBinaryArr(array):
    print("RECV: " + str(array))

def logValRec(message):
    print("RECV: " + message)

def logSend(message):
    print("XMIT: " + message)

#Logs properly formatted string

# -------------------------
# Message Send Functions
# -------------------------

# Sends a message over radio and returns the timestamp of when the message was sent
def sendMessage(message):
    radio.send_bytes(message)
    return time.ticks_ms()

# -------------------------
# Binary Array Conversion Functions
# -------------------------
    
# Converts a string to a byte array
def stringToArr(string):
    arr = bytearray([])
    for i in string:
        arr += bytearray([ord(i)])
    return arr

# Converts a byte array to string
def arrToString(byteArr):
    return str(byteArr,'utf-8')
    
#NOT WORKING ###############################   
# Converts an int to a byte array
def intToArr(integer):
    return bytearray([integer])

#NOT WORKING ###############################
#Converts a byte array to an int
def arrToInt(array):
    return int.from_bytes(array[0:-1],"big")
