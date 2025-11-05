# app.py
from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import plotly.express as px
import plotly.io as pio
import io
import markdown # Used to render the markdown output from the LLM

# Import the new modules
from data_scraper import scrape_everything 
from llm_analyzer import generate_insights, run_simulation

app = Flask(__name__)
# Use session for real apps, global var for this simple example
global_df = None
global_insights = None
global_simulation_result = None

# --- Helper Functions ---
def create_sample_excel():
    """Generates a sample Excel file dynamically and saves it locally."""
    sample_data = {
        'Product': ['Laptop', 'Laptop', 'Smartphone', 'Smartphone', 'Laptop', 'Smartphone'],
        'Market': ['North', 'South', 'North', 'South', 'North', 'South'],
        'Zone': ['Zone A', 'Zone B', 'Zone A', 'Zone B', 'Zone A', 'Zone B'],
        'Sales': [12000, 8500, 15000, 9200, 11000, 14500],
        'Profit': [3000, 1500, 4500, 2100, 2800, 4200],
        'Year': [2021, 2021, 2022, 2022, 2023, 2023]
    }
    df_sample = pd.DataFrame(sample_data)
    file_path = 'static/Sample_Data.xlsx'
    df_sample.to_excel(file_path, index=False)
    return file_path

# --- Flask Routes ---

@app.route('/')
def upload_file_page():
    create_sample_excel() 
    return render_template('upload.html')

@app.route('/download-sample')
def download_sample():
    path = 'static/Sample_Data.xlsx'
    return send_file(path, as_attachment=True, download_name='Sample_Company_Data.xlsx')

@app.route('/upload', methods=['POST'])
def upload_file():
    global global_df
    global global_insights
    global_insights = None # Clear previous insights

    file = request.files.get('file')
    company_name = request.form.get('company_name', 'Default Company')
    company_cik = request.form.get('company_cik', '00000000')
    
    if not file or file.filename == '':
        return redirect(url_for('upload_file_page'))
        
    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        try:
            global_df = pd.read_excel(file)
            
            # --- Integration Step: Scrape data and generate insights ---
            global_scraped_data_text = scrape_everything(company_name, company_cik)
            # global_insights = generate_insights(global_df, scraped_data)
            
            return redirect(url_for('dashboard'))
        except Exception as e:
            return f"<div style='color:red;'>Error processing file or generating insights: {e}</div>"
            
    return "Invalid file format."

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global global_df
    global global_insights
    global global_simulation_result

    if global_df is None or global_df.empty:
        return redirect(url_for('upload_file_page'))
    
    # Handle simulation request POST request
    if request.method == 'POST' and 'scenario_text' in request.form:
        scenario = request.form['scenario_text']
        global_simulation_result = run_simulation(global_df, scenario)
    
    # Generate Plotly Chart
    if all(col in global_df.columns for col in ['Product', 'Sales', 'Market']):
        agg_data = global_df.groupby(['Product', 'Market'])['Sales'].sum().reset_index()
        fig = px.bar(agg_data, x="Product", y="Sales", color="Market", barmode="group",
                     title="Sales Performance by Product and Market")
        graph_html = pio.to_html(fig, full_html=False)
    else:
        graph_html = "<p>Required columns ('Product', 'Sales', 'Market') not found for visualization.</p>"

    # Render insights markdown to HTML
    insights_html = markdown.markdown(global_insights if global_insights else "No insights generated yet.")
    simulation_html = markdown.markdown(global_simulation_result if global_simulation_result else "Run a simulation below.")

    return render_template('dashboard.html', 
                           graph_html=graph_html, 
                           insights_html=insights_html,
                           simulation_html=simulation_html)


if __name__ == '__main__':
    # Ensure the static folders exist
    import os
    if not os.path.exists('static'): os.makedirs('static')
    if not os.path.exists('static/css'): os.makedirs('static/css')
    if not os.path.exists('static/js'): os.makedirs('static/js')
        
    app.run(debug=True)
