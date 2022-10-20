import os
from datetime import *
from random import *

import praw
import requests
from dotenv import load_dotenv

from quotes import quotes
from sql import *
import json



class STANNY_B:
    def __init__(self):

        # Load in credentials from .env
        load_dotenv()

        # Set the bot's username
        self.bot_username = os.getenv('reddit_username')

        self.webhook_url = os.getenv('webhook')

        # Initialize a Reddit object
        self.reddit = praw.Reddit(
            client_id=os.getenv('client_id'),
            client_secret=os.getenv('client_secret'),
            password=os.getenv('password'),
            user_agent=os.getenv('user_agent'),
            username=self.bot_username
        )

        # Set the subreddit to monitor
        self.subreddit = self.reddit.subreddit('vizzy_t_test+freefolk')

        # Pull in quotes from quotes.py
        self.quotes = quotes

        # Lazy variables for noting used quotes to keep from using them again within the hour
        self.posted = []
        self.posted_hour = datetime.now().hour

        # Whelp, time to roast my kiddo alive...
        self.run()

    def send_webhook(self, body):
        """Use webhooks to notify admin on Discord"""
        data = {'content': body, 'username': 'Stanny-B-Bot'}
        requests.post(self.webhook_url, data=data)

    def kiddo_burning(self, redditObject):
        readComments = getComments()
        if redditObject.author == None:
            pass
        elif redditObject.id in readComments or redditObject.author.name == self.bot_username:
            pass
        else:
            to_check = redditObject.body.lower()

            if "mannis" in to_check or "stanny b" in to_check:
                response = ""
                while not response:
                    seed()
                    num = randint(0, len(self.quotes) - 1)
                    if datetime.now().hour != self.posted_hour or len(self.posted) > len(self.quotes) - 5:
                        self.posted = []
                        self.posted_hour = datetime.now().hour

                    if num in self.posted:
                        pass
                    else:
                        try:
                            response = self.quotes[num]
                            if "{}" in response:
                                try:
                                    response = response.format(redditObject.author.name)
                                except:
                                    # Surely there's a better way...
                                    response = response.format(redditObject.author.name,redditObject.author.name)

                            redditObject.reply(body=response)
                            self.posted.append(num)
                            redditObject.upvote()
                            writeComment(redditObject.id)
                            link = f"\n{redditObject.author.name}: {to_check}\nResponse: **'{response}'** \nLink - https://www.reddit.com{redditObject.permalink}"
                            self.send_webhook(link)
                        except Exception as e:
                            print(e)
                            link = F'ERROR - {e}\nLink - https://www.reddit.com{redditObject.permalink}'
                            self.send_webhook(link)

    def run(self):
        print("STANNIS THE MANNIS is online.")

        for comment in self.subreddit.stream.comments():
            self.kiddo_burning(comment)
            requests.get('https://hc-ping.com/2bd71f62-d162-4daa-ad40-5374fb36b3b6')

stanny = STANNY_B()
