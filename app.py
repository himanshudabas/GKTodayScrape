# flask telegram server for GK Today
import json
import logging
import os
import sys
import threading
import time
from datetime import datetime as dttm
import telegram
from flask import Flask, request
from telebot.credentials import bot_token, URL, owner_username
from scraping import app_folder
from telebot import APP_LOG_PATH, bot_welcome_msg, text_msg, send_file_msg

all_users = {}
LOG_PATH = os.path.expanduser(APP_LOG_PATH)
BOT_FOLDER = os.path.expanduser(app_folder)
GKTODAY_TELEBOT_USER_LIST = BOT_FOLDER + "users.json"
GKTODAY_TELEBOT_USER_STATE = BOT_FOLDER + "user_state.json"

TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app_metadata = {}
# TODO :: correctly save the user_state to the disk so that it can be recovered properly on the next run
user_state = {}  # this is to maintain previous 2 commands of users in order to serve the correct file


# occasionally read the app_metadata.json file in case a new file gets updated
def read_app_metadata_async():
    global app_metadata
    while True:
        logging.debug("[read_app_metadata_async] reading from disk")
        time.sleep(14400)
        try:
            f = open(BOT_FOLDER + "app_metadata.json", "r")
            app_metadata = json.loads(f.read())
            f.close()
        except FileNotFoundError:
            raise
        logging.debug("[read_app_metadata_async] Finished reading data to disk")

# initialize the directories
def make_directories():
    # to create the folder for docx and pdf files if they doesn't exist already
    logging.info("making directories")
    os.makedirs(BOT_FOLDER, exist_ok=True)
    os.makedirs(LOG_PATH, exist_ok=True)


# make custom keyboard
def make_keyboard(data):
    import math
    size = len(data)
    sqrt = round(math.sqrt(size))
    col = sqrt
    row = math.floor(size / sqrt)
    k_board = []
    count = 0
    for i in range(0, row):
        row_board = []
        for j in range(0, col):
            row_board.append(data[(i * col) + j])
            count += 1
        k_board.append(row_board)
    if not count == size:
        row_board = []
        for i in range(count, size):
            row_board.append(data[i])
        k_board.append(row_board)
    return k_board


# write data to the file
def write_data(path, data):
    try:
        logging.debug("Writing data to disk")
        os.makedirs(BOT_FOLDER, exist_ok=True)
        f = open(path, "w")
        f.write(data)
        f.close()
        logging.debug("Finished writing data to disk")

    except Exception:
        logging.info("Error occurred in write_data() at")
        raise


# this will remove the most recent call of a user from their user state
def remove_last_user_state(chat_id):
    global user_state
    logging.debug("[remove_last_user_state] removing last user state. i.e.: " + user_state[str(chat_id)][-1])
    user_state[str(chat_id)] = user_state[str(chat_id)][:-1]
    logging.debug("[remove_last_user_state] removed last user state.")

# this will write the user state to a file every 20 minutes
def write_user_state():
    global user_state
    while True:
        logging.debug("[user_state] Writing to disk")
        time.sleep(120)
        write_data(GKTODAY_TELEBOT_USER_STATE, json.dumps(user_state))
        logging.debug("[user_state] Finished writing data to disk")


# initialize the daily_quiz_metadata dictionary
def init_metadata():
    try:
        global all_users, user_state, app_metadata

        try:
            f = open(BOT_FOLDER + "app_metadata.json", "r")
            app_metadata = json.loads(f.read())
            f.close()
        except FileNotFoundError:
            raise

        try:
            f = open(GKTODAY_TELEBOT_USER_LIST, "r")
            all_users = json.loads(f.read())
            f.close()
        except FileNotFoundError:
            pass

        try:
            f = open(GKTODAY_TELEBOT_USER_STATE, "r")
            user_state = json.loads(f.read())
            f.close()
        except FileNotFoundError:
            pass
    except Exception:
        logging.info("Error occurred in open_daily_quiz_metadata() at")
        raise


# function to send broadcast to the users (will be running using thread)
def send_broadcast(all_user_chat_ids, msg, _chat_id, dlt=False):
    global all_users
    count = 0
    sent_to = 0

    for i in range(len(all_user_chat_ids)):
        try:
            result = bot.sendMessage(chat_id=all_user_chat_ids[i], text=msg)
            msg_id = result.message_id

            if dlt:
                time.sleep(0.1)
                bot.deleteMessage(chat_id=all_user_chat_ids[i], message_id=msg_id)
            sent_to += 1
            if i % 100 == 0:
                success = str(sent_to)
                success_msg = "Broadcast Update: \n\tSuccess: " + str(success) + "\n\tBlocked by: " + str(count)
                # send a confirmation message to the owner when the message is successfully broadcasted
                bot.sendMessage(chat_id=_chat_id, text=success_msg)

        except telegram.error.Unauthorized:
            count += 1
            all_users[all_user_chat_ids[i]]['blocked'] = True
            continue
        except telegram.error.TelegramError as err:
            print("Error While Broadcasting::::")
            print("user product_id:", all_user_chat_ids[i])
            print("error :::", err)
            continue

    # Final Success Message
    success = str(sent_to)
    success_msg = "Message broadcasted to " + str(success) + " users!\nBlocked by:" + str(
        count) + "\nclick /menu to go to the main menu"
    # send a confirmation message to the owner when the message is successfully broadcasted
    bot.sendMessage(chat_id=_chat_id, text=success_msg)


# https://github.com/python-telegram-bot/python-telegram-bot/issues/768#issuecomment-368349130
# split long message and send.
def send_message(_bot, _chat_id, text: str, **kwargs):
    # if len(text) <= telegram.constants.MAX_MESSAGE_LENGTH:
    #     bot.send_message(chat_id, text, **kwargs)
    parts = []
    while len(text) > 0:
        if len(text) > telegram.constants.MAX_MESSAGE_LENGTH:
            part = text[:telegram.constants.MAX_MESSAGE_LENGTH]
            first_lnbr: int = part.rfind('\n')
            if first_lnbr != -1:
                parts.append(part[:first_lnbr])
                text = text[first_lnbr:]
            else:
                parts.append(part)
                text = text[telegram.constants.MAX_MESSAGE_LENGTH:]
        else:
            parts.append(text)
            break

    for part in parts:
        _bot.send_message(_chat_id, part, **kwargs)
        time.sleep(1)


# this function will return a string which will be used
def update_user_state(chat_id, text):
    logging.debug("[update_user_state] chat id: "+ str(chat_id) + ". text: "+ text)
    global user_state
    user_state[str(chat_id)].append(text)
    logging.debug("after updating user state: " + " > ".join(user_state[str(chat_id)]))
    logging.debug("[update_user_state] Exiting chat id: "+ str(chat_id) + ". text: "+ text)

# whis function will empty the user state of the user with chat_id
def empty_current_user_state(chat_id):
    global user_state
    logging.debug("[empty_current_user_state] chat id: "+ str(chat_id))
    user_state[str(chat_id)] = []
    logging.debug("[empty_current_user_state] Exiting chat id: "+ str(chat_id))

# function to search the app_metadata and return the appropriate data
# RETURN:
#   target_dict, 1 : implies that we are returning a file
#   target_dict, 0 : implies that we are sending a list, which will be sent to the user as reply_markup
#   None, None : implies that user entered a wrong input
def search_app_md(target_dict, lst=None):
    if lst is None:
        lst = []
    if len(lst) == 0:
        res = []
        try:
            for key, _ in target_dict.items():
                res.append(key)
        except AttributeError:
            # means we have reached a file path, we need to return a file now.
            # at receiving end we will check the other value, i.e. True, True -> we need to send the file.
            return target_dict, 1
        # False -> this is a list
        return res, 0
    if lst[0] in target_dict:
        return search_app_md(target_dict[lst[0]], lst[1:])
    else:
        return None, None


# this function will search the user_state of the user with chat_id and return an appropriate reply
# RETURN:
#   -1 : error
# https://stackoverflow.com/a/366430
def get_next_choice(req_list=None, temp_list=None):
    if temp_list is None:
        temp_list = []
    # Error when req_list is empty
    if len(req_list) == 0:
        return search_app_md(app_metadata, temp_list)
    if req_list[0] == "/menu":
        return get_next_choice(req_list[1:])
    else:
        temp_list.append(req_list[0])
        return get_next_choice(req_list[1:], temp_list)


# function to send the users list to the owner, ASYNC
def send_user_list_to_owner(chat_id, text):
    if text.find("_list") != -1:
        count = 0
        all_users_details = ["[Name], [Username], [Phone], [Requests]"]
        msg = all_users_details[0] + "\n"

        for cur_id, user_details in all_users.items():
            count += 1
            _nm = user_details['name']
            if user_details['name'] is None:
                _nm = "_"
            _u_nm = user_details['username']
            if user_details['username'] is None:
                _u_nm = "_"

            try:
                _phn_num = user_details['phone_number']

                if user_details['phone_number'] is None:
                    _phn_num = "*"
            except KeyError:
                _phn_num = "*"
            try:
                _req = str(user_details['requests'])

                if user_details['requests'] is None:
                    _req = "-1"
            except KeyError:
                _req = "-1"
            all_users_details.append(_nm + ', ' + _u_nm + ', ' + _phn_num + ',' + _req)
            msg += _nm + ', ' + _u_nm + ', ' + _phn_num + ',' + _req + "\n"
        msg += "\nTotal : " + str(count)

    # only return the users count
    else:
        msg = "Total Users: "
        msg += str(len(all_users))
    try:
        send_message(bot, chat_id, msg)
    except Exception as ex:
        msg = "There was an error, please check bot log." + str(ex)
        bot.sendMessage(chat_id=chat_id, text=msg)


# wrapper function to send the broadcast to all users
def send_broadcast_wrapper(chat_id, text):
    msg = text.replace("/broadcast ", "")
    dlt = False
    if msg.find("&del& ") == 0:
        msg = msg.replace("&del& ", "")
        dlt = True

    msg = "Owner: \n\n" + msg
    all_user_chat_ids = []

    for cur_id, user_details in all_users.items():
        if user_details['username'] != "BaapuJi":
            try:
                if not user_details['blocked']:
                    all_user_chat_ids.append(cur_id)
            except KeyError:
                all_users[cur_id]['blocked'] = False
                all_user_chat_ids.append(cur_id)

    # this is done so that the telegram webhook doesn't keep sending us the same
    # command again and again
    broadcast_thread = threading.Thread(target=send_broadcast, args=(all_user_chat_ids, msg, chat_id, dlt,))
    broadcast_thread.start()


# function to send the main menu to the user
def send_main_menu(chat_id, user_name):
    choice = """
    Please select Quiz or Magazine
    """
    # send the custom keyboard with available years as option
    empty_current_user_state(chat_id)
    update_user_state(chat_id, "/menu")
    custom_keyboard = make_keyboard(['Quiz', 'Magazine'])
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    try:
        bot.send_message(chat_id=chat_id, text=choice, reply_markup=reply_markup)
    except telegram.error.Unauthorized:
        logging.info("bot is blocked by \nUSERNAME:", user_name, "\nCHATID: ", str(chat_id))


# start menu for first time users
def send_start_menu(chat_id, user_name):
    # initialize the welcoming message
    start_msg = bot_welcome_msg.format(owner_username.lower())
    # send the welcoming message
    try:
        bot.sendMessage(chat_id=chat_id, text=start_msg, parse_mode=telegram.ParseMode.MARKDOWN_V2)
    except telegram.error.Unauthorized:
        logging.info("bot is blocked by \nUSERNAME:", user_name, "\nCHATID: ", str(chat_id))
    send_main_menu(chat_id, user_name)


# function which sends the main menu when user enters a wrong input
def send_wrong_input(chat_id, user_name):
    incorrect = "Incorrect Option! Please Try Again. Press /menu to go to the main menu"
    try:
        bot.sendMessage(chat_id=chat_id, text=incorrect)
    except telegram.error.Unauthorized:
        logging.info("bot is blocked by \nUSERNAME:", user_name, "\nCHATID: ", str(chat_id))

    send_main_menu(chat_id, user_name)


# update the user_details in the all_users
def update_user_details(chat_id, name, user_name, phn_num):
    if str(chat_id) not in all_users:
        all_users[str(chat_id)]['users_start_date'] = str(dttm.now())
    all_users[str(chat_id)]['name'] = name
    all_users[str(chat_id)]['username'] = user_name
    all_users[str(chat_id)]['phone_number'] = phn_num
    all_users[str(chat_id)]['blocked'] = False
    # this is to keep the count of requests made by a particular user
    try:
        reqs = all_users[str(chat_id)]['requests']
    except KeyError:
        # when this is the first request by the user
        reqs = 0
    all_users[str(chat_id)]['requests'] = str(int(reqs) + 1)
    write_data(GKTODAY_TELEBOT_USER_LIST, json.dumps(all_users))


# This function automatically finds the correct menu/file to send and also handles wrong inputs
def find_and_send_correct_menu(chat_id, user_name, text):
    update_user_state(chat_id, text)
    msg_list, is_file = get_next_choice(user_state[str(chat_id)])

    if isinstance(msg_list, list):
        custom_keyboard = make_keyboard(msg_list)
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        try:
            bot.send_message(chat_id=chat_id, text=text_msg, reply_markup=reply_markup)
        except telegram.error.Unauthorized:
            logging.info("bot is blocked by \nUSERNAME:", user_name, "\nCHATID: ", str(chat_id))

    # received a file path, need to send the file to the user
    elif isinstance(msg_list, str) and is_file:
        remove_last_user_state(chat_id)
        file_path = msg_list
        try:
            bot.send_message(chat_id=chat_id, text=send_file_msg)
            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
            bot.send_document(chat_id=chat_id, document=open(file_path, 'rb'))

        except telegram.error.Unauthorized:
            logging.info("bot is blocked by \nUSERNAME:", user_name, "\nCHATID: ", str(chat_id))
        pass

    # user selected the wrong option
    elif msg_list is None and is_file is None:
        send_wrong_input(chat_id, user_name)
    else:
        raise


make_directories()
init_metadata()
maintenance = False
# this is to set logging to error mode
# _log_level = logging.DEBUG
_log_level = logging.INFO
_log_file_path = LOG_PATH + "app.log"
if _log_level == 10:
    _log_file_path = LOG_PATH + "app_debug.log"

logger = logging.getLogger()
logger.setLevel(_log_level)
file_handler = logging.FileHandler(_log_file_path)
file_handler.setLevel(_log_level)
formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

x = threading.Thread(target=write_user_state)
x.start()
# start the flask app
app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    global all_users, user_state
    chat_id = ""
    msg = update.message
    logging.debug(msg)
    if msg is None:
        msg = update.edited_message

    try:
        chat_id = msg.chat.id
    except KeyError:
        logging.debug("error in chatid = msg.chat.product_id::::")
        logging.debug("update::")
        logging.debug(update)
        logging.debug("msg::")
        logging.debug(msg)

    # proceed if chat is null
    if chat_id is not None:
        # Telegram understands UTF-8, so encode text for unicode compatibility
        text = ""
        try:
            if msg.text is not None:
                text = msg.text.encode('utf-8').decode()
            else:
                text = "/menu"
        except AttributeError as err:
            logging.debug(err)

        first = msg.from_user.first_name
        last = msg.from_user.last_name
        if msg.contact is not None and msg.contact.phone_number is not None:
            phn_num = msg.contact.phone_number
        else:
            phn_num = None
        if first is None:
            first = " "
        if last is None:
            last = " "
        name = first + " " + last
        user_name = msg.from_user.username
        if user_name is None:
            user_name = "_"

        global maintenance

        # This shows the users of the bot that it is currently under maintenance
        if maintenance and user_name != owner_username:
            msg = "This BOT is currently under maintenance! Please try again later, if the problem persists contact " \
                  "the owner at @baapuji "
            try:
                bot.sendMessage(chat_id=chat_id, text=msg)
            except telegram.error.Unauthorized:
                logging.info("bot is blocked by \nUSERNAME:", user_name, "\nCHATID: ", str(chat_id))
            return 'ok'

        # This toggles the maintenance status of the bot
        if text.find("/maintenance") == 0 and user_name == owner_username:
            maintenance = not maintenance
            msg = "Maintenance Status : " + str(maintenance)
            bot.sendMessage(chat_id=chat_id, text=msg)
            return 'ok'

        try:
            if str(chat_id) not in user_state:
                empty_current_user_state(chat_id)
            if all_users[str(chat_id)] is not None:
                pass
        except KeyError:
            all_users[str(chat_id)] = {}
            empty_current_user_state(chat_id)
            # new user
            logging.info("[NEW USER] chat id :" + str(chat_id))

        # When bot is not under maintenance or if it's under maintenance but owner is sending request
        # Owner can access the bot even when it's under maintenance
        if not maintenance or user_name == owner_username:
            update_user_details(chat_id, name, user_name, phn_num)
            # testing
            if user_name is None:
                logging.debug("Username is NONE")
            if name is None:
                logging.debug("name is NONE")
            if chat_id is None:
                logging.debug("chat_id is NONE")
            if text is None:
                logging.debug("text is NONE")
            try :
                print(dttm.now(), "->", user_name, "->", name, "->", str(chat_id), "->", text)
                logging.info(user_name + " -> " + name + " -> " + str(chat_id) +  " -> " + text)
            except TypeError:
                logging.info(str(chat_id) + str(msg))
                raise TypeError

            # when the owner wants to broadcast the a message to all it's active users
            if text.find("/broadcast ") == 0 and user_name == owner_username:
                send_broadcast_wrapper(chat_id, text)

            # when the owner wants to get the user list
            elif text.find("/users") == 0 and user_name == owner_username:
                send_user_list_to_owner(chat_id, text)

            # when user joins the bot for the first time
            elif text == "/start":
                send_start_menu(chat_id, user_name)

            # when user request for the main menu
            elif text == "/menu":
                send_main_menu(chat_id, user_name)

            # when user thanks the Bot
            elif text.lower().find("thank") != -1:
                msg = "स्वागतम् ❤️"
                try:
                    bot.send_message(chat_id=chat_id, text=msg)
                except telegram.error.Unauthorized:
                    logging.info("bot is blocked by \nUSERNAME:", user_name, "\nCHATID: ", str(chat_id))
                send_main_menu(chat_id, user_name)

            # for all other options that user enters
            else:
                find_and_send_correct_menu(chat_id, user_name, text)
            # to flush the stdout to nohup log file
            sys.stdout.flush()
            # this stops the telegram server from repeatedly sending the same request to our webhook
            return 'ok'


# call https://example.com/setwebhook to start your webhook
@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    # shows the following messages in the browser
    if s:
        return "Webhook setup Successful!"
    else:
        return "Webhook setup Failed!"


@app.route('/')
def index():
    # if your VPS has open ports for all IPs then this will be shown if you
    # open your website (https://example.com/) in the browser
    return 'Server is Working'


if __name__ == '__main__':


    # note the threaded arg which allow
    # your app to have more than one thread
    app.run(threaded=True, port=8000)
