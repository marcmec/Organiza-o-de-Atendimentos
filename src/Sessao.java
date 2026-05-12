import java.util.ArrayList;
import java.util.List;

public class Sessao {
    private final int inicioMinutos;   // minutos desde 00:00
    private final int fimMaxMinutos;   // minutos desde 00:00
    private int tempoAtual;
    private final List<int[]> agenda;  // cada entry: [inicio, duracao, indiceAtendimento]
    private final List<Atendimento> atendimentos;

    public Sessao(int inicioMinutos, int fimMaxMinutos) {
        this.inicioMinutos = inicioMinutos;
        this.fimMaxMinutos = fimMaxMinutos;
        this.tempoAtual = inicioMinutos;
        this.agenda = new ArrayList<>();
        this.atendimentos = new ArrayList<>();
    }

    public boolean cabe(Atendimento a) {
        return tempoAtual + a.getDuracaoMinutos() <= fimMaxMinutos;
    }

    public void adicionar(Atendimento a) {
        agenda.add(new int[]{tempoAtual, a.getDuracaoMinutos()});
        atendimentos.add(a);
        tempoAtual += a.getDuracaoMinutos();
    }

    public int getTempoLivre() {
        return fimMaxMinutos - tempoAtual;
    }

    public int getTempoAtual() {
        return tempoAtual;
    }

    public List<Atendimento> getAtendimentos() {
        return atendimentos;
    }

    public List<int[]> getAgenda() {
        return agenda;
    }

    public int getInicioMinutos() {
        return inicioMinutos;
    }

    public boolean isEmpty() {
        return atendimentos.isEmpty();
    }
}
