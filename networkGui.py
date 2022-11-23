from tkinter import *
import subprocess
import re
import platform  
 
 
class Window:
    def __init__(self, master):
        self.master = master
        self.arp()
        
 
        self.Main = Frame(self.master)
        self.master.title("Network Device Status")
 
        self.upper = Frame(self.Main)
 
        self.row = 5
        self.col = 2

        #create cells to hold gui objects for the grid
        self.cells = [[None for i in range(self.col+2)] for j in range(self.row+1)]

        #Set up the labels for the description of the various entries
        self.cells[0][0] =  Label(self.upper,text="Network IP Address")
        self.cells[0][0].grid(row=0,column=0)
        self.cells[0][1] =  Label(self.upper,text="Device MAC Address")
        self.cells[0][1].grid(row=0,column=1)
        self.cells[0][2] =  Label(self.upper,text="(xx-xx-xx-xx-xx-xx)")
        self.cells[0][2].grid(row=0,column=2)
        
        #Go through and populate the remaining grid with entries and status labels
        for i in range(self.row):
            for j in range(self.col):
                self.cells[i+1][j] = Entry(self.upper, width = 20)
                self.cells[i+1][j].grid(row = i+1, column = j)
            self.cells[i+1][self.col] = Label(self.upper,text="Status:")
            self.cells[i+1][self.col].grid(row = i+1, column = self.col,padx=(10, 50))
        
        #Set up a button for each row with a corresponding function for each
        self.cells[1][self.col+1] = Button(self.upper, text="Ping", command=self.pingIpOne)
        self.cells[1][self.col+1].grid(row = 1, column = self.col+1)
        self.cells[2][self.col+1] = Button(self.upper, text="Ping", command=self.pingIpTwo)
        self.cells[2][self.col+1].grid(row = 2, column = self.col+1)
        self.cells[3][self.col+1] = Button(self.upper, text="Ping", command=self.pingIpThree)
        self.cells[3][self.col+1].grid(row = 3, column = self.col+1)
        self.cells[4][self.col+1] = Button(self.upper, text="Ping", command=self.pingIpFour)
        self.cells[4][self.col+1].grid(row = 4, column = self.col+1)
        self.cells[5][self.col+1] = Button(self.upper, text="Ping", command=self.pingIpFive)
        self.cells[5][self.col+1].grid(row = 5, column = self.col+1)
         
        self.upper.pack(padx = 5, pady = 5)
 

        
        #Set up a lower Frame for overall control buttons
        self.lower = Frame(self.Main)
 
        self.saveButton = Button(self.lower, text = "Save", command = self.save)
        self.saveButton.pack(padx = 5, pady = 5, side = RIGHT)
 
        self.loadButton = Button(self.lower, text = "Load", command = self.load)
        self.loadButton.pack(padx = 5, pady = 5, side = RIGHT)
 
        self.clearButton = Button(self.lower, text = "Clear", command = self.clear)
        self.clearButton.pack(padx = 5, pady = 5, side = RIGHT)
        
        self.clearButton = Button(self.lower, text = "Refresh Device Log", command = self.arp)
        self.clearButton.pack(padx = 5, pady = 5, side = LEFT)
                 
        self.lower.pack(padx = 5, pady = 5, expand = True, fill = X)

         
        self.Main.pack(padx = 5, pady = 5, expand = True, fill = X)
 
 
    def save(self):
        file = open("data.txt", "w")
 
        for i in range(1,self.row):
            for j in range(self.col):
                file.write(self.cells[i][j].get() + ",")
            file.write("\n")
 
        file.close()
 
    def load(self):
        file = open("data.txt", "r")
 
        self.clear()
 
        for i in range(1,self.row):
            temp = file.readline()
            temp = temp.split(",")
            for j in range(self.col):
                self.cells[i][j].insert(0, temp[j].strip())

    #used to stop the function of the main timer loop and clear all entries
    def clear(self):
        #go through all rows, clear entry boxes and set status to default
        for i in range(1,6):
            self.cells[i][0].delete(0, 'end')
            self.cells[i][1].delete(0, 'end')
            self.cells[i][2].config(text = "Status:")
    
    def nmap(self,ip):
        #Try to do an nmap scan that renders ARP Requests to populate device arp table
        #If the user does not have nmap except and print program might not be accurate
        try:
            print("Trying to run Nmap scan, this could take a couple of minutes.")
            proc = subprocess.Popen(
                ['nmap','-Pn','-sn',ip],
                stdout=subprocess.PIPE
            )
            stdout, stderr = proc.communicate()
            self.arp()
        except:
            print("Nmap scan failed, program might not show all network devices.")
            
    def arp(self):
        #Look at the ARP table to establish a list of MAC Adresses and thier coresponding IP
        proc = subprocess.Popen(
            ['arp','-a'],
            stdout=subprocess.PIPE
        )

        #Set up input, output and execute ARP
        stdout, stderr = proc.communicate()
        output = stdout.decode('ASCII').split()


        #Go through the output and create a dictionary of IP and MAC addresses for the user to pick from 
        index = 0
        self.macAddressDict = {}
        self.ipAddressDict = {}
        for item in output:
            #If the item is set up like a cmd responce MAC address, 6 alphanumeric pairs with - inbetween, take it and previous entry as IP/MAC combination and put it in dict
            if re.search("..-..-..-..-..-..", item):
                ipAddress = output[index-1]
                macAddress = item
                self.macAddressDict[macAddress] = ipAddress
                self.ipAddressDict[ipAddress] = macAddress
                #print(item," is at index: ",index," and has ip: ",output[index-1], " at index: ",index-1) #Debug Print for all MAC Adress, IP pairs
            index+=1
        #print(self.macAddressDict)
    
    
    
    ###Wish there was a better way to do this but this has to do
    ###Set up individual ping commands for buttons on each row
    ###This command calls a basic template command that then uses row information to do ping functions
    
    
    def pingIpOne(self):
        #Call driver with row of button press
        self.pingDriver(1)
        #set up a 30sec interval to recall driver if both fields have not been cleared
        if(self.cells[1][0].get() != "" and self.cells[1][1].get() != ""):
            root.after(30000,self.pingIpOne)
        else:
            self.cells[1][2].config(text = "Status:")
            self.cells[1][1].insert(0,"")
                     
    def pingIpTwo(self):
        #Call driver with row of button press
        self.pingDriver(2)
        #set up a 30sec interval to recall driver if both fields have not been cleared
        if(self.cells[2][0].get() != "" and self.cells[2][1].get() != ""):
                root.after(30000,self.pingIpTwo)
        else:
            self.cells[2][2].config(text = "Status:")
            self.cells[2][1].insert(0,"") 
                  
    def pingIpThree(self):
        #Call driver with row of button press
        self.pingDriver(3)
        #set up a 30sec interval to recall driver if both fields have not been cleared
        if(self.cells[3][0].get() != "" and self.cells[3][1].get() != ""):
                root.after(30000,self.pingIpThree)
        else:
            self.cells[3][2].config(text = "Status:")
            self.cells[3][1].insert(0,"") 
                    
    def pingIpFour(self):
        #Call driver with row of button press
        self.pingDriver(4)
        #set up a 30sec interval to recall driver if both fields have not been cleared
        if(self.cells[4][0].get() != "" and self.cells[4][1].get() != ""):
                root.after(30000,self.pingIpFour)
        else:
            self.cells[4][2].config(text = "Status:")
            self.cells[4][1].insert(0,"")      
                      
    def pingIpFive(self):
        #Call driver with row of button press
        self.pingDriver(5)
        #set up a 30sec interval to recall driver if both fields have not been cleared
        if(self.cells[5][0].get() != "" and self.cells[5][1].get() != ""):
                root.after(30000,self.pingIpFive)
        else:
            self.cells[5][2].config(text = "Status:")
            self.cells[5][1].insert(0,"")         
              
    def pingCommand(self,ip):
        #check to see the system user is running and choose which parameter to use for count based on that system
        countParam = '-n' if platform.system().lower()=='windows' else '-c'
        #set up the process to ping device once
        proc = subprocess.Popen(
            ['ping',countParam,'1',ip],
            stdout=subprocess.PIPE
        )
        
        stdout, stderr = proc.communicate()
        #Set up command output into a array
        #Array index 2 always holds stats that show if request was reachable
        #use these stats to determine if the device is on the network or not
        output = stdout.decode('ASCII').split("\n")
        if 'Destination host unreachable.' in output[2]:
            #print(output)
            return False
        else:
            #print(output)
            return True        
       
    def pingDriver(self,row):
        #Collect both IP and MAC entry
        deviceIp = str(self.cells[row][0].get())
        deviceMac = self.cells[row][1].get()
        
        #check to see if MAC address is there and IP isn't
        #since it is more likely for an IP to be on a network and a device MAC to not be in the ARP table, this program chooses IP as the priority for searching
        if not deviceIp and deviceMac != None:
            #check to see if MAC in ARP table, run rest of program with that devices IP
            if self.macAddressDict.get(deviceMac):
                deviceIp = self.macAddressDict[deviceMac]
                self.cells[row][0].insert(0,deviceIp)
            #device MAC not in ARP table, cannot move further based on this entry
            else:
                if(deviceIp):
                    self.cells[row][1].insert(0,"Device MAC not found")
                return
        
        #print("This will ping IP:",deviceIp)
        #run ping command and save boolean var to check online status
        onlineStatus = self.pingCommand(deviceIp)
        
        #check if device is in ARP table already
        if self.ipAddressDict.get(deviceIp):
            #print("found MAC in table")
            self.cells[row][1].delete(0,'end')
            self.cells[row][1].insert(0,self.ipAddressDict[deviceIp])
            
        #not in ARP, try nmap scan for specific IP to get MAC address
        else:
            self.nmap(deviceIp)
            #after nmap check if device is now in updated ARP Table
            if self.ipAddressDict.get(deviceIp):
                self.cells[row][1].delete(0,'end')
                self.cells[row][1].insert(0,self.ipAddressDict[deviceIp])
            #Device MAC still not in ARP table
            else:
                self.cells[row][1].delete(0,'end')
                self.cells[1][1].insert(0,"MAC not found")
        
        #Update online status label based on result from ping
        if onlineStatus:
            self.cells[row][2].config(text = "Status: Online")
        else:
            self.cells[row][2].config(text = "Status: Offline")
            
            
root = Tk()
window = Window(root)
#root.after(5000,window.pingDriver(1))
root.mainloop()
