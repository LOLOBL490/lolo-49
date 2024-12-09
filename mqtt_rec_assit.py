import paho.mqtt.client as mqtt
import time
import os
from datetime import datetime
datetime.now()
now  = datetime.now()
heur = now.strftime('%Y-%m-%d %H:%M:%S')

#nom_ssd = '/media/pi/'   +'1c0d1c50-8371-4e0a-b02c-fdc5f2639440'
nom_ssd = '/mnt/ssd120'
import Q
#nom_ssd = '/media/pi/'   +'Volume de 97 Go'
F_assit= ' '  ; F_inj=' ';tep=' '
Q_Jour='000';Veille_Jour = ''
GD="    Grenier Derriere ---"
LV=" ----------- Livebox ---"
CB="   --------- Cabanon ---"
CE="   ------Chauffe Eau ---"
EX=" --------- Exterieur ---"
GV="    - Grenier Devant ---"
#print(len(GD),' ',len(LV),' ',len(CB),'  ',len(CE),'  ',len(EX),'  ',len(GV))

MQTT_ADDRESS = '192.168.1.104' # c'est adresse du RasPI
MQTT_USER = 'cdavid' 
MQTT_PASSWORD = 'cdavid' 
#MQTT_TOPIC = 'home/livingroom/temperature'
MQTT_TOPIC = 'homeassistant/homeassistant_state'
#MQTT_TOPIC = 'home/livingroom/humidity'
def quant():
    now  = datetime.now()
    heur = now.strftime('%Y-%m-%d %H:%M:%S')
    dd = int(now.strftime('%d'))
    dm = int(now.strftime('%m'))
    da = int(now.strftime('%Y'))
    dj=[dd,dm,da]
    global Nouv_Jour,Q_Jour  
    Nouv_Jour = Q.numjouran(dj)
    
    Q_Jour = "00"+str(Nouv_Jour)        
    Q_Jour =str(da%2000)+ Q_Jour[len(Q_Jour)-3:len(Q_Jour)]
   
rc=999 # code retour    
quoi=' ' ; mlieu='yyy'
quant()
F_inj = open( nom_ssd+'/'+Q_Jour+'inj_h.txt','w')


if os.path.isfile( nom_ssd+'/'+Q_Jour+'assit.txt') == False:
    F_assit = open( nom_ssd+'/'+Q_Jour+'assit.txt','w')    
    F_assit.close()
    
def  inj():
    global F_inj
    if os.path.isfile( nom_ssd+'/'+Q_Jour+'inj_h.txt') == False:
        F_assit = open( nom_ssd+'/'+Q_Jour+'inj_h.txt','w')
        
    F_inj = open( nom_ssd+'/'+Q_Jour+'inj_h.txt','r')
    file_lines = F_inj.readlines ()
    if len(file_lines)>5:
        if int(now.strftime('%H')) == 23 and int(now.strftime('%M'))> 50:
             F_inj = open( nom_ssd+'/'+Q_Jour+'inj_h.txt','w')
    F_inj = open( nom_ssd+'/'+Q_Jour+'inj_h.txt','a')
    #F_inj.write(" ---C'est parti--"+'\n')
    #F_inj.close()    


def  on_connect (client, userdata, flags, rc) : 
    """ Le rappel lorsque le client reçoit une réponse CONNACK du serveur.""" 
    print( 'Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def  on_message (client, userdata, msg) : 
    """Le rappel lorsqu'un message PUBLIER est reçu du serveur."""
    #print(client,'    '   ,userdata,  '     ', msg)
    #print('Message recu ' + msg.topic + ' ' + str(msg.payload))
    #home/tot/tot easj b'8815.39'
    tep=str(msg.payload)[2:7]
    quoi=str(msg.topic)[9:10]
    injec=str(msg.topic)[13:157]
    #print('injection essai du 1-08-24 ',injec)
    lieu=str(msg.topic)[5:8]
    global mlieu
    now  = datetime.now()
    heur = now.strftime('%Y-%m-%d %H:%M:%S')
    quant()
    F_assit = open( nom_ssd+'/'+Q_Jour+'assit.txt','a')
   
    '''
    dico={"PuissanceS_M": 0, "PuissanceI_M": 25, "Tension_M": 245.6, "Intensite_M": 0.4, "PowerFactor_M": -0.30,/
          "Energie_M_Soutiree":0,"Energie_M_Injectee":4, "EnergieJour_M_Soutiree":0,/
          "EnergieJour_M_Injectee":3,"Temperature": 29.4}
'''
    dico= " "+str(msg.payload)[3:]

    dico1=dico.split(',')
    print(heur)
    titi= dico1[0].replace("PuissanceS_M","Psou")+','+'\t'
    tutu=dico1[9]
    D_tutu=tutu.find(':')+1
    L_tutu=len(tutu)
    toto=tutu[D_tutu:L_tutu]
    toto=toto.replace(' ','')
    
    titi= titi+dico1[1].replace("PuissanceI_M","Pinj")+','+'\t'
    titi= titi+dico1[2].replace("Tension_M","Volt")+','+'\t'
    titi=titi+dico1[3].replace ("Intensite_M","Inte")+','+'\t'
    titi=titi+dico1[4].replace("PowerFactor_M","PowF")+','+'\t'
    titi= titi+dico1[5].replace("Energie_M_Soutiree","Cons")+','+'\t'
    titi=titi+dico1[6].replace("Energie_M_Injectee"," Inje")+','+'\t'
    titi=titi+dico1[7].replace("EnergieJour_M_Soutiree","So-j")+','+'\t'
    titi=titi+dico1[8].replace("EnergieJour_M_Injectee","In-j")+','+'\t'
    titi=titi+dico1[9].replace("Temperature"," T°--")+','+'\t'
    titi=titi+dico1[10].replace("Ouverture_Triac"," %Tri-")+','+'\t'
    titi=titi+dico1[12].replace("Duree_Triac"," Htri")
    
    F_assit.write(heur+" --------------------------------"+'\n')
    F_assit.write(heur+" "+titi+'\n')
    '''
    titi= dico1[0].replace("PuissanceS_M",'$')
    titi= titi+dico1[1].replace("PuissanceI_M",'$')
    titi= titi+dico1[2].replace("Tension_M",'$')
    titi=titi+dico1[3].replace ("Intensite_M",'$')
    titi=titi+dico1[4].replace("PowerFactor_M",'$')
    titi= titi+dico1[5].replace("Energie_M_Soutiree",'$')
    titi=titi+dico1[6].replace("Energie_M_Injectee",'$')
    titi=titi+dico1[7].replace("EnergieJour_M_Soutiree",'$')
    titi=titi+dico1[8].replace("EnergieJour_M_Injectee",'$')
    titi=titi+dico1[9].replace("Temperature",'$')
    titi=titi+dico1[10].replace("Ouverture_Triac",'$')
    titi=titi+dico1[12].replace("Duree_Triac",'$')
    '''
    F_tutu=open('/mnt/ssd120/fichier/t_ext2.txt','r+')
    F_tutu.truncate()
    F_tutu.write(titi+'\n')
    F_tutu.close()
    #Ouverture_Triac":0,"Actif_Triac":0,"Duree_Triac":1.705452}'

    print(titi)
    
    #F_assit.write(heur+" "+lieu+"-"+quoi+' '+tep+' Recu inj: '+injec+'\n')
    #F_assit.write(heur+" "+str(msg.payload)+'\n')
    F_assit.close()
def  main() :
    quant()
    inj()
    global Veille_Jour
    if Veille_Jour != Nouv_Jour :        
        Veille_Jour = Nouv_Jour
        if os.path.isfile( nom_ssd+'/'+Q_Jour+'assit.txt') == False:
            F_assit = open( nom_ssd+'/'+Q_Jour+'assit.txt','w')
            
             
    mqtt_client = mqtt.Client()
        
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    print(mqtt_client)
    mqtt_client.on_message = on_message
    
    '''def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK")
    else:
        print("Bad connection Returned code=",rc)'''
    
    
    mqtt_client.connect(MQTT_ADDRESS, 1883 )   #1883 c'est le port
    #mqtt_client.connect(MQTT_ADDRESS, 1884 )
    
    mqtt_client.loop_forever()

    
                 
if __name__ == '__main__' :
    print( 'Modif du 30/10/2023  Pont MQTT vers InfluxDB' )
    main()
