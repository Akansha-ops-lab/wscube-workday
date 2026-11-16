import sqlite3
from datetime import date, datetime
import streamlit as st

DB='attendance.db'

def conn():
    c=sqlite3.connect(DB, check_same_thread=False)
    c.execute('''CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY, employee TEXT, work_date TEXT, mode TEXT, check_in TEXT, check_out TEXT, report TEXT, status TEXT DEFAULT 'open', submitted_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, entry_id INTEGER, start_time TEXT, end_time TEXT, task TEXT, outcome TEXT)''')
    return c

def get_today(c, employee):
    return c.execute('SELECT * FROM entries WHERE employee=? AND work_date=?',(employee,str(date.today()))).fetchone()

st.set_page_config(page_title='WsCube Workday', page_icon='🕒', layout='wide')
st.title('WsCube Tech | Workday & Daily Report')
st.caption('Clock in, record work, and submit a locked end-of-day report.')
c=conn()
with st.sidebar:
    st.subheader('Employee access')
    employee=st.text_input('Employee name', value='').strip()
    mode=st.selectbox('Work location', ['Office','Work from home'])
    st.caption('Prototype only: replace name entry with company SSO or employee login before launch.')
if not employee:
    st.info('Enter your name to open today’s workday.'); st.stop()
entry=get_today(c, employee)
if not entry:
    if st.button('Clock in', type='primary'):
        c.execute('INSERT INTO entries(employee,work_date,mode,check_in) VALUES(?,?,?,?)',(employee,str(date.today()),mode,datetime.now().isoformat(timespec='minutes'))); c.commit(); st.rerun()
    st.warning('You are not clocked in today. Clock in to begin.')
    st.stop()
_,_,work_date,work_mode,check_in,check_out,report,status,submitted=entry
m1,m2,m3=st.columns(3); m1.metric('Status',status.title()); m2.metric('Clock in',check_in[11:16]); m3.metric('Work mode',work_mode)
if status=='locked':
    st.success(f'Report submitted and locked at {submitted[11:16] if submitted else ""}.')
    st.subheader('Submitted report'); st.write(report or '—')
    tasks=c.execute('SELECT start_time,end_time,task,outcome FROM tasks WHERE entry_id=?',(entry[0],)).fetchall()
    if tasks: st.dataframe(tasks, use_container_width=True, hide_index=True, column_config={'start_time':'From','end_time':'To','task':'Work item','outcome':'Outcome'})
    st.info(f'Clock out: {check_out[11:16]} · Employee edits are disabled after submission.')
else:
    st.subheader('Work log')
    st.caption('Add one row per focused work block. This report is required to clock out.')
    task_rows=st.data_editor([{'From':'09:00','To':'10:00','Work item':'','Outcome':''}], num_rows='dynamic', use_container_width=True, key='tasks')
    report=st.text_area('Daily summary / handover', placeholder='Summarize key work, blockers, and handover notes…', height=110)
    if st.button('Submit report & clock out', type='primary'):
        clean=[r for r in task_rows if str(r.get('Work item','')).strip()]
        if not clean or not report.strip(): st.error('Add at least one work item and a daily summary before clocking out.')
        else:
            now=datetime.now().isoformat(timespec='minutes')
            c.execute('UPDATE entries SET check_out=?,report=?,status="locked",submitted_at=? WHERE id=?',(now,report.strip(),now,entry[0]))
            c.execute('DELETE FROM tasks WHERE entry_id=?',(entry[0],))
            c.executemany('INSERT INTO tasks(entry_id,start_time,end_time,task,outcome) VALUES(?,?,?,?,?)',[(entry[0],str(r.get('From','')),str(r.get('To','')),str(r.get('Work item','')).strip(),str(r.get('Outcome','')).strip()) for r in clean])
            c.commit(); st.rerun()
st.divider()
st.caption('Manager view: run this demo with a proper login and add role protected review/export before production.')
with st.expander('Manager snapshot (prototype)'):
    rows=c.execute('SELECT employee,work_date,mode,check_in,check_out,status,submitted_at FROM entries ORDER BY work_date DESC, employee').fetchall()
    st.dataframe(rows, use_container_width=True, hide_index=True, column_config={'employee':'Employee','work_date':'Date','mode':'Mode','check_in':'In','check_out':'Out','status':'Report status','submitted_at':'Submitted'})
