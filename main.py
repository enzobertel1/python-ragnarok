import gspread
from google.oauth2.service_account import Credentials
import requests
import datetime
import time
from player import Player,Role,Roaster

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

URL = "https://europe.api.riotgames.com/"

MATCH = "/lol/match/v5/matches/by-puuid/{puuid}/ids"
API_KEY = "RGAPI-c8339727-14f9-4ab4-815a-ea966abf14a6"

SHEET_ID = "1MtUAVv3p2X0syIAfP4Kt62L16Gdder6X66aAjpzKR8M"


creds = Credentials.from_service_account_file("credentials.json",scopes=scopes)
client = gspread.authorize(creds)

SHEET = client.open_by_key(SHEET_ID)

def createNewPlayer(pseudo,tag,role,roster):
    
    p = Player(pseudo,tag,role,roster)
    p.createWS(SHEET)


    
    
    
        
# Créé et formate un joueur dans l'excel de la façon par défaut
def joueur(ws,player:Player):
    ws.update_acell("A1","Pseudo:")
    ws.update_acell("B1",player.name)
    ws.update_acell("C1","Tag:")
    ws.update_acell("D1",player.tag)
    ws.update_acell("E1","PUUID:")
    ws.update_acell("F1",player.puuid)
    ws.update_acell("A2","Role:")
    ws.update_acell("B2",player.role.value)
    ws.update_acell("C2","Equipe:")
    ws.update_acell("D2",player.roster.value)
    

    ws.update_acell("A3","RANG")

    ws.update_acell("A5","Solo Queue Classée")
    ws.update_acell("B5","Moyenne Globale")
    ws.update_acell("C5","Moyenne dernieres games")
    ws.update_acell("D5","Game comptées")
    ws.update_acell("D6",0)

    ws.update_acell("A6","CS/minutes")
    ws.update_acell("A7","Kill participation")
    ws.update_acell("A8","Damage")
    ws.update_acell("A9","Damage Objectif")
    ws.update_acell("A10","Morts / Minutes")
    ws.update_acell("A11","KDA")
    ws.update_acell("A12","Vision Score")

    ws.update("B6:C12",[[0,0]for i in range(6,13)])
    

    ws.format("A3",{
        "backgroundColor": {
            "red": 76/255,
            "green":204/255,
            "blue": 127/255
        },
    })  
    ws.format("B3:C3",{
        "backgroundColor": {
            "red": 183/255,
            "green":225/255,
            "blue": 205/255
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

#Mise à jour des stats de chaque joueur dans l'excel
def update_players():
    wsts = SHEET.worksheets()
    today = datetime.datetime.today().timestamp()-(24*60*60)
    todayStr= str(int(today))
    print(todayStr)
    for ws in wsts:
        if ws.acell("E1").value == "PUUID:":
            print("Mise à jour des données de "+ws.acell("B1").value)

            ws.update([[0] for i in range(6,13)],"C6:C12")

            puuid = ws.acell("F1").value
            url = URL+"lol/match/v5/matches/by-puuid/"+puuid+"/ids"

            nb_games=0

            req = url+"?start=0&count=20&api_key="+API_KEY

            response = requests.get(req)
            if response.ok:
                result = response.json()
                for match_id in result:
                    

                    url = URL+"lol/match/v5/matches/"+match_id
                    response = requests.get(url+"?start=0&count=20&api_key="+API_KEY)
                    if response.ok:
                        res = response.json()
                        if res["info"]["gameMode"] == "CLASSIC" and res["info"]["gameType"] == "MATCHED_GAME":
                            nb_games+=1
                            print('Match ',match_id)
                            #Incrémente le nombre de games jouées
                            game_played = float(ws.acell("D6").value.replace(",","."))+1
                            ws.update_acell("D6",game_played)

                            indexPlayer = res["metadata"]["participants"].index(puuid)
                            participants = res["info"]["participants"][indexPlayer]

                            #Minions/Minute
                            old_mpm = float(ws.acell("B6").value.replace(",","."))
                            mpm = participants["totalMinionsKilled"] / (res["info"]["gameDuration"]/60)
                            mean_mpm = ((old_mpm*(game_played-1)) + mpm) /game_played
                            ws.update_acell("B6", mean_mpm)
                            ws.update_acell("C6", float(ws.acell("C6").value.replace(",",".")) + mpm)

                            #Kill Participation
                            old_kp = float(ws.acell("B7").value.replace(",","."))
                            kp = (participants["assists"] +participants["kills"]) / sum([k["kills"]  for k in res["info"]["participants"] if k["teamId"] == participants["teamId"]] )
                            mean_kp = ((old_kp*(game_played-1)) + kp) /game_played
                            ws.update_acell("B7", mean_kp)

                            ws.update_acell("C7", float(ws.acell("C7").value.replace(",",".")) + kp)

                            #Damage
                            old_dmg = float(ws.acell("B8").value.replace(",","."))
                            dmg = participants["totalDamageDealtToChampions"] / (res["info"]["gameDuration"]/60)
                            mean_dmg = ((old_dmg*(game_played-1)) + dmg) /game_played
                            ws.update_acell("B8", mean_dmg)

                            ws.update_acell("C8", float(ws.acell("C8").value.replace(",",".")) + dmg)

                            #DamageObjective
                            old_dmgObj = float(ws.acell("B9").value.replace(",","."))
                            dmgObj = participants["damageDealtToObjectives"]
                            mean_dmgObj = ((old_dmgObj*(game_played-1)) + dmgObj) /game_played
                            ws.update_acell("B9", mean_dmgObj)

                            ws.update_acell("C9", float(ws.acell("C9").value.replace(",",".")) + dmgObj)

                            #Deaths/minute
                            old_dpm = float(ws.acell("B10").value.replace(",","."))
                            dpm = participants["deaths"] / (res["info"]["gameDuration"]/60)
                            mean_dpm = ((old_dpm*(game_played-1)) + dpm) /game_played
                            ws.update_acell("B10", mean_dpm)

                            ws.update_acell("C10", float(ws.acell("C10").value.replace(",",".")) + dpm)

                            #KDA
                            old_kda = float(ws.acell("B11").value.replace(",","."))
                            kda = (participants["assists"] +participants["kills"])/ participants["deaths"]
                            mean_kda = ((old_kda*(game_played-1)) + kda) /game_played
                            ws.update_acell("B11", mean_kda)

                            ws.update_acell("C11", float(ws.acell("C11").value.replace(",",".")) + kda)

                            #Vision score
                            old_vs = float(ws.acell("B12").value.replace(",","."))
                            vs = participants["visionScore"]
                            mean_vs = ((old_vs*(game_played-1)) + vs) /game_played
                            ws.update_acell("B12", mean_vs)

                            ws.update_acell("C12", float(ws.acell("C12").value.replace(",",".")) + vs)

                            print("CS/Min=",mpm,";Kill Participation=",kp,";Damage=",dmg,";Damage Obj=",dmgObj,";Morts/Min=",dpm,";KDA=",kda,";Vision=",vs)

                            time.sleep(60)
   

                if nb_games < 20 and nb_games >0:       
                    for k in range (6,13):
                        old = float(ws.acell("C"+str(k)).value.replace(",","."))
                        print(old)
                        ws.update_acell("C"+str(k), old/nb_games)
                    

            

if __name__ == "__main__":

    launch = True

    while launch :
        ans = input("Que souhaitez vous faire ?" +
                "\n\t(1) Créer un joueur"+
                "\n\t(2) Mettre à jour les stats"+
                
                "\n Votre réponse : ")
        

        match ans:
            case "1":
                pseudo = input("entrer le nom du joueur : ")
                tag = input("entrer le tag du joueur : ")
                strRole= input("entrer le rôle du joueur : ")

                print()

                if strRole != "" and tag != "" and pseudo != "":
                    createNewPlayer(pseudo,tag)
            case "2":
                update_players()

        rep = input("Continuer ? (Y/n) : ")
        if rep == "n" or rep == "N":
           
            launch = False
                

    