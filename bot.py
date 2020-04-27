import telebot
from configparser import ConfigParser

config = ConfigParser()
config.read('settings.ini')

bot = telebot.TeleBot(config.get('config', 'Token'))