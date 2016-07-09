# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import sys
import logging
import endpoints
import time
from protorpc import remote, messages
from protorpc import message_types

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import User, Game, Move, GameForm, GameForms, UserForm, UserForms, GameHistory,GameHistoryForms
from models import StringMessage, GameForm
from utils import get_by_urlsafe


START_GAME = endpoints.ResourceContainer(game_id = messages.StringField(1), 
                                         player1=messages.StringField(2), player2=messages.StringField(3))

TEST = endpoints.ResourceContainer(game_id = messages.StringField(1), 
                                         player1=messages.StringField(2), player2=messages.StringField(3),
                                         int = messages.IntegerField(4), boolean = messages.BooleanField(5))

GAME_ID = endpoints.ResourceContainer(game_id = messages.StringField(1))
USER_ID = endpoints.ResourceContainer(user_id = messages.StringField(1))
USER_GAME_ID = endpoints.ResourceContainer(user_id = messages.StringField(1), game_id = messages.StringField(2))

NEW_USER = endpoints.ResourceContainer(user_id = messages.StringField(1),
                                       email = messages.StringField(2), name = messages.StringField(3)
                                       )


MAKE_NEXT_MOVE_REQUEST = endpoints.ResourceContainer(
     x = messages.IntegerField(1), y = messages.IntegerField(2),
      user_id=messages.StringField(3), game_id=messages.StringField(4))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='guess_a_number', version='v1')
class GuessANumberApi(remote.Service):
    """Game API"""


    @endpoints.method(request_message=START_GAME,
                      response_message=StringMessage,
                      path='start_game',
                      name='start_game',
                      http_method='POST')

    def startGame(self, request):
      """ Initializes all 9 Tic Tac Toe posible moves using provided game_id, and 2 player ids """

      game_id = request.game_id
      player1 = request.player1
      player2 = request.player2

      if request.game_id == None:
        return StringMessage(message = "Failed, Empty game_id. Please enter a valid unique game_id")

      if request.player1 == None or request.player2 == None:
        return StringMessage(message = "Failed, Missing Players. Make sure both player ids are present")        

      if request.player1 == request.player2:
        return StringMessage(message = "Failed, Player Ids must be different")                

      

      game_exists = len(Move.query(Move.game_id == game_id).fetch()) > 0
      if game_exists:
        return StringMessage(message = "Game Creation Failed, Game ID already exists: {0}".format( game_id ) )

      # Creating Game
      game = Game(game_id = game_id, player1 = player1, player2 = player2)
      game.put()

      print("New Game Created: {0}".format(game))        

      mv1 = Move(x = 0, y = 0, game_id = game_id, available = True, description = "[0,0]")
      mv2 = Move(x = 0, y = 1, game_id = game_id, available = True, description = "[0,1]")
      mv3 = Move(x = 0, y = 2, game_id = game_id, available = True, description = "[0,2]")

      mv4 = Move(x = 1, y = 0, game_id = game_id, available = True, description = "[1,0]")
      mv5 = Move(x = 1, y = 1, game_id = game_id, available = True, description = "[1,1]")
      mv6 = Move(x = 1, y = 2, game_id = game_id, available = True, description = "[1,2]")

      mv7 = Move(x = 2, y = 0, game_id = game_id, available = True, description = "[2,0]")
      mv8 = Move(x = 2, y = 1, game_id = game_id, available = True, description = "[2,1]")
      mv9 = Move(x = 2, y = 2, game_id = game_id, available = True, description = "[2,2]")

      # ndb.put_multi([ mv1, mv2, mv3, mv4, mv5, mv6, mv7, mv8, mv9])

      for m in [ mv1, mv2, mv3, mv4, mv5, mv6, mv7, mv8, mv9]:
        print(" saving: {0}".format(m) )
        m.put()

      return StringMessage(message = "New Game Created, ID: {0} | Player 1: {1} | Player 2: {2}".format( game_id, player1, player2 ) )


    @endpoints.method(request_message = GAME_ID, response_message = StringMessage,
                      path = "cancel_game", name = "cancel_game", http_method = "POST")
    def cancel_game(self, request):
      """ Delete an unfinished game """
      game_id = request.game_id
      game = Game.query(Game.game_id == game_id).get()
      if game == None:
        return StringMessage(message = "No Game found for ID:  {0} ".format(game_id))

      if game.finished == True:
        return StringMessage(message = "Can't delete a game thats already finished")              

      # for the moment, resets every move for provided game_id
      moves = Move.query().fetch()
      moves_deleted = Move.query(Move.game_id == game_id).fetch()

      print("game id is {0} {1}".format(game_id, moves[0].game_id ))

      # Deleting Game
      game.key.delete()

      # Deleting Moves
      for move in moves_deleted:
        move.key.delete()

      return StringMessage(message = "Game Reset Complete, deleted {0} moves for Game:  {1} ".format(len(moves_deleted), game_id))

    @endpoints.method(request_message = USER_ID, response_message = GameForms,
                      path = "get_user_games", name = "get_user_games", http_method = "GET")
    def getUserGames(self, request):

      """ Returns all active games for a given user """
      games = Game.query(ndb.AND(ndb.OR(Game.player1 == request.user_id, Game.player2 == request.user_id ), Game.finished == False)).fetch()
      print("game is")
      print(games[0])

      print("game to form is")
      print(games[0].to_form())      
      game_forms = GameForms(games = [ game.to_form() for game in games ])

      for i in game_forms.games:
        print(i)
        print(i.game_id)

      return game_forms


    @endpoints.method(request_message = USER_GAME_ID, response_message = GameHistoryForms,
                      path = "get_user_game_history", name = "get_user_game_history", http_method = "GET")
    def getUserGameHistory(self, request):
      """ returns all moves made and corresponding game state per move for a given user """
      game_history = GameHistory.query(GameHistory.game_id == request.game_id, GameHistory.user_id == request.user_id).fetch()   
      game_history_forms = GameHistoryForms(moves = [ move.to_form() for move in game_history ])

      return game_history_forms 

    @endpoints.method(request_message = message_types.VoidMessage, response_message = UserForms,
                      path = "get_user_rankings", name = "get_user_rankings", http_method = "GET")
    def getUserRankings(self, request):
      """ returns users ranked by their games won score """

      users = User.query().order(-User.games_won).fetch()   
      user_forms = UserForms(users = [ user.to_form() for user in users ])

      for i in user_forms.users:
        print(i)
        print(i.user_id)
        print(i.games_won)


      return user_forms      

    @endpoints.method(request_message = NEW_USER, response_message = StringMessage,
                      path = "create_user", name = "create_user", http_method = "POST")
    def createUser(self, request):
      """ creates a user so it can be used in different games and recieve email notifications """
      user = User.query(User.user_id == request.user_id).get()
      if user != None:
        return StringMessage(message="User Already exists for ID: " + request.user_id)

      user = User(name = request.name, email = request.email, user_id = request.user_id)
      user.put()
      return StringMessage(message = "User Created with ID: " + request.user_id)

    @endpoints.method(request_message= MAKE_NEXT_MOVE_REQUEST, response_message = StringMessage,
                      name = "make_move", path="make_move", http_method="POST" )
    def makeMove(self, request):
      """ Asigns specific move to a user for a specific game_id, as long as its available
      It also checks if the move is valid, returning the appropiate message for each situation. It 
      also keeps track of every valid move made by a user """
      x = request.x   
      y = request.y
      game_id = request.game_id
      user_id = request.user_id

      game = Game.query(Game.game_id == game_id).get()
      queried_move = Move.query(Move.x == x, Move.y == y, 
                        Move.game_id == game_id).fetch(1)
      all_moves = Move.query(Game.game_id==game_id)

      if game == None :
        print("\n\nInvalid Move, Wrong Game ID\n\n")
        return StringMessage(message = "Invalid Move, Wrong Game ID" )
 
      winner_id = GuessANumberApi._check_winning_condition(game_id) 

      if winner_id != False and winner_id != "no_winners_yet":
        print("\n\n Game Won By {0} \n\n".format(winner_id))
        game.finish_game(winner_id, "game_won")
                    
        return StringMessage(message = "\n\n Game Won By {0} \n\n".format(winner_id), game_state="game_won", winner_id=winner_id)             

      available_moves = Move.query(Move.available == True, Move.game_id == game_id).fetch()
      
      if len(available_moves) == 0:
        print("\n\n Game Ended, No more moves left {0} \n\n".format(game_id))   
        game.finish_game(winner_id, "no_more_moves")

        return StringMessage(message = "\n\n Game Ended, No more moves left {0} \n\n".format(game_id), game_state="no_more_moves", winner_id=winner_id or "")               

      if user_id == None or user_id not in [game.player1, game.player2]:
        print("\n\nInvalid move parameters\n\n")
        return StringMessage(message = "Invalid Move, Wrong User ID" )

      if len(queried_move) == 0:
        print("\n\nInvalid move parameters\n\n")
        return StringMessage(message = "Invalid move parameters, Wrong Game ID or Move out of range" )

      if user_id == game.last_play_user_id:
        print("\n\n This Player already moved\n\n")
        return StringMessage(message = "Invalid move, This Player already moved" )        

      move = queried_move[0]
      if move.available != True:
        print("\n\nMove already done by: {0} \n\n".format(move.user_id))
        return StringMessage(message = "Move {0} has already been made by User with ID: : {1}"
                             .format(move.description, move.user_id) )        

      move.user_id = user_id
      move.available = False
      move.put()

      game.last_play_user_id = user_id
      game.put()

      GuessANumberApi._show_game_picture(game_id)
      state = GuessANumberApi._check_game_state(game_id)

      if state == False:
        state = "no_winners_yet"

      string_move = "[{0},{1}]".format(move.x, move.y)
      saved_move = GameHistory(game_id = game.game_id, user_id = user_id, move = string_move, game_state = state)
      saved_move.put()

      print(saved_move)

      # Final Winning Check
      winner_id = GuessANumberApi._check_winning_condition(game_id) 

      if winner_id != False and winner_id != "no_winners_yet":
        print("\n\n Game Won By {0} \n\n".format(winner_id))
        game.finish_game(winner_id, "game_won")

        return StringMessage(message = "\n\n Game Won By {0} \n\n".format(winner_id), game_state="game_won", 
                             winner_id=winner_id)             

      return StringMessage(message = "New Move {0} assigned to {1} Game ID: {2}, x:{3} and y:{4}"
                           .format(move.description, user_id, game_id, x, y), game_state="game_active", 
                           winner_id=""  )

    @endpoints.method(request_message = GAME_ID, response_message = StringMessage,
                      path = "check_game_state", name = "check_game_state", http_method = "GET")
    def checkGameState(self, request):
      """ Returns de state of the game, either won, out of moves or running """
      game_id = request.game_id
      game = Game.query(Game.game_id == game_id).get()
      winner_id = ""
      GuessANumberApi._show_game_picture(game_id)

      if game == None:
        print("\n\n Game doesnt exist for ID: {0} \n\n".format(game_id))
        return StringMessage(message = "Game doesnt exist for ID: {0} "
                             .format(game_id) )  

      state = GuessANumberApi._check_game_state(game_id)   
      
      if state == "no_more_moves":
        print("\n\n Game Ended, No Winners: {0} \n\n".format(game_id))
        game.finish_game(winner_id, "no_more_moves")

        return StringMessage(message = "Game Ended, No Winners: {0} "
                             .format(game_id), game_state="no_more_moves", 
                           winner_id="" )  

      if state == "no_winners_yet":
        print("\n\n No Winners Yet, Game Continues: {0} \n\n".format(game_id))
        game.finished = False
        game.state = "no_winners_yet"
        game.put()
        return StringMessage(message = "No Winners Yet, Game Continues: {0} "
                             .format(game_id) , game_state="game_active", 
                           winner_id="")  
        


      print("\n\n Game Won By: {0} \n\n".format(state))
      game.finish_game(winner_id, "game_won")

      return StringMessage(message = "Game Won By: {0} "
                           .format(state), game_state="game_won", 
                           winner_id=state )  
        

    @staticmethod
    def _show_game_picture(game_id):

      """ Prints visual representation of game board, for interal testing only """

      moves = Move.query(Move.game_id == game_id).order(Move.x, Move.y).fetch()

      if len(moves) == 0:
        print("\n\nCant print game state, Invalid game_id {0}\n\n".format(game_id))
        return StringMessage(message = "Invalid move parameters. no game found" )

      player1,player2 = GuessANumberApi._get_players_in_game(game_id)

      print("Current Players for Game ID {0}: {1}, {2}".format(game_id, player1, player2) )


      m_00 = Move.query(Move.x == 0, Move.y == 0, 
                        Move.game_id == game_id).fetch(1)[0]
      m_01 = Move.query(Move.x == 0, Move.y == 1, 
                        Move.game_id == game_id).fetch(1)[0] 
      m_02 = Move.query(Move.x == 0, Move.y == 2, 
                        Move.game_id == game_id).fetch(1)[0] 
      m_10 = Move.query(Move.x == 1, Move.y == 0, 
                        Move.game_id == game_id).fetch(1)[0] 
      m_11 = Move.query(Move.x == 1, Move.y == 1, 
                        Move.game_id == game_id).fetch(1)[0] 
      m_12 = Move.query(Move.x == 1, Move.y == 2, 
                        Move.game_id == game_id).fetch(1)[0] 
      m_20 = Move.query(Move.x == 2, Move.y == 0, 
                        Move.game_id == game_id).fetch(1)[0] 
      m_21 = Move.query(Move.x == 2, Move.y == 1, 
                        Move.game_id == game_id).fetch(1)[0] 
      m_22 = Move.query(Move.x == 2, Move.y == 2, 
                        Move.game_id == game_id).fetch(1)[0] 

      m_00 = m_00.user_id or m_00.description
      m_01 = m_01.user_id or m_01.description
      m_02 = m_02.user_id or m_02.description
      m_10 = m_10.user_id or m_10.description
      m_11 = m_11.user_id or m_11.description
      m_12 = m_12.user_id or m_12.description
      m_20 = m_20.user_id or m_20.description
      m_21 = m_21.user_id or m_21.description
      m_22 = m_22.user_id or m_22.description

      print("\n\n\n")
      print("TIC TAC TOE GAME")
      print("\n")
      print(" {0} | {1} | {2} ".format(m_00, m_01, m_02))
      print("-----------------------------")
      print(" {0} | {1} | {2} ".format(m_10, m_11, m_12))
      print("-----------------------------")
      print(" {0} | {1} | {2} ".format(m_20, m_21, m_22))
      print("\n\n\n")

    @staticmethod
    def _check_game_state(game_id):
      """ Checks whether there's a victory condition, losing condition, or no more available moves """

      print("\n\nInside check game state, game_id: " + game_id)

      moves = Move.query(Move.game_id == game_id).fetch()
      game = Game.query(Game.game_id == game_id).get()
      available_moves = Move.query(Move.available == True, Move.game_id == game_id).fetch()
      
      if len(moves) == 0:
        print("\n\n game_id not found {0} \n\n".format(game_id))
        return "game_id_not_found"

      winner_id = GuessANumberApi._check_winning_condition(game_id)
      print("winner_id is " + str(winner_id))

      if winner_id != False:
        print("\n\n############### Game won by:" + winner_id + " ###############\n\n") 
        game.finish_game(winner_id, "game_won")

        return winner_id        

      if len(available_moves) == 0:
        print("\n\n Game Ended, No more moves left {0} \n\n".format(game_id))
        game.finish_game(winner_id, "no_more_moves")
        return "no_more_moves"

           
      print("\n\nNo winners yet for game: {0} \n\n".format(game_id))
      game.finished = False
      game.state = "no_winners_yet"
      game.put()      
      return "no_winners_yet"

      

      

    @staticmethod
    def _check_winning_condition(game_id):
      """ Checks whether there's a victory condition and returns winner user_id if there is, else false"""

      moves = Move.query(Move.game_id == game_id).fetch()
      game = Game.query(Game.game_id == game_id).get()
      user_ids = GuessANumberApi._get_players_in_game(game_id)

      if len(moves) == 0 or game == None:
        print("\n\n game_id not found {0} \n\n".format(game_id))
        return False

      user_1 = game.player1
      user_2 = game.player2

      if user_1 == None or user_2 == None:
        print("\n\n not all users have played a move, Player1: {0}, Player2: {1} \n\n".format(user_1,user_2))
        return False

      print("\n\nChecking winning condition for game id: " + game_id)

      for i in range(0,3):

        # Checking for Horizontal Wins
        horizontal_moves = Move.query(Move.game_id == game_id, Move.x == i) 
        horizontal_moves = [h.user_id for h in horizontal_moves]

        unique_owner = list( set(horizontal_moves) ) 

        if None not in unique_owner and len(unique_owner) == 1:
          winner_id = unique_owner[0] 
          print("\n\nHorizontal Winning condition met, User: {0} Won! Row: {1} \n\n".format(winner_id, i))
          return winner_id     

        # Checking for Vertical Wins
        vertical_moves = Move.query(Move.game_id == game_id, Move.y == i) 
        vertical_moves = [h.user_id for h in vertical_moves]  

        unique_owner = list( set(vertical_moves) )                

        if None not in unique_owner and len(unique_owner) == 1:
          winner_id = unique_owner[0] 
          print("\n\n Vertical Winning condition met, User: {0} Won!, Column: {1} \n\n".format(winner_id, i))
          return winner_id            

      # Checking Cross Wins
      diagonal_moves = []
      for i in range(0,3):
        m = Move.query(Move.game_id == game_id, Move.x == i, Move.y == i).fetch()[0]
        diagonal_moves.append(m.user_id)

      unique_owner = list(set(diagonal_moves))

      if None not in unique_owner and len(unique_owner) == 1:
        winner_id = unique_owner[0] 
        print("\n\n Diagonal Winning condition met, User: {0} Won!, Column: {1} \n\n".format(winner_id, i))
        return winner_id   

      # Checking Cross Wins

      diagonal_moves = []
      checking_moves = []

      for i in range(0,3):
        m = Move.query(Move.game_id == game_id, Move.x == i, Move.y == 2-i).fetch()[0]

      for i in range(0,3):
        m = Move.query(Move.game_id == game_id, Move.x == i, Move.y == 2-i).fetch()[0]
        diagonal_moves.append(m.user_id)
        checking_moves.append(m)       

      unique_owner = list(set(diagonal_moves))
      print("uniq owner {0}".format( unique_owner))
      print("owner length " + str(len(unique_owner)))

      if len(unique_owner) == 1 :
        print("uniq owner is" + str(unique_owner))
        print("owner length " + str(len(unique_owner)))

      if len(unique_owner) == 1 and unique_owner[0] != None:
        winner_id = unique_owner[0] 
        print("\n\n Diagonal Winning condition met, User: {0} Won!, Column: {1} \n\n".format(winner_id, i))
        return winner_id  

      print("\n\n No winning conditions met \n\n")
      return False                


    @staticmethod
    def _get_players_in_game(game_id):
      """ returns player ids from a game """
      moves = Move.query(Move.game_id == game_id).fetch()

      if len(moves) == 0:
        return StringMessage(message = "Invalid move parameters. no game found" )


      print("Getting players in game...")
      user_ids = []

      game = Game.query(Game.game_id == game_id).get()
      user_ids.append(game.player1)
      user_ids.append(game.player2)
      return user_ids

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                        for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([GuessANumberApi])
