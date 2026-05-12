import java.io.*;
import java.util.*;

public class Parser {

    public static List<Atendimento> ler(String caminhoArquivo) throws IOException {
        List<Atendimento> lista = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(caminhoArquivo))) {
            String linha;
            while ((linha = br.readLine()) != null) {
                linha = linha.trim();
                if (linha.isEmpty()) continue;
                lista.add(parseLinha(linha));
            }
        }
        return lista;
    }

    static Atendimento parseLinha(String linha) {
        if (linha.toLowerCase().endsWith("expresso")) {
            String nome = linha.substring(0, linha.toLowerCase().lastIndexOf("expresso")).trim();
            return new Atendimento(nome, 10, true);
        }

        // Find the last token which should be "NNmin"
        int idx = linha.lastIndexOf(' ');
        String token = linha.substring(idx + 1).trim().toLowerCase();
        if (token.endsWith("min")) {
            int duracao = Integer.parseInt(token.replace("min", "").trim());
            String nome = linha.substring(0, idx).trim();
            return new Atendimento(nome, duracao, false);
        }

        throw new IllegalArgumentException("Formato inválido: " + linha);
    }
}
