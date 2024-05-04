import os
import pandas as pd
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"] 
SPREADSHEET_ID = "1NMq9RPDxrHE-mtxUE0VlVJU0xqNcVGBlUe6FWAFFq98" #give the google sheet id 
runningName="socFourSquare"  # Name of the graph 

def main():
  #file authentication
  credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
            
    gc = gspread.authorize(credentials)
    st = gc.open_by_key(SPREADSHEET_ID)
    worksheet = st.get_worksheet(0)  
    
    df = get_as_dataframe(worksheet) #making dataframe
    #print(df.head())
    df.set_index('Index', inplace=True) #made first column as index 
    column_list = df.columns
    #df.loc["degree","memory-3"]=40
    #df.reset_index(inplace=True)     
    #df.drop(columns=df.columns[-1], inplace=True)

  #  print(df.head())
    directory_path = 'txt_files' #location of txt files 
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):
                #inside txt file name format Time-xxx-socFourSquare-5.txt 
                file_split = file.split('-')
                row_name=file_split[1]
                edge_name=file_split[2]
                clique_number=file_split[3].split('.')[0]
                # print(f" row name {row_name} edge_name = {edge_name} clique ={clique_number}")
                
                if edge_name==runningName:
                    file_path = os.path.join(root, file)  
                    with open(file_path, 'r') as f: 
                        content = f.read()
                    #inside txt file format RSS=30844 TIME=0.57+2520.99
                    t= content.split(' ')
                    ms=int(t[0].split('=')[1])
                    time=str(t[1].split('=')[1])
                    
                    column_name_ms='M/S'+'-'+clique_number
                    column_name_RN='RT'+'-'+clique_number

                    df.loc[row_name, column_name_ms] = ms
                    df.loc[row_name, column_name_RN] = time
    
    df.reset_index(inplace=True)                    
    set_with_dataframe(worksheet, df)
        
        
    
    
    
if __name__ == "__main__":
    main()
