import matplotlib
matplotlib.use("Agg")  # off-screen rendering, no GUI backend

import argparse, json, math, random
from collections import defaultdict, deque

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import imageio

# --------------------------
# tiny deterministic word vectors (seeded)
# --------------------------
def make_word_table(dim=64, seed=7):
    rnd = np.random.default_rng(seed)
    table = defaultdict(lambda: rnd.normal(0, 1, dim))
    # lock a few domain words for stability
    base = {
        "uncertainty": rnd.normal(0.5, 0.4, dim),
        "truth": rnd.normal(0.6, 0.4, dim),
        "graph": rnd.normal(0.4, 0.4, dim),
        "physarum": rnd.normal(0.8, 0.3, dim),
        "reasoning": rnd.normal(0.7, 0.3, dim),
        "grow": rnd.normal(0.8, 0.3, dim),
        "reinforce": rnd.normal(0.6, 0.3, dim),
        "decay": rnd.normal(0.4, 0.3, dim),
        "verify": rnd.normal(0.6, 0.3, dim),
        "evidence": rnd.normal(0.6, 0.3, dim),
        "similarity": rnd.normal(0.5, 0.3, dim),
        "attention": rnd.normal(0.5, 0.3, dim),
        "question": rnd.normal(0.6, 0.3, dim),
        "answer": rnd.normal(0.6, 0.3, dim),
        "curiosity": rnd.normal(0.6, 0.3, dim),
    }
    for k, v in base.items():
        table[k] = v
    return table


def sent_embed(text, table, dim=64):
    toks = [t.lower() for t in text.replace("—", " ").replace("-", " ").split()]
    if not toks:
        return np.zeros(dim)
    vecs = []
    for t in toks:
        # strip punctuation crudely
        t = "".join(ch for ch in t if ch.isalnum())
        if not t:
            continue
        vecs.append(table[t])
    if not vecs:
        return np.zeros(dim)
    v = np.mean(vecs, axis=0)
    v = v / (np.linalg.norm(v) + 1e-9)
    return v


def cosine(a, b):
    return float(
        np.dot(a, b)
        / ((np.linalg.norm(a) + 1e-9) * (np.linalg.norm(b) + 1e-9))
    )


# --------------------------
# build graph from atoms
# --------------------------
def build_graph(atoms, emb, k=6, seed=42):
    rnd = np.random.default_rng(seed)
    G = nx.Graph()
    for i, a in enumerate(atoms):
        G.add_node(i, text=a, emb=emb[i])
    # connect each node to k nearest neighbors by semantic similarity
    E = len(atoms)
    sims = np.zeros((E, E), dtype=np.float32)
    for i in range(E):
        for j in range(i + 1, E):
            s = cosine(emb[i], emb[j])
            sims[i, j] = sims[j, i] = s
    for i in range(E):
        idx = np.argsort(-sims[i])[: k + 1]  # include self, drop later
        for j in idx:
            if i == j:
                continue
            G.add_edge(
                i,
                j,
                sim=float(max(0.0, sims[i, j])),
                cond=0.10,
                flow=0.0,
            )
    return G


# --------------------------
# uncertainty: high if neighbors disagree or similarity is weak
# --------------------------
def node_uncertainty(G, i):
    nbrs = list(G.neighbors(i))
    if not nbrs:
        return 1.0
    sims = [G[i][j]["sim"] for j in nbrs]
    # low mean similarity + high variance => high uncertainty
    m = np.mean(sims)
    v = np.var(sims)
    u = (1 - m) * 0.7 + min(1.0, v * 2.0) * 0.3
    return float(np.clip(u, 0.0, 1.2))


# --------------------------
# one growth step
# --------------------------
def step(G, alpha=0.85, reinforce=0.05, decay=0.015, noise=0.02):
    nodes = list(G.nodes())
    U = np.array([node_uncertainty(G, i) for i in nodes])  # nutrient

    # flow accumulation per edge
    new_flow = {}
    for u, v, data in G.edges(data=True):
        # propensity: nutrient gradient + semantic agreement
        nu = U[u]
        nv = U[v]
        grad = max(nu, nv)  # attraction to either nutrient hotspot
        sem = data["sim"]
        prop = grad * (0.6 * sem + 0.4)  # favor coherent edges without killing exploration
        new_flow[(u, v)] = prop

    # EMA flow memory
    maxprop = max(new_flow.values()) if new_flow else 1.0
    for (u, v), prop in new_flow.items():
        prop = prop / (maxprop + 1e-9)
        old = G[u][v]["flow"]
        G[u][v]["flow"] = alpha * old + (1 - alpha) * prop

    # conductance update (truth reinforcement)
    maxflow = max([G[u][v]["flow"] for u, v in G.edges()] or [1.0])
    for u, v, data in G.edges(data=True):
        f = data["flow"] / (maxflow + 1e-9)
        data["cond"] = float(
            np.clip(data["cond"] + reinforce * f - decay, 0.001, 1.5)
        )

    # tiny noise to keep exploration alive
    for u, v, data in G.edges(data=True):
        data["cond"] = float(
            np.clip(
                data["cond"] + np.random.normal(0, noise * 0.02),
                0.001,
                1.5,
            )
        )

    return U


# --------------------------
# render one frame (headless + Retina-safe)
# --------------------------
def render(G, pos, U, t, writer):
    plt.figure(figsize=(6.6, 6.6), dpi=140)
    plt.axis("off")

    # scale nodes by uncertainty
    umin, umax = float(np.min(U)), float(np.max(U))
    sizes = 40 + 240 * (U - umin) / (umax - umin + 1e-9)
    colors = plt.cm.magma((U - umin) / (umax - umin + 1e-9))

    # scale edges by conductance
    conds = np.array([G[u][v]["cond"] for u, v in G.edges()])
    cmin, cmax = float(np.min(conds)), float(np.max(conds))
    widths = 0.5 + 5.0 * ((conds - cmin) / (cmax - cmin + 1e-9))
    alphas = 0.25 + 0.75 * ((conds - cmin) / (cmax - cmin + 1e-9))

    # draw edges
    for idx, (u, v) in enumerate(G.edges()):
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        plt.plot(
            x,
            y,
            color=(1.0, 0.85, 0.25, float(alphas[idx])),
            linewidth=float(widths[idx]),
        )

    # draw nodes
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=sizes,
        node_color=colors,
        linewidths=0,
    )

    plt.text(
        0.03,
        0.97,
        f"Physarum Knowledge — step {t}",
        transform=plt.gca().transAxes,
        color="#f2efe8",
        fontsize=10,
        weight="bold",
    )
    plt.tight_layout(pad=0.05)

    # --- capture frame (off-screen, Retina-safe) ---
    plt.draw()
    fig = plt.gcf()
    fig.canvas.draw()

    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)

    # logical width/height
    w, h = fig.canvas.get_width_height()

    # detect pixel ratio (1 for normal, 2 for Retina, etc.)
    # len(buf) = (w*ratio) * (h*ratio) * 4
    ratio = int(round(np.sqrt(len(buf) / (4 * w * h))))
    W, H = w * ratio, h * ratio

    frame = buf.reshape(H, W, 4)[..., :3]  # drop alpha, keep RGB

    writer.append_data(frame)
    plt.close()


# --------------------------
# query: instant answer over stabilized truth graph
# --------------------------
def instant_answer(G, emb_table, query, topk=3):
    qv = sent_embed(query, emb_table)
    # score nodes by cosine to query, but bias by node's incident conductance
    node_score = []
    for i in G.nodes():
        vec = G.nodes[i]["emb"]
        sim = cosine(qv, vec)
        cond_sum = sum(G[i][j]["cond"] for j in G.neighbors(i)) + 1e-9
        score = 0.7 * sim + 0.3 * (cond_sum / (1.0 + cond_sum))
        node_score.append((score, i))
    node_score.sort(reverse=True)
    picks = node_score[:topk]

    # small trace: walk 2 steps along strongest edges from the best node
    best = picks[0][1]
    trace = [best]
    cur = best
    for _ in range(2):
        nbrs = list(G.neighbors(cur))
        if not nbrs:
            break
        nxt = max(nbrs, key=lambda j: G[cur][j]["cond"])
        if nxt in trace:
            break
        trace.append(nxt)
        cur = nxt

    results = [
        {"text": G.nodes[i]["text"], "score": round(float(s), 4)}
        for s, i in picks
    ]

    return {
        "query": query,
        "results": results,
        "trace_node_ids": trace,
        "trace_text": [G.nodes[i]["text"] for i in trace],
    }


# --------------------------
# main
# --------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--atoms", default="atoms.json")
    ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--gif", default="out.gif")
    ap.add_argument("--export", default="truth_graph.json")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--query", default="")
    ap.add_argument("--topk", type=int, default=3)
    args = ap.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    table = make_word_table()

    atoms = json.load(open(args.atoms))
    emb = [sent_embed(a, table) for a in atoms]

    G = build_graph(atoms, emb, k=6, seed=args.seed)
    pos = nx.spring_layout(
        G, seed=args.seed, k=1 / np.sqrt(max(10, len(G)))
    )

    with imageio.get_writer(args.gif, mode="I", duration=0.06) as writer:
        for t in range(args.steps):
            U = step(G)
            render(G, pos, U, t, writer)

    # export truth graph
    export = {
        "nodes": [
            {"id": i, "text": G.nodes[i]["text"]} for i in G.nodes()
        ],
        "edges": [
            {
                "u": int(u),
                "v": int(v),
                "cond": round(G[u][v]["cond"], 6),
                "sim": round(G[u][v]["sim"], 6),
            }
            for u, v in G.edges()
        ],
    }
    if args.export:
        with open(args.export, "w") as f:
            json.dump(export, f, indent=2)
        print(f"Saved: {args.export}")
    print(f"Saved GIF: {args.gif}")

    if args.query.strip():
        ans = instant_answer(G, table, args.query, topk=args.topk)
        print("\nInstant answer:")
        for r in ans["results"]:
            print(f"  • ({r['score']:.3f}) {r['text']}")
        print("Trace:", " → ".join(ans["trace_text"]))


if __name__ == "__main__":
    main()
