from flask import Flask, request, render_template_string, redirect, url_for
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Welcome</title>
        <style>
            body {
                background-color: #141414;
                color: #E5E5E5;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                text-align: center;
                flex-direction: column;
            }
            h1 {
                color: #E50914;
                font-size: 2.5em;
            }
            button {
                background-color: #E50914;
                color: #E5E5E5;
                border: none;
                padding: 15px 30px;
                font-size: 1.2em;
                cursor: pointer;
                border-radius: 5px;
                margin-top: 20px;
            }
            button:hover {
                background-color: #f40612;
            }
        </style>
    </head>
    <body>
        <h1>Hello, Welcome to the Dashboard Project</h1>
        <form action="{{ url_for('configure_dashboard') }}" method="get">
            <button type="submit">Go to Dashboard</button>
        </form>
    </body>
    </html>
    ''')

@app.route('/configure_dashboard', methods=['GET', 'POST'])
def configure_dashboard():
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            return "No file part", 400
        
        file = request.files['csv_file']
        
        # Check if the file is empty or has no filename
        if file.filename == '':
            return "No selected file", 400
        
        if file and file.filename.endswith('.csv'):
            try:
                filename = file.filename.strip()
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Load CSV into DataFrame
                df = pd.read_csv(filepath)
                
                # Extract column names for dropdowns
                columns = df.columns.tolist()
                
                return render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Configure Dashboard</title>
                    <style>
                        body {
                            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                            margin: 0;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            transition: background-color 0.3s, color 0.3s;
                        }
                        body.dark {
                            background-color: #141414;
                            color: #E5E5E5;
                        }
                        body.light {
                            background-color: #F0F0F0;
                            color: #141414;
                        }
                        .form-container {
                            background-color: #222;
                            padding: 20px;
                            border-radius: 10px;
                            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5);
                            width: 100%;
                            max-width: 350px;
                            transition: background-color 0.3s, color 0.3s;
                        }
                        .form-container.light {
                            background-color: #FFF;
                            box-shadow: 0px 0px 10px rgba(200, 200, 200, 0.5);
                        }
                        h1 {
                            text-align: center;
                            margin-bottom: 20px;
                        }
                        h1.dark {
                            color: #E50914;
                        }
                        h1.light {
                            color: #141414;
                        }
                        label, select, input {
                            display: block;
                            margin: 10px 0;
                            font-size: 16px;
                            width: 100%;
                        }
                        select, input[type="file"], input[type="text"], input[type="submit"] {
                            padding: 8px;
                            background-color: #333;
                            border: 1px solid #555;
                            color: #E5E5E5;
                            border-radius: 5px;
                            width: 100%;
                            box-sizing: border-box;
                            transition: background-color 0.3s, color 0.3s;
                        }
                        select.light, input[type="file"].light, input[type="text"].light, input[type="submit"].light {
                            background-color: #FFF;
                            border: 1px solid #CCC;
                            color: #141414;
                        }
                        input[type="submit"] {
                            background-color: #E50914;
                            border: none;
                            cursor: pointer;
                            margin-top: 20px;
                        }
                        input[type="submit"]:hover {
                            background-color: #f40612;
                        }
                        .theme-toggle {
                            position: absolute;
                            top: 20px;
                            right: 20px;
                            cursor: pointer;
                            font-size: 16px;
                            padding: 5px 10px;
                            border: none;
                            background-color: transparent;
                            color: inherit;
                        }
                    </style>
                </head>
                <body class="dark">
                    <button class="theme-toggle" onclick="toggleTheme()">Switch to Light Theme</button>
                    <div class="form-container dark">
                        <h1 class="dark">Configure Dashboard</h1>
                        <form method="POST" action="{{ url_for('generate_chart') }}">
                            <label for="chart_type">Select Chart Type:</label>
                            <select id="chart_type" name="chart_type" required class="dark">
                                <option value="pie">Pie Chart</option>
                                <option value="bar">Bar Chart</option>
                                <option value="scatter">Scatter Plot</option>
                            </select>

                            <label for="x_column">Select X Column:</label>
                            <select id="x_column" name="x_column" required class="dark">
                                {% for column in columns %}
                                    <option value="{{ column }}">{{ column }}</option>
                                {% endfor %}
                            </select>

                            <label for="y_column">Select Y Column (optional for Pie Chart):</label>
                            <select id="y_column" name="y_column" class="dark">
                                {% for column in columns %}
                                    <option value="{{ column }}">{{ column }}</option>
                                {% endfor %}
                            </select>
                            
                            <input type="hidden" name="csv_file_path" value="{{ filepath }}">
                            <input type="submit" value="Generate Chart" class="dark">
                        </form>
                    </div>
                    <script>
                        function toggleTheme() {
                            const body = document.body;
                            const themeToggle = document.querySelector('.theme-toggle');
                            const formContainer = document.querySelector('.form-container');
                            const selectElements = document.querySelectorAll('select, input[type="file"], input[type="text"], input[type="submit"]');
                            const isDark = body.classList.toggle('dark');
                            body.classList.toggle('light', !isDark);
                            themeToggle.textContent = isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme';
                            formContainer.classList.toggle('dark', isDark);
                            formContainer.classList.toggle('light', !isDark);
                            selectElements.forEach(el => {
                                el.classList.toggle('dark', isDark);
                                el.classList.toggle('light', !isDark);
                            });
                        }
                    </script>
                </body>
                </html>
                ''', columns=columns, filepath=filepath)
            except Exception as e:
                return f"An error occurred while processing the file: {e}", 500
        else:
            return f"Invalid file type. Please upload a CSV file. Received file: {file.filename}", 400
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Configure Dashboard</title>
        <style>
            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                transition: background-color 0.3s, color 0.3s;
            }
            body.dark {
                background-color: #141414;
                color: #E5E5E5;
            }
            body.light {
                background-color: #F0F0F0;
                color: #141414;
            }
            .form-container {
                background-color: #222;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5);
                width: 100%;
                max-width: 350px;
                transition: background-color 0.3s, color 0.3s;
            }
            .form-container.light {
                background-color: #FFF;
                box-shadow: 0px 0px 10px rgba(200, 200, 200, 0.5);
            }
            h1 {
                text-align: center;
                margin-bottom: 20px;
            }
            h1.dark {
                color: #E50914;
            }
            h1.light {
                color: #141414;
            }
            label, select, input {
                display: block;
                margin: 10px 0;
                font-size: 16px;
                width: 100%;
            }
            select, input[type="file"], input[type="text"], input[type="submit"] {
                padding: 8px;
                background-color: #333;
                border: 1px solid #555;
                color: #E5E5E5;
                border-radius: 5px;
                width: 100%;
                box-sizing: border-box;
                transition: background-color 0.3s, color 0.3s;
            }
            select.light, input[type="file"].light, input[type="text"].light, input[type="submit"].light {
                background-color: #FFF;
                border: 1px solid #CCC;
                color: #141414;
            }
            input[type="submit"] {
                background-color: #E50914;
                border: none;
                cursor: pointer;
                margin-top: 20px;
            }
            input[type="submit"]:hover {
                background-color: #f40612;
            }
            .theme-toggle {
                position: absolute;
                top: 20px;
                right: 20px;
                cursor: pointer;
                font-size: 16px;
                padding: 5px 10px;
                border: none;
                background-color: transparent;
                color: inherit;
            }
        </style>
    </head>
    <body class="dark">
        <button class="theme-toggle" onclick="toggleTheme()">Switch to Light Theme</button>
        <div class="form-container dark">
            <h1 class="dark">Configure Dashboard</h1>
            <form method="POST" enctype="multipart/form-data">
                <label for="csv_file">Select CSV file:</label>
                <input type="file" id="csv_file" name="csv_file" accept=".csv" required class="dark">
                <input type="submit" value="Upload and Configure" class="dark">
            </form>
        </div>
        <script>
            function toggleTheme() {
                const body = document.body;
                const themeToggle = document.querySelector('.theme-toggle');
                const formContainer = document.querySelector('.form-container');
                const selectElements = document.querySelectorAll('select, input[type="file"], input[type="text"], input[type="submit"]');
                const isDark = body.classList.toggle('dark');
                body.classList.toggle('light', !isDark);
                themeToggle.textContent = isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme';
                formContainer.classList.toggle('dark', isDark);
                formContainer.classList.toggle('light', !isDark);
                selectElements.forEach(el => {
                    el.classList.toggle('dark', isDark);
                    el.classList.toggle('light', !isDark);
                });
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    try:
        chart_type = request.form['chart_type']
        x_column = request.form.get('x_column')
        y_column = request.form.get('y_column')
        csv_file_path = request.form['csv_file_path']

        if not csv_file_path or not os.path.exists(csv_file_path):
            return "CSV file path is invalid or file does not exist.", 400

        df = pd.read_csv(csv_file_path)

        if chart_type == 'pie':
            fig = px.pie(df, names=x_column)
        elif chart_type == 'bar':
            fig = px.bar(df, x=x_column, y=y_column)
        elif chart_type == 'scatter':
            fig = px.scatter(df, x=x_column, y=y_column)
        else:
            raise ValueError("Invalid chart type")

        chart_html = pio.to_html(fig, full_html=False)

        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Generated Chart</title>
            <style>
                body {
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    margin: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #F0F0F0;
                    color: #141414;
                    flex-direction: column;
                    transition: background-color 0.3s, color 0.3s;
                }
                body.dark {
                    background-color: #141414;
                    color: #E5E5E5;
                }
                body.light {
                    background-color: #F0F0F0;
                    color: #141414;
                }
                .chart-container {
                    width: 90%;
                    max-width: 1200px;
                }
                .theme-toggle {
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    cursor: pointer;
                    font-size: 16px;
                    padding: 5px 10px;
                    border: none;
                    background-color: transparent;
                    color: inherit;
                }
            </style>
        </head>
        <body class="dark">
            <button class="theme-toggle" onclick="toggleTheme()">Switch to Light Theme</button>
            <div class="chart-container">{{ chart_html|safe }}</div>
            <script>
                function toggleTheme() {
                    document.body.classList.toggle('dark');
                    document.body.classList.toggle('light');
                    document.querySelector('.theme-toggle').textContent = document.body.classList.contains('dark') ? 'Switch to Light Theme' : 'Switch to Dark Theme';
                }
            </script>
        </body>
        </html>
        ''', chart_html=chart_html)
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
