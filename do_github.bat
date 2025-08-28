@echo off
@echo off
chcp 65001 >nul

set REPO_URL=https://github.com/JOVIANpega/MU310_FW_GUI.git

echo ============================================
echo [Step 0] 檢查是否已經設定 GitHub 遠端 origin
echo ============================================
git remote -v | find "origin" >nul
if errorlevel 1 (
    echo 沒有找到 origin，現在新增...
    git remote add origin %REPO_URL%
) else (
    echo 已經有設定 origin
)

echo ============================================
echo [Step 1] 清理 Git 歷史中所有超過 100MB 的檔案
echo ============================================
git filter-repo --strip-blobs-bigger-than 100M --force

echo ============================================
echo [Step 2] 更新 .gitignore (忽略所有 .bin 檔)
echo ============================================
echo *.bin>>.gitignore
git add .gitignore
git commit -m "ignore all .bin files" || echo (no changes to commit)

echo ============================================
echo [Step 3] 推送到 GitHub (強制覆蓋)
echo ============================================
git push origin main --force

echo ============================================
echo ✅ 完成！檢查 GitHub Repo 確認是否成功
echo ============================================
pause
