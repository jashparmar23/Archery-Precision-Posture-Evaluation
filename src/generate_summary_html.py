# generate_summary_html.py
import os
import pandas as pd
from jinja2 import Template

def generate_html_from_csv(csv_path="output/reports/summary.csv", output_html="output/reports/summary.html"):
    df = pd.read_csv(csv_path)

    template_str = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Archery Summary Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
            h1 { color: #333; }
            .good { background-color: #e7fbe7; }
            .warn { background-color: #fff3cd; }
        </style>
    </head>
    <body>
        <h1>Archery Video Analysis Summary</h1>
        <table>
            <thead>
                <tr>
                    {% for col in df.columns %}
                    <th>{{ col }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in df.itertuples() %}
                <tr class="{{ 'warn' if row.AnchorFlag == 'Drift Detected' else 'good' }}">
                    {% for value in row[1:] %}
                    <td>{{ value }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """

    template = Template(template_str)
    rendered = template.render(df=df)

    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(rendered)

    print(f"[✔] HTML summary saved to: {output_html}")

if __name__ == "__main__":
    generate_html_from_csv()