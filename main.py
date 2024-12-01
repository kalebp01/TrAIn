from flask import Flask, request, render_template_string, url_for
from PIL import Image
import openai
import time
import re

# Set your API key
openai.api_key = "***Available Upon Request***"

app = Flask(__name__)

# Dictionary of exercise images
exercise_images = {
    "bench press": "static/bench_press.jpg",
    "dumbell row": "static/dumbell_row.jpg",
    "deadlift": "static/deadlift.jpg",
    "push up": "static/push_ups.jpg",
    "squat": "static/squat.jpg",
    "russian twists": "static/russian_twists.jpg"
}

# Generates prompt to chat GPT
def get_workout_plan(data, retries=3):
    height_inches = data['height']
    weight_pounds = data['weight']
    
    system_message = {
        "role": "system",
        "content": f"""You are an AI-powered workout coach. Based on the following user data, generate the best possible workout plan for them:

        Height: {height_inches} inches
        Weight: {weight_pounds} pounds
        BMI: {data['bmi']}
        Goals: {data['goals']}
        Intensity Level: {data['intensity']}
        Age: {data['age']}
        Gender: {data['gender']}
        Duration: {data['duration']} minutes per session
        Average Heart Rate: {data['heart_rate']} bpm

        Please provide a detailed workout plan that includes:
        1. Exercise names
        2. Sets and reps
        3. Rest times
        4. Weekly schedule

        Include instructions for each exercise in 2-3 concise sentences.
        Do not add a summary at the bottom of the response.
        """
    }
    
    user_message = {
        "role": "user",
        "content": f"""
        Please generate a personalized workout plan based on these details:
        
        - Height: {height_inches} inches
        - Weight: {weight_pounds} pounds
        - BMI: {data['bmi']}
        - Goals: {data['goals']}
        - Intensity Level: {data['intensity']}
        - Age: {data['age']}
        - Gender: {data['gender']}
        - Session Duration: {data['duration']} minutes
        - Average Heart Rate: {data['heart_rate']} bpm
        """
    }

    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[system_message, user_message],
                max_tokens=1300,
                temperature=0.7
            )
            workout_plan = response['choices'][0]['message']['content'].strip()
            return workout_plan

        except openai.error.RateLimitError:
            wait_time = 2 ** attempt
            time.sleep(wait_time)

    return "Failed to generate workout plan due to rate limit."


@app.route('/')
def form():
    form_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Workout Plan Form</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: black;
                color: white;
                margin: 0;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }

            form {
                background-color: #222;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
                width: 100%;
                max-width: 400px;
            }

            label {
                display: block;
                margin-bottom: 8px;
                font-size: 14px;
                color: #00bf63;
            }

            input, select, button {
                width: 100%;
                padding: 10px;
                margin-bottom: 20px;
                border: 1px solid #00bf63;
                border-radius: 5px;
                background-color: white;
                color: black;
                font-size: 14px;
            }

            button {
                background-color: #00bf63;
                color: white;
                cursor: pointer;
                font-size: 16px;
            }

            button:hover {
                background-color: #00a352;
            }
        </style>
    </head>
    <body>
        <form action="/submit" method="post">
            <label for="height">Height (inches):</label>
            <input type="number" id="height" name="height" step="0.1" required>
            
            <label for="weight">Weight (pounds):</label>
            <input type="number" id="weight" name="weight" step="0.1" required>
            
            <label for="goals">Goals:</label>
            <input type="text" id="goals" name="goals" required>
            
            <label for="intensity">Intensity Level:</label>
            <select id="intensity" name="intensity" required>
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
            </select>
            
            <label for="age">Age:</label>
            <input type="number" id="age" name="age" required>
            
            <label for="gender">Gender:</label>
            <select id="gender" name="gender" required>
                <option value="male">Male</option>
                <option value="female">Female</option>
            </select>
            
            <label for="duration">Session Duration (minutes):</label>
            <input type="number" id="duration" name="duration" required>
            
            <label for="heart_rate">Average Heart Rate (bpm):</label>
            <input type="number" id="heart_rate" name="heart_rate" required>
            
            <button type="submit">Generate Workout Plan</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(form_html)


@app.route('/submit', methods=['POST'])
def submit_form():
    # Process user inputs
    height_inches = float(request.form['height'])
    weight_pounds = float(request.form['weight'])
    height_cm = height_inches * 2.54
    weight_kg = weight_pounds * 0.453592
    bmi = round(weight_kg / (height_cm / 100) ** 2, 2)
    
    user_data = {
        'height': height_inches,
        'weight': weight_pounds,
        'bmi': bmi,
        'goals': request.form['goals'],
        'intensity': request.form['intensity'],
        'age': int(request.form['age']),
        'gender': request.form['gender'],
        'duration': int(request.form['duration']),
        'heart_rate': int(request.form['heart_rate']),
    }

    workout_plan = get_workout_plan(user_data)

    # Highlight days and replace with <b>
    workout_plan = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", workout_plan)

    image_html = ""
    for exercise, image_filename in exercise_images.items():
        if exercise.lower() in workout_plan.lower():
            # Directly use the relative path to the image in the static folder
            image_html += f'<img src="/{image_filename}" alt="{exercise}" style="max-width: 100%; margin-bottom: 20px;"><br>'

    # Render the result page
    result_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generated Workout Plan</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: black;
                color: white;
                margin: 0;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
            }}
            .container {{
                background-color: #222;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
                width: 100%;
                max-width: 800px;
            }}
            h1 {{
                color: #00bf63;
                text-align: center;
            }}
            pre {{
                background-color: black;
                padding: 20px;
                color: #00bf63;
                border: 1px solid #00bf63;
                border-radius: 5px;
                font-family: 'Courier New', Courier, monospace;
                font-size: 1.2rem;
                overflow-x: auto;
                white-space: pre-wrap;
                line-height: 1.5;
            }}
            img {{
                display: block;
                max-width: 100%;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Generated Workout Plan</h1>
            {image_html}
            <pre>{workout_plan}</pre>
        </div>
    </body>
    </html>
    """
    return render_template_string(result_html)


if __name__ == '__main__':
    app.run(debug=True)
