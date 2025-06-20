import os
import subprocess
from flask import Flask, request, redirect, url_for, render_template, flash, send_from_directory, session
from werkzeug.utils import secure_filename
from google import genai
from markdown import markdown
from datetime import datetime

app = Flask(__name__)

# Configurazione delle cartelle
UPLOAD_FOLDER = 'uploads'
ZEEK_LOGS_FOLDER = 'zeek_logs'
ALLOWED_EXTENSIONS = {'pcap', 'pcapng'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ZEEK_LOGS_FOLDER'] = ZEEK_LOGS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'supersecretkey'

# Configurazione Gemini
GEMINI_API_KEY = "INSERT YOUR GOOGLE API KEY HERE"
client = genai.Client(api_key=GEMINI_API_KEY)

MAX_ROWS_TO_DISPLAY = 1000
MAX_LOG_SIZE_FOR_ANALYSIS = 30000   # 30KB

# Context processor per aggiungere l'anno corrente e la modalità dark a tutti i template
@app.context_processor
def inject_global_vars():
    # MODIFICA QUI: dark_mode è sempre True
    return {
        'current_year': datetime.now().year,
        'dark_mode': True # La dark mode è ora predefinita e sempre attiva
    }

def clear_previous_data():
    print("DEBUG: Avvio pulizia dei dati precedenti...")
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print(f"DEBUG: Rimosso file PCAP: {file_path}")
        except Exception as e:
            print(f"ERRORE: Impossibile rimuovere {file_path}. Causa: {e}")
            flash(f"Errore durante la pulizia del file PCAP: {filename}")

    for filename in os.listdir(app.config['ZEEK_LOGS_FOLDER']):
        file_path = os.path.join(app.config['ZEEK_LOGS_FOLDER'], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print(f"DEBUG: Rimosso log Zeek: {file_path}")
        except Exception as e:
            print(f"ERRORE: Impossibile rimuovere {file_path}. Causa: {e}")
            flash(f"Errore durante la pulizia del log Zeek: {filename}")
    print("DEBUG: Pulizia dei dati completata.")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_zeek_log_columns(log_path):
    # print(f"DEBUG: Tentativo di estrarre colonne da: {log_path}")
    zeek_cut_path = "/usr/local/zeek/bin/zeek-cut"
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith("#fields"):
                    columns_raw = line[len("#fields"):].strip()
                    columns = [col for col in columns_raw.split() if col]
                    # print(f"DEBUG (dal file): Colonne parseggiate: {columns}")
                    return columns
                elif line.startswith("#close"):
                    break
        
        print(f"DEBUG: Riga #fields non trovata. Tentativo con '{zeek_cut_path} -F {log_path}'")
        result = subprocess.run(
            [zeek_cut_path, "-F", log_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        output_lines = result.stdout.strip().splitlines()
        
        if not output_lines:
            print(f"ERRORE: '{zeek_cut_path} -F' non ha prodotto output")
            return []
        
        for line in output_lines:
            if line.startswith("#fields"):
                columns_line = line.replace("#fields\t", "").strip()
                columns = columns_line.split('\t')
                print(f"DEBUG (da zeek-cut -F): Colonne parseggiate: {columns}")
                return columns
        
        print(f"ERRORE: Riga #fields non trovata")
        return []

    except subprocess.CalledProcessError as e:
        print(f"ERRORE: zeek-cut -F errore: {e.returncode}, StdErr: {e.stderr}")
        return []
    except FileNotFoundError:
        print(f"ERRORE: Comando zeek-cut non trovato")
        return []
    except Exception as e:
        print(f"ERRORE: Errore estrazione colonne: {e}")
        return []

def analyze_logs_with_gemini(log_text):
    try:
        prompt = f"""
## Istruzioni di Analisi
Analizza i seguenti log di rete generati da Zeek. Identifica attività sospette, potenziali minacce, anomalie o comportamenti insoliti.

**Formatta la risposta in Markdown con la seguente struttura:**
1. **Riepilogo Esecutivo**: Breve panoramica delle scoperte principali
2. **Analisi Dettagliata**: 
    - Suddivisa per categoria di minaccia/anomalia
    - Include evidenze dai log (IP, porte, comportamenti)
3. **Raccomandazioni**: Azioni concrete da intraprendere
4. **Indicatori di Compromissione (IoC)**: 
    - IP sospetti
    - Porte coinvolte
    - Pattern comportamentali
5. **Priorità**: Classifica delle minacce (Alta/Media/Bassa)

## Log da Analizzare
{log_text[:MAX_LOG_SIZE_FOR_ANALYSIS]}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [{"text": prompt}]}]
        )
        
        html_output = markdown(response.text)
        return html_output
    
    except Exception as e:
        return f"<div class='error'>Errore durante l'analisi con Gemini: {str(e)}</div>"


@app.route('/')
def index():
    uploaded_pcaps = [f for f in os.listdir(app.config['UPLOAD_FOLDER'])
                      if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    zeek_logs = [f for f in os.listdir(app.config['ZEEK_LOGS_FOLDER'])
                   if os.path.isfile(os.path.join(app.config['ZEEK_LOGS_FOLDER'], f))]
    
    return render_template(
        'index.html', 
        uploaded_pcaps=uploaded_pcaps, 
        zeek_logs=zeek_logs
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    clear_previous_data()
    if 'file' not in request.files:
        flash('Nessun file selezionato')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Nessun file selezionato')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash(f'File {filename} caricato con successo! Dati precedenti rimossi.')
        return redirect(url_for('index'))
    else:
        flash('Tipo di file non consentito. Solo .pcap e .pcapng')
        return redirect(url_for('index'))

@app.route('/process_pcap/<filename>', methods=['POST'])
def process_pcap(filename):
    pcap_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(pcap_path):
        flash(f'Il file {filename} non esiste.')
        return redirect(url_for('index'))

    os.makedirs(app.config['ZEEK_LOGS_FOLDER'], exist_ok=True)
    original_cwd = os.getcwd()
    os.chdir(app.config['ZEEK_LOGS_FOLDER'])

    try:
        flash(f'Avvio processamento Zeek per {filename}...')
        zeek_path = "/usr/local/zeek/bin/zeek"
        result = subprocess.run(
            [zeek_path, "-C", "-r", os.path.join(original_cwd, pcap_path)],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            flash(f'Processamento Zeek completato!')
        else:
            flash(f'Errore durante Zeek: {result.stderr}')
    finally:
        os.chdir(original_cwd)

    return redirect(url_for('index'))
@app.route('/view_log/<log_filename>', methods=['GET', 'POST'])
def view_log(log_filename):
    log_path = os.path.join(app.config['ZEEK_LOGS_FOLDER'], log_filename)
    if not os.path.exists(log_path):
        flash(f'Il file di log {log_filename} non esiste.')
        return redirect(url_for('index'))

    output_rows = []
    output_columns = []
    error = ""
    selected_columns = []

    all_available_columns = get_zeek_log_columns(log_path)
    
    if request.method == 'POST' and 'reset_filters' in request.form:
        selected_columns = []
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("#fields"):
                        output_columns = line.replace("#fields\t", "").strip().split('\t')
                        break
                data_lines_raw = [line.strip() for line in lines if not line.startswith("#") and line.strip()]
                for i, line_data in enumerate(data_lines_raw):
                    if i >= MAX_ROWS_TO_DISPLAY:
                        flash(f"Mostrate solo le prime {MAX_ROWS_TO_DISPLAY} righe.")
                        break
                    output_rows.append(line_data.split('\t'))
        except Exception as e:
            error = f"Impossibile leggere il file: {e}"
    
    elif request.method == 'POST':
        selected_columns = request.form.getlist('columns')
        
        if selected_columns:
            try:
                zeek_cut_path = "/usr/local/zeek/bin/zeek-cut"
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_file_stdin:
                    zeek_cut_command = [zeek_cut_path, "-m"] + selected_columns
                    print(f"command view: {zeek_cut_command}")
                    p1 = subprocess.Popen(
                        zeek_cut_command,
                        stdin=log_file_stdin,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    head_command = ["head", "-n", str(MAX_ROWS_TO_DISPLAY + 1)]
                    p2 = subprocess.Popen(
                        head_command,
                        stdin=p1.stdout,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    p1.stdout.close()
                    output_raw, stderr_p2 = p2.communicate()
                    zeek_cut_stderr = p1.communicate()[1]
                
                if output_raw:
                    lines = output_raw.strip().splitlines()
                    if lines:
                        output_columns = lines[0].split('\t')
                        data_lines = lines[1:]
                        for line in data_lines:
                            if line.strip():
                                output_rows.append(line.split('\t'))
                        if len(output_rows) >= MAX_ROWS_TO_DISPLAY:
                            flash(f"Mostrate solo le prime {MAX_ROWS_TO_DISPLAY} righe.")
                else:
                    flash("Nessun output da zeek-cut.")

            except subprocess.CalledProcessError as e:
                error = f"Errore zeek-cut: {e.stderr}"
            except FileNotFoundError:
                error = "Comando zeek-cut non trovato."
            except Exception as e:
                error = f"Errore generico: {e}"
        else:
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith("#fields"):
                            output_columns = line.replace("#fields\t", "").strip().split('\t')
                            break
                    data_lines_raw = [line.strip() for line in lines if not line.startswith("#") and line.strip()]
                    for i, line_data in enumerate(data_lines_raw):
                        if i >= MAX_ROWS_TO_DISPLAY:
                            flash(f"Mostrate solo le prime {MAX_ROWS_TO_DISPLAY} righe.")
                            break
                        output_rows.append(line_data.split('\t'))
            except Exception as e:
                error = f"Impossibile leggere il file: {e}"
    else:
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("#fields"):
                        output_columns = line.replace("#fields\t", "").strip().split('\t')
                        break
                data_lines_raw = [line.strip() for line in lines if not line.startswith("#") and line.strip()]
                for i, line_data in enumerate(data_lines_raw):
                    if i >= MAX_ROWS_TO_DISPLAY:
                        flash(f"Mostrate solo le prime {MAX_ROWS_TO_DISPLAY} righe.")
                        break
                    output_rows.append(line_data.split('\t'))
        except Exception as e:
            error = f"Impossibile leggere il file: {e}"
            
    return render_template(
        'view_log.html',
        log_filename=log_filename,
        output_rows=output_rows,
        output_columns=output_columns,
        error=error,
        all_available_columns=all_available_columns,
        selected_columns=selected_columns
    )

@app.route('/download_log/<log_filename>')
def download_log(log_filename):
    log_path = os.path.join(app.config['ZEEK_LOGS_FOLDER'], log_filename)
    if os.path.exists(log_path):
        return send_from_directory(
            app.config['ZEEK_LOGS_FOLDER'],
            log_filename,
            as_attachment=True
        )
    else:
        flash(f"File {log_filename} non trovato.")
        return redirect(url_for('index'))

@app.route('/analyze_all_logs', methods=['POST'])
def analyze_all_logs():
    try:
        all_logs_text = ""
        for log_file in os.listdir(app.config['ZEEK_LOGS_FOLDER']):
            log_path = os.path.join(app.config['ZEEK_LOGS_FOLDER'], log_file)
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_logs_text += f"\n\n===== {log_file} =====\n"
                all_logs_text += f.read(MAX_LOG_SIZE_FOR_ANALYSIS // 5)   # Limita ogni file a ~6KB
        
        analysis_result_html = analyze_logs_with_gemini(all_logs_text)
        return render_template('analysis_result.html', analysis_result=analysis_result_html)
    except Exception as e:
        return f"Errore durante l'analisi: {str(e)}"

@app.route('/analyze_filtered_logs/<log_filename>', methods=['POST'])
def analyze_filtered_logs(log_filename):
    try:
        log_path = os.path.join(app.config['ZEEK_LOGS_FOLDER'], log_filename)
        if not os.path.exists(log_path):
            flash(f'Il file di log {log_filename} non esiste.')
            return redirect(url_for('index'))

        output_rows = []
        output_columns = []
        error = ""
        selected_columns = []

        all_available_columns = get_zeek_log_columns(log_path)
        if request.method == 'POST':
            selected_columns = request.form.getlist('columns')
            if selected_columns:

                try:
                    zeek_cut_path = "/usr/local/zeek/bin/zeek-cut"
                    sel=selected_columns[0].replace('[',"").replace(']',"").replace("'","").replace(",","")
                    fields = ["-m"]
                    for i in sel.split(" "):
                        fields.append(i)
                    
                    cmd = ["/usr/local/zeek/bin/zeek-cut"] + fields

                    with open(log_path, "rb") as infile:
                        process = subprocess.Popen(
                            cmd,
                            stdin=infile,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        output, stderr = process.communicate()
                        output_raw=output.decode()


                    # print(f"oraw: {output_raw}")
                 
                except Exception as e:
                    error = f"Errore generico: {e}"
  


        

        analysis_result_html = analyze_logs_with_gemini(output_raw)
        return render_template('analysis_result.html', analysis_result=analysis_result_html)
    except Exception as e:
        return f"Errore durante l'analisi filtrata: {str(e)}"

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(ZEEK_LOGS_FOLDER, exist_ok=True)
    app.run(debug=True,host="0.0.0.0",port=5000)
