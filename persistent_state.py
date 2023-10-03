 
from statemachine import State
from statemachine import StateMachine

import sqlite3

from zapedu_fsm import ZapeduMachine
 

class DBPersistentModel():
    """A concrete implementation of a storage strategy for a Model
    that reads and writes to a db.
    """

    def __init__(self, conn, user_id, buss_id): 
        self.conn = conn
        self.buss_id = buss_id
        self.user_id = user_id
        self._state = None
 
    def __repr__(self):
        return f"{type(self).__name__}(state={self.state})"

    @property
    def state(self):
        if self._state is None:
            self._state = self._read_state()
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self._write_state(value)

    def _read_state(self):
        cur = self.conn.cursor()
        cur.execute("select last_state from users where user_id = :user_id and buss_id = :buss_id",{'user_id': self.user_id,'buss_id': self.buss_id})
        row = cur.fetchone()
        cur.close() 
        return row[0]  if row else None 

    def _write_state(self, value):
        cur = self.conn.cursor()
        cur.execute("update users SET last_state = :state where user_id = :user_id and buss_id = :buss_id", {'state':value ,'user_id': self.user_id,'buss_id': self.buss_id})
        cur.close()
 


if __name__ == "__main__":
    conn = sqlite3.connect('banco.db')  

    c = conn.cursor()
    c.execute("drop table users")
    c.execute(''' CREATE TABLE users (user_id int, buss_id int, last_state text,  name text) ''')
    c.execute(" INSERT INTO users VALUES (1, 1, 'single_question' ,'joao') ")

    persisted_state = DBPersistentModel(
                                        conn=conn, 
                                        user_id=1, 
                                        buss_id=1
                                        )

    print(persisted_state)
    print(persisted_state.state)
    if not persisted_state.state:
        print("nao cadastrado")
        exit()

    print("tem cadastro")
    sm = ZapeduMachine(model=persisted_state)
    
    print(f"Initial state: {sm.current_state.id}")

    sm.send("voltar_chat")

    print(f"State after transition: {sm.current_state.id}")

    print( c.execute(" select * from users ").fetchall() ) 
    # del sm
    # del model

    # model = FilePersistentModel(file=state_file)
    # sm = ResourceManagement(model=model)

    # print(f"State restored from file system: {sm.current_state.id}")
    # with open(state_file.name) as f:
    #     for line in f:
    #         print(line)
