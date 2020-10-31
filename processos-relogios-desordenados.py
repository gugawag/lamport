from threading import Thread
from random import randint
import time


class Mensagem:

    def __init__(self, id, num_proc, relogio):
        self.id = id
        self.num_proc = num_proc
        self.relogio = relogio


class Processo(Thread):

    def __init__(self, num_proc, outros_processos=[]):
        Thread.__init__(self)
        self.relogio = 0
        self.num_proc = num_proc
        self.count_msg = 0
        self.outros_processos = outros_processos
        if self.num_proc == 1:
            self.espaco = ''
        elif self.num_proc == 2:
            self.espaco = '     '
        elif self.num_proc == 3:
            self.espaco = '          '

    def run(self):
        while (True):
            tempo_espera = randint(0, 10)
            processo_escolhido = randint(0, 1)
            time.sleep(tempo_espera)
            self.enviar_mensagem(self.outros_processos[processo_escolhido])

    def enviar_mensagem(self, processo_recebedor):
        self.incrementar_relogio()
        self.incrementar_count_msg()
        mensagem = Mensagem(self.count_msg, self.num_proc, self.relogio)
        print(self.espaco, self.relogio, ' [Enviando] - Proc', self.num_proc, ' enviando msg [', self.count_msg,
              '] para proc [',
              processo_recebedor.num_proc, ']')
        processo_recebedor.receber_mensagem(mensagem)

    def receber_mensagem(self, mensagem):
        self.atualizar_relogio(self.relogio, mensagem.relogio)
        print(self.espaco, self.relogio, ' [Recebendo] - Proc', self.num_proc, ' recebendo msg [', mensagem.id,
              '] do proc [',
              mensagem.num_proc,
              ']')

    def atualizar_relogio(self, relogio_local, relogio_proc_mensagem):
        self.relogio = max(relogio_local, relogio_proc_mensagem) + 1

    def incrementar_relogio(self):
        self.relogio += 1

    def incrementar_count_msg(self):
        self.count_msg += 1


proc1 = Processo(1)
proc2 = Processo(2)
proc3 = Processo(3, [proc1, proc2])

proc1.outros_processos = [proc2, proc3]
proc2.outros_processos = [proc1, proc3]

proc1.start()
proc2.start()
proc3.start()
