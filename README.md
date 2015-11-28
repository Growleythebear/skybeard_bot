# skybeard_bot
Telegram bot to organise events, dota nights and many other features.
If you are just a user, skip to the 'how to use' section

##Requirements
- Python 2.7+
- see requirements.txt

##Installation
Install the requirements with `pip install requirements.txt`
Then run `python setup.py` with either the install or develop option depending on what you would like to do

##Running
Run the bot like so:
```python skb_bot.py```

##How to use
###Bot commands and keywords
The commands currently available are:

Dota 2 database commands (the catabase)
* `/register <dota first name>, <dota last name>, www.dotabuff.com/players/<player_id> ` - Register your dota profile with Skybeard
* `/catabase` - show catabase entries that you have permission to see
* `delete cat <index>` deletes the database entry for the index you have specified.

Dota 2 events:
* `/dota` - creates a new dota event and precedes the specifed time after "at". E.g:
 * `/dota at 18:45`
 * `/dota at 1845`
 * `/dota` - will create dota event with default time (19:30)
* `delete dota` - will remove the current dota event
* `shotgun!` - Skybeard will know you wish to participate in the feeding
* `unshotgun!` - Remove yourself from the shotgun (and rdry) list.
* `rdry!` - Skybeard will know you are ready to feed imminently
* `unrdry!` - Remove yourself from the rdrys

Dota 2 related commands:
* `/topfeeds` - Poll the [Dota 2 API](http://dev.dota2.com/showthread.php?t=47115) for everyone's last 25 matches, giving rankings by total deaths
* `/lastmatch` - Poll the Dota 2 API for your last played match and link the DotaBuff page
* `/news` Gives the latest steam news post for Dota 2.    

* `/weather` - Gives the current weather and forecast from the [open weather map](http://openweathermap.org/) for a given location, e.g `/weather London,uk`
* `/movie` - Shows the general information, poster and plot summary for a given movie. e.g `/movie The Room`. Returns an [IMDb](http://www.imdb.com) search url for the title if it is not found in the [Open Movie Database](http://www.omdbapi.com/)

**Keywords**:
* I can be asked if there is a five stack in multiple ways, as well as if/when Dota is happening
* `show/give me spacecats` - Post pictures of cats in space
*  `gainz` - post motivational pictures of lifting
    
###The Catabase
The catabase is a simple database linking the Spacecat's Dota accounts to their telegram accounts. This allows the user to request information from the Dota 2 API without specifying any steam account or Dota 2 profile details with their requests.

To register on the database, the player must supply their preferred name, such as the one they are currently using in game (in a first name, last name format in the style of the Spacecat's Dota 2 names) and their [dotabuff](http://www.dotabuff.com) player profile page. This information is supplied with the registration command, comma separated like so:
```/register <dota first name>, <dota last name>, www.dotabuff.com/players/<player_id> ```

The list of database entries is viewable with the `/catabase` command. Users can delete their entries with `/delete cat <index>`.
The index is the first column of the database entries that are returned with `/catabase`

Users can only delete their own entries, unless they are a catabase admin. Admins of the bot server can added users to the bot admin list by editing the `admins.p` pickle file in python. Simply load the admins list and delete or append telegram user id's.

### Creating Dota 2 events


    
  





