# Authors: Joseph W Saval & Ryan Easter
# CE 484 - Internet of Things
# Final Project
# Node micro:bit
#
# This file acts as a node that communicates with a gateway using a custom
# protocol.

from microbit import *
import radio
import time

# Custom funtions for the access protocol & micro:bits
from accessCom import sendMessage
from accessCom import stringToArr
from accessCom import arrToString
from accessCom import logSend
from accessCom import logValRec

# Globals
nodeName = ""
nodeId = -1
prefixArr = stringToArr("SAVAEAST") #Store the prefix as a byte array

# --------------------------------
# Initialization/Setup
# --------------------------------

#Initialize Radio
radio.on()
radio.config(group=10)

#Convert 'Gate' to byte array & concat to the prefix

initMessage = stringToArr("EASTSAVAGATE")

# --------------------------------
#Send Initial SYN request & resend until valid reply is read

sendSyn = True
while sendSyn == True:
    sendMessage(initMessage) # First send a message
    logSend(arrToString(initMessage)) # Log Message
    lastSyn = time.ticks_ms() #Set timestamp for last SYN send
    
    #Then detect the SYNACK reply
    wait = True
    while wait == True:
        synAck = radio.receive_bytes()

        #If there is no valid reply in 2 seconds resend SYN
        if time.ticks_diff(time.ticks_ms(), lastSyn) > 2000:
            wait = False
        
        #If a reply is received...
        elif synAck:

            #Detect a valid SYNACK message
            if synAck[0:8] == stringToArr("EASTSAVA"):
                synAckString = arrToString(synAck)

                #End out of both loops
                sendSyn = False
                wait = False

                logValRec(synAckString) # Log Received Message
                
                #Configure Device ID
                nodeName = "SAVAEAST" + synAckString[8]
                nodeId = synAckString[8]

# --------------------------------
#Send ACK and wait 2 seconds for a new SYNACK in case ACK wasn't received by the server

ack = "EASTSAVA" + str(nodeId)
sendMessage(stringToArr(ack)) # Send Ack
logSend(ack)
sendAck = True
lastAck = time.ticks_ms()
while sendAck == True:
    
    synAck = radio.receive_bytes() # Buffer
    #Wait for 2.5 seconds before ending loop   
    if time.ticks_diff(time.ticks_ms(),lastAck) > 2500:
            sendAck = False

    #Detect message if under 2 seconds
    elif synAck:
        
        #Detect retransmitted synack & resend ACK
        if synAck[0:9] == stringToArr("EASTSAVA" + str(nodeId)):
            synAckString = arrToString(synAck)
            logValRec(synAckString)
            sendMessage(stringToArr(ack)) # Send Ack
            logSend(ack)
            lastAck = time.ticks_ms()
                
    sleep(10)

# --------------------------------
# Main Loop 
# -Detects display requests (L type messages) & transmits accelerometer values (C type messages) periodically
# --------------------------------

lastCSend = time.ticks_ms()
lastASend = time.ticks_ms()
displayLetter = ''
sendAck = False
while True:
    buffer = radio.receive_bytes()

    # --------------------------------
    # C Type Message Formatting & Sending
    
    #Send Accelerometer readings every 3 seconds
    if time.ticks_diff(time.ticks_ms(),lastCSend) > 3000:
        
        #Read Acceleromoeter values
        tiltX = accelerometer.get_x() + 1500
        tiltY = accelerometer.get_y() + 1500
        tiltZ = accelerometer.get_z() + 1500
        tiltArr = [tiltX,tiltY,tiltZ]

        #Split accel values into 2 bytes if value is to large for 1 byte
        byteArr = bytearray([])
        for i in tiltArr:
            byteArr += (i).to_bytes(2,'big')

        #Format & send C type message without waiting for any reply
        cHeader = stringToArr(nodeName + "0C")
        cMessage = cHeader + byteArr
        sendMessage(cMessage)
        logSend(nodeName[0:8] + " " + nodeName[8:9] + " 0 C " + " " + str(tiltX) + " " + str(tiltY) + " " + str(tiltZ))

        # Reset send time
        lastCSend = time.ticks_ms()

    #Detect message
    if buffer:
        #Detect L message
        if buffer[0:9] == stringToArr("SAVAEAST0") and buffer[9:10] == stringToArr(str(nodeId)) and buffer[10:11] == stringToArr("L"):
            print("entered") #For testing
            logValRec(arrToString(buffer))

            #Display the letter requested
            displayLetter = arrToString(buffer[11:12])
            display.show(displayLetter)
            
            #Send response
            ackString = "SAVAEAST" + str(nodeId) + "0A" + displayLetter #Configure Message String
            ack = stringToArr(ackString) # Convert to binary array
            sendMessage(ack) # Send
            logSend("SAVAEAST" + " " + str(nodeId) + " 0 A " + displayLetter) # aaand log