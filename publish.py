# -*- coding: utf-8 -*-
import os
import re
import subprocess
import sys

# Путь к папке релизов (она же служит Git-репозиторием)
RELEASE_DIR = r"D:\Project_Evgenii\Новая программа\Резервная копия\Update Project"
WORK_DIR = r"D:\Project_Evgenii\Новая программа\Workpeace"

def get_current_version():
    """Читает версию из файла __version__.py в рабочей папке"""
    version_file = os.path.join(WORK_DIR, "__version__.py")
    if not os.path.exists(version_file):
        print(f"❌ Файл __version__.py не найден по пути: {version_file}")
        sys.exit(1)
    
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1).strip()
    print("❌ Не удалось найти переменную VERSION в __version__.py!")
    sys.exit(1)

def find_latest_exe():
    """Ищет самый свежий exe-файл в папке Update Project"""
    if not os.path.exists(RELEASE_DIR):
        print(f"❌ Папка релизов не найдена: {RELEASE_DIR}")
        sys.exit(1)
    
    exe_files = [f for f in os.listdir(RELEASE_DIR) if f.lower().endswith(".exe")]
    if not exe_files:
        print(f"❌ В папке {RELEASE_DIR} нет готовых .exe файлов для релиза!")
        sys.exit(1)
    
    exe_files.sort(key=lambda x: os.path.getmtime(os.path.join(RELEASE_DIR, x)))
    latest = exe_files[-1]
    return os.path.join(RELEASE_DIR, latest), latest

def run_cmd(cmd, cwd=None):
    """Выполняет консольную команду в указанной директории"""
    print(f"⚙️ Выполнение: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd)
    if res.returncode != 0:
        print(f"❌ Ошибка при выполнении команды: {cmd}")
        sys.exit(1)

def main():
    version = get_current_version()
    tag = f"v{version}"
    exe_path, exe_name = find_latest_exe()
    
    print("=" * 60)
    print(f"🚀 ПУБЛИКАЦИЯ РЕЛИЗА ИЗ ПАПКИ UPDATE PROJECT: {tag}")
    print(f"📦 Файл сборки: {exe_name}")
    print("=" * 60)
    
    # 1. Инициализация Git, если её ещё нет
    git_folder = os.path.join(RELEASE_DIR, ".git")
    if not os.path.exists(git_folder):
        print("⚙️ Инициализация Git-репозитория в папке Update Project...")
        run_cmd("git init", cwd=RELEASE_DIR)
        run_cmd("git remote add origin https://github.com/evgenii98prokopev-lang/DynamicIsland.git", cwd=RELEASE_DIR)

    # 2. Автоматическая настройка локального пользователя Git
    run_cmd('git config user.name "Evgenii"', cwd=RELEASE_DIR)
    run_cmd('git config user.email "evgenii@example.com"', cwd=RELEASE_DIR)

    # 3. Операции Git
    run_cmd("git status", cwd=RELEASE_DIR)
    run_cmd("git add .", cwd=RELEASE_DIR)
    
    # Делаем коммит (если выдаст ошибку, что нечего коммитить — скрипт пойдет дальше)
    commit_msg = f"Release {tag}"
    subprocess.run(f'git commit -m "{commit_msg}"', shell=True, cwd=RELEASE_DIR)

    # Проверяем какая ветка (main или master) и пушим
    run_cmd("git push -u origin master", cwd=RELEASE_DIR)
    
    # Обновление тега локально и на удаленном сервере
    run_cmd(f"git tag -f {tag}", cwd=RELEASE_DIR)
    run_cmd(f"git push origin {tag} --force", cwd=RELEASE_DIR)
    
    # 4. Публикация релиза через GitHub CLI (с удалением старого тега на всякий случай)
    subprocess.run(f'gh release delete "{tag}" --yes', shell=True, cwd=RELEASE_DIR)
    
    gh_cmd = f'gh release create "{tag}" "{exe_path}" --title "Dynamic Island {tag}" --notes "Автоматический релиз версии {version}"'
    run_cmd(gh_cmd, cwd=RELEASE_DIR)
    
    print("=" * 60)
    print(f"🎉 Релиз {tag} успешно опубликован!")
    print("=" * 60)

if __name__ == "__main__":
    main()