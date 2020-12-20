#!/usr/bin/env  python3
# -*- coding: utf-8 -*-
########################################################################
# 
# 19-12-2020 11h03
'''     Alarme porte ababdon si reste ouverte A faire Garage seul
réinit apres 5 radars '''

T_Sirene = 60 ; T_Susp = 60

import os
import time
import math
from datetime import datetime
datetime.now()
now  = datetime.now()
heur = now.strftime('%Y-%m-%d %H:%M:%S')
from ftplib import FTP

import lcddriver
import smbus
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte
import RPi.GPIO as GPIO
#import time
import Freenove_DHT as DHT
import DHT11
from DHT11 import *
#import Adafruit_DHT
import lec_bme
import bme280
from bme280  import readBME280All #*
from PCF8574 import PCF8574_GPIO
import board
import busio
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017
import Q   # quantieme
#import manipZero
i2c = busio.I2C(board.SCL, board.SDA)
mcp = MCP23017(i2c)  # MCP23017

nom_ssd = '/media/pi/'+'1c0d1c50-8371-4e0a-b02c-fdc5f2639440'
EDF_OK=True;PORTAIL_O=True;J_N="Nuit";Mradar=False;Mcoul=False;Mgarage=False;Mportes=False;m_alarmeG=False
init=True;lcdPret=True
#ftp = FTP('ftpperso.free.fr','blha',tou)
#etat = ftp.getwelcome() # grâce à la fonction getwelcome(), on récupère le "message de bienvenue"
#print ("Etat : ", etat)
#time.sleep(5)
#print (ftp.dir())
#ftp.cwd('_fields')
#print (ftp.dir())
#f_name =  nom_ssd+'/relev.txt'
#f = open(f_name,'rb')
#tp.storbinary('STOR titi.blh', open(f_name,'rb'))
#F1_relev.close()
#ftp.quit()

lcd=lcddriver.lcd()
lcd.lcd_clear()
#------------------------
GPIO.setmode(GPIO.BCM)

jecris      = 0 ; jecrisV   = 0 ; ValeurPluie = .1 ; CapteurPluie= 0 ;aa='xxx'
Veille_Jour = 1 ; Nouv_Jour = 1 ;Temp_bmeA="22.44" ; AformeA = 77 ;mis_ala=False;AHS=False
G18_PROD = 18 # PRODUIT
G23_CONS = 23 # Cons 
G24_PLUI = 24 # PLUIE
G25_VENT = 25 # VENT
G22_sol  = 22 # Q_Soleil
G21_BOUTO = 21 # EclairEx 27
G19_SIR = 19   # Sirene
G26_ALA = 26   # Alarme
G13_MESA= 13   # Alarme mise en servies SHUNT bleu
G27_ECLA= 27 # EX 16 Lampe Ext
G5_SUSP =  5
G7_APPEL = 7
DHTPin = 17   #define the pin of DHT11.py
sensor1 =11 ; pin1    =17 ; sensor2 =22 ;pin2    =6
######################################"DHTPin = 17 #    #define the pin dans  DHT11
GPIO.setup(G18_PROD,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(G18_PROD, GPIO.RISING,bouncetime=20)
GPIO.setup(G23_CONS,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(G23_CONS, GPIO.RISING,bouncetime=200)  #FALLING
GPIO.setup(G24_PLUI,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(G25_VENT,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(G25_VENT, GPIO.RISING)  # active detection front
GPIO.setup(G22_sol,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(G21_BOUTO,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup( G19_SIR, GPIO.OUT)
GPIO.setup( G7_APPEL, GPIO.OUT)
GPIO.setup (G26_ALA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup (G5_SUSP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(G19_SIR, GPIO.LOW)
GPIO.output(G7_APPEL, GPIO.LOW)
GPIO.setup (G26_ALA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup (G13_MESA,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup (G27_ECLA,GPIO.OUT)
GPIO.output(G27_ECLA,GPIO.LOW)
pin0 = mcp.get_pin(0)
pin2 = mcp.get_pin(2)

pin6 = mcp.get_pin(6)
pin7 = mcp.get_pin(7)
pin8 = mcp.get_pin(8)
pin9 = mcp.get_pin(9)
pin10= mcp.get_pin(10)
pin11= mcp.get_pin(11)
pin12= mcp.get_pin(12)
pin13= mcp.get_pin(13)
# Setup pin0 as an output that's at a high logic level.
pin0.switch_to_output(value=False)
pin2.switch_to_output(value=True)
pin6.switch_to_output(value=True)
pin7.switch_to_output(value=True)

pin8.direction = Direction.INPUT
pin9.direction = Direction.INPUT
pin10.direction = Direction.INPUT
pin11.direction = Direction.INPUT
pin12.direction = Direction.INPUT
pin13.direction = Direction.INPUT
pin8.pull = Pull.UP  #met a False
pin9.pull = Pull.UP
pin10.pull = Pull.UP
pin11.pull = Pull.UP
pin12.pull = Pull.UP
pin13.pull = Pull.UP
pin7.value = False
pin6.value = False
pin2.value = False
time.sleep(5)

#pin0.value = True
#time.sleep(22)
#pin0.value = False

#liste= [G18_PROD,G23_CONS,G24_PLUI,G25_VENT,G22_sol,G21_BOUTO,G19_SIR,G26_ALA,G13_MESA,G13]
#for i in liste :
#    print (i)
bb='xxx'
wattp = '' ; wattc = '' #;  vent = 0
global F1_relev, F2_Total, F3_para, F4_meteo, F5_Jour, F6_vent, f7_pluie ,F_Alarme
datetime.now()
GPIO.setwarnings(False)
hum_dh11=0 ; tem_dh11=0  ; vp=True ; Temp_IP="111" ;volts2=0;volts1=14
oncontinu = False ; qu_pluie    = 0
appui = True ; allume = False ; alarme = False ; alar_oper = False ; alar_susp = False ; Alar_S4 = 0
couloir = 0 ; Radar = 0 ; garage = 0;  porte = 0 ; Compt_Autre =0
AlarmeST = False ; Com_1_Alar = 0 ; Appel=0          ;MAppel=0        ; RAZ_m_Ala=0  ; m_GeuleS=False
Compt_A_Por = 0  ;quiAlarme="Vide"; topdepallum  = 0 ; T_deb_Ala  = 0 ; T_fin_Ala =0 ; Alarme_en_cours = False
Million=0   ; M_T_garage =0 ;alar_stop=0 ;Porte_O=False ; Porte_o=0 ; AbandonP=False
Affich_LCD = True
cc='xxx'
F1_relev=' ' ;F2_Total=' ' ;F3_para=' ' ;  F4_meteo=' '; F5_Jour=' '; F6_vent=' '
F7_pluie=' '; F_Alarme=' ' ;Temp_ext=' ';Temp_Eau=''
bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1

PCF8574_address  = 0x27  # I2C address of the PCF8574 chip.
#PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
#mcp = PCF8574_GPIO(PCF8574_address)
topdep = 0
topbme =int (now.strftime('%H') )-1
Heure_Dep=int (now.strftime('%H') )-1
tou=aa+bb+cc

global maxproH,maxproJ
nb_w_pro = 0 ; nb_w_con = 0 ; w_prod_total = 0 ; w_cons_total = 0

cpu = 333 ; compLCD=0

TopFinSus=0;TopDepSus=0
dernier_demarrage =False
import smtplib
from email.mime.text import MIMEText
quoi="rien"


#mot = input("entrez un mot : ")  
#print (mot  )

def mail(quoiM):
    
    message = MIMEText(str(quoiM)+'\n'+'Temperature : '+str(tem_dh11)+'°'+'\n'+'Humidité : '+str(hum_dh11)+'%'+'\n'+'Eau:'+str(tem_dh22)+'\n'+'ip:'+str(change_IP))
   
    heurm = now.strftime('%Y-%m-%d %H:%M:%S.%f')
    message['Subject'] = 'Météo à '+ heurm

    message['From'] = 'xxx@xxx.net'
    message['To'] = 'lacamalolo@laposte.net'

    server = smtplib.SMTP('smtp.laposte.net:587')
    server.starttls()
    server.login('xxx@xxx.net','xxx')
    server.send_message(message)
    server.quit()

def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)
    GPIO.output(clockpin, False) # start clock low
    GPIO.output(cspin, False)    # bring CS low
    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1
    GPIO.output(cspin, True)
    adcout /= 2    # first bit is 'null' so drop it
    return adcout
# ces numeros de pins GPIO doivent etre modifies pour correspondre aux broches utilisées si vous avez utilisé un autre câblage que celui du tutoriel.
SPICLK = 11 ; SPIMISO = 9 ; SPIMOSI = 10 ; SPICS = 8 # definition de l'interface SPI
GPIO.setup(SPIMOSI,GPIO.OUT)
GPIO.setup(SPIMISO,GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS,  GPIO.OUT)
#definition du ADC utilise (broche du MCP3008). Cette valeur peut aller de 0 à 7.
adcnum = 0
tem_dh22=11
hum_dh22=33
'''
def dht_11():
    global tem_dh11, hum_dh11
    sensor=11 #sensor1
    pin=17
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
        hum_dh11=humidity
        tem_dh11=temperature
        
def dht_22():
    global tem_dh22, hum_dh22   
    sensor=22
    pin=6
    temperature=0.0
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if temperature is not None:  
        print('Temp Eau={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
        hum_dh22=humidity
        tem_dh22=temperature
'''        
def cree_fict(Q_Jour0):
    if os.path.isfile( nom_ssd+'/Alarme'+Q_Jour0+'.txt') == False :
        ouvre(Q_Jour,"Alarme","w")
    if os.path.isfile( nom_ssd+'/relev'+Q_Jour0+'.txt') == False :
        ouvre(Q_Jour,"relev1","w")
    if os.path.isfile( nom_ssd+'/total'+Q_Jour0+'.txt') == False :
        ouvre(Q_Jour,2,"w")
    if os.path.isfile( nom_ssd+'/para.txt') == False :
        ouvre(Q_Jour,3,"w")
    else :
        ouvre(Q_Jour,3,"r")
        Veille_Jour = F3_para.read()

    if os.path.isfile( nom_ssd+'/meteo'+Q_Jour0+'.txt') == False :
        ouvre(Q_Jour,4,"w")
    if os.path.isfile( nom_ssd+'/jour'+Q_Jour0+'.txt') == False :
        ouvre(Q_Jour,5,"w")
    if os.path.isfile( nom_ssd+'/vent'+Q_Jour0+'.txt') == False :
        ouvre(Q_Jour,"Vent","w")
    if os.path.isfile( nom_ssd+'/pluie'+Q_Jour0+'.txt') == False :
        ouvre(Q_Jour,7,"w")
        ouvre(Q_Jour,7,"a")
        F7_pluie.write("Pluie"+"\n")
        F7_pluie.close()
def ouvre(Q_Jour,qui,pour) :
    global F1_relev, F2_Total, F3_para, F4_meteo, F5_Jour, F6_vent, \
           F7_pluie, F_Alarme,Temp_ext,Temp_Eau,dernier_demarrage ,Temp_IP
           
    if qui == "Alarme" :
        F_Alarme = open( nom_ssd+'/Alarme'+Q_Jour+'.txt',pour)
    if qui == "relev1" :
        F1_relev = open( nom_ssd+'/relev'+Q_Jour+'.txt',pour)   
    if qui == 2 :
        F2_Total = open( nom_ssd+'/total'+Q_Jour+'.txt',pour)
    if qui == 3 :
        F3_para = open( nom_ssd+'/para.txt',pour)
    if qui == 4 :
        F4_meteo = open( nom_ssd+'/meteo'+Q_Jour+'.txt',pour)
    if qui == 5 :
        F5_Jour  = open( nom_ssd+'/jour'+Q_Jour+ '.txt',pour)
    if qui == "Vent" :
        F6_vent  = open( nom_ssd+'/vent' +Q_Jour+'.txt',pour)
    if qui == 7 :
        F7_pluie = open( nom_ssd+'/pluie'+Q_Jour+'.txt',pour)
    if qui == 8 :
        Temp_ext = open( '/home/pi/t_ext.txt',pour)
    if qui == "Eau9" :
        Temp_Eau   = open( '/home/pi/eau.txt',pour)
    if qui == "Ip10" :
        if os.path.isfile('/home/pi/index.html.2' ) == False :
            Temp_IP   = open( '/home/pi/index.html',pour)
        else :
            Temp_IP   = open( '/home/pi/index.html.2',pour)      
        
    heur = now.strftime('%Y-%m-%d %H:%M:%S')
    if dernier_demarrage == False :
        F_Alarme = open( nom_ssd+'/Alarme'+Q_Jour+'.txt',"a")  
        #9 = open(nom_ssd+'/demar.txt',"w")
        F_Alarme.write(heur+" demarrage du Programme"+'\n')
        dernier_demarrage = True
def jecriV() :
    global F6_vent,jecrisV
    heur = now.strftime('%Y-%m-%d %H:%M:%S')
    ouvre(Q_Jour,"Vent","a")
    jecrisV = 0

def jecri() :
    global F1_relev,jecris
    heur = now.strftime('%Y-%m-%d %H:%M:%S')
    ouvre(Q_Jour,"relev1","a")
    #F1_relev = open( nom_ssd+'/relev'+Q_Jour+'.txt','a')
    F1_relev.write(" --jecris--- "+heur+'\n')
    jecris = 0

def quant():
    dd = int(now.strftime('%d'))
    dm = int(now.strftime('%m'))
    da = int(now.strftime('%Y'))
    dj=[dd,dm,da]
    global Nouv_Jour  #  +str(Veille_Jour)+" Cons Totale "+str(nb_w_con)+" Max H "+str(maxproH)+'\n')

    Nouv_Jour = (Q.numjouran(dj))

def d11_loop():
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    sumCnt = 0              #number of reading times
    while(True):
        sumCnt += 1         #counting number of reading times
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        #print ("The sumCnt is : %d, \t chk    : %d"%(sumCnt,chk))
        if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            print("DHT11,OK!")

            global hum_dh11,tem_dh11
            hum_dh11 = (dht.humidity)
            tem_dh11 = (dht.temperature)
            print(tem_dh11)
        return

def compt_zero():
    global nb_w_pro,F2_Total,nb_w_con,w_cons_total,w_prod_total,maxproH,maxproJ,Q_Jour,init,nom_ssd,maxpro,nbtour
    w_prod_total = w_prod_total + nb_w_pro
    w_cons_total = w_cons_total + nb_w_con
    ouvre(Q_Jour,2,"a")
    heur = now.strftime('%Y-%m-%d %H:%M:%S')
    F2_Total.write(heur+" Prod Totale "+str(nb_w_pro)+'     '\
    +str(Veille_Jour)+" Cons Totale "+str(nb_w_con)+" Max H "+str(maxproH)+'\n')
    #F2_Total.write(" Cons Totale "+str(nb_w_con)+' ------ '+'\n')
    F2_Total.close()
    maxproH = 0
       
    ouvre(Q_Jour,5,"a")
    F5_Jour.write(heur+" Prod Totale jour "+str(w_prod_total)+" Max Jour :"+str(maxproJ)+\
    "  Cons Totale jour "+str(w_cons_total)+'\n')
         
    if heur=="00:00:00" or init == True or  Minuit==True:
        print(heur,"*Int-->",init,"*Min->",Minuit,"**  RAZ  *******")
        init=False
        maxproJ=0;w_prod_total=0;w_cons_total=0;maxpro=0;nbtour=0 ; nb_w_pro = 0 ; nb_w_con = 0 
    Q_Jour=str(Nouv_Jour)
    F5_Jour.close()
    nbtour=0
def ref_dep(gp):
    global topdep , now , Million , H_ref_pro,Cons_actu,Vent_actu,ref_prod,ref_cons,H_actuel,Porte_o
    global alar_mes,T_deb_Ala,alar_stop,T_fin_Ala,ref_vent,ref_calm,Com_1_Alar,topdepetin
    global topdepallum,TopDepSus,TopFinSus,top5000,Appel,MAppel,RAZ_m_Ala,M_T_garage
    now = datetime.now()
    heur = now.strftime('%Y-%m-%d %H:%M:%S.%f')

    Sec_Milion = now.strftime('%S.%f')
    titi = int( (Sec_Milion[3:9]))
    Million=titi/1000000
    topdep = (int (now.strftime('%H') )* 3600)+(int (now.strftime('%M') )* 60)+(int (now.strftime('%S')))+Million
    if gp == "H_actuel" :
        H_actuel = (topdep)
    elif gp == "Prod" :
        ref_prod = (topdep)
    elif gp=="Cons":
        ref_cons = (topdep)
    elif gp=="Vent":
        ref_vent = (topdep)
    elif gp=="H_ref_pro":
        H_ref_pro = (topdep)
    elif gp=="Cons_actu":
        Cons_actu = (topdep)
    elif gp=="Vent_actu":
        Vent_actu = (topdep)
    elif gp== "Calme" :
        ref_calm = (topdep)
    elif gp=="alar_stop":
        alar_stop = (topdep)
    elif gp=="alar_mes":
        alar_mes = (topdep)   #9
    elif gp=="T_deb_Ala":
        T_deb_Ala = (topdep)
    elif gp=="T_fin_Ala":
        T_fin_Ala = (topdep)
        #print(T_fin_Ala)
    elif gp==12:
        topdepallum = (topdep)
    elif gp=="TopDepSus":
        TopDepSus = (topdep)
    elif gp=="TopFinSus":  
        TopFinSus = (topdep)  #14
    elif gp=="Com_1_Alar":  
        Com_1_Alar = (topdep)
    elif gp=="topdepetin":  
        topdepetin = (topdep)
    elif gp=="top5000":  
        top5000 = (topdep)
    elif gp=="Appel":  
        Appel = (topdep)
    elif gp=="MAppel":  
        MAppel = (topdep)
    elif gp=="RAZ_m_Ala":  
        RAZ_m_Ala =(topdep)
    elif gp=="M_T_garage":  
        M_T_garage =(topdep)    
    elif gp == "Porte_o" :
        Porte_o = (topdep)    
    #print(gp)
    #ouvre(Q_Jour,"Alarme","a")
    #F_Alarme.write( str(gp)+"  "+str(topdep)+'\n' )
     #time.sleep(.51)    
       
def virgule():
    global now
    now = datetime.now()
    Sec_Milion = now.strftime('%S.%f')
    titi = int( (Sec_Milion[3:9]))
    global Million
    Million=titi/1000000

def MesureMil():
    global Mesure_temps
    virgule()
    Mesure_temps = (int (now.strftime('%H') )* 3600) +(int (now.strftime('%M') )* 60)+(int (now.strftime('%S')))+Million
    return Mesure_temps
def get_cpu_temp():     # get CPU temperature and store it into file "/sys/class/thermal/thermal_zone0/temp"
    tmp = open('/sys/class/thermal/thermal_zone0/temp')
    global cpu
    cpu = tmp.read()
    tmp.close()
    return '{:.2f}'.format( float(cpu)/1000 ) + ' C'

def get_time_now():     # get system time
    return datetime.now().strftime('%H:%M:%S')

def loop_affi():
    global Affich_LCD ,  wattp ,  wattc , qu_pluie
    while  Affich_LCD == True and lcdPret == True :
        global qu_pluie,vp
        lcd.lcd_clear()
        lcd.lcd_display_string("CPU: " + str(temp_cpu)+"  "+str(qu_pluie) +" Mm",1)
        lcd.lcd_display_string((get_time_now())+" Eau "+ volts3,2)
        wattp= '    '+wattp
        wattp= wattp[len(wattp)-5:len(wattp)]

        lcd.lcd_display_string("P:"+(wattp)+" Tot "+ str(nb_w_pro),3)
        wattc= '    '+wattc
        wattc= wattc[len(wattc)-5:len(wattc)]

        lcd.lcd_display_string("C:"+(wattc)+" Tot "+ str(nb_w_con),4)
        Affich_LCD = False
def destroy():
    lcd.clear()
    lcd.lcd_clear()
    GPIO.cleanup()
    pin0.value = False
    pin1.value = False
    pin2.value = False

def rebond(toti,LAT) :
    global  oncontinu
    oncontinu = False
    tp1 = GPIO.input(toti)
    time.sleep(LAT)
    tp2 = GPIO.input(toti)
    time.sleep(.02)
    if tp1== tp2 :
        oncontinu = True

def formA(Aformer) :
    global AfA
    AfA=str(Aformer)
    pp = AfA.find('.')
    if pp==-1 :
        AfA_en  = AfA
        AfA_de = ''
    else :
        AfA_en  = AfA[0:pp]
        AfA_de = AfA[pp+1:len(AfA)]
    loAfA_en= len(AfA_en)
    loAfA_de= len(AfA_de)

    if loAfA_en == 3 :
        AfA_en=' '+(AfA_en)
    elif loAfA_en == 2 :
        AfA_en='  '+(AfA_en)
    elif loAfA_en == 1 :
        AfA_en='   '+(AfA_en)
    elif loAfA_en > 3 :
        AfA_en = AfA_en
    if loAfA_de == 1 :
        AfA_de='.'+AfA_de+'00'
    elif loAfA_de == 2 :
        AfA_de='.'+AfA_de+'0'
    elif loAfA_de == 3 :
        AfA_de='.'+AfA_de    
    elif loAfA_de >3:
        AfA_de=AfA[pp:pp+4]
    if Aformer != "temp_cpuN" :    
        AfA=AfA_en+AfA_de
    else :
        Afa=AfA_en
    return AfA
#################### coupe
def annuleMemoireAlarme() :
    global Mradar, Mportes ,Mcoul, Mgarage 
    Mradar=False;Mportes=False;Mcoul=False;Mgarage=False
    
def envoi() :
    try :
        ftp = FTP('ftpperso.free.fr','xxx',tou)
        ftp.cwd('_fields')
        f_name =  nom_ssd+'/relev'+Q_Jour+'.txt'
        f = open(f_name,'rb')
        ftp.storbinary('STOR relev.txt', open(f_name,'rb'))

        f_name =  nom_ssd+'/total'+Q_Jour+'.txt'
        f = open(f_name,'rb')
        ftp.storbinary('STOR total.txt', open(f_name,'rb'))

        f_name =  nom_ssd+'/jour'+Q_Jour+'.txt'
        f = open(f_name,'rb')
        ftp.storbinary('STOR jour.txt', open(f_name,'rb'))

        f_name =  nom_ssd+'/meteo'+Q_Jour+'.txt'
        f = open(f_name,'rb')
        ftp.storbinary('STOR meteo.txt', open(f_name,'rb'))

        f_name =  nom_ssd+'/vent'+Q_Jour+'.txt'
        f = open(f_name,'rb')
        ftp.storbinary('STOR vent.txt', open(f_name,'rb'))
            
        f_name =  nom_ssd+'/pluie'+Q_Jour+'.txt'
        f = open(f_name,'rb')
        ftp.storbinary('STOR pluie.txt', open(f_name,'rb')) 
        ftp.quit()
    except Exception as exception_retournee:
        print("Voici l'erreur :", exception_retournee)
        time.sleep(15)

        try :
            tp = FTP('ftpperso.free.fr','xxx',tou)
        except Exception as exception_retournee:
            print("Voici l'erreur 2:", exception_retournee)
            time.sleep(15)
    else :
        time.sleep(5)
######################### coupe
quant()
Q_Jour=str(Nouv_Jour)
cree_fict(Q_Jour)
Mesure_temps=1
MesureMil()

ref_prod = Mesure_temps
ref_cons = Mesure_temps
ref_vent = Mesure_temps
ref_calm = Mesure_temps
H_ref_pro= Mesure_temps
H_actuel = Mesure_temps
Cons_actu= Mesure_temps
Vent_actu= Mesure_temps
alar_stop= Mesure_temps
TopFinSus= Mesure_temps
TopDepSus= Mesure_temps
topdepetin=Mesure_temps
Mtop5000  =Mesure_temps
top5000   =Mesure_temps
AfA = "toto"
calme    = Mesure_temps
mcalme   = Mesure_temps
ref_dep("Prod")
ref_dep("Cons")
ref_dep("Vent")
#--------------------------
ouvre(Q_Jour,"Ip10","r")
change_IP = Temp_IP.read()
Temp_IP.close()
#--------------------------
jecri()
quant()
##########dht_22()
get_cpu_temp()
temp_cpu=round((int(cpu)/1000),1)
readBME280All()
temperature,pressure,humidity = readBME280All()

maxpro=0;maxproH=0;maxproJ=0;Minuit=False;nbtour=0;moyvolt=0;moycons=0;totvolt=0

vent1=0 ; vent2=0 ; vent3=0 ; vent4=0 ; vent5=0 ; vent6=0 ; vent7=0 ; vent8=0  ; vent9=0 ; vent10=0
#Lvent =[vent1,vent2,vent3,vent4,vent5,vent6,vent7,vent8,vent9,vent10]
#Dvent ={v1:vent1,v2:vent2,v3:vent3,v4:vent4,v5:vent5,v6:vent6,v7:vent7,v8:vent8,v9:vent9,v10:vent10}

ouvre(Q_Jour,"Vent","a") #vent
nb_sec=int(now.strftime('%S'))

#mail('ttoto')

while appui:
        
    time.sleep(.0005)
    nbtour+=1
    if (int(nbtour)%5000 )== 0 or nbtour<2:
        adcnum = 1
        read_adc1 = readadc(adcnum, SPICLK, SPIMOSI, SPIMISO, SPICS)  
        volts1 = read_adc1 * ( 3300.0 / 1024000.0)* 4.9753
        
        adcnum = 2
        read_adc2 = readadc(adcnum, SPICLK, SPIMOSI, SPIMISO, SPICS)
        volts2 = read_adc2 * ( 3300.0 / 1024000.0)* 3.0
        # conversion de la valeur brute lue en milivolts = ADC * ( 3300 / 1024 )
        adcnum = 3
        read_adc3 = readadc(adcnum, SPICLK, SPIMOSI, SPIMISO, SPICS)
        volts3 = read_adc3 * ( 3300.0 / 1024000.0)* 20.0
        if volts3 > 0 :
            value = volts3   # analogRead(0) read A0 pin
            voltage = value / 255.0 * 3.3       #calculate voltage
            Rt = 10 * voltage / (3.3 - voltage)
            #print (value,voltage,Rt)#calculate resistance value of thermistor
            tempK = 1/(1/(273.15 + 25) + math.log(Rt/10)/3950.0) #calculate temperature (Kelvin)
            tempC = tempK -273.15       #calculate temperature (Celsius)
  
        formA(volts3)
        volts3=AfA
         
        #adcnum4 = 4
        #read_adc4 = readadc(adcnum, SPICLK, SPIMOSI, SPIMISO, SPICS)
        #volts4 = read_adc4 * ( 3300.0 / 1024000.0)* 3.0
    
        moyvolt +=1
        totvolt=totvolt+volts2
        moycons= round ((totvolt*1650/moyvolt),2)
        
        
        print("\tTension   : {:.2f}".format(volts1) +'  volts')
        print("\tCons TOR  : {:.2f}".format(moycons)+'  Watts')
        print("\tChauffe   : "+ volts3 +'  °C')
        #print("\tCongel  "+str(volts4))
        #print(tempC)
        #time.sleep(5)
#---------------------------------        
    quant()
#------------------------------
    if Veille_Jour != Nouv_Jour :
        mail('Minuit')
        Minuit= True
        compt_zero()
        ouvre(Q_Jour,3,"w")
        F3_para.write(str(Nouv_Jour))
        F3_para.close()
        Veille_Jour = Nouv_Jour
        CapteurPluie = 0 ;  maxproJ=0;w_prod_total=0;w_cons_total=0;maxpro=0  
        oncontinu = False
        now = datetime.now()
        topbme1  = int (now.strftime('%H') )
        Heure_Nouv = int (now.strftime('%H') )
        Com_1_Alar = 0
    if Heure_Dep != Heure_Nouv :
        ouvre(Q_Jour,3,"w")
        F3_para.write(str(Nouv_Jour)+" Mn  ")
        F3_para.write(str(maxproH)+" Max Heure")
        F3_para.close()
        compt_zero()
        Heure_Dep=Heure_Nouv ; maxproH = 0
        if volts1 < 12.5 :
            mail('Batterie Basse '+str(volts1)+" "+heur)
            
    if topbme1 !=topbme or((int(now.strftime('%M'))%5 )== 0 and int(now.strftime('%S'))==5) :
        F_Alarme.close()
        ouvre(Q_Jour,"Alarme","a")
        topbme   =  topbme1
        readBME280All()
        temperature,pressure,humidity = readBME280All()
        pressure = round(pressure,3)        
        press_mer= round(pressure +(340/8.3),3)
        humidity = round(humidity,2)
        heur     = now.strftime('%Y-%m-%d %H:%M:%S')
        Temp_bmeA= str(temperature)
        ca_caille=False
        if Temp_bmeA[0:1]=='-' :
            ca_caille=True
        pos_point = Temp_bmeA.find('.')
        Temp_bmeA_d = Temp_bmeA[pos_point:len(Temp_bmeA)]
        if ca_caille == False :
            if len(Temp_bmeA_d) == 2 :
                Temp_bmeA = Temp_bmeA + '0'
                print(Temp_bmeA)
                print("------")
            pos_point = Temp_bmeA.find('.')
            Temp_bmeA_d = Temp_bmeA[0:pos_point+1]
            if len(Temp_bmeA_d) == 3 :
                Temp_bmeA='  '+(Temp_bmeA)
            if len(Temp_bmeA_d) == 2 :
                Temp_bmeA='   '+(Temp_bmeA)
        else :
            if len(Temp_bmeA_d) == 2 :
                Temp_bmeA = Temp_bmeA + '0'
            pos_point = Temp_bmeA.find('.')
            Temp_bmeA_d = Temp_bmeA[0:pos_point+1]
            if len(Temp_bmeA_d) == 3 :
                Temp_bmeA='  '+Temp_bmeA
            if len(Temp_bmeA_d) == 4 :
                Temp_bmeA=' '+(Temp_bmeA)
        #pressure = round(pressure,3)
        #press_mer    = round(pressure +(340/8.3),3) 
        formA(pressure)
        pressureN=AfA
        
        formA(press_mer)
        press_mer=AfA
        humidity = round(humidity,2)
        humi_A   = str(humidity)
        pos_point = humi_A.find('.')
        humi_A_d = humi_A[pos_point:len(humi_A)]
        if len(humi_A_d) == 2 :
            humi_A = humi_A + '0'
        heur = now.strftime('%Y-%m-%d %H:%M:%S')
        get_cpu_temp()
        temp_cpu=(int(cpu)/1000)
        temp_cpuN=temp_cpu
        formA(temp_cpuN)
        temp_cpuN=AfA
        
        formA(tem_dh22)
        t22=AfA
        formA(hum_dh22)
        h22=AfA
        
        print(" Meteo: a "+heur+'  '+Temp_bmeA+' C ' + ' cpu: '+str(temp_cpuN)+" Hum "+\
        humi_A +' %  '+str(pressureN)+' hPa ' + str(press_mer))
        print("edf ",EDF_OK," Portail ",PORTAIL_O," Nuit ",J_N  , " Radar->",Mradar," Coul->",Mcoul , " Port->",Mportes, "Gar->",Mgarage)
        ouvre(Q_Jour,4,"a")
        F4_meteo.write(" Meteo: "+heur+'  '+Temp_bmeA+' ' +humi_A+' '+\
        str(pressureN)+' '+ str(press_mer)+ ' cpu: '+str(temp_cpuN)+' eau :'+str(volts3)+'   '+str(tempC)+'\n')
        #F4_meteo.write("edf "+EDF_OK+" Portail "+PORTAIL_O+" Nuit "+J_N+'\n')
        #F4_meteo.write( " Radar->"+Mradar+" Coul->"+Mcoul + " Port->"+Mportes+"Gar->"+Mgarage+'\n')
        F4_meteo.close()
        print ('CPU : '+'{:.1f}'.format( float(cpu)/1000 ))
        if temp_cpu>55:
            print (temp_cpu)
        ouvre(Q_Jour,"Vent","a")
        formA(vent1) ; v1=AfA ; formA(vent2) ; v2=AfA ; formA(vent3) ; v3=AfA ; formA(vent4) ; v4=AfA ; formA(vent5) ; v5=AfA
        formA(vent6) ; v6=AfA ; formA(vent7) ; v7=AfA ; formA(vent8) ; v8=AfA ; formA(vent9) ; v9=AfA ; formA(vent10) ; v10=AfA
                        
        print (v1,' ',v2,' ',v3,' ',v4,' ',v5,' ',v6,' ',v7,' ',v8,' ',v9,' ',v10,' Calme : ',calme)
        F6_vent.write( heur+' '+str(v1)+' '+str(v2)+ ' '+ str(v3)\
        +' '+str(v4)+' '+str(v5)+' '+str(v6)+' '+str(v7)+' '+str(v8)+' '+str(v9)+' '+str(v10)+' '+str(calme)+'\n')
        #for i in Lvent :         
        #    i=0
        vent1=0 ; vent2=0 ; vent3=0 ; vent4=0 ; vent5=0 ; vent6=0 ; vent7=0 ; vent8=0 ; vent9=0 ; vent10=0
            ##########dht_22()
        ouvre(Q_Jour,"Eau9","w")
        
        Temp_Eau.write(str(volts3))
        Temp_Eau.close()
        ouvre(Q_Jour,8,"w")
        Temp_ext.write(Temp_bmeA)
        Temp_ext.close()
        d11_loop()
        #OK le 6-12-20 envoi()
            #print("pas envoi")
            #d11_loop ()
            ##########dht_11()
        print(hum_dh11,tem_dh11,tem_dh22)
        loop_affi()
          #mail()
        print('pas de mail ni envoi')
        Affich_LCD = True
        #annuleMemoireAlarme()
        #Mradar=False;Mportes=False;Mcoul=False;Mgarage=False
        nb_sec=0 #int(now.strftime('%S'))
        time.sleep(.8)
        
    if GPIO.input(G24_PLUI)==0:
        LAT = .05
        rebond(G24_PLUI,LAT)
        if oncontinu == True :
           oncontinu = False
           CapteurPluie += 1
           qu_pluie   = round((CapteurPluie * ValeurPluie),2)
           heur = now.strftime('%Y-%m-%d %H:%M:%S')
           print("Pluie : " + str( qu_pluie) + " Mm" +' '+ heur)
           F1_relev.write("    pluie    : "+heur+' ' +(str(qu_pluie))+'\n')
           ouvre(Q_Jour,7,"a")
           F7_pluie.write("pluie    : "+heur+' ' +(str(qu_pluie))+'\n')
           F7_pluie.close()
           loop_affi()
           Affich_LCD = True

    if GPIO.event_detected(G25_VENT):
        LAT = .005
        rebond(G25_VENT,LAT)
        if oncontinu == True :
            oncontinu = False
            ref_dep("Vent_actu") # donne Vent_actu
            ventN= round(1.8/(Vent_actu-ref_vent),2)
            #vent =str(ventN)
            if ventN>0.99 :
                ref_dep("Calme") #ref_calm
                calme=round(ref_calm-mcalme,2)
                mcalme=round(ref_calm,2)
     
            if ventN<=1 :  vent1+=1
            elif ventN > 1 and ventN <= 2 :  vent2+=1
            elif ventN > 2 and ventN <= 3 :  vent3+=1
            elif ventN > 3 and ventN <= 4 :  vent4+=1
            elif ventN > 4 and ventN <= 5 :  vent5+=1
            elif ventN > 5 and ventN <= 6 :  vent6+=1
            elif ventN > 6 and ventN <= 7 :  vent7+=1
            elif ventN > 7 and ventN <= 8 :  vent8+=1
            elif ventN > 8 and ventN <= 9 :  vent9+=1
            elif ventN > 9 : vent10+=1
           
            #print ('JecrisV->'+str(jecrisV),'  ',v1,' ',v2,' ',v3,' ',v4,' ',v5,' ',v6,' ',v7,' ',v8,' ',v9,' ',v10,' ',calme)
            heur = now.strftime('%Y-%m-%d %H:%M:%S')
            time.sleep(0.0036)
            ref_dep("Vent") # donne ref_vent
            jecrisV += 1
            if (jecrisV > 100):
                print("---vent ercire --")
                F6_vent.close()
                jecriV() # mis a zero dans fonction
            Affich_LCD = True
#---------------------------------------------------------------------
    if GPIO.input(G22_sol)==0:
        Q_soleil=3
#---------------------------------------------------------------------
    #if GPIO.input(G18_PROD)==0:   # 17 Prod
    if   GPIO.event_detected(G18_PROD):
        LAT = .1
        rebond(G18_PROD,LAT)
        if oncontinu == True :
            oncontinu = False
            ref_dep("H_ref_pro") # donne H_ref_pro
            nb_w_pro +=1
            if H_ref_pro - ref_prod != 0 :
                wattpn =round(3600/(H_ref_pro - ref_prod))
                if nbtour<100 :
                    wattpn=0
                #print(H_ref_pro - ref_prod)
                if wattpn < 500 :
                    wattp  =str(wattpn)
                    #print(wattpn)
                    if maxpro < wattpn :
                        maxpro =wattpn
                    maxproN=maxpro
                    if maxproH < wattpn :
                        maxproH=wattpn
                    if maxproJ < wattpn :
                        maxproJ=wattpn
                        
                    formA(wattp)   ; wattp=AfA
                    formA(maxproN) ; maxproN=AfA
                    formA(volts2)  ; voltsR=AfA
                    
                    print(' prod : '+ wattp+"  Cons Instant->"+str(moyconsN)+"  Max "+str(maxpro) + " H: "+ str(maxproH ) +" J: "+ str(maxproJ))   
                    heur = now.strftime('%Y-%m-%d %H:%M:%S')
                    ouvre(Q_Jour,"relev1","a")
                
                    F1_relev.write(" watt produ : "+heur+'         ' +(wattp)+' '+str(voltsR)+'  '+"Max "+str(maxproN)+\
                    " MaxH "+str(maxproH)+" MaxJ "+str(maxproJ)+'\n')
                    time.sleep(0.003)
                    ref_dep("Prod")
                    loop_affi()
                    jecris += 1
                    if (jecris > 200):
                        print("---prod ecrire --")
                        F1_relev.close()
                        jecri()
                else :
                    print ("plus de 500 !")
                Affich_LCD = True
 #-----------------------------------------------------------------
    #if GPIO.input(G23_CONS)==0 :    # 23 Cons
    if   GPIO.event_detected(G23_CONS):
        LAT = .005
        rebond(G23_CONS,LAT)
        if oncontinu == True :
            oncontinu = False
            ref_dep("Cons_actu")
            nb_w_con +=1
            nb_w_conN=nb_w_con
            wattcn=round(3600/(Cons_actu - ref_cons))
            if wattcn < 9000 :
                volts2 = read_adc2 * ( 3300.0 / 1024000.0)* 3.0
                wattc =str(wattcn)
                formA(wattc)     ; wattc=AfA
                formA(nb_w_conN) ; nb_w_conN=AfA
                formA(moycons)   ; moyconsN =AfA
                #print(" Cons : " + wattc +"  "+str(moyconsN) +' '+str(nb_w_conN)+'  Tour: '+str(nbtour))
                heur = now.strftime('%Y-%m-%d %H:%M:%S')
                ouvre(Q_Jour,"relev1","a")
                F1_relev.write(" watt conso : "+heur+' ' + wattc + " " +str(moyconsN)+' '+str(nb_w_conN)+'\n')
                time.sleep(0.0036)
                moyvolt=0;moycons=0;totvolt=0
                ref_dep("Cons")
                loop_affi()
                jecris +=1
                if (jecris >200):
                    print("---cons  ecrire --")
                    F1_relev.close()
                    jecri()
            else :
                    print ("plus de 9000 Watts Cons  Attention SLEEP")
                    time.sleep(2)
            Affich_LCD = True
#### Surveillance
            
    
#envoi GND->pin8=False
    if (int(nbtour)%5000 )== 0 or nbtour<2:
        ref_dep("top5000")
        
        nbTenS=top5000-Mtop5000
        formA(nbTenS)
        nbTenS=AfA
        nbTenST=(top5000-Mtop5000)/5000
        formA(nbTenST)
        nbTenST=AfA
        print("-----------------")
        print ("5000 en "+nbTenS+" seconds Soit un tour en "+nbTenST)
        print("-----------------")
        TOPA=T_deb_Ala-Com_1_Alar
        formA(TOPA)
        TOPA=AfA
        print("PO ",Mportes,"  Co ",Mcoul,"   Ra ",Mradar,"    Ga ",Mgarage,  "  Sir ",m_alarmeG," A:",str(Alar_S4), " PortO ",str(H_actuel - Porte_o))
        print( heur +" Boucle e_o "+str(Alar_S4)+" Compt Porte->"+str(Compt_A_Por)+"   Autre->"+str(Compt_Autre)+"   "+ TOPA )
        Mtop5000=top5000
            
    if pin8.value==False and EDF_OK == False :
        print("EDF OK")
        ouvre(Q_Jour,"Alarme","a")
        F_Alarme.write( heur+"  EDF OK "+"\n")
        #F_Alarme.close()
        EDF_OK=True    
            
    if pin8.value==True and EDF_OK == True :
        ouvre(Q_Jour,"Alarme","a")
        F_Alarme.write( heur+"  EDF KO "+"\n")
        #F_Alarme.close()
        print("EDF KO")
        EDF_OK=False
   
    if pin11.value==True and PORTAIL_O==False:
        print("Fermé")
        ouvre(Q_Jour,"Alarme","a")
        F_Alarme.write( heur+"  Portail Fermé"+"\n")
        PORTAIL_O=True
        #F_Alarme.close()     
    if pin11.value==False and PORTAIL_O==True:
        print("Ouvert")
        ouvre(Q_Jour,"Alarme","a")
        F_Alarme.write( heur+"   Portail Ouvert"+"\n")
        PORTAIL_O=False
        #F_Alarme.close()
        #time.sleep(5)
    if pin12.value==True and J_N=="Jour":  # Contact ouvert
        print("Jour")
        ouvre(Q_Jour,"Alarme","a")
        F_Alarme.write( heur+"  J_N en Jour"+"\n")
        J_N="Nuit"
        time.sleep(.0005)     
        #F_Alarme.close()    
    if pin12.value==False and J_N=="Nuit":
        print("Nuit")
        ouvre(Q_Jour,"Alarme","a")
        F_Alarme.write( heur+" ---- J_N en nuit"+"\n")
        J_N="Jour"
        time.sleep(.0005)     
        
    ref_dep("H_actuel")    
        
    if GPIO.input(G5_SUSP)== 0 and alar_susp == False :
        LAT = .01
        rebond(G5_SUSP,LAT)
        if oncontinu == True :
            oncontinu = False
            ref_dep("TopDepSus")
            alar_susp = True
            TopFinSus=TopDepSus
            pin7.value = True ; pin6.value = False
            print('Alarme stand-by')
            GPIO.output(G19_SIR,GPIO.LOW)
            m_alarmeG=False
            ouvre(Q_Jour,"Alarme","a")
            F_Alarme.write( heur +"      Suspendue G5"+"\n")        
            #time.sleep(10)

    if TopFinSus > TopDepSus + T_Susp and alar_susp == True: #
        alar_susp = False 
        TopFinSus = TopDepSus
        heur = now.strftime('%Y-%m-%d %H:%M:%S')
        print("Fin SUSPENDUE "+' :'+ heur)
        ouvre(Q_Jour,"Alarme","a")
        F_Alarme.write( heur +" FIN Suspendue "+"\n")        
        F_Alarme.close()
        pin7.value = False  ; pin6.value = True
    else :
        ref_dep("TopFinSus")            
       
    if alar_susp == False :
        '''   G26_ALA  :   Radar COULOIR '''
        if GPIO.input(G26_ALA) == 0 and Compt_Autre >  5 :
            Compt_Autre  = 0
        '''  ----------------------    '''   
        if GPIO.input(G13_MESA)== 1 :
            alar_pret = False ; alar_oper = False
            ref_dep("alar_stop")
            mis_ala=False
            GPIO.output(G19_SIR,GPIO.LOW)
            m_alarmeG=False
            pin7.value = True ; pin6.value = False   # 7=led Verte
        else :
            pin7.value = False #  ;  pin6.value = True
            
        if GPIO.input(G13_MESA)== 0 and mis_ala==False : #
            ref_dep("alar_mes")
            
            if alar_mes > alar_stop + 10 : # temps pour fermer porte apres mise en service
                alar_oper = True
                #--------------------------------------
                mis_ala = True
                if mis_ala== True : #Evidement !!!!
                #-----------------------
                    print("Alarme oper")
                    pin6.value = True
                    ouvre(Q_Jour,"Alarme","a")
                    F_Alarme.write( heur +" Oper 19_11"+"\n")        
                    F_Alarme.close()
                    #mis_ala=False
                    alar_mes=alar_stop
                   
        if pin9.value == False and Porte_O == False:
            Porte_O = True
            ref_dep("Porte_o")
        if pin9.value == False :
            porte=1000
        else :
            Porte_O = False
        if pin9.value == False and H_actuel > Porte_o + 150 :
            porte=2000 #AbandonP=True
        if GPIO.input(G26_ALA) == 0 :
            couloir=1
        if  pin10.value == False :
            Radar=10
        if  pin13.value == False :
            garage=100
        Alar_S4 = couloir + Radar + garage + porte
        MAlar_S4 = Alar_S4
        if ((Alar_S4 > 0 and Alar_S4 < 1500) or Alar_S4 > 2000 )\
            and alarme == False  and alar_oper == True and ((Compt_A_Por < 5 and Porte_O ==True) or Compt_Autre < 5) :
            
        #if (GPIO.input(G26_ALA)== 0 or pin9.value==False or pin10.value==False or pin13.value==False )\
            '''#LAT = .1
            #rebond(G26_ALA,LAT)'''
            oncontinu=True
            '''#  a Revoir  car que couloir !!!!! '''
            if oncontinu == True :
                oncontinu = False
                alarme = True
                ''' 1 10 100 101 110 111 1000 1001 1010 1011 1100 1101 1110 1111 2000'''
                if pin9.value==False and Alar_S4 > 999 and Alar_S4 < 1999  :
                    Compt_A_Por += 1
                #if pin9.value==False and (Alar_S4 < 1500 or Alar_S4 > 2000) :
                    '''# Portes temps pour entrer et couper sirene'''
                    time.sleep(10)
                time.sleep(.2) # Radar et Couloir 
                if GPIO.input(G13_MESA)== 1 :
                    alar_pret = False ; alar_oper = False
                    ref_dep("alar_stop")
                else :
                    if int (now.strftime('%H') )< 17 or int (now.strftime('%H') ) > 16 :
                        GPIO.output(G19_SIR,GPIO.HIGH)
                        m_alarmeG=True
                ouvre(Q_Jour,"Alarme","a")
                F_Alarme.write( heur+" " +str(Alar_S4)+"\n")
                if pin13.value==False : #and Mgarage == False:                          
                    F_Alarme.write( heur+" " +str(Compt_A_Por)+" Garage"+"\n")
                    quiAlarme=" Garage"
                    Mgarage=True
                    Compt_Autre+=1
                if pin10.value==False :     
                    F_Alarme.write( heur+" " +str(Compt_A_Por)+" Radar"+"\n")
                    quiAlarme=" Radar"
                    Mradar=True
                    Compt_Autre+=1
                if pin9.value==False and Alar_S4 < 2000 :                        
                    F_Alarme.write( heur+" " +str(Compt_A_Por)+" Portes"+"\n")
                    quiAlarme=" Porte"
                    Mportes=True
                if GPIO.input(G26_ALA)== 0 :
                    F_Alarme.write( heur+" " +str(Compt_A_Por)+" Couloir"+"\n")
                    quiAlarme=" Coul"
                    MCoul=True
                    Compt_Autre+=1
                ref_dep("T_deb_Ala")
                temps_alar = T_deb_Ala
                heur = now.strftime('%Y-%m-%d %H:%M:%S')
                print("Alarme   : " + heur +' '+quiAlarme+" "   +str(Alar_S4)+" P->"+str(Compt_A_Por)+"   A->"+str(Compt_Autre))
                if Compt_Autre == 5 :
                    Compt_Autre += 1
                
                if Compt_A_Por == 5 :
                    Compt_A_Por += 1
                time.sleep(0.01)
        couloir = 0 ; Radar = 0 ; garage = 0   ;  porte = 0
        if alarme == True :
            ref_dep("T_fin_Ala")
            #T_fin_Ala
            if T_fin_Ala > temps_alar + T_Sirene : # sirene gueule 45 s 5x si porte reste ouverte
                T_fin_Ala = T_deb_Ala
                GPIO.output(G19_SIR,GPIO.LOW)
                m_alarmeG=False
                alarme = False
                heur = now.strftime('%Y-%m-%d %H:%M:%S')
                print("Fin Alarme "+ heur+" "+quiAlarme+" "+str(Alar_S4)+" P->"+str(Compt_A_Por)+"   A->"+str(Compt_Autre))
                ouvre(Q_Jour,"Alarme","a")
                F_Alarme.write( heur +"           FIN Alarme "+ quiAlarme +"\n")        
                F_Alarme.close()
                Alar_S4=0
            #else :
                # print('Alarme suspendue')
             
    #---------------------------------------------------------------------
    #if GPIO.event_detected(G21_BOUTO) and allume == False :
    if GPIO.input(G21_BOUTO)== 0 and allume == False :
        LAT = .051
        rebond(G21_BOUTO,LAT)
        if oncontinu == True :
            oncontinu = False
            allume = True
            GPIO.output(G27_ECLA,GPIO.HIGH)
            ref_dep(12)
            temps_allume = topdepallum
            #ref_dep(gp)
            heur = now.strftime('%Y-%m-%d %H:%M:%S')
            print("Allume : " +' '+ heur)
            ouvre(Q_Jour,"Alarme","a")
            F_Alarme.write( heur +" Allumage exterieur "+"\n")        
            #F_Alarme.close()
            #GPIO.setup(G21_BOUTO,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            time.sleep(0.51)
    #print (allume)
    #if GPIO.event_detected(G21_BOUTO) and allume == True :
    if GPIO.input(G21_BOUTO)== 0 and allume == True :
        LAT = .05
        rebond(G21_BOUTO,LAT)
        time.sleep(.5)
        if oncontinu == True :
            oncontinu = False
            allume = False
            GPIO.output(G27_ECLA,GPIO.LOW)

            heur = now.strftime('%Y-%m-%d %H:%M:%S')
            ouvre(Q_Jour,"Alarme","a")
            F_Alarme.write( heur +" Extinction "+"\n")        
            #F_Alarme.close()
            print("Extinction : " +' '+ heur)
            #GPIO.setup(G21_BOUTO,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    if allume == True :
        ref_dep("topdepetin")
        if topdepetin > temps_allume + 133 :
            topdepetin = topdepallum
            GPIO.output(G27_ECLA,GPIO.LOW)
            allume = False
            heur = now.strftime('%Y-%m-%d %H:%M:%S')
            print("Extinction Tempo: " +' '+ heur)
            ouvre(Q_Jour,"Alarme","a")
            F_Alarme.write( heur +"    Extinction auto exterieur "+"\n")        
            #F_Alarme.close()
 
    
   
 
        
#-----------------------------------------------------------------
if __name__ == '__main__':
    print ('c est parti mon kiki ... ')
    time.sleep(5)
    try:
        loop_affi()
    except KeyboardInterrupt:
        destroy()
