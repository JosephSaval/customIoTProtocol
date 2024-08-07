# Authors: Joseph W Saval & Ryan Easter
# CE 484 - Internet of Things
# Final Project
# Gateway micro:bit
#
# This file acts as a gateway for access layer data received from nodes
# over radio and sends valid data received to the MQTT gateway over a COM
# port.

#Micro:Bit Imports
from microbit import *
import radio
import time

# Custom funtions for the access protocol & micro:bits
from accessCom import sendMessage
from accessCom import stringToArr
from accessCom import arrToString
from accessCom import logBinaryArr
from accessCom import logSend
from accessCom import logValRec

# Globals
GATE_NAME = "SAVAEAST0"
GATE_ID = 0 # Specifies the ID for this device
nodeId = 1 # Specifies the ID for new nodes that connect
needHandshakeAck = False # Used to detect 3-way handshake ACKs
sendSynAck = False # Send a SynACK if true
synTS = 0 # Timestamp of last SYN message

#Initialize Radio
radio.on()
radio.config(group=10)

# Vars needed between loop iterations
initTimeout = 0
lTimeout = 0
sendL = False
lastLSend = 0
displayLetter = ''
lDestId = -1 # Node Id for forwarding a L message

#Main Loop - Continuously Listens for nodes
while True:
    
    accessBuffer = radio.receive_bytes()

    # --------------------------------
    # Access Layer Message Detection & validation
    # --------------------------------
    
    if accessBuffer:

        # --------------------------------
        # New Node Handshake
      
        # Detect New CON Request
        # Ignores connection requests while a 3-way handshake is in progress
        # Ignores connection requests if 3 nodes are already connected
        if accessBuffer == stringToArr("EASTSAVAGATE") and not sendSynAck and nodeId < 4:
            synMessage = arrToString(accessBuffer)
            
            #logValRec(synMessage) # Log message
    
            # Set state variable to run the state to send synacks
            sendSynAck = True  
            needHandshakeAck = True

        # Detect a 3-way handshake ACK
        elif accessBuffer[0:8] == stringToArr("EASTSAVA") and accessBuffer[8:9] == stringToArr(str(nodeId)) and needHandshakeAck == True:

            synAck = "EASTSAVA" + arrToString(accessBuffer[8:9]) # Converty SynAck to string for easy manipulation 
            #logValRec(synAck) # Log Message
            sendSynAck = False # Disable the Send SYNACK state
            needHandshakeAck = False # Stop detecting ACKs
            timeout = 0 # Reset timeout

            uart.write('N' + ":" + str(nodeId) + '\r\n') # Alert higher levels that a node is connected
            nodeId += 1 # Increment the node ID

        # --------------------------------
        # Detecting Valid Messages From Nodes
            
        #Detect a valid non-handshake prefix 
        elif accessBuffer[0:8] == stringToArr("SAVAEAST"):

            #Determine that messages are from a known node and intended for the Gateway
            incomingId = int(arrToString(accessBuffer[8:9])) # Node ID
            targetId = int(arrToString(accessBuffer[9:10])) # Gateway ID
            if incomingId < nodeId and targetId == GATE_ID:
                
                # --------------------------------
                # Transfer Accelerometer Values from node to Matlab gate
                
                #Detect 'C' (Accelerometer) type messages
                if arrToString(accessBuffer[10:11]) == "C":
                    tiltX = int.from_bytes(accessBuffer[11:13],'big') - 1500
                    tiltY = int.from_bytes(accessBuffer[13:15],'big') - 1500
                    tiltZ = int.from_bytes(accessBuffer[15:17],'big') - 1500

                    #Log Message
                    #cHeader = arrToString(accessBuffer[0:8])
                    #logValRec(cHeader + " " + str(incomingId) + " " + str(targetId) + " C " + str(tiltX) + " " + str(tiltY) + " " + str(tiltZ))

        
                    #CODE TO TRANSFER ACCEL DATA HERE
                    uart.write('C' + ":" + str(incomingId) + ":" + str(tiltX) + ":" + str(tiltY) + ":" + str(tiltZ) + "\r\n")

                #Detect 'A' (Ack) responses & configure vars to stop sending L messages
                if arrToString(accessBuffer[10:11]) == "A":
                    lTimeout = 0
                    sendL = False
                    aMessage = "A" + ":" + str(lDestId) + ":" + displayLetter
                    uart.write(aMessage + '\r\n')
                
            #else:
                #logBinaryArr(accessBuffer)
        
        #Log invalid message received
        #else:
            #logBinaryArr(accessBuffer)

    # --------------------------------
    # Message Sending - Access Layer
    # --------------------------------
      
    # After a SYN is received send SYNACKs every 2 seconds until an ACK is read or until timed out
    if sendSynAck and time.ticks_diff(time.ticks_ms(), synTS) > 2000 and initTimeout < 5:
        #Format & send SYNACK
        synAckStr = "EASTSAVA" + str(nodeId)
        synAck = stringToArr(synAckStr)
        sendMessage(synAck)
        #logSend(synAckStr)

        #Reset timer & increment timeout
        synTS = time.ticks_ms()
        initTimeout += 1

    #After a L message is received from UART forward the message along the access layer until ACK is received or unless timed out
    if sendL and time.ticks_diff(time.ticks_ms(),lastLSend) > 2000 and lTimeout < 5:
        #Format & send L message
        lMessageStr = "SAVAEAST0" + str(lDestId) + 'L' + displayLetter
        lMessage = stringToArr(lMessageStr)
        sendMessage(lMessage)
        #logSend(lMessageStr)

        #Reset timer & increment timout
        lastLSend = time.ticks_ms()
        lTimeout += 1
        
        
    # --------------------------------
    # COM Message Detection & validation
    # Data is read through the serial UART port
    # --------------------------------
    
    uartBuf = bytearray(20) #UART port buffer
    if uart.any(): # Check if message arrived
        uartSize = uart.readinto(uartBuf) # Read bytes into the buffer and return the number of bytes
        uartMsg = str(uartBuf[0:uartSize],'utf-8')

        #Detect L type message (letter display request)
        if uartMsg[0] == "L":
            lDestId = uartMsg[1]
            displayLetter = uartMsg[2]
            #logValRec(uartMsg[0] + " " + uartMsg[1] + " " + uartMsg[2])

            #Send L message every 2 seconds until ack is received
            sendL = True
            lTimeout = 0
        
    sleep(10)