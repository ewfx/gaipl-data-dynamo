from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
import pandas as pd
import subprocess
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///platform.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/infrastructure')
@login_required
def infrastructure():
    return render_template('infrastructure.html')

@app.route('/monitoring')
@login_required
def monitoring():
    return render_template('monitoring.html')

@app.route('/deployments')
@login_required
def deployments():
    return render_template('deployments.html')

# Add these new routes
@app.route('/tickets')
@login_required
def tickets():
    try:
        # Read Excel file
        df = pd.read_excel('c:\\Users\\Biju\\trae\\static\\data\\tickets.xlsx')
        tickets_data = df.to_dict('records')
        # Count open tickets
        open_tickets_count = len(df[df['Status'] == 'Open'])
        return render_template('tickets.html', tickets=tickets_data, open_count=open_tickets_count)
    except Exception as e:
        flash(f'Error reading tickets data: {str(e)}')
        return render_template('tickets.html', tickets=[], open_count=0)

@app.route('/inspire', methods=['POST'])
@login_required
def inspire():
    try:
        # Replace with your Python script path
        result = subprocess.run(['python', 'c:\\Users\\Biju\\trae\\scripts\\inspire.py'], 
                              capture_output=True, text=True)
        return jsonify({'status': 'success', 'message': 'Script executed successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        user_message = request.json.get('message', '').strip()
        
        # First check if it's a ticket query
        tickets_df = pd.read_excel('c:\\Users\\Biju\\trae\\static\\data\\tickets.xlsx')
        print("Available columns:", tickets_df.columns.tolist())  # Debug print
        
        # Direct match for incident number
        if user_message in tickets_df['Incident'].values:
            ticket = tickets_df[tickets_df['Incident'] == user_message].iloc[0]
            # Get all columns dynamically
            response = "Incident Details:\n"
            for column in tickets_df.columns:
                response += f"{column}: {ticket[column]}\n"
            return jsonify({'response': response})
        
        # If no ticket found, check QA database
        qa_df = pd.read_excel('c:\\Users\\Biju\\trae\\static\\data\\chatbot_qa.xlsx')
        qa_df['Question_Lower'] = qa_df['Question'].str.lower()
        match = qa_df[qa_df['Question_Lower'].str.contains(user_message.lower(), na=False)]
        
        if not match.empty:
            response = match.iloc[0]['Answer']
        else:
            response = "I'm sorry, I couldn't find that incident number or answer your question. Please try again with a valid incident number or question."
            
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error details: {str(e)}")  # Debug print
        return jsonify({'response': f"Error processing request. Please try again."})

@app.route('/ai-insights')
@login_required
def ai_insights():
    return render_template('ai_insights.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            test_user = User(username='admin', password='admin')
            db.session.add(test_user)
            db.session.commit()
    app.run(debug=True)