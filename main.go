package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
)

// Структура для параметров запроса
type BenchParams struct {
	DbName       string `json:"dbname"`
	ScaleFactor  string `json:"scaleFactor" `
	Clients      string `json:"clients"`
	Threads      string `json:"threads" `
	Transactions string `json:"transactions"`
}

// Функция для запуска pgbench
func runPgBench(params BenchParams) (string, error) {
	// Инициализация базы данных для тестирования
	initCmd := exec.Command("pgbench", "-i", "-s", params.ScaleFactor, params.DbName)
	if err := initCmd.Run(); err != nil {
		return "", err
	}

	// Запуск теста
	runCmd := exec.Command("pgbench", "-c", params.Clients, "-j", params.Threads, "-t", params.Transactions, params.DbName)
	output, err := runCmd.CombinedOutput()
	if err != nil {
		return "", err
	}

	return string(output), nil
}

// Обработчик HTTP запроса
func benchHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Unsupported method", http.StatusMethodNotAllowed)
		return
	}

	var params BenchParams
	err := json.NewDecoder(r.Body).Decode(&params)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	output, err := runPgBench(params)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "pgbench output:\n%s", output)
}

func main() {
	// exec.Command("sudo -i -u postgres")
	http.HandleFunc("/bench", benchHandler)

	fmt.Println("Server is running on port 8080...")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
