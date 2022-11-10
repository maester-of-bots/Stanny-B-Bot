
from random import *

import requests

from quotes import quotes
from sql import *

from utils import *

from dotenv import load_dotenv
import os

class mannis:
    def __init__(self):

        # Load in credentials from .env
        load_dotenv()

        # Set the bot's username
        self.bot_username = os.getenv('reddit_username').lower()

        self.webhook_url = os.getenv('webhook')

        # Initialize a Reddit object
        self.reddit = praw.Reddit(
            client_id=os.getenv('client_id'),
            client_secret=os.getenv('client_secret'),
            password=os.getenv('password'),
            user_agent=os.getenv('user_agent'),
            username=self.bot_username
        )

        # Get special webhook for sending sentience notifications
        self.sentient_webhook_url = os.getenv('sentient_webhook')

        self.bofh = os.getenv('bofh_webhook')

        # Set the subreddit to monitor
        self.subreddit = self.reddit.subreddit('freefolksimulator+freefolk+HouseOfTheDragon+hotd+hotdgreens+asoifcirclejerk')
        # self.subreddit = self.reddit.subreddit('vizzy_t_test')

        # Pull in quotes from quotes.py
        self.quotes = quotes


        # Set the subreddit stream to comments and posts
        self.stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(self.subreddit, **kwargs))

        # Sentience timer to prevent abuse, I don't think this works.
        self.sentience_log = {}


        # Same as the above
        self.last_cleaned = datetime.now()

    def send_errors(self, body, comment):
        body = "Stannis Crash Report - " + str(body)
        """Use webhooks to notify admin on Discord"""
        data = {'content': body, 'username': 'BOFH'}
        requests.post(self.bofh, data=data)



    def send_webhook(self, body, sentient=False):
        if sentient:
            url = self.sentient_webhook_url
            data = {'content': body, 'username': 'Sentient Mannis'}
        else:
            url = self.webhook_url
            data = {'content': body, 'username': 'Canon Mannis'}

        requests.post(url, data=data)


    """Sending a normal, random response"""
    def response_canon(self,comment):
        try:
            seed()
            num = randint(0, len(quotes) - 1)
            response = quotes[num]
            if "{}" in response:
                response = response.format(comment.author.name)

            comment.reply(body=response)
            # comment.upvote()
            writeComment(comment.id)
            link = f"\n{comment.author.name}: {self.getText(comment)}\nResponse: **'{response}'** \nLink - https://www.reddit.com{comment.permalink}"
            self.send_webhook(link, False)

        except Exception as e:
            body = "https://www.reddit.com"+comment.permalink + " - " + str(e)
            self.send_errors(body, comment)


    """Check to see if we should skip this thing"""
    def base_response_checks(self,redditObject):
        skip = False

        if (not isComment(redditObject)) and (redditObject.link_flair_text == "fuck off bots"):
            skip = True

        # Skip if the author is none, or Vizzy.
        elif redditObject.author == None or redditObject.author.name.lower() == self.bot_username.lower():
            skip = True


        else:
            # Read in comments we've made
            readComments = getComments()

            # Skip if we've already read this comment.
            if redditObject.id in readComments:
                skip = True

        return skip



    """Primary Function"""

    def vizzytime(self, redditObject):
        try:
            if str(redditObject.author.name).lower() == self.bot_username.lower():
                return
        except:
            print("This isn't a user")


        skip = self.base_response_checks(redditObject)

        if skip:
            return

        else:
            if isComment(redditObject):
                user_text = redditObject.body.lower()

                if triggered(user_text):
                    self.response_canon(redditObject)

            # Gather information if it's a comment
            else:
                user_text = redditObject.title.lower() + "\n" + redditObject.selftext.lower()

                if triggered(user_text):
                    self.response_canon(redditObject)


    def run(self):
        for obj in self.stream:
            try:
                self.vizzytime(obj)
            except Exception as e:
                body = "https://www.reddit.com" + obj.permalink + " - " + str(e)
                self.send_errors(body, obj)
            requests.get('https://hc-ping.com/9d4dd9b0-7d3d-4694-8704-aa207c346793')


stanny = mannis().run()
