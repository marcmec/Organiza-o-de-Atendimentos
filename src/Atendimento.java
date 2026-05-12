public class Atendimento {
    private final String nome;
    private final int duracaoMinutos;
    private final boolean expresso;

    public Atendimento(String nome, int duracaoMinutos, boolean expresso) {
        this.nome = nome;
        this.duracaoMinutos = duracaoMinutos;
        this.expresso = expresso;
    }

    public String getNome() { return nome; }
    public int getDuracaoMinutos() { return duracaoMinutos; }
    public boolean isExpresso() { return expresso; }

    @Override
    public String toString() {
        return nome + " " + (expresso ? "expresso" : duracaoMinutos + "min");
    }
}
