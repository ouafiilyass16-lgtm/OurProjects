# -----------------------------------------------------
# -- Databases => SQLite => Create Skills App Part 1 --
# -----------------------------------------------------
import sqlite3

db=sqlite3.connect("skills.db")
cr=db.cursor()
user_id=1
def commit_close():
  db.commit()

# Input Big Message
input_message = """
What Do You Want To Do ?
"s" => Show All Skills
"a" => Add New Skill
"d" => Delete A Skill
"u" => Update Skill Progress
"q" => Quit The App
Choose Option:
"""

# Input Option Choose
user_input = input(input_message).strip().lower()

# Command List
commands_list = ["s", "a", "d", "u", "q"]

# Define The Methods

def show_skills():

  cr.execute("select * from skills")
  skills=cr.fetchall()
  for skill in skills:
    print(f"skill name=> {skill[0]}",end="")
    print(f"skill progress=> {skill[1]}",end="")

  commit_close()

def add_skill():

 sk = input("Enter Skill Name : ").strip().capitalize()
 # prog=input("entrer votre progress").strip()
 # cr.execute("INSERT INTO skills(name,progress,user_id) VALUES (?,?,?)",(sk,prog,user_id))
 cr.execute( "SELECT name FROM skills WHERE name = ? AND user_id = ?",(sk, user_id) )
 resuelt=cr.fetchone()
 if resuelt is not None:
       print("the skill is already added you cannont added ")
 else:
    prog = input("entrer votre new  progress").strip()
    cr.execute("INSERT INTO skills(name,progress,user_id) VALUES (?,?,?)", (sk, prog, user_id))


    commit_close()
    print("Skill added successfully ✅")


def delete_skill():

  sk = input("Enter Skill Name : ").strip().capitalize()
  cr.execute("DELETE FROM skills WHERE name=? and user_id=?",(sk,user_id))
  commit_close()

def update_skill():
  sk = input("Enter Skill Name : ").strip().capitalize()
  prog = input("entrer votre new progress").strip()
  cr.execute("update skills set progress=? where name=?",(prog,sk))
  commit_close()

# Check If Command Is Exists
if user_input in commands_list:


  if user_input == "s":

    show_skills()

  elif user_input == "a":

    add_skill()


  elif user_input == "d":

    delete_skill()

  elif user_input == "u":

    update_skill()

  else:

    print("App Is Closed.")

else:

  print(f"Sorry This Command \"{user_input}\" Is Not Found")