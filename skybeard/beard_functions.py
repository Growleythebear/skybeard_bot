#functions called directly by the bot
import requests
import events
import telegram
import re
import random
import dota_functions as df
import bottools as btools
from msg_texts import * #imports 'msgs' dictionary
import pdb
import numpy as np
import matplotlib
matplotlib.use('Agg') #disable x-forwarding
import matplotlib.pyplot as plt
import pickle
import yaml
import pyowm
import omdb
import logging
import math
import datetime
import time
import sys
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

#Request, format and send dota last match info
def last_match(bot, message):
    sendText(bot,message.chat_id,msgs['getmatch'])
    
    try:
        dota_id = df.get_dota_id_from_telegram(message.from_user.id)
        logging.info('Last match request:',dota_id,message.from_user.first_name,dota_id,message.from_user.id)
        match_id = df.getLastMatch(dota_id)
        bot.sendMessage(chat_id=message.chat_id,
            text="[Requested DotaBuff page for match "
            +str(match_id)+"](http://dotabuff.com/matches/"+str(match_id)+").",
            parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        logging.info('last match info requested my non-registered user,',message.user)
        bot.sendMessage(chat_id=message.chat_id,text='You don\'t appear to be in the catabase. Please register using the /register command')

#Request, format and send dota feeding info.
def feeding(bot,message,BASE_URL,update=False):
    sendText(bot,message.chat_id,msgs['getfeed'])
    
    table = msgs['feedtable']
    
    #refreshed data from dota api
    if (update):
        logging.info('feed data update requested')
        sendText(bot,message.chat_id,msgs['serverpoll'])
        feeds = df.valRank('deaths')
        pickle.dump(feeds,open('catabase/feeds.p','wb'))
        logging.info('new feeds file saved')
    
    #displays cached data
    else:
        try:
            feeds = pickle.load(open('catabase/feeds.p','rb')) 
        #will update automatically if local cache not found
        except Exception as e:
            logging.error(e)
            sendText(bot,message.chat_id,'Local feed data not found...')
            sendText(bot,message.chat_id,msgs['serverpoll'])
            feeds = valRank('deaths')
            logging.info('feeding data defaulted to:', feeds)
            pickle.dump(feeds,open('catabase/feeds.p','wb'))
    
    i=0; #rank iterator
    for rank in feeds:
        i+=1
        table+=str(i)+"....."+str(rank['dota_name'])+"...."+str(rank['total_vals'])+"\n"    
    sendText(bot,message.chat_id,table)
    
    footer = "Congratulations to "+str(feeds[0]['dota_name'])+"! \nCheck out the match where he fed the most ("+str(feeds[0]['top_vals'])+" times!)"

    sendText(bot,message.chat_id,footer)

    bot.sendMessage(chat_id=message.chat_id,
            text="["+str(feeds[0]['dota_name'])+"'s DotaBuff Match](http://dotabuff.com/matches/"+str(feeds[0]['top_match'])+").",
            parse_mode=telegram.ParseMode.MARKDOWN)

    #graphing test
    fig = plt.figure()
    ax = fig.add_subplot(111)
    feed_values = feeds[0]['val_list']
    match_ids = feeds[0]['match_list']
    N= len(feed_values)
    ind = np.arange(N)
    width =0.8
    bars = ax.bar(ind, feed_values, width,
                            color='#e2e6ed')
    ax.set_axis_bgcolor('#bcc5d4')
    ax.set_xlim(-width,len(ind)+width)
    ax.set_ylim(0,max(feed_values)+2)
    ax.set_ylabel('deaths per game')
    ax.set_title(feeds[0]['dota_name']+'\'s graph of shame')
    ax.set_xticks(ind+width)
    ax.set_xlabel('games')
    xtickNames = ax.set_xticklabels(match_ids)
    plt.setp(xtickNames, rotation=90, fontsize=6)
    imgPath = 'img/feed.png'
    plt.savefig(imgPath,facecolor='#bcc5d4')
    postImage(imgPath,message.chat_id,BASE_URL) 

#Wrapper for telegram.bot.sendMessage() function. Markdown enabled
def sendText(bot,chat_id,text,webprevoff=False):
    
    #
    try:
        bot.sendMessage(chat_id=chat_id,text=text,parse_mode="Markdown",disable_web_page_preview=webprevoff)
    except:
        bot.sendMessage(chat_id=chat_id,text=text,disable_web_page_preview=webprevoff) 

#Searches for commands sent to bot
def command(cmd,text):
    if re.match(cmd,text,re.IGNORECASE):
        return True
    else:
        return False

#Searches for keywords sent to bot
def keywords(words,text):
    if any(word in text for word  in words):
        return True
    else:
        return False


def infoprint(bot,message,text):
    logging.info(("\nDota info request:\n["+text+"]"))
    logging.info("USER: ",message.from_user.id,message.from_user.first_name) 
    logging.info("USER MESSAGE:")
    logging.info(message.text)

def updateGainz(message):
    user = message.from_user
    user_id = user.id
    name = user.first_name

    try:
        gainz_history = yaml.load(open('catabase/gym_history.yaml','rb'))
    except:
        logging.warning('no gainz_history.yaml found. Creating new file')
        gainz_history = []
    
    now = datetime.datetime.now()
    user_new ={'user_id': user_id, 'time': now, 'name': name }
    match = btools.keySearch(gainz_history,'user_id',user_id)
    if match:
        for entry in gainz_history:
            if entry['user_id'] ==user_id:
                entry.update(user_new)
    else:
        gainz_history.append(user_new)
    yaml.dump(gainz_history,open('catabase/gym_history.yaml','wb'))
    yaml.dump(gainz_history,sys.stdout)

def checkGainz(message):

    #if there is no gym history, just post gainz photos anyway
    try:
        gainz_history = yaml.load(open('catabase/gym_history.yaml','rb'))
    except:
        logging.warning('no gainz_history.yaml found. Returning true for gainzCheck())')
        return True
    
    user_id = message.from_user.id
    entry = btools.keySearch(gainz_history,'user_id',user_id)
    
    #check if it has been more than one week (168 hours) since last gym check-in
    if entry and not expiry(entry['time'],168):
        return True
    else:
        return False


#Show chat members why they should go lift
def gainz(bot,message):
    gain_photos= [
            'http://i.imgur.com/QrdcYCP.jpg',
            'http://i.imgur.com/zopXdvc.jpg',
            'http://i.imgur.com/jEi18ha.jpg'
            ]
    
    chat_id = message.chat_id 
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    random.seed()
    
    if (checkGainz(message)):
        i = random.randint(0, len(gain_photos)-1)
        try:
            bot.sendPhoto(chat_id=chat_id, photo=gain_photos[i])
        except:
            logging.error('PHOTO PARSE ERROR:',gain_photos[i],sys.exc_info()[0])
    else:
        try:
            bot.sendPhoto(chat_id=chat_id, photo='http://i.imgur.com/Rra4uun.png') #send blobby gains
        except:
            logging.error('PHOTO PARSE ERROR:',bad_gainz[j],sys.exc_info()[0])
        sendText(bot,message.chat_id,', '.join([user_name, msgs['nogainz']]))

#Post cats in space
def postCats(bot,message):
    cat_photos= [
            'http://i.imgur.com/bJ043fy.jpg',
            'http://i.imgur.com/iFDXD5L.gif',
            'http://i.imgur.com/6r3cMsl.gif',
            'http://i.imgur.com/JpM5jcX.jpg',
            'http://i.imgur.com/r7swEJv.jpg',
            'http://i.imgur.com/vLVbiKu.jpg',
            'http://i.imgur.com/Yy0TCXA.jpg',
            'http://i.imgur.com/2eV7kmq.gif',
            'http://i.imgur.com/rnA769W.jpg',
            'http://i.imgur.com/08mxOAK.jpg'
            ]

    i = random.randint(0, len(cat_photos)-1)
    try:
        bot.sendPhoto(chat_id=message.chat_id, photo=cat_photos[i])
    except:
        logging.error('unable to parse photo:',cat_photos[i],sys.exc_info()[0])
        bot.sendPhoto(chat_id=message.chat_id,photo='http://cdn.meme.am/instances/500x/55452028.jpg')



#http POST request 
def postImage(imagePath,chat_id,REQUEST_URL):
#    pdb.set_trace()
    data = {'chat_id': chat_id}
    try:
        files = {'photo': open(imagePath,'rb')}
    except:
        return logging.error('could not send local photo',sys.exc_info()[0])
    return requests.post(REQUEST_URL + '/sendPhoto', params=data, files=files)
    
#possibility of uploading pics to dropbox with this function (needs python 2.7 or greater)    
#def dropbox():
#    client = dropbox.client.DropboxClient(os.environ.get('DROPBOX_TOKEN'))
#    print 'linked account: ', client.account_info()
#    f = open('img/feed.png', 'rb')
#    response = client.put_file('/feed.png', f)
#    print 'uploaded: ', response
#    folder_metadata = client.metadata('/')
#    print 'metadata: ', folder_metadata
#
#    f, metadata = client.get_file_and_metadata('/magnum-opus.txt')
#    out = open('magnum-opus.txt', 'wb')
#    out.write(f.read())
#    out.close()
#    print metadata

#search the omdb for a movie and displays the poster and summary
def movies(bot,message,title):
    chat_id=message.chat_id
    
    #makes the imdb search url if match not found
    def buildImdbUrl(title):
        title_list = [element.strip() for element in title.split(' ')]
        url_elements = [
                'http://www.imdb.com/find?ref_=nv_sr_fn&q=',
                '+'.join(title_list),
                '&s=all'
                ]
        url = ''.join(url_elements)
        logging.info('imdb url built',url)
        return url
    
    #poll api
    try:
        result = omdb.get(title=title)
        result.title
    except:
        sendText(bot,message.chat_id,msgs['nomovie'])
        bot.sendMessage(chat_id=chat_id,text=buildImdbUrl(title),disable_web_page_preview=True)
        #sendText(bot,message.chat_id,str(buildImdbUrl(title)),True)
    else:
        logging.info('omdb result:', result)
        film = result.title
        year = result.year
        director = result.director
        metascore = result.metascore
        imdbscore = result.imdb_rating
        plot = result.plot
        
        poster = result.poster
        imdb = 'http://www.imdb.com/title/'+result.imdb_id
        reply = (
                'Title: '+film+'\n'
                'Year: '+year+'\n'
                'Director: '+director+'\n'
                'Metascore: '+metascore+'\n'
                'IMDb rating: '+imdbscore+'\n'
                'Plot:\n'+plot
                )     

        #exception handling for movies with no poster   
        try:
            bot.sendPhoto(chat_id=chat_id,photo=poster)
        except:
            logging.error("no poster found in omdb result",result)
        sendText(bot,chat_id,reply)
        sendText(bot,chat_id,imdb,True)


#gives current weather and forecast for given location.
def forecast(bot,message,BASE_URL):
    owm = pyowm.OWM(os.environ.get('OWM_TOKEN'))
    text = message.text
    
    try:
        location = text.split('/weather',1)[1]
    
    #default location
    except:
        location = 'Birmingham,uk'
    if not location:
        location = 'Birmingham,uk'
    try:    
        #7 days of forecast
        forecast = owm.daily_forecast(location,limit=7)
        tomorrow = pyowm.timeutils.tomorrow()
        weather_tmrw = forecast.get_weather_at(tomorrow)
        logging.info(tomorrow)
    except:
        logging.info('weather request error ',sys.exc_info()[0])
        return sendText(bot,message.chat_id,'I\'m sorry, something went wrong.')
    
    #api gives 'closest match'. bot prints true location name
    true_location = forecast.get_forecast().get_location().get_name()
    coor_lon =  forecast.get_forecast().get_location().get_lon()
    coor_lat =  forecast.get_forecast().get_location().get_lat()
    
    lst_clouds = []
    lst_temp = []
    lst_status = []
    lst_time = []

    f_day = forecast.get_forecast()
    
    #get forecasts for each day
    for weather in f_day:
        lst_clouds.append( weather.get_clouds())
        lst_temp.append(weather.get_temperature('celsius')['max'])
        lst_status.append(weather.get_status())
        lst_time.append(weather.get_reference_time('iso'))
    logging.info(lst_clouds,lst_temp,lst_status,lst_time,len(lst_temp))

    #7 day forecast plot 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    N= len(lst_status)
    ind = np.arange(N)
    width =0.6
    bars_temp = ax.bar(ind, lst_temp, width,
                            color='#e2e6ed')
    ax.set_axis_bgcolor('#bcc5d4')
    ax.set_xlim(-width,len(ind)+width)
    ax.set_ylim(0,max(lst_temp)+5)
    ax.set_title('Seven day forecast')
    ax.set_xticks(ind+width)
    ax.set_xlabel('Next 7 days')
    ax.set_ylabel('Max. temperature (C)')
    plt.yticks(np.arange(min(lst_temp), max(lst_temp)+1, 1.0)) 
    xtickNames = ax.set_xticklabels(lst_status)
    plt.setp(xtickNames, rotation=45, fontsize=15)
    imgPath = 'img/weather.png'
    plt.savefig(imgPath,facecolor='#bcc5d4')
    temp_tmrw = weather_tmrw.get_temperature('celsius')
   
    #check each status (quick implementation. Needs to be mapped)    
    if forecast.will_be_sunny_at(tomorrow):
        logging.info('status: sunny')
        status = 'sunny'
    elif forecast.will_be_sunny_at(tomorrow):
        logging.info('status: cloudy')
        status = 'cloudy'
    elif forecast.will_be_rainy_at(tomorrow):
        logging.info('status: rainy')
        status = 'rainy'
    elif forecast.will_be_snowy_at(tomorrow):
        logging.info('status: snowy')
        status = 'snowy'
    elif forecast.will_be_stormy_at(tomorrow):
        logging.info('status: stormy')
        status = 'stormy'
    elif forecast.will_be_foggy_at(tomorrow):
        logging.info('status: foggy')
        status = 'foggy'
    elif forecast.will_be_tornado_at(tomorrow):
        logging.info('status: tornado')
        status = 'TORNADO!!'
    elif forecast.will_be_hurricane_at(tomorrow):
        logging.info('status: hurricane')
        status = 'HURRICANE!!'
    else:
        logging.error('unknown weather status',forecast.get_forecast)
        status = '<unknown status>'
    
    logging.info('forecast request:',message,forecast) 
    fore_reply = 'Tomorrow in '+true_location+', it will be *'+status+'* with a maximum temperature of *'+str(temp_tmrw['max'])+'* degrees C' 
    
    #current weather observation   
    observation = owm.weather_at_place(location)
    weather = observation.get_weather()
    logging.info('weather results:',message,weather)
    obs_wind = weather.get_wind()
    obs_temp = weather.get_temperature('celsius')

    obs_reply = 'Current weather status in *'+true_location+': ' +str(weather.get_detailed_status())+'*.\nWind speed (km/h):\t*'+str(obs_wind['speed'])+'*. Temperature (C):\t*'+str(obs_temp['temp'])+'*'
    
    #current weather and forecast replies
    sendText(bot,message.chat_id,obs_reply)
    sendText(bot,message.chat_id,fore_reply)
    #location of weather report
    bot.sendLocation(message.chat_id,coor_lat,coor_lon)
    #send forecast graph
    postImage(imgPath,message.chat_id,BASE_URL) 
     

#calcuate the distance between two points on the surface of a sphere.
#returns true if distance of location two is within given radius from location two
#takes two sets of map coordinates and radius 
def haversine(lat1,lon1,lat2,lon2,radius):

    earth_radius = 6371
    theta1 = math.radians(lon1)
    theta2 = math.radians(lon2)
    
    phi1 = math.radians(90.- lat1)
    phi2 = math.radians(90.-lat2)
    
    c = cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1-theta2)+math.cos(phi1)*math.cos(phi2))
    d = math.acos(c)*earth_radius
    
    logging.info('location check. Distance: ',d )
    
    if d < radius:
        return d,True
    else:
        return d,False


    
#checks if user location is within the vicinity of location of interest
#currently checks is location is within 100m of particular gyms
def locCheck(bot,message): 

    lon = message.location.longitude
    lat = message.location.latitude
    try:
        gyms = yaml.load(open('catabase/gyms.yaml','rb'))
    except:
        gyms = []
        logging.error('No gym coordinates found')

    name = message.from_user.first_name

    for gym in gyms:
        d,in_radius = haversine(gym['lat'],gym['lon'],lat,lon,0.1)
        if in_radius:
            logging.info('in gym vicinity ',gym['lat'],gym['lon'],lat,lon)
            return sendText(bot,message.chat_id,'Good job on the gains at ' +gym['name']+' '+name+', I\'m proud of you')

 
#thank user
def thank(bot,chat_id,message):

    sendText(
            bot,chat_id,
            ' '.join([msgs['thanks'],str(message.from_user.first_name)]))

#greet user
def greet(bot,chat_id,message):
    sendText(
            bot,chat_id,
            ''.join([msgs['welcome1'],
                str(message.from_user.id),
                msgs['welcome2'],
                message.from_user.first_name]))


#say goodbye to users
def goodbye(bot,chat_id,message):
    sendText(bot,chat_id,"Daisy...daisy...") 


#echo user message to given chat id    
def echocats(bot,message):
    echo = message.text.split('/echo',1)[1]
    chat = yaml.load(open('catabase/echochat.yaml','rb'))
    try:
        sendText(bot,chat,echo)
    except:
        return logging.error('failed to echo message',message,echo,chat)


#get latest dota news post
def dotaNews(bot,message):

    payload={
            'appid':'570',  #dteam appid for dota2
            'count':'1',    #latest news post only
            'maxlength':'300' #maximum length of news summary for bot message
            }
    news = df.steamNews(payload)[0]
    
    logging.info(news)
    
    if not news:
        logging.error('No news items found in steam api request')
        return sendText(bot,message.chat_id,msgs['nonews'])
    
    header = '*Latest Dota 2 news post* ('+news['feedlabel']+')'
    
    try:
        return sendText(bot,message.chat_id,newsReply(header,news),True)
    except:
        logging.error('Couldn\'t parse: ',news)
 
#format news message for bot message
def newsReply(header,news):
    title = '\n*'+news['title']+'*'
    contents = news['contents']
    url = news['url']
    texts = [
            header,
            title,
            contents,
            '\nSee the rest of this post here:',
            url]
    reply = '\n'.join(texts)
    print reply
    return reply

#post new dota 2 patch
def postUpdate(bot,message):
    patch = df.getNewPatch()
    if patch:
        date = datetime.datetime.fromtimestamp(
            patch['date']
            ).strftime('%Y-%m-%d %H:%M')
                   
        header = '*NEW DOTA 2 PATCH!*'+date+''
        try:
            #using sendMessage as markdown can cause problems
            sendText(bot,message.chat_id,newsReply(header,patch),True)
        except:
            logging.error('Couldn\'t parse: ',patch)
        #update list of potentially unpatched players from the catabase
        cats = yaml.load(open('catabase/catabase.yaml','rb'))
        yaml.dump(cats,open('catabase/unpatched.yaml','wb'))

#checks if something has expired, e.g a dota event or the time between dota 2 update checking
def expiry(initial_time,dtime): #dtime in hours
    if datetime.datetime.now() > initial_time+datetime.timedelta(hours=dtime):
        return True

def msgTag(bot, message, name):
    user_name = message.from_user.first_name
    tagged_msg = {
            'time':         datetime.datetime.now(),
            'chat_id':      message.chat_id,
            'name':         name.lower(),
            'sender':       user_name,
            'sender_id':    message.from_user.id,
            'text':         message.text
            }
    sendText(bot,message.chat_id,user_name+msgs['tag_saved']) 
    return tagged_msg

#    try:
#        tags_list = yaml.load(open('catabase/tags.yaml','rb'))
#    except:
#        logging.warning('no tags.yaml found, creating new file')
#        tags_list = []
#
#    tags_list.append(tagged_msg)

def tagReply(bot,message,tag):
    user_name = message.from_user.first_name
    sendText(bot,message.chat_id,user_name+msgs['tag_reply'])
    sendText(bot,message.chat_id,'from: '+tag['sender']+' at '+tag['time'].strftime('%m-%d %H:%M')+'\n\n'+tag['text'])
    

