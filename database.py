# database.py
import sqlite3
from datetime import datetime
import json

class DogHealthDB:
    def __init__(self, db_path="dog_health.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Videos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_filename TEXT,
                saved_video_path TEXT,
                upload_date TIMESTAMP,
                tail_summary TEXT,
                ear_summary TEXT,
                head_summary TEXT,
                posture_summary TEXT,
                health_status TEXT,
                activity_status TEXT,
                recommendation TEXT,
                graphs_path TEXT,
                duration_seconds REAL
            )
        ''')
        
        # Frames table for detailed data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS frame_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                frame_number INTEGER,
                tail_state TEXT,
                ear_state TEXT,
                head_state TEXT,
                posture_state TEXT,
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        ''')
        
        self.conn.commit()
    
    def save_video_analysis(self, video_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO videos 
            (video_filename, saved_video_path, upload_date, tail_summary, ear_summary, 
             head_summary, posture_summary, health_status, activity_status, 
             recommendation, graphs_path, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_data['video_filename'],
            video_data['saved_video_path'],
            video_data['upload_date'],
            video_data['tail_summary'],
            video_data['ear_summary'],
            video_data['head_summary'],
            video_data['posture_summary'],
            video_data['health_status'],
            video_data['activity_status'],
            video_data['recommendation'],
            video_data['graphs_path'],
            video_data['duration_seconds']
        ))
        video_id = cursor.lastrowid
        
        # Save frame data
        if 'frame_data' in video_data:
            for frame in video_data['frame_data']:
                cursor.execute('''
                    INSERT INTO frame_analysis 
                    (video_id, frame_number, tail_state, ear_state, head_state, posture_state)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    video_id,
                    frame['frame_number'],
                    frame['tail_state'],
                    frame['ear_state'],
                    frame['head_state'],
                    frame['posture_state']
                ))
        
        self.conn.commit()
        return video_id
    
    def get_all_videos(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, video_filename, upload_date, health_status, 
                   activity_status, saved_video_path, graphs_path
            FROM videos 
            ORDER BY upload_date DESC
        ''')
        return cursor.fetchall()
    
    def get_video_details(self, video_id):
        cursor = self.conn.cursor()
        
        # Get video info
        cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
        video_info = cursor.fetchone()
        
        if not video_info:
            return None
        
        # Get column names
        col_names = [description[0] for description in cursor.description]
        video_dict = dict(zip(col_names, video_info))
        
        # Get frame data
        cursor.execute('''
            SELECT frame_number, tail_state, ear_state, head_state, posture_state
            FROM frame_analysis 
            WHERE video_id = ? 
            ORDER BY frame_number
        ''', (video_id,))
        
        frame_data = []
        for row in cursor.fetchall():
            frame_data.append({
                'frame_number': row[0],
                'tail_state': row[1],
                'ear_state': row[2],
                'head_state': row[3],
                'posture_state': row[4]
            })
        
        video_dict['frame_data'] = frame_data
        return video_dict
    
    def close(self):
        self.conn.close()