#wagerbot.py made using https://www.richwerks.com/index.php/2019/beginner-twitch-chatbot-using-python/
from twitchio.ext import commands
import random
from config import *
 
bot = commands.Bot(
    irc_token=TMI_TOKEN,
    client_id=CLIENT_ID,
    nick=BOT_NICK,
    prefix=BOT_PREFIX,
    initial_channels=CHANNEL
)
bookiename = 'pipsname'
openwagers = {}
confirmedwagers = {}
wagersloss = {}
wagerswon = {}
settings = {
  "userlimit": 0,  # 0 = Everyone can play, 1 = subscribed only, 2 = only mods can play
  "minbet": "20",
  "currency": "USD"
}

@bot.event
async def event_ready():
    print(f"{BOT_NICK} is online!")
    ws = bot._ws
 
@bot.event
async def event_message(ctx):
    if ctx.author.name.lower() == BOT_NICK.lower():
        return
    await bot.handle_commands(ctx)
    print(f'{ctx.channel} - {ctx.author.name}: {ctx.content}')
     
@bot.command(name='wager')
async def wager(ctx):
    global openwagers
    global settings
    userlevel = 0
    if ctx.author.name.is_subscriber == True:
        userlevel = 1
        if ctx.authorname.is_mod == True:
            userlevel = 2
    commandSplit = ctx.content.split(' ')
    if len(commandSplit) > 1 and commandSplit[1].isnumeric() and userlevel >= settings["userlimit"]:
        if ctx.author.name in openwagers:
            openwagers[ctx.author.name] = str(int(openwagers[ctx.author.name]) + int(commandSplit[1]))
            await ctx.channel.send(f"{ctx.author.name} adding another {commandSplit[1]} to their open wager for a total of {openwagers[ctx.author.name]} ! If this is too much for you please use the !wager remove command.")
        else:
            await ctx.channel.send(f"{ctx.author.name} wants to wager {commandSplit[1]} !")
            openwagers[ctx.author.name] = commandSplit[1]
    elif len(commandSplit) > 1 and commandSplit[1].lower() == 'remove':
        del openwagers[ctx.author.name]
        await ctx.channel.send(f"{ctx.author.name} removed their wager!")
    else:
        await ctx.channel.send(f"{ctx.author.name} to wager you need to show intent by typing !wager XX where XX is a number representing how much {settings[currency]} you want to wager. {settings[minimum]}{settings[currency]} minimum! Use !wager remove to remove your unbooked bet.  Once booked you are locked in unless the bookie says.")
        
@bot.command(name='bookie')
async def bookie(ctx):
    global bookiename
    if ctx.author.name == bookiename:
        global openwagers
        global confirmedwagers
        global wagerswon
        global wagersloss
        global settings
        commandSplit = ctx.content.split(' ')
        #list all users who want to wager
        if len(commandSplit) > 1 and commandSplit[1] == '#':
            await ctx.channel.send(f"Open bets {openwagers} confirmed bets {confirmedwagers} the bookie has won {wagerswon} and the bookie has loss {wagersloss} ")
        #book/confirm wager
        elif len(commandSplit) > 2 and commandSplit[1] == 'bet':
            if commandSplit[2] in confirmedwagers:
                confirmedwagers[commandSplit[2]] = str(int(openwagers[commandSplit[2]]) + int(confirmedwagers[commandSplit[2]]))
                del openwagers[commandSplit[2]]
                await ctx.channel.send(f"{commandSplit[2]} your bet for {confirmedwagers[commandSplit[2]]} is locked in!")
            else:
                confirmedwagers[commandSplit[2]] = openwagers[commandSplit[2]]
                del openwagers[commandSplit[2]]
                await ctx.channel.send(f"{commandSplit[2]} your bet for {confirmedwagers[commandSplit[2]]} is locked in!")
        #remove confirmed wager
        elif len(commandSplit) > 1 and commandSplit[1] == 'remove':
            del confirmedwagers[commandSplit[2]]
            await ctx.channel.send(f"The bookie has removed the wager for {commandSplit[2]} ")
        elif len(commandSplit) > 1 and commandSplit[1] == 'won':
            if commandSplit[2] in wagerswon:
                wagerswon[commandSplit[2]] = str(int(confirmedwagers[commandSplit[2]]) + int(wagerswon[commandSplit[2]]))
                del confirmedwagers[commandSplit[2]]
                await ctx.channel.send(f"You loss to the bookie {commandSplit[2]} .")
            else:
                wagerswon[commandSplit[2]] = confirmedwagers[commandSplit[2]]
                del confirmedwagers[commandSplit[2]]
                await ctx.channel.send(f"You loss {wagerswon[commandSplit[2]]} to the bookie {commandSplit[2]} .")
        elif len(commandSplit) > 1 and commandSplit[1] == 'loss':
            if commandSplit[2] in wagersloss:
                wagersloss[commandSplit[2]] = str(int(confirmedwagers[commandSplit[2]]) + int(wagersloss[commandSplit[2]]))
                del confirmedwagers[commandSplit[2]]
                await ctx.channel.send(f"You beat the bookie {commandSplit[2]} for {wagersloss[commandSplit[2]]} .")
            else:
                wagersloss[commandSplit[2]] = confirmedwagers[commandSplit[2]]
                del confirmedwagers[commandSplit[2]]
                await ctx.channel.send(f"You beat the bookie {commandSplit[2]} .")
        elif len(commandSplit) > 1 and commandSplit[1] == 'newbookie':
            bookiename = commandSplit[2]
            await ctx.channel.send(f"New bookie is {commandSplit[2]} ")
        elif len(commandSplit) > 1 and commandSplit[1] == 'delopen':
            openwagers = {}
            await ctx.channel.send(f"All open wagers have been removed")
        elif len(commandSplit) > 1 and commandSplit[1] == 'reset':
            openwagers = {}
            confirmedwagers = {}
            wagersloss = {}
            wagerswon = {}
            await ctx.channel.send(f"WagerBot has been reset")
        elif len(commandSplit) > 2 and commandSplit[1] == "mode":
            if commandSplit[2] == "mods":
                settings["userlimit"] = 2
                await ctx.channel.send(f"Wagers limited to mods only.")
            elif commandSplit[2] == "subs":
                settings["userlimit"] = 1
                await ctx.channel.send(f"Wagers limited to subscribers only.")
            elif commandSplit[2] == "all":
                settings["userlimit"] = 0
                await ctx.channel.send(f"Wagers open for everyone!")
        else:
            await ctx.channel.send(f"{ctx.author.name} to book a wager you need to confirm intent by typing !bookie bet NameOfPersonWagering or use !bookie # to list all wagers. Using !bookie won/loss NameOfPerson will move them to the won/loss against the bookie categories. !bookie delopen removes all open wagers. bookie reset will reset everything.")
    else:
       await ctx.channel.send(f"{ctx.author.name} you are not set as the bookie")
 
if __name__ == "__main__":
    bot.run()
