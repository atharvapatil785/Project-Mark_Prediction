import os
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox
from sklearn.linear_model import LinearRegression

# ==========================================
# PART 1: GENERATE DATA & TRAIN MODEL
# ==========================================

def train_and_save_model():
    # 1. Generate Dummy Data
    num_students = 200
    total_lectures = 60
    
    # Random data generation
    attendance = np.random.randint(20, total_lectures + 1, num_students)
    unit_test = np.random.randint(5, 31, num_students)
    practicals = np.random.randint(10, 21, num_students)
    insem = np.random.randint(10, 31, num_students)
    
    # Calculate realistic EndSem score
    calculated_score = (
        (unit_test * 0.5) + (practicals * 0.8) + (insem * 0.8) + 
        ((attendance / total_lectures) * 10) + np.random.randint(-10, 10, num_students)
    )
    endsem = np.clip(calculated_score, 0, 70).astype(int)
    
    # Create DataFrame
    df = pd.DataFrame({
        'lecture_attended': attendance,
        'total_lectures_alloted': total_lectures, # Added this column to CSV
        'unit_test_score_outoff_30': unit_test,
        'Practicals_score_outoff_20': practicals,
        'insem_score_outoff_30': insem,
        'endsem_score_outoff_70': endsem
    })

    # 1. Get the folder where THIS python file is located
    current_folder = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Combine that folder path with the filename
    file_path = os.path.join(current_folder, "student_marks_dataset.csv")
    
    # Save the data to a CSV file on your computer
    df.to_csv(file_path, index=False)
    print(f"Success: 'student_marks_dataset.csv' has been created at: {file_path}")

    # 2. Train Linear Regression
    X = df[['lecture_attended', 'unit_test_score_outoff_30', 
            'Practicals_score_outoff_20', 'insem_score_outoff_30']]
    y = df['endsem_score_outoff_70']
    
    model = LinearRegression()
    model.fit(X, y)
    
    return model

# Run the training function immediately
print("Training model and generating CSV...")
trained_model = train_and_save_model()

# ==========================================
# PART 2: THE GUI PREDICTION LOGIC
# ==========================================
def predict_result():
    try:
        # Get inputs
        lectures = int(entry_lectures.get())
        total_lec = int(entry_total_lec.get()) # Used for validation only
        unit_test = float(entry_ut.get())
        practical = float(entry_prac.get())
        insem = float(entry_insem.get())

        if lectures > total_lec:
            messagebox.showerror("Error", "Attended lectures cannot be more than Total lectures!")
            return

        # Prepare input for model
        input_data = pd.DataFrame([[lectures, unit_test, practical, insem]], 
                                  columns=['lecture_attended', 'unit_test_score_outoff_30', 
                                           'Practicals_score_outoff_20', 'insem_score_outoff_30'])

        # Predict
        pred_endsem = trained_model.predict(input_data)[0]
        final_endsem = round(pred_endsem)

        # Clip result
        if final_endsem > 70: final_endsem = 70
        if final_endsem < 0: final_endsem = 0

        # Grading Logic
        total_marks = final_endsem + insem
        
        if final_endsem < 28:
            grade = "FAIL (EndSem < 28)"
            color = "red"
        elif total_marks < 40:
            grade = "FAIL (Total < 40)"
            color = "red"
        elif 40 <= total_marks < 55:
            grade = "Pass (Third Class)"
            color = "#FF8C00" # Dark Orange
        elif 55 <= total_marks < 65:
            grade = "Pass (Second Class)"
            color = "blue"
        elif 65 <= total_marks < 75:
            grade = "Pass (First Class)"
            color = "green"
        else:
            grade = "Pass (Distinction)"
            color = "green"

        result_text.set(f"Predicted EndSem: {final_endsem} / 70\n"
                        f"Total Marks: {total_marks} / 100\n"
                        f"Result: {grade}")
        lbl_result.config(fg=color)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers.")

# ==========================================
# PART 3: CREATE THE GUI WINDOW
# ==========================================
root = tk.Tk()
root.title("Student Marks Predictor")
root.geometry("400x550")

tk.Label(root, text="Student Performance Predictor", font=("Arial", 16, "bold")).pack(pady=15)

frame_inputs = tk.Frame(root)
frame_inputs.pack(pady=5)

def create_field(label_text, row):
    tk.Label(frame_inputs, text=label_text, font=("Arial", 10)).grid(row=row, column=0, padx=10, pady=8, sticky="e")
    entry = tk.Entry(frame_inputs)
    entry.grid(row=row, column=1, padx=10, pady=8)
    return entry

entry_lectures = create_field("Lectures Attended:", 0)
entry_total_lec = create_field("Total Lectures Alloted:", 1)
entry_ut = create_field("Unit Test Score (30):", 2)
entry_prac = create_field("Practical Score (20):", 3)
entry_insem = create_field("InSem Score (30):", 4)

# Set defaults
entry_total_lec.insert(0, "60")

btn_predict = tk.Button(root, text="Predict Result", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=predict_result)
btn_predict.pack(pady=20)

result_text = tk.StringVar()
result_text.set("Enter details to see prediction")
lbl_result = tk.Label(root, textvariable=result_text, font=("Arial", 14, "bold"), justify="center")
lbl_result.pack(pady=10)

root.mainloop()