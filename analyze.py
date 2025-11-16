import pandas as pd
import sys
import time
import argparse
import base64
from io import BytesIO
import matplotlib.pyplot as plt

def analyze_data(filepath, target_column=None):
    """
    Performs EDA and optional AutoML on the given data file.
    """
    print("Reading data...")
    time.sleep(1) # Simulate work
    df = pd.read_csv(filepath, header=None, delim_whitespace=True)

    print("Cleaning data...")
    time.sleep(1) # Simulate work
    for col in df.select_dtypes(include=['number']).columns:
        df[col].fillna(df[col].mean(), inplace=True)
    for col in df.select_dtypes(include=['object']).columns:
        df[col].fillna(df[col].mode()[0], inplace=True)

    print("Calculating summary statistics...")
    time.sleep(1) # Simulate work
    summary = df.describe().to_dict()
    skewness = df.skew(numeric_only=True).to_dict()
    kurtosis = df.kurtosis(numeric_only=True).to_dict()
    for col in summary:
        if col in skewness:
            summary[col]['skew'] = skewness[col]
        if col in kurtosis:
            summary[col]['kurtosis'] = kurtosis[col]

    print("Calculating correlations...")
    time.sleep(1) # Simulate work
    corr_matrix = df.corr(numeric_only=True)
    corr_matrix.fillna(0, inplace=True) # Replace NaN with 0 for HTML generation

    print("Generating suggestions...")
    time.sleep(1) # Simulate work
    suggestions = set() # Use a set to avoid duplicate suggestions
    for col, stats in summary.items():
        if stats.get('skew', 0) > 1:
            suggestions.add(f'Column {col} is highly skewed. Consider a log transformation.')
        if stats.get('kurtosis', 0) > 3:
            suggestions.add(f'Column {col} has high kurtosis, indicating potential outliers.')

    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            if abs(corr_matrix.iloc[i, j]) > 0.8:
                suggestions.add(f'High correlation between {col1} and {col2}. Consider removing one.')

    automl_results = {}
    if target_column:
        print(f"Starting AutoML for target: {target_column}...")

        # Check if target_column is an integer (index)
        try:
            target_column = int(target_column)
            if target_column < 0 or target_column >= len(df.columns):
                 raise ValueError("Target column index is out of bounds.")
            target_column = df.columns[target_column]
        except ValueError:
            if target_column not in df.columns:
                 raise ValueError(f"Target column '{target_column}' not found in the dataset.")

        # Dynamically determine problem type
        if pd.api.types.is_numeric_dtype(df[target_column]) and df[target_column].nunique() > 20:
             from pycaret.regression import setup, compare_models, pull, plot_model, save_model
             exp = setup(data=df, target=target_column, session_id=123, verbose=False)
        else:
             from pycaret.classification import setup, compare_models, pull, plot_model, save_model
             exp = setup(data=df, target=target_column, session_id=123, verbose=False)

        best_model = compare_models()

        automl_results['performance_grid'] = pull().to_html()

        # Generate and save plots as base64 strings
        plot_names = ['feature', 'summary']
        for plot_name in plot_names:
            try:
                plot_model(best_model, plot=plot_name, save=True)
                with open(f'{plot_name}.png', "rb") as f:
                    automl_results[f'{plot_name}_plot'] = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"Could not generate plot '{plot_name}': {e}")
                automl_results[f'{plot_name}_plot'] = None

    return summary, corr_matrix.to_dict(), list(suggestions), automl_results

def generate_html(summary, corr_matrix, suggestions, automl_results=None):
    """
    Generates a self-contained HTML report from the analysis results.
    """

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Analysis Report</title>
        <style>
            body {{ font-family: sans-serif; }}
            h1, h2 {{ border-bottom: 2px solid #333; padding-bottom: 0.5rem; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .high-corr {{ background-color: #ffcccc; }}
            .med-corr {{ background-color: #ffffcc; }}
        </style>
    </head>
    <body>
        <h1>Data Analysis Report</h1>

        <h2>Summary Statistics</h2>
        {summary_table}

        <h2>Correlation Matrix</h2>
        {corr_table}

        <h2>Suggestions</h2>
        <ul>
            {suggestions_list}
        </ul>

        {automl_section}
    </body>
    </html>
    """

    summary_table = create_html_table(summary)
    corr_table = create_html_table(corr_matrix, highlight_corr=True)
    suggestions_list = "".join(f"<li>{s}</li>" for s in suggestions)
    automl_section = ""

    if automl_results:
        automl_section += "<h2>AutoML Report</h2>"
        automl_section += "<h3>Model Performance</h3>"
        automl_section += automl_results.get('performance_grid', '<p>No performance data available.</p>')

        if automl_results.get('feature_plot'):
            automl_section += "<h3>Feature Importance</h3>"
            automl_section += f"<img src='data:image/png;base64,{automl_results['feature_plot']}'/>"

        if automl_results.get('summary_plot'):
            automl_section += "<h3>SHAP Summary Plot</h3>"
            automl_section += f"<img src='data:image/png;base64,{automl_results['summary_plot']}'/>"

    return html.format(
        summary_table=summary_table,
        corr_table=corr_table,
        suggestions_list=suggestions_list,
        automl_section=automl_section
    )

def create_html_table(data, highlight_corr=False):
    """
    Creates an HTML table from a dictionary of dictionaries.
    """
    headers = list(data.keys())
    if not headers:
        return "<p>No data to display.</p>"

    first_col_keys = list(data[headers[0]].keys())

    table = '<table>'
    table += '<tr><th></th>'
    for header in headers:
        table += f'<th>{header}</th>'
    table += '</tr>'

    for row_name in first_col_keys:
        table += '<tr>'
        table += f'<td><strong>{row_name}</strong></td>'
        for header in headers:
            value = data[header].get(row_name, 'N/A')
            className = ''
            if highlight_corr and isinstance(value, (int, float)):
                if abs(value) > 0.8 and abs(value) < 1:
                    className = 'high-corr'
                elif abs(value) > 0.5 and abs(value) < 1:
                    className = 'med-corr'
            table += f'<td class="{className}">{value:.4f}</td>' if isinstance(value, float) else f'<td>{value}</td>'
        table += '</tr>'

    table += '</table>'
    return table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform data analysis and AutoML.')
    parser.add_argument('input_filepath', type=str, help='Path to the input data file.')
    parser.add_argument('output_filepath', type=str, help='Path to the output report file.')
    parser.add_argument('--target', type=str, help='Name of the target column for AutoML.')
    args = parser.parse_args()

    try:
        print("Starting analysis...")
        time.sleep(1) # Simulate work

        summary, corr_matrix, suggestions, automl_results = analyze_data(args.input_filepath, args.target)

        print("Generating HTML report...")
        time.sleep(1) # Simulate work

        html = generate_html(summary, corr_matrix, suggestions, automl_results)
        with open(args.output_filepath, 'w') as f:
            f.write(html)

        print("Analysis complete.")
        time.sleep(1) # Simulate work
    except Exception as e:
        import traceback
        print("--- SCRIPT FAILED ---")
        print(traceback.format_exc())
        sys.exit(1)
