from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Expense {self.category} {self.amount}>'

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    categories = db.session.query(Expense.category, db.func.sum(Expense.amount).label('total_amount')).group_by(Expense.category).all()
    return render_template('index.html', categories=categories)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        amount = request.form['amount']
        
        if not category or not amount:
            flash('Please fill all the fields')
            return redirect(url_for('add_expense'))

        try:
            amount = float(amount)
        except ValueError:
            flash('Amount should be a number')
            return redirect(url_for('add_expense'))

        date = datetime.now().strftime('%Y-%m-%d')
        new_expense = Expense(date=date, category=category, amount=amount)
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully')
        return redirect(url_for('index'))
    
    return render_template('add_expense.html')

@app.route('/category/<category>')
def category_expenses(category):
    expenses = Expense.query.filter_by(category=category).all()
    return render_template('category_expenses.html', category=category, expenses=expenses)

if __name__ == '__main__':
    app.run(debug=True)
