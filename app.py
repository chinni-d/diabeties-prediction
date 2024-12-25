from flask import Flask, render_template, request, make_response
import joblib
import numpy as np
import pdfkit  # Ensure this is installed

app = Flask(__name__)

# Load the trained model
model = joblib.load('diabetes_ensemble_model.pkl')


# Route for home page
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/predict')
def prediction():
    return render_template('predict.html')
@app.route('/predict', methods=['POST'])
def predict():
    # Get the form data safely
    name = request.form.get('name', 'Anonymous')
    gender = request.form.get('gender', 'Not Specified')

    # Collect numerical inputs, ensuring they are converted to float
    inputs = []
    try:
        inputs = [
            float(request.form.get('pregnancies', 0)),
            float(request.form.get('insulin', 0)),
            float(request.form.get('glucose', 0)),
            float(request.form.get('bmi', 0)),
            float(request.form.get('blood_pressure', 0)),
            float(request.form.get('diabetes_pedigree', 0)),
            float(request.form.get('skin_thickness', 0)),
            float(request.form.get('age', 0))
        ]
    except ValueError:
        return "Invalid input detected. Please check your form data."

    # Convert the inputs into a 2D array for prediction
    final_features = np.array([inputs])

    # Predict using the loaded model
    prediction = model.predict(final_features)

    # Interpret the result
    result = 'It has been determined that you have diabetes.' if prediction[0] == 1 else 'The analysis shows a healthy glucose response; you are not diabetic.'
    result_class = 'diabetes' if prediction[0] == 1 else 'healthy'
    # Render the result page with inputs and prediction result
    return render_template('result.html', inputs=[name, gender] + inputs, prediction_text=f'Diabetes Test Result: {result}', result_class=result_class)
# New route for recommendations
@app.route('/recommendations', methods=['POST'])
def recommendations():
    # Get data passed from the form (name, gender, etc.)
    name = request.form.get('name', 'Anonymous')
    gender = request.form.get('gender', 'Not Specified')

    # Sample recommendations
    recommendations = [
        "Maintain a healthy diet rich in vegetables and lean proteins.",
        "Exercise regularly to manage blood sugar levels.",
        "Consult your healthcare provider for further advice.",
        "Stay hydrated and avoid sugary drinks."
    ]

    return render_template('recommendations.html', name=name, recommendations=recommendations)

path_to_wkhtmltopdf = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'  # Update this if necessary
pdfkit_config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)


@app.route('/print-report', methods=['POST'])
def print_report():
    # Collect form data for the report
    name = request.form.get('name', 'Anonymous')
    gender = request.form.get('gender', 'Not Specified')
    prediction_text = request.form.get('prediction_text', 'No prediction available.')

    # Gather inputs from the form
    inputs = [
        request.form.get('pregnancies', '0'),
        request.form.get('insulin', '0'),
        request.form.get('glucose', '0'),
        request.form.get('bmi', '0'),
        request.form.get('blood_pressure', '0'),
        request.form.get('diabetes_pedigree', '0'),
        request.form.get('skin_thickness', '0'),
        request.form.get('age', '0')
    ]


    # Debug print to verify input values
    print("Report Inputs:", name, gender, inputs, prediction_text)
# Determine the CSS class based on the prediction result

    # Render the HTML template for the report
    rendered_html = render_template('report_template.html', name=name, gender=gender, inputs=inputs, prediction_text=prediction_text)

    # Convert HTML to PDF using pdfkit
    try:
        pdf = pdfkit.from_string(rendered_html, False, configuration=pdfkit_config)
    except Exception as e:
        print("Error generating PDF:", e)
        return "There was an error generating the PDF report."

    # Create a response to open the PDF in a new tab
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=diabetes_report.pdf'

    return response

if __name__ == "__main__":
    app.run(debug=True)
