import pandas as PD
import webbrowser
import dash
import dash_html_components as HTML
import dash_core_components as dcc

import plotly.graph_objects as GO
import plotly.express as EX
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc
import dash_table as dt

Dash_obj = dash.Dash()
project_name = 'Telecom Project'

def Split_into_3():
    dataset = 'Partially_clean_CDR_data.csv'
   
    
    call_cols = ["4", "5", "14", "31", "120", "147", "267", "312", "345", \
                 "date", "starttime", "endtime", "duration", "Hour_information", "Weekday"] 
    call_data = PD.read_csv(dataset, usecols = call_cols, low_memory = False)
    
    call_data = PD.DataFrame(call_data)    
    
    service_cols = ["31", "120", "147", "345", "date", "starttime", "endtime", "duration"]
    service_data = call_data[service_cols]
    
    device_cols = ["5", "31", "120", "312", "345", "date", "starttime", "endtime", "duration"]
    device_data = call_data[device_cols] 
    
    # pass a dictionary for coloumns :
    call_data = call_data.rename(columns = {"4":"Group", "5":"Call Direction", "14":"Missed Call",\
                                            "31":"Group ID", "120":"User ID", "147":"Features",\
                                                "267":"VP Dialling Face Result",\
                                                "312":"Usage Device Type", "345":"User Device Type"})
        
    service_data = service_data.rename(columns = {"120":"User ID", "31":"Group ID",\
                                                  "345":"User Device Type",\
                                                      "date":"Feature Event Date"})                                          

    device_data = device_data.rename(columns = {"5":"Device Event Type Direction", "120":"User ID",\
                                                "31":"Group ID", "345":"User Device Type",\
                                                "date":"Device Event Date",\
                                                    "312":"Usage Device Type"})
    
    call_data.to_csv('Call_data.csv', index = None)
    service_data.to_csv('Service_data.csv', index = None)
    device_data.to_csv('Device_data.csv', index = None)  
    
def load_to_df():
    
    global call_df
    call_data = PD.read_csv('Call_data.csv')
    call_df = PD.DataFrame(call_data)
    
    global service_df
    service_data = PD.read_csv('Service_data.csv')
    service_df = PD.DataFrame(service_data)
    
    global device_df
    device_data = PD.read_csv('Device_data.csv')
    device_df = PD.DataFrame(device_data)

def options_for_dropdown():
    date_list = sorted( call_df['date'].dropna().unique().tolist() )
    
    global start_date_list
    start_date_list = [{"label":str(i), "value":str(i)} for i in date_list]
    
    global end_date_list
    end_date_list = [{"label":str(i), "value":str(i)} for i in date_list]
    
    global report_format
    report_format = [{"label":str(i), "value":str(i)} for i in ['Hourly', 'Daywise', 'Weekly']]

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')
    
def Create_UI():
    page_layout =  HTML.Div(
        [HTML.H1(children='CDR Analytics', id = 'Page Heading'),
        
        dcc.Dropdown(id = 'Startdate Dropdown', options = start_date_list, placeholder = 'Select Start Date'),
        dcc.Dropdown(id = 'Enddate Dropdown', options = end_date_list, placeholder = 'Select End Date'),
        dcc.Dropdown(id = 'Group Dropdown', multi = True, placeholder = 'Select Group'),
        dcc.Dropdown(id = 'Report type Dropdown', options = report_format, placeholder = 'Select Report Type'),
        
        HTML.Br(),
        
        dcc.Loading(HTML.Div(id = 'Visualisation Object', children = 'Graphs, Cards, Table'))
        ]         
                 
        )
    return page_layout

@Dash_obj.callback(
    Output('Visualisation Object','children'),
    [
     Input('Startdate Dropdown','value'),
     Input('Enddate Dropdown','value'),
     Input('Group Dropdown','value'),
     Input('Report type Dropdown','value')
     
     ]
    )

def Update_Visualisation(start_date, end_date, group, report_type):
    
    figure = GO.Figure()
    
    if (report_type == 'Hourly'):
        condition = (call_df['date']>=start_date) & (call_df['date']<=end_date)
        Corresp_hrs = call_df[condition] ['Hour_information']
        Unique_hrs = sorted(Corresp_hrs.unique())
        Hr_and_count = [
            {"label":i,"value":Corresp_hrs.tolist().count(i)} 
            for i in Unique_hrs]
        figure = GO.Figure(
            
            data = GO.Scatter(
                x = PD.DataFrame.from_dict(Hr_and_count['label']),
                y = PD.DataFrame.from_dict(Hr_and_count['value'])
                )
            )
         
    elif (report_type == 'Daywise'):
         condition = (call_df['date']>=start_date) & (call_df['date']<=end_date)
         Corresp_date = call_df[condition] ['date']
         Unique_date = sorted(Corresp_date.unique())
         Date_and_count = [
             {"label":i,"value":Corresp_date.tolist().count(i)} 
             for i in Unique_date]
         figure = GO.Figure(
            
             data = GO.Scatter(
                 x = PD.DataFrame.from_dict(Date_and_count['label']),
                 y = PD.DataFrame.from_dict(Date_and_count['value'])
                 )
             )
        
    elif (report_type == 'Weekly'):
         condition = (call_df['date']>=start_date) & (call_df['date']<=end_date)
         Corresp_day = call_df[condition] ['Weekday']
         Unique_day = sorted(Corresp_day.unique())
         Day_and_count = [
             {"label":i,"value":Corresp_day.tolist().count(i)} 
             for i in Unique_day]
         figure = GO.Figure(
            
             data = GO.Scatter(
                 x = PD.DataFrame.from_dict(Day_and_count['label']),
                 y = PD.DataFrame.from_dict(Day_and_count['value'])
                 )
             )
    else:
        print('No report type provided')
    
    return [dcc.Graph(figure), HTML.Div(dbc.Card()), dt.DataTable()]

@Dash_obj.callback(
    Output('Group Dropdown','options'),
    [
     Input('Startdate Dropdown','value'), 
     Input('Enddate Dropdown','value')
     ]    
    )

def Update_Group(start_date, end_date):
    
    reformed_data = call_df[(call_df['date']>=start_date) & (call_df['date']<=end_date)]
    
    group_list = reformed_data['Group'].unique().tolist()  
    
    group_list = [ {"label":i, "value":i} for i in group_list ]
    
    return group_list

# Main code

def main():
    print('Now inside main()')
    
    global project_name
    print('Project title :', project_name)
    
    open_browser()
    
    load_to_df()
    options_for_dropdown()
    
    global Dash_obj
    Dash_obj.layout = Create_UI()   
    Dash_obj.title = project_name # Changes the text near the favicon    
    Dash_obj.run_server()
    
    print('End of main() reached')
    
    # Global variables cannot be changed locally, So :
    
    global call_df, service_df, device_df, start_date_list,\
        end_date_list, report_type
    
    project_name = None
    call_df = None
    service_df = None
    device_df = None
    start_date_list = None
    end_date_list = None
    report_type = None
    Dash_obj = None

if (__name__ == '__main__'):
    main()