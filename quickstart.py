from __future__ import print_function
import pickle
import os.path
import time
from tkinter import *
import tkinter
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/tasks']

defaultTasks=[{'title': 'Gym','notes': 'Skipping and others'},{'title': 'Meditate','notes': 'Peace and calm'},{'title': 'Zen Mode','notes': 'be zen'}]

dailyTasks=[]
service:any
taskListID:any



window = tkinter.Tk()
labelText = StringVar()
window.configure(background='white')

ws = window.winfo_screenwidth()
hs = window.winfo_screenheight()
w = 200  # width for the Tk root
h = 500  # height for the Tk root
x = (ws / 2) - (w / 2)
y = (hs / 2) - (h / 2)

canvas1 = tkinter.Canvas(window, bg="white")
canvas1.grid(row=1,column=0)
canvas2 = tkinter.Canvas(window, bg="white")
canvas2.grid(row=1,column=3)

def doSomething():
    print('doSomething called')
    global dailyTasks
    dailyTasks.append({'title':'pushed task'})
    applytoLabel()
    

def applytoLabel():
    global dailyTasks
    global canvas
    n = len(dailyTasks)
    element = ' '
    for i in range(n):
        element = element + dailyTasks[i]['title']+'\n' 
    global labelText
    labelText.set(element)
    



def getTasks():
    global service
    global dailyTasks
    global taskListID
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get('items', [])
    dailyTasks=[]
    if not items:
        print('No task lists found.')
    else:
        #print('Task lists:')
        for item in items:
            #print(u'{0} ({1})'.format(item['title'], item['id']))
            if(item['title']=='Daily'):
                taskListID=item['id']
                tasksobj=service.tasks().list(tasklist=item['id']).execute()
                #print(tasksobj)
                print('Tasks in list '+ item['title'])
                try:
                    if(tasksobj['items']):
                        dailyTasks=tasksobj['items']
                        applytoLabel()
                except:
                    dailyTasks=[]
    
    
                

def printTasks():
    global dailyTasks
    global service
    global taskListID
    print('Tasks are:')
    for task in dailyTasks:
        print(task['title'])

def clearTasks():
    print('Deleting tasks')
    global dailyTasks
    global service
    global taskListID
    for item in dailyTasks:
        print('item')
        service.tasks().delete(tasklist=taskListID, task=item['id']).execute()
    dailyTasks=[]
    applytoLabel()
    getTasks()


def completeAllTasks():
    print('Completing tasks')
    global dailyTasks
    global service
    global taskListID
    for taskobj in dailyTasks:
        task = service.tasks().get(tasklist=taskListID, task=taskobj['id']).execute()
        task['status'] = 'completed'
        result = service.tasks().update(tasklist='@default', task=task['id'], body=task).execute()

    getTasks()


def populateTasks():
    global dailyTasks
    global service
    global taskListID
    global defaultTasks
    clearTasks()
    print('Populating tasks')
    for task in defaultTasks:
        result = service.tasks().insert(tasklist=taskListID, body=task).execute()

    getTasks()


button1 = Button(canvas2, text='Complete All', fg='black', bg='#1976D2', command=completeAllTasks, height=2, width=15) 
button1.grid(row=1, column=0) 

button2 = Button(canvas2, text='Refresh Tasks', fg='black', bg='#1976D2', command=getTasks, height=2, width=15) 
button2.grid(row=2, column=0)

button3 = Button(canvas2, text='Delete All', fg='black', bg='#1976D2', command=clearTasks, height=2, width=15) 
button3.grid(row=3, column=0) 

button4 = Button(canvas2, text='Populate Tasks', fg='black', bg='#1976D2', command=populateTasks, height=2, width=15) 
button4.grid(row=4, column=0) 



def main():
    global dailyTasks
    global service
    global window
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    today = date.today().strftime("%d/%m/%Y")
    print("Today's date:", today)
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('tasks', 'v1', credentials=creds)

    # Call the Tasks API
    #do get tasksk every 1 min (API has limit of 50000 queries per day)
    getTasks()
    printTasks()
    time.sleep(5)
    global labelText
    l9 = tkinter.Label(canvas1, textvariable=labelText, font= "calibri 14", bg="white", width="34")
    l9.grid(row=0,column=0)
    #l9.pack()
    window.mainloop()

if __name__ == '__main__':
    main()