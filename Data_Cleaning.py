import re
import math
import numpy as NP
import pandas as PD
import datetime 


Dataset = PD.read_csv('raw_cdr_data.csv', header=None, low_memory=False)

df = PD.DataFrame(Dataset)

def datetime_divider(data) :
  for i in range(len(data)):
      
    if re.match('\d', str(data[i]) ):
      regexp = re.compile('\d{1,8}')
      a = regexp.findall( str(data[i]) )
      data[i] = [ a[0],a[1] ]     
    else:
      data[i] = [NP.nan,NP.nan]
      
  return data
df["date"], df["time"] = zip( *datetime_divider( df[9].tolist()) )


 
def date_modifier(data):
  for i in range(len(data)):
      
    if (re.match('\d', str(data[i])) ):
       str1 = str(data[i]) [0:4]
       str2 = str(data[i]) [4:6]
       str3 = str(data[i]) [6:8]
       data[i] = '-'.join([str1, str2, str3])      
    else:
       data[i] = NP.nan
       
  return data
df["date"] = date_modifier(df["date"])



def time_modifier(data):
  for i in range(len(data)):  
      
    if (re.match('\d', str(data[i])) ):
       Hr = int( str(data[i]) [0:2] )
       if (Hr >= 12):
          Hr = Hr - 12
          Hr = str(Hr)
          merd = 'PM'
       else:
          Hr = str(Hr)
          merd = 'AM'
       Min = (str(data[i])) [2:4]
       Sec = (str(data[i])) [4:6]

       data[i] = ':'.join([Hr, Min, Sec]) + ' ' + merd
       
    else:
       data[i] = NP.nan 
       
  return data
df["time"] = time_modifier(df["time"])



def Correct_terminology(data):

  data[5] = data[5].replace('Originating','Outgoing')
  data[5] = data[5].replace('Terminating', 'Incoming') 
  data[267] = data[267].replace('Success', 'Voice Portal')
  data[312] = data[312].replace('Shared Call Appearance', 'Secondary Device')
  return data
df = Correct_terminology(df)


def Clean_312(data):
  for i in range(len(data)):
      
    if ( (data[i] == "Primary Device") | (data[i] == "Secondary Device") ):
      continue      
    else:
      data[i] = NP.nan
      
  return data
df[312] = Clean_312(df[312].tolist())  
 


def Combine_services(data1, data2, data3):
  for i in range(len(data1)):
    
    if data1[i] is NP.nan:
      
      if data2[i] is not NP.nan and data3[i] is not NP.nan :
        data1[i] = str(data1[i]) + ', ' + str(data2[i])
      elif data2[i] is not NP.nan :
        data1[i] = str(data2[i])
      else:
        data1[i] = str(data3[i])
    
    else:
      continue
    
    return data1 
df[147] = Combine_services( df[147].tolist(), df[267].tolist(), df[312].tolist() )


 

def Call_time_fetcher(data):
  for i in range(len(data)):
   

    if (math.isnan(data[i])):
      continue
  
    else:  
      Yr = str(data[i]) [:4]
      Mnth = str(data[i]) [4:6]
      Day = str(data[i]) [6:8]
      Hrs = str(data[i]) [8:10]
      Mins = str(data[i]) [10:12]
      Secs = str(data[i]) [12:14]

      if(float(Secs) >= 60):
        Secs = float(Secs) - 60
        Mins = float(Mins) + 1
      if(float(Mins) >= 60):
        Mins = float(Mins) - 60
        Hrs = Hrs + 1
      
      data[i] = f"{Yr}-{Mnth}-{Day} {Hrs}:{Mins}:{Secs}"
    
  return data
df["starttime"] = PD.to_datetime(Call_time_fetcher( df[9].tolist() ) )
df["endtime"] = PD.to_datetime(Call_time_fetcher( df[13].tolist() ) )



df["duration"] = ( df["endtime"]-df["starttime"] ).astype("timedelta64[m]")


 
def Hourly_range(data):
  for i in range(len(data)):

    data[i] = str(data[i])
    if (data[i] != "nan"):
      
      if re.search('PM', data[i]):
        time_data = re.findall('\d+', data[i])
        if time_data[0] != '12':
          time_data = int(time_data[0]) + 12 
        else:
          time_data = time_data[0]
      
      else:
        time_data = re.findall('\d+', data[i])
        if int(time_data[0]) == 12:
          time_data = f"0{ int(time_data[0]) - 12 }" 
        else:
          time_data = time_data[0]

      data[i] = f"{time_data}:00 - {time_data}:59"

    else:
      data[i] = NP.nan 

  return data 
df["Hour_information"] = Hourly_range(df["time"])  



def Weekly_range(data):
  for i in range(len(data)):
      
      if not (PD.isnull( data[i] )):
        Yr, Mnth, Day = [int(x) for x in (data[i]).split("-")] 
        ans = datetime.date(Yr, Mnth, Day) 
        data[i] = ans.strftime("%A")
      else:
        data[i] = NP.nan 

  return data
df["Weekday"] = Weekly_range(df["date"])



df = df.drop("time",axis = 1)


df.to_csv('Partially_clean_CDR_data.csv', index = None)