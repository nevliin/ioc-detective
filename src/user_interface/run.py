import json
import logging
import os
import pickle
import urllib.request
import uuid

from flask import Flask, redirect, url_for, render_template, request, flash, send_from_directory, send_file, jsonify, \
    session
from werkzeug.utils import secure_filename
from src import additional_actions
from src.ioc_extraction.indicator_utils import IndicatorCombinationMode
from src.ioc_extraction.ioc_extractor import IoCExtractor
from src.report_collection.report_collector import ReportCollector
from src.rule_generation.rule_generator import RuleGenerator
from src.text_mining.pdf_converter import PDFConverter
from src.text_mining.txt_converter import TXTConverter
from src.util import LogCollector

report_collector = ReportCollector()

app = Flask(__name__)

DOCUMENT_STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'documents')
SIGMA_STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sigma')
LOGS_STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'logs')
INDICATORGROUP_STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'indicator_groups')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config.json')


@app.route("/")
@app.route("/home")
def home():
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    return render_template("home.html", wiki_link=config['wiki'])


ALLOWED_EXTENSIONS = {'txt', 'pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            file_uuid = str(uuid.uuid4())
            file_path = os.path.join(DOCUMENT_STORAGE_DIR, file_uuid)
            try:
                file.save(file_path)
                return process_report(file_uuid, file_path, filename)
            except Exception as e:
                print(e)
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
    elif request.method == 'GET':
        url = request.args.get('url')
        return render_template("upload.html", url=url)


@app.route('/generate-from-url', methods=['GET'])
def generate_from_url():
    url = request.args.get('url')

    file_uuid = str(uuid.uuid4())
    file_path = os.path.join(DOCUMENT_STORAGE_DIR, file_uuid)
    urllib.request.urlretrieve(url, file_path)
    filename = url.split('/')[-1]
    return process_report(file_uuid, file_path, filename, mode="git_report")


def process_report(file_uuid, file_path, filename, mode="default"):
    if 'indicator_pattern' in request.cookies:
        indicator_filter = request.cookies['indicator_pattern'].split(',')
    else:
        indicator_filter = None

    name, file_extension = os.path.splitext(filename)
    log_collector = LogCollector()
    if file_extension.lower() == '.txt':
        converter = TXTConverter(log_collector=log_collector)
    if file_extension.lower() == '.pdf':
        converter = PDFConverter(log_collector=log_collector)
    try:
        document = converter.run(file_path, filename)
        ioc_extractor = IoCExtractor(mode=IndicatorCombinationMode.SECTION,
                                     log_collector=log_collector, pattern_filter=indicator_filter)
        indicator_groups = ioc_extractor.extract(document)

        log_collector.create_logs_for_indicators(indicator_groups)

        if len(indicator_groups) > 0:
            rule_generator = RuleGenerator(document_name=filename,
                                           save_path=os.path.join(SIGMA_STORAGE_DIR, file_uuid),
                                           log_collector=log_collector)
            rule_generator.generate(indicator_groups)
        else:
            log_collector.add('Rule Generation', 'No indicators found', logging.INFO)

        additional_actions.find_rule_links(log_collector, document)

        os.remove(file_path)
        # logs = log_collector.render_logs()
        # indicator_logs = log_collector.get_indicator_logs_by_group()
        with open(os.path.join(LOGS_STORAGE_DIR, file_uuid), 'wb') as f:
            pickle.dump(log_collector, f)
        with open(os.path.join(INDICATORGROUP_STORAGE_DIR, file_uuid), 'wb') as f:
            pickle.dump(indicator_groups, f)
        if mode == "git_report":
            return redirect(url_for("download_page", file_uuid=file_uuid, report_name=filename))
        elif mode == "default":
            return jsonify(file_uuid=file_uuid, report_name=filename)
    except Exception as e:
        excp_str = f"[{e.__class__.__name__}] {str(e)}"
        if mode == "git_report":
            session["exception"] = excp_str
            return redirect(url_for("exception"))
        elif mode == "default":
            return jsonify(exception=excp_str)


@app.route('/exception', methods=['GET'])
def exception():
    if 'exception' in session:
        exception_str = session['exception']
    else:
        exception_str = 'No exception found'
    return render_template('exception.html', exception=exception_str)


@app.route('/download-file', methods=['GET'])
def download_file():
    file_uuid = request.args.get('file_uuid')
    report_name = request.args.get('report_name')
    file_uuid = secure_filename(file_uuid)
    if os.path.exists(os.path.join(SIGMA_STORAGE_DIR, file_uuid)):
        return send_file(os.path.join(SIGMA_STORAGE_DIR, file_uuid),
                         mimetype='text/yaml',
                         attachment_filename=f"{report_name}.yaml",
                         as_attachment=True)
    else:
        return 'Not found', 404


@app.route("/report-check")
def git_check():
    """Check Github for new reports"""
    report_info = report_collector.get_reports()
    github_repos_configured = len(report_collector.repos) > 0
    return render_template("report_check.html", github_repos_configured=github_repos_configured, reports=report_info.reports, last_updated=report_info.last_checked)


@app.route("/download", methods=['GET'])
def download_page():
    file_uuid = request.args.get("file_uuid")
    report_name = request.args.get("report_name")
    log_collector = None
    with open(os.path.join(LOGS_STORAGE_DIR, file_uuid), 'rb') as f:
        log_collector = pickle.load(f)
    if log_collector is None:
        return "", 404
    indicator_logs = log_collector.get_indicator_logs_by_group()
    info_logs = log_collector.get_info_logs()
    return render_template("download.html", file_uuid=file_uuid, report_name=report_name, indicator_logs=indicator_logs,
                           info_logs=info_logs)


@app.route("/update-sigma", methods=['POST'])
def update_sigma():
    file_uuid = request.json["file_uuid"]
    ioc_uuids = request.json["ioc_uuids"]
    filename = request.json["filename"]

    with open(os.path.join(INDICATORGROUP_STORAGE_DIR, file_uuid), 'rb') as f:
        indicator_groups = pickle.load(f)

    for group in indicator_groups:
        for i in range(len(group)-1, -1, -1):
            if group.indicators[i].uuid not in ioc_uuids:
                del group.indicators[i]

    for i in range(len(indicator_groups)-1, -1, -1):
        if len(indicator_groups[i].indicators) == 0:
            del indicator_groups[i]

    # Overwrite Sigma-Rule
    rule_generator = RuleGenerator(document_name=filename,
                                   save_path=os.path.join(SIGMA_STORAGE_DIR, file_uuid))
    rule_generator.generate(indicator_groups)

    # Return/Let the download happen
    return "", 200
