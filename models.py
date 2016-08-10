"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
		"""User profile"""
		name = ndb.StringProperty(required=True)
		email =ndb.StringProperty()
		user_id = ndb.StringProperty(required = True)
		games_won = ndb.IntegerProperty(default=0)

		def to_form(self):
			user = UserForm()
			user.name = self.name
			user.email = self.email
			user.user_id = self.user_id
			user.games_won = self.games_won
			return user


class Move(ndb.Model):
		"Position on TicTacToe Board"

		user_id = ndb.StringProperty()
		x = ndb.IntegerProperty(required=True)
		y = ndb.IntegerProperty(required=True)
		available = ndb.BooleanProperty()
		game_id = ndb.StringProperty()
		description = ndb.StringProperty()

class GameHistory(ndb.Model):
		game_id = ndb.StringProperty()
		user_id = ndb.StringProperty()
		move = ndb.StringProperty()
		game_state = ndb.StringProperty()

		def to_form(self):
			game_history_form = GameHistoryForm()
			game_history_form.game_id = self.game_id
			game_history_form.user_id = self.user_id
			game_history_form.move = self.move
			game_history_form.game_state = self.game_state
			
			return  game_history_form


class Game(ndb.Model):
		player1 = ndb.StringProperty()
		player2 = ndb.StringProperty()
		game_id = ndb.StringProperty(required=True)
		winner_id = ndb.StringProperty()
		last_play_user_id = ndb.StringProperty()
		finished = ndb.BooleanProperty(default=false)		
		state = ndb.StringProperty()

		def update_scores(self):
				if None in [self.player1, self.player2]:
						return None

				player1 = User.query(User.user_id == self.player1)
				player2 = User.query(User.user_id == self.player2)

				return player1.email


		def finish_game(self, winner_id, game_state):
				if self.finished == True:
						print("Game already finished")
						return self

				if winner_id != False:
						user = User.query(User.user_id == winner_id).get()
						if user != None:
								user.games_won = user.games_won + 1	          
								self.winner_id = winner_id	
								user.put()				

				self.state = game_state
				self.finished = True
				self.put()
				print("Game Stats Updated")

				return self




		def to_form(self):
				"""Returns a GameForm representation of the Game"""
				form = GameForm()
				form.player1 = self.player1
				form.player2 = self.player2
				form.game_id = self.game_id
				form.last_play_user_id = self.last_play_user_id
				form.finished = self.finished
				form.state = self.state
				return form		


class GameForm(messages.Message):
		"""GameForm for outbound game state information"""
		player1 = messages.StringField(1)
		player2 = messages.StringField(2)
		game_id = messages.StringField(3)
		last_play_user_id = messages.StringField(4)
		finished = messages.BooleanField(5)		
		state = messages.StringField(6)		
		games_won = messages.IntegerField(7)
		games_finished = messages.IntegerField(8)


class GameHistoryForm(messages.Message):
		"""GameForm for outbound game state information"""
		user_id = messages.StringField(1)
		game_id = messages.StringField(2)
		move = messages.StringField(3)
		game_state = messages.StringField(4)		

class GameHistoryForms(messages.Message):
		"""GameForm for outbound game state information"""
		moves = messages.MessageField(GameHistoryForm, 1, repeated = True)


class GameForms(messages.Message):
		"""ConferenceForms -- multiple Conference outbound form message"""
		games = messages.MessageField(GameForm, 1, repeated=True)


class UserForm(messages.Message):
		name = messages.StringField(1)
		email = messages.StringField(2)
		user_id = messages.StringField(3, required = True)
		games_won = messages.IntegerField(4, default = 0)

class UserForms(messages.Message):
		users = messages.MessageField(UserForm, 1, repeated = True)


class StringMessage(messages.Message):
		"""StringMessage-- outbound (single) string message"""
		message = messages.StringField(1, required=True)
		game_state = messages.StringField(2, default="")
		winner_id = messages.StringField(3, default="no_winners_yet")


