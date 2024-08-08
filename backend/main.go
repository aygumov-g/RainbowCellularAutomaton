package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"maps"
	"net/http"
	"strconv"
	"strings"
)

type Cell struct {
	Status   bool   `json:"status"`
	Color    [3]int `json:"color"`
	LongTime int    `json:"long_time"`
}

type Request struct {
	Net                map[string]Cell `json:"net"`
	DefaultCellColor   [3]int          `json:"default_cell_color"`
	EffectCellColor    [3]int          `json:"effect_cell_color"`
	LongTimeCellColors [][][]int       `json:"long_time_cell_colors"`
}

func brain(request Request) map[string]Cell {
	var neighbours = [][]int{
		{1, 0}, {1, 1}, {0, 1}, {-1, 1},
		{-1, 0}, {-1, -1}, {0, -1}, {1, -1},
	}
	var output = maps.Clone(request.Net)
	for key := range request.Net {
		xAndy, state := strings.Split(key, ":"), [2]int{0, 0}
		for _, neighbour := range neighbours {
			newX, _ := strconv.Atoi(xAndy[0])
			newY, _ := strconv.Atoi(xAndy[1])
			newX += neighbour[0]
			newY += neighbour[1]
			if _, ok := request.Net[fmt.Sprintf("%d:%d", newX, newY)]; ok {
				/*
					Сюда попадаем, если итерируемый сосед
					текущей клетки существует на поле.
				*/

				if request.Net[fmt.Sprintf("%d:%d", newX, newY)].Status {
					/*
						Сюда попадаем если текущий итерируемый
						сосед текущей клетки живой.
					*/

					state[0] += 1
				} else {
					/*
						Сюда попадаем если текущий итерируемый
						сосед текущей клетки мёртвый.
					*/

					state[1] += 1
				}
			}
		}
		if request.Net[key].Status {
			/*
				Сюда попадаем если текущая клетка живая.
			*/

			if !(state[0] == 2 || state[0] == 3) {
				//if !(state[0] == 1 || state[0] == 2 || state[0] == 3 || state[0] == 4 || state[0] == 5) {
				/*
					Сюда попадаем если у текущей живой клетки нет либо двух, либо трёх
					живых соседей, для того чтобы убить эту текущую клетку.
				*/

				output[key] = Cell{Status: false, Color: request.DefaultCellColor, LongTime: 0}
			} else {
				/*
					Сюда попадаем если у текущей живой клетки такая ситуация, что она
					остаётся живой, для того чтобы поставить ей цвет по умолчанию.
				*/

				var longTime = request.Net[key].LongTime
				var cell = Cell{Status: true, Color: request.DefaultCellColor, LongTime: longTime + 1}
				for _, valueLonTimeCell := range request.LongTimeCellColors {
					if valueLonTimeCell[2][0] == 0 {
						/*
							Сюда попадаем если специальное значение установлено
							на 0, то бишь, чтобы моргнуть клеткой.
						*/

						if longTime == valueLonTimeCell[1][0] {
							cell.Color = [3]int(valueLonTimeCell[0])
						}
					} else if valueLonTimeCell[2][0] == 1 {
						/*
							Сюда попадаем если специальное значение установлено
							на 1, то бишь, чтобы перекрасить клетку.
						*/

						if longTime >= valueLonTimeCell[1][0] {
							cell.Color = [3]int(valueLonTimeCell[0])
						}
					}
				}
				output[key] = cell
			}
		} else {
			/*
				Сюда попадаем если текущая клетка мёртвая.
			*/

			if state[0] == 3 {
				/*
					Сюда попадаем если у текущей мёртвой клетки есть ровно 3 живых
					соседа, для того чтобы оживить эту текущую клетку.
				*/

				output[key] = Cell{Status: true, Color: request.EffectCellColor}
			}
		}
	}

	return output
}

func handler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "POST" {
			if bytesRequest, err := io.ReadAll(r.Body); !(err != nil) {
				var request Request
				if err := json.Unmarshal(bytesRequest, &request); !(err != nil) {
					if bytesResponse, err := json.Marshal(brain(request)); !(err != nil) {
						_, err := w.Write(bytesResponse)
						if err != nil {
							log.Printf("Ошибка при оптравке ответа клиенту. Error=%s\n", err)
						}
					}
				}
			}
		}
	}
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", handler())
	if err := http.ListenAndServe(":12345", mux); err != nil {
		log.Printf("Сервер не запустился. Error=%s\n", err)
	}
}
