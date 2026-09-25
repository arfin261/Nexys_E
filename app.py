from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # মিনি অ্যাপ থেকে ডাটা আদান-প্রদানের জন্য

DB_NAME = "users.db"

def init_db():
    """ডাটাবেজ টেবিল তৈরি করার ফাংশন"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/get_balance', methods=['GET'])
def get_balance():
    """ইউজারের বর্তমান ব্যালেন্স ডাটাবেজ থেকে এনে দেখাবে"""
    user_id = request.args.get('user_id')
    username = request.args.get('username', 'User')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row:
        balance = row[0]
    else:
        # নতুন ইউজার হলে ডাটাবেজে যুক্ত করা হবে
        cursor.execute("INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)", (user_id, username, 0.0))
        conn.commit()
        balance = 0.0

    conn.close()
    return jsonify({"balance": balance})

@app.route('/add_reward', methods=['POST'])
def add_reward():
    """বিজ্ঞাপন দেখার পর ব্যালেন্স যোগ করার ফাংশন"""
    data = request.json
    user_id = data.get('user_id')
    amount = 0.050  # প্রতি বিজ্ঞাপনে ০৫০ পয়সা জমা হবে

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    new_balance = cursor.fetchone()[0]
    conn.close()

    return jsonify({"success": True, "new_balance": new_balance})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
