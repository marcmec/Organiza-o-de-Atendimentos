package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	duracaoManha    = 210 // 08:00–11:30 (3h30 = 210 min)
	duracaoTarde    = 269 // 13:30–17:59 (teto: reunião deve começar ANTES das 18:00)
	duracaoExpresso = 10
)

type Atendimento struct {
	Nome    string
	Duracao int
	Label   string 
}

type Sessao struct {
	Turno        string
	HoraInicio   time.Time
	Capacidade   int
	Atendimentos []Atendimento
	TempoOcupado int
}

func (s *Sessao) Cabe(a Atendimento) bool {
	return s.TempoOcupado+a.Duracao <= s.Capacidade
}

func (s *Sessao) Adicionar(a Atendimento) {
	s.Atendimentos = append(s.Atendimentos, a)
	s.TempoOcupado += a.Duracao
}

type Consultorio struct {
	ID    int
	Manha *Sessao
	Tarde *Sessao
}


func novaSessao(turno string) *Sessao {
	cfg := map[string]struct {
		inicio string
		cap    int
	}{
		"manha": {"08:00", duracaoManha},
		"tarde": {"13:30", duracaoTarde},
	}
	c := cfg[turno]
	t, _ := time.Parse("15:04", c.inicio)
	return &Sessao{Turno: turno, HoraInicio: t, Capacidade: c.cap}
}

func novoConsultorio(id int) *Consultorio {
	return &Consultorio{
		ID:    id,
		Manha: novaSessao("manha"),
		Tarde: novaSessao("tarde"),
	}
}


func parseAtendimento(linha string) (Atendimento, error) {
	partes := strings.Fields(strings.TrimSpace(linha))
	if len(partes) < 2 {
		return Atendimento{}, fmt.Errorf("linha muito curta: %q", linha)
	}

	ultimo := strings.ToLower(partes[len(partes)-1])
	nome := strings.Join(partes[:len(partes)-1], " ")

	if ultimo == "expresso" {
		return Atendimento{Nome: nome, Duracao: duracaoExpresso, Label: "expresso"}, nil
	}

	if strings.HasSuffix(ultimo, "min") {
		durStr := strings.TrimSuffix(ultimo, "min")
		dur, err := strconv.Atoi(durStr)
		if err != nil || dur <= 0 {
			return Atendimento{}, fmt.Errorf("duração inválida: %q", ultimo)
		}
		return Atendimento{Nome: nome, Duracao: dur, Label: ultimo}, nil
	}

	return Atendimento{}, fmt.Errorf("formato não reconhecido: %q", ultimo)
}


func organizar(atendimentos []Atendimento) ([]*Consultorio, []Atendimento) {
	// FFD: ordena do maior para o menor — reduz fragmentação
	sort.Slice(atendimentos, func(i, j int) bool {
		return atendimentos[i].Duracao > atendimentos[j].Duracao
	})

	var consultorios []*Consultorio
	var naoAlocados []Atendimento

	for _, at := range atendimentos {
		alocado := false

		// 1ª passagem: tenta todas as manhãs existentes
		for _, c := range consultorios {
			if c.Manha.Cabe(at) {
				c.Manha.Adicionar(at)
				alocado = true
				break
			}
		}

		// 2ª passagem: tenta todas as tardes existentes
		if !alocado {
			for _, c := range consultorios {
				if c.Tarde.Cabe(at) {
					c.Tarde.Adicionar(at)
					alocado = true
					break
				}
			}
		}

		// 3ª passagem: abre novo consultório
		if !alocado {
			c := novoConsultorio(len(consultorios) + 1)
			switch {
			case c.Manha.Cabe(at):
				c.Manha.Adicionar(at)
				alocado = true
			case c.Tarde.Cabe(at):
				// Atendimento grande demais para a manhã mas cabe na tarde
				c.Tarde.Adicionar(at)
				alocado = true
			}
			if alocado {
				consultorios = append(consultorios, c)
			}
		}

		// Atendimento não cabe em nenhuma sessão (ex: duração > 269min)
		if !alocado {
			naoAlocados = append(naoAlocados, at)
		}
	}

	return consultorios, naoAlocados
}


func imprimir(consultorios []*Consultorio) {
	t17, _ := time.Parse("15:04", "17:00")
	t18, _ := time.Parse("15:04", "18:00")

	for _, c := range consultorios {
		fmt.Printf("Consultório %d:\n", c.ID)

		// Sessão da manhã
		if len(c.Manha.Atendimentos) > 0 {
			atual := c.Manha.HoraInicio
			for _, at := range c.Manha.Atendimentos {
				fmt.Printf("  %s %s %s\n", atual.Format("15:04"), at.Nome, at.Label)
				atual = atual.Add(time.Duration(at.Duracao) * time.Minute)
			}
			fmt.Println("  11:30 Higienização")
		}

		// Sessão da tarde
		if len(c.Tarde.Atendimentos) > 0 {
			atual := c.Tarde.HoraInicio
			for _, at := range c.Tarde.Atendimentos {
				fmt.Printf("  %s %s %s\n", atual.Format("15:04"), at.Nome, at.Label)
				atual = atual.Add(time.Duration(at.Duracao) * time.Minute)
			}

			reuniao := atual
			if reuniao.Before(t17) {
				reuniao = t17
			}

			// Validação: reunião deve começar antes das 18:00
			if !reuniao.Before(t18) {
				fmt.Fprintf(os.Stderr,
					"ERRO Consultório %d: tarde sobrecarregada — reunião seria às %s (limite: 17:59)\n",
					c.ID, reuniao.Format("15:04"))
			}

			fmt.Printf("  %s Reunião de encerramento\n", reuniao.Format("15:04"))
		}

		fmt.Println()
	}
}

func main() {
	file, err := os.Open("atendimentos.txt")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Erro ao abrir arquivo: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	var atendimentos []Atendimento
	scanner := bufio.NewScanner(file)
	for numLinha := 1; scanner.Scan(); numLinha++ {
		texto := scanner.Text()
		if strings.TrimSpace(texto) == "" {
			continue
		}
		at, err := parseAtendimento(texto)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Linha %d ignorada — %v\n", numLinha, err)
			continue
		}
		atendimentos = append(atendimentos, at)
	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "Erro de leitura: %v\n", err)
		os.Exit(1)
	}

	if len(atendimentos) == 0 {
		fmt.Fprintln(os.Stderr, "Nenhum atendimento válido encontrado.")
		os.Exit(1)
	}

	consultorios, naoAlocados := organizar(atendimentos)
	imprimir(consultorios)

	if len(naoAlocados) > 0 {
		fmt.Fprintln(os.Stderr, "AVISO: atendimentos que não cabem em nenhuma sessão:")
		for _, at := range naoAlocados {
			fmt.Fprintf(os.Stderr, "  ✗ %s (%dmin)\n", at.Nome, at.Duracao)
		}
		os.Exit(2)
	}
}