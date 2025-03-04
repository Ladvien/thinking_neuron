# neuron_template
A template for the Neuron projects


## Setup Ollama on Ubuntu
1. Install `ollama`
```sh
curl -fsSL https://ollama.com/install.sh | sh
```


## Creating a Discoverable API
- [Richard Madison Maturity Model](https://en.wikipedia.org/wiki/Richardson_Maturity_Model)
- https://github.com/jtc42/fastapi-hypermodel?tab=readme-ov-file

## FastAPI Best Practices
- https://github.com/zhanymkanov/fastapi-best-practices?tab=readme-ov-file


## Setup Ollama Daemon on Manjaro:

1. Instructions - https://github.com/ollama/ollama/blob/main/docs/linux.md
2. Create a file called `/etc/systemd/system/ollama.service` with the following content--and please note, the `HOST` must be set to bind it to the local network:
```sh
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ladvien
Group=ladvien
Restart=always
RestartSec=3
Environment="PATH=$PATH"
Environment="OLLAMA_HOST=0.0.0.0:11434"

[Install]
WantedBy=default.target
```

3. Enable the service:
```sh
sudo systemctl enable ollama
```
4. Start the service:
```sh
sudo systemctl start ollama
```

5. Check the status of the service:
```sh
sudo systemctl status ollama
```

6. Create a file called `/etc/systemd/system/deepseek_r1_runner.service` with the following content:
```sh
[Unit]
Description=Daemon for running DeepseekR1 locally.
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/ollama run deepseek-r1:14b 
User=ladvien
Group=ladvien
Restart=on-failure
SyslogIdentifier=deepseek_r1_runner
RestartSec=5
TimeoutStartSec=infinity
 
[Install]
WantedBy=multi-user.target # Make it accessible to other users
```


Test curl command:
```
curl -X POST http://192.x.x.x:11434/api/generate \
     -H "Content-Type: application/json" \
     -d '{
           "model": "deepseek-r1:14b",
           "prompt": "Explain quantum mechanics in simple terms.",
           "stream": true
         }'
````