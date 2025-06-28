from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
# from flask_executor import Executor
import re
import sqlite3
import io

from Evaluator import Evaluator

app = Flask(__name__)

USERNAME = 'test'
PASSWORD = 'test'
dbname = 'TEST.db'

@app.route('/')
def index():
    jobs = get_job_list()
    return render_template("user_index.html", jobs=jobs)

@app.route('/application/<int:job_id>', methods=['GET'])
def application(job_id):
    select_ls = ['titel', 'job_overview', 'degree']
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute(f"SELECT {', '.join(select_ls)} FROM jobs WHERE job_id='{job_id}'")
    datas = cur.fetchall()
    conn.close()
    job_datas = dict()
    for i,data in enumerate(datas[0]):
        if isinstance(data ,(bytes, bytearray)):
            continue
        job_datas[select_ls[i]] = data
    return render_template('job_application.html', job_datas=job_datas, job_id=job_id)

@app.route('/resept_user_info/<int:job_id>', methods=['POST'])
def resept_user_info(job_id):
    pdfs = request.files.to_dict()
    text_data = request.form.to_dict()
    pdfs = {k:sqlite3.Binary(pdfs[k].read()) for k in pdfs.keys()}
    model_names, model_texts = _get_model_text(job_id)
    Ever = Evaluator(model_names=model_names, model_texts=model_texts)
    eval_texts = [text_data[f"abstract{i}"] for i in range(1, 4)]
    eval_texts.append(text_data[f"appeal"])
    # evel
    points_ls, total_point = Ever.fit(evaluate_texts=eval_texts)

    points = {f'job_abst{i+1}_score': poi for i, poi in enumerate(points_ls[1:])}
    points["job_appeal_score"] = points_ls[0]

    datas = {'job_id':job_id, 'total_score':total_point, **text_data, **pdfs, **points}
    _add_user(datas)
    return redirect("/")

def _get_model_text(job_id):
    select = ["job_overview"]
    select.extend([f'abstract{i}' for i in range(1, 5)])
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    q = ", ".join(select)
    cur.execute(f"SELECT {q} name FROM jobs WHERE job_id='{job_id}'")
    datas = cur.fetchall()
    conn.close()
    return select, list(datas[0])

def _add_user(datas):
    labels = ["job_id", 'name', 'appeal', 'degree', 'email',\
            'telephone', 'resume', 'abstract1_titel', \
            'abstract1', 'abstract2_titel', 'abstract2', 'abstract3_titel', 'abstract3',\
            'job_abst1_score', 'job_abst2_score', 'job_abst3_score', 'job_abst4_score', 'job_appeal_score', 'total_score']
    ph = ", ".join(["?" for _ in labels])
    user_info_strs = ", ".join(labels)
    data_list = [datas[lab] for lab in labels]
    q = "INSERT INTO users ({0}) VALUES ({1})".format(user_info_strs, ph)
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute(q, data_list)
    conn.commit()
    conn.close()

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        user = request.form["user"]
        pasd = request.form["pasd"]
        if user == USERNAME and pasd == PASSWORD:
            jobs = get_job_list()
            return render_template('job_index.html', jobs=jobs)
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")


def get_job_list():
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute('SELECT job_id, titel FROM jobs')
    titles = cur.fetchall() 
    conn.close()
    return titles

@app.route('/job_info_manage/<int:job_id>', methods=['POST'])
def job_info_manage(job_id):
    labels = ['titel', 'job_overview', 'degree', 'abstract1_titel',  'abstract1', 'abstract2_titel', 'abstract2', \
              'abstract3_titel', 'abstract3', 'abstract4_titel', 'abstract4']
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    select_str = ", ".join(labels)
    cur.execute(f"SELECT {select_str} FROM jobs WHERE job_id='{job_id}'")
    datas = cur.fetchall()
    conn.close()
    job_datas = dict()
    for i,data in enumerate(datas[0]):
        job_datas[labels[i]] = data
    return render_template('job_registration.html', job_datas=job_datas, job_id=job_id)

@app.route("/applicant_index/<int:job_id>", methods=["POST"])
def applicant_index(job_id):
    users = get_users_id(job_id)
    return render_template('applicant_index.html', users=users)

@app.route("/applicants/<int:user_id>", methods=["POST"])
def applicants(user_id):
    labels = ["job_id", 'name', 'appeal', 'degree', 'email', 'telephone', 'resume',\
               'abstract1_titel',  'abstract1', 'abstract2_titel',  'abstract2','abstract3_titel', 'abstract3',\
                'job_abst1_score', 'job_abst2_score', 'job_abst3_score', 'job_abst4_score', 'job_appeal_score', 'total_score']
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    select_str = ", ".join(labels)
    cur.execute(f"SELECT {select_str} FROM users WHERE user_id='{user_id}'")
    datas = cur.fetchall()
    conn.close()
    pdfs = dict()
    user_datas = dict()
    print(len(datas[0]), len(labels))
    for i,data in enumerate(datas[0]):
        if isinstance(data ,(bytes, bytearray)):
            pdfs[labels[i]] = data
            continue
        user_datas[labels[i]] = data
    # print(pdfs["job_abst1_score"])
    return render_template('applicant.html', user_datas=user_datas, user_id=user_id)



@app.route('/download_blob/<string:tabel_name>/<int:id>/<string:pdf_key>', methods=['POST'])
def download_blob(tabel_name, id, pdf_key):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    if tabel_name == "jobs":
        q = "SELECT {0} FROM {1} WHERE job_id={2}".format(pdf_key, tabel_name, id)
        cur.execute(q)
    elif tabel_name == "users":
        q = "SELECT {0} FROM {1} WHERE user_id={2}".format(pdf_key, tabel_name, id)
        cur.execute(q)
    else:
        conn.close()
        return
    data = cur.fetchall()
    conn.close()
    pdf = data[0][0]
    return send_file(io.BytesIO(pdf), mimetype='application/pdf', as_attachment=True,  download_name=f"{pdf_key}_id{id}.pdf")


@app.route("/add_job", methods=['POST'])
def add_job():
    return render_template('add_job.html')

@app.route("/add_db_job", methods=["POST"])
def add_db_job():
    labels = ["titel", 'job_overview', 'degree', 'abstract1_titel', 'abstract1', 'abstract2_titel', 'abstract2', \
              'abstract3_titel', 'abstract3', 'abstract4_titel', 'abstract4']
    pdfs = request.files.to_dict()
    text_data = request.form.to_dict()
    pdfs = {k:sqlite3.Binary(pdfs[k].read()) for k in pdfs.keys()}
    datas = {**text_data, **pdfs}
    print(len(datas))
    job_info_strs = ", ".join(labels)
    ph = ", ".join(["?" for _ in labels])
    data_list = [datas[lab] for lab in labels]
    q = "INSERT INTO jobs ({0}) VALUES ({1})".format(job_info_strs, ph)
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute(q, data_list)
    conn.commit()
    conn.close()

    jobs = get_job_list()
    return render_template('job_index.html', jobs=jobs)

@app.route('/delete_db/<string:tabel_name>/<int:job_id>/<int:user_id>', methods=['POST'])
def delete_db(tabel_name, job_id, user_id):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    if tabel_name == "jobs":
        cur.execute(f"DELETE FROM jobs WHERE job_id='{job_id}'")
        # cur.execute(f"DELETE FROM users WHERE job_id='{id}'")
        conn.commit()
        conn.close()
        jobs = get_job_list()
        return render_template('job_index.html', jobs=jobs)
    elif tabel_name == "users":
        cur.execute(f"DELETE FROM users WHERE user_id='{user_id}'")
        conn.commit()
        conn.close()
        users = get_users_id(job_id=job_id)
        return render_template('applicant_index.html', users=users)


def get_users_id(job_id):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute(f"SELECT user_id, name, total_score FROM users WHERE job_id='{job_id}' ORDER BY total_score DESC")
    titles = cur.fetchall()
    conn.close()
    return titles

if __name__ == '__main__':
    app.run()


