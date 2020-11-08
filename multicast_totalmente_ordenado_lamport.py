# Problema: ordem total das mensagens trocadas entre processos
# Algoritmo:
# 1 - toda mensagem é marcada no tempo (timestamped) com a hora corrente (hora lógica) do enviador
# 2 - Quando uma mensagem é enviada, conceitualmente ela também é enviada para o próprio enviador
#   obs.: assumimos que mensagens do mesmo enviador são recebidas na mesma ordem que elas são enviadas (não é um problema,
#   já que já temos algoritmos de ordenação, tipo TCP), e que mensagens não são perdidas
# 3 - Quando um processo recebe uma mensagem, ela é colocada em sua fila local, ordenada de acordo com seu timestamp.
#     O recebedor multicast um ack para os outros processos (desta forma, todos os processos, eventualmente, terão a
#     mesma cópia de mensagens
# 4 - Um processo entrega a mensagem para a aplicação apenas quando a mensagem está na cabeça da fila e foi dado ack por
#     todos os outros processos. A mensagem, assim, é removida da fila. Os acks associados a ela podem ser descartados.
#     (como todos tem a mesma cópia das mensagens, todas as mensagems são entregues na mesma ordem)

from threading import Thread
from random import randint
import time


class Ack:

    def __init__(self, num_proc, id_msg, relogio, enviador):
        self.num_proc = num_proc
        self.id_msg = id_msg
        self.relogio = relogio
        self.enviador = enviador


class Mensagem:

    def __init__(self, id, num_proc, relogio):
        self.id = id
        self.num_proc = num_proc
        self.relogio = relogio
        self.is_ack_enviado = False

    def __eq__(self, other):
        if self.num_proc == other.num_proc and self.id == other.id:
            return True
        return False

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
        self.fila_msgs = []
        self.acks = dict()

    def run(self):
        while (True):
            tempo_espera = randint(0, 10)
            time.sleep(tempo_espera)
            self.enviar_mensagem()

    def enviar_mensagem(self):
        self.incrementar_relogio()
        self.incrementar_count_msg()
        mensagem = Mensagem(self.count_msg, self.num_proc, self.relogio)
        print(self.espaco, self.relogio, ' [Enviando] - ', self.num_proc, '.', self.count_msg)
        self.fila_msgs.append(mensagem)
        self.ordenar_fila()
        for processo in self.outros_processos:
            processo.receber_mensagem(mensagem)

    def receber_mensagem(self, mensagem):
        self.atualizar_relogio(self.relogio, mensagem.relogio)
        print(self.espaco, self.relogio, '[Recebendo] -', self.num_proc, 'msg [', mensagem.num_proc,
              '.', mensagem.id, ']')
        self.fila_msgs.append(mensagem)
        self.ordenar_fila()
        mensagem_cabeca = self.fila_msgs[0]
        # envia ack se a mensagem na cabeça não for minha ou se ainda não enviou
        if not mensagem_cabeca.num_proc == self.num_proc or not mensagem_cabeca.is_ack_enviado:
            # enviando ack
            self.enviar_ack(mensagem_cabeca)

        self.testar_entregar_mensagem()

    def enviar_ack(self, mensagem):
        self.incrementar_relogio()
        ack = Ack(mensagem.num_proc, mensagem.id, self.relogio, self.num_proc)
        print(self.espaco, self.relogio, 'ACK [enviando] - Proc', self.num_proc, 'de msg[', ack.num_proc, '.', ack.id_msg, ']')
        for processo in self.outros_processos:
            processo.receber_ack(ack)
        mensagem.is_ack_enviado = True

    def receber_ack(self, ack):
        self.atualizar_relogio(self.relogio, ack.relogio)
        print(self.espaco, self.relogio, 'ACK [recebendo] - Proc', self.num_proc, 'de enviador ', ack.enviador,
              'de msg[', ack.num_proc, '.', ack.id_msg, ']')
        acks_do_processo = self.acks.get(ack.num_proc, False)
        if not acks_do_processo:
            acks_do_processo = []
        acks_do_processo.append(ack)
        self.testar_entregar_mensagem()
        # mensagem_do_ack = [msg for msg in self.fila_msgs if msg.id == ack.id_msg and msg.num_proc == ack.num_proc]
        # if mensagem_do_ack:
        #     mensagem_do_ack = mensagem_do_ack[0]
        #     self.ordenar_fila()
        #     # se é para entregar para aplicação (está na cabeça com todos os acks), entrega
        #     if self.fila_msgs and self.fila_msgs[0] == mensagem_do_ack:
        #         if self.is_mensagem_completely_acked(mensagem_do_ack, len(self.outros_processos) + 1):  # quant processos = outros + 1
        #             print(self.espaco, self.relogio, '[Entrega-App] - Proc ', self.num_proc, ': entregando mensagem para app: [', mensagem_do_ack.num_proc,
        #                   '.', mensagem_do_ack.id, ']')
        #             self.fila_msgs.pop(0)

    def atualizar_relogio(self, relogio_local, relogio_proc_mensagem):
        self.relogio = max(relogio_local, relogio_proc_mensagem) + 1

    def incrementar_relogio(self):
        self.relogio += 1

    def incrementar_count_msg(self):
        self.count_msg += 1

    def ordenar_fila(self):
        self.fila_msgs.sort(key=lambda msg: (msg.relogio, msg.num_proc))

    def testar_entregar_mensagem(self):
        self.ordenar_fila()
        # # se é para entregar para aplicação (está na cabeça com todos os acks), entrega
        # mensagem_cabeca = self.fila_msgs[0]
        #
        # # envia ack se a mensagem na cabeça não for minha ou se ainda não enviou
        # if self.is_mensagem_completely_acked(mensagem_cabeca, len(self.outros_processos) + 1):  # quant processos = outros + 1
        #     print('Proc ', self.num_proc, ': entregando mensagem para app: proc [', mensagem_cabeca.num_proc,
        #           '] id [', mensagem_cabeca.id, ']')
        #     self.fila_msgs.pop(0)

        if len(self.fila_msgs) > 0:
            mensagem_cabeca = self.fila_msgs[0]

            if mensagem_cabeca:
                    # se é para entregar para aplicação (está na cabeça com todos os acks), entrega
                    if self.fila_msgs and self.fila_msgs[0] == mensagem_cabeca:
                        if self.is_mensagem_completely_acked(mensagem_cabeca, len(self.outros_processos) + 1):  # quant processos = outros + 1
                            print(self.espaco, self.relogio, '[Entrega-App] - Proc ', self.num_proc, ': entregando mensagem para app: [', mensagem_cabeca.num_proc, '.', mensagem_cabeca.id, ']')
                            self.fila_msgs.pop(0)

    def is_mensagem_completely_acked(self, mensagem, quant_processes):
            """
                quant_processes: quantidade total de processos total
            """
            for num_proc in range(1, quant_processes + 1):
                # o próprio processo não precisa enviar um ack para suas mensagens
                if num_proc == self.num_proc:
                    continue
                acks_do_processo = self.acks.get(num_proc, False)
                if acks_do_processo and len(acks_do_processo) > 0:
                    ack_encontrado = [ack for ack in acks_do_processo if ack.id_msg == mensagem.id and ack.num_proc == mensagem.num_proc]
                    if not len(ack_encontrado) > 0:
                        return False
                else:
                    return False
            return True


proc1 = Processo(1)
proc2 = Processo(2)
proc3 = Processo(3, [proc1, proc2])

proc1.outros_processos = [proc2, proc3]
proc2.outros_processos = [proc1, proc3]

proc1.start()
proc2.start()
proc3.start()
