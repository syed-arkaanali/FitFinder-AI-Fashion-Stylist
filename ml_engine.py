import joblib
import pandas as pd

def load_models():
    """Loads all the pickled ML models."""
    bodytype_pipeline = joblib.load("models/bodytype_pipeline.pkl")
    bodytype_labels = joblib.load("models/bodytype_labels.pkl")
    size_model = joblib.load("models/size_category_model.pkl")
    size_columns = joblib.load("models/model_columns.pkl")
    
    return bodytype_pipeline, bodytype_labels, size_model, size_columns

def predict_fit(bodytype_pipeline, bodytype_labels, size_model, size_columns, 
                waist_cm, height_cm, arm_cm, leg_cm, age, weight_lbs, height_inches):
    """
    Runs the K-Means and Random Forest models with the BMI override logic.
    Returns a dictionary with the results.
    """
    # 1. Body Type Prediction
    bodytype_input = pd.DataFrame([{
        "Waist_Circumference_cm": waist_cm, "Height_cm": height_cm,
        "Arm_Length_cm": arm_cm, "UpperLeg_Length_cm": leg_cm
    }])
    
    cluster_id = bodytype_pipeline.predict(bodytype_input)[0]
    predicted_body_type = bodytype_labels[cluster_id]

    # 2. BMI Calculation & Override
    bmi = (weight_lbs / (height_inches ** 2)) * 703
    final_body_type = predicted_body_type

    if predicted_body_type == "Tall-Heavy":
        if bmi < 18.5: 
            final_body_type = "Slim-Tall"
        elif bmi >= 25: 
            final_body_type = "Tall-Broad"

    # 3. Size Prediction
    size_input = pd.DataFrame([{
        "age": age, "height_inches": height_inches,
        "weight_lbs": weight_lbs, "mapped_body_type": final_body_type
    }])
    
    size_input = pd.get_dummies(size_input, columns=["mapped_body_type"])
    size_input = size_input.reindex(columns=size_columns, fill_value=0)
    predicted_size = size_model.predict(size_input)[0]

    # Return everything as a clean dictionary
    return {
        "body_type": final_body_type, 
        "size": str(predicted_size),
        "bmi": round(bmi, 2)
    }