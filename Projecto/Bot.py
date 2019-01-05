# coding=utf-8
import requests
import json
import os,sys
import time
import datetime as dt
from time import sleep
import random

class Bot:


    exist=0
    while exist== 0:
        b_name=raw_input("Introduza o nome do Edificio:")
        #dono_ID=raw_input("Introduza o ID do dono do Bot:")
        #hash = random.getrandbits(128)
        ip = '127.0.0.1'
        port = '5000'
        req1 = requests.get('http://'+ ip +':'+ port +'/Bot/PendingBots')
        #print(req1.content)
        aux=req1.content
        if(1):
    	       for x in range(1):
                    Botkey=random.randint(1,101)
                    while str(Botkey) in aux:
                        Botkey=random.randint(1,101)
        headers={"Content-Type":"application/json;charset=UTF-8"}
        key={
        'Botkey' : Botkey,
        'Build_name' : b_name,
        }
        req2 = requests.post('http://'+ ip +':'+ port +'/Bot/registry',json=key, headers=headers)
        resposta=json.loads(req2.text)
        print("O servidor respondeu:")
        print(resposta)
        if resposta == "O Edificio escolhido existe":
            exist=1
    ##### Até o Admin fizer Load na pagina dele dos bots por registar
    card={
    'Botkey' : Botkey,
    'Build_name' : b_name,
    }
    switch = 0
    print("Esperando por Inserção no Sistema. Aguarde...")
    while switch==0:
        req3 = requests.get('http://'+ ip +':'+ port +'/Bot/AcceptBot')
        response=req3.text
        if str(Botkey) in response:
            print(response)
            print("Estou la dentro")
            switch=1
            response2= json.loads(response)
            b_id=response2[str(Botkey)]['Build_ID']
            break
        sleep(15)

    #Help
    print("Bind concluído!")
    print("O identificador do Bot é:")
    print(Botkey)
    msg = raw_input("Introduza a mensagem periodica:")
    print("A sua mensagem foi:",msg)
    msgjson = {
        'BotID' : Botkey,
        'build_id' : b_id,
        'user_loc' : b_name,
        'message' : msg,
    }
    #print(msgjson)

    while 1:
        print(msgjson)
        req = requests.post('http://'+ ip +':'+ port +'/Bot/message',json=msgjson, headers=headers)
        sleep(30)
    #print("HTTP Status Code: " + str(req.status_code))
    #print(req.headers)
    #json_response = json.loads(req.content)
    #print("Pokemon Name: " + json_response['name'])
