@echo off
title 主页更新 - 提交到 GitHub
chcp 65001 >nul

cd /d "D:\我的坚果云\个人主页"

echo [1/3] 暂存文件...
git add -A

echo [2/3] 提交...
git commit -m "update: 页面展示升级 - 新增引用统计面板、引用徽标、2026论文"

echo [3/3] 推送到 GitHub...
echo 正在使用 token 认证...
git remote set-url origin https://muzixiang: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@github.com/muzixiang/muzixiang.github.io.git
git push origin main

:: 恢复原始 URL（不包含 token）
git remote set-url origin https://github.com/muzixiang/muzixiang.github.io.git

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo   ✓ 推送成功！
    echo   https://muzixiang.github.io/
    echo   等待几分钟后刷新即可看到更新
    echo ============================================
) else (
    echo.
    echo   ✗ 推送失败，错误码：%errorlevel%
)

pause
