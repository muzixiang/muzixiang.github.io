import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import StringIO
import numpy as np

# 1. 准备数据
csv_content = 'detect_result_20251219_183954.csv'  # 假设CSV文件内容已存储在此变量中
#csv_content = 'detect_result_20251224_095527.csv'

# 2. 读取数据为DataFrame
try:
    df = pd.read_csv(csv_content)
except Exception as e:
    print(f"Error reading CSV: {e}")
    # 尝试更健壮的读取方式，防止格式问题
    df = pd.read_csv(StringIO(csv_content), on_bad_lines='skip')

# 3. 数据预处理
# 将时间戳转换为 datetime 对象，以便于绘图
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 4. 设置绘图风格
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (15, 12)
plt.rcParams['font.family'] = 'sans-serif' # 避免中文字体问题，使用默认无衬线字体
# 如果需要支持中文，可以尝试设置 font.sans-serif 为 ['SimHei'] 或其他中文字体，但云端环境可能不支持

# 创建一个包含4个子图的画布
fig, axes = plt.subplots(4, 1, sharex=True)

# ===== Feature 0 绘图 =====

# 子图 1: Feature 0 真实值 vs 预测值
ax0 = axes[0]
ax0.plot(df['timestamp'], df['feat_0_real'], label='Real', color='#1f77b4', alpha=0.8, linewidth=1.5)
ax0.plot(df['timestamp'], df['feat_0_pred'], label='Pred', color='#2ca02c', alpha=0.8, linewidth=1.5, linestyle='--')

# 标记异常点 (Feature 0)
anomalies_0 = df[df['feat_0_is_anomaly'] == 1]
ax0.scatter(anomalies_0['timestamp'], anomalies_0['feat_0_real'], color='red', label='Anomaly', s=50, zorder=5)

ax0.set_title('Feature 0: Real vs Prediction', fontsize=14, fontweight='bold')
ax0.set_ylabel('Value', fontsize=12)
ax0.legend(loc='upper right')
ax0.grid(True, linestyle='--', alpha=0.6)

# 子图 2: Feature 0 正常概率 (Normal Probability)
ax1 = axes[1]
# 绘制正常概率曲线
ax1.plot(df['timestamp'], df['feat_0_norm_prob'], label='Normal Probability', color='#9467bd', linewidth=1.5)
# 可以选择用红色填充低概率区域（即高异常风险区域）
ax1.fill_between(df['timestamp'], 0, df['feat_0_norm_prob'], color='#9467bd', alpha=0.1)

# 标记异常区域对应的概率点
ax1.scatter(anomalies_0['timestamp'], anomalies_0['feat_0_norm_prob'], color='red', s=30, zorder=5)

ax1.set_title('Feature 0: Normal Probability (Lower is more anomalous)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Probability', fontsize=12)
ax1.set_ylim(-0.05, 1.05) # 概率范围固定在0-1之间
ax1.legend(loc='lower right')
ax1.grid(True, linestyle='--', alpha=0.6)


# ===== Feature 1 绘图 =====

# 子图 3: Feature 1 真实值 vs 预测值
ax2 = axes[2]
ax2.plot(df['timestamp'], df['feat_1_real'], label='Real', color='#1f77b4', alpha=0.8, linewidth=1.5)
ax2.plot(df['timestamp'], df['feat_1_pred'], label='Pred', color='#2ca02c', alpha=0.8, linewidth=1.5, linestyle='--')

# 标记异常点 (Feature 1)
anomalies_1 = df[df['feat_1_is_anomaly'] == 1]
ax2.scatter(anomalies_1['timestamp'], anomalies_1['feat_1_real'], color='red', label='Anomaly', s=50, zorder=5)

ax2.set_title('Feature 1: Real vs Prediction', fontsize=14, fontweight='bold')
ax2.set_ylabel('Value', fontsize=12)
ax2.legend(loc='upper right')
ax2.grid(True, linestyle='--', alpha=0.6)

# 子图 4: Feature 1 正常概率 (Normal Probability)
ax3 = axes[3]
# 绘制正常概率曲线
ax3.plot(df['timestamp'], df['feat_1_norm_prob'], label='Normal Probability', color='#9467bd', linewidth=1.5)
# 填充
ax3.fill_between(df['timestamp'], 0, df['feat_1_norm_prob'], color='#9467bd', alpha=0.1)

# 标记异常区域对应的概率点
ax3.scatter(anomalies_1['timestamp'], anomalies_1['feat_1_norm_prob'], color='red', s=30, zorder=5)

ax3.set_title('Feature 1: Normal Probability (Lower is more anomalous)', fontsize=14, fontweight='bold')
ax3.set_ylabel('Probability', fontsize=12)
ax3.set_xlabel('Timestamp', fontsize=12)
ax3.set_ylim(-0.05, 1.05)
ax3.legend(loc='lower right')
ax3.grid(True, linestyle='--', alpha=0.6)

# 格式化X轴时间显示
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate() # 自动旋转日期标签

plt.tight_layout()

# 保存并显示
save_path = 'anomaly_detection_plot.png'
plt.savefig(save_path)
print(f"Plot saved to {save_path}")