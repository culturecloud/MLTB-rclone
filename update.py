# Source: https://github.com/anasty17/mirror-leech-telegram-bot/blob/master/update.py

import logging
from os import path as ospath, environ
from subprocess import run as srun
from pymongo import MongoClient
from dotenv import load_dotenv
from subprocess import run as srun

LOGGER = logging.getLogger(__name__)

if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

LOGGER.info("Running updater script...")

CONFIG_ENV = environ.get('CONFIG_ENV', None)
if CONFIG_ENV:
    LOGGER.info("CONFIG_ENV variable found! Downloading config file ...")
    download_file = srun(["curl", "-sL", f"{CONFIG_ENV}", "-o", "config.env"])
    if download_file.returncode == 0:
        LOGGER.info("Config file has been downloaded as 'config.env'")
    else:
        LOGGER.error("Something went wrong while downloading config file! please recheck the CONFIG_ENV variable")
        exit(1)
        
load_dotenv('config.env', override=True)

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    LOGGER.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

bot_id = int(BOT_TOKEN.split(':', 1)[0])

DATABASE_URL = environ.get('DATABASE_URL', '')
if len(DATABASE_URL) == 0:
    DATABASE_URL = None
    
DATABASE_NAME = environ.get('DATABASE_NAME', '')
if len(DATABASE_NAME) == 0:
    DATABASE_NAME = 'RCMLTB'

if DATABASE_URL is not None:
    conn = MongoClient(DATABASE_URL)
    db = conn.DATABASE_NAME
    if config_dict := db.settings.config.find_one({'_id': bot_id}):  #retrun config dict (all env vars)
        environ['UPSTREAM_REPO'] = config_dict['UPSTREAM_REPO']
        environ['UPSTREAM_BRANCH'] = config_dict['UPSTREAM_BRANCH']
    conn.close()
    
UPGRADE_PKGS = environ.get('UPGRADE_PKGS', 'False')
if UPGRADE_PKGS.lower() == 'true':
    srun(["pip3", "install", "--no-cache-dir", "-Ur libraries.txt"])

UPSTREAM_REPO = environ.get('UPSTREAM_REPO', '')
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = None

UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH', '')
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = 'master'

if UPSTREAM_REPO is not None:
    if ospath.exists('.git'):
        srun(["rm", "-rf", ".git"])

    update = srun([f"git init -q \
            && git config --global user.email sam.agd@outlook.com \
            && git config --global user.name rctb \
            && git add . \
            && git commit -sm update -q \
            && git remote add origin {UPSTREAM_REPO} \
            && git fetch origin -q \
            && git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)

    if update.returncode == 0:
        LOGGER.info('Successfully updated from UPSTREAM_REPO')
    else:
        LOGGER.error('Something went wrong while updating, check UPSTREAM_REPO if valid or not!')
