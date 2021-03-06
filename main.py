from nclink.utilities import Nextcloud
from nclink.utilities import Helper
import nclink.config as config
import PythonTelegramWraper.bot as BotWrapper
import mail.mail as mail
import constants
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext.filters import Filters
from telegram.ext import CallbackQueryHandler
import drinklist.drinks as drinks

class Main:

    def __init__(self):
        self.nc = Nextcloud(config.url,config.user, config.password, config.base_dir)#
        self.stats={}

    def admin(self, update, context):
        user = update.message.from_user
        chatID = BotWrapper.chatID(update)

        BotWrapper.sendMessage(chatID, "Request has been sent...")
        button_list = [
            InlineKeyboardButton("Ja", callback_data=chatID),
            InlineKeyboardButton("Nein", callback_data="no")
        ]
        reply_markup = InlineKeyboardMarkup(
            BotWrapper.build_menu(button_list, n_cols=1))
        message = '{} (@{}) wants to admin, accept request?'.format(
            user['first_name'], user['username'])
        BotWrapper.getBot().sendMessage(config.admin, message, reply_markup=reply_markup)

    def adminResponse(self, update, context):
        chatID = BotWrapper.chatID(update)
        try:
            BotWrapper.getBot().delete_message(chat_id=update.effective_chat.id,
                                               message_id=update.effective_message.message_id)
        except Exception as e:
            print(e)
        inp = str(update.callback_query.data)
        if inp is not "no":
            BotWrapper.modifyUser(int(inp), 'not_registred')
            BotWrapper.sendMessage(inp, "You have been accepted")
            BotWrapper.sendMessage(chatID, "Request has been accepted")
        else:
            BotWrapper.sendMessage(chatID, "Request has been denied")

    def request(self, update, context):
        chatID = BotWrapper.chatID(update)

        if str(chatID) in BotWrapper.getUserData():

            self.increase_stat_count('Requests: ')
            
            incoming_message = update.message.text
            print("message from:",str(chatID),"->",incoming_message)
            
            msg = []
            if ";" not in incoming_message:
                msg = incoming_message.split()[1:]
            else:
                first_space = incoming_message.find(" ")
                msg = incoming_message[first_space+1:]
                msg = msg.split(";")
                
                msgTemp=[]
                for bad_string in msg:
                    msgTemp.append(bad_string.strip())
                
                msg=msgTemp

            BotWrapper.sendMessage(
                chatID, "Started searching for "+str(msg))

            def cache_callback_function(message):
                BotWrapper.sendMessage(chatID, message)

            exams,cached,fetched = self.nc.get_links(msg,11,cache_callback=cache_callback_function)

            self.increase_stat_count("Exam Links generated: ",len(exams))
            self.increase_stat_count("Cached Links: ",cached)
            self.increase_stat_count("Non-Cached Links: ",fetched)

            for exam in exams:
                self.increase_stat_count(str(exam)+": ")
                BotWrapper.sendMessage(chatID, str(
                    exam)+": " + str(exams[exam][0]), isHTML=True, no_web_page_preview=True)
            
            BotWrapper.sendMessage(chatID, "Cached Links: "+str(cached)+"\nNew Links: "+str(fetched), isHTML=True, no_web_page_preview=True)

    def resolve(self, update, context):
        chatID = BotWrapper.chatID(update)

        if str(chatID) in BotWrapper.getUserData():
            message_lines = update.message.text.split("\n")
            ticket_number = int(message_lines[0].split()[1])
            links = message_lines[1:]

            if "en" in message_lines[0]:
                was_resolved=mail.resolveTicket(ticket_number, links, language="en")
            else:
                was_resolved=mail.resolveTicket(ticket_number, links)

            if was_resolved:
                self.increase_stat_count("Resolved with Bot: ")
                BotWrapper.sendMessage(chatID,"Ticket "+str(ticket_number)+ " has been resolved")
                def cache_callback_function(message):
                    BotWrapper.sendMessage(chatID, message)
                if BotWrapper.getUserData()[str(chatID)] != "not_registred":
                    drinks.order_drink(BotWrapper.getUserData()[str(chatID)],'Verleihticket',cache_callback_function)
                else:
                    BotWrapper.sendMessage(chatID, "Please register your username first with /username <username>")

            else:
                BotWrapper.sendMessage(chatID,"An error occured")

    def statistics(self, update, context):
        chatID = BotWrapper.chatID(update)
        if str(chatID) in BotWrapper.getUserData():

            message=""

            for key in self.stats:
                message+=str(key)+str(self.stats[key])+"\n"

            BotWrapper.sendMessage(chatID,message,isHTML=True)

    def help(self, update, context):
        chatID = BotWrapper.chatID(update)
        if str(chatID) in BotWrapper.getUserData():
            BotWrapper.sendMessage(chatID,constants.help_message)

    def increase_stat_count(self,stat,amount=1):
        if stat in self.stats:
            self.stats[stat]=self.stats[stat]+amount
        else:
            self.stats[stat]=amount
    
    def test_drink(self, update, context):
        chatID = BotWrapper.chatID(update)
        if str(chatID) in BotWrapper.getUserData():
            def cache_callback_function(message):
                BotWrapper.sendMessage(chatID, message)
            drinks.order_drink('schieljn','Verleihticket',cache_callback_function)
    
    def add_name(self, update, context):
        chatID = BotWrapper.chatID(update)
        if str(chatID) in BotWrapper.getUserData():
            username=update.message.text.split(" ")[1]
            BotWrapper.modifyUser(int(chatID), username)
            
            BotWrapper.sendMessage(chatID, "New username is: "+username)


main = Main()

BotWrapper.addBotCommand("request", main.request)
BotWrapper.addBotCommand("r", main.request)
BotWrapper.addBotCommand("admin", main.admin)
BotWrapper.addBotCommand("resolve", main.resolve)
BotWrapper.addBotCommand("stats", main.statistics)
BotWrapper.addBotCommand("help", main.help)
BotWrapper.addBotCommand("username", main.add_name)

BotWrapper.botBackend.dispatcher.add_handler(
    CallbackQueryHandler(main.adminResponse))

BotWrapper.startBot()

