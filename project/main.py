import os
from flask_login import login_required, current_user
from . import db
import subprocess
import re
import yaml
from time import sleep
from dotenv import load_dotenv
from flask import Blueprint, Flask, redirect, render_template, request, flash, url_for, abort
load_dotenv()

title = os.getenv("APPIMAGES_TITLE") or "RACE AppImage deployment tool"
path = os.getenv("APPIMAGES_PATH")
inventory = os.getenv("INVENTORY_FILE")
user = os.getenv("APPIMAGES_USER") or os.getenv("USER")
port_no = os.getenv("PORT_SERVER")

if path is None or not os.path.isdir(path):
    raise FileNotFoundError(
        f"AppImages directory ({path}) does not exist. Create it or adjust the path in .env and re-launch the application.")

if inventory is None or not os.path.isfile(inventory):
    raise FileNotFoundError(
        f"Inventory YAML does not exist at ({inventory}). Create it or adjust the path in .env and re-launch the application.")

main = Blueprint('main', __name__)

@main.context_processor
def inject_title_for_all_templates():
    return dict(title=title)

@main.route('/', methods=['POST', 'GET'])
@main.route('/appimages', methods=['POST', 'GET'])
@login_required
def index():
    hosts = []
    files = os.listdir(path)

    with open(inventory, "r") as stream:
        try:
            y = yaml.safe_load(stream)
            for i in y.items():
                if "hosts" in i[1]:
                    hostsTemp = i[1]["hosts"]
                    for hostname, ansible_host in hostsTemp.items():
                        hosts.append((hostname, ansible_host["ansible_host"]))
        except yaml.YAMLError as exc:
            print(exc)

    return render_template('index.html', files=files, hosts=hosts)


@main.route('/deploy', methods=['POST'])
@login_required
def call_ansible():
    pc_form = request.form.getlist('pc')

    appimage_form = request.form['appimages']

    if not pc_form:
        flash("Enter a valid PC to deploy")
        return redirect(url_for('main.index'))
    s = ','.join(pc_form)
    x = s.split(",")
    pcs_failed = []
    for m in x:
        try:
            output = subprocess.run(["ansible-playbook", "playbook_deploy.yml", "-i", inventory, "-u", f"{user}", "-e",
                                        f"pc={m}", "-e",
                                        f"appuser={user}", "-e",
                                        f"appimage={appimage_form}", "-e",
                                        f"port_no={port_no}", "-e",
                                        f"appimage_path={path}", ])
            print(output)
            if "returncode=0" not in str(output):
                pcs_failed.append(m)
        except Exception as e:
            print(e)

    hosts = []
    with open(inventory, "r") as stream:
        try:
            y = yaml.safe_load(stream)
            for i in y.items():
                if "hosts" in i[1]:
                    hostsTemp = i[1]["hosts"]
                    for pc in pc_form:
                        for hostname, ansible_host in hostsTemp.items():
                            if pc in hostname:
                                hosts.append(
                                    (hostname, ansible_host["ansible_host"]))
        except yaml.YAMLError as exc:
            print(exc)

    return render_template('deploy.html', pcs=pc_form, image=appimage_form, hosts=hosts, port_no=port_no, pcs_failed=pcs_failed)


@main.route('/view_log', methods=['POST', 'GET'])
@login_required
def view_log():
    if request.method == 'POST':
        if request.form['stop'] == 'STOP':
            stopmypc = request.form['pc']
            try:
                output = subprocess.run(["ansible-playbook", "playbook_halt.yml", "-i", inventory,
                                         "-e", f"appuser={user}", "-e", f"pc={stopmypc}", "-u", f"{user}"])
                print(output)
            except Exception as e:
                print(e)
            return render_template('stop_appimage.html', info="AppImage Stopped")
        else:
            host = request.form['host']
            port = request.form['port']
            print("target is " + host + ":" + port)
            if not host or not port:
                flash("Enter a valid host and port to read logs from")
                return redirect(url_for('main.index'))
            return render_template('view_log_client.html', host=host, port=port)

    mypc = request.args.get('pc')
    return render_template('view_log_client.html', mypc=mypc)
