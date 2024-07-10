from datetime import datetime, timedelta
from collections import Counter
from waweza.models import Goal, Habit, HabitLog, Mood, StatusType, MoodType
from sqlalchemy import func

def get_week_range():
    today = datetime.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end

def get_analytics_data():
    start, end = get_week_range()
    
    goals = Goal.query.all()
    habits = Habit.query.all()
    habit_logs = HabitLog.query.filter(HabitLog.date >= start, HabitLog.date <= end).all()
    moods = Mood.query.filter(Mood.date >= start, Mood.date <= end).all()

    goal_progress = {goal.title: goal.status.value for goal in goals}
    
    habit_completion = {habit.name: sum(1 for log in habit.logs if log.completed and start <= log.date <= end) for habit in habits}
    
    mood_counter = Counter(mood.mood_type.value for mood in moods)
    
    goals_completed = sum(1 for goal in goals if goal.status == StatusType.COMPLETED) / len(goals) if goals else 0
    
    habit_completion_rate = sum(habit_completion.values()) / (len(habits) * 7) if habits else 0
    
    most_common_mood = max(mood_counter, key=mood_counter.get, default=None)
    
    mood_trend = 'Stable'
    if moods:
        mood_values = [mood.mood_type.value for mood in moods]
        if len(mood_values) > 1:
            if mood_values[-1] > mood_values[0]:
                mood_trend = 'Improving'
            elif mood_values[-1] < mood_values[0]:
                mood_trend = 'Declining'

    mood_over_time = {
        'dates': [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)],
        'values': [next((mood.mood_type.value for mood in moods if mood.date.date() == (start + timedelta(days=i)).date()), None) for i in range(7)]
    }

    goal_habit_correlation = [
        {'x': goal.status.value, 'y': sum(1 for log in habit.logs if log.completed and start <= log.date <= end) / 7}
        for goal in goals
        for habit in habits
    ]

    return {
        'goal_progress': goal_progress,
        'habit_completion': habit_completion,
        'mood_counter': dict(mood_counter),
        'goals_completed': round(goals_completed * 100, 2),
        'habit_completion_rate': round(habit_completion_rate * 100, 2),
        'most_common_mood': MoodType(most_common_mood).name if most_common_mood else 'No data',
        'mood_trend': mood_trend,
        'mood_over_time': mood_over_time,
        'goal_habit_correlation': goal_habit_correlation
    }

def calculate_habit_streak(user_id):
    current_date = datetime.utcnow().date()
    streak = 0
    
    # Query to get all user's habits
    habits = Habit.query.filter_by(user_id=user_id).all()
    
    if not habits:
        return 0
    
    while True:
        # Check if all habits were completed for the current date
        completed_habits = HabitLog.query.filter(
            HabitLog.habit_id.in_([h.id for h in habits]),
            func.date(HabitLog.date) == current_date,
            HabitLog.completed == True
        ).count()
        
        if completed_habits == len(habits):
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak