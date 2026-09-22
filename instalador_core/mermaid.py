# -*- coding: utf-8 -*-
"""Geradores de diagrama mermaid: o mapa do material e o fluxo do curso.
Saída compatível com Obsidian (native), GitHub (.mmd renderizado) e mermaid.live."""


def _seguro(t):
    return str(t).replace('"', "'").replace("\n", " ")


def mapa_mermaid(mapa, max_nos=26):
    tops = sorted(mapa.get("arquivos", []), key=lambda a: -a["linhas"])[:max_nos]
    ids = {a["caminho"]: "n%d" % i for i, a in enumerate(tops)}
    entrada = (mapa.get("leitura_sugerida") or [""])[0]

    risco = {}
    for r in mapa.get("riscos", []):
        if r["arquivo"] in ids:
            sev = {"critico": 3, "alto": 2, "medio": 1, "baixo": 0}.get(r.get("nivel", ""), 0)
            risco[r["arquivo"]] = max(risco.get(r["arquivo"], 0), sev)

    L = ["flowchart TD"]
    L.append('    ALVO(["%s"])' % _seguro(mapa.get("nome", "material")))
    classes = {}
    for a in tops:
        nid = ids[a["caminho"]]
        rotulo = "%s<br/>%s linhas" % (_seguro(a["caminho"]), a["linhas"])
        cls = "ok"
        if risco.get(a["caminho"], 0) >= 3:
            cls = "critico"
        elif risco.get(a["caminho"], 0) == 2:
            cls = "alto"
        elif risco.get(a["caminho"], 0) == 1:
            cls = "medio"
        extra = ""
        if a["caminho"] == entrada:
            extra = " ⚑"
            cls += ",entrada"
        L.append('    %s["%s%s"]:::%s' % (nid, rotulo, extra, cls.split(",")[0]))
        classes[nid] = cls
    ALVO_LIGADO = False
    for src, dst in mapa.get("grafo", []):
        if src in ids and dst in ids:
            L.append("    %s --> %s" % (ids[src], ids[dst]))
            ALVO_LIGADO = True
    if tops and not ALVO_LIGADO:
        L.append("    ALVO -.-> %s" % ids[tops[0]["caminho"]])
    elif tops:
        L.append("    ALVO --> %s" % ids[entrada if entrada in ids else tops[0]["caminho"]])
    for nid, cls in sorted(classes.items()):
        partes = cls.split(",")
        if len(partes) > 1:
            L.append("    class %s %s" % (nid, partes[-1]))
    n_riscos = len(mapa.get("riscos", [])) + len(mapa.get("estruturais", []))
    L.append('    R(["riscos mapeados: %d"]):::risco' % n_riscos)
    for a in tops:
        if risco.get(a["caminho"], 0) >= 1:
            L.append("    R -.-> %s" % ids[a["caminho"]])
    L.append("    classDef ok fill:#EEF2F8,stroke:#5A6B85,color:#1C2733")
    L.append("    classDef critico fill:#E06C5A,stroke:#7A1F12,color:#fff")
    L.append("    classDef alto fill:#F0B45A,stroke:#8A5A10,color:#3A2A05")
    L.append("    classDef medio fill:#F5DEA0,stroke:#8A7420,color:#3A3205")
    L.append("    classDef risco fill:#FBEAEA,stroke:#B4403A,color:#7A1F12")
    L.append("    classDef entrada stroke-width:3px,stroke:#1D5FD6")
    return "\n".join(L)


def curso_mermaid(curso, confianca=None):
    conf = confianca if confianca is not None else (curso or {}).get("juizo", {}).get("confianca", "?")
    fases = (curso or {}).get("fases", [])
    titulos = {f["n"]: f["titulo"].split(" — ")[0] for f in fases}
    L = ["flowchart TD"]
    L.append('    A(["material: código, programa ou pasta"])')
    L.append('    D["Destripador — destrincha tudo"]')
    L.append('    M[("mapa estrutural<br/>arquivos · símbolos · riscos")]')
    L.append('    P["Professor — monta 6 fases"]')
    L.append('    C{{"Cético desafia"}}')
    L.append('    V{{"Convicto defende"}}')
    L.append('    J{{"Juiz decide"}}')
    L.append("    A --> D --> M --> P")
    L.append("    P --> C")
    L.append("    P --> V")
    L.append("    C --> J")
    L.append("    V --> J")
    L.append('    J -->|"confiança %s/100"| S{"material aprovado para virar ensino?"}' % conf)
    L.append('    S -->|sim| O1[["curso.pdf"]]')
    L.append('    S -->|sim| O2[["curso.docx"]]')
    L.append('    S -->|sim| O3[["curso.md + mapa.json<br/>para agentes"]]')
    L.append('    S -->|sim| O4[["obsidian/<br/>vault do aluno"]]')
    L.append('    S -->|sim| O5[["mapa.mmd + curso.mmd"]]')
    if fases:
        ultimo = None
        for f in fases:
            L.append('    F%d["Fase %d — %s"]' % (f["n"], f["n"], _seguro(titulos.get(f["n"], f["titulo"]))))
            ultimo = f["n"]
            if f["n"] > 1:
                L.append("    F%d --> F%d" % (f["n"] - 1, f["n"]))
        L.append("    J --> F1")
        L.append("    F%d --> O1" % ultimo)
    L.append("    classDef agente fill:#EEF2F8,stroke:#5A6B85")
    L.append("    classDef saida fill:#E2F2E8,stroke:#1F7A4D")
    L.append("    class O1,O2,O3,O4,O5 saida")
    return "\n".join(L)
