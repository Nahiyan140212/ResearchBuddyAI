#!/usr/bin/env python3
"""
Database management tool for ResearchBuddy AI logs.
Use this script to perform database operations like queries, exports, and maintenance.
"""

import argparse
import pandas as pd
import sqlite3
import os
import sys
import datetime
from database_handler import DatabaseLogger

def list_sessions(db_logger, limit=10):
    """List the most recent sessions."""
    print(f"\nListing the {limit} most recent sessions:")
    print("-" * 80)
    
    sessions = db_logger.get_all_sessions(limit=limit)
    if not sessions:
        print("No sessions found in the database.")
        return
    
    # Print session information with interaction count
    print(f"{'Session ID':<40} | {'Start Time':<20} | {'Messages':<8}")
    print("-" * 80)
    
    for session in sessions:
        session_id = session[0]
        start_time = session[1]
        
        # Get interaction count
        db_logger.cursor.execute(
            "SELECT COUNT(*) FROM interactions WHERE session_id = ?",
            (session_id,)
        )
        count = db_logger.cursor.fetchone()[0]
        
        print(f"{session_id:<40} | {start_time:<20} | {count:<8}")

def show_session(db_logger, session_id):
    """Show details of a specific session."""
    # Get session details
    db_logger.cursor.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        (session_id,)
    )
    session = db_logger.cursor.fetchone()
    
    if not session:
        print(f"Session {session_id} not found.")
        return
    
    print(f"\nSession Details: {session_id}")
    print(f"Start Time: {session[1]}")
    print(f"Browser: {session[2]}")
    print(f"IP: {session[3]}")
    
    # Get interaction count and timing
    interactions = db_logger.get_session_interactions(session_id)
    
    if not interactions:
        print("No interactions found for this session.")
        return
    
    print(f"Total Messages: {len(interactions)}")
    
    # Calculate session duration
    first_time = interactions[0][2]
    last_time = interactions[-1][2]
    fmt = "%Y-%m-%d %H:%M:%S.%f"
    try:
        duration = datetime.datetime.strptime(last_time, fmt) - datetime.datetime.strptime(first_time, fmt)
        print(f"Session Duration: {duration}")
    except (ValueError, TypeError):
        print("Could not calculate session duration.")
    
    # List all interactions
    print("\nInteractions:")
    print("-" * 100)
    for i, interaction in enumerate(interactions):
        print(f"Message {i+1}: {interaction[2]}")
        print(f"User: {interaction[7][:100]}..." if len(interaction[7]) > 100 else f"User: {interaction[7]}")
        print(f"Assistant ({interaction[3]}): {interaction[8][:100]}..." if len(interaction[8]) > 100 else f"Assistant: {interaction[8]}")
        print("-" * 100)

def export_session(db_logger, session_id, output_format="csv"):
    """Export a session to a file."""
    interactions = db_logger.get_session_interactions(session_id)
    
    if not interactions:
        print(f"No interactions found for session {session_id}")
        return
    
    # Create a DataFrame
    df = pd.DataFrame(interactions, columns=[
        "Interaction ID", "Session ID", "Timestamp", "Model Name", "Model ID",
        "Temperature", "Max Tokens", "User Query", "Model Response",
        "Has File", "File Name", "Has Image", "Execution Time (ms)"
    ])
    
    # Create filename
    filename = f"researchbuddy_session_{session_id[:8]}_{datetime.datetime.now().strftime('%Y%m%d')}"
    
    if output_format == "csv":
        output_file = f"{filename}.csv"
        df.to_csv(output_file, index=False)
    elif output_format == "json":
        output_file = f"{filename}.json"
        df.to_json(output_file, orient="records", indent=2)
    elif output_format == "excel":
        output_file = f"{filename}.xlsx"
        df.to_excel(output_file, index=False)
    elif output_format == "text":
        output_file = f"{filename}.txt"
        with open(output_file, "w") as f:
            for _, row in df.iterrows():
                f.write(f"Time: {row['Timestamp']}\n")
                f.write(f"User: {row['User Query']}\n")
                f.write(f"Assistant ({row['Model Name']}): {row['Model Response']}\n")
                f.write("-" * 80 + "\n")
    else:
        print(f"Unsupported format: {output_format}")
        return
    
    print(f"Exported session to {output_file}")

def export_stats(db_logger, output_format="csv"):
    """Export usage statistics to a file."""
    # Get basic stats
    stats = db_logger.get_stats()
    
    # Query for model usage
    db_logger.cursor.execute(
        "SELECT model_name, COUNT(*) as count FROM interactions GROUP BY model_name ORDER BY count DESC"
    )
    model_usage = db_logger.cursor.fetchall()
    model_df = pd.DataFrame(model_usage, columns=["Model", "Count"])
    
    # Query for daily interactions
    db_logger.cursor.execute(
        "SELECT date(timestamp) as date, COUNT(*) as count FROM interactions GROUP BY date(timestamp) ORDER BY date"
    )
    daily_usage = db_logger.cursor.fetchall()
    daily_df = pd.DataFrame(daily_usage, columns=["Date", "Count"])
    
    # Query for average response time by model
    db_logger.cursor.execute(
        "SELECT model_name, AVG(execution_time_ms) as avg_time FROM interactions GROUP BY model_name"
    )
    execution_times = db_logger.cursor.fetchall()
    time_df = pd.DataFrame(execution_times, columns=["Model", "Average Time (ms)"])
    
    # Create filename
    filename = f"researchbuddy_stats_{datetime.datetime.now().strftime('%Y%m%d')}"
    
    if output_format == "csv":
        model_df.to_csv(f"{filename}_models.csv", index=False)
        daily_df.to_csv(f"{filename}_daily.csv", index=False)
        time_df.to_csv(f"{filename}_response_times.csv", index=False)
        print(f"Exported stats to {filename}_*.csv files")
    elif output_format == "json":
        stats_dict = {
            "overview": stats,
            "model_usage": model_df.to_dict(orient="records"),
            "daily_usage": daily_df.to_dict(orient="records"),
            "response_times": time_df.to_dict(orient="records")
        }
        with open(f"{filename}.json", "w") as f:
            import json
            json.dump(stats_dict, f, indent=2)
        print(f"Exported stats to {filename}.json")
    elif output_format == "excel":
        with pd.ExcelWriter(f"{filename}.xlsx") as writer:
            # Create overview sheet
            overview_df = pd.DataFrame([stats])
            overview_df.to_excel(writer, sheet_name="Overview", index=False)
            model_df.to_excel(writer, sheet_name="Model Usage", index=False)
            daily_df.to_excel(writer, sheet_name="Daily Usage", index=False)
            time_df.to_excel(writer, sheet_name="Response Times", index=False)
        print(f"Exported stats to {filename}.xlsx")
    else:
        print(f"Unsupported format: {output_format}")

def run_query(db_logger, query):
    """Run a custom SQL query on the database."""
    try:
        db_logger.cursor.execute(query)
        results = db_logger.cursor.fetchall()
        
        if not results:
            print("Query returned no results.")
            return
        
        # Get column names
        column_names = [description[0] for description in db_logger.cursor.description]
        
        # Create a DataFrame for better display
        df = pd.DataFrame(results, columns=column_names)
        
        # Print the results
        print("\nQuery Results:")
        print(df.to_string())
        print(f"\nTotal rows: {len(df)}")
        
    except sqlite3.Error as e:
        print(f"SQL error: {e}")

def cleanup_database(db_logger, days=30):
    """Clean up old records from the database."""
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    
    # Get count of records to be deleted
    db_logger.cursor.execute(
        "SELECT COUNT(*) FROM interactions WHERE datetime(timestamp) < datetime(?)",
        (cutoff_date.strftime("%Y-%m-%d %H:%M:%S"),)
    )
    interaction_count = db_logger.cursor.fetchone()[0]
    
    db_logger.cursor.execute(
        "SELECT COUNT(*) FROM sessions WHERE datetime(start_time) < datetime(?)",
        (cutoff_date.strftime("%Y-%m-%d %H:%M:%S"),)
    )
    session_count = db_logger.cursor.fetchone()[0]
    
    print(f"This will delete {interaction_count} interactions and {session_count} sessions older than {days} days.")
    confirmation = input("Are you sure you want to proceed? (y/n): ")
    
    if confirmation.lower() != 'y':
        print("Operation cancelled.")
        return
    
    try:
        # Delete old interactions
        db_logger.cursor.execute(
            "DELETE FROM interactions WHERE datetime(timestamp) < datetime(?)",
            (cutoff_date.strftime("%Y-%m-%d %H:%M:%S"),)
        )
        
        # Delete old sessions that have no interactions left
        db_logger.cursor.execute(
            """
            DELETE FROM sessions 
            WHERE session_id NOT IN (SELECT DISTINCT session_id FROM interactions)
            AND datetime(start_time) < datetime(?)
            """,
            (cutoff_date.strftime("%Y-%m-%d %H:%M:%S"),)
        )
        
        db_logger.conn.commit()
        print(f"Successfully deleted {interaction_count} interactions and {session_count} sessions.")
        
    except sqlite3.Error as e:
        print(f"Error during cleanup: {e}")

def main():
    parser = argparse.ArgumentParser(description="ResearchBuddy AI Database Management Tool")
    parser.add_argument("--db", help="Database file path", default="logs/chat_logs.db")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List sessions command
    list_parser = subparsers.add_parser("list", help="List recent chat sessions")
    list_parser.add_argument("--limit", type=int, default=10, help="Number of sessions to list")
    
    # Show session command
    show_parser = subparsers.add_parser("show", help="Show details of a specific session")
    show_parser.add_argument("session_id", help="Session ID to show")
    
    # Export session command
    export_parser = subparsers.add_parser("export-session", help="Export a session to a file")
    export_parser.add_argument("session_id", help="Session ID to export")
    export_parser.add_argument("--format", choices=["csv", "json", "excel", "text"], default="csv", help="Output format")
    
    # Export stats command
    stats_parser = subparsers.add_parser("stats", help="Export usage statistics")
    stats_parser.add_argument("--format", choices=["csv", "json", "excel"], default="csv", help="Output format")
    
    # Custom query command
    query_parser = subparsers.add_parser("query", help="Run a custom SQL query")
    query_parser.add_argument("sql_query", help="SQL query to execute")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old records")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Delete records older than this many days")
    
    args = parser.parse_args()
    
    # Check if database file exists
    if not os.path.exists(args.db) and args.command != "help":
        print(f"Database file not found: {args.db}")
        print("Please check the path or run the main application first to create the database.")
        sys.exit(1)
    
    # Initialize database connection
    db_logger = DatabaseLogger(db_path=args.db)
    
    try:
        if args.command == "list":
            list_sessions(db_logger, args.limit)
        elif args.command == "show":
            show_session(db_logger, args.session_id)
        elif args.command == "export-session":
            export_session(db_logger, args.session_id, args.format)
        elif args.command == "stats":
            export_stats(db_logger, args.format)
        elif args.command == "query":
            run_query(db_logger, args.sql_query)
        elif args.command == "cleanup":
            cleanup_database(db_logger, args.days)
        else:
            parser.print_help()
    finally:
        # Close database connection
        db_logger.close()

if __name__ == "__main__":
    main()
