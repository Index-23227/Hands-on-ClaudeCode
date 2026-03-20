"""
Doosan E0509 Visualization Dashboard
로봇 없이 실행 가능한 시각화 도구.

실행: python visualize_doosan.py
출력: doosan_dashboard.png (종합 대시보드)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

from doosan_e0509_config import DOOSAN_E0509_CONFIG
from doosan_action_adapter import DoosanActionAdapter, DoosanSafetyConfig


# ============================================================
# 1. Joint Specs Visualization
# ============================================================

def plot_joint_specs(ax):
    """Joint별 범위/속도를 시각화"""
    config = DOOSAN_E0509_CONFIG
    joint_names = [f"J{i+1}" for i in range(6)]

    lower_deg = np.rad2deg(config["joint_limits_lower"])
    upper_deg = np.rad2deg(config["joint_limits_upper"])
    max_vel = np.rad2deg(config["joint_max_velocities"])

    y = np.arange(6)
    bar_height = 0.35

    # Range bars (symmetric around 0)
    ranges = upper_deg - lower_deg
    bars = ax.barh(y, ranges, height=bar_height, left=lower_deg,
                   color='#4C9BE8', alpha=0.8, edgecolor='#2970B0', linewidth=1.2)

    # Center line
    ax.axvline(x=0, color='#333', linewidth=1, linestyle='-', alpha=0.5)

    # Labels
    for i in range(6):
        ax.text(upper_deg[i] + 10, y[i], f"{upper_deg[i]:+.0f}°",
                va='center', fontsize=9, fontweight='bold', color='#2970B0')
        ax.text(lower_deg[i] - 10, y[i], f"{lower_deg[i]:+.0f}°",
                va='center', ha='right', fontsize=9, fontweight='bold', color='#2970B0')
        # Velocity annotation
        ax.text(0, y[i] + 0.22, f"max {max_vel[i]:.0f}°/s",
                va='bottom', ha='center', fontsize=7, color='#666', style='italic')

    ax.set_yticks(y)
    ax.set_yticklabels(joint_names, fontsize=11, fontweight='bold')
    ax.set_xlabel("Range (degrees)", fontsize=10)
    ax.set_title("Joint Ranges & Max Velocities", fontsize=13, fontweight='bold', pad=10)
    ax.set_xlim(-400, 400)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)


# ============================================================
# 2. Safety Clamp Simulation
# ============================================================

def simulate_trajectory(num_steps=100):
    """랜덤 VLA 출력으로 시뮬레이션, clamped vs unclamped 비교"""
    adapter = DoosanActionAdapter()
    np.random.seed(42)

    # 초기 상태
    init_pos = np.deg2rad([0, 0, 0, 0, 0, 0])
    adapter.set_current_state(init_pos, 0.0)

    raw_targets = []   # clamp 없이 누적된 목표
    safe_targets = []  # clamp 적용된 실제 목표
    clamp_flags = []
    gripper_states = []

    current_raw = init_pos.copy()
    current_safe = init_pos.copy()

    for step in range(num_steps):
        # 랜덤 VLA action (일부는 과격한 값)
        if step < 30:
            raw_action = np.random.normal(0.02, 0.01, 7)
        elif step < 60:
            raw_action = np.random.normal(0.08, 0.03, 7)  # aggressive
        else:
            raw_action = np.random.normal(-0.03, 0.02, 7)

        raw_action[6] = 0.8 if step > 40 else 0.2  # gripper

        # Raw (unclamped) trajectory
        current_raw = current_raw + raw_action[:6]
        raw_targets.append(current_raw.copy())

        # Safe (clamped) trajectory
        adapter.set_current_state(current_safe, 0.0)
        result = adapter.convert(raw_action, dt=0.1)
        current_safe = result['joint_targets']
        safe_targets.append(current_safe.copy())
        clamp_flags.append(result['was_clamped'])
        gripper_states.append(result['gripper_open'])

    return {
        'raw': np.array(raw_targets),
        'safe': np.array(safe_targets),
        'clamped': np.array(clamp_flags),
        'gripper': np.array(gripper_states),
    }


def plot_trajectory_comparison(axes, sim_data):
    """Joint 1, 2, 3의 raw vs safe 궤적 비교"""
    steps = np.arange(len(sim_data['raw']))
    safety = DoosanSafetyConfig()
    joint_labels = ["J1", "J2", "J3"]
    colors_raw = ['#FF6B6B', '#FF9F43', '#FECA57']
    colors_safe = ['#2196F3', '#00BCD4', '#4CAF50']

    for idx, ax in enumerate(axes):
        raw_deg = np.rad2deg(sim_data['raw'][:, idx])
        safe_deg = np.rad2deg(sim_data['safe'][:, idx])
        upper_deg = np.rad2deg(safety.joint_pos_upper[idx])
        lower_deg = np.rad2deg(safety.joint_pos_lower[idx])

        # Danger zone shading
        ax.axhspan(upper_deg, upper_deg + 50, color='#FF0000', alpha=0.08)
        ax.axhspan(lower_deg - 50, lower_deg, color='#FF0000', alpha=0.08)

        # Limit lines
        ax.axhline(upper_deg, color='red', linewidth=1.5, linestyle='--', alpha=0.7, label='Limit')
        ax.axhline(lower_deg, color='red', linewidth=1.5, linestyle='--', alpha=0.7)

        # Trajectories
        ax.plot(steps, raw_deg, color=colors_raw[idx], linewidth=1.5,
                alpha=0.6, linestyle=':', label='Raw (no clamp)')
        ax.plot(steps, safe_deg, color=colors_safe[idx], linewidth=2.0,
                alpha=0.9, label='Safe (clamped)')

        # Clamp markers
        clamped_steps = steps[sim_data['clamped']]
        if len(clamped_steps) > 0:
            ax.scatter(clamped_steps, safe_deg[sim_data['clamped']],
                      color='orange', s=8, zorder=5, alpha=0.5)

        ax.set_title(f"{joint_labels[idx]} Trajectory", fontsize=11, fontweight='bold')
        ax.set_ylabel("Angle (°)", fontsize=9)
        ax.legend(fontsize=7, loc='upper right')
        ax.grid(alpha=0.3)

    axes[-1].set_xlabel("Timestep", fontsize=10)


# ============================================================
# 3. Clamp Statistics
# ============================================================

def plot_clamp_stats(ax, sim_data):
    """Clamp 발생 빈도 히트맵"""
    clamped = sim_data['clamped']
    total = len(clamped)
    clamped_count = clamped.sum()
    safe_count = total - clamped_count

    # Pie chart
    sizes = [safe_count, clamped_count]
    labels = [f'Safe\n{safe_count} steps', f'Clamped\n{clamped_count} steps']
    colors = ['#4CAF50', '#FF9800']
    explode = (0, 0.08)

    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=90,
        textprops={'fontsize': 9},
        pctdistance=0.6,
    )
    for t in autotexts:
        t.set_fontweight('bold')
        t.set_fontsize(10)

    ax.set_title("Safety Clamp Statistics", fontsize=13, fontweight='bold', pad=10)


# ============================================================
# 4. Gripper State Timeline
# ============================================================

def plot_gripper_timeline(ax, sim_data):
    """그리퍼 상태 타임라인"""
    steps = np.arange(len(sim_data['gripper']))
    gripper = sim_data['gripper'].astype(float)

    ax.fill_between(steps, 0, gripper, color='#26A69A', alpha=0.4, step='post')
    ax.step(steps, gripper, color='#00897B', linewidth=2, where='post')

    ax.set_ylim(-0.1, 1.3)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['CLOSE', 'OPEN'], fontsize=10, fontweight='bold')
    ax.set_xlabel("Timestep", fontsize=10)
    ax.set_title("Gripper State", fontsize=11, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)


# ============================================================
# 5. Robot Spec Summary Table
# ============================================================

def plot_spec_table(ax):
    """로봇 스펙 요약 테이블"""
    ax.axis('off')

    specs = [
        ["Model", "Doosan E0509"],
        ["DOF", "6 + Gripper"],
        ["Payload", "5 kg"],
        ["Reach", "900 mm"],
        ["Repeatability", "±0.05 mm"],
        ["Protection", "IP66"],
        ["Controller IP", "192.168.127.100"],
        ["Control Hz", "10 Hz (target)"],
        ["Action Dim", "7 (6J + 1G)"],
        ["Action Type", "Joint Delta"],
    ]

    table = ax.table(
        cellText=specs,
        colLabels=["Parameter", "Value"],
        cellLoc='center',
        loc='center',
        colWidths=[0.45, 0.45],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)

    # Style header
    for j in range(2):
        cell = table[0, j]
        cell.set_facecolor('#1565C0')
        cell.set_text_props(color='white', fontweight='bold', fontsize=10)
        cell.set_edgecolor('#0D47A1')

    # Style rows
    for i in range(1, len(specs) + 1):
        for j in range(2):
            cell = table[i, j]
            cell.set_facecolor('#E3F2FD' if i % 2 == 0 else 'white')
            cell.set_edgecolor('#BBDEFB')
            if j == 1:
                cell.set_text_props(fontweight='bold')

    ax.set_title("Doosan E0509 Specifications", fontsize=13,
                 fontweight='bold', pad=15, color='#1565C0')


# ============================================================
# 6. Pipeline Architecture Diagram
# ============================================================

def plot_pipeline(ax):
    """VLA 제어 파이프라인 흐름도"""
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)

    boxes = [
        (0.5,  1.2, "Camera\n(RGB)", '#E3F2FD', '#1565C0'),
        (2.3,  1.2, "VLA\nInference", '#FFF3E0', '#E65100'),
        (4.1,  1.2, "Action\nAdapter", '#E8F5E9', '#2E7D32'),
        (5.9,  1.2, "Safety\nClamp", '#FFEBEE', '#C62828'),
        (7.7,  1.2, "Doosan\nE0509", '#F3E5F5', '#6A1B9A'),
    ]

    for x, y, text, fc, ec in boxes:
        rect = mpatches.FancyBboxPatch(
            (x, y), 1.4, 1.2,
            boxstyle="round,pad=0.1",
            facecolor=fc, edgecolor=ec, linewidth=2
        )
        ax.add_patch(rect)
        ax.text(x + 0.7, y + 0.6, text, ha='center', va='center',
                fontsize=9, fontweight='bold', color=ec)

    # Arrows
    arrow_style = dict(arrowstyle='->', color='#555', lw=2, mutation_scale=15)
    for i in range(len(boxes) - 1):
        x_start = boxes[i][0] + 1.4
        x_end = boxes[i+1][0]
        y_mid = 1.8
        ax.annotate('', xy=(x_end, y_mid), xytext=(x_start, y_mid),
                    arrowprops=arrow_style)

    # Feedback arrow (robot → camera)
    ax.annotate('', xy=(0.5, 1.2), xytext=(7.7 + 1.4, 1.2),
                arrowprops=dict(arrowstyle='->', color='#999',
                               lw=1.5, linestyle='--',
                               connectionstyle='arc3,rad=0.4'))
    ax.text(4.5, 0.5, "feedback (joint state)", ha='center',
            fontsize=8, color='#999', style='italic')

    ax.set_title("VLA Control Pipeline", fontsize=13, fontweight='bold', pad=10)


# ============================================================
# 7. Readiness Checklist
# ============================================================

def plot_checklist(ax):
    """미리 준비 가능/불가능 체크리스트"""
    ax.axis('off')

    items = [
        ("Embodiment Config", True),
        ("Action Adapter", True),
        ("Safety Clamp Logic", True),
        ("ROS2 Controller", True),
        ("Demo Recorder", True),
        ("VLA Inference Client", True),
        ("OpenPI Train Config", True),
        ("Norm Stats", False),
        ("Camera Calibration", False),
        ("Demo Collection", False),
        ("Fine-tuning", False),
        ("E2E Testing", False),
    ]

    y_start = 0.95
    for i, (name, ready) in enumerate(items):
        y = y_start - i * 0.075
        marker = "●" if ready else "○"
        color = '#4CAF50' if ready else '#F44336'
        status = "READY" if ready else "ON-SITE"

        ax.text(0.05, y, marker, fontsize=14, color=color,
                va='center', transform=ax.transAxes)
        ax.text(0.12, y, name, fontsize=9, va='center',
                transform=ax.transAxes,
                fontweight='bold' if ready else 'normal')
        ax.text(0.75, y, status, fontsize=8, va='center',
                transform=ax.transAxes, color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2',
                         facecolor=color, alpha=0.12, edgecolor=color, linewidth=0.5))

    ready_count = sum(1 for _, r in items if r)
    ax.text(0.5, 0.02, f"{ready_count}/{len(items)} pre-built",
            ha='center', fontsize=10, fontweight='bold', color='#1565C0',
            transform=ax.transAxes)

    ax.set_title("Hackathon Readiness", fontsize=13, fontweight='bold', pad=10)


# ============================================================
# Main: Compose Dashboard
# ============================================================

def create_dashboard():
    fig = plt.figure(figsize=(22, 16), facecolor='#FAFAFA')
    fig.suptitle("Doosan E0509 — Hackathon Pre-Prep Dashboard",
                 fontsize=20, fontweight='bold', color='#1565C0', y=0.98)

    gs = GridSpec(4, 4, figure=fig, hspace=0.4, wspace=0.35,
                  left=0.05, right=0.95, top=0.93, bottom=0.04)

    # Row 0: Spec table + Pipeline
    ax_spec = fig.add_subplot(gs[0, :2])
    ax_pipe = fig.add_subplot(gs[0, 2:])

    # Row 1: Joint ranges (full width)
    ax_joints = fig.add_subplot(gs[1, :3])
    ax_clamp = fig.add_subplot(gs[1, 3])

    # Row 2: Trajectory comparison (3 joints)
    sim_data = simulate_trajectory(100)
    ax_traj = [fig.add_subplot(gs[2, i]) for i in range(3)]
    ax_grip = fig.add_subplot(gs[2, 3])

    # Row 3: Checklist
    ax_check = fig.add_subplot(gs[3, :2])
    ax_extra = fig.add_subplot(gs[3, 2:])

    # Draw all plots
    plot_spec_table(ax_spec)
    plot_pipeline(ax_pipe)
    plot_joint_specs(ax_joints)
    plot_clamp_stats(ax_clamp, sim_data)
    plot_trajectory_comparison(ax_traj, sim_data)
    plot_gripper_timeline(ax_grip, sim_data)
    plot_checklist(ax_check)

    # Extra: delta distribution
    plot_delta_distribution(ax_extra, sim_data)

    output_path = "/home/user/toyexample/doosan_dashboard.png"
    fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#FAFAFA')
    plt.close()
    print(f"Dashboard saved to {output_path}")
    return output_path


def plot_delta_distribution(ax, sim_data):
    """Safe trajectory의 step-wise delta 분포"""
    safe = sim_data['safe']
    deltas = np.diff(safe, axis=0)
    deltas_deg = np.rad2deg(deltas)

    colors = ['#2196F3', '#00BCD4', '#4CAF50', '#FF9800', '#9C27B0', '#F44336']
    labels = [f"J{i+1}" for i in range(6)]

    parts = ax.violinplot(deltas_deg, positions=range(6), showmeans=True, showmedians=True)

    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.6)

    parts['cmeans'].set_color('#333')
    parts['cmedians'].set_color('#333')

    ax.axhline(0, color='#999', linewidth=0.5, linestyle='-')
    max_delta_deg = np.rad2deg(0.05)
    ax.axhline(max_delta_deg, color='red', linewidth=1, linestyle='--', alpha=0.5, label=f'Max delta ({max_delta_deg:.1f}°)')
    ax.axhline(-max_delta_deg, color='red', linewidth=1, linestyle='--', alpha=0.5)

    ax.set_xticks(range(6))
    ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
    ax.set_ylabel("Delta (°/step)", fontsize=10)
    ax.set_title("Joint Delta Distribution (After Clamp)", fontsize=11, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)


if __name__ == "__main__":
    path = create_dashboard()
