import sqlite3
import json

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
        Creates the 2 tables for the database if they don't already exist:
        - stock_strategy: stores the stock ticker alongside the strategy name, and strategy parameters
        - strategy_data: stores the strategy data for each stock_strategy record
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_strategy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                strategy TEXT NOT NULL,
                params TEXT NOT NULL,
                time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, strategy, params)
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_strategy_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(stock_strategy_id) REFERENCES stock_strategy(id)
            );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            print("Error creating tables: ", e)

    def insertStrategy(self, ticker, strategy, strategy_params, strategy_data):
        """
        Inserts a stock strategy into the database. If the strategy already exists, it will not be inserted.
        The method adds the stock and strategy to the stock_strategy table, and the strategy data to the strategy_data table.
        """
        try:
            cursor = self.conn.cursor()

            # Insert into stock_strategy table
            serialized_params = json.dumps(strategy_params, sort_keys=True)
            cursor.execute("""
            INSERT INTO stock_strategy (ticker, strategy, params)
            VALUES (?, ?, ?)
            ON CONFLICT DO NOTHING;
            """, (ticker, strategy, serialized_params))

            # Get the stock_strategy_id
            cursor.execute("""
            SELECT id FROM stock_strategy
            WHERE ticker = ? AND strategy = ? AND params = ?;
            """, (ticker, strategy, serialized_params))
            stock_strategy_id = cursor.fetchone()[0]

            if not stock_strategy_id:
                raise Exception("Failed to insert stock strategy")

            # Insert into strategy_data table
            serialized_data = json.dumps(strategy_data, separators=(',', ':'))
            cursor.execute("""
            INSERT INTO strategy_data (stock_strategy_id, data)
            VALUES (?, ?);
            """, (stock_strategy_id, serialized_data))

            self.conn.commit()
            print("Strategy inserted successfully")
        except sqlite3.Error as e:
            self.conn.rollback()
            print("Error inserting strategy: ", e)

    def getStockStrategyId(self, ticker, strategy, strategy_params):
        """
        given a unique ticker, strategy, and strategy_params combination, returns the stock_strategy_id
        """
        try:
            cursor = self.conn.cursor()
            serialized_params = json.dumps(strategy_params, sort_keys=True)
            cursor.execute("""
            SELECT id FROM stock_strategy
            WHERE ticker = ? AND strategy = ? AND params = ?;
            """, (ticker, strategy, serialized_params))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print("Error retrieving stock strategy ID: ", e)
            return None
    
    def getStockStrategyData(self, stock_strategy_id):
        """
        given a unique stock_strategy_id, returns the strategy data that matches the stock_strategy_id
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT data FROM strategy_data
            WHERE stock_strategy_id = ?;
            """, (stock_strategy_id,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
        except sqlite3.Error as e:
            print("Error retrieving stock strategy data: ", e)
            return None



    def removeStockStrategy(self, ticker, strategy, strategy_params):
        """
        Given a unique ticker, strategy, and strategy_params combination, removes the stock strategy from the database.
        """
        try:
            stock_strategy_id = self.getStockStrategyId(ticker, strategy, strategy_params)
            if not stock_strategy_id:
                print(f"No strategy found for {ticker} with {strategy}.")
                return

            cursor = self.conn.cursor()

            # Delete from strategy_data table
            cursor.execute("""
            DELETE FROM strategy_data WHERE stock_strategy_id = ?;
            """, (stock_strategy_id,))

            # Delete from stock_strategy table
            cursor.execute("""
            DELETE FROM stock_strategy WHERE id = ?;
            """, (stock_strategy_id,))

            self.conn.commit()
            print(f"Strategy {strategy} for {ticker} successfully removed.")
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error: {e} during removal of strategy {strategy} for {ticker}")
