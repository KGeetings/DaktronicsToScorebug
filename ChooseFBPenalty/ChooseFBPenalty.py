from os import path
from tkinter import *
import os.path
from shutil import move
from tkinter import filedialog

# penaltyFile = r"C:\Users\PCTech\Videos\OBS Capture\OBS Graphics\LivePenalty.txt"
# penaltyFile = r"..\TestPython\ChooseFBPenalty\LivePenalty.txt"
penaltyFile = r"C:\Users\pctech\Documents\LivePenalty.txt"

root = Tk()
root.resizable(height=None, width=None)
root.title(" Choose Current FB Penalty")

# List of penalties
penalties = [
    "Injury Timeout",
    "Chop Block",
    "Clipping",
    "Defensive Holding",
    "Defensive Offside",
    "Defensive Pass Interference",
    "Delay of Game",
    "Delay of Kickoff",
    "Encroachment ",
    "Facemask",
    "Fair Catch Interference",
    "False Start",
    "Horse Collar",
    "Illegal Blindside Block",
    "Illegal Block",
    "Illegal Contact",
    "Illegal Formation",
    "Illegal Forward Handoff",
    "Illegal Forward Pass",
    "Illegal Motion",
    "Illegal Shift",
    "Illegal Substitution",
    "Illegal Use of Hands",
    "Intentional Grounding",
    "Offensive Holding",
    "Offensive Offside",
    "Offensive Pass Interference",
    "Roughing the Kicker",
    "Roughing the Passer",
    "Running Into The Kicker",
    "Taunting",
    "Too Many Men On Field",
    "Tripping",
    "Unnecessary Roughness",
    "Unsportsmanlike Conduct",
    "Use of Helmet"
]

# Sort the penalties alphabetically
penalties.sort()

# Display a radio button list for each penalty, where when a user clicks on a radio button, the penalty is set as the current penalty
def displayPenaltyList():
    global penaltyList
    global penaltyFile
    penaltyList = Listbox(root, height=0, width=60)
    # on double click, save the penalty
    penaltyList.bind("<Double-Button-1>", lambda x: savePenalty())
    penaltyList.pack()
    readPenalty()
    penaltyList.insert(END, "Current Penalty: " + currentPenalty)
    # make the current penalty yellow
    penaltyList.itemconfig(0, bg="yellow")
    penaltyList.insert(END, "Choose a new penalty")
    penaltyList.insert(END, " ")
    # Insert the sorted penalties into the list
    for penalty in penalties:
        penaltyList.insert(END, penalty)

# Set the current penalty to the penalty selected by the user
def savePenalty():
    global currentPenalty
    global penaltyFile
    currentPenalty = penaltyList.get(penaltyList.curselection())
    penaltyList.delete(0, END)
    penaltyList.insert(END, "Current Penalty: " + currentPenalty)
    # make the current penalty yellow
    penaltyList.itemconfig(0, bg="yellow")
    penaltyList.insert(END, "Choose a new penalty")
    penaltyList.insert(END, " ")
    for penalty in penalties:
        penaltyList.insert(END, penalty)

    penaltyFile2 = open(penaltyFile, "w")
    penaltyFile2.write(currentPenalty)
    penaltyFile2.close()

# Read the current penalty from the file
def readPenalty():
    global currentPenalty
    global penaltyFile
    # Check to see if the file exists
    if os.path.isfile(penaltyFile):
        penaltyFile2 = open(penaltyFile, "r")
        currentPenalty = penaltyFile2.read()
        penaltyFile2.close()
    else:
        currentPenalty = "No Penalty Selected"

def changePenaltyFile():
    global penaltyFile
    penaltyFile = filedialog.askopenfilename()

# pack the buttons
displayPenaltyList()
savePenaltyButton = Button(root, text="Save Penalty", command=savePenalty)
savePenaltyButton.pack()
changeFileButton = Button(root, text="Change Penalty File", command=changePenaltyFile)
changeFileButton.pack()

root.mainloop()

# Run to compile to .exe file with no console:
# pyinstaller -F --workpath ./ChooseFBPenalty/build --noconsole --onefile --windowed --distpath ./ChooseFBPenalty/dist --paths=site-packages ./ChooseFBPenalty/ChooseFBPenalty.py
