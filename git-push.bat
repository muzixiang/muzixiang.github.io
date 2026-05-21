@echo off
title 主页更新 - 提交到 GitHub

echo 正在提交主页更新...
cd /d "D:\我的坚果云\个人主页"

:: 检查是否有变更
git status --porcelain >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到变更或 Git 仓库异常
    pause
    exit /b
)

:: 添加所有变更
git add -A

:: 提交
git commit -m "update: 页面展示升级 - 新增引用统计面板、引用徽标、2026论文"

:: 推送到 GitHub
echo 正在推送到 GitHub...
git push

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo   ✓ 推送成功！
    echo   https://muzixiang.github.io/
    echo   刷新页面后即可看到更新
    echo ============================================
) else (
    echo.
    echo   ✗ 推送失败，请检查 GitHub 凭据是否正确
    echo   可以在 Windows 凭据管理器中查看
)

pause
