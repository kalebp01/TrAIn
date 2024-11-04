from PIL import Image
import openai
import time

# Set your API key
openai.api_key = "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"

# Generates prompt to chat GPT
def get_workout_plan(data, retries=3):
    # Convert metric values to imperial
    height_inches = round(data['height'] * 0.393701, 2)
    weight_pounds = round(data['weight'] * 2.20462, 2)
    
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

        Be specific with instructions for each workout activity (Ex: explain how to perform squats, situps, etc.)
        Disregard adding any notes or conclusion section I only want the workout routine and instructions.
        Unless specified, make workouts 4 day regimens without including rest days.
        Sets and Reps instead of separate lines should appear as X sets and Y reps.
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

    # Dictionary containing workout images with relative paths
    workout_images = {
        "bench press": "bench_press.jpg",
        "squat": "squat.jpg",
        "deadlift": "deadlift.jpg",
        "bicep curls": "bicep_curls.jpg",
        "shoulder press": "shoulder_press.jpg"
    }

    # Retry logic in case of rate limit error
    for attempt in range(retries):
        try:
            # Request to the OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[system_message, user_message],
                max_tokens=1300,
                temperature=0.7
            )
            # Extract the workout plan content
            workout_plan = response['choices'][0]['message']['content'].strip()

            # Select only relevant images based on exercises mentioned in the response
            included_images = {exercise: path for exercise, path in workout_images.items() if exercise in workout_plan.lower()}

            # Return the workout plan and relevant images
            return {
                "workout_plan": workout_plan,
                "images": included_images
            }

        except openai.error.RateLimitError:
            wait_time = 2 ** attempt
            print(f"Rate limit exceeded. Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)

    print("Max retries reached. Please check your API quota.")
    return None

# Test with sample data
user_data = {
    'height': 100,       
    'weight': 120,
    'bmi': 30.9,
    'goals': "lose weight and build muscle",
    'intensity': "moderate",
    'age': 22,
    'gender': "female",
    'duration': 60,
    'heart_rate': 90
}

# Generate and print workout plan with images
workout_data = get_workout_plan(user_data)
if workout_data:
    print("Generated Workout Plan:")
    print(workout_data["workout_plan"])
    print("\nDisplaying Associated Workout Images:")

    # Display each relevant image using PIL
    for exercise, image_path in workout_data["images"].items():
        print(f"Displaying image for: {exercise.title()}")
        image = Image.open(image_path)
        image.show()
else:
    print("Failed to generate workout plan due to rate limit.")