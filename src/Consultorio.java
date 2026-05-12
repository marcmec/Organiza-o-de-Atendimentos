public class Consultorio {
    private final int numero;
    private final Sessao manha;
    private final Sessao tarde;

    // 08:00 = 480min, 11:30 = 690min
    // 13:30 = 810min, 17:00 = 1020min, 18:00 = 1080min
    public static final int MANHA_INICIO  = 8 * 60;         // 480
    public static final int MANHA_FIM     = 11 * 60 + 30;   // 690
    public static final int TARDE_INICIO  = 13 * 60 + 30;   // 810
    public static final int REUNIAO_MIN   = 17 * 60;         // 1020 — deve começar DEPOIS das 17:00
    public static final int REUNIAO_MAX   = 18 * 60;         // 1080 — deve começar ANTES das 18:00

    public Consultorio(int numero) {
        this.numero = numero;
        this.manha = new Sessao(MANHA_INICIO, MANHA_FIM);
        this.tarde = new Sessao(TARDE_INICIO, REUNIAO_MAX);  // limite hard para encaixe
    }

    public int getNumero() { return numero; }
    public Sessao getManha() { return manha; }
    public Sessao getTarde() { return tarde; }

    /**
     * A tarde termina dentro da janela válida para a reunião?
     * Deve terminar após 17:00 e antes/às 18:00.
     */
    public boolean tardeValida() {
        int fim = tarde.getTempoAtual();
        return fim > REUNIAO_MIN && fim <= REUNIAO_MAX;
    }

    /**
     * Pode encaixar este atendimento na tarde sem violar a janela da reunião?
     */
    public boolean cabeNaTarde(Atendimento a) {
        int novofim = tarde.getTempoAtual() + a.getDuracaoMinutos();
        return novofim <= REUNIAO_MAX;
    }

    public static String formatarHora(int minutos) {
        return String.format("%02d:%02d", minutos / 60, minutos % 60);
    }
}
