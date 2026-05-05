from database import engine, Base
import sqlalchemy

def alter_table():
    with engine.connect() as conn:
        try:
            conn.execute(sqlalchemy.text('ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT \'CUSTOMER\';'))
            conn.commit()
            print("Added role column.")
        except Exception as e:
            print("role column might already exist:", str(e))
            
        try:
            conn.execute(sqlalchemy.text('ALTER TABLE users ADD COLUMN primary_branch VARCHAR(100);'))
            conn.commit()
            print("Added primary_branch column.")
        except Exception as e:
            print("primary_branch column might already exist:", str(e))

if __name__ == "__main__":
    alter_table()
