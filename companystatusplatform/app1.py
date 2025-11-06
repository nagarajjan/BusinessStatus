# app.py
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd
import plotly.express as px
import plotly.io as pio
import io
import markdown 
import os 
import requests 
from bs4 import BeautifulSoup 

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

# --- Global Variables ---
global_df = None
global_insights = None
global_simulation_result = None
# Changed to lists to store multiple results
global_scraped_product_data = [] 
global_scraped_competitors_data = None 

# --- Helper Functions (Placeholders) ---
def scrape_everything(name, cik): 
    print(f"Scraping data for {name} ({cik})...")
    return "Scraped data placeholder text."

def generate_insights(df, data): 
    print("Generating insights...")
    return "**Summary of Findings:**\n* Sales look good.\n* South market is competitive."

def run_simulation(df, scenario): 
    print(f"Running simulation for: {scenario}")
    return f"**Scenario Simulated:** *{scenario}*\n\n**Result:** Simulation predicts 5% increase in North sales."

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
# --- End Helper Functions ---


# --- Integrated Scraper Functions (WORKING SAMPLE CODE) ---

def scrape_product_info(url):
    """Scrapes a single product page from http://books.toscrape.com/ for basic info."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_element = soup.find('h1') 
        price_element = soup.find('p', class_='price_color')
        
        title = title_element.text.strip() if title_element else 'N/A'
        price = price_element.text.strip() if price_element else 'N/A'
        
        return {'URL': url, 'Title': title, 'Price': price, 'Status': 'Success'}
    except requests.exceptions.RequestException as e:
        return {'URL': url, 'Title': 'Error', 'Price': 'Error', 'Status': f'Failed: {e}'}


def scrape_competitors_list(url):
    """Scrapes a category listing page from http://books.toscrape.com/ for multiple items."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        competitors = []
        for item in soup.find_all('article', class_='product_pod'):
            title = item.h3.a['title'] if item.h3 and item.h3.a else 'N/A'
            price = item.find('p', class_='price_color').text.strip() if item.find('p', class_='price_color') else 'N/A'
            
            competitors.append({'Name': title, 'Price': price})
            
        return competitors if competitors else [{'Name': 'N/A', 'Price': 'N/A', 'Status': 'No matching elements found'}]
    except requests.exceptions.RequestException as e:
        return [{'Name': 'Error', 'Price': f'Failed: {e}', 'Status': 'Request Failed'}]

# --- End Scraper Functions ---


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
    global global_df, global_insights
    global_insights = None 
    file = request.files.get('file')
    company_name = request.form.get('company_name', 'Default Company')
    company_cik = request.form.get('company_cik', '00000000')
    if not file or file.filename == '':
        flash("No file selected.", "error")
        return redirect(url_for('upload_file_page'))
    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        try:
            global_df = pd.read_excel(file)
            global_scraped_data_text = "" # Placeholder
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Error processing file: {e}", "error")
            return redirect(url_for('upload_file_page'))
    flash("Invalid file format.", "error")
    return redirect(url_for('upload_file_page'))


@app.route('/scrape_product', methods=['POST'])
def scrape_product_route():
    # Fix: Added def for the function and corrected global access
    global global_scraped_product_data
    url = request.form.get('product_url')
    if url:
        result = scrape_product_info(url)
        global_scraped_product_data.append(result) # Append to list
        flash(f"Scraped product information from {url}", "success")
    else:
        flash("Please provide a valid URL.", "error")
    return redirect(url_for('dashboard'))


@app.route('/scrape_competitors', methods=['POST'])
def scrape_competitors_route():
    global global_scraped_competitors_data
    url = request.form.get('competitors_url')
    if url:
        global_scraped_competitors_data = scrape_competitors_list(url)
        flash(f"Scraped competitors from {url}", "success")
    else:
        flash("Please provide a valid URL.", "error")
    return redirect(url_for('dashboard'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global global_df, global_insights, global_simulation_result, global_scraped_product_data, global_scraped_competitors_data

    if global_df is None or global_df.empty:
        return redirect(url_for('upload_file_page'))
    
    # Handle simulation request POST request
    if request.method == 'POST' and 'scenario_text' in request.form:
        scenario = request.form['scenario_text']
        # global_simulation_result = "Simulation results placeholder."
        global_simulation_result = run_simulation(global_df, scenario)
        # Add a flash message to confirm it ran
        flash("Simulation run successfully!", "success")
        # Note: If you don't redirect here, the POST data is processed. 
        # The subsequent GET will use the newly updated global variable.
    
    # ... (Generate Plotly Chart logic) ...

    # Render insights markdown to HTML
    insights_html = markdown.markdown(global_insights if global_insights else "No insights generated yet.")
    # This line processes the *current* value of global_simulation_result
    simulation_html = markdown.markdown(global_simulation_result if global_simulation_result else "Run a simulation below.")

    return render_template('dashboard1.html', 
                           graph_html=graph_html, 
                           insights_html=insights_html,
                           simulation_html=simulation_html)


        
        
    
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
    
    product_data = global_scraped_product_data
    competitors_data = global_scraped_competitors_data
    
    # Fix: Corrected the template name back to dashboard.html
    return render_template('dashboard1.html', 
                           graph_html=graph_html, 
                           insights_html=insights_html,
                           simulation_html=simulation_html,
                           product_data=product_data,
                           competitors_data=competitors_data)


@app.route('/download_excel_report')
def download_excel_report():
    global global_df, global_insights, global_simulation_result, global_scraped_competitors_data, global_scraped_product_data
    if global_df is None or global_df.empty: return redirect(url_for('upload_file_page'))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        global_df.to_excel(writer, sheet_name='Raw Data', index=False)
        insights_data = {'Section': ['AI Insights', 'Simulation Results'], 'Content': [global_insights if global_insights else 'N/A', global_simulation_result if global_simulation_result else 'N/A']}
        insights_df = pd.DataFrame(insights_data)
        insights_df.to_excel(writer, sheet_name='Summary', index=False)
        if global_scraped_competitors_data:
            comp_df = pd.DataFrame(global_scraped_competitors_data)
            comp_df.to_excel(writer, sheet_name='Competitors', index=False)
        # Add the multi-product data to a sheet
        if global_scraped_product_data:
            prod_df = pd.DataFrame(global_scraped_product_data)
            prod_df.to_excel(writer, sheet_name='Scraped Products', index=False)

    buffer.seek(0)
    # Fix: Added the closing return statement
    return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='company_status_report.xlsx')

@app.route('/download_report')
def download_report():
    return "Functionality available in previous app.py versions if needed."

if __name__ == '__main__':
    if not os.path.exists('static'): os.makedirs('static')
    if not os.path.exists('static/css'): os.makedirs('static/css')
    if not os.path.exists('static/js'): os.makedirs('static/js')
    app.run(debug=True)
