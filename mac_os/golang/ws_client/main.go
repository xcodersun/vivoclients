package main

import (
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"
	"io/ioutil"
	"encoding/json"
	"github.com/gorilla/websocket"
	"fmt"
)

type Config struct {
	Host        string             `json:"host"`
	Port        string             `json:"port"`
	Channel     string             `json:"channel"`
	Device      string             `json:"device"`
	Tags        map[string]string  `json:"tags"`
	AccessToken string             `json:"access_token"`
	Interval    int                `json:"interval"`
}

func main() {
	log.SetFlags(0)

	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt)

	config := getConfig()
	url := getUrl(&config)
	log.Printf("connecting to %s", url)

	header := http.Header(make(map[string][]string))
	header.Add("AccessToken", config.AccessToken)

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

	ticker1 := time.NewTicker(time.Duration(10)*time.Second)
	ticker2 := time.NewTicker(time.Duration(config.Interval)*time.Second)
	defer ticker1.Stop()
	defer ticker2.Stop()

	for {
		select {
		case <-ticker1.C:
			err := ws.WriteMessage(websocket.PingMessage, []byte{})
			if err != nil {
				log.Println("write:", err)
				return
			}
		case <-ticker2.C:
			log.Println("ticker2")
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

func getConfig() Config {
	raw, err := ioutil.ReadFile("./config/example.json")
	if err != nil {
		log.Println(err.Error())
		os.Exit(1)
	}
	var config Config
	json.Unmarshal(raw, &config)
	return config
}

func getUrl(config *Config) string {
	var url = "ws://%s:%s/channels/%s/devices/%s/ws?"
	url = fmt.Sprintf(url, config.Host, config.Port, config.Channel, config.Device)
	if len(config.Tags) != 0 {
		for k, v := range config.Tags {
			url += k + "=" + v + "&"
		}
		sz := len(url)
		url = url[:sz-1]
	}
	return url
}