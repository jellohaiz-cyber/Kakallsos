import asyncio
import random
import html
import logging
import sys
import re
import time
from threading import Event
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from telegram import ReplyKeyboardMarkup

logging.basicConfig(level=logging.ERROR)

BOT_TOKENS = [
  "8737207969:AAHPeiwJ4D4W_INzWKb7eWrevnLipoFbeV8",
  "8727463659:AAGB8eqFjpl0FW7AObDDOb36f47emRqLinY",
  "8710532825:AAFW_Wm4SeSIyFADP7Qn2ATMVEn2UPbB14Y",
  "8376295901:AAHQuMPY0Ot2KnnfZsa5sq3Dt5jPvvZM0F8",
  "8773951189:AAH8Ld6b0IiIfJkTBIv1_5u7NoX1jJf_avo",
  "8682697219:AAH_xWaAdsppXHWz54LTaDRpCtbIc9F0E0k",
  "8660253407:AAFUs6LKJ3lCPEOBRbY-8cCcx1BebhCTwS8",
  "8782399502:AAHUwap842yeR6Mt9Y1_dVqDr3exekjVM-E",
  "8787085457:AAHu1tanlBN4VeVQkXiRO8EH1JEyg7pO3vA",
  "8724977940:AAF8DOUmBcoNvfgekZYxcQB_lTPzPqHHC8s"
]


OWNER_ID = 7462915877
ADMIN_IDS = {7462915877}
MY_BOT_IDS = {int(t.split(':')[0]) for t in BOT_TOKENS if ":" in t}

MUTE_ALL_MODE = False
muted_users = set()
stop_events = {}
sent_messages_dict = {}
current_delay = 0.0001
auto_title = {}
auto_title_tasks = {}
combined_tasks = {}

SPECIAL_MESSAGE = "꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰ ꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰꙰⃟꙰⃟꙰⃟꙰"
MESSAGES = ["chó ngu=)))","óc cứt à em=)))","ẳng lên=)))","đỉ mẹ m ngu à=)))","lô=)))","đỉ chó lồn =)))=)))","tao chặt đầu con gái mẹ m mà=)))=)))","sao nào thằng cặc=)))=)))","đụ con gái mẹ m=)))=)))","óc lồn sỉ=)))=)))","con mẹ mày chết rồi à=))=)))","lồn mồ côi=)))=)))","con mẹ mày chết mà e=)))=)))","mẹ mày là đỉ lồn âm binh=))=)))","Slow k e=)))","slow mẹ m bị t xử mò=)))","a bại cap noti e=)))","anh địt con má m bể lồn=)))=)))","sao nào con trai=)))=)))","chó lồn bể bóng à=)))=)))","địt con má mày lồn cứt heo=)))","ý kiến à mặt cứt=)))=)))","con má mày chết e=)))=)))","óc lồn thiếu mẹ=)))=)))","anh băm đầu cha mày mà=)))","đỉ lồn ăn cứt mồ côi=)))=)))","chó lồn khắm dịch=)))=)))","xa dao chết mẹ m giờ=)))=)))","anh đâm lủng lổ lồn con gái mẹ m e ơi=)))","ngu ưi a phạt con mẹ mày nhoa=))=)))","lồn mất dạy=)))=)))","dkm lồn này bất hiếu ae=)))=)))","sở thích nhìn mẹ no tắm=)))=)))","chó lồn ơi sủa nào con=)))","mẹ mày làm a khoái cảm phết=)))=)))","đụ con mẹ mày tk cứt culi=)))=)))","cha phú địt chết dòng họ m mà kaka=)))","r xg=)))","chậm à=)))","cho mày chạy à=)))","gap t nhu gap thanh phai kg=)))","con đỉ ngu lồn=)))","tk lồn lơ ngơ phết e=)))=)))","chó ngu cái lồn mẹ mày thâm xì e=)))=)))","cái vú mày mày siu lép ấy e=)))","mông mẹ m bức tường à=)))=)))","địt con mẹ mày bố địt chết mẹ m e ơi=)))","chó lồn ơi con mẹ mày sung phết=)))=)))","con đỉ ơi a chém cái lồn mẹ m tơi bời tan nát đấy=)))=)))","chó lồn ăn cứt a nào=)))=)))","ngoan nào con chó của a=)))=)))","anh lại địt con già mày giờ=)))=)))","mẹ mày lồn ngheo=)))=)))","chó ngheo thiếu thốn đủ điều=}})=)))","mẹ mày ngu vl em=)))","địt mẹ m ma đéo cãi e ơi=)))","óc lồn cặc nhỏ ghệ bỏ mẹ nó luôn e ơi=)))=)))","thằng cặc giết cha vì cái lồn con giá nó=)))=)))","dkm lồn bất hiếu vl em=)))=)))","sao m rụng ngay khi anh đến r=)))","mồ côi thắp hương cha mẹ trc khi chửi chưa=)))","m mồ côi không cha mẹ đổ thừa cay bố m kìa=)))","tây tạng béo mỡ cha chọc chết tươi rồi=)))","m còn trò j thể hiện nhanh lên o kia=)))","óc chó ko trình lên đây sủa mạnh mẽ lên anh chơi mày cả ngày mà=)))","ơ hay óc chó ơi m sủa mạnh mẽ lên sao lại bị dập rồi=)))","lêu lêu thằng ngu không làm gì được cay anh kia=)))","haha óc chó gà bị chửi cay cú ớt mẹ rồi=)))=)))","óc chó ngu cay cha bán mạng đi chửi cha má kìa=)))=)))","m chạy đâu v con chó ngu ơi không được chạy mà=)))=)))","ai đụng gì óc chó để nó sợ rồi chạy thục mạng kìa=)))","culi ngu bị anh chửi té tát nước vô mặt m kìa=)))=)))","culi bị chửi mất xác kìa=)))","thằng nguuu giết cha bóp cổ má để cầu win anh à=)))","hi vọng làm dân war của con ngu bị t dập tắt từ khi nó sủa điên trước mặt t ae=)))=)))","bà nội m loạn luân vs bố m còn ông ngoại m loạn luân vs mẹ m mà thg nhận cún=)))=)))","Cn thú mại dâm bán dâm mà như bán trinh hoa hậu v=)))","con ngu nứng quá đến cả con mom nó gần u60 r nó vẫn ko tha=)))=)))","Mẹ mày làm con chó canh cửa cho nhà t mà=)))","đáp ngôn nhanh hơn tý đc k tk ngu xuẩn=)))","bat qua tang con cho chay bo ne=)))","Vào 1 hôm bỗng con đĩ mẹ nhà m die thì lúc đó cha làm bá chủ sàn mẹ r=)))","con đĩ mẹ mày bất lực vì bị tao chửi mà chỉ biết câm lặng=)))","mẹ mày bị t đụ đột quỵ ngoài nhà nghỉ kìa đem hòm ra nha=)))","đem hai cái mày với con mẹ m luôn nha=)))","thời gian trôi qua để cảm nhận nỗi đau đi ửa à=)))","nhai t chặt đầu con đĩ má m ra đó=)))","thằng ngu lgbt da đen sủa lẹ ai cko mày câm=)))","thằng sex thú đang cố làm cha cay hả thằng bại não=)))","tao miễn nhiễm mà thằng ngu=)))","Anh Bá Vcl Lỡ Đá Chết Mẹ mày Rồi=)))","Mẹ Mày Banh Háng Cho Khách Đụ Kìa Thằng Óc=)))","Tao Lỡ Cho Mẹ Mày Bú Cu Tao Roi Sướng Vai Cặc=)))","Lêu Lêu Nhìn Cha Đụ Mẹ Mày Ko Làm Được Gì À Đừng Có Cay Cha Nha=)))","bị tao khủng bộ quá nát mẹ cái hộp sọ với não luôn rồi à=)))=)))","m là con đĩ đầu đinh giết má để loạn luân với bố mà con khốn=)))","van thơ anh lai láng để con mẹ m dạng háng mỗi đêm=)))=)))","qua sông thì phải bắc cầu kiều con mẹ mày muốn làm đĩ thì phải yêu chiều các anh mà=)))","Th lồn ngu này hay đạp xe đạp ngang nhà tao bị tao chọi đá về méc mẹ mà=)))","thằng ngu này đang đi bộ bị t đánh úp nó về mách mẹ mà ae=)))","thang nay an va khen chubin anh singu khen ngon qua=)))=)))","chó ngu=)))","óc cứt à em=)))","ẳng lên=)))","đỉ mẹ m ngu à=)))","lô=)))","đỉ chó lồn =)))=)))","tao chặt đầu con gái mẹ m mà=)))=)))","sao nào thằng cặc=)))=)))","đụ con gái mẹ m=)))=)))","óc lồn sỉ=)))=)))","con mẹ mày chết rồi à=))=)))","lồn mồ côi=)))=)))","con mẹ mày chết mà e=)))=)))","mẹ mày là đỉ lồn âm binh=))=)))","Slow k e=)))","slow mẹ m bị t xử mò=)))","a bại cap noti e=)))","anh địt con má m bể lồn=)))=)))","sao nào con trai=)))=)))","chó lồn bể bóng à=)))=)))","địt con má mày lồn cứt heo=)))","ý kiến à mặt cứt=)))=)))","con má mày chết e=)))=)))","óc lồn thiếu mẹ=)))=)))","anh băm đầu cha mày mà=)))","đỉ lồn ăn cứt mồ côi=)))=)))","chó lồn khắm dịch=)))=)))","xa dao chết mẹ m giờ=)))=)))","anh đâm lủng lổ lồn con gái mẹ m e ơi=)))","ngu ưi a phạt con mẹ mày nhoa=))=)))","lồn mất dạy=)))=)))","dkm lồn này bất hiếu ae=)))=)))","sở thích nhìn mẹ no tắm=)))=)))","chó lồn ơi sủa nào con=)))","mẹ mày làm a khoái cảm phết=)))=)))","đụ con mẹ mày tk cứt culi=)))=)))","cha phú địt chết dòng họ m mà kaka=)))","r xg=)))","chậm à=)))","cho mày chạy à=)))","gap t nhu gap thanh phai kg=)))","con đỉ ngu lồn=)))","tk lồn lơ ngơ phết e=)))=)))","chó ngu cái lồn mẹ mày thâm xì e=)))=)))","cái vú mày mày siu lép ấy e=)))",
    "mông mẹ m bức tường à=)))=)))","địt con mẹ mày bố địt chết mẹ m e ơi=)))","chó lồn ơi con mẹ mày sung phết=)))=)))","con đỉ ơi a chém cái lồn mẹ m tơi bời tan nát đấy=)))=)))","chó lồn ăn cứt a nào=)))=)))","ngoan nào con chó của a=)))=)))","anh lại địt con già mày giờ=)))=)))","mẹ mày lồn ngheo=)))=)))","chó ngheo thiếu thốn đủ điều=}})=)))","mẹ mày ngu vl em=)))","địt mẹ m ma đéo cãi e ơi=)))","óc lồn cặc nhỏ ghệ bỏ mẹ nó luôn e ơi=)))=)))","thằng cặc giết cha vì cái lồn con giá nó=)))=)))","dkm lồn bất hiếu vl em=)))=)))","sao m rụng ngay khi anh đến r=)))","mồ côi thắp hương cha mẹ trc khi chửi chưa=)))","m mồ côi không cha mẹ đổ thừa cay bố m kìa=)))","tây tạng béo mỡ cha chọc chết tươi rồi=)))","m còn trò j thể hiện nhanh lên o kia=)))","óc chó ko trình lên đây sủa mạnh mẽ lên anh chơi mày cả ngày mà=)))","ơ hay óc chó ơi m sủa mạnh mẽ lên sao lại bị dập rồi=)))","lêu lêu thằng ngu không làm gì được cay anh kia=)))","haha óc chó gà bị chửi cay cú ớt mẹ rồi=)))=)))","óc chó ngu cay cha bán mạng đi chửi cha má kìa=)))=)))","m chạy đâu v con chó ngu ơi không được chạy mà=)))=)))","ai đụng gì óc chó để nó sợ rồi chạy thục mạng kìa=)))","culi ngu bị anh chửi té tát nước vô mặt m kìa=)))=)))","culi bị chửi mất xác kìa=)))","thằng nguuu giết cha bóp cổ má để cầu win anh à=)))","hi vọng làm dân war của con ngu bị t dập tắt từ khi nó sủa điên trước mặt t ae=)))=)))","bà nội m loạn luân vs bố m còn ông ngoại m loạn luân vs mẹ m mà thg nhận cún=)))=)))","Cn thú mại dâm bán dâm mà như bán trinh hoa hậu v=)))","con ngu nứng quá đến cả con mom nó gần u60 r nó vẫn ko tha=)))=)))","Mẹ mày làm con chó canh cửa cho nhà t mà=)))","đáp ngôn nhanh hơn tý đc k tk ngu xuẩn=)))","bat qua tang con cho chay bo ne=)))","Vào 1 hôm bỗng con đĩ mẹ nhà m die thì lúc đó cha làm bá chủ sàn mẹ r=)))","con đĩ mẹ mày bất lực vì bị tao chửi mà chỉ biết câm lặng=)))","mẹ mày bị t đụ đột quỵ ngoài nhà nghỉ kìa đem hòm ra nha=)))","đem hai cái mày với con mẹ m luôn nha=)))","thời gian trôi qua để cảm nhận nỗi đau đi ửa à=)))","nhai t chặt đầu con đĩ má m ra đó=)))","thằng ngu lgbt da đen sủa lẹ ai cko mày câm=)))","thằng sex thú đang cố làm cha cay hả thằng bại não=)))","tao miễn nhiễm mà thằng ngu=)))","Anh Bá Vcl Lỡ Đá Chết Mẹ mày Rồi=)))","Mẹ Mày Banh Háng Cho Khách Đụ Kìa Thằng Óc=)))","Tao Lỡ Cho Mẹ Mày Bú Cu Tao Roi Sướng Vai Cặc=)))","Lêu Lêu Nhìn Cha Đụ Mẹ Mày Ko Làm Được Gì À Đừng Có Cay Cha Nha=)))","bị tao khủng bộ quá nát mẹ cái hộp sọ với não luôn rồi à=)))=)))","m là con đĩ đầu đinh giết má để loạn luân với bố mà con khốn=)))","van thơ anh lai láng để con mẹ m dạng háng mỗi đêm=)))=)))","qua sông thì phải bắc cầu kiều con mẹ mày muốn làm đĩ thì phải yêu chiều các anh mà=)))","Th lồn ngu này hay đạp xe đạp ngang nhà tao bị tao chọi đá về méc mẹ mà=)))","thằng ngu này đang đi bộ bị t đánh úp nó về mách mẹ mà ae=)))","thang nay an va khen chubin anh singu khen ngon qua=)))=)))","Mếu cha mẹ r=)))","Cay cú mẹ r=)))","Lgbt bày binh bố trận dồn cha hả=)))","Dồn ngu mà cũng đòi dồn=)))","Nhìn lũ tật cầm cái phím tắt hăng ghê=)))","Cha mày chúa tể trị lũ đú=)))","Cha mày bón cứt dô mõm m nè=)))","Ê đỉ ngu=)))","Sao rồi ổn kh=)))","Hay ổn lòi lìa=)))","Nhìn mặt m là bt không ổn r=)))","Cn tinh tinh bị cha đọa đày=)))","Bị cha mày đọa đày xuống diêm la địa phủ=)))","Để đầu thai chuyển kiếp thành súc vật=)))","Đừng cay cha mà làm liều=)))","Nhìn bản mặt mày là đủ hiểu cay cỡ nào=)))","Mày đái ra máu r kìa=)))","Nhanh tay lên nào=)))","Nhanh tay múc nc máu lồn cho tk cha mày uống lẹ=)))","Rồi lun cn ôn thú bị anh sỉ nhục mẹ r=)))","Sỉ nhục như cn động vật bậc thấp=)))","ngu si 4 chi phát triển=)))","Tự nhiên cái hăng ngang dị=)))","Hăng ngang làm anh sợ ghê=)))","Hăng lên đc tí r ngủm r à=)))","Đái ra máu xè xè r=)))","Ăn năn xám hối r à=)))","Cay quá nên uống nc đái chó cho đỡ cay đi em=)))","Mếu chết đỉ mẹ mày đi=)))","Đầu thai mẹ mày đi cn tạp chủng=)))","Cn ngu xi đần độn dốt nát=)))","Bị cha cho tha hóa thành cchó ngu dốt=)))","Sao mày ngu như v=)))","Cay cay cay cha rồi=)))","Ai cho mày cay cha hả=)))","Cay chừa phần người ta với=)))","Cay ht phần thiên hạ là sao dị=)))","Ê cn thú hoang dã=)))","Cn dị tật bẩm sinh liệt não=)))","Hấp hối mẹ mày rồi à=)))","Cha mày trùm đấng mxh ai làm lại anh đâu=)))","Mày khóc rồi à=)))","Con bào thai trong ống nghiệm cũng bt mếu à=)))","Mày sủa như cách cn chó nhà mày sủa đê=)))","Ê sao cay cú cha mày rồi=)))","Ai cho mày cay cha hả=)))","Cn tinh tinh đội lót nhân dân hại dân lành=)))","Cạn ngôn r hả cn thú ngu êy=)))","Sao lặp ngôn liên tục v=)))","Gõ dài dòng kh dame thì gõ làm gì=)))","Mày là cn phò trường chinh mà=)))","Cn thú mại dâm bán dâm mà như bán trinh hoa hậu v=)))","Ê cn đỉ phát ngôn xàm bậy=)))","Mày đừng tự vả dô mặt m nữa=)))","Nhìn mày là bt kh ổn r=)))","Mày bt anh là chuyên trừng trị những thể loại như m kh=)))","Sao mày đú quá v=)))","Khi nào ht đú hả cn thú ngu=)))","Chắc xog quả này chắc ht đú ha=)))","Ê cn thú ngu ngục bẩm sinh=)))","Mày là cn thú ms đẻ ra đã ngu sẵn r=)))","Ê cn âm binh đầu đường xó chợ=)))","Mày hăng mạnh mẽ lên đê=)))","Sao tự nhiên yếu xìu như xìu cặc v=)))","Mẹ mày bị mày loạn luân đụ rung lồn mà=)))","Cặc chưa mọc lông mà đòi đụ này đụ kia=)))","con chó ngu ngục lên thể hiện trình bị anh sút=)))","thằng ngu đang cố tỏ ra mình ổn à=)))","ơ ơ ơ sao em lại hăng=)))","dân war 2024 hăng ròi kìa ae=)))","bị anh chọc cho tê cu à=)))","nhìn tk óc dái đú đang đú bot nhìn ngu vậy=)))","ơ tk ngu ai treo vậy em=)))","tự nhiên treo vậy tk gà bí ngôn=)))","ai giả bộ sợ cho em nó đỡ quê đê=)))","tk ngu ăn cứt tao mà ra oai à=)))","sao em đú dữ vậy tỉnh lên đê=)))","mày chết r à=)))","sao chết kìa=)))","bị t hành nên muốn chết à=)))","con lồn ngu=)))=)))","sao kìa=)))","mạnh lên kìa=)))","yếu sinh lý à=)))","sủa đê=)))","cay à=)))",
    "hăng đê=)))","gà kìa ae=)))","akakaa=)))","óc chó kìa=)))","ổn không=)))","bất ổn à=)))","ơ kìaaa=)))","hăng hái đê=)))","chạy à=)))","tởn à=)))","kkkk=)))","mày dốt à=)))","cặc ngu=)))","cháy đê=)))","chat hăng lên=)))","cố lên=)))","mồ côi cay=)))","cay à=)))","cn chó ngu=)))","óc cặc kìa=)))","đĩ đú=)))","đú kìa=)))","cùn v=)))","r x=)))","hhhhh=)))","kkakak=)))","sao đú=)))","cặc con=)))","ngu kìa=)))","chat mạnh đê=)))","hăng ee=)))","ơ ơ ơ=)))","sủa cháy đê=)))","sủa mạnh eei=)))","mày óc à con=)))","tao cho m chạy à=)))","con đĩ ngu sủa=)))","mày chạy à con đĩ lồn=)))","con gái mẹ mày chết kìa=)))","bắt quả tang con chó chạy bố nè=)))","rồi lun nó méc mẹ à=)))","Zz xuất trận eiii=)))","Zz bá mà ơ=)))","bịa kìa ae=)))","mày bịa như con gái mẹ mày vậy=)))","rồi luôn con bede sợ rồi=)))","rồi rồi nó phèn kìa=)))","mày sợ rồi hả=)))","quốc thiên win sàn này mà=)))","kkk con bede bị j rồi kìa=)))","trời má ơi nó sợ bố à=)))","sồn miếng đi em=)))","sợ lắm pk=)))","mày làm j đc bố dọ=)))","con bede cay dái kiểu=)))","con bồ mày bị tao đụ tét lồn mà=)))","con đầu đất này=)))","nhìn nó sồn hài vl ae=)))","mày bede xuất trận à em=)))","con gái mẹ mày cầu xin tao kìa=)))","con bede sồn kìa=)))","sợ j đó=)))","mày bịa anh sợ mày à=)))","con chó bịa vậy=)))","bịa quá ko tốt đâu=)))","Zz xuất trận cmnr=)))","nhìn con bede sồn kìa=)))","sợ r hả=)))","nó sợ tớ kìa=)))","sồn gái mẹ mày đê=)))","bố bá mà=)))","ơ con bede mày cay mẹ rồi=)))","mày k có câu nào khác nữa à=)))","con bede bớt sồn mẹ mày đê=)))","cay j ó=)))","bịa mẹ j ghê vậy=)))","con bede mày làm ko lại anh à=)))","làm ko lại nên mới bịa nè=)))","sồn như cách mày chịch ghệ m đó em=)))","rồi lun nó tức kìa=)))","mày lỏ dái v=)))","con gái mẹ mày die r kìa=)))","sồn đê=)))","ơ ơ con bede=)))","hăng mẹ mày đê=)))","con bede ăn hiếp bố à=)))","con cay kìa=)))","cay boài mẹ r=)))","nói mày á em=)))","mày sợ tao mà=)))","mày thèm con cu bố mà=)))","ô ô mày tục tĩu bậy=)))","quéo cặc rồi à=)))","m sợ kìa=)))","ê ê tk ngu=)))","con béo m sợ kìa=)))","m ngu thật=)))","rén à=)))","nó rén tao thật r=)))","mày sợ tao òi=)))","m ngu kiàaa=)))","con chó sủa đê=)))","mày ngu vãi=)))","con đĩ mẹ mày=)))","mẹ mày die r à=)))","má ơi nó sồn kìa=)))","con đĩ mẹ m die kìa=)))","mẹ ơi=)))","m sợ kiàaa=)))","con sugar daddy=)))","ơ ơ sồn kìa=)))","sủa mẹ m đê con bede=)))","m sồn quá dạ=)))","hí hí=)))","má mày=)))","nhìn nó nch joke vl=)))","m béo vãi=)))","con chó béo v=)))","m béo v=)))","con điên eiii=)))","con gái mẹ mày kìa=)))","con culi sồn dọ=)))","Zz win mà=)))","ơ ơ bede=)))","sao mày béo vậy em=)))","ơ ơ=)))","con mẹ mày=)))","con đĩ mẹ mày=)))","gái mẹ mày die kìa=)))","mẹ m=)))","ê ê con chó=)))","đĩ mẹ mày=)))","sủa đê=)))","mẹ m die kìa=)))","bố win mà=)))","trời trời=)))","anh win mà=)))","mày dámm tranh vs anh à=)))","con điên boài=)))","sủa êyy=)))","m die kìa=)))","má mẹ m=)))","con die bầm=)))","ủa m sợ à=)))","m sợ anh mà=)))","con bede sợ r kìa=)))","j dọ=)))","gái mẹ m=)))","ô ô=)))","cười mẹ mày à=)))","m sợ kìa=)))","con điên=)))","con chó=)))","gái má m nè=)))","sồn kìa ơ=)))","Zz đấng sàn war mà=)))","bố bá mà=)))","m điên mà=)))","m die kìa=)))","mày sợ kiàa=)))","con tật rách chân à=)))","sồn như cách m die di em=)))","mẹ m=)))","m lbgt r à=)))","sa o j=)))","mày câm à=)))","mày câm mẹ rồi=)))","con chó cay anh=)))","con mẹ mày=)))","sồn v em=)))","die mẹ m r à=)))","con chó=)))","chết kiàa=)))","kìa kìa=)))","sa o sồn dọ=)))","chết kìa=)))","cdm tk não bò=)))","chó ơi=)))","sủa đê=)))","m cay t à em=)))","con chó sợ chạy kida=)))","hăng êiiii=)))","đồ con ngu=)))","con bede seen lén à=)))","a cho m chạy chx=)))","m sợ bố mà=)))","r r nó sợ r=)))","mày cay bố kìa=)))","kkk=)))","m sợ bố mà=)))","cayyy=)))","con chó ngôn kém v=)))","m ngu ngục mà=)))","con bede cay boài rồi kìa=)))","con chó xuất trận êyyy=)))","Zz win à=)))","ô Zz win mẹ r=)))","m béo m tự ti mà=)))","m bị bọn t đá mà=)))","sa o m sợ v=)))","đừng sợ mà=)))","sợ là kém cõi lắm đấy=)))","sa o m phèn vậy=)))","m phèn rõ mà=)))","ô con chó cái này=)))","con béo sợ à=)))","bố cấm m sợ nha=)))","t cho m sợ chx=)))","m ảo à=)))",
    "con chó ảo win kìa=)))","m béo vcl=)))","rên kinh vl=)))","bại bố à=)))","m bại bố mẹ kìa=)))","con chó bede=)))","sồn đê em=)))","con chó cay bẻm=)))","r xong chạy r kìa=)))","mày ngu vãi cặc=)))","con chó êyyy=)))","rồi xong nó cay bẻm òi=)))","mẹ m die thảm kìa=)))","con chó ngu vl=)))","r xong nó die r=)))","con mẹ mày ngu vãi=)))","r xong chạy r kìa=)))","con bede sồn đê=)))","mày chạy à=)))","hmm=)))","nó gần hết ngôn rồi à=)))","con mèo hoang hết ngôn kìa=)))","con chó cay boài=)))","con bẻm cay này=)))","rồi xog nó lên xe chạy bẻm mạng rồi=)))","con bot ngu này=)))","mày ngu và thần kinh vãi=)))","mày sồn đê em=)))","con chó cực nhọc v=)))","con giết mẹ mắng cha này=)))","ko lmj đc à=)))","hhh=)))","con bẻm sợ quéo cặc rồi=)))","mày sợ bố như ma mà=)))","Zz bá vl=)))","con bede xưng đấng à=)))","hot ỉa chạy mẹ rồi=)))","con bẻm=)))","mày định giết tg à=)))","con chó ngu hiểu sai nghĩa kìa=)))","tg là thời gian mà=)))","ô con chó ngu hiểu sai quê=)))","chó này quê v=)))","r r nó cắn kìa=)))","bố bá vl=)))","m sợ bố như sợ đò mà=)))","rồi xong nó chạy rồi=)))","con bẻm cay à=)))","bố cho cay chưa=)))","bố cấm mày cay mà=)))","con lồn dốt nát này=)))","mẹ m béo vl=)))","giảm mỡ đê=)))","con đĩ nhà nghèo=)))","nhìn m sồn trụ vs bot mắt cừi vl=)))","con chó m phèn v=)))","m nghèo mà em=)))","m chạy mẹ rồi à=)))","bố chưa cho chạy mà=)))","ngu v=)))","sồn ê=)))","chửi bố đê=)))","mày nhát v em=)))","bồ m bị chửi k kháng cự bảo vệ à=)))","tk hèn=)))","bố giết cả nhà m mà=)))","con chó tục v=)))","bot j kìa=)))","bịa à=)))","con chó dốt ngu bịa kiểu=)))","nhìn m phèn vl=)))","m dốt nát vãi=)))","m ko = 1 gốc tao mà=)))","m sợ bố mún die mà=)))","m đi đầu thai đê con chó êyyy=)))","mẹ m die bẻm r kìa=)))","mày đê cầu cứu đê=)))","gọi ng chửi bố đê=)))","m sợ tao mà=)))","con chó bẻm=)))","bố cấm m sợ tao mà=)))","sao m sợ tao vậy=)))","nó sợ tao à=)))","mẹ m die bầm kìa=)))","rồi xong=)))","nó die r=)))","con chó ngôn phèn=)))","m ngôn bẩn vl=)))","m phèn mà=)))","sủa mẹ m đê=)))","con chó dốt êyyy=)))","m chít mẹ m r=)))","sồn ào mẹ m đê=)))","con bẻm=)))","m sợ bố muốn die mà=)))","rồi xong nó sợ tao kìa=)))","bẻm êyyy=)))","m đú mà=)))","đú mà xạo kìa=)))","xạo lồn quá z=)))","chửi bố êyyy=)))","tk lbgt êyy=)))","m đâu r=)))","m đầu hàng à=)))","kk clm nó đầu hàng mẹ rồi kìa=)))","sao m đầu hàng vậy=)))","bố cho đầu hàng chx=)))","con đú này=)))","m đầu hàng lmj=)))","bố cho à=)))","bố chx đút cặc vô lồn bồ mày mà=)))","chx j đã đầu hàng rồi=)))","tk này đầu óc lớp 1 mà=)))","các con bẩn này=)))","chửi bố đê=)))","lũ lồn câm lặng kìa=)))","m sợ rồi à=)))","bt m sợ mà=)))","tao lập lại cho vui thôi=)))","chứ mày gà vãi lồn=)))","như tk đú=)))","m còn bede nx chứ=)))","con bede cay boài=)))","ko ai chửi bố nx hết vậy=)))","sợ à=)))","lũ cmay treo r à=)))","đuối nên treo à=)))","mày treo mẹ rồi=)))","phèn ghê trời ạ=)))","s m phèn v=)))","phèn vãi lồn=)))","con bede ngu này=)))","mày sợ rồi à=)))","bố win rõ mà=)))","mày sợ bố như sợ chó mà=)))","rên rĩ dưới thân bố à=)))","con bồ mày ngon đấy=)))","sủa eiii=)))","hăng eiiii=)))","các con chó êyy=)))","mày sợ tao òi=)))","tk bần hèn này=)))","sồn gái mẹ mày đi=)))","hmm=)))","sợ à=)))","con bede sợ r kìa=)))","ơ ơ sợ à=)))","đúng vl=)))","mày sợ tao r kìa=)))","hmm tk bẻm ơi=)))","sao dọ=)))","hăng như lúc m chửi t đi=)))","haizzz=)))","con chó bại=)))","mồ côi mà=)))","Zz win mẹ r=)))","tk bẻm ơi=)))","sao em cay chị dạ=)))","ko đc cay nè=)))","rồi luôn m giận chị à=)))","bố bá quá nên m giận đk=)))","cay bố cmnr=)))","sồn đê con chó êyy=)))","m die lặng mà=)))","sồn như con gái mẹ m anh xem đê=)))","con quỷ đầu đinh êyy=)))","ẳng mạnh đê=)))","hăng hái lên=)))","Zz win rõ bọn mày mà=)))","lũ mồ côi êy gào mạnh lên=)))","sồn mẹ m đê=)))","sủa đê=)))","con chó=)))","ẳng mạnh lên=)))","đĩ mẹ mày=)))","mày câm điếc à=)))","ê con chó đĩ phèn=)))","con gái má mày=)))","m bị tật à=)))","con điếm=)))","sủa cho bố=)))","con mẹ mày=)))","sủa cho bố đê=)))","con chó êyy=)))","con chó cái êyy=)))","cay anh à=)))","sao ơ=)))","dồi lun=)))","sợ r=)))","con bede bt sợ r=)))","sủa mẹ m đê=)))","ẳng cho bố êyy=)))","gái mẹ mày die mà=)))","con chó êyy=)))","mày câm à=)))","sồn như ban đầu đi bé êy=)))","kìa kìa nó sợ t kìa=)))","nó sợ tao mà ae=)))","bố m ra=)))","m ngu vl=)))","con đĩ phèn=)))","sủa đê=)))","m ẳng mẹ m đê chó=)))","m câm à=)))","bố cho câm chx=)))","ẳng vs bố đê=)))","con chó ơi=)))","sao v=)))","mày sợ bố à=)))","con đĩ=)))","mẹ m die thảm mà=)))","m ko nói j nx à=)))","tới mốt ko em=)))","m phèn vl=)))","ẳng mẹ m đê=)))","sủa đê=)))","m sợ tao m=)))","con chó ngu=)))","con gái mẹ m=)))","m bị câm mà=)))","sao ẳng lại r=)))","m die bầm mà=)))","ơ kìa=)))","con đĩ ơi=)))","sao m phèn v=)))","r lun=)))","nó sợ mik r=)))","k dám lmj nx à=)))","s m phèn v=)))","ơ con chó=)))","câm điếc à=)))","m bị dị tật à em=)))","con đĩ ơi=)))","s m phèn v=)))","m sủa đê=)))","câm r à=)))","m bị điếc mà=)))","sủa mạnh đê=)))","con mẹ mày=)))","m ngu mà=)))","Zz bá mà=)))","m cản đc Zz à con ngu=)))","m ảo à em=)))","r xong nó ảo r=)))","cay quá nên ảo=)))","con chó 10 năm nx ăn đc anh k=)))","con chó rên đi=)))","má mày=)))","con bede=)))","đĩ mẹ mày=)))","sủa đê=)))","con gái mẹ mày=)))","m câm mẹ r=)))","kkk=)))","sủa đê=)))","m sủa mạnh tí=)))","con đĩ mẹ mày=)))","con chó ơi=)))","con chó ơ sủa lẹ đi=)))","con mẹ m bede à=)))","kkk=)))","con chó êyy=)))","sủa đê=)))","mẹ mày câm mẹ m đê=)))","con bde sủa mạnh tí=)))","sủa lẹ đi tr=)))","m ngu mà=)))","sủa mạnh đê=)))","con đĩ mẹ mày=)))","ẳng to lên=)))","con chó êyyy=)))","đĩ má màyy sủa mạnh đê=)))","con đĩ mẹ mày die kìa=)))","r r xong lun=)))","đĩ má mày=)))","con chó ơi=)))","con đĩ má mày câm à=)))","r xong nó sồn kìa=)))","ơ ơ con chó=)))","mẹ mày=)))","câm điếc cmnr=)))","con chó êyyy=)))","sủa lẹ đê=)))","con gái má m=)))","ơ ơ sủa đi=)))","câm à=)))","sủa mẹ đê=)))","đĩ má mày câm à=)))","r xong chạy à=)))","con đĩ ơi m ngu mà em=)))","con chó=)))","con đĩ ơi=)))","r lun m câm à=)))","con bede tật câm mồm r à=)))","m sợ bố mà=)))","tr ơi sao đấy=)))","con đĩ má mày=)))","con đĩ ơi=)))","con chó ngu vl=)))","con chó ngu êyyy=)))","con gái mẹ mày=)))","sủa điên đê=)))","r xong nó chạy r=)))","m sợ hãi bố à=)))","sợ bố kìa=)))",
    "r r=)))","chạy r à=)))","chó ơi=)))","sủa đê=)))","mạnh mẽ lên=)))","Zz win à=)))","cha win mẹ rồi=)))","con bede sao cưỡng chế đc khôi=)))","ẳng đê=)))","mạnh lên=)))","con đĩ ơi=)))","bố bá mà=)))","sồn đê=)))","gái mẹ mày câm à=)))","r xong con bede=)))","m chít mẹ r à=)))","ẳng mẹ m đê=)))","m ngu vl=)))","sủa đê con chó=)))","m dốt mà=)))","câm điếc à=)))","con chó này bị ngu mẹ r=)))","sợ bố à=)))","câm điếc mẹ r kìa=)))","nhìn con bede sồn kìa=)))","sồn gái mẹ m đê=)))","con mẹ mày=)))","sủa đê đc k=)))","câm à=)))","đĩ mẹ mày tk óc bò=)))","sủa đêyyy=)))","má mày die à=)))","câm loạn à=)))","con gái mẹ mày=)))","sủa lẹ đi đc ko=)))","Zz bá vãi chó=)))","câm loạn à=)))","bố bá mà=)))","bọn m ghẻ tiền mà=)))","ẳng đê=)))","bố cân hết mà=)))","con đĩ mẹ mày=)))","mày ngu vl=)))","sủa đê=)))","sủa mạnh lên=)))","bố bá mà=)))","con đĩ má mày die à=)))","sủa đê con chó êyyy=)))","con gái mẹ mày=)))","r xong chạy r=)))","đĩ êyy=)))","m đái bậy à em=)))","con chó này nay hô tục v=)))","con đĩ mẹ mày die kìa=)))","r xong m chạy à=)))","sủa đê=)))","con bede êyy=)))","má mày câm kìa=)))","đĩ bà già mày=)))","sủa êyy=)))","ẳng mẹ đê=)))","con chó dốt=)))","con đĩ mẹ mày=)))","ơ ơ câm à=)))","con bede cắn bố êy=)))","m lm thân bố mà=)))","con chó êy=)))","m ngu vl=)))","con chó béo=)))","con đĩ bede=)))","con mẹ m=)))","sủa đê=)))","m câm à=)))","con chó m phế mà=)))","mẹ m die thảm mà=)))","m là con đĩ bede mà=)))","sồn đê=)))","mẹ m die mà=)))","r xong=)))","m sợ r à=)))","kkk=)))","nó sợ r kìa=)))","ê con bede êyy=)))","con chó ngu vl=)))","sủa lẹ đi đc k=)))","con mẹ m die kiàaa=)))","r xog=)))","kkk=)))","sợ Zz đk=)))","má đĩ bê đê sợ bố kìa=)))","sủa mẹ m đê=)))","con chó êyy=)))","m câm con đĩ mẹ m r=)))","câm là má m die nè=)))","sủa đê=)))","cay à=)))","m sợ t rõ mà=)))","nào em lớn=)))","ơ ơ=)))","con bede eyyy=)))","m sợ rõ mà=)))","sao sợ=)))","con mắm thúi này=)))","sồn đê=)))","hăng mẹ m đê=)))","con chó ngu êyy=)))","m phế mò=)))","gà vl=)))","m phế mà em=)))","sủa mạnh lên đê=)))","phát biểu và nhanh nhẹn lên=)))","chậm dọ=)))","con bede êyyy=)))","sao chậm v=)))","m sợ bố mà=)))","ơ kìa=)))","sồn mẹ m đê=)))","con đĩ bede=)))","m sợ bố vãi cứk mà=)))","?=)))","ngôn m phèn vl=)))","m sợ bố ro mà=)))","hăng hái đê=)))","chậm v=)))","sủa mạnh đê chó=)))","m phế mà=)))","Zz win mẹ r=)))","con bede cẩm tú=)))","con mẹ mày=)))","m phế mà ơ=)))","bịa à=)))","sao bịa v=)))"]
GROUP_TITLES = [
    "☄🚀𝙏𝙤𝙠𝙮𝙤 𝘽𝙖 𝙎𝙖𝙣 𝙏𝙧𝙚𝙤🤯💫💤",
    "☄️🚀𝘾𝙝𝙖 𝙏𝙤𝙠𝙮𝙤 𝘿𝙚𝙣 𝘽𝙤𝙣 𝙆𝙞𝙙 𝙋𝙝𝙖𝙞 𝙎𝙤✈💔🌠💤",
    "☄🚀𝘾𝙝𝙖 𝙏𝙤𝙠𝙮𝙤 𝘾𝙖𝙣 𝘼𝙡𝙡 𝘽𝙤𝙣 𝙆𝙞𝙙 𝙈𝙖𝙥🌌✈💤",
    "☄️🚀𝘾𝙝𝙖 𝙏𝙤𝙠𝙮𝙤 𝘾𝙖𝙣 𝘼𝙡𝙡 𝘽𝙤𝙣 𝙆𝙞𝙙 𝙏𝙚𝙡𝙚𝙜𝙧𝙖𝙢🌟💫✈💤",
    "☄️🚀𝘽𝙪 𝘾𝙖𝙘 𝙏𝙤𝙠𝙮𝙤 𝙉𝙚 𝙗𝙤𝙣 𝙆𝙞𝙙🌌😜✈💤",
    "☄️🚀𝙎𝙤 𝘾𝙝𝙖 𝙏𝙤𝙠𝙮𝙤 𝘿𝙚𝙣 𝙉𝙤𝙞 𝙈𝙚𝙘 𝙈𝙚✈🌠🌸💤",
    "☄️🚀𝙑𝙚 𝘽𝙪 𝙏𝙞 𝙈𝙚 𝘿𝙞 𝙀𝙢 𝘾𝙝𝙖 𝙏𝙤𝙠𝙮𝙤 𝙒𝙞𝙣✈🌌🐲💤",
    "☄️🚀 𝙏𝙤𝙠𝙮𝙤 𝙗𝙤 𝙢𝙖𝙮 𝙗𝙖 𝙨𝙖𝙣 𝙖𝙡𝙡 𝙩𝙚𝙡𝙚𝙜𝙧𝙖𝙢✈🌌🥀💤",
    "☄️🚀𝙏𝙤𝙠𝙮𝙤 𝙏𝙧𝙚𝙤 𝘿𝙚𝙣 𝘽𝙤𝙣 𝙉𝙤𝙩𝙞 𝙋𝙝𝙖𝙞 𝙎𝙤✈💫🐉💤",
]

def purify(text):
    return re.sub(r'[^\w\s\d\.,!?:;=\-\(\)]+', '', text).strip()

async def del_cmd(update: Update):
    try: await update.message.delete()
    except: pass
    
async def doi_ten(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    cid = update.effective_chat.id

    if cid in auto_title_tasks:
        auto_title_tasks[cid].cancel()
        del auto_title_tasks[cid]
        await asyncio.sleep(0.1)

    auto_title_tasks[cid] = asyncio.create_task(
        auto_change_title(context.bot, cid)
    )

    await context.bot.send_message(cid, "𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐𓆪𓂁𖣘")
    
async def auto_change_title(bot, chat_id):
    try:
        while chat_id in auto_title_tasks:
            for title in GROUP_TITLES:
                try:
                    await bot.set_chat_title(chat_id, title)
                except:
                    pass
                await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
        
async def attack_engine(bot: Bot, chat_id, targets, tid, mode, custom, token):
    try:
        while tid in stop_events and not stop_events[tid].is_set():
            try:
                random.shuffle(targets)
                grp = targets[:5]
                if mode == "sp3":
                    msg = purify(random.choice(MESSAGES))
                    lines = [f"<a href='tg://user?id={u}'>\u200b</a>" for u in grp]
                    text = "".join(lines) + msg
                elif mode == "sp1":
                    lines = [f"<a href='tg://user?id={u}'>{html.escape(purify(random.choice(MESSAGES)))}</a>" for u in grp]
                    text = "\n".join(lines)
                elif mode == "sp2":
                    msg_val = custom if custom else "Sủa"
                    lines = [f"<a href='tg://user?id={u}'>{html.escape(msg_val)}</a>" for u in grp]
                    text = "\n".join(lines)
                else:
                    raw_msg = random.choice(MESSAGES)
                    text = "".join([f"<a href='tg://user?id={u}'>\u200b\u200c\u200d</a>" for u in grp]) + f"{raw_msg} {SPECIAL_MESSAGE}"
                if text:
                    m = await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                    if token not in sent_messages_dict: sent_messages_dict[token] = []
                    sent_messages_dict[token].append(m.message_id)
            except: 
                await asyncio.sleep(current_delay * 10)
            await asyncio.sleep(current_delay)
    except asyncio.CancelledError:
        pass

async def combined_attack(bot, chat_id, targets, tid, mode, custom, token):
    try:
        spam_task = asyncio.create_task(attack_engine(bot, chat_id, targets, tid, mode, custom, token))
        title_task = asyncio.create_task(auto_change_title(bot, chat_id))
        auto_title_tasks[chat_id] = title_task

        await asyncio.gather(spam_task, title_task, return_exceptions=True)
    except asyncio.CancelledError:
        spam_task.cancel()
        title_task.cancel()
        await asyncio.gather(spam_task, title_task, return_exceptions=True)
        raise
    finally:
        if chat_id in auto_title_tasks:
            del auto_title_tasks[chat_id]
            
async def handle_war_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    await del_cmd(update)
    
    cmd = update.message.text.split()[0].lower() 
    cid, tok = update.effective_chat.id, context.application.bot.token
    tid = f"{cid}_{tok.split(':')[0]}"
    
    if tid in combined_tasks:
        combined_tasks[tid].cancel()
        del combined_tasks[tid]
    if tid in stop_events:
        stop_events[tid].set()
        del stop_events[tid]
    if cid in auto_title_tasks:
        auto_title_tasks[cid].cancel()
        del auto_title_tasks[cid]
    await asyncio.sleep(0.01)
    
    stop_events[tid] = Event()
    
    uids = []
    txt = ""
    flag = False
    
    if update.message.reply_to_message:
        replied_user = update.message.reply_to_message.from_user
        if replied_user:
            uids.append(replied_user.id)
    
    if context.args:
        for i, a in enumerate(context.args):
            if a.isdigit() and not flag:
                uids.append(int(a))
            else:
                flag = True
                txt = " ".join(context.args[i:])
                break
    else:
        if update.message.reply_to_message and update.message.reply_to_message.text:
            txt = update.message.reply_to_message.text
    
    if not uids: 
        return
    
    m_mode = "sp1"
    task = asyncio.create_task(combined_attack(context.application.bot, cid, uids, tid, m_mode, txt, tok))
    combined_tasks[tid] = task
    if not hasattr(context.application, 'attack_tasks'):
        context.application.attack_tasks = []
    context.application.attack_tasks.append(task)

async def handle_war(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    await del_cmd(update)
    
    cmd = update.message.text.split()[0].lower()
    cid, tok = update.effective_chat.id, context.application.bot.token
    tid = f"{cid}_{tok.split(':')[0]}"
    
    if tid in stop_events: stop_events[tid].set()
    await asyncio.sleep(0.01)
    stop_events[tid] = Event()
    
    uids = []
    txt = ""
    flag = False
    
    if update.message.reply_to_message:
        replied_user = update.message.reply_to_message.from_user
        if replied_user:
            uids.append(replied_user.id)
    
    if context.args:
        for i, a in enumerate(context.args):
            if a.isdigit() and not flag:
                uids.append(int(a))
            else:
                flag = True
                txt = " ".join(context.args[i:])
                break
    else:
        if update.message.reply_to_message and update.message.reply_to_message.text:
            txt = update.message.reply_to_message.text
    
    if not uids: 
        return
    
    m_mode = {"/sp1":"sp1", "/sp2":"sp2", "/sp3":"sp3"}.get(cmd, "sp")
    task = asyncio.create_task(attack_engine(context.application.bot, cid, uids, tid, m_mode, txt, tok))
    if not hasattr(context.application, 'attack_tasks'):
        context.application.attack_tasks = []
    context.application.attack_tasks.append(task)

async def handle_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    await del_cmd(update)
    
    global current_delay
    
    try:
        if not context.args:
            return
            
        val = float(context.args[0])
        
        if val < 0.001: 
            val = 0.001
        if val > 100.0: 
            val = 100.0
            
        current_delay = val
        
        if context.application.bot.token == BOT_TOKENS[0]:
            await context.application.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=f" 𝑺𝑷𝑬𝑬𝑫 : {current_delay}"
            )
    except:
        pass

async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    await del_cmd(update)
    cmd = update.message.text.split()[0].lower()
    global MUTE_ALL_MODE

    if "all" in cmd:
        MUTE_ALL_MODE = ("camall" in cmd)
        if context.application.bot.token == BOT_TOKENS[0]:
            await context.application.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"<b>𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘 : \n {' Đã Đeo Rọ Cho All Group' if MUTE_ALL_MODE else 'Đã Mở Rọ All Group'}</b>",
                parse_mode=ParseMode.HTML
            )
        return

    uid = (
        update.message.reply_to_message.from_user.id
        if update.message.reply_to_message
        else (int(context.args[0]) if context.args and context.args[0].isdigit() else None)
    )

    if uid:
        if "cam" in cmd:
            muted_users.add(uid)
        else:
            muted_users.discard(uid)

        if context.application.bot.token == BOT_TOKENS[0]:
            msg = f"<a href='tg://user?id={uid}'>𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘</a>"
            await context.application.bot.send_message(
                chat_id=update.effective_chat.id,
                text=msg,
                parse_mode=ParseMode.HTML
            )


async def handle_sys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    await del_cmd(update)

    cmd = update.message.text.split()[0].lower()
    cid = update.effective_chat.id

    if cmd == "/dung":
        for k in list(stop_events.keys()):
            if str(cid) in k:
                stop_events[k].set()
                if k in combined_tasks:
                    combined_tasks[k].cancel()
                    del combined_tasks[k]

        if cid in auto_title_tasks:
            auto_title_tasks[cid].cancel()
            del auto_title_tasks[cid]

        if context.application.bot.token == BOT_TOKENS[0]:
            await context.application.bot.send_message(
                chat_id=cid,
                text="𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘"
            )

    elif cmd == "/xoa":
        tsks = []
        for t, ids in sent_messages_dict.items():
            for mid in ids:
                tsks.append(
                    context.application.bot_data[t].delete_message(cid, mid)
                )
            sent_messages_dict[t] = []

        await asyncio.gather(*tsks, return_exceptions=True)

    elif cmd == "/id":
        if context.application.bot.token != BOT_TOKENS[0]:
            return

        msg = update.message
        target_id = None

        if msg.reply_to_message:
            target_id = msg.reply_to_message.from_user.id

        elif context.args:
            arg = context.args[0]
            if arg.isdigit():
                target_id = int(arg)
            else:
                if not arg.startswith("@"):
                    arg = "@" + arg
                try:
                    user = await context.bot.get_chat(arg)
                    target_id = user.id
                except:
                    pass

        if not target_id and msg.entities:
            for ent in msg.entities:
                if ent.type == "text_mention":
                    target_id = ent.user.id
                    break

        if not target_id:
            target_id = msg.from_user.id

        await context.bot.send_message(
            chat_id=cid,
            text=f"<b>UID :  </b> <code>{target_id}</code> ",
            parse_mode=ParseMode.HTML
        )

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if context.application.bot.token != BOT_TOKENS[0]:
        return
    
    chat_id = update.effective_chat.id
    
    if update.message.reply_to_message:
        target_admin_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_admin_id = int(context.args[0])
        except:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ ID không hợp lệ",
                parse_mode=ParseMode.HTML
            )
            return
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Vui lòng reply tin nhắn hoặc nhập ID",
            parse_mode=ParseMode.HTML
        )
        return
    
    ADMIN_IDS.add(target_admin_id)
    response_message = f"<b>𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘 𝐔𝐩𝐝𝐚𝐭𝐞:</b>\n\nĐã Thêm Admin: <code>{target_admin_id}</code>"
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=response_message,
        parse_mode=ParseMode.HTML
    )

async def xoa_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if context.application.bot.token != BOT_TOKENS[0]:
        return
    
    chat_id = update.effective_chat.id
    
    if update.message.reply_to_message:
        target_admin_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_admin_id = int(context.args[0])
        except:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ ID không hợp lệ",
                parse_mode=ParseMode.HTML
            )
            return
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Vui lòng reply tin nhắn hoặc nhập ID",
            parse_mode=ParseMode.HTML
        )
        return
    
    ADMIN_IDS.discard(target_admin_id)
    response_message = f"<b>𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘 𝐔𝐩𝐝𝐚𝐭𝐞:</b>\n\nĐã Xóa Admin: <code>{target_admin_id}</code>"
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=response_message,
        parse_mode=ParseMode.HTML
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if context.application.bot.token != BOT_TOKENS[0]:
        return

    await del_cmd(update)

    text = (
        "<b>𖣘𓂄𓆩𝑩𝑨 𝑺𝑨𝑵 𝑻𝑶𝑲𝒀𝑶 𓆪𓂁𖣘</b>\n\n"
        "╔━━ 𖣘𓂄𓆩𝑺𝑷𝑨𝑴𓆪𓂁𖣘 ━╗\n"
        "║⋆˚ ✦ ˚ ✧ ★⋆˚⋆. ✧ . ★⋆˚\n"
        "║ ✧ /sp ➣ 𝑇𝑎𝑔 𝐿𝑎𝑔 𝐺ℎ𝑜𝑠𝑡\n"
        "║ ✦ /sp1 ➢ 𝑇𝑎𝑔 𝐼𝑛𝑙𝑖𝑛𝑒\n"
        "║ ✧ /sp2 ➣ 𝑇𝑒𝑥𝑡 𝐼𝑛𝑙𝑖𝑛𝑒\n"
        "║ ✦ /sp3 ➢ 𝑇𝑎𝑔 𝐺ℎ𝑜𝑠𝑡\n"
        "║ ✧ /gr ➢ 𝑆𝑝𝑎𝑚 𝐺𝑟𝑜𝑢𝑝 𝑁𝑎𝑚𝑒\n"
        "║ ✦ /all ➢ 𝑆𝑝𝑎𝑚 𝐺𝑟𝑜𝑢𝑝 \n" 
        "║⋆˚ ✦ ˚ ✧ ★⋆˚✦. ˚✧.★⋆˚\n"
        "╚━━━━━━━━━━━━━━╝\n\n"
        "╔━ 𖣘𓂄𓆩𝑺𝑻𝑨𝑻𝑼𝑺𓆪𓂁𖣘 ━╗\n"
        "║⋆˚ ✧ ˚ ✦✧ ★⋆˚⋆˚✦.\n"
        "║ ✦ /delay ➣ 𝑆𝑝𝑒𝑒𝑑\n"
        "║ ✧ /dung ➢ 𝑆𝑡𝑜𝑝 𝑆𝑝𝑎𝑚\n"
        "║ ✦ /id ➣ 𝐼𝑛𝑓𝑜 𝑈𝑠𝑒𝑟\n"
        "║⋆˚ ✧ ˚ ✦ ★⋆˚✧⋆✧˚\n"
        "╚━━━━━━━━━━━━━━╝\n\n"
        "╔━ 𖣘𓂄𓆩𝑫𝑬𝑳𝑬𝑻𝑬𓆪𓂁𖣘 ━╗\n"
        "║⋆˚ ✦ ˚ ✧ ★⋆˚⋆˚　✦.  ˚\n"
        "║ ✦ /xoa ➢ 𝐷𝑒𝑙𝑒𝑡𝑒 𝑇𝑖𝑛 𝐵𝑜𝑡\n"
        "║ ✧ /cam ➣ 𝐿𝑜𝑐𝑘 𝑈𝑠𝑒𝑟\n"
        "║ ✦ /sua ➢ 𝑈𝑛𝑙𝑜𝑐𝑘 𝑈𝑠𝑒𝑟\n"
        "║ ✧ /camall ➣ 𝐿𝑜𝑐𝑘 𝐺𝑟𝑜𝑢𝑝\n"
        "║ ✦ /suaall ➢ 𝑈𝑛𝑙𝑜𝑐𝑘 𝐺𝑟𝑜𝑢𝑝\n"
        "║⋆˚ ✦ ˚ ✧ ★⋆˚⋆˚　✧.  \n"
        "╚━━━━━━━━━━━━━━━╝\n\n"
        "╔━━𖣘𓂄𓆩𝑨𝑫𝑴𝑰𝑵𓆪𓂁𖣘━╗\n"
        "║⋆˚ ✦ ˚ ✧ ★⋆˚⋆˚　✦.  ˚\n"
        "║ ✦ /add ➣ 𝐴𝑑𝑑 𝐴𝑑𝑚𝑖𝑛\n"
        "║ ✧ /xoaad ➢ 𝐷𝑒𝑙𝑒𝑡𝑒 𝐴𝑑𝑚𝑖𝑛\n"
        "║⋆˚ ✧ ˚ ✦ ★⋆˚⋆˚　✧.  \n"
        "╚━━━━━━━━━━━━━━╝"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="HTML"
    )

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    uid = update.effective_user.id

    if uid in ADMIN_IDS or uid in MY_BOT_IDS:
        return

    if MUTE_ALL_MODE or uid in muted_users:
        try:
            await update.message.delete()
        except:
            pass

async def boot(token, pool):
    try:
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler(["sp", "sp1", "sp2", "sp3"], handle_war))
        app.add_handler(CommandHandler("delay", handle_delay))
        app.add_handler(CommandHandler(["dung", "xoa", "id"], handle_sys))
        app.add_handler(CommandHandler(["cam", "sua", "camall", "suaall"], handle_admin))
        app.add_handler(CommandHandler(["add"], add_admin))
        app.add_handler(CommandHandler(["xoaad"], xoa_admin))
        app.add_handler(CommandHandler("menu", handle_menu))
        app.add_handler(CommandHandler("gr", doi_ten))
        app.add_handler(CommandHandler("all", handle_war_all))
        app.add_handler(MessageHandler(filters.ALL, monitor))
        
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        
        pool.append(app)
        colors = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m", "\033[97m"]
        reset = "\033[0m"
        rainbow = "".join([colors[i % len(colors)] + "●" for i in range(13)]) + reset
        print(f"{colors[len(pool) % len(colors)]}⚡ {token[:8]}... | {rainbow} | 𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘 | Bot {len(pool)}/13 Online{reset}")
        return app
    except Exception as e:
        print(f"💥 {token[:8]}... | 𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘 | Lỗi: {str(e)[:30]}")
        return None

async def tat_ung_dung_bot(ung_dung_bot):
    try:
        if ung_dung_bot.updater:
            if ung_dung_bot.updater.running:
                await ung_dung_bot.updater.stop()
        if ung_dung_bot.running:
            await ung_dung_bot.stop()
        if ung_dung_bot.initialized:
            await ung_dung_bot.shutdown()
    except Exception as loi_tat_bot:
        chuoi_loi_tat = f"Loi tat bot: {loi_tat_bot}"
        print(chuoi_loi_tat)

async def main():
    danh_sach_pool = []
    
    banner_hien_thi = "\n"
    banner_hien_thi += "\033[91m╔══════════════════════════════════════════════════════╗\n"
    banner_hien_thi += "\033[92m║      \033[93m🌈 \033[94m𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘 \033[95m🌈      ║\n"
    banner_hien_thi += "\033[96m║            \033[97mKhởi Động Hệ Thống\033[96m            ║\n"
    banner_hien_thi += "\033[91m╚══════════════════════════════════════════════════════╝\033[0m\n"
    print(banner_hien_thi)
    
    try:
        danh_sach_nhiem_vu_khoi_dong = []
        for token_cua_bot in BOT_TOKENS:
            nhiem_vu_moi = boot(token_cua_bot, danh_sach_pool)
            danh_sach_nhiem_vu_khoi_dong.append(nhiem_vu_moi)
            
        ket_qua_khoi_dong = await asyncio.gather(*danh_sach_nhiem_vu_khoi_dong, return_exceptions=True)
        
        danh_sach_token_hoat_dong = []
        for ung_dung in danh_sach_pool:
            token_bot_dang_chay = ung_dung.bot.token
            danh_sach_token_hoat_dong.append(token_bot_dang_chay)
            
        for ung_dung in danh_sach_pool:
            ung_dung.bot_data["all"] = danh_sach_token_hoat_dong
            for token_dang_xet in danh_sach_token_hoat_dong:
                if ung_dung.bot.token == token_dang_xet:
                    ung_dung.bot_data[token_dang_xet] = ung_dung.bot
                else:
                    for bot_trong_danh_sach in danh_sach_pool:
                        if bot_trong_danh_sach.bot.token == token_dang_xet:
                            ung_dung.bot_data[token_dang_xet] = bot_trong_danh_sach.bot
                            break
        
        so_luong_bot_song = len(danh_sach_pool)
        tong_so_luong_bot = len(BOT_TOKENS)
        
        chuoi_thong_bao_thanh_cong = "\n\033[95m════════════════════════════════════════════════════════════\033[0m\n"
        chuoi_thong_bao_thanh_cong += f"   \033[92mĐã khởi động {so_luong_bot_song}/{tong_so_luong_bot} Bot thành công! \033[96m✨\033[0m\n"
        chuoi_thong_bao_thanh_cong += "   \033[93m𖣘𓂄𓆩𝑯𝒐𝒕 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘 \033[94msẵn sàng chiến đấu! \033[91m🔥\033[0m\n"
        chuoi_thong_bao_thanh_cong += "\033[95m════════════════════════════════════════════════════════════\033[0m\n"
        print(chuoi_thong_bao_thanh_cong)
        
        su_kien_duy_tri_hoat_dong = asyncio.Event()
        await su_kien_duy_tri_hoat_dong.wait()
            
    except KeyboardInterrupt:
        print("\n\033[91m════════════════════════════════════════════════════════════\033[0m")
        print("   \033[93m🛑 Đang tắt các bot...\033[0m")
        danh_sach_nhiem_vu_tat = []
        for ung_dung in danh_sach_pool:
            nhiem_vu_tat = tat_ung_dung_bot(ung_dung)
            danh_sach_nhiem_vu_tat.append(nhiem_vu_tat)
        await asyncio.gather(*danh_sach_nhiem_vu_tat, return_exceptions=True)
        print("   \033[92m✅ Đã tắt tất cả bot!\033[0m")
        print("   \033[96m𖣘𓂄𓆩𝑯𝒐?? 𝑾𝒂𝒓 𝑻𝒐𝒌𝒚𝒐 𓆪𓂁𖣘 \033[95mtạm biệt! \033[91m👋\033[0m")
        print("\033[91m════════════════════════════════════════════════════════════\033[0m")
    except Exception as loi_main:
        chuoi_loi_chinh = f"Lỗi khởi chạy hệ thống: {loi_main}"
        print(chuoi_loi_chinh)

if __name__ == "__main__":
    try:
        vong_lap_su_kien = asyncio.new_event_loop()
        asyncio.set_event_loop(vong_lap_su_kien)
        vong_lap_su_kien.run_until_complete(main())
    except KeyboardInterrupt:
        he_thong_thoat = 0
        sys.exit(he_thong_thoat)
    except Exception as loi_khoi_tao:
        chuoi_loi_hien_thi = f"Lỗi từ hệ điều hành Termux: {loi_khoi_tao}"
        print(chuoi_loi_hien_thi)
