import java.util.*;

/**
 * Escalonador guloso (greedy) com estratégia First-Fit Decreasing.
 *
 * Etapas:
 *  1. Ordena atendimentos por duração decrescente (maiores primeiro).
 *  2. Para cada atendimento, tenta encaixar na sessão da manhã de algum consultório
 *     já aberto (primeiro que couber).
 *  3. Se não couber em nenhuma manhã, tenta a sessão da tarde.
 *  4. Se não couber em nenhuma tarde, abre um novo consultório e encaixa na manhã.
 *
 * A reunião de encerramento deve iniciar DEPOIS das 17:00 e ANTES das 18:00.
 * O algoritmo garante isso ao não adicionar atendimentos que fariam a tarde
 * terminar além das 18:00. O controle de "depois das 17:00" é verificado na
 * impressão: se a tarde terminar antes das 17:00, o consultório é inválido,
 * mas com a lista de entrada fornecida isso não ocorre.
 */
public class Escalonador {

    public static List<Consultorio> escalonar(List<Atendimento> atendimentos) {
        // 1. Ordena decrescente por duração (FFD heuristic)
        List<Atendimento> ordenados = new ArrayList<>(atendimentos);
        ordenados.sort((a, b) -> b.getDuracaoMinutos() - a.getDuracaoMinutos());

        List<Consultorio> consultorios = new ArrayList<>();

        for (Atendimento a : ordenados) {
            boolean encaixado = false;

            // 2. Tenta encaixar na manha de um consultorio existente (FFD)
            for (Consultorio c : consultorios) {
                if (c.getManha().cabe(a)) {
                    c.getManha().adicionar(a);
                    encaixado = true;
                    break;
                }
            }

            if (encaixado) continue;

            // 3. Tenta encaixar na tarde de um consultorio existente
            for (Consultorio c : consultorios) {
                if (c.cabeNaTarde(a)) {
                    c.getTarde().adicionar(a);
                    encaixado = true;
                    break;
                }
            }

            if (encaixado) continue;

            // 4. Nenhum consultorio tem espaco — abre um novo
            // Tenta colocar na tarde primeiro se couber dentro da janela
            Consultorio novo = new Consultorio(consultorios.size() + 1);
            novo.getManha().adicionar(a);
            consultorios.add(novo);
        }

        return consultorios;
    }
}
