from flask import Flask, render_template, request, jsonify, flash, redirect, session
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms.fields import DateField
import os
import random
from pymysql import connect
import datetime
from datetime import date , timedelta ,datetime
import json
import calendar
app = Flask(__name__)

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

@app.route('/',methods=['GET', 'POST'])
def scheduler():
	if request.method == 'POST':
		scale = request.form.get('scale')
		start = request.form.get('start')
		end = request.form.get('end')
		artsist = request.form.get('searchartist')
		prev = request.form.get('prev')
		today = request.form.get('today')
		nextd = request.form.get('next')
		print('prev', prev)
		print('nextd', nextd)
		print('today', today)
		print('scale', scale)
		print('Start', start)
		print('end', end)
		if scale == '1':
			# date_str = datetime.today().strftime('%Y-%m-%d')
			date_obj = datetime.today().strftime('%Y-%m-%d')
			start_of_week = datetime.today() - timedelta(days=datetime.today().weekday())  # Monday
			end_of_week = start_of_week + timedelta(days=6)  # Sunday
			start_date = start_of_week.strftime('%Y-%m-%d')
			end_date = end_of_week.strftime('%Y-%m-%d')
			duration = 7
			print(start_of_week)
			print(end_of_week)
		elif scale == '2':
			print('Month')
			temp_var = calendar.monthrange(int(datetime.now().strftime('%Y')), int(datetime.now().strftime('%m')))
			duration = temp_var[1]
			start_date = '{0}-{1}-1'.format(datetime.now().strftime('%Y'), datetime.now().strftime('%m'))
			end_date = '{0}-{1}-{2}'.format(datetime.now().strftime('%Y'), datetime.now().strftime('%m'),duration)
			print(start_date)
			print(end_date)
		else:
			if prev:
				duration = int(prev.split(",")[2])
				if duration >= 8:
					scale = 2
					print('Scale :', scale)
				if scale == 2:
					temp_date = prev.split(",")[0]
					temp_month = int(temp_date.split('-')[1])
					temp_year = int(temp_date.split('-')[0])
					if temp_month == '1':
						temp_var = calendar.monthrange(temp_year-1, temp_month+11)
						duration = temp_var[1]
						start_date = '{0}-{1}-1'.format(temp_year-1, temp_month+11)
						end_date = '{0}-{1}-{2}'.format(temp_year-1, temp_month+11, duration)
					else:
						temp_var = calendar.monthrange(temp_year, temp_month - 1)
						duration = temp_var[1]
						start_date = '{0}-{1}-1'.format(temp_year, temp_month - 1)
						end_date = '{0}-{1}-{2}'.format(temp_year, temp_month - 1, duration)
				else:
					duration = int(prev.split(",")[2])
					start_date = datetime.strptime(prev.split(",")[0], '%Y-%m-%d').date() - timedelta(days=duration)
					end_date = start_date + timedelta(days=duration)
			elif nextd:
				duration = int(nextd.split(",")[2])
				if duration >= 8:
					scale = 2
					print('Scale :', scale)
				if scale == 2:
					temp_date = nextd.split(",")[0]
					temp_month = int(temp_date.split('-')[1])
					temp_year = int(temp_date.split('-')[0])
					if temp_month == '12':
						temp_var = calendar.monthrange(temp_year + 1, temp_month - 11)
						duration = temp_var[1]
						start_date = '{0}-{1}-1'.format(temp_year + 1, temp_month - 11)
						end_date = '{0}-{1}-{2}'.format(temp_year + 1, temp_month - 11,
														duration)
					else:
						temp_var = calendar.monthrange(temp_year, temp_month + 1)
						duration = temp_var[1]
						start_date = '{0}-{1}-1'.format(temp_year, temp_month + 1)
						end_date = '{0}-{1}-{2}'.format(temp_year, temp_month + 1,
														duration)
				else:
					duration = int(nextd.split(",")[2])
					start_date = datetime.strptime(nextd.split(",")[0], '%Y-%m-%d').date() + timedelta(days=duration)
					end_date = start_date + timedelta(days=duration)
			elif today:
				duration = int(today.split(",")[2])
				start_date = datetime.today().strftime('%Y-%m-%d')
				end_date = datetime.today() + timedelta(days=duration)
				end_date = end_date.strftime('%Y-%m-%d')
			else:
				start_date = datetime.strptime(start, '%Y-%m-%d').date()
				print(start_date)
				end_date = datetime.strptime(end, '%Y-%m-%d').date()
				print(end_date)
				# duration = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days()
				duration = (end_date - start_date).days + 1
	else:
		start_date = datetime.today().strftime('%Y-%m-%d')
		end_of_week = datetime.today() + timedelta(days=6)
		end_date = end_of_week.strftime('%Y-%m-%d')
		duration = 7
		print(start_date)
		print(end_date)
	sql = "SELECT dep_id, dep_name FROM department WHERE dep_id not in ('4','5','7','8','15','14','16','17','18')"
	alDept = get_all(sql)
	sql = "SELECT proj_id, proj_code FROM project_settings"
	alProj = get_all(sql)
	alDept_id = []        
	final = []
	# print(alDept)
	# print(alDept_id)
	for i in alDept:
	    alDept_id.append(i[0])
	dep_dict = dict(alDept)
	projDict = dict(alProj)
	# print(dep_dict)
	# Get user details from artist table based on department .
	# only getting the active users list.
	for j in alDept_id:
	    myDict = {}
	    sql = "SELECT artist_id, login FROM artist WHERE dep_id = {0} AND access != 'none'".format(j)
	    artist_details = get_all(sql)
	    # print('artist_details : ', len(artist_details))
	    # print(artist_details)
	    # print('Department : ', dep_dict[j])
	    # Get all task details assigned to an artist.
	    dept_stDate = []
	    dept_enDate = []
	    alArtist_tasks = []
	    for k in artist_details:
	        sql = "SELECT proj_id, scope_id, type_id, task_type_name, FMD, EMD, CMD, latest_int_version, task_status, bid_start, bid_end FROM task WHERE assigned_to = {0} and (bid_start between '{1}' and '{2}' or bid_end between '{1}' and '{2}')".format(int(k[0]), start_date, end_date)
	        task_details = get_all(sql)
	        temp_stDate = []
	        temp_enDate = []
	        artist_tasks = []
	        artist_emd = []
	        artist_cmd = []
	        for l in task_details:            
	            temp_task = []
	            temp_stDate.append(l[9])
	            temp_enDate.append(l[10])
	            temp_task.append(projDict[l[0]])
	            # sql = "SELECT scope_name FROM scope WHERE scope_id = {0}".format(l[1])
	            temp_task.append(l[9])
	            temp_task.append(l[10])
	            temp_task.append(l[5])
	            temp_task.append(l[6])
	            artist_tasks.append(temp_task)
	            if l[5] != None and l[5] != '':
	                artist_emd.append(int(l[5]))
	            else:
	                artist_emd.append(0)
	            # print('CMD : ', l[6], ' - ', l[1])
	            if l[6] != None and l[5] != '':
	                artist_cmd.append(int(l[6]))
	            else:
	                artist_cmd.append(0)
	        if temp_stDate != [] and temp_enDate !=[]:
	            # task without start date and end date are not included
	            dept_stDate.append(min(temp_stDate))
	            dept_enDate.append(max(temp_enDate))
	            alArtist_tasks.append([k[1]+'-'+str(sum(artist_emd))+'-'+str(sum(artist_cmd)), min(temp_stDate), max(temp_enDate), artist_tasks])
	        else:
	            alArtist_tasks.append([k[1], '', '', ''])
	    if dept_stDate != [] and dept_enDate != []:
	        myDict['Dept'] = dep_dict[j] + '-dept'
	        myDict['Sart_date'] = min(dept_stDate)
	        myDict['End_date'] = max(dept_enDate)
	        myDict['Artist'] = alArtist_tasks
	        final.append(myDict)
	    else:
	        myDict['Dept'] = dep_dict[j] + '-dept'
	        myDict['Sart_date'] = ''
	        myDict['End_date'] = ''
	        myDict['Artist'] = alArtist_tasks
	        final.append(myDict)
	data = final
	print(data)
	return render_template('scheduler.html' , data = data, st=start_date, duration=duration)

@app.route('/updatescheduleradd1',methods=['GET', 'POST'])
def updatescheduleradd1():
	print('INside')
	if request.method == 'POST':
		data = request.get_json()
		print(data)

@app.route('/updatescheduleredit',methods=['GET', 'POST'])
def updatescheduleredit():
	if request.method == 'POST':
		ajaxdata = request.get_json()
		print(ajaxdata)

@app.route('/updateschedulerdelete',methods=['GET', 'POST'])
def updateschedulerdelete():
	if request.method == 'POST':
		ajaxdata = request.get_json()
		print(ajaxdata)
		
if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)


