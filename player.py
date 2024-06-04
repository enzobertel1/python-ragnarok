import requests
from enum import Enum
import time

URL = "https://europe.api.riotgames.com/"
API_KEY = "RGAPI-c8339727-14f9-4ab4-815a-ea966abf14a6"

NB_ROWS = 100
NB_COLS = 20

CELL_VALUES = {
                "minionsPerMinutes": "6",
                "killParticipation": "7",
                "damagePerMinute":"8",
                "damageObjectives":"9",
                "deathsPerMinute":"10",
                "kda":"11",
                "vision":"12"
            }

class Role(Enum):
    SUPPORT = "Support"
    TOP = "Top"
    MID = "Mid"
    JUNGLE = "Jungle"
    ADC = "Adc"

class Roaster(Enum):
    VALHALLA = "Valhalla"
    HELHEIM = "Helheim"

def getMatchInfo(match_id,puuid):
    url = URL+"lol/match/v5/matches/"+match_id
    response = requests.get(url+"?api_key="+API_KEY)
    if response.ok:
        res = response.json()
        

        if res["info"]["gameMode"] == "CLASSIC" and res["info"]["gameType"] == "MATCHED_GAME":

            indexPlayer = res["metadata"]["participants"].index(puuid)
            durationInMinutes = res["info"]["gameDuration"]/60

            player = res["info"]["participants"][indexPlayer]
            return {
                "minionsPerMinutes": player["totalMinionsKilled"] / (durationInMinutes),
                "killParticipation": (player["assists"] +player["kills"]) / sum([k["kills"]  for k in res["info"]["participants"] if k["teamId"] == player["teamId"]]),
                "damagePerMinute":player["totalDamageDealtToChampions"]/durationInMinutes,
                "damageObjectives":player["damageDealtToObjectives"],
                "deathsPerMinute":player["deaths"]/durationInMinutes,
                "kda":(player["assists"] +player["kills"])/ player["deaths"] if player["deaths"]!=0 else 1,
                "vision":player["visionScore"]
            }
        else:
            raise BaseException("La partie n\'est pas en mode normal")
        
def replaceMeanInWs(ws,place:str,value:float,nbGames:int):
    old = float(ws.acell(place).value.replace(",","."))
    new = ((old*(nbGames-1)) + value) /nbGames
    ws.update_acell(place,new)

def fill_ws(p):

    ws=p.ws
    ws.update_acell("A1","Pseudo:")
    ws.update_acell("B1",p.name)
    ws.update_acell("C1","Tag:")
    ws.update_acell("D1",p.tag)
    ws.update_acell("E1","PUUID:")
    ws.update_acell("F1",p.puuid)
    ws.update_acell("A2","Role:")
    ws.update_acell("B2",p.role.value)
    ws.update_acell("C2","Equipe:")
    ws.update_acell("D2",p.roster.value)
    

    ws.update_acell("A3","RANG")

    ws.update_acell("A5","Solo Queue Classée")
    ws.update_acell("B5","Moyenne Globale")
    ws.update_acell("C5","Moyenne dernieres games")
    ws.update_acell("D5","Game comptées")
    ws.update_acell("D6",0)

    for k,v in CELL_VALUES.items():
        ws.update_acell("A"+v,k)

    ws.update("B6:C12",[[0,0]for i in range(6,13)])
    

    ws.format("A3",{
        "backgroundColor": {
            "red": 76/255,
            "green":204/255,
            "blue": 127/255
        },
    })  
   

    ws.format("A5:D5",{
        "backgroundColor": {
            "red": 255/255,
            "green":109/255,
            "blue": 1/255
        },
        "horizontalAlignment": "CENTER",
        "textFormat": {
            "foregroundColor": {
                "red": 1.0,
                "green": 1.0,
                "blue": 1.0
            },
            "fontSize": 12,
            "bold": True
    }
    })   

    ws.format("A6:D12",{
        "backgroundColor": {
            "red": 255/255,
            "green":229/255,
            "blue": 153/255
        },
        "horizontalAlignment": "CENTER",
    })  

class Player :
    def __init__(self,name:str,tag:str,role:Role,roster:Roaster,puuid=None,ws=None,) -> None:
        # init values
        self.name = name
        self.tag = tag
        self.roster = roster
        self.role = role

        # lateinit values
        self.ws = ws
        self.puuid = puuid
    
    def createWS(self,sheet):
        self.getPUUID()
        ws = None
        try:
            ws = sheet.worksheet(self.roster.value+"_"+self.role.value)
        except BaseException as e:
            ws = None

        if ws != None:
            rep = input("Un joueur a déjà ce rôle. Voulez vous le remplacer ? (y/N)")

            if rep == "y" or rep == "Y":
                sheet.del_worksheet(ws)

                ws = sheet.add_worksheet(title=self.roster.value+"_"+self.role.value,rows=NB_ROWS,cols=NB_COLS)
        else:
            ws = sheet.add_worksheet(title=self.roster.value+"_"+self.role.value,rows=NB_ROWS,cols=NB_COLS)
            
        self.ws = ws

        fill_ws(self)

        print(self.ws.col_values(7))

        return ws
    
    

        

    def havePuuid (self):
        return self.puuid != None


    def getPUUID(self):
        '''
        Récupère le puuid du joueur (ID unique du joueur)
        '''

        if self.puuid !=None :
            return self.puuid
        if self.ws != None :
            self.puuid = self.ws.acell("F1").value
            return self.puuid
        
        response = requests.get(URL+"riot/account/v1/accounts/by-riot-id/"+self.name+"/"+self.tag+"?api_key="+API_KEY)
        if response.ok:
            self.puuid = response.json()["puuid"]
            
        return self.puuid
    
    def getLastMatchsIds(self):
        '''
        Récupère les ids des 20 derniers matchs du joueur (ID unique du joueur)
        '''
        if not self.havePuuid():
            raise BaseException("Exception : getMatchIds => Le joueur n'a pas de PUUID")
        
        #Regardez le tableau d'ids dans la colonne G
        
        matchsAlreadyDone = []

        for i in range(1,21):
            if (self.ws.acell("G"+str(i)).value == None):
                matchsAlreadyDone.append(self.ws.acell("G"+str(i)).value)

        url = URL+"lol/match/v5/matches/by-puuid/"+self.puuid+"/ids"
        
        req = url+"?start=0&count=20&api_key="+API_KEY

        response = requests.get(req)

        if response.ok:
                result = response.json()
                return list(filter((lambda x : (x not in matchsAlreadyDone)), result))
        else:
            raise BaseException("Exception : getMatchIds => La requête n'a pas fonctionnée")
        
    def update(self) :
        try:
            matchIds = self.getLastMatchsIds()
            
            if len(matchIds)> 0:
                self.ws.update([[0] for _ in range(6,13)],"C6:C12")

            nb_games=0
            for match_id in matchIds :
                try:
                    
                    match = getMatchInfo(match_id,self.puuid)

                    #Incrémente le nombre de games jouées
                    game_played = float(self.ws.acell("D6").value.replace(",","."))+1
                    self.ws.update_acell("D6",game_played)
                    nb_games+=1

                    fill = False
                    for i in range(1,21):
                        if (self.ws.acell("G"+str(i)).value == None):
                            self.ws.update_acell("G"+str(i),match_id)
                            fill = True
                            break

                    if not fill:
                        for i in range(1,21):
                            self.ws.update_acell("G"+str(i),self.ws.acell("G"+str(i+1)).value)

                        self.ws.update_acell("G20",match_id)

                    print("Partie : ",match_id)
                                

                    for k,v in CELL_VALUES.items():
                        replaceMeanInWs(self.ws,"B"+v,match[k],game_played)
                        replaceMeanInWs(self.ws,"C"+v,match[k],nb_games)


                    time.sleep(60)

                except BaseException as e:
                    print(str(e))
        except BaseException as e:
            print(str(e))




        

