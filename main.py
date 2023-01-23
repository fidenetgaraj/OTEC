#Bismillahirrahmanirrahim
#imports 
from time import sleep
import machine, neopixel
from machine import Pin, UART
from pinDef import pinDef
from collections import namedtuple
import sys
from settings import readSettings, modifySettings
#variables
gsn = "" # GSM serial Number
ccid = "" # Caller Id
ticks = False
callIsActive = False
day = ""
month = ""
year = ""
clck = ""
mnts = ""
scnds = ""


timeData = []
gpsData = []

lat = ""
latPole = ""
long = ""
longPole = ""
speedAsKnots = ""
speedAsKm = ""
cog = ""
authUsers = []

bckspc = bytes([26])
bigger = ">"

wholeGPSSentence = False
validGPSData = False
            
#define  pins
np = neopixel.NeoPixel(machine.Pin(pinDef.neoPixel), pinDef.neoPixelCount)
ledA = Pin(pinDef.userLed0, Pin.OUT)    # define user LedA
ledB = Pin(pinDef.userLed1, Pin.OUT)    # define user LedB

r0 = 0
r1 = 0
g0 = 0
g1 = 0
b0 = 0
b1 = 0


#defining pins
gsmWakeUpPin = Pin(pinDef.gsmWakeUp, Pin.OUT)
ap4890EnPin = Pin(pinDef.ap4890En, Pin.OUT)
tlvEnPin = Pin(pinDef.tlvEn, Pin.OUT)
gpsForceOnPin = Pin(pinDef.gpsFOn, Pin.OUT)
gsmRiPin = Pin(pinDef.gsmRI, Pin.IN)
gsmPOutPin = Pin(pinDef.gsmExtPower, Pin.IN)
btnA = Pin(pinDef.btnA, Pin.IN)
btnB = Pin(pinDef.btnB, Pin.IN)



#namedTuple defines
atCmd = namedtuple("atcmd", ("text", "timeout", "response"))
# gsm Commands
at = atCmd("AT\r", 300, ["OK", "ERROR"])
atA = atCmd("ATA\r", 300, ["OK", "ERROR"])
atD = atCmd("ATD", 1000, ["OK",  "ERROR"])
atH = atCmd("ATH\r", 1000, ["OK",  "ERROR"])
atS0 = atCmd("ATS0=4\r", 300, ["OK",  "ERROR"])
atQMOSTAT = atCmd("AT+QMOSTAT=1\r", 300, ["OK",  "ERROR"])
atQAUDCH = atCmd("AT+QAUDCH=0\r", 300, ["OK",  "ERROR"])
atQMIC = atCmd("AT+QMIC=0,5\r", 300,  ["OK",  "ERROR"])
atCRSL = atCmd("AT+CRSL=90\r", 300, ["OK",  "ERROR"])
atE0 = atCmd("ATE0\r",  300,  ["OK",  "ERROR"])# Command Echo
atL3 = atCmd("ATL3\r",  300,  ["OK",  "ERROR"])# Ses Seviyesi (en yüksekte)
atCLVL = atCmd("AT+CLVL=40\r",  300,  ["OK",  "ERROR"])# Ses Seviyesi (en yüksekte) 
atCLIP1 = atCmd("AT+CLIP=1\r",  300,  ["OK",  "ERROR"])# Calling Id presentation
atCPIN = atCmd("ATCPIN?\r",  300,  ["OK",  "ERROR"])# Command Echo
atQGSN = atCmd("AT+QGSN\r",  3000,  ["OK",  "ERROR"]) # Gsm Serial Number
atCCID = atCmd("AT+CCID\r",  300,  ["OK",  "ERROR"]) # Sim Abone No
atQNITZ = atCmd("AT+QNITZ=1\r",  3000,  ["OK",  "ERROR"]) # Network Time Sync Enable
atCTZU = atCmd("AT+CTZU=3\r",  3000,  ["OK",  "ERROR"]) # Localized Time Sync
atCTZR = atCmd("AT+CTZR=1\r",  3000,  ["OK",  "ERROR"]) # Time Sync Bildirimi
atCCLK = atCmd("AT+CCLK?\r",  1000,  ["OK",  "ERROR"])  # Saat?
#atQGNSSC = atCmd("AT+QGNSSC=1\r",  300,  ["OK",  "ERROR"])  # GNSS Power On
#atQGNSS = atCmd("AT+QGNSS=0\r",  300,  ["OK",  "ERROR", "+CME ERROR:"])  # GNSS NMEA Tipi
atCMGF = atCmd("AT+CMGF=1\r",  300,  ["OK",  "ERROR", "+CME ERROR:"])  # SMS Format
atCNMI = atCmd("AT+CNMI=2, 1\r",  300,  ["OK",  "ERROR", "+CME ERROR:"])  # SMS Notification Type
atQNSTATUS = atCmd("AT+QNSTATUS\r",  1000,  ["OK",  "ERROR"])  # Network Status
atCSQ = atCmd("AT+CSQ\r",  300,  ["OK",  "ERROR",  "+CME ERROR:"])  # Signal Quality
atCREG = atCmd("AT+CREG?\r",  300,  ["OK",  "ERROR", "+CME ERROR:", "+CREG:"])  # Signal Quality
atCOPS = atCmd("AT+COPS?\r", 300, ["OK", "ERROR"]) # Operator Names
atCMGL = atCmd('AT+CMGL="REC UNREAD"\r', 3000,  ["OK",  "ERROR"])
atCMGD = atCmd("AT+CMGD=1, 4\r", 3000,  ["OK",  "ERROR"])
atQMGDA = atCmd("""AT+QMGDA="DEL ALL"\r""", 3000,  ["OK",  "ERROR"]) #Bütün SMSleri sil
atCMGS = atCmd("AT+CMGS=", 5000, ["OK", "ERROR"])
atCSCS = atCmd("""AT+CSCS="GSM"\r""", 5000, ["OK", "ERROR"])
#atQGNSSRD = atCmd("AT+QGNSSRD?\r", 3000, ["OK",  "ERROR"])
atCSMP = atCmd("AT+CSMP=17, 167, 0, 0\r", 1000, ["OK",  "ERROR"])
atCSCS = atCmd('AT+CSCS="GSM"\r', 1000, ["OK",  "ERROR"])
atQIFGCNT = atCmd("AT+QIFGCNT=0\r", 1000, ["OK",  "ERROR"])
atQICSGP = atCmd('AT+QICSGP=1, "INTERNET", "", ""\r', 1000, ["OK",  "ERROR"])
atQIREGAPP=atCmd("AT+QIREGAPP\r", 5000, ["OK",  "ERROR"])
atCGATT = atCmd("AT+CGATT?\r", 5000, ["OK",  "ERROR"])
atQIACT = atCmd("AT+QIACT\r", 5000, ["OK",  "ERROR"])
atQLOCCFG = atCmd("AT+QLOCCFG?\r", 5000, ["OK",  "ERROR"])
atQCELLLOC = atCmd("AT+QCELLLOC\r", 5000, ["OK",  "ERROR"])
atCPBS = atCmd("""AT+CPBS="SM"\r""", 5000, ["OK",  "ERROR"])
atCPBW = atCmd("""AT+CPBW={},"{}",145,"{}"\r""", 5000, ["OK",  "ERROR"])
atCPBR = atCmd("AT+CPBR={}\r", 30000, ["OK",  "ERROR"])
atCNUM = atCmd("AT+CNUM\r", 3000, ["OK",  "ERROR"])


#defining UARTS
gsm = UART(pinDef.gsmCh, baudrate=115200, tx = Pin(pinDef.gsmTx), rx = Pin(pinDef.gsmRx))
gps = UART(pinDef.gpsCh, baudrate=9600, tx = Pin(pinDef.gpsTx), rx = Pin(pinDef.gpsRx))

def notice(ch, r = 0, g = 0, b= 0):
    global r0
    global r1
    global g0
    global g1
    global b0
    global b1
    
    if ch == 0:
        r0 = r
        g0 = g
        b0 = b
    elif ch == 1:
        r1 = r
        g1 = g
        b1 = b
    
    np[0] = (r0, g0, b0)
    np[1] = (r1, g1, b1)
    np.write()
    

def chkGSMIsOn():
    extPower = gsmPOutPin.value()
    if extPower == 0:
        gsmWakeUpPin.on()
        sleep(1)
        gsmWakeUpPin.off()
        sleep(10)
        info("gsm Module is turned on \r\n", "chkGSMIsOn")
    else:
        info("gsm Module is already on \r\n")

def shutDownGsm():
    
    extPower = gsmPOutPin.value()
    if extPower == 1:
        info("GSM Module is now on and will be shut down", title = "shutDownGsm")
        gsmWakeUpPin.on()
        sleep(1)
        gsmWakeUpPin.off()
        sleep(5)
        extPower = gsmPOutPin.value()
        if extPower == 0:
            info("GSM Module is power down", title = "shutDownGsm")
        else:
            info("GSM Module is still on", title =  "shutDownGsm")
    else:
        info("GSM Module is already off", title = "shutDownGsm")
    
    
   
        

def info(text, sender = "", title = ""):
    raw = "<info: {}".format(text)
    if sender !="":
        raw = raw + " sender: {}".format(sender)
    if title !="":
        raw = raw + " title: {}".format(title)
    raw = raw + ">\r\n"
    print(raw)
      
def getAuthUsers():
    
    global authUsers
    phonebook = []
    authUsers = []
    raw = sendCmd(atCPBR, 1)
    if raw[1] != "":
        authUsers.append(raw[1])
        phonebook.append(raw)
    raw = sendCmd(atCPBR, 2)
    if raw[1] != "":
        authUsers.append(raw[1])
        phonebook.append(raw)
    info(authUsers, title = "AuthUsers")
    return phonebook

def sendCmd(cmd, param = ""):
    global ccid
    global timeData
    global authUsers
    global callIsActive
    global gpsData
    global validGPSData
    
    if cmd != "":
            
        raw = cmd.text    
        if raw == "ATD":
            raw = "ATD{};\r".format(param)
        
        if "AT+CMGS=" in raw:
            raw = """AT+CMGS="{}"\r""".format(param)
        
        if "AT+CPBW" in raw:
            raw = cmd.text.format(param[0], param[1], param[2])
        
        if "AT+CPBR" in raw:
            raw = cmd.text.format(param)
            
        
        text = raw.encode("utf-8")
        info(text, "sendCmd", "cmd") 
        
        gsm.write(text)
        timeout = cmd.timeout
    else:
        timeout = 100
    sayac = 0
    prev = 1
    resp = ""
    act = 0
    
    while(sayac < timeout):
        sayac += 1
        if sayac % 100 == 0 and gsm.any() > 0:
            prev = act
        sleep(1/1000)
        act = gsm.any()
        
        if prev == act:
            text = "prev: {}, sayac: {}".format(prev, sayac)
            info(text, "sendCmd", "getText")
            sayac = timeout
    if (sayac == timeout) and (gsm.any() == 0):
        info("cevap Yok")
    else:
        sleep(0.2)
        raw = gsm.read(gsm.any())
        info(raw, "sendCmd", "resp")
        resp = raw.decode("utf-8")
        
        if bigger in resp:
            info("sms bigger chk", title = "SMS")
    
        
        if "MO RING" in resp:
            #ap4890EnPin.on()
            info("begin Calling")
            callIsActive = False
        
        elif "MO CONNECTED" in resp:
            ap4890EnPin.on()
            info("Connected")
            callIsActive = True
            
            
        elif "+CLIP:" in resp:
            dialer = resp.split('"')[1]
            info(dialer, "CID")
            if dialer in authUsers:
                    
                ap4890EnPin.on()
                #sendCmd(atA)
                info("answer the call")
                callIsActive = True
            else:
                sendCmd(atH)
        elif "NO CARRIER" in resp:
            ap4890EnPin.off()
            info("end Calling")
            callIsActive = False
        
        elif "BUSY" in resp:
            ap4890EnPin.off()
            info("cancel Calling")
            callIsActive = False
        
        elif "+CMTI:" in resp: #SMS mesaj var
            sendCmd(atCMGL)
    
        elif "QGSN" in resp:
            raw = resp.split("\r\n")[1]
            gsn = raw.split('"')[1]
            info(gsn, title = "QGSN")
            
            
        elif "CCID" in resp:
            ccid = resp.split(':')[1].split("\r\n")[0].strip(' ').strip('"')
            info(ccid, title = "CCID")
            return ccid
     
        elif "+CCLK" in resp:
            """AT+CCLK?\r\r\n+CCLK: "22/12/22,10:57:13+12"\r\n\r\nOK\r\n"""
            currTime = resp.split('"')[1].split(",")[1].split("+")[0]
            clck = currTime[:2]
            mnts = currTime[3:5]
            scnds = currTime[6:]
            
            currDate = resp.split('"')[1].split(",")[0]
            year = currDate[:2]
            month = currDate[3:5]
            day = currDate[6:]
            
            #print(f"year:{year}, month:{month}, day:{day}, clck: {clck}, mnts: {mnts}, sec:{scnds} \r\n")
            
            timeData = [year, month, day, clck, mnts, scnds]
            info(timeData, "sendCmd", "currTime")
            
        
        elif "CMGL" in resp:
            """AT+CMGL="REC UNREAD"\r\r\n+CMGL: 11,"REC UNREAD","+9050xxxxxxx","","2022/12/25 01:37:40+12"\r\nMerhaba \r\n\r\nOK\r\n"""
            smsContainer = resp.split("\r\n")
            if len(smsContainer) > 3:
                owner = smsContainer[1].split(",")[2].strip('"')
                smsTime = smsContainer[1].split(",")[4].strip('"')
                smsBody = smsContainer[2]
                smsYear = smsTime[:4]
                smsMonth = smsTime[5:7]
                smsDay = smsTime[8:10]
                smsHour = smsTime[11:13]
                smsMinute = smsTime[14:16]
                smsSecond = smsTime[17:19]
                sms = [owner, smsBody, smsYear, smsMonth, smsDay, smsHour, smsMinute, smsSecond]
                                 
                info(sms, "SMS")
                #Sms ile ilgili işlemler buradan devam edecek
                if "ekle" in smsBody.lower():
                    info("Ekle Rutinine giriş yapıldı", "Ekle")
                    raw = smsBody.split(",")
                    key = raw[1]
                    index = raw[2]
                    text = raw[3]
                    if key == ccid[14:]:
                        saveToSIM(index, owner, text)
                        info("Added to SIM", title = "saveToSIM")
                        pb = getAuthUsers()
                        info(pb, title = "pb")
                        sleep(1)
                        user1 = ""
                        user2 = ""
                        try:
                            user1 = f" {pb[0][2]}, {pb[0][1]} "
                            user2 = f" {pb[1][2]}, {pb[1][1]} "
                        except:
                            pass
                        
                        text = "{} number saved at order {}\r\n AuthUsers: \r\n1->:{} \r\n 2->: {}\r\n".format(owner, index, user1, user2)
                        
                        sendSMS(owner, text)
                        
                        
                    else:
                        text = "CCID last 6 key is invalid"
                        sendSMS(owner, text) 
                
                elif owner in authUsers:
                    if  "reply" in smsBody.lower():
                        smsText  = "this is an OTEC generated SMS"
                        sendSMS(owner, smsText)
                    
                    elif ("activate" in smsBody.lower()) and ("tracking"  in smsBody.lower()) and not ("deactivate" in smsBody.lower()):
                        configureGPS()
                        text = "GPS Tracking is activated"
                        modifySettings("tracking", "on")
                        sendSMS(owner, text)
                        
                    
                    elif ("deactivate" in smsBody.lower()) and ("tracking"  in smsBody.lower()):
                        tlvEnPin.off() #aynı zamanda SHT30 ve I2C port enerjisi de kesiliyor. Dikkat
                        gpsForceOnPin.off()
                        text = "GPS Tracking is deactivated"
                        modifySettings("tracking", "off")
                        sendSMS(owner, text)
                    elif "led" in smsBody.lower():
                        raw = smsBody.split("=")[1].split(",")
                        np[0] = (0,0,0)
                        np[1] = (0,0,0)
                        
                        order = int(raw[0])
                        r = int(raw[1])
                        g = int(raw[2])
                        b = int(raw[3])
                        np[order] = (r,g,b)
                        np.write()
                    elif "loc" in smsBody.lower():
                        #https://www.google.com/maps/@37.xxxxx,30.xxxxxx,15z
                        # 37xxxxx,N,03034xxxxx,E
                        #gpsData = [latitude, latitudePole, longitude, longitudePole, speedAsKnots, speedAsKm, cog, timeData]
                        #timeData = [year, month, day, clck, mnts, scnds]
                        latitude = gpsData[0] #"37xxxxx
                        latitudePole = gpsData[1] #"N"
                        longitude  = gpsData[2] #"030xxxxx0"
                        longitudePole = gpsData[3] #"E"
                        
                        link = "https://www.google.com.tr/maps/place/{}{}+{}{}"
                        timeData = gpsData[7]
                        timeText = "Last Valid GPS is taken at (yy/mm/dd hh:mm) {}/{}/{} {}:{}".format(timeData[0], timeData[1], timeData[2], timeData[3], timeData[4])
                        #"https://www.google.com/maps/@{},{},15z"

                        latitudeDeg = int(latitude[:2])
                        latitudeRest = float( latitude[2:4] + "." + latitude[5:]) / 60
                        longitudeDeg = int(longitude[:3])
                        longitudeRest = float( longitude[3:5] + "." + longitude[6:]) / 60
                        mapslatitude = latitudeDeg + latitudeRest
                        mapslongitude  = longitudeDeg + longitudeRest
                        gpsText = link.format(mapslatitude, latitudePole, mapslongitude, longitudePole)
                        text = "{}\r\n{}".format(gpsText, timeText)
                        sendSMS(owner, text)
                    
                    elif "gps" in smsBody.lower():
                        if validGPSData == True:
                            text = gpsData[0] + "," + gpsData[1] + ";" + gpsData[2] + "," + gpsData[3] 
                        else:
                            text = "there is no valid GPS Data"
                        sendSMS(owner, text)
                        
                        
                        
                
                        
                else:
                    text = "Unauthorized user!!!"
                    info(text, title = "SMS User")
                    #sendSMS(owner, "Unauthorized user!!!")
                    
                
                    
                # iş bittikten sonra gelen smsleri silecek bir rutin ekle
                
                sendCmd(atQMGDA)
        elif "+CPBR" in resp:
            """AT+CPBR=1\r\r\n+CPBR: 1,"+90505xxxx",145,"Fxxx"\r\n\r\nOK\r\n"""
            raw = resp.split(":")[1].split("\r\n")
            loc = raw[0].split(",")[0].strip()
            number = raw[0].split(",")[1].strip('"')
            text = raw[0].split(",")[3].strip('"')
            pB = [loc, number, text]
            info(pB, title = "phoneBook")
            return pB
        
            
                
            
        
        else:
            return resp
    
def saveToSIM(index, nr, text):
    params = [index, nr, text]
    sendCmd(atCPBW, params)
    
    
def sendSMS(num,text):
    resp = sendCmd(atCMGS, num)
    info(resp ," '>' waiting")
    if bigger in resp: 	
        gsm.write(text.encode('utf-8'))
        gsm.write(bckspc)
    info(text, "smsGonder")

"""
b'$GPGGA,095731.000,37xx.xxxx,N,030xx.xxxxx,E'b',2,8,1.11,814.2,M,36.2,M,,*58\r\n
$GNGSA,A,3,07,13,05,14,20,,,,,,,,1.41,1.11,0.87,1*0C\r\n
$GNGSA,'b'A,3,78,68,66,,,,,,,,,,1.41,1.11,0.87,2*09\r\n
$GPGSV,3,1,10,30,71,354,,14,61,177,16,07,45,053,1'b'8,20,44,247,41,0*6A\r\n
$GPGSV,3,2,10,05,38,295,39,49,38,218,37,09,28,118,12,13,27,308,26,0*66\r'b'\n
$GPGSV,3,3,10,08,14,058,,17,01,158,,0*6F\r\n
$GLGSV,2,1,08,67,69,141,23,78,65,254,25,68,54,330'b',24,77,46,028,,1*71\r\n
$GLGSV,2,2,08,66,16,145,31,79,15,229,20,69,05,327,,76,01,040,,1*7C\r\n
$GNGL'b'L,3727.2303,N,03034.9980,E,095731.000,A,D*44\r\n
$GPTXT,01,01,02,ANTSTATUS=OPEN*2B\r\n'

"""
def configureGPS():
    global gps
    
    info("configureGPS", "configureGPS")
    gpsForceOnPin.on() # GPS force On pin açık
    tlvEnPin.on() # GPS besleme açık
    sleep(1)
    
    info("baudrate Change", "configureGPS")
    cmd = "$PQBAUD,W,115200*43\r\n".encode("utf-8")
    gps.write(cmd)
    sleep(1/2)
    gpsResp = gps.read(gps.any())
    print(gpsResp)
    
    try:
        print("baud: 9600: {}\r\n".format(gpsResp))
        text = gpsResp.decode("utf-8")
        print(text)
        
    except UnicodeError:
        print("exception\r\n")
        sleep(1/2)
        
        gps = UART(pinDef.gpsCh, baudrate = 115200, tx = Pin(pinDef.gpsTx), rx = Pin(pinDef.gpsRx))

        sleep(1/2)
        gpsResp = gps.read(gps.any())
        info("baud: 115200", "configureGPS")
        text = gpsResp.decode("utf-8")
        print(gpsResp)
        print(text)
        
        info("gps Sentence Format Change", "configureGPS")
        cmd = "$PMTK314,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*34\r\n"
        gps.write(cmd)
        sleep(1/2)
        gpsResp = gps.read(gps.any())
        print(gpsResp)
        sleep(1/2)
            
    
def getGPSSentence():  
    global lat
    global latPole 
    global long
    global longPole
    global speedAsKnots
    global speedAsKm
    global cog
    global validGPSData
    global gpsData
    global timeData
    
    
    sayac = 0
    prev = 1
    resp = ""
    act = 0
    timeout = 100
    
    while(sayac < timeout):
        sayac += 1
        if sayac % 50 == 0 and gps.any() > 0:
            prev = act
        sleep(1/1000)
        act = gps.any()
        
        if prev == act:
            text = "prev: {}, sayac: {}".format(prev, sayac)
            info(text, "getGPSSentence")
            sayac = timeout
            raw = gps.read(gps.any())
            info(raw, "getGPSSentence")
            resp = raw.decode("utf-8")
            
            gpsContainer = resp.split("\r\n")
            info(gpsContainer, "GPS")
            for i in gpsContainer:
                #$GNRMC,095731.000,A,37xx.xxxx,N,030xx.xxxx,E,0.00,193.26,241222'b',,,D,V*03\r\n
                if (("$GPRMC" in i ) or ("$GNRMC" in i )) and (len(i) > 70):
                    gprmcContainer = i.split(",")
                    if gprmcContainer[2] == "A":
                        validGPSData = True
                    elif gprmcContainer[2] == "V":
                        validGPSData = False
                    
                    if validGPSData == True:
                        latitude = gprmcContainer[3]
                        latitudePole = gprmcContainer[4]
                        longitude = gprmcContainer[5]
                        longitudePole = gprmcContainer[6]
                        speedAsKnots = gprmcContainer[7]
                        cog = gprmcContainer[8]
                        gpsData = [latitude, latitudePole, longitude, longitudePole, speedAsKnots, speedAsKm, cog, timeData]
                        info(gpsData, title = "GPRMC")
                        
                elif (("$GPRMC" in i ) or ("$GNRMC" in i )) and (len(i) < 70):
                        gprmcContainer = i.split(",")
                        if gprmcContainer[2] == "V":
                            validGPSData = False  
                    #$GPVTG,193.26,T,,M,0.00,N,0.00,K,D*37\r\n    
                if ("$GPVTG" in i ) or ("$GNVTG" in i ):
                    gpvtgContainer = i.split(",")
                    if gpvtgContainer[2] == "T":
                        speedAsKm = gprmcContainer[7]
                        info(speedAsKm, "GPVTG")
            
                if validGPSData == True:
                    return(gpsData)
                else:
                    return("")
    
notice(0, b = 20)
configureGPS()

notice(0)
shutDownGsm()

notice(0, r = 20)

chkGSMIsOn()

notice(0, b = 20)

status = readSettings("tracking")
info(status, title = "Tracking Status")
if status == "on": #ayarlar dosyasından kayıtlı durumu oku ve ona göre açılışta GPS'i aç/kapa
    tlvEnPin.on() # TLV aynı zamanda GPS, SHT30 ve I2C portlarını da enerjilendiriyor. İleride sıkıntı açabilir. 
else:     
    tlvEnPin.off() # TLV aynı zamanda GPS, SHT30 ve I2C portlarını da enerjilendiriyor. İleride sıkıntı açabilir. 


gpsForceOnPin.on()
ap4890EnPin.off() # Enerji tüketmesin şimdilik. Çağrı olunca açarız. 

notice(0, g = 20)
response = sendCmd(at)
print(response)
#wait for access SIM

sendCmd(atQGSN)
sendCmd(atCCID)
sendCmd(atQNITZ)
sendCmd(atCTZU)
sendCmd(atCTZR)
sendCmd(atCCLK)
sendCmd(atCLIP1)
sendCmd(atS0)
sendCmd(atQMOSTAT)
sendCmd(atCRSL)
sendCmd(atL3)
sendCmd(atCLVL)
sendCmd(atQAUDCH)
sendCmd(atQMIC)


sendCmd(atCMGF)
sendCmd(atCNMI)
sendCmd(atCMGL)
sendCmd(atCSCS)
sendCmd(atCPBS)
#sendCmd(atCMGD)
response = sendCmd(atCNUM)
print(response)
getAuthUsers()

notice(0)

sayac = 0
gpsContainer = []
while(True):
    
    sayac+=1
    sleep(1/1000)
    btnAStt = btnA.value()
    btnBStt = btnB.value()
    ri = gsmRiPin.value()
    raw = str(btnAStt) + "," + str(btnBStt)  
    #info(raw, title = "btnA,btnB")
    if btnAStt == 0: # Butonlardan birine basıldı ise
        telNum = sendCmd(atCPBR,1)[1] 
        if callIsActive == True: # aktif çağrı varsa
            info("Cancel the call", title = "btnState")
            sendCmd(atH)
            callIsActive = False
            sleep(3)
        else:
            text = f"dialing: {telNum}"
            info(text, title = "btnState")
            sendCmd(atD, telNum ) # sim kart lokasyon ile değişecek 
            sleep(3)
            
    if btnBStt == 0: # Butonlardan birine basıldı ise
        telNum = sendCmd(atCPBR,2)[1] 
        if callIsActive == True: # aktif çağrı varsa
            info("Cancel the call", title = "btnState")
            sendCmd(atH)
            callIsActive = False
            sleep(3)
        else:
            text = f"dialing: {telNum}"
            info(text, title = "btnState")
            sendCmd(atD, telNum ) # sim kart lokasyon ile değişecek
            sleep(3)


    if sayac % 50 == 0:
        if validGPSData == True:
            notice(1, g = 20)
        else:
            notice(1, r = 20)
        
        if gsm.any() > 0 :
            sendCmd("")  
        
        if gps.any() >0:
            getGPSSentence()
                    
    if sayac % 500 == 0: # 1sn de 2
        info(callIsActive, "call status", "while")
        

    if sayac % 1000 == 0: # 1sn de 1
        ticks = not ticks
        if ticks == True:
            notice(0, g = 20)
        else:
            notice(0)
        
    if sayac % 2000 == 0: # 2sn de 1
        pass
    if sayac % 10000 == 0: # 10sn de 1
        sendCmd(atCCLK)   
    if sayac % 60000 == 0: # 1dk de 1
        sendCmd(atCCID)
        #SIM karttaki 1 ve 2. sırada kayıtlı numaraları güncelle
        authUsers = []
        raw = sendCmd(atCPBR, 1)
        if raw[1] != "":
            authUsers.append(raw[1])

        raw = sendCmd(atCPBR, 2)
        if raw[1] != "":
            authUsers.append(raw[1])

        info(authUsers, title = "AuthUsers")




