#!/usr/bin/python

import tkinter
import serial
import struct
import pyautogui 

#global vars
setOpen = False
myPort = 'tty.MindWaveMobile-SerialPo'
threshhold = 10
snapOn = False
startClicked = False
ser = None
values = 0
vList = []
amCali = False
key1 = 'command'
key2 = 'shift'
key3 = '3'
key4 = ''

#make sure the conditions for checking the payload is good.
def checkPayload():    
    SYNC = b'\xaa'
    global ser

    #Synchronize on [SYNC] bytes
    v = ser.read()
    if( v != SYNC ):
        return;
    v = ser.read()
    if( v != SYNC):
        return; 

    #Parse [PLENGTH] byte
    while( True ):
        pLength = ser.read()
        if( pLength != b'\xAA'):
            break;

    if( pLength > b'\xA9'):
        return;

    #Collect [PAYLOAD...] bytes
    checksum = 0
    i = 0
    payload = []
    pLength = struct.unpack('b', pLength)[0]

        
    while( i < pLength):
        payload.append(ser.read())
        checksum = checksum + struct.unpack('b', payload[i])[0]
        i = i + 1
    

    #Parse [CHECKSUM] byte
    checksum = checksum & 0xFF
    checksum = ~checksum & 0xFF
        
    #Verify [PAYLOAD...] checksum against [CHECKSUM]
    v = ser.read()
    v = struct.unpack('b', v)[0]
    if( v != checksum ):
        return

    #Since [CHECKSUM] is ok, parse the data payload
    parsePayload( pLength, payload )
    
#Parse the payload.
def parsePayload( pLength, payload ):
    EXCODE = b'\x55'
    bytesParsed = 0
    global vList
    global values
    global amCali

    print(payload)
    #Loop until all bytes are parsed from the payload array
    while( bytesParsed < pLength ):
            
        #Parse the extendedCodeLevel, code, and length
        extendedCodeLevel = 0
        while( payload[bytesParsed] == EXCODE ):
            extendedCodeLevel = extendedCodeLevel + 1
            bytesParsed = bytesParsed + 1
        
        code = struct.unpack('b', payload[bytesParsed])[0]
        bytesParsed = bytesParsed + 1

        if( code & 0x80 ):
            length = struct.unpack('B', payload[bytesParsed])[0]
            bytesParsed = bytesParsed + 1
        else:
            length = 1
        
        #Based on the exntededCodeLevel, code, length, and the [CODE]
        #Definitions Table, handle the next "length" bytes of data from
        #the payload as appropriate for your application.
        
        #we only care about the attention meter.
        if( code == 4 ):
            #for now just add this part to make sure attention is capped to 100.
            att = struct.unpack('B', payload[bytesParsed])[0]
            if( att > 100 ):
                att = 100
            
            print("Attention is " , att)
            if( att > threshhold ):
                
                if( not amCali ):
                    global key1
                    global key2
                    global key3
                    global key4
                    
                    if( key1 != '' ):
                        pyautogui.keyDown(key1)
                    if( key2 != '' ):
                        pyautogui.keyDown(key2)
                    if( key3 != ''):
                        pyautogui.keyDown(key3)
                    if( key4 != ''):
                        pyautogui.keyDown(key4)
                    pyautogui.keyUp(key1)
                    pyautogui.keyUp(key2)
                    pyautogui.keyUp(key3)
                    pyautogui.keyUp(key4)
                    #pyautogui.hotkey('command', 'shift', '3')
                else:
                    vList.append(att)
                    values = values + 1
                break;

        #Increment the bytesParsed by the length of the Data Value
        bytesParsed = bytesParsed + length

#settings window
def settingsWindow():
    global setOpen
    if( not setOpen ):
        
        setWin = tkinter.Toplevel()
        
        def resetSetOpen():
            global setOpen
            setOpen = False
            setWin.destroy()

        setWin.protocol("WM_DELETE_WINDOW", resetSetOpen)
        setWin.resizable( width = False, height = False )
        setWin.geometry("300x300+500+300")
        
        #Port setting
        L1 = tkinter.Label(setWin, text = "Port Path")
        L1.place( x = 20, y = 20 )
        E1 = tkinter.Entry(setWin, width = 23 )
        E1.place( x = 90, y = 15 )
        E1.insert(0 , myPort)
       
        def newPort():
            global myPort
            myPort = E1.get()

        print( E1.get() )
        setPort = tkinter.Button( setWin, text="Set Port", command = newPort )
        setPort.place(x = 120, y = 45 )

        #macro setting
        
        MacroText = tkinter.Label( setWin, text = "Set Macro")
        MacroText.place( x = 120, y = 100 )
        
        M1 = tkinter.Entry( setWin, width = 7)
        M1.place( x = 10, y = 130 )
        M1.insert(0, key1)
        
        M2 = tkinter.Entry( setWin, width = 7)
        M2.place( x = 80, y = 130 )
        M2.insert(0, key2)

        M3 = tkinter.Entry( setWin, width = 7)
        M3.place( x = 150, y = 130 )
        M3.insert(0, key3)

        M4 = tkinter.Entry( setWin, width = 7)
        M4.place( x = 220, y = 130 )
        M4.insert(0, key4)
        print(key1)
        print(key2)
        print(key3)
        print(key4)
        #set the macro
        def newMac():
            global key1
            global key2
            global key3
            global key4

            key1 = M1.get()
            key2 = M2.get()
            key3 = M3.get()
            key4 = M4.get()



        MButton = tkinter.Button( setWin, text="Set Macro", command=newMac )
        MButton.place( x = 110, y = 160 )

        #calibrate stuff below
        calString = tkinter.StringVar()
        calLabel = tkinter.Label(setWin, textvariable = calString)
        calLabel.place(x = 50, y = 280)
        calString.set("No calibrations have been done yet.")
        
        #Calibrate for attention
        def beginCal():
            global values
            global vList
            global amCali
            global ser

            if( values < 12 ):
                amCali = True
                ser = serial.Serial('/dev/' + myPort, 57600)
                checkPayload()
                fakeVal = values - 2 + 1
                if( fakeVal <= 0 ):
                    calString.set("Calibrating...")
                else:
                    calString.set("Obtained " + str(fakeVal) + "/10 values.")
                
                setWin.after(10, beginCal)
            
            else:
                global threshhold
                avsum = 0
                for result in vList:
                   print(result)
                   avsum = avsum + result

                avsum = int(avsum / 10)
                threshhold = avsum
                print(threshhold)
                calString.set("Done! Calibrated value is " + str(avsum))
                ser.close()
                
                values = 0
                avsum = 0
                vList = []
                amCali = False  

        calibrate = tkinter.Button( setWin, text="Calibrate", command = beginCal )
        calibrate.place(x = 120, y = 250 )
        setOpen = True

#this will be the main GUI.
def setGUI():
    window = tkinter.Tk()
    window.title( "Snap" )
    window.geometry( "400x200+300+100" )
    window.resizable( width=False, height=False )
    
    var = tkinter.StringVar()
    label = tkinter.Label( window, textvariable=var )
    var.set("Welcome to Snap.\nPlease configure your settings first, then begin.")
    label.pack(pady = 20)
    
    def startParse():
        global snapOn
        global startClicked
        
        if( not snapOn ):
            startClicked = True
            
            global ser
            ser = serial.Serial('/dev/' + myPort, 57600)
            
            checkPayload()
            window.after(10, startParse)
        else:
            print("Stopping Snap...")
            snapOn = False
            startClicked = False

    def stopParse():
        global snapOn
        global startClicked
        global ser
        if( startClicked ):
            snapOn = True
            ser.close()
    
    snapButton = tkinter.Button( window, text="Begin Snap", command = startParse )
    snapButton.place(x = 80 , y = 70 )

    stopButton = tkinter.Button( window, text="Stop Snap", command = stopParse )
    stopButton.place( x = 220, y = 70 )
    

    settingsButton = tkinter.Button( window, text="Settings", command = settingsWindow )
    settingsButton.place( x = 160, y = 110)
    
    window.mainloop()

setGUI()
