import sqlite3
import json
import datetime

class DBHandler:
    def __init__(self):
        self.conn = None
        self.createConnection()
        self.createTables()

    def createConnection(self):
        try:
            self.conn = sqlite3.connect('trading_tool.db')
        except sqlite3.Error as e:
            print("Error establishing connection: ", e)


    def closeConnection(self):
        if self.conn:
            self.conn.close()
    
    def createTables(self):
        """
        Creates:
        - stock_strategy: stores the stock ticker alongside the strategy name, and strategy parameters
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_strategy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                strategy TEXT NOT NULL,
                params TEXT NOT NULL,
                UNIQUE(ticker, strategy, params)
            );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            print("Error creating tables: ", e)

    def insertStrategy(self, strategy, strategy_params):
        """
        Inserts a stock strategy into the database. If the strategy already exists, it will not be inserted.
        """
        ticker = strategy.getTicker()

        strategy_name = strategy.getName()
        try:
            cursor = self.conn.cursor()

            # Insert into stock_strategy table
            serialized_params = json.dumps(strategy_params, sort_keys=True)
            cursor.execute("""
            INSERT INTO stock_strategy (ticker, strategy, params)
            VALUES (?, ?, ?)
            ON CONFLICT(ticker, strategy, params) DO NOTHING;
            """, (ticker, strategy.getName(), serialized_params))

            # Get the stock_strategy_id
            stock_strategy_id = cursor.lastrowid

            if stock_strategy_id == 0:
                return f"Failed to insert strategy {strategy_name} for {ticker}. This strategy might already exist with the given parameters."
            
            self.conn.commit()
            return None
        
        except sqlite3.Error as e:
            self.conn.rollback()
            return f"Error inserting strategy for {ticker}: {e}"
            

    def getStockStrategyId(self, strategy, strategy_params):
        """
        given a unique ticker, strategy, and strategy_params combination, returns the stock_strategy_id
        """
        try:
            ticker = strategy.getTicker()
            strategy_name = strategy.getName()
            cursor = self.conn.cursor()
            serialized_params = json.dumps(strategy_params, sort_keys=True)
            cursor.execute("""
            SELECT id FROM stock_strategy
            WHERE ticker = ? AND strategy = ? AND params = ?;
            """, (ticker, strategy_name, serialized_params))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print("Error retrieving stock strategy ID: ", e)
            return None

    def getStockStrategy(self, stock_strategy_id):
        """
        Given a stock_strategy_id, returns the stock strategy
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT ticker, strategy, params, time_stamp FROM stock_strategy
            WHERE id = ?;
            """, (stock_strategy_id,))
            result = cursor.fetchone()

            ticker = result[0]
            strategy = result[1]
            params = json.loads(result[2])

            return (ticker, strategy, params)
        except sqlite3.Error as e:
            print("Error retrieving stock strategy: ", e)
            return None


    def getAllStockStrategies(self):
        """
        Returns all stock strategies in the database
        """
        query = """
        SELECT id, ticker, strategy, params FROM stock_strategy;
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()

            stock_strategies = {}
            for row in result:
                id = row[0]
                ticker = row[1]
                strategy = row[2]
                params = json.loads(row[3])

                if ticker not in stock_strategies:
                    stock_strategies[ticker] = []
                
                stock_strategies[ticker].append((id,strategy, params))

            return stock_strategies
        except sqlite3.Error as e:
            print("Error retrieving all stock strategies: ", e)
            return None



    def removeStockStrategy(self, stock_strategy_id):
        """
        Given a unique ticker, strategy, and strategy_params combination, removes the stock strategy from the database.
        """
        try:

            cursor = self.conn.cursor()

            # Delete from stock_strategy table
            cursor.execute("""
            DELETE FROM stock_strategy WHERE id = ?;
            """, (stock_strategy_id,))

            self.conn.commit()
            print(f"Strategy successfully removed.")
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error: {e} during removal of strategy")
