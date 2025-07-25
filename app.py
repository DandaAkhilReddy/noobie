from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gym_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import Food, WeightLog, DailyLog, FoodEntry

@app.route('/')
def index():
    today = date.today()
    daily_log = DailyLog.query.filter_by(date=today).first()
    if not daily_log:
        daily_log = DailyLog(date=today)
        db.session.add(daily_log)
        db.session.commit()
    
    weight_log = WeightLog.query.filter_by(date=today).first()
    recent_foods = FoodEntry.query.filter_by(daily_log_id=daily_log.id).all()
    
    all_foods = Food.query.all()
    return render_template('index.html', 
                         daily_log=daily_log, 
                         weight_log=weight_log,
                         recent_foods=recent_foods,
                         all_foods=all_foods)

@app.route('/add_food', methods=['GET', 'POST'])
def add_food():
    if request.method == 'POST':
        name = request.form['name']
        calories = float(request.form['calories'])
        protein = float(request.form['protein'])
        
        food = Food(name=name, calories_per_100g=calories, protein_per_100g=protein)
        db.session.add(food)
        db.session.commit()
        flash('Food added successfully!')
        return redirect(url_for('index'))
    
    return render_template('add_food.html')

@app.route('/log_food', methods=['POST'])
def log_food():
    food_id = int(request.form['food_id'])
    quantity = float(request.form['quantity'])
    
    food = Food.query.get(food_id)
    today = date.today()
    daily_log = DailyLog.query.filter_by(date=today).first()
    
    if not daily_log:
        daily_log = DailyLog(date=today)
        db.session.add(daily_log)
        db.session.commit()
    
    calories = (food.calories_per_100g * quantity) / 100
    protein = (food.protein_per_100g * quantity) / 100
    
    food_entry = FoodEntry(
        daily_log_id=daily_log.id,
        food_id=food_id,
        quantity_grams=quantity,
        calories=calories,
        protein=protein
    )
    
    db.session.add(food_entry)
    
    daily_log.total_calories += calories
    daily_log.total_protein += protein
    
    db.session.commit()
    flash('Food logged successfully!')
    return redirect(url_for('index'))

@app.route('/log_weight', methods=['POST'])
def log_weight():
    weight = float(request.form['weight'])
    today = date.today()
    
    weight_log = WeightLog.query.filter_by(date=today).first()
    if weight_log:
        weight_log.weight = weight
    else:
        weight_log = WeightLog(weight=weight, date=today)
        db.session.add(weight_log)
    
    db.session.commit()
    flash('Weight logged successfully!')
    return redirect(url_for('index'))

@app.route('/foods')
def foods():
    all_foods = Food.query.all()
    return render_template('foods.html', foods=all_foods)

@app.route('/analytics')
def analytics():
    today = date.today()
    daily_log = DailyLog.query.filter_by(date=today).first()
    
    # Get last 7 days of data
    import pandas as pd
    from datetime import timedelta
    
    end_date = today
    start_date = today - timedelta(days=6)
    
    daily_logs = DailyLog.query.filter(DailyLog.date >= start_date, DailyLog.date <= end_date).all()
    weight_logs = WeightLog.query.filter(WeightLog.date >= start_date, WeightLog.date <= end_date).all()
    
    # Calculate protein target achievement
    protein_achieved = daily_log.total_protein >= daily_log.protein_target if daily_log else False
    protein_percentage = round((daily_log.total_protein / daily_log.protein_target) * 100, 1) if daily_log and daily_log.protein_target > 0 else 0
    
    return render_template('analytics.html', 
                         daily_log=daily_log,
                         daily_logs=daily_logs,
                         weight_logs=weight_logs,
                         protein_achieved=protein_achieved,
                         protein_percentage=protein_percentage)

@app.route('/set_protein_target', methods=['POST'])
def set_protein_target():
    target = float(request.form['target'])
    today = date.today()
    
    daily_log = DailyLog.query.filter_by(date=today).first()
    if not daily_log:
        daily_log = DailyLog(date=today, protein_target=target)
        db.session.add(daily_log)
    else:
        daily_log.protein_target = target
    
    db.session.commit()
    flash('Protein target updated successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)