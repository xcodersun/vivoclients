package main

import (
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"
	"github.com/gorilla/websocket"
)

var origin = "http://localhost/"

var url = "ws://localhost:8081/channels/dNPbBY7op5zxqLen/devices/mactest1/ws?room=garage&floor=1st"

func main() {
	log.SetFlags(0)

	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt)

	log.Printf("connecting to %s", url)

	header := http.Header(make(map[string][]string))
	header.Add("AccessToken", "1234abcd")

	ws, _, err := websocket.DefaultDialer.Dial(url, header)
	if err != nil {
		log.Fatal("dial:", err)
	}

	ws.SetPongHandler(func(payload string) error {
		log.Printf("Pong: %s", payload)
		return nil
	})

	defer ws.Close()

	done := make(chan struct{})

	go func() {
		defer ws.Close()
		defer close(done)
		for {
			_, message, err := ws.ReadMessage()
			if err != nil {
				log.Println("read:", err)
				return
			}
			log.Printf("recv: %s", message)
		}
	}()

	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			err := ws.WriteMessage(websocket.PingMessage, []byte{})
			if err != nil {
				log.Println("write:", err)
				return
			}
		case <-interrupt:
			log.Println("interrupt")
			err := ws.WriteMessage(websocket.CloseMessage, websocket.FormatCloseMessage(websocket.CloseNormalClosure, ""))
			if err != nil {
				log.Println("write close:", err)
				return
			}
			select {
			case <-done:
			case <-time.After(time.Second):
			}
			ws.Close()
			return
		}
	}
}