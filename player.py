import requests
from enum import Enum

URL = "https://europe.api.riotgames.com/"
API_KEY = "RGAPI-c8339727-14f9-4ab4-815a-ea966abf14a6"

NB_ROWS = 100
NB_COLS = 20

class Role(Enum):
    SUPPORT = "Support"
    TOP = "Top"
    MID = "Mid"
    JUNGLE = "Jungle"
    ADC = "Adc"

class Roaster(Enum):
    VALHALLA = "Valhalla"
    HELHEIM = "Helheim"

class Player :
    def __init__(self,name:str,tag:str,role:Role,roster:Roaster) -> None:
        # init values
        self.name = name
        self.tag = tag
        self.roster = roster
        self.role = role

        # lateinit values
        self.ws = None
        self.puuid = None
    
    def createWS(self,sheet):

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
        matchsAlreadyDone = self.ws.col_values(7)

        url = URL+"lol/match/v5/matches/by-puuid/"+self.puuid+"/ids"
        
        req = url+"?start=0&count=20&api_key="+API_KEY

        response = requests.get(req)

        if response.ok:
                result = response.json()
                return filter((lambda x : (x not in matchsAlreadyDone)), result)
        else:
            raise BaseException("Exception : getMatchIds => La requête n'a pas fonctionnée")
        
    def update(self) :
        try:
            matchIds = self.getLastMatchsIds()
            

            nb_games=0
            for match_id in matchIds :
                pass
        except BaseException as e:
            print(str(e))




        

