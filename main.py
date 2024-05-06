import gspread
from google.oauth2.service_account import Credentials
import requests

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

URL = "https://europe.api.riotgames.com/"

MATCH = "/lol/match/v5/matches/by-puuid/{puuid}/ids"
API_KEY = "RGAPI-c8339727-14f9-4ab4-815a-ea966abf14a6"

SHEET_ID = "1MtUAVv3p2X0syIAfP4Kt62L16Gdder6X66aAjpzKR8M"
NB_ROWS = 100
NB_COLS = 20

creds = Credentials.from_service_account_file("credentials.json",scopes=scopes)
client = gspread.authorize(creds)

SHEET = client.open_by_key(SHEET_ID)

def createNewPlayer(sheet_name, pseudo,tag):
    try:
        ws = SHEET.worksheet(sheet_name)
    except BaseException as e:
        ws = None
    
    response = requests.get(URL+"riot/account/v1/accounts/by-riot-id/"+pseudo+"/"+tag+"?api_key="+API_KEY)
    if response.ok:
        puuid = response.json()["puuid"]

        if ws != None:
            rep = input("Un joueur a déjà ce rôle. Voulez vous le remplacer ? (y/N)")

            if rep == "y" or rep == "Y":
                SHEET.del_worksheet(ws)

                ws = SHEET.add_worksheet(title=sheet_name,rows=NB_ROWS,cols=NB_COLS)

                joueur(ws,pseudo,tag,puuid)
        else:
            ws = SHEET.add_worksheet(title=sheet_name,rows=NB_ROWS,cols=NB_COLS)
            joueur(ws,pseudo,tag,puuid)
        
# Créé et formate un joueur dans l'excel de la façon par défaut
def joueur(ws,pseudo,tag,puuid):
    ws.update_acell("A1","Pseudo:")
    ws.update_acell("B1",pseudo)
    ws.update_acell("C1","Tag:")
    ws.update_acell("D1",tag)
    ws.update_acell("E1","PUUID:")
    ws.update_acell("F1",puuid)

    ws.update_acell("A3","RANG")

    ws.update_acell("A5","Solo Queue Classée")
    ws.update_acell("B5","Moyenne Globale")
    ws.update_acell("C5","Moyenne 20 games")
    ws.update_acell("D5","Game comptées")
    ws.update_acell("D6",0)

    ws.update_acell("A6","CS/minutes")
    ws.update_acell("A7","Kill participation")
    ws.update_acell("A8","Damage")
    ws.update_acell("A9","Damage Objectif")
    ws.update_acell("A10","Morts / Minutes")
    ws.update_acell("A11","KDA")
    

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
    })   

    ws.format("A6:D11",{
        "backgroundColor": {
            "red": 255/255,
            "green":229/255,
            "blue": 153/255
        },
    })   

#Mise à jour des stats de chaque joueur dans l'excel
def update_players():
    wsts = SHEET.worksheets()

    for ws in wsts:
        if ws.acell("E1").value == "PUUID:":
            print("Mise à jour des données de "+ws.acell("B1").value)



            puuid = ws.acell("F1").value
            url = URL+"lol/match/v5/matches/by-puuid/"+puuid+"/ids"

            response = requests.get(url+"?start=0&count=20&api_key="+API_KEY)
            if response.ok:
                result = response.json()
                print(result)
                for match_id in result:
                    
                    url = URL+"lol/match/v5/matches/"+match_id
                    response = requests.get(url+"?start=0&count=20&api_key="+API_KEY)
                    if response.ok:
                        res = response.json()
                        if res["info"]["gameMode"] == "CLASSIC" and res["info"]["gameType"] == "MATCHED_GAME":
                            indexPlayer = res["metadata"]["participants"].index(puuid)
                            print(res["info"]["participants"][indexPlayer])

            

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
                role= input("entrer le rôle du joueur : ")

                if role != "" and tag != "" and pseudo != "":
                    createNewPlayer(role.upper(),pseudo,tag)
            case "2":
                update_players()

        rep = input("Continuer ? (Y/n) : ")
        if rep == "n" or rep == "N":
           
            launch = False
                

    