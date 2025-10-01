'''
Prospecting Buddy is a lightweight, dead-simple, offline, CRM-lite
with a minimal learning curve created to solve the organizational
problem of keeping track of prospects via follow-up date. 
It's convenience is apparent during any kind of activity which makes heavy
use of lead sourcing and lead nurturing, like outbound sales or applying
to several jobs per day. 

It's built entirely in Python and makes use of the limited yet surprisingly
fun and easy to use tkinter GUI library. There is one main Frame on which
the whole of the program is painted. Prospect entry on the right, followup
shortlist on the left. Currently displays a list of followups
where the initial recorded followup date matches the current date of the 
user's system (of course, taking into account timezone).

Planned additions:
 - View options for followup list for distinct days other than today
 - Option to delete entry
 - Button to kill program

This is an MVP (minimal viable product), and significant GUI changes
are subject to take place at any time.

'''

VERSION = '0.1'

try:
  from tkinter import *
  from tkinter import ttk
  from tkinter import scrolledtext
  from tkcalendar import DateEntry # Installation distinct from tkinter is necessary
  import sqlite3 # I love you sqlite
  import pandas as pd # Not used in program but useful for visualizing data in shell
  import datetime
except ImportError as e:
  print(f'Error importing module: {e}')
  sys.exit(2)

### SQL QUERY FUNCTIONS ###

### CONNECT DB ###
def create_table():
  '''
  Function: create_table
  Parameters: none
  Returns: void
  Uses: Globally in line 193
  Creates table Entries in which to store contact and followup information
  '''
  with sqlite3.connect('db.db') as conn:
    cursor = conn.cursor()

    ### CREATE TABLE ###
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS Entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name TEXT NOT NULL,
        poc TEXT NOT NULL,
        contact TEXT NOT NULL,
        warmth INT NOT NULL,
        followup_date TEXT NOT NULL
    );
    '''
    cursor.execute(create_table_query)
    print('Table successfully created')

def insert_entry(business_name, poc, contact, warmth, followup_date):
  '''
  Function: insert_entry
  Parameters: Name of Business, contact name, contact info, lead warmth, initial followup date
  Returns: void
  Uses: Used as command in enter_button_entry in line 298
  Enters contact and followup information into database including followup date
  in yyyy-mm-dd format. Commits information to db
  '''
  with sqlite3.connect('db.db') as conn:
    cursor = conn.cursor()

    insert_entry_query = '''
    INSERT INTO Entries (business_name, poc, contact, warmth, followup_date)
    VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(insert_entry_query, [business_name, poc, contact, warmth, followup_date])
    success_message_label.configure(text=f'Entry for {business_name} successful.')

    conn.commit()

def get_followup_dates():
  '''
  Function: get_followup_dates
  Parameters: none
  Returns: List of all entries for which followup_date == today's date
  Uses: First globally in line 311, second in line 313 via display_followups > render_followups > handle_update
  '''
  with sqlite3.connect('db.db') as conn:
    cursor = conn.cursor()
     
    today = datetime.date.today() # If you just use DATE('now') it does not account for timezones
    # Note that there is no need to convert to ISO specifically due to the date format in which
    # dates are being saved (see lines 180, 292)

    get_followup_dates_query = 'SELECT * FROM Entries WHERE DATE(followup_date) = ?'
    cursor.execute(get_followup_dates_query, (today,))
    return cursor.fetchall()

def update_entry(new_date, entry_id):
  '''
  Function: update_query
  Parameters: new_date, entry_id
  Returns: void
  Uses: Called in line 145 via function handle_update
  Updates column new_date where entry_id is equal to id of the given entry.
  '''
  with sqlite3.connect('db.db') as conn:
    cursor = conn.cursor()

    update_entry_query = 'UPDATE Entries SET followup_date = ? WHERE id = ?;'
    cursor.execute(update_entry_query, (new_date, entry_id))

    conn.commit()

def delete_enry(entry_id): # Currently Unused TODO add ttk.Button to display_followups to delete entry.
  '''
  Function: delete_enry
  Parameters: entry_id
  Returns: void
  Uses: Called in lambda funcion inside of display_followups
  '''
  cursor = conn.cursor()

  delete_entry_query = 'DELETE FROM Entries WHERE id = ?'
  cursor.execute(delete_entry_query, (entry_id,))

  conn.commit()

### GUI-SPECIFIC FUNCTIONS ###

def clear_frame(frame):
  '''
  Function: clear_frame
  Parameters: frame => frame from which to clear entries
  Returns: void
  Uses: handle_update < render_followups < display_followups
  Destroys all widgets in a given frame.
  '''
  for widget in frame.winfo_children():
    widget.destroy()

def handle_update(frame, entry_id, new_date):
  '''
  Function: handle_update
  Parameters: frame, entry_id, new_date
  Returns: void
  Uses: render_followups < display_followups
  Calls SQL command inside update_entry, clears frame, and renders followups
  '''
  update_entry(new_date, entry_id)

  updated_followups = get_followup_dates()
  clear_frame(frame)
  render_followups(frame, updated_followups)
  print(new_date)

def render_followups(frame, followups):
  '''
  Function: render_followups
  Parameters: frame, followups
  Returns: void
  Uses: display_followups
  Renders each entry from the list followups. 
  Uses three ttk.Frames to store useful information
  about each follow up, and packs them all for each
  entry. Command calls lambda so arguments of the
  function handle_update can be referenced. Critically
  important to have nd and eid as parameters or else
  entry id (entry[0]) and new_date.get() will reference
  incorrect information. (i.e., the last entry generated 
  by the for loop and the date in the DateEntry 
  on initial GUI paint). 
  '''
  for entry in followups:
    entry_row_1 = ttk.Frame(frame)
    entry_row_2 = ttk.Frame(frame)
    entry_row_3 = ttk.Frame(frame)

    entry_row_1.pack(pady=2, padx=10, fill='x')
    entry_row_2.pack(pady=2, padx=10, fill='x')
    entry_row_3.pack(pady=(0, 20), padx=10, fill='x')

    ttk.Label(entry_row_1, text=f'{entry[0]}, {entry[1]}').pack(side='left')
    ttk.Label(entry_row_2, text=f'{entry[2]} {entry[3]}').pack(side='left')
    new_date = DateEntry(entry_row_3, width=10, date_pattern='yyyy-mm-dd')
    new_date.pack(side='left')
    update_button = ttk.Button(entry_row_3, width=5, text='U', command=lambda nd=new_date, eid=entry[0]: handle_update(frame, eid, nd.get())) # must parameterize new_date and entry[0] as nd and eid inside lambda due to python's late binding. This allows you to access latest information.
    update_button.pack(side='left')


def display_followups(followups): 
  '''
  Function: display_followups
  Parameters: followups
  Returns: void
  Creates a list of followups on the left hand side of the application 
  in a scrollable canvas. See below that there
  is no elegant way to create a scroll container 
  natively in tkinter. The following is the best I
  could come up with without creating a read-only
  texarea with scrolledtest.ScrolledTest, which is not
  what I wanted.
  '''
  if len(followups) < 1:
    message_row = ttk.Frame(shortlist_frame).pack()
    no_followups_message = 'No follow-ups scheduled!'
    ttk.Label(message_row, text=no_followups_message).pack(pady=50, padx=10)
  else:
    def scroll(event): # configures canvas to scroll
      followup_canvas.configure(scrollregion=followup_canvas.bbox('all'), width=445, height=400)
    
    # to create a scroll container, one needs: frame > canvas > frame > items

    ### Scroll logic vvv ###

    followup_canvas = Canvas(shortlist_frame) 
    followup_frame = Frame(followup_canvas)

    scrollbar = Scrollbar(shortlist_frame, orient='vertical', command=followup_canvas.yview) 

    followup_canvas.configure(yscrollcommand=scrollbar.set)

    followup_canvas.pack(side='left')
    scrollbar.pack(side='right', fill='y')

    followup_canvas.create_window((1, 1), window=followup_frame,anchor='nw')
    followup_frame.bind('<Configure>', scroll)

    ### Scroll logic ^^^ ###

    render_followups(followup_frame, followups)
    print(followups)

### CREATE TABLE IF NOT EXISTS ###

create_table()

### INITIALIZE TKINTER GUI ###

root = Tk()
root.title('Prospecting Buddy')
root.geometry(f'1100x600')

input_frame = ttk.Frame(root)
input_frame.pack(side='right', fill='y', padx=20, pady=20)

shortlist_frame = ttk.Frame(root, relief=GROOVE)
shortlist_frame.pack(side='left', fill='y', padx=20, pady=20)

input_width = 18

### BUSINESS NAME ###
business_name_row = ttk.Frame(input_frame)
business_name_row.pack(pady=15, padx=10, fill='x')

ttk.Label(business_name_row, text='Business Name: ').pack(side='left')
business_name_entry = ttk.Entry(business_name_row, width=input_width)
business_name_entry.pack(side='right') 

### POC ###
poc_row = ttk.Frame(input_frame)
poc_row.pack(pady=15, padx=10, fill='x')

ttk.Label(poc_row, text='Point of Contact: ').pack(side='left')
poc_entry = ttk.Entry(poc_row, width=input_width)
poc_entry.pack(side='right') 

### CONTACT ###
contact_row = ttk.Frame(input_frame)
contact_row.pack(pady=15, padx=10, fill='x')

ttk.Label(contact_row, text='Contact Info: ').pack(side='left')
contact_entry = ttk.Entry(contact_row, width=input_width)
contact_entry.pack(side='right') 

### LEAD WARMTH ###
warmth_row = ttk.Frame(input_frame)
warmth_row.pack(pady=15, padx=10, fill='x')

lead_warmth_options = [
                        'Warm',
                        'Neutral',
                        'Cold'
                      ]

ttk.Label(warmth_row, text='Lead Warmth: ').pack(side='left')
# Combobox is readonly to ensure only specific entries allowed. 
warmth_entry = ttk.Combobox(warmth_row, values=lead_warmth_options, state='readonly', width=input_width)
warmth_entry.set(lead_warmth_options[0])
warmth_entry.pack(side='right') 

### FOLLOW UP DATE ###
followup_row = ttk.Frame(input_frame)
followup_row.pack(pady=15, padx=10, fill='x')

ttk.Label(followup_row, text='Follow-Up Date: ').pack(side='left')
followup_entry = DateEntry(followup_row, width=input_width, date_pattern='yyyy-mm-dd') 
# Note that yyyy-mm-dd is the only allowed date pattern in sqlite
followup_entry.pack(side='right') 

### ENTER BUTTON ###
enter_button_row = ttk.Frame(input_frame)
enter_button_row.pack(pady=15, padx=10, fill='x')
success_message_row = ttk.Frame(input_frame)
success_message_row.pack(pady=15, padx=10, fill='x')

enter_button_entry = ttk.Button(enter_button_row, # this looks ugly
                                text='ENTER',
                                command=lambda: insert_entry(business_name_entry.get(),
                                                             poc_entry.get(),
                                                             contact_entry.get(),
                                                             warmth_entry.get(),
                                                             followup_entry.get()))

success_message_label = ttk.Label(success_message_row, text='') # text is configured in insert_entry
success_message_label.pack()
enter_button_entry.pack() 

followups = get_followup_dates()

display_followups(followups) # what a wild and crazy ride

root.mainloop()
