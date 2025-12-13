import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# ==========================================
# 1. 模拟数据生成 (Simulate Data)
# ==========================================
np.random.seed(42)

# 生成“正常”的训练集重构误差 (通常误差服从 Gamma 或 对数正态分布，是右偏的)
# shape=2, scale=0.5 模拟一般的低误差波动
train_errors = np.random.gamma(shape=2, scale=0.5, size=1000)

# 生成测试集：前半段正常，中间突然出现异常(误差变大)，后半段恢复
test_errors = np.random.gamma(shape=2, scale=0.5, size=200)
# 在索引 100-130 之间人为加入异常（误差值显著升高）
test_errors[100:130] += np.random.normal(loc=4.0, scale=0.5, size=30)

# ==========================================
# 2. 核心计算逻辑 (你的需求)
# ==========================================

# A. 对数据进行 Log 变换
# 理由：原始误差 >=0 且右偏，不符合高斯分布假设。Log 变换后更接近正态分布。
# 加 1e-6 是为了防止 log(0) 报错
train_log = np.log(train_errors + 1e-6)
test_log = np.log(test_errors + 1e-6)

# B. 在训练集上统计参数 (mu, sigma)
mu = np.mean(train_log)
sigma = np.std(train_log)

print(f"训练集 Log后均值(mu): {mu:.4f}, 标准差(sigma): {sigma:.4f}")

# C. 计算异常概率 (Anomaly Probability)
# 使用 CDF：计算“当前误差值在统计分布中出现的累计概率”
# 如果结果接近 1 (如 0.999)，说明该误差值在正常分布中极难出现，属于异常
anomaly_probs = norm.cdf(test_log, loc=mu, scale=sigma)

# ==========================================
# 3. 绘图展示
# ==========================================
plt.figure(figsize=(12, 8))

# 子图 1: 原始重构误差
plt.subplot(2, 1, 1)
plt.plot(test_errors, color='blue', label='Reconstruction Error')
plt.axvspan(100, 130, color='red', alpha=0.1, label='True Anomaly Region')
plt.title("Step 1: Raw Reconstruction Errors (Test Set)")
plt.ylabel("Error Value")
plt.legend()
plt.grid(True, alpha=0.3)

# 子图 2: 计算出的异常概率
plt.subplot(2, 1, 2)
plt.plot(anomaly_probs, color='orange', linewidth=2, label='Anomaly Probability')
plt.axvspan(100, 130, color='red', alpha=0.1)

# 画一条 0.99 的警戒线
plt.axhline(y=0.99, color='red', linestyle='--', label='Threshold (0.99)')

plt.title("Step 2: Converted Anomaly Probability (0 to 1)")
plt.ylabel("Probability")
plt.xlabel("Time Step")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 打印一下异常区域的一个样本数据看看
idx = 110
print(f"\n--- 样本检查 (Index {idx}) ---")
print(f"原始误差值: {test_errors[idx]:.4f}")
print(f"Log转换值:  {test_log[idx]:.4f}")
print(f"异常概率:   {anomaly_probs[idx]:.8f}")