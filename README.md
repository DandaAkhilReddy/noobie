# Gym Progress Tracker

A simple Python Flask web application to track your gym progress, food intake, calories, and protein consumption.

## Features

- **Food Logging**: Add foods to database with calories and protein per 100g
- **Daily Tracking**: Log food consumption and track daily calories/protein
- **Weight Tracking**: Record your daily weight
- **Protein Target**: Set and track daily protein goals
- **Analytics**: View 7-day trends with interactive charts
- **Clean UI**: Bootstrap-based responsive interface

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Visit `http://localhost:5000`

## Usage

1. **Add Foods**: Go to "Add Food" to create your food database
2. **Log Daily Weight**: Enter your weight on the dashboard
3. **Set Protein Target**: Adjust your daily protein goal
4. **Log Food**: Select foods and quantities to track consumption
5. **View Analytics**: Check your progress trends and achievements

## Azure Deployment

This app is configured for Azure App Service deployment:

1. Update `app.yaml` with your Azure configuration
2. Set up Azure DevOps pipeline using `azure-pipelines.yml`
3. Configure service connections and variables
4. Push to trigger deployment

## Database

Uses SQLite by default. For production, update `DATABASE_URL` environment variable to use PostgreSQL or other databases.

## Project Structure

```
├── app.py              # Main Flask application
├── models.py          # Database models
├── requirements.txt   # Python dependencies
├── templates/         # HTML templates
├── static/           # CSS and JS files
├── app.yaml          # Azure App Service config
└── Dockerfile        # Container configuration
```