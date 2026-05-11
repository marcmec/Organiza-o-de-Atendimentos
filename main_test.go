package main

import (
	"testing"
	"time"
)

// ──────────────────────────────────────────────
// parseAtendimento
// ──────────────────────────────────────────────

func TestParseAtendimento_Minutos(t *testing.T) {
	at, err := parseAtendimento("Castração de gato adulto 90min")
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	if at.Nome != "Castração de gato adulto" {
		t.Errorf("Nome: got %q, want %q", at.Nome, "Castração de gato adulto")
	}
	if at.Duracao != 90 {
		t.Errorf("Duracao: got %d, want 90", at.Duracao)
	}
	if at.Label != "90min" {
		t.Errorf("Label: got %q, want %q", at.Label, "90min")
	}
}

func TestParseAtendimento_Expresso(t *testing.T) {
	at, err := parseAtendimento("Aplicação de vacina antirrábica expresso")
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	if at.Nome != "Aplicação de vacina antirrábica" {
		t.Errorf("Nome: got %q", at.Nome)
	}
	if at.Duracao != duracaoExpresso {
		t.Errorf("Duracao: got %d, want %d", at.Duracao, duracaoExpresso)
	}
	if at.Label != "expresso" {
		t.Errorf("Label: got %q, want %q", at.Label, "expresso")
	}
}

func TestParseAtendimento_ExpressoMaiusculo(t *testing.T) {
	// O enunciado diz que nomes não contêm números — mas "EXPRESSO" em caixa alta
	// deve ser reconhecido pela normalização com ToLower.
	_, err := parseAtendimento("Microchipagem EXPRESSO")
	if err != nil {
		t.Errorf("EXPRESSO em maiúsculo deveria ser aceito, erro: %v", err)
	}
}

func TestParseAtendimento_EspacosExtras(t *testing.T) {
	at, err := parseAtendimento("  Consulta de rotina 30min  ")
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	if at.Duracao != 30 {
		t.Errorf("Duracao: got %d, want 30", at.Duracao)
	}
}

func TestParseAtendimento_ErroDuracaoZero(t *testing.T) {
	_, err := parseAtendimento("Consulta 0min")
	if err == nil {
		t.Error("deveria retornar erro para duração zero")
	}
}

func TestParseAtendimento_ErroDuracaoNegativa(t *testing.T) {
	_, err := parseAtendimento("Consulta -30min")
	if err == nil {
		t.Error("deveria retornar erro para duração negativa")
	}
}

func TestParseAtendimento_ErroDuracaoNaoNumerica(t *testing.T) {
	_, err := parseAtendimento("Consulta abcmin")
	if err == nil {
		t.Error("deveria retornar erro para duração não numérica")
	}
}

func TestParseAtendimento_ErroFormatoDesconhecido(t *testing.T) {
	_, err := parseAtendimento("Consulta de rotina horas")
	if err == nil {
		t.Error("deveria retornar erro para formato desconhecido")
	}
}

func TestParseAtendimento_ErroLinhaCurta(t *testing.T) {
	_, err := parseAtendimento("somenteuma")
	if err == nil {
		t.Error("deveria retornar erro para linha com uma única palavra")
	}
}

func TestParseAtendimento_ErroLinhaVazia(t *testing.T) {
	_, err := parseAtendimento("   ")
	if err == nil {
		t.Error("deveria retornar erro para linha vazia")
	}
}

// ──────────────────────────────────────────────
// Sessao.Cabe / Sessao.Adicionar
// ──────────────────────────────────────────────

func TestSessaoCabe_VaziaAceita(t *testing.T) {
	s := novaSessao("manha")
	at := Atendimento{Duracao: 60}
	if !s.Cabe(at) {
		t.Error("sessão vazia deveria aceitar atendimento de 60min")
	}
}

func TestSessaoCabe_FronteirExata(t *testing.T) {
	s := novaSessao("manha") // capacidade 210
	at := Atendimento{Duracao: 210}
	if !s.Cabe(at) {
		t.Error("atendimento exatamente no limite deveria caber")
	}
}

func TestSessaoCabe_UmMinutoAlem(t *testing.T) {
	s := novaSessao("manha") // capacidade 210
	at := Atendimento{Duracao: 211}
	if s.Cabe(at) {
		t.Error("atendimento um minuto além do limite não deveria caber")
	}
}

func TestSessaoCabe_CheiaNaoAceita(t *testing.T) {
	s := novaSessao("manha")
	s.Adicionar(Atendimento{Duracao: 210})
	if s.Cabe(Atendimento{Duracao: 1}) {
		t.Error("sessão cheia não deveria aceitar nenhum atendimento")
	}
}

func TestSessaoAdicionar_AtualizaTempoELista(t *testing.T) {
	s := novaSessao("tarde")
	a1 := Atendimento{Nome: "A", Duracao: 60}
	a2 := Atendimento{Nome: "B", Duracao: 45}
	s.Adicionar(a1)
	s.Adicionar(a2)

	if s.TempoOcupado != 105 {
		t.Errorf("TempoOcupado: got %d, want 105", s.TempoOcupado)
	}
	if len(s.Atendimentos) != 2 {
		t.Errorf("len(Atendimentos): got %d, want 2", len(s.Atendimentos))
	}
}

// ──────────────────────────────────────────────
// novaSessao / novoConsultorio
// ──────────────────────────────────────────────

func TestNovaSessaoManha(t *testing.T) {
	s := novaSessao("manha")
	if s.Capacidade != duracaoManha {
		t.Errorf("Capacidade manhã: got %d, want %d", s.Capacidade, duracaoManha)
	}
	if s.HoraInicio.Format("15:04") != "08:00" {
		t.Errorf("HoraInicio manhã: got %q, want %q", s.HoraInicio.Format("15:04"), "08:00")
	}
}

func TestNovaSessaoTarde(t *testing.T) {
	s := novaSessao("tarde")
	if s.Capacidade != duracaoTarde {
		t.Errorf("Capacidade tarde: got %d, want %d", s.Capacidade, duracaoTarde)
	}
	if s.HoraInicio.Format("15:04") != "13:30" {
		t.Errorf("HoraInicio tarde: got %q, want %q", s.HoraInicio.Format("15:04"), "13:30")
	}
}

func TestNovoConsultorio(t *testing.T) {
	c := novoConsultorio(3)
	if c.ID != 3 {
		t.Errorf("ID: got %d, want 3", c.ID)
	}
	if c.Manha == nil || c.Tarde == nil {
		t.Fatal("Manha ou Tarde são nil")
	}
}

// ──────────────────────────────────────────────
// organizar — comportamento do algoritmo
// ──────────────────────────────────────────────

func ats(duracoes ...int) []Atendimento {
	result := make([]Atendimento, len(duracoes))
	for i, d := range duracoes {
		result[i] = Atendimento{Nome: "X", Duracao: d, Label: "Xmin"}
	}
	return result
}

func TestOrganizar_AtendimentoUnico(t *testing.T) {
	cs, nao := organizar(ats(60))
	if len(cs) != 1 {
		t.Fatalf("esperava 1 consultório, got %d", len(cs))
	}
	if len(nao) != 0 {
		t.Errorf("esperava 0 não alocados, got %d", len(nao))
	}
	if len(cs[0].Manha.Atendimentos) != 1 {
		t.Error("atendimento único deveria ir para a manhã")
	}
}

func TestOrganizar_TodosExpressos(t *testing.T) {
	// 21 expressos = 210 min → cabe exatamente em 1 manhã
	entrada := make([]Atendimento, 21)
	for i := range entrada {
		entrada[i] = Atendimento{Nome: "Vacina", Duracao: 10, Label: "expresso"}
	}
	cs, nao := organizar(entrada)
	if len(nao) != 0 {
		t.Errorf("esperava 0 não alocados, got %d", len(nao))
	}
	totalManha := 0
	for _, c := range cs {
		totalManha += c.Manha.TempoOcupado
	}
	if totalManha != 210 {
		t.Errorf("tempo total de manhã: got %d, want 210", totalManha)
	}
}

func TestOrganizar_FFDOrdenaPorDuracao(t *testing.T) {
	// Entra desordenado; o maior deve ser alocado primeiro (FFD).
	entrada := []Atendimento{
		{Nome: "Pequeno", Duracao: 30},
		{Nome: "Grande", Duracao: 120},
		{Nome: "Medio", Duracao: 60},
	}
	cs, _ := organizar(entrada)
	// Após FFD, o primeiro atendimento da manhã do primeiro consultório
	// deve ser o maior (120).
	primeiro := cs[0].Manha.Atendimentos[0]
	if primeiro.Duracao != 120 {
		t.Errorf("FFD: esperava duração 120 primeiro, got %d", primeiro.Duracao)
	}
}

func TestOrganizar_UsaTardeDoMesmoConsultorioAvantesDeAbrirNovoFFD(t *testing.T) {
	// FFD: com {210, 60}, o 60 cabe na tarde do C1 — o algoritmo deve
	// aproveitar a tarde existente antes de abrir um segundo consultório.
	entrada := []Atendimento{
		{Nome: "A", Duracao: 210}, // preenche manhã C1
		{Nome: "B", Duracao: 60},  // deve ir para a tarde do C1 (não abre C2)
	}
	cs, _ := organizar(entrada)
	if len(cs) != 1 {
		t.Fatalf("esperava 1 consultório (tarde do C1 ainda tem espaço), got %d", len(cs))
	}
	if len(cs[0].Tarde.Atendimentos) != 1 {
		t.Error("item B deveria ter ido para a tarde do C1")
	}
}

func TestOrganizar_AbreNovoConsultorioQuandoTodasSessoesEstaoCheia(t *testing.T) {
	// Quando manhã e tarde do C1 estão ocupadas, um novo consultório é aberto.
	// {210, 269, 60}: A→manhã C1, B→tarde C1, C→manhã C2
	entrada := []Atendimento{
		{Nome: "A", Duracao: 210},
		{Nome: "B", Duracao: 269},
		{Nome: "C", Duracao: 60},
	}
	cs, _ := organizar(entrada)
	if len(cs) < 2 {
		t.Fatalf("esperava ao menos 2 consultórios, got %d", len(cs))
	}
	if len(cs[1].Manha.Atendimentos) == 0 {
		t.Error("item C deveria ir para a manhã do C2")
	}
}

func TestOrganizar_GrandeDemaisParaManha_CabeNaTarde(t *testing.T) {
	// 211 min: não cabe na manhã (210), mas cabe na tarde (269)
	cs, nao := organizar(ats(211))
	if len(nao) != 0 {
		t.Fatalf("atendimento de 211min deveria ser alocado (cabe na tarde), got naoAlocados=%d", len(nao))
	}
	if len(cs) != 1 {
		t.Fatalf("esperava 1 consultório, got %d", len(cs))
	}
	if len(cs[0].Tarde.Atendimentos) != 1 {
		t.Error("atendimento de 211min deveria estar na tarde")
	}
	if len(cs[0].Manha.Atendimentos) != 0 {
		t.Error("manhã deveria estar vazia")
	}
}

func TestOrganizar_NaoAlocaAtendimentoMaiorQueQualquerSessao(t *testing.T) {
	cs, nao := organizar(ats(300)) // 300 > duracaoTarde(269)
	if len(nao) != 1 {
		t.Errorf("esperava 1 não alocado, got %d", len(nao))
	}
	if len(cs) != 0 {
		t.Errorf("nenhum consultório deveria ser criado, got %d", len(cs))
	}
}

func TestOrganizar_NenhumAtendimento(t *testing.T) {
	cs, nao := organizar([]Atendimento{})
	if len(cs) != 0 {
		t.Errorf("esperava 0 consultórios, got %d", len(cs))
	}
	if len(nao) != 0 {
		t.Errorf("esperava 0 não alocados, got %d", len(nao))
	}
}

func TestOrganizar_SessaoNuncaExcedeCapacidade(t *testing.T) {
	// Lista variada — verifica que nenhuma sessão ultrapassa seu limite
	entrada := []Atendimento{
		{Duracao: 90}, {Duracao: 90}, {Duracao: 90},
		{Duracao: 60}, {Duracao: 60}, {Duracao: 60},
		{Duracao: 45}, {Duracao: 45}, {Duracao: 30},
		{Duracao: 30}, {Duracao: 10}, {Duracao: 10},
	}
	cs, _ := organizar(entrada)
	for _, c := range cs {
		if c.Manha.TempoOcupado > duracaoManha {
			t.Errorf("C%d: manhã excedeu capacidade (%d > %d)",
				c.ID, c.Manha.TempoOcupado, duracaoManha)
		}
		if c.Tarde.TempoOcupado > duracaoTarde {
			t.Errorf("C%d: tarde excedeu capacidade (%d > %d)",
				c.ID, c.Tarde.TempoOcupado, duracaoTarde)
		}
	}
}

func TestOrganizar_TodosAtendimentosAlocados(t *testing.T) {
	// Todos os 23 atendimentos do enunciado devem ser alocados
	entrada := []Atendimento{
		{Duracao: 90}, {Duracao: 10}, {Duracao: 45}, {Duracao: 30},
		{Duracao: 30}, {Duracao: 120}, {Duracao: 45}, {Duracao: 10},
		{Duracao: 30}, {Duracao: 60}, {Duracao: 45}, {Duracao: 60},
		{Duracao: 90}, {Duracao: 30}, {Duracao: 60}, {Duracao: 30},
		{Duracao: 10}, {Duracao: 45}, {Duracao: 30}, {Duracao: 30},
		{Duracao: 90}, {Duracao: 60}, {Duracao: 45},
	}
	cs, nao := organizar(entrada)

	if len(nao) != 0 {
		t.Errorf("esperava 0 não alocados, got %d", len(nao))
	}

	totalAlocado := 0
	for _, c := range cs {
		totalAlocado += len(c.Manha.Atendimentos) + len(c.Tarde.Atendimentos)
	}
	if totalAlocado != len(entrada) {
		t.Errorf("total alocado: got %d, want %d", totalAlocado, len(entrada))
	}
}

func TestOrganizar_UsaTresConsultorios(t *testing.T) {
	// A entrada do enunciado deve gerar exatamente 3 consultórios
	entrada := []Atendimento{
		{Duracao: 90}, {Duracao: 10}, {Duracao: 45}, {Duracao: 30},
		{Duracao: 30}, {Duracao: 120}, {Duracao: 45}, {Duracao: 10},
		{Duracao: 30}, {Duracao: 60}, {Duracao: 45}, {Duracao: 60},
		{Duracao: 90}, {Duracao: 30}, {Duracao: 60}, {Duracao: 30},
		{Duracao: 10}, {Duracao: 45}, {Duracao: 30}, {Duracao: 30},
		{Duracao: 90}, {Duracao: 60}, {Duracao: 45},
	}
	cs, _ := organizar(entrada)
	if len(cs) != 3 {
		t.Errorf("esperava 3 consultórios, got %d", len(cs))
	}
}

// ──────────────────────────────────────────────
// Invariantes de horário após organizar
// ──────────────────────────────────────────────

func TestReuniaoDentroDoLimite(t *testing.T) {
	t17, _ := time.Parse("15:04", "17:00")
	t18, _ := time.Parse("15:04", "18:00")

	entrada := []Atendimento{
		{Duracao: 90}, {Duracao: 10}, {Duracao: 45}, {Duracao: 30},
		{Duracao: 30}, {Duracao: 120}, {Duracao: 45}, {Duracao: 10},
		{Duracao: 30}, {Duracao: 60}, {Duracao: 45}, {Duracao: 60},
		{Duracao: 90}, {Duracao: 30}, {Duracao: 60}, {Duracao: 30},
		{Duracao: 10}, {Duracao: 45}, {Duracao: 30}, {Duracao: 30},
		{Duracao: 90}, {Duracao: 60}, {Duracao: 45},
	}
	cs, _ := organizar(entrada)

	for _, c := range cs {
		if len(c.Tarde.Atendimentos) == 0 {
			continue
		}

		// Calcula hora da reunião
		reuniao := c.Tarde.HoraInicio.Add(
			time.Duration(c.Tarde.TempoOcupado) * time.Minute,
		)
		if reuniao.Before(t17) {
			reuniao = t17
		}

		if reuniao.Before(t17) {
			t.Errorf("C%d: reunião às %s — antes das 17:00", c.ID, reuniao.Format("15:04"))
		}
		if !reuniao.Before(t18) {
			t.Errorf("C%d: reunião às %s — 18:00 ou depois", c.ID, reuniao.Format("15:04"))
		}
	}
}

func TestManhaNaoPassaDas1130(t *testing.T) {
	tLimite := 210 // 08:00 + 210min = 11:30

	entrada := []Atendimento{
		{Duracao: 90}, {Duracao: 60}, {Duracao: 60}, {Duracao: 30},
	}
	cs, _ := organizar(entrada)
	for _, c := range cs {
		if c.Manha.TempoOcupado > tLimite {
			t.Errorf("C%d: manhã com %dmin — excede 11:30", c.ID, c.Manha.TempoOcupado)
		}
	}
}

// ──────────────────────────────────────────────
// parseAtendimento — casos de fronteira adicionais
// ──────────────────────────────────────────────

func TestParseAtendimento_DuracaoGrande(t *testing.T) {
	at, err := parseAtendimento("Cirurgia longa 269min")
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	if at.Duracao != 269 {
		t.Errorf("Duracao: got %d, want 269", at.Duracao)
	}
}

func TestParseAtendimento_NomeComDoisPontos(t *testing.T) {
	// Garante que nomes com ":" não quebram o parse (ex: "Resgate emocional: socialização...")
	at, err := parseAtendimento("Resgate emocional: socialização de gato feral 60min")
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	if at.Duracao != 60 {
		t.Errorf("Duracao: got %d, want 60", at.Duracao)
	}
	if at.Nome != "Resgate emocional: socialização de gato feral" {
		t.Errorf("Nome: got %q", at.Nome)
	}
}