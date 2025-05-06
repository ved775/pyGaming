import pyodbc


class Db:
    def save_score_to_db(score,user_id):
        try:
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=ved;DATABASE=pygaming')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO score (user_id,game_id,score) VALUES (?,?,?)", (user_id,4,score))
            conn.commit()
            conn.close()
            print("Score saved to database.")
        except Exception as e:
            print("Failed to save score:", e)
            
    def start_session(user_id):
        try:
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=ved;DATABASE=pygaming')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO game_session (user_id,game_id,outcome) VALUES (?,?,?)", (user_id,4,'win'))
            conn.commit()
            conn.close()
            print("Score saved to database.")
        except Exception as e:
            print("Failed to save score:", e)    
            
    def end_game_session(user_id):
        try:
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=ved;DATABASE=pygaming')
            cursor = conn.cursor()
            cursor.execute("UPDATE game_session SET end_at = SYSDATETIME(),outcome = ? WHERE user_id = ? AND end_at IS NULL", ('win',user_id))
            conn.commit()   
            conn.close()
        except Exception as e:
            print("Failed to end game session:", e)     
            
    def leader(score,user_id):
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=ved;DATABASE=pygaming')
        cursor = conn.cursor()
        cursor.execute("SELECT score FROM leaderboard WHERE user_id = ? AND game_id = ?", (user_id, 4))
        result = cursor.fetchone()
        if result is None:
          # No existing record, insert new one
          cursor.execute("INSERT INTO leaderboard (user_id, game_id, score) VALUES (?, ?, ?)", (user_id, 4, score))
        elif score > result[0]:
          # Score is higher, update record
           cursor.execute("UPDATE leaderboard SET score = ? WHERE user_id = ? AND game_id = ?", (score, user_id, 4))
        conn.commit() 
        conn.close()             
            