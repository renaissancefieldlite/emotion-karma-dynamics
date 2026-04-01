from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


OUT = Path(__file__).resolve().parent


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
    axs[0].set_title("Secondary Modulation Stays Secondary")
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


def main():
    style()
    make_feedback_loop()
    make_biomarker_panel()
    make_coupled_resonance()
    make_secondary_modulation()
    make_stack_measurement_ladder()


if __name__ == "__main__":
    main()
