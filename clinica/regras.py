"""Regras de funcionamento da clínica, expressas em minutos desde a meia-noite.

Trabalhar com "minutos desde a meia-noite" (ex.: 08:00 -> 480) torna toda a
aritmética de horário trivial: somar a duração de um atendimento é somar um
inteiro, e formatar de volta para HH:MM é uma simples divisão por 60.

Centralizar as regras aqui significa que, se a clínica mudar um horário, basta
alterar uma constante — nenhum trecho do algoritmo precisa ser tocado.
"""

# ---- Sessão da manhã -------------------------------------------------------
INICIO_MANHA = 8 * 60            # 08:00 -> 480
HIGIENIZACAO = 11 * 60 + 30      # 11:30 -> 690  (início da higienização)

# ---- Sessão da tarde -------------------------------------------------------
INICIO_TARDE = 13 * 60 + 30      # 13:30 -> 810

# A reunião de encerramento começa DEPOIS das 17:00 e ANTES das 18:00.
# Interpretamos a janela como [17:00, 18:00): a reunião não começa antes das
# 17:00 e precisa ter começado antes das 18:00. Essa escolha de fronteira está
# justificada no RACIOCINIO.md (pergunta sobre as regras) e é trocável aqui.
REUNIAO_INICIO_MIN = 17 * 60     # 17:00 -> 1020 (limite inferior, inclusivo)
REUNIAO_INICIO_MAX = 18 * 60     # 18:00 -> 1080 (limite superior, exclusivo)

# ---- Capacidades derivadas (em minutos) -----------------------------------
CAP_MANHA = HIGIENIZACAO - INICIO_MANHA            # 210  (ocupação <= 210)
CAP_TARDE = REUNIAO_INICIO_MAX - INICIO_TARDE      # 270  (ocupação  < 270)
MIN_TARDE = REUNIAO_INICIO_MIN - INICIO_TARDE      # 210  (ocupação >= 210)

# Maior conteúdo válido de UM consultório: manhã cheia (<=210) + tarde quase
# cheia (<270, logo no máximo 269 com minutos inteiros). Usado para estimar o
# número mínimo de consultórios.
CAP_CONSULTORIO = CAP_MANHA + (CAP_TARDE - 1)      # 210 + 269 = 479

# ---- Atendimentos expressos ------------------------------------------------
EXPRESSO_MIN = 10                # todo atendimento "expresso" dura 10 minutos
