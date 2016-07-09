#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import GuessANumberApi

from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
		def get(self):
				"""Send a reminder email to each User with an email about games.
				Called every hour using a cron job"""

				# 
				unfinished_games = Game.query(Game.finished != True).fetch()

				user_ids = []
				for game in unfinished_games:
					if game.player1 not in user_ids:
						user_ids.append(game.player1)
					if game.player2 not in user_ids:
						user_ids.append(game.player2)

				users = User.query(User.email != None).fetch()
							
				app_id = app_identity.get_application_id()
				for user in users:

					if user.user_id in user_ids:
						subject = 'Tic Tac Toe Reminder'
						body = 'Hello {0}, you have an unfinished Tic Tac Toe Games!!!'.format(user.name)
						# This will send test emails, the arguments to send_mail are:
						# from, to, subject, body
						mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
													 user.email,
													 subject,
													 body)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
		def post(self):
				"""Update game listing announcement in memcache."""
				GuessANumberApi._cache_average_attempts()
				self.response.set_status(204)


app = webapp2.WSGIApplication([
		('/crons/send_reminder', SendReminderEmail),
		('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
