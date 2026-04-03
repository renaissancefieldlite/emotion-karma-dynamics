from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.font_manager import FontProperties
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "charts"


DEVANAGARI_FONT = FontProperties(
    family=[
        "Kohinoor Devanagari",
        "Devanagari Sangam MN",
        "Devanagari MT",
        "ITF Devanagari",
        "Arial Unicode MS",
    ]
)


def style():
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 200,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "font.size": 10,
            "legend.frameon": True,
        }
    )
    OUT.mkdir(parents=True, exist_ok=True)


def logistic(x):
    return 1.0 / (1.0 + np.exp(-x))


def make_feedback_loop():
    n = 700
    dt = 0.05
    t = np.arange(n) * dt

    stimulus = np.zeros(n)
    for center, amp, width in [(90, 1.5, 18), (240, -1.0, 26), (420, 1.2, 22), (560, -0.8, 16)]:
        stimulus += amp * np.exp(-0.5 * ((np.arange(n) - center) / width) ** 2)

    kernel_x = np.arange(160)
    kernel = np.exp(-kernel_x / 38.0)
    kernel /= kernel.sum()

    e = np.zeros(n)
    a = np.zeros(n)
    k = np.zeros(n)

    alpha = 0.22
    gamma = 1.6

    for i in range(1, n):
        a[i - 1] = np.tanh(1.25 * e[i - 1])
        back = 0.0
        upper = min(i, len(kernel))
        if upper > 0:
            back = np.sum(kernel[:upper] * a[i - upper : i][::-1])
        k[i] = back
        de = -alpha * e[i - 1] + stimulus[i] + gamma * back
        e[i] = e[i - 1] + dt * de

    a[-1] = np.tanh(1.25 * e[-1])

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(t, stimulus, label="Input stimulus", color="#4C78A8", linewidth=2.0)
    ax.plot(t, e, label="Emotion state e(t)", color="#F58518", linewidth=2.4)
    ax.plot(t, a, label="Action a(t)", color="#54A24B", linewidth=2.0)
    ax.plot(t, k, label="Returned consequence k(t)", color="#B279A2", linewidth=2.0)
    ax.axhline(0, color="black", linewidth=0.8, alpha=0.6)
    ax.set_title("Emotion / Karma Feedback Loop")
    ax.set_xlabel("Time")
    ax.set_ylabel("Normalized units")
    ax.legend(loc="upper right")
    ax.text(
        0.015,
        0.02,
        "Schematic: state -> action -> delayed return -> updated state",
        transform=ax.transAxes,
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(OUT / "01_emotion_feedback_loop.png")
    plt.close(fig)


def make_biomarker_panel():
    n = 500
    t = np.linspace(0, 10, n)
    stress = np.exp(-0.5 * ((t - 2.2) / 0.9) ** 2) + 0.7 * np.exp(-0.5 * ((t - 5.2) / 0.8) ** 2)

    regulated_amyg = 0.35 + 0.55 * stress * np.exp(-0.16 * t)
    dysregulated_amyg = 0.38 + 0.72 * stress

    regulated_front = 0.52 + 0.20 * np.tanh(1.1 * (t - 3.2))
    dysregulated_front = 0.50 - 0.16 * logistic(2.0 * (t - 2.6))

    regulated_hrv = 0.42 + 0.25 * np.exp(-0.5 * ((t - 6.7) / 1.2) ** 2)
    dysregulated_hrv = 0.39 - 0.12 * np.exp(-0.5 * ((t - 4.5) / 1.1) ** 2)

    regulated_cort = 0.28 + 0.58 * np.exp(-0.5 * ((t - 2.4) / 1.0) ** 2) * np.exp(-0.18 * t)
    dysregulated_cort = 0.30 + 0.70 * np.exp(-0.5 * ((t - 2.6) / 1.0) ** 2)

    fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    panels = [
        ("Amygdala drive", regulated_amyg, dysregulated_amyg, "#E45756"),
        ("Frontal regulation index", regulated_front, dysregulated_front, "#4C78A8"),
        ("HF-HRV", regulated_hrv, dysregulated_hrv, "#54A24B"),
        ("Cortisol", regulated_cort, dysregulated_cort, "#B279A2"),
    ]

    for ax, (title, reg, dys, color) in zip(axs.flat, panels):
        ax.plot(t, reg, color=color, linewidth=2.4, label="Regulated")
        ax.plot(t, dys, color=color, linewidth=2.0, linestyle="--", alpha=0.9, label="Dysregulated")
        ax.set_title(title)
        ax.set_ylabel("Normalized level")
        ax.legend(loc="upper right", fontsize=8)

    for ax in axs[1]:
        ax.set_xlabel("Time")

    fig.suptitle("Biomarker Regulation Panel", fontsize=15, y=0.98)
    fig.text(
        0.5,
        0.01,
        "Schematic only. Shapes represent regulation and recovery structure, not a single dataset.",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    fig.savefig(OUT / "02_biomarker_regulation_panel.png")
    plt.close(fig)


def make_coupled_resonance():
    n = 900
    dt = 0.03
    t = np.arange(n) * dt

    theta1 = np.zeros(n)
    theta2 = np.zeros(n)
    theta1[0] = 0.2
    theta2[0] = 2.4

    w1 = 1.02
    w2 = 0.96
    coupling = 0.42

    for i in range(1, n):
        d1 = w1 + coupling * np.sin(theta2[i - 1] - theta1[i - 1])
        d2 = w2 + coupling * np.sin(theta1[i - 1] - theta2[i - 1])
        theta1[i] = theta1[i - 1] + dt * d1
        theta2[i] = theta2[i - 1] + dt * d2

    sig1 = np.sin(theta1)
    sig2 = np.sin(theta2)
    phase_diff = np.angle(np.exp(1j * (theta1 - theta2)))

    fig, axs = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axs[0].plot(t, sig1, label="System A", color="#4C78A8", linewidth=2.0)
    axs[0].plot(t, sig2, label="System B", color="#F58518", linewidth=2.0)
    axs[0].set_title("Coupled Resonance / Phase Locking")
    axs[0].set_ylabel("Oscillation")
    axs[0].legend(loc="upper right")

    axs[1].plot(t, phase_diff, color="#54A24B", linewidth=2.0)
    axs[1].axhline(0, color="black", linewidth=0.8, alpha=0.5)
    axs[1].set_ylabel("Phase difference")
    axs[1].set_xlabel("Time")
    axs[1].text(
        0.015,
        0.05,
        "Convergence toward smaller phase difference = stronger alignment",
        transform=axs[1].transAxes,
        fontsize=9,
        color="#444444",
    )

    fig.tight_layout()
    fig.savefig(OUT / "03_coupled_resonance.png")
    plt.close(fig)


def make_secondary_modulation():
    n = 700
    dt = 0.04
    t = np.arange(n) * dt

    drive = 0.75 * np.sin(0.55 * t) + 0.35 * np.sin(1.4 * t + 0.9)
    e_base = np.zeros(n)
    e_mod = np.zeros(n)
    q = 0.09 * np.sin(8.0 * t) + 0.03 * np.random.default_rng(7).normal(size=n)
    beta = 0.07
    alpha = 0.18

    for i in range(1, n):
        e_base[i] = e_base[i - 1] + dt * (-alpha * e_base[i - 1] + drive[i])
        e_mod[i] = e_mod[i - 1] + dt * (-alpha * e_mod[i - 1] + drive[i] + beta * q[i])

    fig, axs = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axs[0].plot(t, e_base, label="Backbone dynamics F(e,t)", color="#4C78A8", linewidth=2.2)
    axs[0].plot(t, e_mod, label="Backbone + beta q(t)", color="#E45756", linewidth=1.8, alpha=0.9)
    axs[0].set_title("Small Overlap Term Inside the Larger Field Model")
    axs[0].set_ylabel("State")
    axs[0].legend(loc="upper right")

    axs[1].plot(t, q, color="#B279A2", linewidth=1.6)
    axs[1].axhline(0, color="black", linewidth=0.8, alpha=0.5)
    axs[1].set_ylabel("q(t)")
    axs[1].set_xlabel("Time")
    axs[1].text(
        0.015,
        0.06,
        "Small perturbation term only. It does not replace the main dynamical model.",
        transform=axs[1].transAxes,
        fontsize=9,
        color="#444444",
    )

    fig.tight_layout()
    fig.savefig(OUT / "04_secondary_modulation.png")
    plt.close(fig)


def make_stack_measurement_ladder():
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")

    boxes = [
        (0.7, 6.0, 2.2, 2.2, "#4C78A8", "HRV1.0\nAutonomic capture"),
        (3.5, 6.0, 2.2, 2.2, "#54A24B", "QuantumHRV\nVariability summary"),
        (6.3, 6.0, 2.5, 2.2, "#F58518", "Bridge Protocol\nEEG / HRV field step"),
        (9.5, 6.0, 1.9, 2.2, "#B279A2", "Muse 2\nEEG lane"),
        (2.1, 2.0, 2.8, 2.0, "#72B7B2", "Measured state\nHRV, timing, RR windows"),
        (5.0, 2.0, 2.8, 2.0, "#E45756", "Cross-modal state\nEEG + HRV + prompts"),
        (7.9, 2.0, 2.8, 2.0, "#9D755D", "Theory discipline\nFeedback first,\nquantum overlap secondary"),
    ]

    for x, y, w, h, color, label in boxes:
        rect = plt.Rectangle((x, y), w, h, facecolor=color, alpha=0.16, edgecolor=color, linewidth=2.2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=11, weight="bold")

    arrows = [
        ((2.9, 7.1), (3.5, 7.1)),
        ((5.7, 7.1), (6.3, 7.1)),
        ((8.8, 7.1), (9.5, 7.1)),
        ((1.8, 6.0), (3.0, 4.0)),
        ((4.6, 6.0), (6.1, 4.0)),
        ((10.4, 6.0), (9.3, 4.0)),
        ((4.9, 3.0), (5.0, 3.0)),
        ((7.8, 3.0), (7.9, 3.0)),
    ]

    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", linewidth=2.0, color="#444444"))

    ax.text(
        6.0,
        9.2,
        "Emotion-State Measurement Ladder",
        ha="center",
        va="center",
        fontsize=16,
        weight="bold",
    )
    ax.text(
        6.0,
        8.5,
        "Current stance: measurable physiology first, cross-modal fusion next, speculative overlap last",
        ha="center",
        va="center",
        fontsize=10,
        color="#444444",
    )
    ax.text(
        6.0,
        0.8,
        "This ties the chart pack to the actual Playground stack instead of leaving it as free-floating theory.",
        ha="center",
        va="center",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(OUT / "05_stack_measurement_ladder.png")
    plt.close(fig)


def make_vedic_translation_chart():
    fig, ax = plt.subplots(figsize=(14, 6.8))
    ax.axis("off")

    rows = [
        ["Karma", "कर्म", "karma", "action-plus-return", "delayed return, persistence term"],
        ["Rasa", "रस", "rasa", "felt tone, affective coloring", "structured affect state"],
        ["Bhava", "भाव", "bhava", "emotional mode, felt state", "state-class / valence-arousal pattern"],
        ["Samskara", "संस्कार", "saṃskāra", "stored imprint, unresolved carryover", "learned groove, recurrent bias"],
        ["Nadi", "नाड़ी", "nāḍī", "flow channel, pathway image", "regulation channel / pathway metaphor"],
        ["Chakra", "चक्र", "chakra", "concentration zone, energetic center", "load cluster / regulation hub"],
    ]

    col_labels = [
        "Vedic term",
        "Devanagari",
        "Transliteration",
        "Working meaning in this repo",
        "Modern measurement-facing read",
    ]

    table = ax.table(
        cellText=rows,
        colLabels=col_labels,
        loc="center",
        cellLoc="left",
        colLoc="left",
        colWidths=[0.12, 0.12, 0.14, 0.28, 0.34],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.0)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#243447")
            cell.set_text_props(color="white", weight="bold")
            cell.set_edgecolor("#243447")
        else:
            cell.set_edgecolor("#d5dbe5")
            cell.set_facecolor("#f9fbfd" if row % 2 else "#eef3f8")
            if col == 0:
                cell.set_text_props(weight="bold", color="#182028")
            else:
                cell.set_text_props(color="#182028")
            if col == 1:
                cell.get_text().set_fontproperties(DEVANAGARI_FONT)
                cell.get_text().set_fontsize(12)

    ax.set_title("Vedic / Modern Translation Layer", fontsize=16, weight="bold", pad=20)
    fig.text(
        0.5,
        0.065,
        "The chart pairs traditional vocabulary with the repo's measurement-first translation layer.",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=(0.02, 0.08, 0.98, 0.94))
    fig.savefig(OUT / "06_vedic_modern_translation_layer.png")
    plt.close(fig)


def make_chakra_language_map():
    fig, ax = plt.subplots(figsize=(14, 10.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 16)
    ax.axis("off")

    chakras = [
        {
            "name": "Sahasrara",
            "dev": "सहस्रार",
            "trans": "sahasrāra",
            "subtitle": "Crown",
            "color": "#8e63ce",
            "positive": "unity, peace, meaning",
            "negative": "isolation, disconnection, meaning collapse",
            "modern": "big-picture integration, existential frame, top-level coherence",
        },
        {
            "name": "Ajna",
            "dev": "आज्ञा",
            "trans": "ājñā",
            "subtitle": "Third Eye",
            "color": "#5166c2",
            "positive": "clarity, intuition, pattern recognition",
            "negative": "confusion, overwhelm, distorted interpretation",
            "modern": "attention framing, cognitive lens, interpretation load",
        },
        {
            "name": "Vishuddha",
            "dev": "विशुद्ध",
            "trans": "viśuddha",
            "subtitle": "Throat",
            "color": "#3b8fcf",
            "positive": "truth, expression, clean signaling",
            "negative": "suppression, frustration, blocked voice",
            "modern": "communication bottleneck, expression inhibition, signal gating",
        },
        {
            "name": "Anahata",
            "dev": "अनाहत",
            "trans": "anāhata",
            "subtitle": "Heart",
            "color": "#49a95a",
            "positive": "love, empathy, relational openness",
            "negative": "grief, jealousy, defensive closure",
            "modern": "social safety, trust regulation, HRV-linked relational coherence",
        },
        {
            "name": "Manipura",
            "dev": "मणिपूर",
            "trans": "maṇipūra",
            "subtitle": "Solar Plexus",
            "color": "#e0b83d",
            "positive": "confidence, agency, directed power",
            "negative": "anger, shame, control fixation",
            "modern": "self-worth regulation, control stress, performance pressure",
        },
        {
            "name": "Svadhisthana",
            "dev": "स्वाधिष्ठान",
            "trans": "svādhiṣṭhāna",
            "subtitle": "Sacral",
            "color": "#ef8c3a",
            "positive": "flow, pleasure, creativity",
            "negative": "guilt, craving, attachment loops",
            "modern": "reward / attachment dynamics, affective flow, desire regulation",
        },
        {
            "name": "Muladhara",
            "dev": "मूलाधार",
            "trans": "mūlādhāra",
            "subtitle": "Root",
            "color": "#d45757",
            "positive": "security, trust, grounding",
            "negative": "fear, anxiety, instability",
            "modern": "threat bias, survival loading, cortisol-heavy defensive state",
        },
    ]

    spine_x = 2.3
    ys = np.linspace(13.7, 2.3, len(chakras))
    ax.plot([spine_x, spine_x], [ys[-1], ys[0]], color="#8f98a4", linewidth=5.4, alpha=0.9, zorder=1)

    wave_y = np.linspace(ys[-1], ys[0], 500)
    amp = 0.48
    cycles = 3.1
    phase = (wave_y - ys[-1]) / (ys[0] - ys[-1]) * (2 * np.pi * cycles)
    ida_x = spine_x - amp * np.sin(phase)
    pingala_x = spine_x + amp * np.sin(phase)
    ax.plot(ida_x, wave_y, color="#9bb5d9", linewidth=2.2, linestyle=(0, (1.2, 2.4)), alpha=0.95, zorder=2)
    ax.plot(pingala_x, wave_y, color="#d7a56c", linewidth=2.2, linestyle=(0, (5, 3)), alpha=0.95, zorder=2)

    ax.text(
        7.2,
        15.25,
        "Chakra / Nadi Language Map",
        ha="center",
        va="center",
        fontsize=20,
        weight="bold",
        color="#182028",
    )
    ax.text(
        7.2,
        14.55,
        "Nadis as channels, chakras as load-bearing nodes in the repo's emotion-karma field model",
        ha="center",
        va="center",
        fontsize=10.5,
        color="#4b5563",
    )
    ax.text(spine_x - 0.85, 14.55, "Ida", ha="center", va="center", fontsize=10, color="#597fb6", weight="bold")
    ax.text(spine_x, 14.55, "Sushumna", ha="center", va="center", fontsize=10, color="#475569", weight="bold")
    ax.text(spine_x + 0.95, 14.55, "Pingala", ha="center", va="center", fontsize=10, color="#b6732d", weight="bold")

    for idx, (chakra, y) in enumerate(zip(chakras, ys)):
        circ = plt.Circle((spine_x, y), 0.38, facecolor=chakra["color"], edgecolor="white", linewidth=2.5, zorder=3)
        ax.add_patch(circ)
        if idx < len(chakras) - 1:
            ax.annotate(
                "",
                xy=(spine_x, ys[idx + 1] + 0.45),
                xytext=(spine_x, y - 0.45),
                arrowprops=dict(arrowstyle="->", linewidth=1.8, color="#94a3b8"),
            )

        rect = plt.Rectangle((3.15, y - 0.78), 10.1, 1.56, facecolor="#fbfcfe", edgecolor="#d5dbe5", linewidth=1.2)
        ax.add_patch(rect)
        ax.add_patch(plt.Rectangle((3.15, y - 0.78), 0.18, 1.56, facecolor=chakra["color"], edgecolor=chakra["color"]))

        ax.text(3.55, y + 0.34, f"{chakra['name']} ({chakra['subtitle']})", fontsize=12.5, weight="bold", color="#182028")
        ax.text(6.3, y + 0.34, chakra["dev"], fontsize=13.5, color="#182028", fontproperties=DEVANAGARI_FONT)
        ax.text(7.7, y + 0.34, chakra["trans"], fontsize=11, color="#4b5563", style="italic")

        ax.text(3.55, y - 0.02, f"Positive / open: {chakra['positive']}", fontsize=9.6, color="#1f5130")
        ax.text(7.1, y - 0.02, f"Negative / loaded: {chakra['negative']}", fontsize=9.6, color="#7a2e2e")
        ax.text(3.55, y - 0.44, f"Modern read: {chakra['modern']}", fontsize=9.3, color="#334155")

    footer = (
        "Working bridge: nadis are treated here as channels or pathways; chakras are treated as node-like "
        "concentration zones where unresolved load, bias, and perception-coloring can accumulate. "
        "Ida, Pingala, and Sushumna are shown as the three main channel lines feeding the node map."
    )
    ax.text(7.1, 0.75, footer, ha="center", va="center", fontsize=9.2, color="#4b5563", wrap=True)

    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.98))
    fig.savefig(OUT / "07_chakra_language_map.png")
    plt.close(fig)


def make_custom_nadi_map():
    fig, ax = plt.subplots(figsize=(12.5, 14))
    fig.patch.set_facecolor("#0d2c4a")
    ax.set_facecolor("#0d2c4a")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 16)
    ax.axis("off")

    center_x = 6.0
    node_y = [13.8, 12.1, 10.3, 8.4, 6.45, 4.5, 2.6]
    node_colors = ["#8e63ce", "#5166c2", "#3b8fcf", "#49a95a", "#e0b83d", "#ef8c3a", "#d45757"]
    node_names = ["Crown", "Brow", "Throat", "Heart", "Solar", "Sacral", "Root"]

    # Main channels
    ax.plot([center_x, center_x], [2.1, 14.4], color="#f4f0dd", linewidth=4.2, alpha=0.95, zorder=2)

    y = np.linspace(2.2, 14.2, 600)
    phase = (y - 2.2) / (14.2 - 2.2) * (2 * np.pi * 3.1)
    ida = center_x - 0.78 * np.sin(phase)
    pingala = center_x + 0.78 * np.sin(phase)
    ax.plot(ida, y, color="#c7d8ef", linewidth=2.2, linestyle=(0, (1.2, 2.4)), zorder=1)
    ax.plot(pingala, y, color="#efc37f", linewidth=2.2, linestyle=(0, (5, 3)), zorder=1)

    # Small branch channels
    for y0 in node_y[1:-1]:
        ax.plot([center_x - 0.55, center_x - 2.2], [y0, y0 + 0.6], color="#f4f0dd", linewidth=1.15, alpha=0.6)
        ax.plot([center_x + 0.55, center_x + 2.2], [y0, y0 + 0.6], color="#f4f0dd", linewidth=1.15, alpha=0.6)
        ax.plot([center_x - 0.5, center_x - 1.85], [y0, y0 - 0.75], color="#f4f0dd", linewidth=1.0, alpha=0.35)
        ax.plot([center_x + 0.5, center_x + 1.85], [y0, y0 - 0.75], color="#f4f0dd", linewidth=1.0, alpha=0.35)

    # Node circles and labels
    for y0, color, name in zip(node_y, node_colors, node_names):
        ax.add_patch(plt.Circle((center_x, y0), 0.28, facecolor=color, edgecolor="white", linewidth=1.4, zorder=4))
        ax.text(center_x + 0.48, y0, name, va="center", fontsize=10.2, color="white", weight="bold")

    ax.text(6.0, 15.25, "Custom Nadi Field Map", ha="center", fontsize=20, color="white", weight="bold")
    ax.text(
        6.0,
        14.68,
        "Nadis = channels / circuit lines. Chakras = node-like load zones where return and residue concentrate.",
        ha="center",
        fontsize=10.3,
        color="#d9e5f2",
    )

    # Main nadi callouts
    ax.text(2.2, 13.75, "इडा  Ida", fontsize=12, color="#c7d8ef", weight="bold")
    ax.text(2.2, 13.15, "cooling / inward / receptive channel", fontsize=9.3, color="#d9e5f2")
    ax.text(2.2, 12.7, "working read: introspective load, memory, parasympathetic-like recovery", fontsize=8.8, color="#d9e5f2")

    ax.text(8.65, 13.75, "पिङ्गला  Pingala", fontsize=12, color="#efc37f", weight="bold")
    ax.text(8.65, 13.15, "activating / outward / mobilizing channel", fontsize=9.3, color="#d9e5f2")
    ax.text(8.65, 12.7, "working read: drive, action bias, sympathetic-like activation", fontsize=8.8, color="#d9e5f2")

    ax.text(4.35, 1.65, "सुषुम्ना  Sushumna", fontsize=12, color="#f4f0dd", weight="bold")
    ax.text(4.35, 1.15, "central integration line through the node stack", fontsize=9.3, color="#d9e5f2")

    # Repo interpretation box
    box = plt.Rectangle((0.85, 0.6), 3.25, 3.0, facecolor="#123758", edgecolor="#d9e5f2", linewidth=1.0, alpha=0.95)
    ax.add_patch(box)
    ax.text(1.15, 3.15, "Repo Read", fontsize=11.5, color="white", weight="bold")
    ax.text(1.15, 2.62, "• nadis = channels / circuit paths", fontsize=9.2, color="#d9e5f2")
    ax.text(1.15, 2.17, "• chakras = node-like concentration zones", fontsize=9.2, color="#d9e5f2")
    ax.text(1.15, 1.72, "• saṃskāra = stored load in the system", fontsize=9.2, color="#d9e5f2")
    ax.text(1.15, 1.27, "• emotion = active phase", fontsize=9.2, color="#d9e5f2")
    ax.text(1.15, 0.82, "• karma = delayed return through the channels", fontsize=9.2, color="#d9e5f2")

    # Branch lane box
    box2 = plt.Rectangle((8.35, 0.6), 2.85, 3.0, facecolor="#123758", edgecolor="#d9e5f2", linewidth=1.0, alpha=0.95)
    ax.add_patch(box2)
    ax.text(8.65, 3.15, "Branch Lanes", fontsize=11.5, color="white", weight="bold")
    ax.text(8.65, 2.58, "Older systems describe many more nadis.", fontsize=9.0, color="#d9e5f2")
    ax.text(8.65, 2.08, "This map keeps the major three visible", fontsize=9.0, color="#d9e5f2")
    ax.text(8.65, 1.63, "and treats side branches as local", fontsize=9.0, color="#d9e5f2")
    ax.text(8.65, 1.18, "distribution paths around each node.", fontsize=9.0, color="#d9e5f2")

    ax.text(
        6.0,
        0.28,
        "Custom working graphic for the emotion-karma dynamics repo. It maps traditional channel language into a systems / measurement frame.",
        ha="center",
        fontsize=8.9,
        color="#d9e5f2",
    )

    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.98))
    fig.savefig(OUT / "08_custom_nadi_field_map.png", facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    style()
    make_feedback_loop()
    make_biomarker_panel()
    make_coupled_resonance()
    make_secondary_modulation()
    make_stack_measurement_ladder()
    make_vedic_translation_chart()
    make_chakra_language_map()
    make_custom_nadi_map()


if __name__ == "__main__":
    main()
