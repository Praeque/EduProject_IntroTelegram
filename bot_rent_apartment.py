import math
import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import json
import datetime
import calendar
from math import ceil

bot = telebot.TeleBot('5378831917:AAFEesUktOsPqVrijR0ArA2l8XXmZftcQwc')


def main_menu(message):

    create_user_handler(message)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    menu = ['Search apartments', 'Add my apartment', 'My booking','Update balance']
    markup.add(*menu)
    bot.send_message(message.from_user.id, '<b><i>Welcome to main menu!</i></b>', reply_markup=markup, parse_mode='html')
    bot_handler[message.from_user.id]['menu'] = {'Search apartments': search_apartments,
                           'Add my apartment': add_my_apartment,
                           'Update balance': update_balance, 'My booking': My_booking}


def create_user_handler(message):
    if message.from_user.id in new_apartment:
        if'photos' in new_apartment[message.from_user.id]:
            if len(new_apartment[message.from_user.id]['photos']):
                remove_photos(message)
    with open('data/users_id.json', 'r') as file_users:
        data_users = json.load(file_users)
    print(str(message.from_user.id))
    balance = data_users[str(message.from_user.id)]['balance']
    new_apartment[message.from_user.id] = {'address': None, 'price': None, 'photos': [],
                     "start_date": None, "finish_date": None, 'phone_number': None, "name_hostess": None}
    bot_handler[message.from_user.id] = {'get_info_from_user': False, 'function_after_get_info': main_menu,
                   'menu': {'Go to main menu': main_menu},
                   'Back': main_menu, 'current_function': None, 'save_info_in': None,
                   'argument_for_save': None, 'function_before_get_photo': None,
                   'function_after_get_photo': None, 'text_expected': False, 'photo_expected': False,
                   'function_get_info': None, 'checking_info': False, 'searching_month': None,
                                    'addresses_of_selected_month': [], 'last_id': message.from_user.id,
                                    'count_shows_rents': 0, 'data_apartments': None, 'step_search': 4,
                                    'list_calendar': [], 'head_calendar': [], 'dates_list': [],
                                    'selected_address': None, 'buy_days': [], 'call_data_expected': False,
                                    'balance': balance, 'total_cost': 0}


def search_apartments(message):
    bot_handler[message.from_user.id]['call_data_expected'] = False
    bot_handler[message.chat.id]['text_expected'] = True
    bot_handler[message.chat.id]['count_shows_rents'] = 4
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton('Go to main menu'))
    bot_handler[message.chat.id]['menu'] = {'Go to main menu': main_menu}
    notice = '<b>Enter the month in which you want to rent out the property:</b>\n<i>In format  <u>2022.10</u></i>'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')
    bot_handler[message.chat.id]['save_info_in'] = bot_handler
    bot_handler[message.chat.id]['argument_for_save'] = 'searching_month'
    bot_handler[message.chat.id]['function_after_get_info'] = show_apartments
    bot_handler[message.chat.id]['function_get_info'] = search_apartments
    bot_handler[message.chat.id]['correct_input'] = check_input_for_search_apartments


def check_input_for_search_apartments(message):
    try:
        month = [int(i) for i in message.text.split('.')]
        if datetime.date(*month, calendar.monthrange(*month)[1]) < datetime.date.today():
            notice = '<b>You cannot specify a month from the past! \U0001F605</b>'
            bot.send_message(message.from_user.id, notice, parse_mode='html')
            return False
        with open('apartments/apartments.json', 'r') as file_apartment:
            data_apartment = json.load(file_apartment)
        for address in data_apartment:
            if message.text in data_apartment[address]['available days']:
                return True
        bot.send_message(message.from_user.id, f'<b>Announcement for {message.text} not found!</b>', parse_mode='html')
        return False
    except Exception as error:
        bot.send_message(message.from_user.id, '<b>Incorrect date of month</b>', parse_mode='html')
        return False


def show_apartments(message):
    bot_handler[message.chat.id]['text_expected'] = False
    markup_for_bring_apartments(message)
    find_apartment_selected_date(message)
    bring_apartments(message)


def markup_for_bring_apartments(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('Show this page again', 'Back to select date')
    markup.add('Go to main menu')
    bot_handler[message.chat.id]['menu'] = {'Show this page again': bring_apartments,
                                            'Back to select date': search_apartments,
                                            'Go to main menu': main_menu}
    notice = f'<b>Announcements for the</b> <u>{bot_handler[message.chat.id]["searching_month"]}</u>:'
    bot.send_message(message.from_user.id, notice, reply_markup=markup, parse_mode='html')


def bring_apartments_more(message):
    bot_handler[message.from_user.id]['count_shows_rents'] += bot_handler[message.from_user.id]['step_search']
    if bot_handler[message.from_user.id]['count_shows_rents'] >\
            len(bot_handler[message.from_user.id]['addresses_of_selected_month']):
        bot_handler[message.from_user.id]['count_shows_rents'] =\
            len(bot_handler[message.from_user.id]['addresses_of_selected_month'])
    bring_apartments(message)


def bring_apartments_less(message):
    bot_handler[message.from_user.id]['count_shows_rents'] -= bot_handler[message.from_user.id]['step_search']
    if bot_handler[message.from_user.id]['count_shows_rents'] < bot_handler[message.from_user.id]['step_search']:
        bot_handler[message.from_user.id]['count_shows_rents'] = bot_handler[message.from_user.id]['step_search']
    bring_apartments(message)


def bring_apartments(message):
    bot_handler[message.from_user.id]['call_data_expected'] = True
    data_apartments = bot_handler[message.from_user.id]['data_apartments']
    found_addresses = bot_handler[message.from_user.id]['addresses_of_selected_month']
    count_show_apartments = bot_handler[message.from_user.id]['count_shows_rents']
    step = bot_handler[message.from_user.id]['step_search']
    if count_show_apartments > len(found_addresses):
        step -= count_show_apartments - len(found_addresses)
        count_show_apartments = len(found_addresses)
    for address in found_addresses[count_show_apartments-step:count_show_apartments]:
        show_add(message, address, data_apartments)
    show_inline_keyboard(message, step, count_show_apartments, found_addresses)


def show_add(message, address, data_apartments):
    price = data_apartments[address]['price']
    name_hostess = data_apartments[address]['name_hostess']
    phone_number = data_apartments[address]['phone_number']
    notice = f"""<b>Address:</b>  <i>{address}</i>\n<b>Price</b>:  <i>{price} UAH / per day</i>\n
<b>Phone number:</b>  <i>{phone_number}</i>\n<b>Name of hostess:</b>  {name_hostess}"""
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text='Show main photo', callback_data=address + '*_*show_photo_mein')
    button2 = InlineKeyboardButton(text='Show all photos', callback_data=address + '*_*show_photo_all')
    markup.add(button1, button2)
    markup.add(InlineKeyboardButton(text='View available dates for rent', callback_data=address + '*_*view_dates'))
    bot.send_message(message.from_user.id, notice, parse_mode='html', reply_markup=markup)


def view_available_dates(call):
    address = call.data.split('*_*')[0]
    bot_handler[call.from_user.id]['selected_address'] = address
    month = bot_handler[call.from_user.id]['searching_month']
    empty_days, day_in_month = calendar.monthrange(*[int(i) for i in month.split('.')])
    data_apartments = bot_handler[call.from_user.id]['data_apartments']
    dates_list = data_apartments[address]['available days'][month].split(',')
    bot_handler[call.from_user.id]['dates_list'] = dates_list
    max_button = math.ceil((empty_days + day_in_month)/7) * 7
    empty_days_in_the_end = max_button - empty_days - day_in_month
    markup = InlineKeyboardMarkup(row_width=7)
    head = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    head_buttons = []
    for i in head:
        head_buttons.append(InlineKeyboardButton(text=i, callback_data=' '))
    bot_handler[call.from_user.id]['head_calendar'] = head_buttons
    markup.add(*head_buttons)
    list_of_buttons = []
    for empty in range(empty_days):
        list_of_buttons.append(' ')
    for day in range(1, day_in_month+1):
        if str(day) in dates_list:
            list_of_buttons.append(day)
        else:
            list_of_buttons.append('*')
    for empty in range(empty_days_in_the_end):
        list_of_buttons.append(' ')
    bot_handler[call.from_user.id]['list_calendar'] = list_of_buttons
    list_of_inline_buttons = []
    for day in list_of_buttons:
        list_of_inline_buttons.append(InlineKeyboardButton(text=day, callback_data=day))
    markup.add(*list_of_inline_buttons)
    markup.add(InlineKeyboardButton(text='Selected:  0 days  /  0  cost', callback_data=' '))
    notice = '<b>Click on the dates witch you want to rent:</b>'
    bot.send_message(call.from_user.id, notice, reply_markup=markup, parse_mode='html')
    notice =f'            <b>Yor balance:  {bot_handler[call.from_user.id]["balance"]}</b>          ' \
            f'       <i>Selected month: {bot_handler[call.from_user.id]["searching_month"]}</i>'
    bot.send_message(call.from_user.id, notice, parse_mode='html')
    notice = '\U0000203C<b>Removing a booking you get back only <u>90%</u> of the money!</b>\U0000203C'
    bot.send_message(call.from_user.id, notice, parse_mode='html')


def show_inline_keyboard(message, step, count_show_apartments, found_addresses):
    if count_show_apartments > step and len(found_addresses) <= count_show_apartments:
        previous_page(message, step, count_show_apartments, found_addresses)
    elif len(found_addresses) > count_show_apartments and count_show_apartments <= step:
        next_page(message, step, count_show_apartments, found_addresses)
    elif count_show_apartments > step and len(found_addresses) > count_show_apartments:
        previous_and_next_page(message, step, count_show_apartments, found_addresses)
    else:
        no_pages(message, step, count_show_apartments, found_addresses)


def previous_page(message, step, count_show_apartments, found_addresses):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Previous page', callback_data='less_apartments'))
        notice = f'<b>Page</b>: {ceil(count_show_apartments/step)} / {ceil(len(found_addresses)/step)}'
        bot.send_message(message.from_user.id, notice, parse_mode='html', reply_markup=markup)


def next_page(message, step, count_show_apartments, found_addresses):
        markup = InlineKeyboardMarkup(row_width=1)
        button = InlineKeyboardButton(text='Next page', callback_data='more_apartments')
        markup.add(button)
        notice = f'<b>Page</b>: <i>{ceil(count_show_apartments / step)} / {ceil(len(found_addresses) / step)}</i>'
        bot.send_message(message.from_user.id, notice, parse_mode='html', reply_markup=markup)


def previous_and_next_page(message, step, count_show_apartments, found_addresses):
        markup = InlineKeyboardMarkup(row_width=2)
        button1 = InlineKeyboardButton(text='Previous page', callback_data='less_apartments')
        button2 = InlineKeyboardButton(text='Next page', callback_data='more_apartments')
        markup.add(button1, button2)
        notice = f'<b>Page</b>: <i>{ceil(count_show_apartments / step)} / {ceil(len(found_addresses) / step)}</i>'
        bot.send_message(message.from_user.id, notice, parse_mode='html', reply_markup=markup)


def no_pages(message, step, count_show_apartments, found_addresses):
        notice1 = f'<b>Page</b>: <i>{ceil(count_show_apartments / step)} / {ceil(len(found_addresses) / step)}</i>'
        notice2 = '\n<b>That`s all on this month</b>'
        bot.send_message(message.from_user.id, notice1 + notice2, parse_mode='html')


def find_apartment_selected_date(message):
    bot_handler[message.chat.id]['addresses_of_selected_month'] = []
    month = '.'.join([str(int(i)) for i in bot_handler[message.chat.id]['searching_month'].split('.')])
    with open('apartments/apartments.json', 'r') as file_apartments:
        data_apartments = json.load(file_apartments)
        bot_handler[message.chat.id]['data_apartments'] = data_apartments
    for address in data_apartments:
        print(address)
        if month in data_apartments[address]['available days']:
            bot_handler[message.chat.id]['addresses_of_selected_month'].append(address)






def add_my_apartment(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton('I agree'), KeyboardButton('Go to main menu'))
    warning = '''<b>The data will be processed by the bot
And will be visible to other users.\nAre you agree?</b>'''
    bot.send_message(message.chat.id, warning, reply_markup=markup, parse_mode='html')
    bot_handler[message.chat.id]['menu'] = {'Go to main menu': main_menu, 'I agree': get_address}
    bot_handler[message.chat.id]['save_info_in'] = new_apartment
    bot_handler[message.chat.id]['argument_for_save'] = 'address'
    bot_handler[message.chat.id]['function_after_get_info'] = get_price
    bot_handler[message.chat.id]['function_get_info'] = get_address
    bot_handler[message.chat.id]['correct_input'] = check_input_address







def get_address(message):
    bot_handler[message.chat.id]['text_expected'] = True
    bot_handler[message.chat.id]['menu'] = {'Go to main menu': main_menu, 'Back': add_my_apartment}
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['menu']['Back'] = checking_info
    markup_for_get_address(message)
    bot_handler[message.chat.id]['save_info_in'] = new_apartment
    bot_handler[message.chat.id]['argument_for_save'] = 'address'
    bot_handler[message.chat.id]['function_after_get_info'] = get_price
    bot_handler[message.chat.id]['function_get_info'] = get_address
    bot_handler[message.chat.id]['correct_input'] = check_input_address
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['function_after_get_info'] = checking_info


def check_input_address(message):
    with open('apartments/apartments.json', 'r') as file_apartments:
        data_apartments = json.load(file_apartments)
    if message.text in data_apartments:
        bot.send_message(message.chat.id, '<b>This address already exists!</b>', parse_mode='html')
        return False
    if is_exists_cyrillic(message.text):
        bot.send_message(message.chat.id, '<b>Expected only latin!</b>', parse_mode='html')
        return False
    if len(message.text) < 9:
        notice = '<b>address should be longer!\nFor understanding were is it</b>'
        bot.send_message(message.chat.id, notice, parse_mode='html')
        return False
    return True


def is_exists_cyrillic(text):
    letters_ru = u'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    for s in text:
        if s in letters_ru:
            return True
    return False


def markup_for_get_address(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if new_apartment[message.chat.id]['address']:
        if not bot_handler[message.chat.id]['checking_info']:
            markup.add('Continue')
            bot_handler[message.chat.id]['menu']['Continue'] = get_price
        notice = f'Your address:\n{new_apartment[message.chat.id]["address"]}' \
                 f'\nyou can enter a new one or continue with this'
        bot.send_message(message.chat.id, notice)
    markup.add('Back', 'Go to main menu')
    notice = '<b>Enter the address of your apartment:</b>' \
             '\n<i>(Make sure your apartment can be found at this address)</i>'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')


def get_price(message):
    bot_handler[message.chat.id]['text_expected'] = True
    bot_handler[message.chat.id]['photo_expected'] = False
    bot_handler[message.chat.id]['menu'] = {'Go to main menu': main_menu, 'Back': add_my_apartment}
    markup_for_get_price(message)
    bot_handler[message.chat.id]['save_info_in'] = new_apartment
    bot_handler[message.chat.id]['argument_for_save'] = 'price'
    bot_handler[message.chat.id]['function_after_get_info'] = photo_expected
    bot_handler[message.chat.id]['function_after_get_photo'] = get_start_date
    bot_handler[message.chat.id]['function_before_get_photo'] = get_price
    bot_handler[message.chat.id]['function_get_info'] = get_price
    bot_handler[message.chat.id]['correct_input'] = check_input_price
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['function_after_get_info'] = checking_info


def check_input_price(message):
    try:
        if int(message.text) >= 0:
            return True
        else:
            notice = '<b>The price cannot be less than zero!\n' \
                     'I don`t think you want to give money instead of taking</b> \U0001F605 \U0001F602'
    except ValueError:
        notice = '<b>Price must contain only numbers!</b>'
    bot.send_message(message.chat.id, notice, parse_mode='html')
    return False


def markup_for_get_price(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if new_apartment[message.chat.id]['price']:
        if not bot_handler[message.chat.id]['checking_info']:
            markup.add('Continue')
            bot_handler[message.chat.id]['menu']['Continue'] = photo_expected
        if bot_handler[message.chat.id]['checking_info']:
            bot_handler[message.chat.id]['menu']['Continue'] = checking_info
        notice = f'Your price:\n{new_apartment[message.chat.id]["price"]}\nyou can enter a new one or continue with this'
        bot.send_message(message.chat.id, notice)
    markup.add('Back', 'Go to main menu')
    bot_handler[message.chat.id]['menu']['Back'] = get_address
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['menu']['Back'] = checking_info
    notice = '<b>Enter rental price for 1 day? <u>(UAH)</u></b>\n<i>(excluding commission)</i>'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')


def get_start_date(message):
    bot_handler[message.chat.id]['photo_expected'] = False
    bot_handler[message.chat.id]['text_expected'] = True
    markup_for_get_start_date(message)
    bot_handler[message.chat.id]['save_info_in'] = new_apartment
    bot_handler[message.chat.id]['argument_for_save'] = 'start_date'
    bot_handler[message.chat.id]['function_after_get_info'] = get_finish_date
    bot_handler[message.chat.id]['function_get_info'] = get_start_date
    bot_handler[message.chat.id]['correct_input'] = check_input_start_date
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['function_after_get_info'] = checking_info


def check_input_start_date(message):
    try:
        date_input = [int(i) for i in (message.text).split('.')]
        if datetime.date(*date_input) > datetime.date.today():
            return True
        else:
            notice = '<b>You cannot specify a date from the past!</b>'
    except Exception:
        notice = '<b>Incorrect format</b>'
    bot.send_message(message.chat.id, notice, parse_mode='html')
    return False


def markup_for_get_start_date(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if new_apartment[message.chat.id]['start_date']:
        if not bot_handler[message.chat.id]['checking_info']:
            markup.add('Continue')
            bot_handler[message.chat.id]['menu']['Continue'] = get_finish_date
        notice = f'Specified <i>start date</i> of the rent:\n{new_apartment[message.chat.id]["start_date"]}' \
                 f'\nyou can enter a new one or continue with this'
        bot.send_message(message.chat.id, notice,parse_mode='html')
    markup.add('Back', 'Go to main menu')
    bot_handler[message.chat.id]['menu']['Back'] = photo_expected
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['menu']['Back'] = checking_info
    notice = '<b>Enter the <i>date from which you are ready to rent</i> out apartment in the format:</b>\n<i>2022.10.09</i>'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')


def get_finish_date(message):
    bot_handler[message.chat.id]['text_expected'] = True
    markup_for_get_finish_date(message)
    bot_handler[message.chat.id]['save_info_in'] = new_apartment
    bot_handler[message.chat.id]['argument_for_save'] = 'finish_date'
    bot_handler[message.chat.id]['function_after_get_info'] = get_phone_number
    bot_handler[message.chat.id]['function_get_info'] = get_finish_date
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['function_after_get_info'] = checking_info
    bot_handler[message.chat.id]['correct_input'] = check_input_finish_date


def check_input_finish_date(message):
    try:
        date_input = [int(i) for i in message.text.split('.')]
        date_start = [int(i) for i in new_apartment[message.chat.id]['start_date'].split('.')]
        print((datetime.date(*date_input) - datetime.date(*date_start)).days)
        if datetime.date(*date_input) < datetime.date(*date_start):
            notice = '<b>The end date of the rent cannot be earlier than the start of the rent!</b>'
        elif (datetime.date(*date_input) - datetime.date(*date_start)).days < 30:
            notice = '<b>You cannot rent out housing for less than a month!</b>'
        else:
            return True
    except Exception:
        notice = '<b>Incorrect format</b>'
    bot.send_message(message.chat.id, notice, parse_mode='html')
    return False


def markup_for_get_finish_date(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if new_apartment[message.chat.id]['finish_date']:
        if not bot_handler[message.chat.id]['checking_info']:
            markup.add('Continue')
            bot_handler[message.chat.id]['menu']['Continue'] = get_phone_number
        notice = f'Specified <i>finish date</i> of the rent:\n{new_apartment[message.chat.id]["finish_date"]}' \
                 f'\nyou can enter a new one or continue with this'
        bot.send_message(message.chat.id, notice, parse_mode='html')
    markup.add('Back', 'Go to main menu')
    bot_handler[message.chat.id]['menu']['Back'] = get_start_date
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['menu']['Back'] = checking_info
    notice = '<b>Enter the <i>date until which you can rent</i> out the apartment in the format:</b>\n<i>2022.10.09</i>'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')


def get_phone_number(message):
    bot_handler[message.chat.id]['text_expected'] = True
    markup_for_get_phone_number(message)
    bot_handler[message.chat.id]['save_info_in'] = new_apartment
    bot_handler[message.chat.id]['argument_for_save'] = 'phone_number'
    bot_handler[message.chat.id]['function_after_get_info'] = get_name_hostess
    bot_handler[message.chat.id]['function_get_info'] = get_phone_number
    bot_handler[message.chat.id]['correct_input'] = check_input_phone_number


def check_input_phone_number(message):
    try:
        int(message.text)
        if message.text[:3] == '380' and len(message.text) == 12:
            return True
    except Exception:
        pass
    bot.send_message(message.chat.id, '<b>Incorrect number</b>', parse_mode='html')


def markup_for_get_phone_number(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if new_apartment[message.chat.id]['phone_number']:
        if not bot_handler[message.chat.id]['checking_info']:
            markup.add('Continue')
            bot_handler[message.chat.id]['menu']['Continue'] = get_name_hostess
        notice = f'Specified number:\n{new_apartment[message.chat.id]["phone_number"]}' \
                 f'\nyou can enter a new one or continue with this'
        bot.send_message(message.chat.id, notice)
    markup.add('Back', 'Go to main menu')
    bot_handler[message.chat.id]['menu']['Back'] = get_finish_date
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['menu']['Back'] = checking_info
    notice = '<b>Enter the number by which you can find out information about housing:</b>' \
             '\n<i>In format:   <u><b>380</b></u>631234567</i>'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')

def get_name_hostess(message):
    print('hostes!!!!')
    bot_handler[message.chat.id]['text_expected'] = True
    markup_for_get_name_hostess(message)
    bot_handler[message.chat.id]['save_info_in'] = new_apartment
    bot_handler[message.chat.id]['argument_for_save'] = 'name_hostess'
    bot_handler[message.chat.id]['function_after_get_info'] = checking_info
    bot_handler[message.chat.id]['function_get_info'] = get_name_hostess
    bot_handler[message.chat.id]['correct_input'] = check_name_hostess


def check_name_hostess(message):
    if is_exists_cyrillic(message.text):
        bot.send_message(message.chat.id, '<b>Expected only latin!</b>', parse_mode='html')
        return False
    return True


def markup_for_get_name_hostess(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if new_apartment[message.chat.id]['name_hostess']:
        if not bot_handler[message.chat.id]['checking_info']:
            markup.add('Continue')
            bot_handler[message.chat.id]['menu']['Continue'] = checking_info
        notice = f'Specified name hostess:\n{new_apartment[message.chat.id]["name_hostess"]}' \
                 f'\nyou can enter a new one or continue with this'
        bot.send_message(message.chat.id, notice)
    markup.add('Back', 'Go to main menu')
    bot_handler[message.chat.id]['menu']['Back'] = get_phone_number
    if bot_handler[message.chat.id]['checking_info']:
        bot_handler[message.chat.id]['menu']['Back'] = checking_info
    notice = '<b>Enter the name of the hostess of these apartments:</b>'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')


def checking_info(message):
    bot_handler[message.chat.id]['text_expected'] = False
    bot_handler[message.chat.id]['photo_expected'] = False
    markup_for_checking_info(message)
    bot_handler[message.chat.id]['checking_info'] = True
    bot.send_message(message.chat.id, 'checking...')
    bot_handler[message.chat.id]['function_before_get_photo'] = checking_info
    bot_handler[message.chat.id]['function_after_get_photo'] = checking_info


def markup_for_checking_info(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('Confirm')
    buttons = []
    bot_handler[message.chat.id]['menu'] = {'Confirm': confirm_new_apartment, 'Reset date and return to menu': main_menu,
                           f'Photo{(len(new_apartment[message.chat.id]["photos"]) > 1) * "s"}'
                           f' which you uploaded.': photo_expected}
    input_for_user = {'address': get_address, 'price': get_price, 'photos': photo_expected,
                      'start_date': get_start_date, 'finish_date': get_finish_date,
                      'phone_number': get_phone_number, "name_hostess": get_name_hostess}
    for key, info in new_apartment[message.chat.id].items():
        if key != 'photos':
            buttons.append(f"{key.replace('_', ' ').title()}:\n{info}")
            for keyy, value in input_for_user.items():
                if keyy == key:
                    bot_handler[message.chat.id]['menu'][f"{key.replace('_', ' ').title()}:\n{info}"] = value
    buttons.insert(2, f'Photo{(len(new_apartment[message.chat.id]["photos"]) > 1) * "s"} which you uploaded.')
    markup.add(buttons[0])
    markup.add(*buttons[1:])
    markup.add('Reset date and return to menu')
    notice = '<b>Check entered information:</b>\n<i>(Click on the information if you want to change)</i>'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')


def confirm_new_apartment(message):
    with open('apartments/apartments.json', 'r') as file_apart:
        apart_data = json.load(file_apart)
    generete_data(message, apart_data)
    with open('apartments/apartments.json', 'w') as file_apart:
        json.dump(apart_data, file_apart, indent=4)
    new_apartment[message.chat.id] = {}
    notice = '<b>\U0001F389 Your listing has been successfully saved!!!</b> \U0001F389'
    bot.send_message(message.chat.id, notice, parse_mode='html')
    main_menu(message)


def generete_data(message, apart_data):
    apart_data[new_apartment[message.chat.id]['address']] = {}
    apart_data[new_apartment[message.chat.id]['address']]['price'] = new_apartment[message.chat.id]['price']
    apart_data[new_apartment[message.chat.id]['address']]['photos'] = new_apartment[message.chat.id]['photos']
    apart_data[new_apartment[message.chat.id]['address']]['available days'] = {}
    apart_data[new_apartment[message.chat.id]['address']]['booked days'] = {}
    create_days_for_rent(message, apart_data)
    apart_data[new_apartment[message.chat.id]['address']]['phone_number'] = new_apartment[message.chat.id]['phone_number']
    apart_data[new_apartment[message.chat.id]['address']]['name_hostess'] = new_apartment[message.chat.id]['name_hostess']
    apart_data[new_apartment[message.chat.id]['address']]['user_id'] = message.from_user.id


def month_counter(message):
    start_date_num = [int(i) for i in (new_apartment[message.chat.id]['start_date']).split('.')]
    star_date = datetime.date(*start_date_num)
    finish_date_num = [int(i) for i in (new_apartment[message.chat.id]['finish_date']).split('.')]
    finish_date = datetime.date(*finish_date_num)
    month_count = star_date.month
    year_count = star_date.year
    month_number = 1
    while month_count != finish_date.month or year_count != finish_date.year:
        month_number += 1
        month_count += 1
        if month_count == 13:
            month_count = 1
            year_count += 1
    return month_number


def create_days_for_rent(message, apart_data):
    month_number = month_counter(message)
    star_date = datetime.date(*[int(i) for i in (new_apartment[message.chat.id]['start_date']).split('.')])
    finish_date = datetime.date(*[int(i) for i in (new_apartment[message.chat.id]['finish_date']).split('.')])
    for i in range(month_number):
        date_month = star_date.month + i
        date_year = star_date.year + (date_month-1)//12
        date_month = date_month - (((date_month-1) // 12) * 12)
        days_in_month = calendar.monthrange(date_year, date_month)[1]
        if i == 0:
            days_str = ','.join([str(i) for i in range(star_date.day, days_in_month + 1)])
        elif i == month_number - 1:
            days_str = ','.join([str(i) for i in range(1, finish_date.day + 1)])
        else:
            days_str = ','.join([str(i) for i in range(1, days_in_month + 1)])
        apart_data[new_apartment[message.chat.id]['address']]['available days'][f'{date_year}.{date_month}'] = days_str


def My_booking(message):
    with open('apartments/apartments.json', 'r') as file_apartment:
        data_apartments = json.load(file_apartment)
    show_menu = False
    for address in data_apartments:
        if str(message.from_user.id) in data_apartments[address]['booked days']:
            if not show_menu:
                bot_handler[message.from_user.id]['call_data_expected'] = True
                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add('Go to mein menu')
                bot_handler[message.from_user.id]['menu'] = {'Go to mein menu': main_menu}
                notice = f'<b>Your all booking :</b>'
                bot.send_message(message.from_user.id, notice, parse_mode='html', reply_markup=markup)
                show_menu = True
            show_booked_add(message, address, data_apartments)
    else:
         if not show_menu:
            notice = '<b>You don`t have booking yet!</b>'
            bot.send_message(message.from_user.id, notice, parse_mode='html')



def show_booked_add(message, address, data_apartments):

    price = data_apartments[address]['price']
    name_hostess = data_apartments[address]['name_hostess']
    phone_number = data_apartments[address]['phone_number']
    notice = f"""<b>Address:</b>  <i>{address}</i>\n<b>Price</b>:  <i>{price} UAH / per day</i>\n
<b>Phone number:</b>  <i>{phone_number}</i>\n<b>Name of hostess:</b>  {name_hostess}"""
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text='Show main photo', callback_data=address + '*_*show_photo_mein')
    button2 = InlineKeyboardButton(text='Show all photos', callback_data=address + '*_*show_photo_all')
    markup.add(button1, button2)
    bot.send_message(message.from_user.id, notice, parse_mode='html', reply_markup=markup)
    for month in data_apartments[address]['booked days'][str(message.from_user.id)]:
        markup = InlineKeyboardMarkup(row_width=2)
        # button1 = InlineKeyboardButton(text=f'Change your booking in {month}',
        #                                 callback_data=address+'*_*' + month + '*_*view_booked_dates')  # TODO: create
        button2 = InlineKeyboardButton(text=f'Delete booking {month}',
                                      callback_data=address+'*_*' + month + '*_*delete_booking')
        markup.add(button2)
        booked_days = data_apartments[address]["booked days"][str(message.from_user.id)][month].replace(',', '   ')
        notice = f'<b>Booking in {month}:</b>          <i>{booked_days}</i>'
        bot.send_message(message.from_user.id, notice, parse_mode='html', reply_markup=markup)
        notice = '\U0000203C<b>Removing a booking you get back only <u>90%</u> of the money!</b>\U0000203C'
        bot.send_message(message.from_user.id, notice, parse_mode='html')



def update_balance(message):
    bot_handler[message.from_user.id]['text_expected'] = False
    with open('data/users_id.json') as file_users:
        all_users = json.load(file_users)
    first_name = all_users[str(message.from_user.id)]['first_name']
    last_name = all_users[str(message.from_user.id)]['last_name']
    balance = all_users[str(message.from_user.id)]['balance']
    notice = f'<b>{first_name} {last_name}</b>\n<i>Your balance:   <b>{balance}</b>  UAH</i>'
    markup_update_balance(message, notice)


def markup_update_balance(message, notice):
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Update your balance', 'Go to main menu')
    bot_handler[message.from_user.id]['menu'] = {'Update your balance': update_user_balance,
                                                 'Go to main menu': main_menu}
    bot.send_message(message.from_user.id, notice, parse_mode='html', reply_markup=markup)


def update_user_balance(message):
    bot_handler[message.from_user.id]['text_expected'] = True
    bot_handler[message.chat.id]['save_info_in'] = bot_handler
    bot_handler[message.chat.id]['argument_for_save'] = 'new_balance'
    bot_handler[message.chat.id]['function_after_get_info'] = update_balance
    bot_handler[message.chat.id]['function_get_info'] = update_user_balance
    bot_handler[message.chat.id]['correct_input'] = check_input_update_user_balance
    bot_handler[message.chat.id]['menu'] = {'Go to main menu': main_menu, 'Back': update_balance}
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Back', 'Go to main menu')
    notice = '<b>Enter the replenishment amount:\n</b><i>(UAH)</i>'
    bot.send_message(message.from_user.id, notice, parse_mode='html', reply_markup=markup)


def check_input_update_user_balance(message):
    try:
        if 0 > int(message.text):
            notice = '<b>Top-up amount cannot be less than zero!</b>'
        elif int(message.text) > 10000:
            notice = '<b>Top-up amount cannot be more than 10 000 UAH!</b>\n<i>(this is only available for vip)</i>'
        else:
            notice = f'\U0001F389<b>Congratulations, your balance has been successfully' \
                     f' topped up by {message.text} UAH </b>\U0001F389'
            bot.send_message(message.from_user.id, notice, parse_mode='html')
            change_balance(message)
            return True
    except:
        notice = '<b>You can only enter numbers!</b>'
    bot.send_message(message.from_user.id, notice, parse_mode='html')
    return False


def change_balance(message):
    with open('data/users_id.json', 'r') as file_users:
        data_users = json.load(file_users)
    user_balance = int(data_users[str(message.from_user.id)]['balance'])
    top_up = int(message.text)
    changed_balance = user_balance + top_up
    data_users[str(message.from_user.id)]['balance'] = changed_balance
    with open('data/users_id.json', 'w') as file_users:
        json.dump(data_users, file_users, indent=4)

def remove_photos(message):
    for photo in new_apartment[message.chat.id]['photos']:
        src = os.path.join(os.path.abspath(os.path.dirname(__file__)), photo)
        os.remove(src)
    new_apartment[message.chat.id]['photos'] = []
    photo_expected(message)


def photo_expected(message):
    bot.send_message(message.chat.id, '<b>Photo expected...</b>', parse_mode='html')
    bot_handler[message.chat.id]['photo_expected'] = True
    bot_handler[message.chat.id]['text_expected'] = False
    if len(new_apartment[message.chat.id]['photos']):
        markup = is_photo_before(message)
    else:
        markup = is_not_photo_before(message)
    notice = '<i>(drag and drop photo - "for quick upload" <u>with compression</u>):</i>'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')


def is_not_photo_before(message):
    notice = '<b>This will be the main photo of your apartment, choose wisely</b>'
    bot.send_message(message.chat.id, notice, parse_mode='html')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    bot_handler[message.chat.id]['menu'] = {'Go to main menu': main_menu}
    if not bot_handler[message.chat.id]['checking_info']:
        markup.add('Back')
        bot_handler[message.chat.id]['menu']['Back'] = bot_handler[message.chat.id]['function_before_get_photo']
    markup.add('Go to main menu')
    return markup


def is_photo_before(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    notice = f'<b>Uploaded photo{(len(new_apartment[message.chat.id]["photos"])>1)*"s"} saved</b>' \
             f'\nYou can Add more photos, remove or <u>continue</u>:'
    bot.send_message(message.chat.id, notice, parse_mode='html')
    if not bot_handler[message.chat.id]['checking_info']:
        markup.add('Continue')
        bot_handler[message.chat.id]['menu']['Continue'] = bot_handler[message.chat.id]['function_after_get_photo']
    markup.add('Remove uploaded photos', 'Back', 'Go to main menu')
    bot_handler[message.chat.id]['menu']['Remove uploaded photos'] = remove_photos
    bot_handler[message.chat.id]['menu']['Back'] = bot_handler[message.chat.id]['function_before_get_photo']
    return markup


def get_name_photo(message, format):
    photo_name = new_apartment[message.chat.id]['address']      #.replace('.', '-').replace(' ', '_')
    while os.path.exists('photos/' + photo_name + format):
        photo_name += '+'
    return photo_name


def save_photo(message: telebot.types.Message):
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    format = os.path.splitext(file_info.file_path)[-1]
    photo_name = get_name_photo(message, format)
    src = 'photos/' + photo_name + format
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    # bot.reply_to(message, "Photo added successfully.")
    new_apartment[message.chat.id]['photos'].append(src)


def markup_after_receive_photo(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add('Continue', 'Remove uploaded photos', 'Back', 'Go to main menu')
    bot_handler[message.chat.id]['menu']['Continue'] = bot_handler[message.chat.id]['function_after_get_photo']
    bot_handler[message.chat.id]['menu']['Remove uploaded photos'] = remove_photos
    bot.send_message(message.chat.id, '<b>Photo expected...</b>', parse_mode='html')
    notice = f'<b>Uploaded photo{(len(new_apartment[message.chat.id]["photos"])>1)*"s"} saved</b>' \
             '\nYou can Add more photos, remove or <u>continue</u>:'
    bot.send_message(message.chat.id, notice, reply_markup=markup, parse_mode='html')


transliteration_letters = {'А':  'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 'Ж': 'ZH', 'З': 'Z',
                           'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
                           'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'KH', 'Ц': 'TC', 'Ч': 'CH', 'Ш': 'SH',
                           'Щ': 'SHCH', 'Ы': 'Y', 'Э': 'E', 'Ю': 'IU', 'Я': 'IA'}


def transliteration(user_name):
    if user_name:
        list_of_name_letters = []
        for letter in str(user_name):
            if letter.upper() in transliteration_letters:
                list_of_name_letters.append(transliteration_letters[letter.upper()])
            else:
                list_of_name_letters.append(letter)
        name = ''.join(list_of_name_letters).title()
        return name
    else:
        return user_name


def add_new_user(message):
    with open('data/users_id.json', 'r') as users_file:
        users_info = json.load(users_file)
    if str(message.from_user.id) not in users_info:
        user_first_name = transliteration(message.from_user.first_name)
        user_last_name = transliteration(message.from_user.last_name)
        time_registration = f'{datetime.datetime.now()}'[11:-7]+f'   {datetime.date.today()}'
        new_user = {'balance': 0, 'first_name': user_first_name, 'last_name': user_last_name,
                    'user_name': message.from_user.username, 'registration_time': time_registration}
        users_info[message.from_user.id] = new_user
        with open('data/users_id.json', 'w') as users_file:
            json.dump(users_info, users_file, indent=4)


@bot.message_handler(commands=['start', 'Click_here_for_start'])
def start(message):
    add_new_user(message)
    greeting = f'<b>Hello {transliteration(message.from_user.first_name)}!\U0001F64F' \
               f'\nHere you can rent an apartment in the <i>Carpathians</i>' \
               f'\nHave a good rest or earn money\U0001F601\n Let`s go to the main menu!</b>.\U0001F447'
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Go to main menu')
    bot.send_message(message.chat.id, greeting, reply_markup=markup, parse_mode='html')
    create_user_handler(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.from_user.id in bot_handler and bot_handler[call.from_user.id]['call_data_expected'] == True:

        if 'show_photo' in call.data:
            show_photo(call)
        elif 'more_apartments' == call.data:
            bring_apartments_more(call)
        elif 'less_apartments' == call.data:
            bring_apartments_less(call)
        elif 'view_dates' in call.data:
            view_available_dates(call)
        elif call.data in bot_handler[call.from_user.id]['dates_list']:
            selection_dates(call)
        elif call.data == 'buy':
            buy_selected_days(call)
        elif 'delete_booking' in call.data:
            delete_booking(call)
    else:
        ...                                                                     # TODO: change


def selection_dates(call):
    data_apartments = bot_handler[call.from_user.id]['data_apartments']
    address = bot_handler[call.from_user.id]['selected_address']
    price = int(data_apartments[address]['price'])
    markup = InlineKeyboardMarkup(row_width=7)
    markup.add(*bot_handler[call.from_user.id]['head_calendar'])
    bot_handler[call.from_user.id]['list_calendar'] = [str(i) for i in bot_handler[call.from_user.id]['list_calendar']]
    index_button = bot_handler[call.from_user.id]['list_calendar'].index(call.data)
    index_date = bot_handler[call.from_user.id]['dates_list'].index(call.data)
    print(call.data)
    print(call.data.replace('#', ''))
    if '#' not in call.data:
        bot_handler[call.from_user.id]['list_calendar'][index_button] = call.data+'#'
        bot_handler[call.from_user.id]['dates_list'][index_date] = call.data+'#'
    else:
        bot_handler[call.from_user.id]['list_calendar'][index_button] = call.data.replace('#', '')
        bot_handler[call.from_user.id]['dates_list'][index_date] = call.data.replace('#', '')
    list_of_inline_buttons = []
    for day in bot_handler[call.from_user.id]['list_calendar']:
        list_of_inline_buttons.append(InlineKeyboardButton(text=day, callback_data=day))
    markup.add(*list_of_inline_buttons)
    selected_days = 0
    for day in bot_handler[call.from_user.id]['list_calendar']:
        if "#" in day:
            selected_days += 1
    notice = f'Click for booking :  {selected_days} days  /  {selected_days*price}  cost'
    bot_handler[call.from_user.id]['total_cost'] = selected_days*price
    markup.add(InlineKeyboardButton(text=notice, callback_data='buy'))
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup)
    print(bot_handler[call.from_user.id]['total_cost'])


def buy_selected_days(call):
    if bot_handler[call.from_user.id]['total_cost'] <= bot_handler[call.from_user.id]['balance']:
        for i in range(len(bot_handler[call.from_user.id]['dates_list'])-1, -1, -1):
            day = bot_handler[call.from_user.id]['dates_list'][i]
            if '#' in day:
                bot_handler[call.from_user.id]['dates_list'].remove(day)
                bot_handler[call.from_user.id]['buy_days'].append(day.replace('#', ''))
        bot_handler[call.from_user.id]['buy_days'].reverse()
        change_file(call)
    else:
        notice = '<b>Not enough money in the account!</b>'
        bot.send_message(call.from_user.id, notice, parse_mode='html')


def change_file(call):
    with open('apartments/apartments.json', 'r') as file_apartments:
        updated_data_apartment = json.load(file_apartments)
    updated_data_month = updated_data_apartment[bot_handler[call.from_user.id]['selected_address']][
        "available days"][bot_handler[call.from_user.id]['searching_month']]
    old_data_month = (bot_handler[call.from_user.id]['data_apartments'])[bot_handler[call.from_user.id][
        'selected_address']]["available days"][bot_handler[call.from_user.id]['searching_month']]
    if updated_data_month == old_data_month:
        days_str = ','.join([str(i) for i in bot_handler[call.from_user.id]['dates_list']])
        updated_data_apartment[bot_handler[call.from_user.id]['selected_address']][
            "available days"][bot_handler[call.from_user.id]['searching_month']] = days_str
        days_str_booked = ','.join([str(i) for i in bot_handler[call.from_user.id]['buy_days']])
        if not str(call.from_user.id) in updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]["booked days"]:
            updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]["booked days"][str(call.from_user.id)] = {}
        if bot_handler[call.from_user.id]['searching_month'] not in updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]["booked days"][str(call.from_user.id)]:
            updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]["booked days"][str(call.from_user.id)][bot_handler[call.from_user.id]['searching_month']] = days_str_booked
        else:
            month =updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]["booked days"][str(call.from_user.id)][bot_handler[call.from_user.id]['searching_month']]
            new_month = sorted(month.split(',') + bot_handler[call.from_user.id]['buy_days'])
            nwe_days_str_booked = ','.join([str(i) for i in new_month])
            updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]["booked days"][
                str(call.from_user.id)][bot_handler[call.from_user.id]['searching_month']] = nwe_days_str_booked
        if 'money_earned' not in updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]:
            updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]['money_earned'] = bot_handler[call.from_user.id]['total_cost']
        else:
            updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]['money_earned'] = int(updated_data_apartment[bot_handler[call.from_user.id]['selected_address']]['money_earned']) + int(bot_handler[call.from_user.id]['total_cost'])
        with open('apartments/apartments.json', 'w') as file_apartments:
            json.dump(updated_data_apartment, file_apartments, indent=4)
        with open('data/users_id.json', 'r') as file_users:
            data_users = json.load(file_users)
        data_users[str(call.from_user.id)]['balance'] = bot_handler[call.from_user.id]['balance'] - bot_handler[call.from_user.id]['total_cost']
        with open('data/users_id.json', 'w') as file_users:
            json.dump(data_users, file_users, indent=4)
        notice = '<b>\U0001F389 Сongratulations!\nApartment booked successfully !\U0001F389 </b>'
        bot.send_message(call.from_user.id, notice, parse_mode='html')
        main_menu(call)
    else:
        notice = '<b>Data has been changed during booking, please try again</b>'
        bot.send_message(call.from_user.id, notice, parse_mode='html')
        main_menu(call)



def delete_booking(call):  #address + '*_*' + month + '*_*delete_booking'
    with open('apartments/apartments.json', 'r') as file_apartments:
         data_apartments = json.load(file_apartments)
    address = call.data.split('*_*')[0]
    month = call.data.split('*_*')[1]
    if month not in data_apartments[address]['booked days'][str(call.from_user.id)]:
        print(1)
        return None
    available_dates = data_apartments[address]['available days'][month].split(',')
    booked_dates = data_apartments[address]['booked days'][str(call.from_user.id)][month].split(',')
    available_dates = sorted([int(day) for day in (booked_dates + available_dates)])
    data_apartments[address]['available days'][month] = ','.join([str(day) for day in available_dates])
    del data_apartments[address]['booked days'][str(call.from_user.id)][month]
    if len(data_apartments[address]['booked days'][str(call.from_user.id)]) == 0:
        del data_apartments[address]['booked days'][str(call.from_user.id)]
    price = int(data_apartments[address]['price']) * len(booked_dates)
    data_apartments[address]['money_earned'] = int(data_apartments[address]['money_earned']) - int(price)
    with open('apartments/apartments.json', 'w') as file_apartments:
        json.dump(data_apartments, file_apartments, indent=4)
    with open('data/users_id.json', 'r') as file_users:
        data_users = json.load(file_users)
    data_users[str(call.from_user.id)]['balance'] = int(data_users[str(call.from_user.id)]['balance']) + price*0.9
    with open('data/users_id.json', 'w') as file_users:
        json.dump(data_users, file_users, indent=4)
    notice = f'<b>The reservation was canceled!\nYou received 90% of the amount( {price*0.9} / {price} )</b>'
    bot.send_message(call.from_user.id, notice, parse_mode='html')
    main_menu(call)




def show_photo(call):
    with open('apartments/apartments.json', 'r') as file_apartments:
        data_apartments = json.load(file_apartments)
    address = call.data.split('*_*')[0]
    all_photos = data_apartments[address]['photos']
    for a_photo in all_photos:
        photo = open(a_photo, 'rb')
        bot.send_photo(call.from_user.id, photo)
        if 'show_photo_mein' in call.data:
            break


@bot.message_handler(content_types=['photo'])
def photo_handler(message: telebot.types.Message):

    if bot_handler[message.chat.id]['photo_expected']:

        try:

            save_photo(message)

            markup_after_receive_photo(message)

        except Exception as error:

            bot.reply_to(message, str(error))

    else:

        bot.send_message(message.chat.id, '<b>Unexpected photo!</b>', parse_mode='html')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.chat.id in bot_handler:
        if message.text in bot_handler[message.chat.id]['menu']:
            bot_handler[message.chat.id]['menu'][message.text](message)
        elif bot_handler[message.chat.id]['text_expected']:
            if bot_handler[message.chat.id]['correct_input'](message):
                (bot_handler[message.chat.id]['save_info_in'])[message.chat.id][bot_handler[message.chat.id]['argument_for_save']] = message.text
                bot_handler[message.chat.id]['function_after_get_info'](message)
            else:
                bot_handler[message.chat.id]['function_get_info'](message)
        elif bot_handler[message.chat.id]['photo_expected']:
            bot.send_message(message.chat.id, '<b>Photo expected!</b>', parse_mode='html')
        else:
            bot.send_message(message.chat.id, '<b>Unexpected text!</b>', parse_mode='html')
    else:
        bot.send_message(message.chat.id, '<b>Bot has been reloaded\n/Click_here_for_start </b>', parse_mode='html')


new_apartment = {}
bot_handler = {}
bot.polling(True)
# bot.infinity_polling(timeout=10, long_polling_timeout=5)










