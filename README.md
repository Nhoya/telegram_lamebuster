#  Telegram lamebuster bot

__**Actually this is a W.I.P. read the [TODO list](/TODO.md) for more info**__


A simple python bot to get rid of annoying flooders

## Overview

The purpose of this bot is to stop bad users and bots from flooding channels.

Each group will have a db structure composed by:
- Whitelist: the bot will ignore users in this list
- Bots Whitelist: by default, [due to  stupid Telegram policy](https://core.telegram.org/bots/faq#why-doesn-39t-my-bot-see-messages-from-other-bots), if you want to add a bot in your group it should be added to this list, otherwise lamebuster will kick them. 
- Banlist: all the users banned by lamebuster (useful for private groups where you can't actually ban)
- Filters: It define which 

## Dependencies

lamebuster needs [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) to work:

`pip3 install python-telegram-bot`


## Commands

-`/whitelist [add | remove]`
Will add or remove from whitelist  the user quoted by the message

-`/whitelist show`
Print whitelist

-`/setfilter [ TEXT | MEDIA | ALL ]`
Set the entities parsed. Can be text only  messages, media only (gif, photo, video, stickers) or everything

