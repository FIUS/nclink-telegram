from nclink.utilities import Nextcloud
from nclink.utilities import Helper
import nclink.config as config
import PythonTelegramWraper.bot as BotWrapper
import mail.mail as mail
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext.filters import Filters
from telegram.ext import CallbackQueryHandler


class Main:

    def __init__(self):
        self.nc = Nextcloud(config.url,config.user, config.password, config.base_dir)

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
            BotWrapper.modifyUser(int(inp), True)
            BotWrapper.sendMessage(inp, "You have been accepted")
            BotWrapper.sendMessage(chatID, "Request has been accepted")
        else:
            BotWrapper.sendMessage(chatID, "Request has been denied")

    def request(self, update, context):
        chatID = BotWrapper.chatID(update)

        if str(chatID) in BotWrapper.getUserData(): 

            incoming_message = update.message.text
            print("message from:",str(chatID),"->",incoming_message)
            
            msg = []
            if ";" not in incoming_message:
                msg = incoming_message.split()[1:]
            else:
                first_space = incoming_message.find(" ")
                msg = incoming_message[first_space+1:]
                msg = msg.split(";")

            BotWrapper.sendMessage(
                chatID, "Started searching for "+str(msg))

            exams,cached,fetched = self.nc.get_links(msg)

            for exam in exams:

                BotWrapper.sendMessage(chatID, str(
                    exam)+": " + str(exams[exam][0]), isHTML=True, no_web_page_preview=True)
            
            BotWrapper.sendMessage(chatID, "Cached Links: "+str(cached)+"\nNew Links: "+str(fetched), isHTML=True, no_web_page_preview=True)

    def resolve(self, update, context):
        chatID = BotWrapper.chatID(update)

        if str(chatID) in BotWrapper.getUserData():
            message_lines = update.message.text.split("\n")
            ticket_number = int(message_lines[0].split()[1])
            links = message_lines[1:]

            was_resolved=mail.resolveTicket(ticket_number, links)

            if was_resolved:
                BotWrapper.sendMessage(chatID,"Ticket "+str(ticket_number)+ " has been resolved")
            else:
                BotWrapper.sendMessage(chatID,"An error occured")




main = Main()

BotWrapper.addBotCommand("request", main.request)
BotWrapper.addBotCommand("r", main.request)
BotWrapper.addBotCommand("admin", main.admin)
BotWrapper.addBotCommand("resolve", main.resolve)
BotWrapper.botBackend.dispatcher.add_handler(
    CallbackQueryHandler(main.adminResponse))

BotWrapper.startBot()

