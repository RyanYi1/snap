# Snap
Read data from Neurosky Mindwave Mobile headset to obtain user's attention level. When the attention level meets a threshold, the program executes a keyboard shortcut. The threshold value can be calibrated by the user, and set to a default of 10. The keyboard shortcut executed by this program can also be set. The shortcut is set to Command + Shift + 3 (screenshot on Mac). 

The program uses Pyautogui and Tkinter for keyboard clicking simulation and GUI respectfully. Serial Ports were used to read the data from the headest. 

The packets of data obtained from the headset was parsed from the directions given by the [ThinkGreat Serial Stream Guide](http://developer.neurosky.com/docs/doku.php?id=thinkgear_communications_protocol)

Current Features
1. Calibrate threshold level for attention
2. Set macro for program to execute
3. Execute set short if attention meets threshold

Features to Add
1. Add blink strength to execute alongside attention
2. Incorporate method to allow program to execute up to 4 macros (eye detection considered)
