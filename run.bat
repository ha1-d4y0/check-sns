@echo off
cd /d "%~dp0"

echo ==========================================
echo  モニタリングモードを選択してください
echo ==========================================
echo [1] ライブステータス表示 (status)
echo [2] 全データ表示 (all)
echo ==========================================

choice /c 12 /n /m "番号を入力してください (1 または 2): "

if errorlevel 2 (
    echo.
    echo --- 全データモードで起動中 ---
    python check-sns.py all
) else if errorlevel 1 (
    echo.
    echo --- ライブステータスモードで起動中 ---
    python check-sns.py status
)

echo.
pause
