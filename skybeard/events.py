import telegram
import re
import telegram
import datetime 
import logging
import pdb
import random
from beard_functions import *
from msg_texts import *
import bottools as btools
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


#class for dota event
class dota:
    
    def __init__(self,bot,message,time):

        self.bot = bot
        self.creator = message.from_user
        self.message = message 
        self.rdrys = []
        self.people =[]
        self.people.append(self.creator.first_name)
        
        #set times
        self.time = time
        self.date_create = datetime.datetime.now()
        self.hour = None
        self.minute = None
        self.date_dota = None
        self.set_time(self.time)
                      
        #dota initialization text message
        sendText(bot,message.chat_id,
                ' '.join([msgs['makedota'],
                    tformat(self.date_dota),
                    msgs['w'],
                    self.creator.first_name])
                )
        self.play_since_patch(self.creator)
   
        self.dtime = self.date_dota-self.date_create

        infoprint(self.bot,message,"dota event")

    def set_time(self,time):
        try:
            self.hour = time[:2]
            self.minute = time[2:]
            self.date_dota = self.date_create.replace(hour=int(self.hour),minute=int(self.minute))
        except:
            self.hour = '19'
            self.minute = '30'
            self.date_dota = self.date_create.replace(hour=int(self.hour),minute=int(self.minute))
            
            sendText(self.bot,self.message.chat_id,msgs['t_error'])
    
    def play_since_patch(self,player):
        player_id = player.id
        try:
            cats = yaml.load(open('catabase/unpatched.yaml','rb'))
        except:
            return logging.error('no un patched players file')
        
        if btools.keySearch(cats,'telegram_id',player_id): 
            i = next(index for (index, cat) in enumerate(cats) if cat["telegram_id"] == player_id)
            logging.info('deleting cat from unpatched players',i,cats(i))
            cats.pop(i)
            yaml.dump(cats,open('catabase/unpatched.yaml','wb'))
            return sendText(self.bot,self.message.chat_id,msgs['patch_warn'])
        else:
            return logging.info('player is patched')

    def shotgun(self,message,user_str=''):
        infoprint(self.bot,message,"shotgun request")
        if user_str is '':
            first_name = message.from_user.first_name
        else:
            first_name = user_str

        if first_name not in self.people:
            sendText(self.bot,
                    message.chat_id,
                    ' '.join([first_name,
                        msgs['shotgun'],
                    self.time+" with: \n",
                    ', '.join(self.people)])
                    )
            self.people.append(first_name)
        else:
            sendText(self.bot,message.chat_id,
                    ''.join([first_name,
                    ", you already shotgunned"])
                    )
        self.play_since_patch(message.from_user)
        
    def unshotgun(self,message,case):
        
        if (case == 'shotgun'):
            self.people = remove_list_val(self.people,message.from_user.first_name)
        if (case == 'shotgun' or 'rdry'):
            self.rdrys = remove_list_val(self.rdrys,message.from_user.first_name)
        sendText(self.bot,message.chat_id,
                message.from_user.first_name
                +', your '+case+' has been cancelled!')

    def rdry_up(self,message):

        infoprint(self.bot,message,"ready up request")
        
        if message.from_user.first_name not in self.rdrys:
            self.rdrys.append(message.from_user.first_name)
            sendText(self.bot,message.chat_id,
                    ''.join([message.from_user.first_name,
                    ", you have readied up! \nCurrent rdry's: \n",
                    ', '.join(self.rdrys)])
                    )
        else:
            sendText(self.bot,message.chat_id,
                    message.from_user.first_name+", you are already readied up!")
        if message.from_user.first_name not in self.people:
            self.people.append(message.from_user.first_name)
            sendText(self.bot,message.chat_id,'(...and I\'ve also shotgunned you)')

    def get_rdrys(self):
        return self.rdrys
    
    def stack(self,message):
        infoprint(self.bot,message,"stack status request")
        num_rdry = len(self.rdrys)
        num_shot = len(self.people)
        
        if (num_shot == 5):
            sendText(self.bot,message.chat_id,
                    "There is currently a 5 stack with: \n"
                    +', '.join(self.people)
                    +'\nCurrent rdry\'s:\n'
                    +', '.join(self.rdrys))

        elif(num_shot<5):

            sendText(self.bot,message.chat_id,
                    'No stack yet. \nCurrent shotguns: \n'
                    +', '.join(self.people)
                    +'\nCurrent rdry\'s: \n'
                    +', '.join(self.rdrys))
        else:

            sendText(self.bot,
                    message.chat_id,msgs['overstack']+', '.join(self.people))

    def info(self,message):
        infoprint(self.bot,message,"dota info request")
        sendText(self.bot,message.chat_id,
                "Dota is happening tonight at "
                +self.time+" with: \n"
                +', '.join(self.people))

    def time_info(self,message):
        infoprint(self.bot,message,"dota time info request")
        self.dtime = self.date_dota-datetime.datetime.now()
	#+datetime.timedelta(hours=1) accounts for time zone difference. Remove when server is UK side.
        dt_hours,dt_minutes,dt_seconds = get_dtime(self.dtime)
        dtime_str = ':'.join([dt_hours,dt_minutes,dt_seconds])
        
        if (datetime.datetime.now()>self.date_dota):
            when_str = 'Dota already began at '+tformat(self.date_dota)
        else:
            when_str = "Dota will begin at "+tformat(self.date_dota)+", in "+dtime_str

        sendText(self.bot,message.chat_id,when_str+"\n*Shotguns:*\n"+', '.join(self.people))

    def tcheck(self,message):
        mins = 15
        if self.date_dota - datetime.datetime.now() < datetime.timedelta(minutes=mins) and self.date_dota > datetime.datetime.now():
            sendText(self.bot,message.chat_id,'Dota will begin in a few minutes. Get hype!')
            return True
        else: 
            return False

def nodota(bot, message):
    
    sendText(bot,message.chat_id,msgs['nodota'])


#For unshotgunning, unrdry-ing 
def remove_list_val(the_list, val):
       return [value for value in the_list if value != val]

#zero pad time format
def tformat(date):
    return str(date.hour).zfill(2)+":"+str(date.minute).zfill(2)


#Find if the time was specified for an event and what it is
def get_time(bot,message):
    logging.info('Getting dota time from message:',message.text)
    text = message.text
   
    for ch in [':','.',';','-']:
        if  ch in message.text:
            print ch
            text = message.text.replace(ch,'')

    match = re.search(r'at\s*(\w+)', text)
    
    if match:
        print match.group(1)
        time = str(match.group(1))
    else:    
        sendText(bot,message.chat_id,msgs['notime'])
        time = "1930"
    
    return time


def get_str_list(bot,message,match):
    if match in message.text:
        string = message.text.split("with",1)[1]
        split_list = [element.strip() for element in string.split(',')]
        return split_list
    else:
        return []
    
    
def get_dtime(dtime):
    days, seconds = dtime.days, dtime.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return str(hours),str(minutes),str(seconds)


#DEPRECATED
#Find out what kind of event it is 
def get_event(message):

    for pattern in message.text.split():
        if "dota" in pattern.lower():
            event = "dota"
        else:
          event = "event"
