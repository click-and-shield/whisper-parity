# Ollama notes

## Install "ollama"

Go to [Download Ollama](https://ollama.com/download/linux)

Install the IA:

	curl -fsSL https://ollama.com/install.sh | sh

## CLI commands

> See [CLI commands](https://github.com/ollama/ollama)

**Pull a model**:

	ollama pull llama3.2
    ollama pull deepseek-r1

> See [https://ollama.com/library](https://ollama.com/library)

**Start a model** (will also pull the model):

	ollama run llama3.2

**Remove a model**:

	ollama rm llama3.2

**Pass the prompt as an argument**:

	ollama run llama3.2 "Summarize this file: $(cat README.md)"

**List models on your computer**:

	ollama list

**List which models are currently loaded**:

	ollama ps

**Stop a model**:

	ollama stop llama3.2

**Start Ollama**:

	ollama serve

**Check that the service is up**:

```
dev@focus:~$ systemctl status ollama
● ollama.service - Ollama Service
     Loaded: loaded (/etc/systemd/system/ollama.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2025-06-03 20:00:35 UTC; 8min ago
   Main PID: 4258 (ollama)
      Tasks: 13 (limit: 76505)
     Memory: 23.7M
        CPU: 200ms
     CGroup: /system.slice/ollama.service
             └─4258 /usr/local/bin/ollama serve
```

