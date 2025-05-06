"""
Improved Database and Error Handling for Car Game
"""

import pyodbc
import logging
import queue
import threading
import time

# Set up logging
logging.basicConfig(
    filename='car_game.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DBConnectionPool:
    """Connection pool to reuse database connections"""
    
    def __init__(self, connection_string, pool_size=3):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.connections = queue.Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        
        # Initialize connection pool
        try:
            for _ in range(pool_size):
                conn = pyodbc.connect(self.connection_string)
                self.connections.put(conn)
            logging.info(f"Connection pool initialized with {pool_size} connections")
        except pyodbc.Error as e:
            logging.error(f"Failed to initialize connection pool: {str(e)}")
            raise
    
    def get_connection(self, timeout=5):
        """Get a connection from the pool with timeout"""
        try:
            conn = self.connections.get(timeout=timeout)
            return conn
        except queue.Empty:
            logging.warning("Connection pool timeout - creating new connection")
            try:
                return pyodbc.connect(self.connection_string)
            except pyodbc.Error as e:
                logging.error(f"Failed to create new connection: {str(e)}")
                raise
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        try:
            if not conn.closed:
                self.connections.put(conn, block=False)
            else:
                # Replace closed connection
                self.connections.put(pyodbc.connect(self.connection_string))
        except queue.Full:
            # Close connection if pool is full (should not happen with proper usage)
            conn.close()
            logging.warning("Connection pool full - closing connection")
        except Exception as e:
            logging.error(f"Error returning connection to pool: {str(e)}")
            
    def close_all(self):
        """Close all connections in the pool"""
        while not self.connections.empty():
            try:
                conn = self.connections.get(block=False)
                conn.close()
            except Exception as e:
                logging.error(f"Error closing connection: {str(e)}")


class DBTaskQueue:
    """Queue for database operations with error handling"""
    
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
        self.task_queue = queue.Queue()
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        logging.info("DB task queue initialized and worker started")
    
    def add_task(self, task_func, *args, **kwargs):
        """Add a database task to the queue"""
        self.task_queue.put((task_func, args, kwargs))
    
    def _process_queue(self):
        """Worker that processes database tasks"""
        while self.is_running:
            try:
                # Get a task from the queue with timeout to allow for shutdown
                try:
                    task_func, args, kwargs = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Get a connection and execute the task
                conn = None
                cursor = None
                try:
                    conn = self.connection_pool.get_connection()
                    cursor = conn.cursor()
                    task_func(cursor, *args, **kwargs)
                    conn.commit()
                    logging.debug(f"DB task {task_func.__name__} completed successfully")
                except pyodbc.OperationalError as e:
                    logging.error(f"Database operational error in {task_func.__name__}: {str(e)}")
                    if conn:
                        # Don't return failed connections to the pool
                        conn = None
                except pyodbc.ProgrammingError as e:
                    logging.error(f"SQL syntax error in {task_func.__name__}: {str(e)}")
                    if conn:
                        conn.rollback()
                except pyodbc.Error as e:
                    logging.error(f"Database error in {task_func.__name__}: {str(e)}")
                    if conn:
                        conn.rollback()
                except Exception as e:
                    logging.error(f"Unexpected error in DB task {task_func.__name__}: {str(e)}")
                    if conn:
                        conn.rollback()
                finally:
                    if cursor:
                        cursor.close()
                    if conn:
                        self.connection_pool.return_connection(conn)
                    self.task_queue.task_done()
            except Exception as e:
                logging.critical(f"Critical error in DB queue worker: {str(e)}")
                time.sleep(5)  # Prevent CPU spinning on critical errors
    
    def shutdown(self):
        """Shutdown the worker thread"""
        self.is_running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        logging.info("DB task queue shutdown")


class DB:
    """Improved database interface with error handling"""
    
    # Singleton pattern - share connection pool across instances
    _instance = None
    _connection_pool = None
    _task_queue = None
    _init_lock = threading.Lock()
    
    def __new__(cls):
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = super(DB, cls).__new__(cls)
                # Initialize connection pool if not already done
                if cls._connection_pool is None:
                    try:
                        connection_string = 'DRIVER={SQL Server};SERVER=ved;DATABASE=pygaming'
                        cls._connection_pool = DBConnectionPool(connection_string)
                        cls._task_queue = DBTaskQueue(cls._connection_pool)
                        logging.info("DB singleton initialized")
                    except Exception as e:
                        logging.critical(f"Failed to initialize DB: {str(e)}")
                        # Re-raise to prevent silent failures during initialization
                        raise
        return cls._instance
    
    def _save_score(self, cursor, user_id, score):
        """Internal method to save score"""
        cursor.execute("INSERT INTO score (user_id, game_id, score) VALUES (?, ?, ?)", 
                      (user_id, 5, score))
    
    def save_score(self, user_id, score):
        """Queue task to save score"""
        self._task_queue.add_task(self._save_score, user_id, score)
    
    def _start_session(self, cursor, user_id):
        """Internal method to start session"""
        cursor.execute("INSERT INTO game_session (user_id, game_id, outcome) VALUES (?, ?, ?)", 
                      (user_id, 5, 'ongoing'))
    
    def start_session(self, user_id):
        """Queue task to start session"""
        self._task_queue.add_task(self._start_session, user_id)
    
    def _end_session(self, cursor, user_id, outcome='win'):
        """Internal method to end session"""
        cursor.execute("UPDATE game_session SET end_at = SYSDATETIME(), outcome = ? "
                      "WHERE user_id = ? AND end_at IS NULL", 
                      (outcome, user_id))
    
    def end_session(self, user_id, outcome='win'):
        """Queue task to end session"""
        self._task_queue.add_task(self._end_session, user_id, outcome)
    
    def _update_leaderboard(self, cursor, score, user_id):
        """Internal method to update leaderboard"""
        try:
            cursor.execute("SELECT score FROM leaderboard WHERE user_id = ? AND game_id = ?", 
                          (user_id, 5))
            result = cursor.fetchone()
            if result is None:
                # No existing record, insert new one
                cursor.execute("INSERT INTO leaderboard (user_id, game_id, score) VALUES (?, ?, ?)", 
                              (user_id, 5, score))
            elif score > result[0]:
                # Score is higher, update record
                cursor.execute("UPDATE leaderboard SET score = ? WHERE user_id = ? AND game_id = ?", 
                              (score, user_id, 5))
        except Exception as e:
            # Log the specific error for leaderboard operation
            logging.error(f"Error updating leaderboard: {str(e)}")
            raise
    
    def leader(self, score, user_id):
        """Queue task to update leaderboard"""
        self._task_queue.add_task(self._update_leaderboard, score, user_id)
    
    @classmethod
    def shutdown(cls):
        """Cleanly shutdown DB resources"""
        if cls._task_queue:
            cls._task_queue.shutdown()
        if cls._connection_pool:
            cls._connection_pool.close_all()
        logging.info("DB resources shut down")


# Game exception handling
class GameError(Exception):
    """Base exception for game-related errors"""
    pass

class ResourceLoadError(GameError):
    """Exception for resource loading failures"""
    pass

class DatabaseError(GameError):
    """Exception for database-related failures"""
    pass


# Example usage in main game loop
def initialize_game(user_id):
    """Initialize game with error handling"""
    try:
        # Start DB session
        DB().start_session(user_id)
        return True
    except Exception as e:
        logging.error(f"Failed to initialize game: {str(e)}")
        # Allow game to continue even if DB fails
        return False

def game_over_handler(user_id, score):
    """Handle game over with error handling"""
    try:
        DB().save_score(user_id, score)
        DB().leader(score, user_id)
        return True
    except Exception as e:
        logging.error(f"Failed to process game over: {str(e)}")
        return False

def quit_game(user_id):
    """Clean shutdown of game resources"""
    try:
        DB().end_session(user_id)
        # Give time for DB operations to complete
        time.sleep(0.5)
        DB.shutdown()
    except Exception as e:
        logging.error(f"Error during game shutdown: {str(e)}")

# Resource loading with error handling
def load_image(path):
    """Load an image with error handling"""
    try:
        import pygame
        image = pygame.image.load(path)
        return image
    except pygame.error as e:
        logging.error(f"Failed to load image {path}: {str(e)}")
        raise ResourceLoadError(f"Could not load image: {path}")

# Example of how to modify main game code to use this
"""
# In main game:
try:
    # Initialize game
    user_id = int(sys.argv[1])
    initialize_game(user_id)
    
    # Game loop
    running = True
    while running:
        # Game logic here
        # ...
        
        # On game over
        if gameover:
            game_over_handler(user_id, score)
            
    # On quit
    quit_game(user_id)
    
except ResourceLoadError as e:
    print(f"Error loading game resources: {str(e)}")
    pygame.quit()
    sys.exit(1)
except Exception as e:
    logging.critical(f"Unhandled exception: {str(e)}")
    pygame.quit()
    sys.exit(1)
finally:
    pygame.quit()
"""
