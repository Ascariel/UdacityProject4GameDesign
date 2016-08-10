#Full Stack Nanodegree Project 4 Refresh

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
 
 
 
##Game Description:
Tic Tac Toe is a game where players alternate placing 'X' and 'O' tokens/marks on a 3x3 grid. The game ends when a user is able to match 3 straight or crossed marks of their type, or when the grid is already full and there is now more available moves.

Short step by step explanation:

1. The game is played on a grid that's 3 squares by 3 squares.

2. You are X, your friend (or the computer in this case) is O. Players take turns putting their marks in empty squares.

3. The first player to get 3 of her marks in a row (up, down, across, or diagonally) is the winner.

4. When all 9 squares are full, the game is over. If no player has 3 marks in a row, the game ends in a tie.

5. Scores are kept as the number of games each user has won. Users with higher wins get ranked top.

## Score Keeping

- ** Score keeping is very simple for this game, everytime a user wins, his games_won score increases by one. Unfinished, lost or tied games do not affect this score and are not registered.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.
 - README.md includes explanations on how to setup/run the app, and how it works

##Endpoints Included:
 - **createUser**
    - Path: 'create_user'
    - Method: POST
    - Parameters:  (email, name, user_id)
    - Returns: Message confirming creation of the User
    - Description: Creates a new User. user_id provided must be unique. Will 
    return an appropiate message if a User with that user_id already exists.
         
    
 - **startGame**
    - Path: 'start_game'
    - Method: POST
    - Parameters: player1, player2, game_id 
    - Returns: StringMessage with initial game state.
    - Description: Creates a new Game. Initializes all 9 Tic Tac Toe posible moves using provided game_id, and 2 player different user ids 

- **cancel_game**
    - Path: 'cancel_game'
    - Method: DELETE
    - Parameters: game_id 
    - Returns: StringMessage with game deletion success response
    - Description: Attempts to find and completely erase a game for a given game_id. Responds with appropiate success/failure messages

- **getUserGames**
    - Path: 'get_user_games'
    - Method: GET
    - Parameters: user_id
    - Returns: Returns array of GameForm's containing all the games played by a user.
    - Description: Finds and returns all active game for a given user. 

- **getUserGameHistory**
    - Path: 'get_user_game_history'
    - Method: GET
    - Parameters: user_id
    - Returns: Returns array of GameHistoryForms's containing all the moves played by a user.
    - Description: Returns all moves made and corresponding game state per move for a given user

- **getUserRankings**
    - Path: 'get_user_game_rankings'
    - Method: GET
    - Parameters: none
    - Returns: Returns array of UserForm's containing all users sorted by their games won count
    - Description: Finds all users and display their information sorted by their winning score

- **makeMove**
    - Path: 'make_move'
    - Method: PUT
    - Parameters: user_id, game_id, x_move, y_move
    - Returns: StringMessage with appropiate success response for submitted move
    - Description: Asigns specific move to a user for a specific game_id, as long as its available
      It also checks if the move is valid, returning the appropiate message for each situation. It 
      also keeps track of every valid move made by a user


 - **checkGameState**
    - Path: 'check_game_state'
    - Method: GET
    - Parameters: game_id
    - Returns: StringMessage with current game state.
    - Description:  Returns de state of the game, either won, out of moves or running 
                   
                   

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Move**
    - Records completed games. Associated with Users model via KeyProperty.
  
 - **GameHistory**
    - Records completed games. Associated with Users model via KeyProperty.
    
 - **Move**
    - Records completed games. Associated with Users model via KeyProperty.


##Forms Included:
 - **GameForm**
    - Representation of a Game's state (players, game_id, state etc
 - **GameHistoryForm**
    - Used to create a move log (user_id, game_id, move coordinates etc)
 - **GameHistoryForms**
    - Array of Gameforms
 - **StringMessage**
    - Simple flexible message for different scenarios,
    guesses).
 - **UserForm**
    - Used to show user information (name, email, user_id, games_won etc)
 - **UserForms**
    - To display array of UserForm's 


