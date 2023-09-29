from typing import Any
from statemachine import StateMachine, State
import time

class ZapeduMachine(StateMachine):
    "Texto"
    chat = State(initial=True)
    single_question = State()
    multiple_questions_test = State() 
    sm_interna:StateMachine = None

    questao = chat.to(single_question)
    full_test = chat.to(multiple_questions_test) 

    voltar_chat = ( single_question.to(chat) |
                   multiple_questions_test.to(chat) |
                   chat.to(chat)
                   )
    
   
    def before_questao(self): 
        print( f"GLOBAL: ADS: Running GLOBAL....")
    
    def on_enter_single_question(self):
        print("GLOBAL:para voltar para o modo chat é só falar.")
        self.sm_interna = ZapeduMachineSingleQuestion(master=self)
        self.sm_interna._graph().write_png("ZapeduMachineInternal.png")
         

    def on_exit_single_question(self):
        print("GLOBAL:depois a gente treina mais...")
        self.sm_interna = None



class ZapeduMachineSingleQuestion(StateMachine):
    "Controle de questao"
    response = None
    sm_global = None
    single_question = State(initial=True)
    waiting_answer = State() 
    correct_answer = State()
    wrong_answer = State()
    sair = State()

    waiting = single_question.to(waiting_answer)  
    success = waiting_answer.to(correct_answer)
    fail =  waiting_answer.to(wrong_answer)

    retry = wrong_answer.to(waiting_answer)


    voltar_chat = ( single_question.to(sair) | 
                   waiting_answer.to(sair)| 
                   waiting_answer.to(sair)|
                   correct_answer.to(sair)
                   )

    def __init__(self, master:StateMachine ,model: Any = None, state_field: str = "state", start_value: Any = None, rtc: bool = True, allow_event_without_transition: bool = False):
        self.sm_global = master 
        super().__init__(model, state_field, start_value, rtc, allow_event_without_transition)
 

    def on_enter_single_question(self):
        if self.response:
            print(f"INTERNAL: {self.current_state.id} -> tente outra vez ?")
            self.response = None
        else:
            print(f"INTERNAL: {self.current_state.id} -> ENCREVENDO QUESTAO")
        self.waiting()
   
    def on_enter_waiting_answer(self):
        print(f"INTERNAL: {self.current_state.id} -> ESPERANDO RESPOSTA(sleep 3)")
        time.sleep(3)
        self.success()

    def on_enter_correct_answer(self):
        print(f"INTERNAL: {self.current_state.id} -> acertou krai !!!") 
        self.send("voltar_chat")

    def on_enter_wrong_answer(self):
        print(f"INTERNAL: {self.current_state.id} -> ENCREVENDO QUESTAO")
        self.response = True
        self.waiting()
   
    def before_questao(self): 
        print( f"INTERNAL: ADS: Running internal machine ....")
    
    def on_enter_multiple_questions_test(self):
        print(f"INTERNAL: {self.current_state.id} -> para voltar para o modo chat é só falar.")


    def on_exit_multiple_questions_test(self):
        print(f"INTERNAL: {self.current_state.id} -> depois a gente treina mais...")

    def before_voltar_chat(self):
        self.sm_global.send("voltar_chat")




if __name__ == '__main__':
    sm = ZapeduMachine()
    img_path = "./ZapeduMachine.png"
    sm._graph().write_png(img_path)
    print("ESTADO INICIAL")
    print("state: ", sm.current_state.id)
    print("Aluno pediu questão")
    sm.questao()  # ou sm.send("questao")
    print("state: ", sm.current_state.id)
 
    try:
        #sm.full_test()
        sm.send("full_test")
    except:
        print("pode n boy")

    print("state: ", sm.current_state.id)
    # print(sm.current_state.name)
    sm.voltar_chat()
    sm.send("voltar_chat")
    #print("state: ", sm.current_state.id)
    #sm.full_test()
    #sm.sm_interna._graph().write_png(img_path2)
    print("state: ", sm.current_state.id)

    #print(sm)

    sm.send("voltar_chat")
    sm.send("voltar_chat")
    sm.send("voltar_chat")
    print("state: ", sm.current_state.id)