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




     

#Mise à jour des stats de chaque joueur dans l'excel
def update_players():
    wsts = SHEET.worksheets()
    
    
    for ws in wsts:
        
        if ws.acell("E1").value == "PUUID:":
            print("\nMise à jour des données de "+ws.acell("B1").value)
            match ws.acell("B2").value:
                case "Support":
                   match  ws.acell("D2").value:
                        case "Valhalla":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.SUPPORT,Roaster.VALHALLA,ws.acell("F1").value,ws)
                            p.update()
                        case "Helheim":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.SUPPORT,Roaster.HELHEIM,ws.acell("F1").value,ws)
                            p.update()
                case "Mid":
                    match  ws.acell("D2").value:
                        case "Valhalla":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.MID,Roaster.VALHALLA,ws.acell("F1").value,ws)
                            p.update()
                        case "Helheim":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.MID,Roaster.HELHEIM,ws.acell("F1").value,ws)
                            p.update()
                case "Top":
                    match  ws.acell("D2").value:
                        case "Valhalla":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.TOP,Roaster.VALHALLA,ws.acell("F1").value,ws)
                            p.update()
                        case "Helheim":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.TOP,Roaster.HELHEIM,ws.acell("F1").value,ws)
                            p.update()
                case "Jungle":
                    match  ws.acell("D2").value:
                        case "Valhalla":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.JUNGLE,Roaster.VALHALLA,ws.acell("F1").value,ws)
                            p.update()
                        case "Helheim":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.JUNGLE,Roaster.HELHEIM,ws.acell("F1").value,ws)
                            p.update()
                case "Adc":
                    match  ws.acell("D2").value:
                        case "Valhalla":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.ADC,Roaster.VALHALLA,ws.acell("F1").value,ws)
                            p.update()
                        case "Helheim":
                            p = Player(ws.acell("B1").value,ws.acell("D1").value,Role.ADC,Roaster.HELHEIM,ws.acell("F1").value,ws)
                            p.update()
    print("\nJoueurs mis à jour.")

                
                            

                    

            

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
                strRole= input("entrer le rôle du joueur (S/T/J/A/M): ")
                strRoster= input("entrer le roster du joueur (V/H) : ")

                if tag != "" and pseudo != "":
                    match strRole.upper():
                        case "S"|"SUPPORT"|"SUPP":
                            match strRoster.upper():
                                case "V"|"VALHALLA":
                                    createNewPlayer(pseudo,tag,Role.SUPPORT,Roaster.VALHALLA)
                                case "H"|"HELHEIM":
                                    createNewPlayer(pseudo,tag,Role.SUPPORT,Roaster.HELHEIM)
                        case "T"|"TOP":
                            match strRoster.upper():
                                case "V"|"VALHALLA":
                                    createNewPlayer(pseudo,tag,Role.TOP,Roaster.VALHALLA)
                                case "H"|"HELHEIM":
                                    createNewPlayer(pseudo,tag,Role.TOP,Roaster.HELHEIM)
                        case "J"|"JUNGLE"|"JUNGLER":
                            match strRoster.upper():
                                case "V"|"VALHALLA":
                                    createNewPlayer(pseudo,tag,Role.JUNGLE,Roaster.VALHALLA)
                                case "H"|"HELHEIM":
                                    createNewPlayer(pseudo,tag,Role.JUNGLE,Roaster.HELHEIM)

                        case "M"|"MID":
                            match strRoster.upper():
                                case "V"|"VALHALLA":
                                    createNewPlayer(pseudo,tag,Role.MID,Roaster.VALHALLA)
                                case "H"|"HELHEIM":
                                    createNewPlayer(pseudo,tag,Role.MID,Roaster.HELHEIM)

                        case "A"|"ADC"|"ADCARRY":
                            match strRoster.upper():
                                case "V"|"VALHALLA":
                                    createNewPlayer(pseudo,tag,Role.ADC,Roaster.VALHALLA)
                                case "H"|"HELHEIM":
                                    createNewPlayer(pseudo,tag,Role.ADC,Roaster.HELHEIM)
                        
                        case _ :
                            print("Rôle inconnu\n")
            case "2":
                update_players()
            

        rep = input("Continuer ? (Y/n) : ")
        if rep == "n" or rep == "N":
           
            launch = False
                

    