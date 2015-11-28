import telegram
import yaml
import pickle
import shutil
import beard_functions as bf
from msg_texts import * 
import logging

def getCats():
    
    try:
        spacecats = yaml.load(open('catabase/catabase.yaml','rb'))
    except:
        spacecats = []

    return spacecats

def regCats(bot,message):
    
    text = message.text
    user = message.from_user
    tg_id = user.id
    tg_fname = user.first_name
    tg_sname = user.last_name
    
    spacecats = getCats()
    catmatch = filter(lambda cat: cat['telegram_id'] == tg_id, spacecats)
    
    if catmatch:
        bf.sendText(bot,message.chat_id,msgs['reg_check'],True)
        return
    else:
        details = text.split('/register',1)[1]
        
        try:
            details_list = [element.strip() for element in details.split(',')]
            dota_fname = details_list[0]
            dota_sname = details_list[1]
            dota_id = int(details_list[2].split('/players/',1)[1])
            dota_name = ' '.join([dota_fname,dota_sname])
        
        except:
            bf.sendText(bot,message.chat_id,msgs['reg_help'],True)
            return
        
        cat_dict = {
                'dota_name':    dota_name,
                'dota_id':      dota_id,
                'first_name':   tg_fname,
                'last_name':    tg_sname,
                'telegram_id':  tg_id
                }
        logging.info(cat_dict)
        
        spacecats.append(cat_dict)
        saveCats(spacecats)
        return bf.sendText(bot,message.chat_id,'New Spacecat added to the space catabase!')

def saveCats(cats):
    yaml.dump(cats,open('catabase/catabase.yaml','wb'))

def deleteCat(bot,message):
    cats = getCats()
    
    try:
        index = int(message.text.split('cat',1)[1].strip())
    except:
        return bf.sendText(bot,message.chat_id,'Couldn\'t parse index')
    
    try:
        cat = cats[index]
    except:
        return bf.sendText(bot,message.chat_id,'index not found')


    if(permission(message,cat)):
        cats.pop(index)
    else:
        return bf.sendText(bot,message.chat_id,message.from_user.first_name+', you do not have permission to delete this entry')

    saveCats(cats)
    return bf.sendText(bot,message.chat_id,'Entry number '+str(index)+' removed.\nNew catabase saved.')

def permission(message,db_entry):
    user_id = message.from_user.id
    try:
        admins = pickle.load(open('catabase/catmins.p','rb'))
    except:
        admins = []

    if (db_entry['telegram_id']==user_id) or user_id in admins:
        return True
    else:
        return False

def is_user_admin(message):
    user_id = message.from_user.id

    try:
        admins = pickle.load(open('catabase/catmins.p','rb'))
    except:
        admins = []

    if user_id in admins:
        return True
    else:
        return False

def printCats(bot,message):
    cats = getCats()

    logging.info(cats)
    
    db_size = len(cats)
    bf.sendText(bot,message.chat_id,'There are '+str(db_size)+' catabase entries:')
    entry_found = False
    for index in range (0,len(cats)):
        cat = cats[index]
        if permission(message,cat):
            entry_found = True
            vals = [str(i) for i in cat.values()]
            bf.sendText(bot,message.chat_id,str(index)+', '+', '.join(vals))
    if not entry_found:
            bf.sendText(bot,message.chat_id,'It appears as though you do not have permission to view any entries.')

def dumpCats(bot,message):
    cats = getCats()
    for cat in cats:
        bf.sendText(bot,message,str(cat))
        logging.info(cat)

