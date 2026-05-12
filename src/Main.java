import java.io.*;
import java.util.*;

public class Main {

    public static void main(String[] args) throws IOException {
        String arquivo = args.length > 0 ? args[0] : "atendimentos.txt";

        List<Atendimento> atendimentos = Parser.ler(arquivo);
        System.out.println("Total de atendimentos carregados: " + atendimentos.size());
        System.out.println();

        List<Consultorio> consultorios = Escalonador.escalonar(atendimentos);
        Impressor.imprimir(consultorios);

        System.out.println("Total de consultórios utilizados: " + consultorios.size());
    }
}
