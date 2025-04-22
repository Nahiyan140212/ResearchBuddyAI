import streamlit as st
import pandas as pd
import plotly.express as px
from database_handler import DatabaseLogger
import datetime

def main():
    """Admin dashboard for viewing chat logs and statistics."""
    st.set_page_config(page_title="ResearchBuddy Admin", layout="wide")
    
    st.title("ResearchBuddy Admin Dashboard")
    
    # Password protection
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        with st.form("login_form"):
            password = st.text_input("Admin Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                # Simple password check - in production, use a more secure method
                # and store password securely in environment variables or secrets
                if password == "admin123":  # Replace with a secure password
                    st.session_state.admin_authenticated = True
                    st.experimental_rerun()
                else:
                    st.error("Incorrect password")
        return
    
    # Initialize database connection
    db_logger = DatabaseLogger()
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select a page",
            ["Overview", "Session List", "Interaction Details", "Export Data"]
        )
    
    if page == "Overview":
        # Get statistics
        stats = db_logger.get_stats()
        
        # Display statistics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sessions", stats["total_sessions"])
        with col2:
            st.metric("Total Interactions", stats["total_interactions"])
        with col3:
            st.metric("Most Popular Model", f"{stats['most_popular_model']} ({stats['most_popular_model_count']})")
        
        # Get data for visualizations
        st.subheader("Usage Analytics")
        
        # Query for model usage
        db_logger.cursor.execute(
            "SELECT model_name, COUNT(*) as count FROM interactions GROUP BY model_name ORDER BY count DESC"
        )
        model_usage = db_logger.cursor.fetchall()
        
        # Query for daily interactions
        db_logger.cursor.execute(
            "SELECT date(timestamp) as date, COUNT(*) as count FROM interactions GROUP BY date(timestamp) ORDER BY date"
        )
        daily_usage = db_logger.cursor.fetchall()
        
        # Create DataFrames
        if model_usage:
            model_df = pd.DataFrame(model_usage, columns=["Model", "Count"])
            fig1 = px.bar(model_df, x="Model", y="Count", title="Model Usage Distribution")
            st.plotly_chart(fig1)
        
        if daily_usage:
            daily_df = pd.DataFrame(daily_usage, columns=["Date", "Count"])
            fig2 = px.line(daily_df, x="Date", y="Count", title="Daily Interactions")
            st.plotly_chart(fig2)
        
        # Average execution time by model
        db_logger.cursor.execute(
            "SELECT model_name, AVG(execution_time_ms) as avg_time FROM interactions GROUP BY model_name"
        )
        execution_times = db_logger.cursor.fetchall()
        
        if execution_times:
            time_df = pd.DataFrame(execution_times, columns=["Model", "Average Time (ms)"])
            fig3 = px.bar(time_df, x="Model", y="Average Time (ms)", title="Average Response Time by Model")
            st.plotly_chart(fig3)
    
    elif page == "Session List":
        st.subheader("All Chat Sessions")
        
        # Get all sessions
        sessions = db_logger.get_all_sessions(limit=100)
        
        if sessions:
            sessions_df = pd.DataFrame(sessions, columns=["Session ID", "Start Time", "Browser", "IP"])
            sessions_df["Start Time"] = pd.to_datetime(sessions_df["Start Time"])
            
            # Add interaction count
            session_counts = []
            for session_id in sessions_df["Session ID"]:
                db_logger.cursor.execute(
                    "SELECT COUNT(*) FROM interactions WHERE session_id = ?",
                    (session_id,)
                )
                count = db_logger.cursor.fetchone()[0]
                session_counts.append(count)
            
            sessions_df["Messages"] = session_counts
            
            # Sort by most recent
            sessions_df = sessions_df.sort_values("Start Time", ascending=False)
            
            # Display the sessions with a filter
            min_messages = st.slider("Minimum Messages", 1, 50, 1)
            filtered_df = sessions_df[sessions_df["Messages"] >= min_messages]
            
            st.dataframe(filtered_df)
            
            # Session selection for detailed view
            selected_session = st.selectbox(
                "Select a session to view details",
                options=filtered_df["Session ID"].tolist(),
                format_func=lambda x: f"Session {x[:8]}... ({filtered_df[filtered_df['Session ID']==x]['Start Time'].iloc[0].strftime('%Y-%m-%d %H:%M')})"
            )
            
            if selected_session:
                st.session_state.selected_session_id = selected_session
                st.button("View Session Details", on_click=lambda: st.session_state.update({"page": "Interaction Details"}))
        else:
            st.info("No sessions found in the database.")
    
    elif page == "Interaction Details":
        st.subheader("Chat Interaction Details")
        
        # Check if session ID is selected or allow selection
        if "selected_session_id" not in st.session_state:
            session_ids = [row[0] for row in db_logger.get_all_sessions(limit=100)]
            if session_ids:
                selected_session = st.selectbox("Select a session", options=session_ids)
                st.session_state.selected_session_id = selected_session
            else:
                st.info("No sessions found.")
                return
        
        # Display interactions for the selected session
        interactions = db_logger.get_session_interactions(st.session_state.selected_session_id)
        
        if interactions:
            # Convert to DataFrame for better display
            interactions_df = pd.DataFrame(interactions, columns=[
                "Interaction ID", "Session ID", "Timestamp", "Model Name", "Model ID",
                "Temperature", "Max Tokens", "User Query", "Model Response",
                "Has File", "File Name", "Has Image", "Execution Time (ms)"
            ])
            
            # Format timestamp
            interactions_df["Timestamp"] = pd.to_datetime(interactions_df["Timestamp"])
            
            # Display metadata
            st.subheader(f"Session: {st.session_state.selected_session_id[:8]}...")
            session_start = interactions_df["Timestamp"].min()
            session_end = interactions_df["Timestamp"].max()
            duration = session_end - session_start
            
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            with meta_col1:
                st.metric("Messages", len(interactions_df))
            with meta_col2:
                st.metric("Duration", f"{duration.total_seconds()/60:.1f} minutes")
            with meta_col3:
                st.metric("Primary Model", interactions_df["Model Name"].value_counts().index[0])
            
            # Show full conversation
            st.subheader("Conversation")
            for _, row in interactions_df.iterrows():
                st.write(f"**Time:** {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Display user query in a blue box
                st.markdown(f"""
                <div style="background-color:#e6f2ff; padding:10px; border-radius:5px; margin-bottom:10px">
                <strong>User:</strong> {row['User Query']}
                </div>
                """, unsafe_allow_html=True)
                
                # Display model response in a green box
                st.markdown(f"""
                <div style="background-color:#e6ffe6; padding:10px; border-radius:5px; margin-bottom:20px">
                <strong>Assistant ({row['Model Name']}):</strong> {row['Model Response'][:200]}...
                <br><small>Response time: {row['Execution Time (ms)']}ms | Temp: {row['Temperature']} | Max tokens: {row['Max Tokens']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Expandable full response
                with st.expander("View full response"):
                    st.write(row['Model Response'])
                
                st.markdown("---")
        else:
            st.info(f"No interactions found for session {st.session_state.selected_session_id}")
    
    elif page == "Export Data":
        st.subheader("Export Database Data")
        
        export_type = st.radio("Select export type", ["All Sessions", "All Interactions", "Specific Session"])
        
        if export_type == "All Sessions":
            sessions = db_logger.get_all_sessions(limit=10000)
            if sessions:
                sessions_df = pd.DataFrame(sessions, columns=["Session ID", "Start Time", "Browser", "IP"])
                csv = sessions_df.to_csv(index=False)
                
                st.download_button(
                    label="Download Sessions CSV",
                    data=csv,
                    file_name=f"researchbuddy_sessions_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No sessions to export.")
        
        elif export_type == "All Interactions":
            # Warning about potential large file
            st.warning("This might be a large export depending on your database size.")
            if st.button("Generate Full Export"):
                db_logger.cursor.execute("SELECT * FROM interactions")
                interactions = db_logger.cursor.fetchall()
                
                if interactions:
                    interactions_df = pd.DataFrame(interactions, columns=[
                        "Interaction ID", "Session ID", "Timestamp", "Model Name", "Model ID",
                        "Temperature", "Max Tokens", "User Query", "Model Response",
                        "Has File", "File Name", "Has Image", "Execution Time (ms)"
                    ])
                    csv = interactions_df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download All Interactions CSV",
                        data=csv,
                        file_name=f"researchbuddy_all_interactions_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No interactions to export.")
        
        elif export_type == "Specific Session":
            session_ids = [row[0] for row in db_logger.get_all_sessions(limit=100)]
            if session_ids:
                selected_session = st.selectbox("Select a session to export", options=session_ids)
                
                if st.button("Generate Session Export"):
                    interactions = db_logger.get_session_interactions(selected_session)
                    
                    if interactions:
                        interactions_df = pd.DataFrame(interactions, columns=[
                            "Interaction ID", "Session ID", "Timestamp", "Model Name", "Model ID",
                            "Temperature", "Max Tokens", "User Query", "Model Response",
                            "Has File", "File Name", "Has Image", "Execution Time (ms)"
                        ])
                        csv = interactions_df.to_csv(index=False)
                        
                        st.download_button(
                            label="Download Session CSV",
                            data=csv,
                            file_name=f"researchbuddy_session_{selected_session[:8]}_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No interactions found for this session.")
            else:
                st.info("No sessions available to export.")
    
    # Close the database connection when done
    db_logger.close()

if __name__ == "__main__":
    main()
