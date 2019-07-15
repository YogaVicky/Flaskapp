from flask import Flask, render_template, request, jsonify, flash, redirect, session, abort
from werkzeug import secure_filename
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms.fields import DateField
import os
import pandas as pd
import math
import shutil
import sys
from datetime import timedelta
from cryptography.fernet import Fernet
from pymysql import connect
from datetime import datetime
import json


app = Flask(__name__)

bootstrap = Bootstrap(app)
UPLOAD_FOLDER = 'D:/PROJECTS/bids'
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
else:
    pass

class MyForm(Form):
    date = DateField(id='datepick')


def dbconect(sql):
    result = []
    db = connect(host='192.168.2.90', database='pfxdb', user='pipe', password='asdf$123')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    for i in cursor.fetchall():
        result.append(i[0])
    cursor.close()
    return result


def get_all(sql):
    result = []
    db = connect(host='192.168.2.90', database='pfxdb', user='pipe', password='asdf$123')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    for i in cursor.fetchall():
        result.append(i)
    cursor.close()
    return result

def get_lcl(sql):
    result = []
    db = connect(host='localhost', database='pfx', user='root', password='1234')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    for i in cursor.fetchall():
        result.append(i)
    cursor.close()
    return result

def get_lcl2(sql):
    db = connect(host='localhost', database='pfx', user='root', password='1234')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()

def get_artistID(login):
    """find artist ID with the help of their workstation login"""
    try:
        sql = "SELECT artist_id from artist where login='{0}'".format(str(login))
        artistID = dbconect(sql)[0]
        return artistID
    except IndexError:
        return []


def collect_typename(typeID):
    try:
        sql = "SELECT type_name from type where type_id={0}".format(typeID)
        tasktype = dbconect(sql)[0]
        return tasktype
    except IndexError:
        return []


def collect_projName(projID):
    """return project ID for project name or code"""
    try:
        sql = "SELECT proj_code from project_settings WHERE proj_id='{0}'".format(projID)
        list_projName = dbconect(sql)[0]
        return list_projName
    except IndexError:
        return []


def collect_scopeName(scopeID):
    """given scopeName, return corresponding scope ID"""
    try:
        sql = "SELECT scope_name from scope WHERE scope_id={0}".format(scopeID)
        scopeName = dbconect(sql)[0]
        return scopeName
    except IndexError:
        return []


def collect_statusName(task_status_id):
    try:
        sql = "SELECT task_status_name from task_status where task_status_id={0}".format(task_status_id)
        statusName = dbconect(sql)[0]
        return statusName
    except IndexError:
        return []

def get_pfxdb_notes(pub_id):
    '''function to return list of tuples containing reviewer name,notes,& attachment'''
    pfxdb_notes = []
    reviewer_list = []
    notes_list = []
    attachment_list = []

    for i in pub_id:
        sql = "SELECT reviewer_name,notes,attachment from notes where publish_id='{0}'".format(i)
        res = get_all(sql)
        if res != []:
            for j in res:
                reviewer_list.append(j[0])
                notes_list.append(j[1])
                attachment_list.append(j[2])

            temp = (i, reviewer_list, notes_list, attachment_list)
            pfxdb_notes.append(temp)
        else:
            temp = (i, '', '', '')
            pfxdb_notes.append(temp)

    return pfxdb_notes

def takeninth(elem):
    return elem[9]

def get_task_details(userLogin):
    '''function to get task assigned to artist'''
    artID = get_artistID(userLogin)
    sql = "SELECT * from task where assigned_to={0} ORDER BY bid_end desc".format(artID)
    res = get_all(sql)
    version_dict = []
    notes_dict = []
    p_res = []
    for i in res:
        i = list(i)
        task_id = i[0]
        proj_id = i[1]
        scope_id = i[2]
        type_id = i[3]
        pub_id = get_publish_id(task_id)
        ver = get_pfxdb_version(pub_id)
        version_dict.append(ver)
        notes = get_pfxdb_notes(pub_id)
        notes_dict.append(notes)

        ##### HTML link replacing and downloading or opening the link upon clicking in browser ########
        import os
        import shutil
        # paths = []
        try:
            for attachment in notes_dict[0][1][3]:

                if os.path.exists(attachment):

                    filename = os.path.basename(attachment)

                    global new_file_path
                    new_file_path = "D:/Murthy/Git_Projects/webmodules/login/static/tempfiles/" + filename
                    try:
                        files = shutil.copy(attachment, new_file_path)
                    except:
                        pass
                    if filename == os.path.basename(new_file_path):

                        if attachment == attachment in notes_dict[0][1][3]:
                            #
                            index = notes_dict[0][1][3].index(attachment)

                            notes_dict[0][1][3].remove(attachment)
                            notes_dict[0][1][3].insert(index, filename)
                #
                else:
                    print("Path does not exist")

        except IndexError:
            pass
        ##### HTML #######

        if type_id == 0:
            sql = "SELECT task_type_name from task where task_id={0}".format(task_id)
            res = dbconect(sql)[0]
            i[3] = res.upper()
        elif type(type_id) == int:
            type_name = collect_typename(type_id)
            i[3] = type_name.upper()

        user = i[12]
        frame_start = i[5]
        frame_end = i[6]
        description = i[7]
        # emd = i[10]
        # cmd = i[11]
        task_status = i[16]
        bid_start = i[17]
        bid_end = i[18]

        if task_id != 0:
            proj = collect_projName(proj_id)
            scope = collect_scopeName(scope_id)
            status = collect_statusName(task_status)
            i[1] = proj
            i[2] = scope
            i[16] = status
            try:
                i[18] = i[18].date().strftime('%d-%m-%Y')
            except AttributeError:
                i[18] = i[18].split()[0]
                end_date = i[18].split('-')[2]
                end_mnth = i[18].split('-')[1]
                end_yr = i[18].split('-')[0]
                i[18] = end_date + '-' + end_mnth + '-' + end_yr

            indexes = [4, 8, 9, 10, 11, 12, 13, 14, 15, 17]
            for index in sorted(indexes, reverse=True):
                del i[index]
            p_res.append(i)
        #

        else:
            proj = collect_projName(proj_id)
            scope = collect_scopeName(scope_id)
            status = collect_statusName(task_status)
            i[1] = proj
            i[2] = scope
            i[16] = status
            try:

                i[18] = i[18].date().strftime('%d-%m-%Y')
            except AttributeError:
                i[18] = i[18].split()[0]
                end_date = i[18].split('-')[2]
                end_mnth = i[18].split('-')[1]
                end_yr = i[18].split('-')[0]
                i[18] = end_date + '-' + end_mnth + '-' + end_yr

            indexes = [4, 8, 9, 10, 11, 12, 13, 14, 15]
            for index in sorted(indexes, reverse=True):
                del i[index]
            p_res.append(i)

    # print(notes_dict)
    # print(type(p_res))
    # length = len(p_res)
    # print(length)
    # print(p_res)

    # print(p_res)
    return p_res, version_dict, notes_dict


def collect_projID(projName):
    '''returning corresponding project ID of project codes/names'''
    try:
        sql = "SELECT proj_id from project_settings WHERE proj_code='{0}'".format(projName)
        list_projID = dbconect(sql)[0]
        return list_projID
    except IndexError:
        return []


def collect_scopID(scopeName, projid):
    '''return scope_id of scope_name'''
    try:
        sql = "SELECT scope_id from scope WHERE scope_name LIKE '%{0}' AND proj_id='{1}'".format(scopeName, projid)
        list_scopeID = dbconect(sql)[0]
        return list_scopeID
    except IndexError:
        return []


def collect_typeID(typeName):
    '''find type id for type name'''
    try:
        sql = "SELECT type_id from type WHERE type_name='{0}'".format(typeName)
        task_id = dbconect(sql)[0]
        return task_id
    except IndexError:
        return []


def get_publish_id(taskID):
    '''get list of publishes made against the specific task'''
    pub_id = []
    sql = "SELECT publish_id from publish_q where task_id={0}".format(taskID)
    res = dbconect(sql)
    return res


def get_pfxdb_version(pub_id):
    '''get internal versions from db based on the publish IDs by looping through their list'''
    pfxdb_version = []
    for i in pub_id:
        sql = "SELECT int_version from file where publish_id='{0}'".format(i)
        try:
            res = dbconect(sql)[0]
            temp = (i, res)
            pfxdb_version.append(temp)
        except IndexError:
            pfxdb_version = []
    return pfxdb_version


@app.route('/')
def home():
    '''renders the homepage after successful login'''
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        # different configs according to dept and access settings
        userLogin = session.get('username')
        # userLogin = 'benjamin'
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        res = get_all(sql)[0]
        session['dept'] = res[0]
        session['access'] = res[1]
        result = get_task_details(userLogin)
        dashbord_dept = [1, 2, 3, 19, 23, 20]

        min_opt = ['YTS', 'WIP', 'HOLD', 'REVIEW']
        low_opt = ['YTS', 'WIP', 'HOLD', 'REVIEW', 'TL_APPROVED', 'TL_IMPROVISE', 'SUP_REVIEW']
        high_opt = ['SUP_REVIEW', 'SUP_APPROVED', 'SUP_IMPROVISE', 'STAGE_1_QC', 'CLIENT_REVIEW']
        max_opt = ['STAGE_1_QC', 'STAGE_1_APPROVED', 'STAGE_1_IMPROVISE', 'STAGE_2_QC', 'CLIENT_REVIEW']
        super_opt = ['STAGE_2_QC', 'STAGE_2_APPROVED', 'STAGE_2_IMPROVISE', 'CLIENT_REVIEW']
        client_opt = ['CLIENT_REVIEW', 'CLIENT_APPROVED', 'CLIENT_IMPROVISE']
        prod_opt = ['YTS', 'WIP', 'HOLD', 'REVIEW', 'CLIENT_REVIEW', 'CLIENT_APPROVED', 'CLIENT_IMPROVISE',
                    'TL_APPROVED', 'TL_IMPROVISE', 'SUP_REVIEW', 'SUP_APPROVED', 'SUP_IMPROVISE', 'STAGE_1_QC',
                    'STAGE_1_APPROVED', 'STAGE_1_IMPROVISE', 'STAGE_2_QC',
                    'STAGE_2_APPROVED', 'STAGE_2_IMPROVISE']

        prod_dept = [11]
        # prod_desn = [32,33,34,36,37,38]
        # status_opt =
        if res[0] in dashbord_dept and res[1] == 'min':
            # print(len(result[0]),len(result[1]),len(result[2]))

            return render_template("dashboard_1.html", username=userLogin, data=result[0], status_opt=min_opt,
                                   versions=result[1], notes=result[2])
        if res[0] in dashbord_dept and res[1] == 'low':
            # print(len(result[0]),len(result[1]),len(result[2]))
            return render_template("TL_dashboard.html", username=userLogin, data=result[0], status_opt=low_opt,
                                   versions=result[1], notes=result[2])
        if res[0] in dashbord_dept and res[1] == 'high':
            # print(len(result[0]),len(result[1]),len(result[2]))
            return render_template("sup_dashboard.html", username=userLogin, data=result[0], status_opt=high_opt,
                                   versions=result[1], notes=result[2])
        if res[0] in dashbord_dept and res[1] == 'max':
            # print(len(result[0]),len(result[1]),len(result[2]))
            return render_template("ravi_dashboard.html", username=userLogin, data=result[0], status_opt=max_opt,
                                   versions=result[1], notes=result[2])
        elif res[0] in prod_dept and res[1] == 'min':
            return render_template("prod_dashbord.html", username=userLogin, data=result[0], status_opt=prod_opt,
                                   versions=result[1], notes=result[2])
        elif res[0] in prod_dept and res[1] == 'low':
            artID = get_artistID(userLogin)
            sql0 = "select proj_code from project_settings"
            overall_proj = dbconect(sql0)
            sql = "select proj_code,thumbnail,category,bid_start_date,bid_end_date,proj_status_id from project_settings " \
                  "where line_producer={0}".format(artID)
            proj_list = get_all(sql)
            sql = "select projcode from tempvariables"
            proj_list2 = get_all(sql)
            projchecklist = []
            for i in overall_proj:
                projchecklist.append(i[0])
            for i in proj_list2:
                projchecklist.append(i[0])
            sql = "select artist_id,login from artist"
            artist_list = get_all(sql)
            user_dict = dict(artist_list)
            return render_template("projects_display.html", u_name=userLogin, proj_list=proj_list, user_list=user_dict,
                                   allprojlist=projchecklist)
        elif res[0] in prod_dept and res[1] == 'high':
            return render_template("pm_dashbord.html", username=userLogin, data=result[0], status_opt=prod_opt,
                                   versions=result[1], notes=result[2])

            # else:
            #     return render_template("artish_dashbord.html", username=userLogin, data=result[0], status_opt=status_opt,
            #                            versions=result[1], notes=result[2])
            # print(len(result[0]), len(result[1]), len(result[2]))
            # print(result[1])
            # print(result[2])
            # return render_template("dashboard_1.html", username=userLogin, data=result[0], status_opt=status_opt,
            #                        versions=result[1], notes=result[2])
            # return render_template("dashboard_1.html", username=userLogin,data=result[0],status_opt=status_opt,versions=result[1])

            # return render_template("dashboard_1.html", username=userLogin,data=result[0],status_opt=status_opt,versions=result[1])


def collect_bidDetails(artistID):
    '''function to collect bid details'''
    sql = "SELECT * from bid_details where created_by={0}".format(artistID)
    res = get_all(sql)
    return res


@app.route('/for_sup_review')
def for_sup_review():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        userLogin = session.get('username')
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        result = get_task_details(userLogin)
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        details = get_lcl(sql)
        dept = details[0][0]
        access = details[0][1]
        print(access)
        if (access == 'min'):
            print(access)
        if (dept == 23 and ( access == 'low' or access =='max' or access =='high')):
            return render_template("sup_review.html")
        else:
            return render_template("No_access.html")



@app.route('/my_bids', methods=['GET'])
def myBids():
    '''function to return an LP's bids and it's status'''
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        userLogin = session.get('username')
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        result = get_task_details(userLogin)
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        details = get_lcl(sql)
        dept = details[0][0]
        access = details[0][1]
        print(access)
        if ((dept == 11 and ( access == 'high' or access =='max' or access =='low' )) or dept ==20):
            return render_template("html_1.html", bid_details=bid_details)
        else:
            return render_template("No_access.html")




@app.route('/projects', methods=['GET', 'POST'])
def projects():
    '''function to display all projects in DB'''
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        userLogin = session.get('username')
        sql = "select proj_code,thumbnail,category,bid_start_date,bid_end_date,proj_status_id from project_settings"
        proj_list = get_all(sql)
        sql = "select projcode from tempvariables"
        proj_list2 = get_all(sql)
        projchecklist = []
        for i in proj_list:
            projchecklist.append(i[0])
        for i in proj_list2:
            projchecklist.append(i[0])
        sql = "select artist_id,login from artist"
        artist_list = get_all(sql)
        user_dict = dict(artist_list)
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        result = get_task_details(userLogin)
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        details = get_lcl(sql)
        dept = details[0][0]
        access = details[0][1]
        print(access)
        if ((dept == 11 and ( access == 'high' or access =='max' or access =='low' )) or dept ==20):
           return render_template("lp_dashboard.html", u_name=userLogin, proj_list=proj_list, user_list=user_dict,
                               allprojlist=projchecklist)
        else:
            return render_template("No_access.html")



@app.route('/addProj', methods=['GET'])
def addProj():
    '''function to create new project'''
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        userLogin = session.get('username')
        sql = "select proj_code,thumbnail,category,bid_start_date,bid_end_date,proj_status_id from project_settings"
        proj_list = get_all(sql)
        sql = "select projcode from tempvariables"
        proj_list2 = get_all(sql)
        projchecklist = []
        for i in proj_list:
            projchecklist.append(i[0])
        for i in proj_list2:
            projchecklist.append(i[0])
        sql = "select artist_id,login from artist"
        artist_list = get_all(sql)
        user_dict = dict(artist_list)
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        result = get_task_details(userLogin)
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        details = get_lcl(sql)
        dept = details[0][0]
        access = details[0][1]
        print(access)
        if (access == 'min'):
            print(access)
        if (dept == 11 and access =='low' ):
            return render_template("new_proj.html", u_name=userLogin, proj_list=proj_list, user_list=user_dict,
                                   allprojlist=projchecklist)
        else:
                return render_template("No_access.html")


@app.route('/newBid', methods=['GET', 'POST'])
def newBid():
    '''function to upload new bid excel and then load'''
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        userLogin = session.get('username')
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        result = get_task_details(userLogin)
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        details = get_lcl(sql)
        dept = details[0][0]
        access = details[0][1]
        print(access)
        if (access == 'min'):
            print(access)
        if ((dept == 11 and ( access == 'high' or access =='max' or access =='low' )) or dept ==20):
            f = request.files['bid_sheet']
            filename = secure_filename(f.filename)
            proj_name = filename.split('_')[0].upper()  # assumed that all project bidding sheets are named as aln_bidding
            bid_folder = UPLOAD_FOLDER + '/' + proj_name
            if not os.path.exists(bid_folder):
                os.mkdir(bid_folder)
            f.save(os.path.join(bid_folder, filename))
            bid_sheet = bid_folder + '/' + filename

            fread_errors = []
            import pandas as pd
            try:
                shot_excel = pd.read_excel(bid_sheet, sheet_name='Shots')
                shot_json = shot_excel.to_json(bid_folder + '/shots.json', orient='records')
                with open(bid_folder + '/shots.json') as f:
                    shot_json = json.load(f)



            except:
                shot_json = ''
                fread_errors.append(0)

            try:
                asset_excel = pd.read_excel(bid_sheet, sheet_name='Assets')
                asset_json = asset_excel.to_json(bid_folder + '/assets.json', orient='records')
                with open(bid_folder + '/assets.json') as f:
                    asset_json = json.load(f)

            except:
                asset_json = ''
                fread_errors.append(1)
                asset_headers = []
            headers = ['CONPT', 'ANI', 'MGS', 'MAT', 'MM', 'ROT', 'RA', 'DYN', 'LIT', 'REN', 'PRE COMP', 'PNT', 'COM',
                    'STORYBOARD', 'MOD', 'TEX', 'UV', 'FUR', 'RIG', 'LOOKDEV']
            sql = "select login from artist"
            artist_list = get_all(sql)
            user_list = []
            for j in artist_list:
                user_list.append(j[0])
            print(user_list)
            return render_template("bid_table.html", proj=proj_name, errors=fread_errors, shot_json=shot_json,
                                asset_json=asset_json, keys=headers, user_list=user_list)


def get_login(artistID):
    '''function to get login given artist ID'''
    sql = "SELECT login from artist where artist_id={0}".format(artistID)
    try:
        res = dbconect(sql)[0]
    except IndexError:
        res = ''
    return res


@app.route('/<proj_code>/editProj')
def editProj(proj_code):
    '''editing project'''
    # if request.method == 'POST':
    #     data = request.get_json()
    #     proj_code = data['result']
    #     print(proj_code,'proj_code')
    #     return '',200
    # elif request.method == 'GET':
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        userLogin = session.get('username')
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        result = get_task_details(userLogin)
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        details = get_lcl(sql)
        dept = details[0][0]
        access = details[0][1]
        print(access)
        if (access == 'min'):
            print(access)
        if (dept == 11 and access =='low' ):
            import os
            userLogin = session.get('username')
            sql = "SELECT * from project_settings where proj_code='{0}'".format(proj_code)
            res = get_all(sql)[0]
            lp = get_login(res[12])  # get artist login given their artist ID
            print(lp)
            coord_3d = get_login(res[13])
            coord_2d = get_login(res[14])
            proj_manager = get_login(res[15])
            vfx_head = get_login(res[16])
            vfx_sup = get_login(res[17])
            head_2d = get_login(res[18])
            art_dir = get_login(res[19])
            cg_sup = get_login(res[20])
            roto_coord = get_login(res[21])
            paint_coord = get_login(res[22])
            roto_sup = get_login(res[23])
            paint_sup = get_login(res[24])
            stat = res[26]
            if type(stat) == int:
                sql = "SELECT status_name from project_status where project_status_id={0}".format(stat)
                stat - dbconect(sql)[0]
            else:
                pass

            proj_details = dict(code=proj_code, thumbnail=os.path.basename(res[2]), resolution=res[3], category=res[4],
                                fps=res[5], inpDate=res[6], outDate=res[7], slate_2d=res[8],
                                slate_3d=res[9], macro_2d=res[10], macro_3d=res[11], lp=lp, cord_2d=coord_2d,
                                cord_3d=coord_3d, pm=proj_manager, head=vfx_head, sup=vfx_sup, head2d=head_2d,
                                artdir=art_dir, cgsup=cg_sup, roto=roto_coord, pnt=paint_coord, rotosup=roto_sup,
                                pntsup=paint_sup, ocio=res[25], status=stat, bid_st=res[27],
                                bid_e=res[28], inp=res[33], out=res[34], qt_codec=res[35], qt_res=res[36], tech_doc=res[37])

            return render_template("edit_proj.html", details=proj_details,
                                   projCategory=['VFX', 'ROTO', 'PAINT', 'PREP', '2D', '3D'],
                                   projStatus=['IN_PROGRESS', 'YTS', 'WIP', 'PAUSE', 'HOLD', 'REMOVED', 'DELIVERED'])
        else:
            return render_template("No_access.html")


@app.route('/login', methods=['POST'])
def do_admin_login():
    sql = "SELECT password,salt from artist where login = '{0}'".format(request.form['username'])
    try:
        paswd = get_all(sql)[0]
        key_select = paswd[1].encode()
        encripted = paswd[0].encode()
        f = Fernet(key_select)
        password = f.decrypt(encripted)
        # print(password)
        if request.form['password'] == password.decode():
            session['logged_in'] = True
            session['username'] = request.form['username']
            return home()
        else:
            flash('Invalid password!')
            return home()
    except:
        flash('Wrong Username!')
        return home()


def get_artist_notes(artistName):
    '''function to get all notes given to an artist'''
    sql = "SELECT proj_name,scope_name,type_name,int_version,reviewer_name,notes,attachment,note_id , timestamp from notes where artist_name='{0}'".format(
        artistName)
    res = get_all(sql)
    return res

def get_lp_notes(lp):
    return lp

def get_artist_project(artistName):
    '''function to get all project name assign to an artist'''
    sql = "SELECT artist_id from artist where login='{0}'".format(artistName)
    art_id = get_all(sql)[0][0]
    sql = "SELECT DISTINCT proj_id from task where assigned_to='{0}'".format(
        art_id)
    proj_id = get_all(sql)
    list1 = []
    for i in proj_id:
        sql = "SELECT proj_code from project_settings where proj_id ='{0}'".format(i[0])
        list1.append(dbconect(sql)[0])
    return list1


def get_artist_task(artistName):
    sql = "SELECT artist_id from artist where login='{0}'".format(artistName)
    art_id = get_all(sql)[0][0]
    sql = "SELECT DISTINCT task_type_name from task where assigned_to='{0}'".format(
        art_id)
    list1 = get_all(sql)
    task_nam = []
    for i in list1:
        task_nam.append(i[0])
    return task_nam


def get_task_type():
    sql = "SELECT DISTINCT task_type_name from task_type"
    list1 = get_all(sql)
    list1 = get_all(sql)
    task_nam = []
    for i in list1:
        task_nam.append(i[0])
    return task_nam



@app.route("/noteslp" , methods=['GET', 'POST'])
def noteslp():
    import os
    import shutil
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.method == 'POST':
            ajaxinput = request.get_json()
            print(ajaxinput)
            type_convert = {'ROT': '2d_roto', '2D_ELEMENT': '2d_element', 'PAINT': '2d_paint',
                            'MATTEPAINT': 'art_mattepaint',
                            'CONCEPT_ART': 'concept_art', '2D_LAYOUT': '2d_layout', 'SLAPCOMP': '2d_slapcomp',
                            'PRECOMP': '2d_precomp', 'COMP': '2d_out', '2D_TEST': '2d_test',
                            'MATCHMOVE': '3d_matchmove',
                            'MODEL': '3d_model', 'HDRI': '3d_hdri', 'RIGGING': '3d_rigging', 'SHADING': '3d_shading',
                            'LOOKDEV': '3d_lookdev', '3D_TEST': '3d_test', 'LIGHTING': '3d_lighting',
                            'DYNAMICS': '3d_dynamics',
                            'SHOTSCULPT': '3d_shotsculpt', '3D_ANIMATION': '3d_animation', 'TEXTURING': '3d_texture',
                            'PREVIZ': 'pre_visualisation', 'PIPE_TEST': 'pipe_test', 'PIPE_OUT': 'pipe_out',
                            '3D_LAYOUT': '3d_layout'}
            convertion_list = []
            for i in ajaxinput['tNames']:
                convertion_list.append(type_convert[i])
            print('CL: ', convertion_list)
            sql = "SELECT proj_name,scope_name,type_name,int_version,artist_name,reviewer_name,notes,attachment,note_id , timestamp FROM notes"
            proj_all = get_lcl(sql)
            # print(proj_all)
            proj_filter = []
            if(ajaxinput['pNames'] and ajaxinput['sNames'] and ajaxinput['rNames'] and convertion_list):
                for project in proj_all:
                    # print(project)
                    if project[0] in ajaxinput['pNames'] and project[2] in convertion_list and project[1] == ajaxinput['sNames'] and project[5] == ajaxinput['rNames']:
                        proj_filter.append(project)
            elif(ajaxinput['pNames'] and ajaxinput['sNames'] and ajaxinput['rNames']):
                for project in proj_all:
                    # print(project)
                    if project[0] in ajaxinput['pNames'] and project[1] == ajaxinput['sNames'] and project[5] == ajaxinput['rNames']:
                        proj_filter.append(project)
            elif (ajaxinput['pNames'] and ajaxinput['sNames'] and convertion_list):
                for project in proj_all:
                    # print(project)
                    if project[0] in ajaxinput['pNames'] and project[2] in convertion_list and project[1] == ajaxinput['sNames']:
                        proj_filter.append(project)
            elif (ajaxinput['pNames'] and convertion_list and ajaxinput['rNames']):
                for project in proj_all:
                    # print(project)
                    if project[0] in ajaxinput['pNames'] and project[2] in convertion_list and project[5] == ajaxinput['rNames']:
                        proj_filter.append(project)
            elif (ajaxinput['sNames'] and convertion_list and ajaxinput['rNames']):
                for project in proj_all:
                    # print(project)
                    if project[2] in convertion_list and project[1] == ajaxinput['sNames'] and project[5] == ajaxinput['rNames']:
                        proj_filter.append(project)
            elif (ajaxinput['sNames'] and convertion_list):
                for project in proj_all:
                    # print(project)
                    if project[2] in convertion_list and project[1] == ajaxinput['sNames'] :
                        proj_filter.append(project)
            elif (ajaxinput['sNames'] and ajaxinput['rNames']):
                for project in proj_all:
                    # print(project)
                    if project[5] == ajaxinput['rNames'] and project[1] == ajaxinput['sNames']:
                        proj_filter.append(project)
            elif (ajaxinput['sNames'] and ajaxinput['pNames']):
                for project in proj_all:
                    # print(project)
                    if project[0] in ajaxinput['pNames'] and project[1] == ajaxinput['sNames']:
                        proj_filter.append(project)
            elif (ajaxinput['pNames'] and ajaxinput['rNames']):
                for project in proj_all:
                    # print(project)
                    if project[0] in ajaxinput['pNames'] and project[5] == ajaxinput['rNames']:
                        proj_filter.append(project)
            elif (ajaxinput['pNames'] and convertion_list):
                for project in proj_all:
                    # print(project)
                    if project[0] in ajaxinput['pNames'] and project[2] in convertion_list:
                        proj_filter.append(project)
            elif (ajaxinput['rNames'] and convertion_list):
                for project in proj_all:
                    # print(project)
                    if project[5] == ajaxinput['rNames'] and project[2] in convertion_list:
                        proj_filter.append(project)
            elif (ajaxinput['pNames']):
                for project in proj_all:
                    # print(project)
                    if project[0] in ajaxinput['pNames']:
                        proj_filter.append(project)
            elif (ajaxinput['sNames']):
                for project in proj_all:
                    # print(project)
                    if project[1] == ajaxinput['sNames']:
                        proj_filter.append(project)
            elif (ajaxinput['rNames']):
                for project in proj_all:
                    # print(project)
                    if project[5] == ajaxinput['rNames']:
                        proj_filter.append(project)
            elif (convertion_list):
                for project in proj_all:
                    # print(project)
                    if project[2] in convertion_list:
                        proj_filter.append(project)
            else:
                print("NO INPUT")
            # print(proj_filter)
            for i in range(len(proj_filter)):
                proj_filter[i] = list(proj_filter[i])
                if os.path.exists(proj_filter[i][7]):
                    print('proj_default[i][j][7]', proj_filter[i][7])
                    filename = os.path.basename(proj_filter[i][7])
                    print('filename', filename)
                    global newf1
                    newf1 = "D:/webmodules/login/static/tempfiles/" + filename
                    print(newf1)
                    shutil.copy(proj_filter[i][7], newf1)
                    proj_filter[i][7] = filename
                else:
                    proj_filter[i][7] = ""
            print(proj_filter)
            return jsonify(proj_filter = proj_filter)
        userLogin = session.get('username')
        sql = "SELECT artist_id FROM artist WHERE login = '{0}'".format(userLogin)
        temp =  get_lcl(sql)
        user = temp[0][0]
        sql = "SELECT proj_code FROM project_settings WHERE line_producer = '{0}'".format(user)
        temp = get_lcl(sql)
        # print(temp)
        projcode_default = []
        for i in temp:
            projcode_default.append(i[0])
        # print(projcode_default)
        proj_default = []
        for i in projcode_default:
            sql = "SELECT proj_name,scope_name,type_name,int_version,artist_name,reviewer_name,notes,attachment,note_id , timestamp FROM notes WHERE proj_name = '{0}'".format(i)
            temp = get_lcl(sql)
            # print(temp)
            if(temp):
                proj_default.append(temp)
        proj_default = list(proj_default)
        sql = "SELECT proj_name,scope_name,type_name,int_version,artist_name,reviewer_name,notes,attachment,note_id , timestamp FROM notes"
        proj_all = get_lcl(sql)
        # print(proj_all)
        # return "Hello"
        sql = "SELECT proj_code FROM project_settings"
        projects = get_lcl(sql)
        sql = "SELECT scope_name FROM scope"
        scopes = get_lcl(sql)
        # print(scopes)
        sql4 = "SELECT task_type_name FROM task_type"
        types = get_lcl(sql4)
        # print(types)
        sql3 = "SELECT firstname FROM artist WHERE access NOT LIKE 'min'"
        reviewers = get_lcl(sql3)
        # print(reviewers)
        for i in range(len(reviewers)):
            reviewers[i] = list(reviewers[i])
            reviewers[i][0] = reviewers[i][0].lower()

        # print(reviewers)
        for i in range(len(proj_default)):
            for j in range(len(proj_default[i])):
                proj_default[i][j] = list(proj_default[i][j])
                # print(proj_default[i][j][7])
                if os.path.exists(proj_default[i][j][7]):
                    # print('proj_default[i][j][7]', proj_default[i][j][7])
                    filename = os.path.basename(proj_default[i][j][7])
                    # print('filename', filename)
                    global newf
                    newf = "D:/webmodules/login/static/tempfiles/" + filename
                    # print(newf)
                    shutil.copy(proj_default[i][j][7], newf)
                    proj_default[i][j][7] = filename
                else:
                    proj_default[i][j][7]
        # print(types)
        # print(reviewers)
        print(proj_default)
        return render_template("noteslp.html", proj_default = proj_default , proj_all = proj_all , username = userLogin , projects = projects , types = types , scopes = scopes , reviewers = reviewers)
    #
    #     temp = get_artist_notes(userLogin)
    #     retList = []
    #     notes = []
    #     for j in temp:
    #         if os.path.exists(j[6]):
    #             filename = os.path.basename(j[6])
    #             global newf
    #             newf = "D:/webmodules/login/static/tempfiles/" + filename
    #             shutil.copy(j[6], newf)
    #         else:
    #             filename = ""
    #         k = dict(proj=j[0], scope=j[1], type=j[2], int_version=j[3], reviewer=j[4], notes=j[5], attachment=filename , id = j[7] , date = j[8])
    #         notes.append(k)
    #     retList.append(notes)
    #     # print(notes)
    #     temp = get_artist_project(userLogin)
    #     retList.append(temp)
    #     # print(temp)
    #     temp = get_task_type()
    #     # print(temp)
    #     retList.append(temp)
    #     # print(retList)
    # return render_template("noteslp.html",user = retList)



@app.route("/notes")
def notes():
    import os
    import shutil
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        userLogin = session.get('username')
        temp = get_artist_notes(userLogin)
        retList = []
        notes = []
        for j in temp:
            if os.path.exists(j[6]):
                filename = os.path.basename(j[6])
                global newf
                newf = "D:/webmodules/login/static/tempfiles/" + filename
                shutil.copy(j[6], newf)
            else:
                filename = ""
            k = dict(proj=j[0], scope=j[1], type=j[2], int_version=j[3], reviewer=j[4], notes=j[5], attachment=filename , id = j[7] , date = j[8])
            notes.append(k)
        retList.append(notes)
        # print(notes)
        temp = get_artist_project(userLogin)
        retList.append(temp)
        # print(temp)
        temp = get_task_type()
        # print(temp)
        retList.append(temp)
        print(retList)
    return render_template("test.html",user = retList)

    # paths = []

@app.route("/note",methods=['GET', 'POST'])
def process():
    import os
    import shutil
    if request.method == 'POST':
        data = request.get_json()
        # print('Hello1')
        # print(data)
        # print(data['pNames'])
        # print(data['tNames'])
        userLogin = session.get('username')
        temp = get_artist_notes(userLogin)
        # print(temp)
        retList = []
        notes = []
        type_convert = {'ROT': '2d_roto', '2D_ELEMENT': '2d_element', 'PAINT': '2d_paint', 'MATTEPAINT': 'art_mattepaint',
                'CONCEPT_ART': 'concept_art', '2D_LAYOUT': '2d_layout', 'SLAPCOMP': '2d_slapcomp',
                'PRECOMP': '2d_precomp', 'COMP': '2d_out', '2D_TEST': '2d_test', 'MATCHMOVE': '3d_matchmove',
                'MODEL': '3d_model', 'HDRI': '3d_hdri', 'RIGGING': '3d_rigging', 'SHADING': '3d_shading',
                'LOOKDEV': '3d_lookdev', '3D_TEST': '3d_test', 'LIGHTING': '3d_lighting', 'DYNAMICS': '3d_dynamics',
                'SHOTSCULPT': '3d_shotsculpt', '3D_ANIMATION': '3d_animation', 'TEXTURING': '3d_texture',
                'PREVIZ': 'pre_visualisation', 'PIPE_TEST': 'pipe_test', 'PIPE_OUT': 'pipe_out',
                '3D_LAYOUT': '3d_layout'}
        for j in temp:
            convertion_list = []
            for i in data['tNames']:
                # print(i)
                convertion_list.append(type_convert[i])
            # print('CL: ', convertion_list)
            if j[0] in data['pNames'] and j[2] in convertion_list:
                # print(j[6])
                if os.path.exists(j[6]):
                    filename = os.path.basename(j[6])
                    global newf2
                    newf2 = "D:/webmodules/login/static/tempfiles/" + filename
                    shutil.copy(j[6], newf2)
                else:
                    filename = ""
                k = dict(proj=j[0], scope=j[1], type=j[2], int_version=j[3], reviewer=j[4], notes=j[5], attachment=filename, id = j[7] , date = j[8])
                notes.append(k)
        retList.append(notes)
        temp = get_artist_project(userLogin)
        retList.append(temp)
        temp = get_task_type()
        retList.append(temp)
        print(retList)
        return jsonify(user=retList)
        # return '',200


@app.route("/shot/<int:shotproj_id>", methods=['GET', 'POST'])
def shot(shotproj_id):

    tasktypes = {'PIPE': 'pipe_ingest', 'REF': 'pipe_reference', 'GENERIC': 'pipe_generic', 'TST': 'pipe_test',
                 '3DPIPE': '3d_pipe', 'MM': '3d_matchmove', 'TEX': '3d_texture', 'SHADE': '3d_shading',
                 'RIG': '3d_rigging', 'ANI': '3d_animation', 'SS': '3d_shotsculpt', 'FX': '3d_fx',
                 'LGHT': '3d_lighting',
                 'HDRI': '3d_hdri', 'CGT': '3d_test', 'CG': '3d_out', 'OUT': '2d_out', 'LAY': '2d_layout',
                 'PREP': '2d_prep', 'SLPCMP': '2d_slapcomp', 'PRE': '2d_precomp', 'CMP': '2d_comp', 'TST': '2d_test',
                 '2DPIPE': '2d_pipe', 'DYN': '3d_dynamics', 'LOOKDEV': '3d_lookdev', 'CONC': 'concept_art',
                 'MP': 'art_mattepaint', 'PNT': '2d_paint', 'PREVIZ': 'pre_visualisation', 'E': '2d_element',
                 'ROT': '2d_roto', 'HDRP': '3d_hdrphotos', 'MOD': '3d_model', 'LAYOUT_CAM': '3d_layout',
                 '2DPIPE': '2d_pipe', 'MGSC': '3d_mayas', 'NGSC': '2d_nukes', 'FGSC': '2d_fusions', 'CMPA': '2d_comp_a',
                 'CMPB': '2d_comp_b', 'CMPC': '2d_comp_c', 'CMPD': '2d_comp_d', 'CMPE': '2d_comp_e'}
    typeid = {
        "ROT": 32,
        "2D Element": 31,
        "Paint": 29,
        "Mattepaint": 28,
        "Concept Art": 27,
        "2D Layout": 18,
        "Slapcomp": 20,
        "Precomp": 21,
        "Comp": 22,
        "2D Test": 23,
        "MatchMove": 6,
        "Texturing": 7,
        "Shading": 8,
        "Rigging": 9,
        "3D Animation": 10,
        "ShotSculpt": 11,
        "Dynamics": 12,
        "Model": 35,
        "Lighting": 13,
        "3D Test": 15,
        "LookDev": 26,
        "HRDI": 14,
        "3D Layout": 37,
        "Previz": 30,
        "Pipe Test": 4,
        "Pipe Out": 17
    }
    if request.method == 'POST':
        userLogin = session.get('username')
        scopenotes = request.form.get('Scopenotes')
        tasknotes = request.form.get('Tasknotes')
        print("tasknotes",tasknotes)
        assignednotes = request.form.get('Assignednotes')
        intversionnotes = request.form.get('INTVersionnotes')
        notesnotes = request.form.get('Notes')
        attachmentnotes = request.files.get('Attachment')
        print(scopenotes,tasknotes,assignednotes,intversionnotes,notesnotes,attachmentnotes,shotproj_id,userLogin)
        excel = request.files.get('excel')
        scategory = request.form.get('scategory')
        sname = request.form.get('scopename')
        keyword = request.form.get('keyword')
        scopeattach = request.files.get('scopeattach')
        thumb = request.form.get('thumbnail')
        frames = request.form.get('frames')
        sap = request.form.get('sap')
        desc = request.form.get('desc')
        sid2 = request.form.get('categoryid2')
        sid = request.form.get('categoryid')
        createscope = request.form.get('createscope')
        taskexcel = request.files.get('taskexcel')
        taskformproject = request.form.get('Project')
        taskformsubscope = request.form.get('Subscope')
        taskformscope = request.form.get('Scope')
        taskformlength = request.form.get('Taskslength')
        if(scopenotes):
            sql = "SELECT proj_code FROM project_settings WHERE proj_id = '{0}'".format(shotproj_id)
            proj_code = get_lcl(sql)[0][0]
            filename = secure_filename(attachmentnotes.filename)
            # Save Thumb File
            filepath = '//san/10_TEMP_FILES/' + proj_code + '/DB/PFXDB/ATTACHMENTS/'
            print(filepath)
            proj_code.save(os.path.join(filepath, filename))
            proj_code.save(os.path.join('c:\\temp\\',filename))
            pjthumbfile = filepath + filename

            sql = "SELECT login FROM artist WHERE artist_id = '{0}'".format(assignednotes)
            artist = get_lcl(sql)[0][0]
            sql = "SELECT scope_id FROM scope WHERE scope_name = '{0}'".format(scopenotes)
            scopeid = get_lcl(sql)[0][0]
            sql = "SELECT publish_id FROM file WHERE scope_id = '{0}' AND proj_id ='{1}'".format(scopeid,shotproj_id)
            publishid = get_lcl(sql)[0][0]
            sql = "INSERT INTO notes (proj_name, publish_id, scope_name, type_name, artist_name, reviewer_name, int_version,notes,attachment) VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}')".format(proj_code,publishid,scopenotes,tasknotes,artist,userLogin,intversionnotes,notesnotes,pjthumbfile)
            print(sql)
            get_lcl(sql)
        if(taskformlength):
            if(int(taskformlength) == 1):
                singletaskproj = int(request.form.get('Project'))
                singletasksubscope = request.form.get('Subscope')
                singletaskscope = request.form.get('Scope')
                singletasktasks = request.form.get('Task')
                singletaskdesc = request.form.get('Description')
                singletaskfmd = float(request.form.get('FMD'))
                singletaskstartframe = request.form.get('startframe')
                singletaskendframe = request.form.get('endframe')
                singletaskbidstart = datetime.strptime(request.form.get('startdate'),"%Y-%m-%d")
                singletaskbidend = singletaskbidstart + timedelta(int(singletaskfmd)+1)
                tid = typeid[singletasktasks]
                print(typeid)
                sql = "SELECT scope_id from scope WHERE scope_name = '{0}'".format(singletasksubscope + '/' + singletaskscope)
                print(sql)
                scopeid = get_lcl(sql)
                print(scopeid)
                sql2 = "INSERT INTO task(proj_id,scope_id,type_id,task_type_name,description,FMD,frame_start,frame_end,bid_start,bid_end) VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(singletaskproj,scopeid[0][0],tid, singletasktasks, singletaskdesc, singletaskfmd, singletaskstartframe, singletaskendframe, singletaskbidstart, singletaskbidend)
                print(sql2)
                # get_lcl2(sql2)
            if(int(taskformlength) > 1):
                for i in range(int(taskformlength)):
                    i = str(i)

                    table1 = request.form.get('Project' + i)
                    table2 = request.form.get('Scope' + i)
                    table3 = request.form.get('Subscope' + i)
                    table4 = request.form.get('Task' + i)
                    table5 = request.form.get('Description' + i)
                    table6 = float(request.form.get('FMD' + i))
                    table7 = request.form.get('startframe' + i)
                    table8 = request.form.get('endframe' + i)
                    table9 = datetime.strptime(request.form.get('bidstart' + i),"%Y-%m-%d")
                    table10 = table9 + timedelta(int(table6) + 1)
                    tid = typeid[table4]
                    sql = "SELECT scope_id from scope WHERE scope_name = '{0}'".format(table3 + '/' +table2 )
                    scopeid = get_lcl(sql)
                    print(scopeid)
                    sql2 = "INSERT INTO task(proj_id,scope_id,type_id,task_type_name,description,FMD,frame_start,frame_end,bid_start,bid_end) VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(table1,scopeid[0][0],tid,table4,table5,table6,table7,table8,table9,table10)
                    # get_lcl2(sql2)
                    print(sql2)

        if(taskexcel):
            checkexcel = 0
            print(taskexcel.filename)
            df = pd.read_excel(taskexcel)
            df = df.fillna("-")
            projectexcel = df['Project'].tolist()
            lengthexcel = len(projectexcel)
            print(lengthexcel)
            scopeexcel = df['Scope'].tolist()
            subscopeexcel = df['Subscope'].tolist()
            tasksexcel = df['Task'].tolist()
            descriptionexcel = df['Description'].tolist()
            FMDexcel = df['FMD'].tolist()
            StartFrameexcel = df['Startframe'].tolist()
            EndFrameexcel = df['Endframe'].tolist()
            Bidstartexcel = df['Bidstart'].tolist()
            for i in range(lengthexcel):
                print(tasksexcel[i])
                check = 0
                if projectexcel[i] != "-":
                    check = check + 1
                else:
                    flash(f"Project name missing in Row {i+1}")
                if tasksexcel[i] != "-":
                    check = check + 1
                else:
                    flash(f"Task name missing in Row {i+1}")
                if subscopeexcel[i] != "-":
                    check = check + 1
                else:
                    flash(f"Subscope name missing in Row {i+1}")
                if (scopeexcel[i] != "-"):
                    check = check + 1
                else:
                    flash(f"Scope name missing in Row {i+1}")
                if (descriptionexcel[i] != "-"):
                    check = check + 1
                else:
                    flash(f"Description missing in Row {i+1}")
                if (FMDexcel[i]!= "-"):
                    check = check + 1
                else:
                    flash(f"FMD missing in Row {i+1}")
                if (StartFrameexcel[i] != "-"):
                    check = check + 1
                else:
                    flash(f"StartFrame missing in Row {i+1}")
                if (EndFrameexcel[i] != "-"):
                    check = check + 1
                else:
                    flash(f"EndFrame missing in Row {i+1}")
                if (Bidstartexcel[i] != "-"):
                    check = check + 1
                else:
                    flash(f"BidStart missing in Row {i+1}")
                print(check)
                if (check == 9):
                    print(tasksexcel[i])
                    check = tasksexcel[i]
                    tasksexcel[i] = tasktypes[check]
                    print(projectexcel)
                    print(scopeexcel)
                    print(subscopeexcel)
                    print(tasksexcel)
                    print(descriptionexcel)
                    print(FMDexcel)
                    print(StartFrameexcel)
                    print(EndFrameexcel)
                    print(Bidstartexcel)
                    print(taskexcel)

                    sql = "SELECT proj_id from project_settings WHERE proj_code = '{0}'".format(projectexcel[i])
                    projectid = get_lcl(sql)
                    print(projectid[0][0])
                    sql = "SELECT type_id from type WHERE type_name = '{0}'".format(tasksexcel[i])
                    typeid = get_lcl(sql)
                    print(typeid)
                    sql = "SELECT scope_id from scope WHERE scope_name = '{0}'".format(subscopeexcel[i] + '/' +scopeexcel[i])
                    scopeid = get_lcl(sql)
                    print(scopeid)
                    FMD = int(FMDexcel[i]) + 1
                    bidend = Bidstartexcel[i] + timedelta(FMD)
                    sql2 = "INSERT INTO task(proj_id,scope_id,type_id,task_type_name,description,FMD,frame_start,frame_end,bid_start,bid_end) VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(projectid[0][0],scopeid[0][0],typeid[0][0],tasksexcel[i],descriptionexcel[i],FMDexcel[i],StartFrameexcel[i],EndFrameexcel[i],Bidstartexcel[i],bidend)
                    get_lcl2(sql2)
                    print(sql2)

        if(sid2):
            sid2 = sid2.rsplit('/', 1)
            scid = sid2[0]
            print(scid)
            print(createscope)
            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id,createscope,scid)
            get_lcl(sql2)
            print(sql2)


        if(excel):
            print(excel.filename)
            df = pd.read_excel(excel)
            frames = df['frames']
            subscope = df['sub_scope'].tolist()
            scopename = df['scope_name'].tolist()
            sap = df['SAP']
            keyword = df['keyword']
            description = df['description']
            pipeline = df['pipeline']
            projcode = df['proj_code']
            length = df['ID']
            checktotal = 0
            for i in length:
                print(scopename[i - 1])
                scopelist = subscope[i-1].split('/')
                if scopelist[0] == 'Asset':
                    len2 = len(scopelist)
                    print(len2)
                    if len2 > 9:
                        continue
                    count = 0
                    count1 = 0
                    count2 = 0
                    if len2 == 1:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                scopename[i - 1] = scopename[i - 1].strip()
                                sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(
                                    shotproj_id, scopename[i - 1], scat)
                                print(sql2)
                                print('exist')
                                get_lcl(sql2)
                                sname = subscope[i - 1] + '/' + scopename[i - 1]
                                sname = sname.strip()
                                print(sname)
                                sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                    shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                    description[i - 1])
                                print(sql)
                                get_lcl2(sql)
                                checktotal = checktotal +1


                    if len2 == 2:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                count1 = 1
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        scopename[i-1] = scopename[i-1].strip()
                                        sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i-1], scat)
                                        print(sql2)
                                        print('exist')
                                        get_lcl(sql2)
                                        count = 1
                                        print(count)
                                        sname = subscope[i - 1] + '/' + scopename[i - 1]
                                        print(sname)
                                        sname = sname.strip()
                                        sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                            shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                            description[i - 1])
                                        print(sql)
                                        get_lcl2(sql)
                                        checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[1] = scopelist[1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id,scopelist[1], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(scopelist[1])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i-1] = scopename[i-1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id,scopename[i-1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname = sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

                    if len2 == 3:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        count1 = 1
                                        for check3 in scope_list:
                                            if check3[1] == scopelist[2]:
                                                print(check3[1])
                                                scat = check3[0]
                                                scopename[i - 1] = scopename[i - 1].strip()
                                                sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], scat)
                                                print(sql2)
                                                print('exist')
                                                get_lcl(sql2)
                                                count = 1
                                                print(count)
                                                sname = subscope[i - 1] + '/' + scopename[i - 1]
                                                print(sname)
                                                sname = sname.strip()
                                                sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],description[i - 1])
                                                print(sql)
                                                get_lcl2(sql)
                                                checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[2]= scopelist[2].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopelist[2], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(scopelist[2])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i - 1] = scopename[i - 1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname = sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

                    if len2 == 4:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        for check3 in scope_list:
                                            if check3[1] == scopelist[2]:
                                                print(check3[1])
                                                scat = check3[0]
                                                count1 = 1
                                                for check4 in scope_list:
                                                    if check4[1] == scopelist[3]:
                                                        print(check4[1])
                                                        scat = check4[0]
                                                        scopename[i - 1] = scopename[i - 1].strip()
                                                        sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], scat)
                                                        print(sql2)
                                                        print('exist')
                                                        get_lcl(sql2)
                                                        count = 1
                                                        print(count)
                                                        sname = subscope[i - 1] + '/' + scopename[i - 1]
                                                        print(sname)
                                                        sname = sname.strip()
                                                        sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                                            shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                                            description[i - 1])
                                                        print(sql)
                                                        get_lcl2(sql)
                                                        checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[3] = scopelist[3].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopelist[3], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(scopelist[3])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i - 1] = scopename[i - 1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname =sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

                    if len2 == 5:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        for check3 in scope_list:
                                            if check3[1] == scopelist[2]:
                                                print(check3[1])
                                                scat = check3[0]
                                                for check4 in scope_list:
                                                    if check4[1] == scopelist[3]:
                                                        print(check4[1])
                                                        scat = check4[0]
                                                        count1 = 1
                                                        for check5 in scope_list:
                                                            if check5[1] == scopelist[4]:
                                                                print(check5[1])
                                                                scat = check5[0]
                                                                scopename[i - 1] = scopename[i - 1].strip()

                                                                sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], scat)
                                                                print(sql2)
                                                                print('exist')
                                                                get_lcl(sql2)
                                                                count = 1
                                                                print(count)
                                                                sname = subscope[i - 1] + '/' + scopename[i - 1]
                                                                print(sname)
                                                                sname = sname.strip()
                                                                sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                                                    shotproj_id, scat, sname, keyword[i - 1], frames[i - 1],
                                                                    sap[i - 1], description[i - 1])
                                                                print(sql)
                                                                get_lcl2(sql)
                                                                checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[4] = scopelist[4].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopelist[4], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(scopelist[4])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i - 1] = scopename[i - 1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname = sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

                    if len2 == 6:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        for check3 in scope_list:
                                            if check3[1] == scopelist[2]:
                                                print(check3[1])
                                                scat = check3[0]
                                                for check4 in scope_list:
                                                    if check4[1] == scopelist[3]:
                                                        print(check4[1])
                                                        scat = check4[0]
                                                        for check5 in scope_list:
                                                            if check5[1] == scopelist[4]:
                                                                print(check5[1])
                                                                scat = check5[0]
                                                                count1 = 1
                                                                for check6 in scope_list:
                                                                    if check6[1] == scopelist[5]:
                                                                        print(check6[1])
                                                                        scat = check6[0]
                                                                        scopename[i - 1] = scopename[i - 1].strip()

                                                                    sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], scat)
                                                                    print(sql2)
                                                                    print('exist')
                                                                    get_lcl(sql2)
                                                                    count = 1
                                                                    print(count)
                                                                    sname = subscope[i - 1] + '/' + scopename[i - 1]
                                                                    print(sname)
                                                                    sname = sname.strip()
                                                                    sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                                                        shotproj_id, scat, sname, keyword[i - 1], frames[i - 1],
                                                                        sap[i - 1], description[i - 1])
                                                                    print(sql)
                                                                    get_lcl2(sql)
                                                                    checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[5] = scopelist[5].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopelist[5], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(scopelist[5])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i - 1] = scopename[i - 1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname = sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

                    if len2 == 7:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        for check3 in scope_list:
                                            if check3[1] == scopelist[2]:
                                                print(check3[1])
                                                scat = check3[0]
                                                for check4 in scope_list:
                                                    if check4[1] == scopelist[3]:
                                                        print(check4[1])
                                                        scat = check4[0]
                                                        for check5 in scope_list:
                                                            if check5[1] == scopelist[4]:
                                                                print(check5[1])
                                                                scat = check5[0]
                                                                for check6 in scope_list:
                                                                    if check6[1] == scopelist[5]:
                                                                        print(check6[1])
                                                                        scat = check6[0]
                                                                        count1 = 1
                                                                        for check7 in scope_list:
                                                                            if check7[1] == scopelist[6]:
                                                                                print(check7[1])
                                                                                scat = check7[0]
                                                                            scopename[i - 1] = scopename[i - 1].strip()
                                                                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], scat)
                                                                            print(sql2)
                                                                            print('exist')
                                                                            get_lcl(sql2)
                                                                            count = 1
                                                                            print(count)
                                                                            sname = subscope[i - 1] + '/' + scopename[
                                                                                i - 1]
                                                                            print(sname)
                                                                            sname = sname.strip()
                                                                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                                                                shotproj_id, scat, sname, keyword[i - 1],
                                                                                frames[i - 1], sap[i - 1],
                                                                                description[i - 1])
                                                                            print(sql)
                                                                            get_lcl2(sql)
                                                                            checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[6] = scopelist[6].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopelist[6], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(scopelist[6])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i - 1] = scopename[i - 1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname = sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

                    if len2 == 8:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        for check3 in scope_list:
                                            if check3[1] == scopelist[2]:
                                                print(check3[1])
                                                scat = check3[0]
                                                for check4 in scope_list:
                                                    if check4[1] == scopelist[3]:
                                                        print(check4[1])
                                                        scat = check4[0]
                                                        for check5 in scope_list:
                                                            if check5[1] == scopelist[4]:
                                                                print(check5[1])
                                                                scat = check5[0]
                                                                for check6 in scope_list:
                                                                    if check6[1] == scopelist[5]:
                                                                        print(check6[1])
                                                                        scat = check6[0]
                                                                        for check7 in scope_list:
                                                                            if check7[1] == scopelist[6]:
                                                                                print(check7[1])
                                                                                scat = check7[0]
                                                                                count1 = 1
                                                                                for check8 in scope_list:
                                                                                    if check8[1] == scopelist[7]:
                                                                                        print(check8[1])
                                                                                        scat = check8[0]
                                                                                        scopename[i - 1] = scopename[i - 1].strip(                                                                                      " ", "")

                                                                                    sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], scat)
                                                                                    print(sql2)
                                                                                    print('exist')
                                                                                    get_lcl(sql2)
                                                                                    count = 1
                                                                                    print(count)
                                                                                    sname = subscope[i - 1] + '/' + \
                                                                                            scopename[i - 1]
                                                                                    print(sname)
                                                                                    sname = sname.strip(                                                                                                                "")
                                                                                    sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                                                                        shotproj_id, scat, sname, keyword[i - 1],
                                                                                        frames[i - 1], sap[i - 1],
                                                                                        description[i - 1])
                                                                                    print(sql)
                                                                                    get_lcl2(sql)
                                                                                    checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[7] = scopelist[7].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopelist[7], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(scopelist[7])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i - 1] = scopename[i - 1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname = sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

                    if len2 == 9:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        for check3 in scope_list:
                                            if check3[1] == scopelist[2]:
                                                print(check3[1])
                                                scat = check3[0]
                                                for check4 in scope_list:
                                                    if check4[1] == scopelist[3]:
                                                        print(check4[1])
                                                        scat = check4[0]
                                                        for check5 in scope_list:
                                                            if check5[1] == scopelist[4]:
                                                                print(check5[1])
                                                                scat = check5[0]
                                                                for check6 in scope_list:
                                                                    if check6[1] == scopelist[5]:
                                                                        print(check6[1])
                                                                        scat = check6[0]
                                                                        for check7 in scope_list:
                                                                            if check7[1] == scopelist[6]:
                                                                                print(check7[1])
                                                                                scat = check7[0]
                                                                                for check8 in scope_list:
                                                                                    if check8[1] == scopelist[7]:
                                                                                        print(check8[1])
                                                                                        scat = check8[0]
                                                                                        count1 = 1
                                                                                        for check9 in scope_list:
                                                                                            if check9[1] == scopelist[8]:
                                                                                                print(check9[1])
                                                                                                scat = check9[0]
                                                                                            scopename[i - 1] = scopename[i - 1].strip(                                                                                          " ", "")
                                                                                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], scat)
                                                                                            print(sql2)
                                                                                            print('exist')
                                                                                            get_lcl(sql2)
                                                                                            count = 1
                                                                                            print(count)
                                                                                            sname = subscope[
                                                                                                        i - 1] + '/' + \
                                                                                                    scopename[i - 1]
                                                                                            print(sname)
                                                                                            sname = sname.strip(                                                                                          " ", "")
                                                                                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                                                                                shotproj_id, scat, sname,
                                                                                                keyword[i - 1],
                                                                                                frames[i - 1],
                                                                                                sap[i - 1],
                                                                                                description[i - 1])
                                                                                            print(sql)
                                                                                            get_lcl2(sql)
                                                                                            checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[8] = scopelist[8].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopelist[8], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(scopelist[8])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i - 1] = scopename[i - 1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id, scopename[i - 1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname = sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

                if scopelist[0] == 'Shot':
                    len2 = len(scopelist)
                    print(len2)
                    if len2 > 3:
                        # flash(f"Row {i}'s subscope length too long")
                        print("invalid2")
                        continue
                    count = 0
                    count1 = 0
                    count2 = 0

                    if len2 == 1:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                scopename[i - 1] = scopename[i - 1].strip()
                                sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(
                                    shotproj_id, scopename[i - 1], scat)
                                print(sql2)
                                print('exist')
                                get_lcl(sql2)
                                sname = subscope[i - 1] + '/' + scopename[i - 1]
                                print(sname)
                                sname = sname.strip()
                                sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                    shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                    description[i - 1])
                                print(sql)
                                get_lcl2(sql)
                                checktotal = checktotal + 1
                    if len2 == 2:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                count1 = 1
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        scopename[i - 1] = scopename[i - 1].strip()
                                        sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(
                                            shotproj_id, scopename[i - 1], scat)
                                        print(sql2)
                                        print('exist')
                                        get_lcl(sql2)
                                        count = 1
                                        print(count)
                                        sname = subscope[i - 1] + '/' + scopename[i - 1]
                                        print(sname)
                                        sname = sname.strip()
                                        sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                            shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                            description[i - 1])
                                        print(sql)
                                        get_lcl2(sql)
                                        checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[1] = scopelist[1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(
                                shotproj_id, scopelist[1], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(
                                scopelist[1])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i - 1] = scopename[i - 1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(
                                shotproj_id, scopename[i - 1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname = sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

                    if len2 == 3:
                        sql = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
                        scope_list = get_lcl(sql)
                        for check in scope_list:
                            if check[1] == scopename[i - 1]:
                                count2 = 1
                        if count2 == 1:
                            print("Invalid2")
                            continue
                        for check in scope_list:
                            if check[1] == scopelist[0]:
                                print(check[1])
                                scat = check[0]
                                for check2 in scope_list:
                                    if check2[1] == scopelist[1]:
                                        print(check2[1])
                                        scat = check2[0]
                                        count1 = 1
                                        for check3 in scope_list:
                                            if check3[1] == scopelist[2]:
                                                print(check3[1])
                                                scat = check3[0]
                                                scopename[i - 1] = scopename[i - 1].strip()
                                                sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(
                                                    shotproj_id, scopename[i - 1], scat)
                                                print(sql2)
                                                print('exist')
                                                get_lcl(sql2)
                                                count = 1
                                                print(count)
                                                sname = subscope[i - 1] + '/' + scopename[i - 1]
                                                print(sname)
                                                sname = sname.strip()
                                                sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                                    shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                                    description[i - 1])
                                                print(sql)
                                                get_lcl2(sql)
                                                checktotal = checktotal + 1
                        if count == 0 and count1 == 1:
                            scopelist[2] = scopelist[2].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(
                                shotproj_id, scopelist[2], scat)
                            get_lcl(sql2)
                            print(sql2)
                            print(count)
                            sql = "SELECT category_id FROM scope_category WHERE category_name = '{0}'".format(
                                scopelist[2])
                            l = get_lcl(sql)
                            print(sql)
                            print(l[0][0])
                            scopename[i - 1] = scopename[i - 1].strip()
                            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(
                                shotproj_id, scopename[i - 1], l[0][0])
                            print(sql2)
                            get_lcl2(sql2)
                            sname = subscope[i - 1] + '/' + scopename[i - 1]
                            print(sname)
                            sname = sname.strip()
                            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}',{4},'{5}','{6}')".format(
                                shotproj_id, scat, sname, keyword[i - 1], frames[i - 1], sap[i - 1],
                                description[i - 1])
                            print(sql)
                            get_lcl2(sql)
                            checktotal = checktotal + 1

            print(i)
            print(checktotal)
            if i != checktotal:
                flash(f"{checktotal} Rows added , {i - checktotal} Rows not added")






            # sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,thumbnail,frame_count,SAP,scope_description) VALUES({0},{1},'{2}','{3}','{4}',{5},'{6}','{7}')".format(70, scid, sname, keyword, thumb, frames, sap, desc)
            # print(sql)
            # get_lcl2(sql)
            # sname2 = sname.rsplit('/', 1)
            # sname3 = sname2[1]
            # print(sname3)
            # sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(70,sname3,scid)
            # print(sql2)
            # get_lcl2(sql2)
        if(sid):
            sid = sid.rsplit('/', 1)
            scid = sid[0]
            ssid = sid[1]
            sname = scategory + sname;
            print(sname)
            print(keyword)
            print(thumb)
            print(frames)
            print(sap)
            print(desc)
            print(sid)
            print(scid)
            print(scopeattach)
            sname = sname.strip()
            if (scopeattach):
                sql = "SELECT proj_code FROM project_settings WHERE proj_id = '{0}'".format(shotproj_id)
                proj_code = get_lcl(sql)[0][0]
                filename = secure_filename(scopeattach.filename)
                # Save Thumb File
                filepath = '//san/10_TEMP_FILES/' + proj_code + '/DB/PFXDB/SCOPES/THUMBNAILS'
                print(filepath)
                proj_code.save(os.path.join(filepath, filename))
                proj_code.save(os.path.join('c:\\temp\\', filename))
                newscopeattach = filepath + filename
            sql = "INSERT into scope (proj_id,scope_category_id,scope_name,scope_keyword_id,thumbnail,frame_count,SAP,scope_description,thumbnail) VALUES({0},{1},'{2}','{3}','{4}',{5},'{6}','{7}')".format(shotproj_id,scid,sname,keyword,thumb,frames,sap,desc,newscopeattach)
            print(sql)
            # get_lcl2(sql)
            sname2 = sname.rsplit('/', 1)
            sname3 = sname2[1]
            sname3 = sname3.strip()
            sql2 = "INSERT into scope_category (projid,category_name,super_category) VALUES({0},'{1}',{2})".format(shotproj_id,sname3,scid)
            print(sql2)
            get_lcl2(sql2)
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        type_convert = {'ROT': '2d_roto', '2D_ELEMENT': '2d_element', 'PNT': '2d_paint',
                        'MATTEPAINT': 'art_mattepaint',
                        'CONCEPT_ART': 'concept_art', '2D_LAYOUT': '2d_layout', 'SLAPCOMP': '2d_slapcomp',
                        'PRECOMP': '2d_precomp', 'COMP': '2d_out', '2D_TEST': '2d_test',
                        'MATCHMOVE': '3d_matchmove',
                        'MODEL': '3d_model', 'HDRI': '3d_hdri', 'RIGGING': '3d_rigging', 'SHADING': '3d_shading',
                        'LOOKDEV': '3d_lookdev', '3D_TEST': '3d_test', 'LIGHTING': '3d_lighting',
                        'DYNAMICS': '3d_dynamics',
                        'SHOTSCULPT': '3d_shotsculpt', '3D_ANIMATION': '3d_animation', 'TEXTURING': '3d_texture',
                        'PREVIZ': 'pre_visualisation', 'PIPE_TEST': 'pipe_test', 'PIPE_OUT': 'pipe_out',
                        '3D_LAYOUT': '3d_layout'}
        userLogin = session.get('username')
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        result = get_task_details(userLogin)
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        details = get_lcl(sql)
        dept = details[0][0]
        access = details[0][1]
        if (access == 'low' or access == 'max' or access == 'high' or (access == 'min' and dept == 11) or (dept == 20)):
            sql = "select proj_id,thumbnail,scope_category_id,scope_name,scope_description,SAP,production_status,scope_id from scope where proj_id={0}".format(shotproj_id)
            proj_list = get_lcl(sql)
            proj_dict = []
            for j in proj_list:
                # print(j[3])
                detail = j[3].rsplit('/', 1)
                name = detail[1]
                category = detail[0]
                # sql = "select proj_id,thumbnail,scope_category_id,scope_name,scope_description,SAP,production_status,scope_id from scope where proj_id={0}"
                # proj_name = get_lcl(sql)
                try:
                    # print(j[i])
                    if os.path.exists(j[i]):
                        scopethumb = os.path.basename(j[i])
                        global newfscope
                        newfscope = "C:/Users/demo/Desktop/login/static/tempfiles/" + scopethumb
                        shutil.copy(j[i], newfscope)
                        print(scopethumb)
                    else:
                        scopethumb = "default.jpg"
                except:
                    scopethumb = "default.jpg"
                k = dict(proj_id=j[0], thumbnail=scopethumb, category=category, name=name, description=j[4], SAP=j[5], status=j[6], scope_id=j[7] , c_id = j[2])
                print(k)
                proj_dict.append(k)
            sql2 = "SELECT scope_id,task_type_name,assigned_to,EMD,CMD,task_status,latest_int_version,latest_client_version,bid_end,task_id,bid_start,frame_start,frame_end FROM `task` WHERE proj_id= {0}".format(shotproj_id)
            sql3 = "SELECT DISTINCT scope_id,task_type_name FROM `task` WHERE proj_id= {0}".format(shotproj_id)
            unique_list = get_lcl(sql3)


            for g in range(len(unique_list)):
                unique_list[g] = list(unique_list[g])
                # print(unique_list[g][1])
                try:
                    unique_list[g][1] = type_convert[unique_list[g][1]]
                except:
                    unique_list[g][1] = unique_list[g][1]
            task_list = get_lcl(sql2)
            task_dict = []
            # print(unique_list)
            for j in task_list:
                # print(j[1])
                notesdefaults = []
                attachdefaults = []
                task_type_short = j[1]
                try:
                    task_type_short = type_convert[task_type_short]
                except:
                    pass
                # j[1] = type_convert[j[1]]
                sql2 = "SELECT scope_name FROM `scope` WHERE scope_id = '{0}'".format(j[0])
                scopenameshot = get_lcl(sql2)
                # print(scopenameshot)
                sql2 = "SELECT firstname FROM `artist` WHERE artist_id = '{0}'".format(j[2])
                artistname = get_lcl(sql2)
                # print(artistname)
                sql = "SELECT publish_id from publish_q where task_id={0}".format(j[9])
                pubid = get_lcl(sql)
                sql = "SELECT thumbnail from publish_q where task_id={0}".format(j[9])
                pubthumb = get_lcl(sql)
                # print(pubthumb)
                try:
                    # print(pubthumb[0][0])
                    pubthumb[0] = list(pubthumb[0])
                    if os.path.exists(pubthumb[0][0]):
                        filenamethumb = os.path.basename(pubthumb[0][0])
                        global newfthumb
                        newfthumb = "C:/Users/demo/Desktop/login/static/tempfiles/" + filenamethumb
                        shutil.copy(pubthumb[0][0], newfthumb)
                        # print(filenamethumb)
                    else:
                        filenamethumb = ""
                except:
                    filenamethumb = ""
                # print(filenamethumb)
                # print("pubid",pubid)

                if(pubid):
                    for i in pubid:
                        # print(i[0])
                        sql2 = "SELECT notes,reviewer_name,int_version,note_id,attachment FROM `notes` WHERE publish_id = '{0}'".format(i[0])
                        versionnotes = get_lcl(sql2)
                        if(versionnotes):
                            # print(versionnotes)
                            for i in range(len(versionnotes)):
                                versionnotes[i] = list(versionnotes[i])
                                if os.path.exists(versionnotes[i][4]):
                                    filename = os.path.basename(versionnotes[i][4])
                                    global newftask
                                    newftask = "D:/webmodules/login/static/tempfiles/" + filename
                                    shutil.copy(versionnotes[i][4], newftask)
                                else:
                                    filename = ""
                                versionnotes[i][4] = filename
                        if(versionnotes):
                            notesdefaults.append(versionnotes)
                        try:
                            sql2 = "SELECT file_id , file_path FROM `file` WHERE publish_id = '{0}' AND int_version = '{1}'".format(i[0] , j[6])
                            # print(sql2)
                            versionattach = get_lcl(sql2)
                            # print("versionattach", versionattach)
                            for k in range(len(versionattach)):
                                # print(k)
                                # print('Length :', len(versionattach))
                                versionattach[k] = list(versionattach[k])
                                # print("versionttach[k]",versionattach[k])
                                # print('Path : ' , versionattach[k][1])

                                if os.path.exists(versionattach[k][1]) and versionattach[k][1].split('.')[-1] == 'mov':
                                    # print('Inside path')
                                    filename = os.path.basename(versionattach[k][1])
                                    global newftask2
                                    newftask2 = "D:/final/login/static/tempfiles/" + filename
                                    # shutil.copy(versionattach[k][1], newftask2)
                                else:
                                    # print('Inside Else')
                                    filename = ""
                                versionattach[k].append(filename)
                                splits = versionattach[k][1].split('/')
                                versionattach[k].append(splits[-3] + '-' + splits[-2]+ '-' + splits[-1])
                            # print("versionattach", versionattach)
                            if(versionattach):
                                attachdefaults.append(versionattach)

                        except:
                            pass
                            # print("publishid",i)

                # if  (scopenameshot and artistname):
                #     sql2 = "SELECT notes,reviewer_name,int_version,note_id FROM `notes` WHERE proj_name = 'tactic_development' AND scope_name = '{0}' AND type_name = '{1}' AND  artist_name = '{2}'".format(
                #         scopenameshot[0][0], task_type_short, artistname[0][0])
                #     print(sql2)
                #     notesshot = get_lcl(sql2)
                #     print(notesshot)
                #     if(notesshot):
                #         for i in notesshot:
                #             print('I', i)
                #         notesdefault = notesshot
                # print("notesdefaults", notesdefaults)
                # print(j[6],"attachdefaults", attachdefaults)
                k = dict(scope_id=j[0], task=task_type_short, assigned=j[2], emd=j[3], cmd=j[4], status=j[5], intversion=j[6], clientversion=j[7], due=j[8] , notes = notesdefaults , taskid = j[9] , start = j[10] , attach = attachdefaults , thumb = filenamethumb , startframe = j[11] , endframe = j[12])
                task_dict.append(k)
            l = len(task_dict)
            sql3 = "SELECT category_id,category_name,super_category FROM `scope_category` WHERE projid = {0}".format(shotproj_id)
            scope_list = get_lcl(sql3)
            scope_dict = []
            for j in scope_list:
                k = dict(c_id=j[0], c_name=j[1], sc_id=j[2])
                scope_dict.append(k)
            return render_template ("shot.html", proj_dict=proj_dict, task_dict=task_dict, scope_dict=scope_dict,l=l,unique_list = unique_list)
        else:
            return render_template("No_access.html")

@app.route("/modal", methods=['GET','POST'])
def modal():
    if request.method == 'POST':
        data = request.get_json()
        result = data['result']
        taskID = get_task_id(result['project'], result['scope'], result['task'], result['artist'])
        pubID = get_publish_id(taskID)
        print(pubID, taskID)
        version_dict = get_pfxdb_version(pubID)
        return jsonify(versions=version_dict)






@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route("/setting")
def setting():
    if not session.get('logged_in'):
        return home()
    else:
        username = session.get('username')
        return render_template("setting.html", result=username)


@app.route("/changPasword", methods=['POST'])
def changPasword():
    if not session.get('logged_in'):
        return home()
    else:
        username = session.get('username')
        sql = "SELECT password,salt from artist where login = '{0}'".format(username)
        try:
            paswd = get_all(sql)[0]
            key_select = paswd[1].encode()
            encripted = paswd[0].encode()
            f = Fernet(key_select)
            password = f.decrypt(encripted)
            if request.form['currentpwd'] == password.decode():
                if request.form['newpwd'] == request.form['retyppwd']:
                    password_provided = request.form['newpwd'].encode()
                    key = Fernet.generate_key()
                    f = Fernet(key)
                    token = f.encrypt(password_provided)
                    salt = key.decode()
                    passcode = token.decode()
                    try:
                        # print(passcode, salt, username)
                        sql = "UPDATE `artist` SET `password`= '{0}',`salt`='{1}' WHERE `login` = '{2}'".format(
                            passcode, salt, username)
                        paswd = dbconect(sql)
                        flash('Update Successfully!')
                        return setting()
                    except:
                        flash('Error in Update!')
                        return setting()
                else:
                    flash('Password Mismatch!')
                    return setting()
            else:
                flash('Wrong Password!')
                return setting()
        except:
            flash('Wrong Username!')
            return changPasword()


def get_task_typeID(task_name):
    '''getting task type ID if task name is given'''
    sql = "SELECT task_status_id from task_status where task_status_name = '{0}'".format(task_name.upper())
    res = dbconect(sql)[0]
    return res


def update_status(task_id, task_status):
    '''updating task_id status'''
    taskIypeID = get_task_typeID(task_status)
    sql = "UPDATE task SET task_status={0} WHERE task_id={1}".format(taskIypeID, task_id)
    try:
        res = dbconect(sql)
        return True
    except:
        return False


def check_workHour(task_id):
    '''checth last calculated work hour of the project'''

    sql = "SELECT work_hours from task_work_hrs where task_id={0}".format(task_id)
    res = dbconect(sql)
    current_stamp = datetime.now()  # get current timestamp
    if res == []:
        sql = "INSERT into task_work_hrs(task_id,start_time,processed_time) VALUES({0},'{1}','{2}')".format(task_id,
                                                                                                            current_stamp,
                                                                                                            current_stamp)
        res1 = dbconect(sql)
        res = "00:00:00"
    else:
        pass
    return res[0]


def get_workHour(task_id):
    '''checth last calculated work hour of the project'''
    sql = "SELECT work_hours from task_work_hrs where task_id={0}".format(task_id)
    res = dbconect(sql)
    current_stamp = datetime.now()  # get current timestamp
    if res == []:
        res = ("00:00:00", '0')
    else:
        sql = "SELECT processed_time from task_work_hrs where task_id={0}".format(task_id)
        res1 = dbconect(sql)
        res = (res[0], res1[0])
    return res


@app.route("/pause_calc", methods=['POST'])
def pause_calc():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        userLogin = session.get('username')
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        result = get_task_details(userLogin)
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        details = get_lcl(sql)
        dept = details[0][0]
        access = details[0][1]
        print(access)
        if (access == 'min'):
            print(access)
        if ((dept == 11 and ( access == 'high' or access =='max' or access =='low' )) or dept ==20):
            '''end point to post if person clicks meeting or break'''
            from datetime import datetime
            data = request.get_json()
            result = data['result']
            task_id = result['task_id']
            status = result['opt']
            update_status(int(task_id), status)
            if status == 'PAUSE':
                curr_time = datetime.now()
                sql = "UPDATE task_work_hrs SET stop_time='{0}' where task_id='{1}'".format(curr_time, task_id)
                res = dbconect(sql)
                sql1 = "SELECT stop_time,processed_time from task_work_hrs where task_id='{0}'".format(task_id)
                res = get_all(sql1)[0]
                duration = (res[0] - res[1]).total_seconds()
                temp = check_workHour(task_id)
                if temp != "00:00:00":
                    h, m, s = temp.split(":")
                    time = int(h) * 3600 + int(m) * 60 + int(s)
                else:
                    time = 0

                overall = time + duration
                mins = divmod(overall, 60)
                hrs = divmod(mins[0], 60)
                print('check')
                work_hrs = str(int(hrs[0])) + ':' + str(int(hrs[1])) + ':' + str(int(mins[1]))
                sql2 = "UPDATE task_work_hrs SET work_hours='{0}' where task_id='{1}'".format(work_hrs, task_id)
                res = dbconect(sql2)

            elif status == 'WIP':
                curr_time = datetime.now()

                sql = "UPDATE task_work_hrs SET processed_time='{0}' where task_id='{1}'".format(curr_time, task_id)
                res = dbconect(sql)
            return '', 200

        else:
            return render_template("No_access.html")



@app.route("/status_change", methods=['POST'])
def status_change():
    '''end point to post changes'''
    if request.method == 'POST':

        data = request.get_json()
        result = data['result']
        task_id = result['task_id']
        status = result['opt']
        count_statuses = ['WIP']
        stop_statuses = ['PAUSE', 'HOLD', 'REVIEW']

        if status.upper() in count_statuses:
            curr_time = datetime.now()
            sql = "UPDATE task_work_hrs SET processed_time='{0}' where task_id='{1}'".format(curr_time, task_id)
            res = dbconect(sql)

        elif status.upper() in stop_statuses:
            curr_time = datetime.now()
            sql = "UPDATE task_work_hrs SET stop_time='{0}' where task_id='{1}'".format(curr_time, task_id)
            res = dbconect(sql)
            sql1 = "SELECT stop_time,processed_time from task_work_hrs where task_id='{0}'".format(task_id)
            res = get_all(sql1)[0]
            duration = (res[0] - res[1]).total_seconds()
            temp = check_workHour(task_id)
            if temp != "00:00:00":
                h, m, s = temp.split(":")
                time = int(h) * 3600 + int(m) * 60 + int(s)
            else:
                time = 0

            overall = time + duration
            mins = divmod(overall, 60)
            hrs = divmod(mins[0], 60)
            work_hrs = str(int(hrs[0])) + ':' + str(int(hrs[1])) + ':' + str(int(mins[1]))
            sql2 = "UPDATE task_work_hrs SET work_hours='{0}' where task_id='{1}'".format(work_hrs, task_id)
            res = dbconect(sql2)

        workHourCheck = check_workHour(task_id)
        time = workHourCheck.split(':')
        success = update_status(task_id, status)
        # print(result,time)
        return jsonify(time=time)


@app.route("/timer", methods=['POST'])
def timer_display():
    '''end point to get work hours to display'''
    if request.method == 'POST':
        data = request.get_json()
        result = data['result']
        task_id = result['task_id']
        # print(result)
        # return jsonify(success=success)
        workHourCheck = check_workHour(task_id)
        time = workHourCheck.split(':')
        return jsonify(time=time)


@app.route("/stopwatch", methods=['POST'])
def stopwatch():
    '''end point to post changes'''
    if request.method == 'POST':
        data = request.get_json()
        result = data['result']
        task_id = result['task_id']
        status = result['opt']
        workHourCheck = get_workHour(task_id)
        time = workHourCheck[0].split(':')
        if workHourCheck[1] != '0':
            print(workHourCheck[1])
            current_stamp = datetime.now()
            print(current_stamp)
            tdelta = current_stamp - workHourCheck[1]
            print(workHourCheck[0])
            inSecs = get_sec(workHourCheck[0])
            print('WH', inSecs)
            seconds = tdelta.days * 24 * 3600 + tdelta.seconds
            print(seconds)
            total = int(inSecs) + int(seconds)
            print(total)
        else:
            total = 0
        print(result, time)
        return jsonify(time=time, seconds=total)


def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


@app.route("/nproj")
def newProject():
    if not session.get('logged_in'):
        return home()
    elif session['logged_in'] == False:
        return home()
    else:

        userLogin = session.get('username')
        sql = "SELECT dep_id, access from artist where login = '{0}'".format(userLogin)
        result = get_task_details(userLogin)
        artID = get_artistID(userLogin)
        bid_details = collect_bidDetails(artID)
        details = get_lcl(sql)
        dept = details[0][0]
        access = details[0][1]
        print(access)

        if (dept == 11 and access =='low'):
            username = session.get('username')
            form = MyForm()
            return render_template("projnew.html", form=form)
        else:
            return render_template("No_access.html")



@app.route("/calendar")
def calendar():
    return render_template("calendar.html")


def validate_status(username):
    # return 0 if task is in WIP and 1 if no tasks are in WIP
    artID = get_artistID(username)
    sql = "SELECT task_id from task where assigned_to = {0} and task_status=19".format(artID)
    res = dbconect(sql)
    print(res)
    if res != []:
        return 0
    else:
        return 1

@app.route("/newproject", methods=['POST'])
def projectDetails():
    if request.method == 'POST':
        pjName = request.form.get('code')
        pjThumb = request.form.get('thumbfile')
        pjresolution = request.form.get('resolution')
        pjframerate = request.form.get('framerate')
        pjinputdate = request.form.get('inputdate')
        pjoutputdate = request.form.get('outputdate')
        pjtwodslate = request.form.get('twodslate')
        pjthreedslate = request.form.get('threedslate')
        pjtwodailymacro = request.form.get('twodailymacro')
        pjthredailymacro = request.form.get('thredailymacro')
        pjlineproducer = request.form.get('lineproducer')
        pjtwodcoordinator = request.form.get('twodcoordinator')
        pjthredcoordinator = request.form.get('thredcoordinator')
        pjrotocoordinator = request.form.get('rotocoordinator')
        pjpaintcoordinator = request.form.get('paintcoordinator')
        pjrotosupervisor = request.form.get('rotosupervisor')
        pjpaintsupervisor = request.form.get('paintsupervisor')
        pjprojectmanager = request.form.get('projectmanager')
        pjvfxhead = request.form.get('vfxhead')
        pjvfxsupervisor = request.form.get('vfxsupervisor')
        pj2dhead = request.form.get('2dhead')
        pjartdirector = request.form.get('artdirector')
        pjcgsupervisor = request.form.get('cgsupervisor')
        pjociofile = request.form.get('ociofile')
        pjbidstart = request.form.get('bidstart')
        pjbidend = request.form.get('bidend')
        pjinformat = request.form.get('informat')
        pjoutformat = request.form.get('outformat')
        pjcodec = request.form.get('codec')
        pjmovresolution = request.form.get('movresolution')
        pjcategory = request.form.get('pjcategory')
        pjstatus = request.form.get('pjstatus')
        pjtechdocument = request.form.get('pjtechdocument')
        sql = "INSERT INTO project_settings" \
              "(proj_code, thumbnail, resolution,frame_rate, input_date," \
              " output_date, slate_2d, slate_3d, daily_macro_2d, daily_macro_3d," \
              " line_producer, coordinator_3d, coordinator_2d,roto_coordinator," \
              "paint_coordinator,  roto_supervisor, paint_supervisor, project_manager," \
              " vfx_head, vfx_supervisor, head_2d, art_dir, cg_supervisor,OCIO_path," \
              " bid_start_date, bid_end_date,input_format, output_format, movie_codec," \
              " movie_resolution,category,proj_status_id, tech_document) " \
              "VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}'," \
              "'{11}','{12}','{13}','{14}','{15}','{16}','{17}','{18}','{19}','{20}'," \
              "'{21}','{22}','{23}','{24}','{25}','{26}','{27}','{28}','{29}','{30}'," \
              "'{31}')".format(pjName,pjThumb,pjresolution,pjframerate,pjinputdate,pjoutputdate,
                               pjtwodslate,pjthreedslate,pjtwodailymacro,pjthredailymacro,
                               pjlineproducer,pjthredcoordinator,pjtwodcoordinator,
                               pjrotocoordinator,pjpaintcoordinator,pjrotosupervisor,
                               pjpaintsupervisor,pjprojectmanager,pjvfxhead,pjvfxsupervisor,
                               pj2dhead,pjartdirector,pjcgsupervisor,pjociofile,pjbidstart,
                               pjbidend,pjinformat,pjoutformat,pjcodec,pjresolution,pjcategory,pjstatus,pjtechdocument)
        get_lcl(sql)
@app.route("/validate", methods=['POST'])
def validate():
    '''don't logout if there are tasks in WIP'''
    if request.method == 'POST':
        data = request.get_json()
        result = data['result']
        success = validate_status(result)
        return jsonify(success=success)


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run('0.0.0.0', 100, debug=True)
