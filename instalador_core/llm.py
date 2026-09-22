# -*- coding: utf-8 -*-
"""Backend de IA opcional: Ollama local → OpenAI → OpenRouter → silêncio.
Sem nenhum deles, todo o sistema roda no motor determinístico (heurísticas
reais sobre o código): curso completo nasce até offline."""
import json
import os
import socket
import urllib.request

_CACHE = {}


def porta_aberta(host, porta, tempo=0.5):
    try:
        s = socket.create_connection((host, porta), timeout=tempo)
        s.close()
        return True
    except OSError:
        return False


def detectar():
    """Retorna (backend, modelo) ou None."""
    if "detecao" in _CACHE:
        return _CACHE["detecao"]
    backend = None
    if os.environ.get("INSTALADOR_SEM_IA") == "1":
        backend = None
    elif os.environ.get("OLLAMA_HOST") or porta_aberta("127.0.0.1", 11434):
        backend = ("ollama", os.environ.get("OLLAMA_MODEL", "llama3.2"))
    elif os.environ.get("OPENAI_API_KEY"):
        backend = ("openai", os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    elif os.environ.get("OPENROUTER_API_KEY"):
        backend = ("openrouter", os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"))
    _CACHE["detecao"] = backend
    return backend


def chamar(sistema, usuario, max_caracteres=1400, timeout=60):
    """Retorna texto do modelo, ou None (quem chama cai no motor local)."""
    det = detectar()
    if not det:
        return None
    nome, modelo = det
    try:
        if nome == "ollama":
            host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
            corpo = {"model": modelo, "stream": False,
                     "messages": [{"role": "system", "content": sistema},
                                  {"role": "user", "content": usuario}]}
            url = host + "/api/chat"
            chave = None
        else:
            if nome == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                chave = os.environ["OPENAI_API_KEY"]
            else:
                url = "https://openrouter.ai/api/v1/chat/completions"
                chave = os.environ["OPENROUTER_API_KEY"]
            corpo = {"model": modelo,
                     "messages": [{"role": "system", "content": sistema},
                                  {"role": "user", "content": usuario}],
                     "max_tokens": max(120, max_caracteres // 3)}
        headers = {"Content-Type": "application/json"}
        if chave:
            headers["Authorization"] = "Bearer " + chave
        req = urllib.request.Request(url, data=json.dumps(corpo).encode("utf-8"),
                                     headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode("utf-8"))
        if nome == "ollama":
            txt = d.get("message", {}).get("content", "")
        else:
            txt = d["choices"][0]["message"]["content"]
        txt = (txt or "").strip()
        return txt[:max_caracteres] if txt else None
    except Exception:
        return None
