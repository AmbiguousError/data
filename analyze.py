import pandas as pd
import sys
import time

def analyze_data(filepath):
    """
    Performs EDA on the given data file and returns the results.
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

    return summary, corr_matrix.to_dict(), list(suggestions)

def generate_html(summary, corr_matrix, suggestions):
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
    </body>
    </html>
    """

    summary_table = create_html_table(summary)
    corr_table = create_html_table(corr_matrix, highlight_corr=True)
    suggestions_list = "".join(f"<li>{s}</li>" for s in suggestions)

    return html.format(
        summary_table=summary_table,
        corr_table=corr_table,
        suggestions_list=suggestions_list
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
    if len(sys.argv) != 3:
        print("Usage: python analyze.py <input_filepath> <output_filepath>")
        sys.exit(1)

    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    print("Starting analysis...")
    time.sleep(1) # Simulate work

    summary, corr_matrix, suggestions = analyze_data(input_filepath)

    print("Generating HTML report...")
    time.sleep(1) # Simulate work

    html = generate_html(summary, corr_matrix, suggestions)
    with open(output_filepath, 'w') as f:
        f.write(html)

    print("Analysis complete.")
    time.sleep(1) # Simulate work
