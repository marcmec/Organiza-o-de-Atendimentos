import java.util.List;

public class Impressor {

    public static void imprimir(List<Consultorio> consultorios) {
        for (Consultorio c : consultorios) {
            System.out.println("Consultorio " + c.getNumero() + ":");
            imprimirSessao(c.getManha());
            System.out.println(Consultorio.formatarHora(Consultorio.MANHA_FIM) + " Higienizacao");
            imprimirSessao(c.getTarde());

            int fimTarde = c.getTarde().getTempoAtual();
            // Reuniao deve comecar DEPOIS das 17:00 e ANTES das 18:00
            int horaReuniao = Math.max(fimTarde, Consultorio.REUNIAO_MIN + 1);
            System.out.println(Consultorio.formatarHora(horaReuniao) + " Reuniao de encerramento");
            System.out.println();
        }
    }

    private static void imprimirSessao(Sessao sessao) {
        List<Atendimento> lista = sessao.getAtendimentos();
        List<int[]> agenda = sessao.getAgenda();

        for (int i = 0; i < lista.size(); i++) {
            Atendimento a = lista.get(i);
            int inicio = agenda.get(i)[0];
            String sufixo = a.isExpresso() ? "expresso" : a.getDuracaoMinutos() + "min";
            System.out.println(Consultorio.formatarHora(inicio) + " " + a.getNome() + " " + sufixo);
        }
    }
}
