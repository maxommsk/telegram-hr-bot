# 🔗 Настройка синхронизации с GitHub

## 📋 Пошаговая инструкция

### 1. Создание репозитория на GitHub

1. **Перейдите на GitHub.com** и войдите в свой аккаунт
2. **Нажмите "New repository"** (зеленая кнопка)
3. **Заполните данные репозитория:**
   - Repository name: `telegram_hr_bot_postgresql`
   - Description: `Telegram HR Bot with PostgreSQL for job search and recruitment`
   - Visibility: `Public` (или `Private` по желанию)
   - ❌ **НЕ** инициализируйте с README, .gitignore или лицензией
4. **Нажмите "Create repository"**

### 2. Подключение локального репозитория

После создания репозитория GitHub покажет инструкции. Выполните команды:

```bash
# Добавляем удаленный репозиторий
git remote add origin https://github.com/YOUR_USERNAME/telegram_hr_bot_postgresql.git

# Переименовываем ветку в main (если нужно)
git branch -M main

# Отправляем код на GitHub
git push -u origin main
```

### 3. Настройка SSH (рекомендуется)

Для удобной работы без ввода пароля каждый раз:

```bash
# Генерируем SSH ключ
ssh-keygen -t ed25519 -C "your_email@example.com"

# Добавляем ключ в ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Копируем публичный ключ
cat ~/.ssh/id_ed25519.pub
```

Затем:
1. Перейдите в **Settings → SSH and GPG keys** на GitHub
2. Нажмите **"New SSH key"**
3. Вставьте скопированный ключ
4. Измените URL репозитория на SSH:

```bash
git remote set-url origin git@github.com:YOUR_USERNAME/telegram_hr_bot_postgresql.git
```

### 4. Настройка .env для GitHub

Создайте файл `.env.example` с примером конфигурации:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=telegram_hr_bot
POSTGRES_USER=hr_bot_user
POSTGRES_PASSWORD=YOUR_PASSWORD_HERE

# Flask Configuration
FLASK_SECRET_KEY=your_super_secret_key_here_change_in_production
FLASK_DEBUG=True
PORT=5000

# Notification Settings
NOTIFICATION_ENABLED=true

# File Upload Settings
MAX_CONTENT_LENGTH=16777216

# Database URL (alternative to separate params)
# DATABASE_URL=postgresql://user:password@host:port/database
```

### 5. Настройка GitHub Actions (CI/CD)

Создайте файл `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        TELEGRAM_BOT_TOKEN: test_token
      run: |
        python -m pytest tests/ -v
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Yandex Cloud
      run: |
        echo "Deployment to Yandex Cloud would happen here"
        # Здесь будут команды для деплоя
```

### 6. Защита секретов

В настройках репозитория GitHub:
1. Перейдите в **Settings → Secrets and variables → Actions**
2. Добавьте секреты:
   - `TELEGRAM_BOT_TOKEN`
   - `POSTGRES_PASSWORD`
   - `FLASK_SECRET_KEY`
   - `YC_SERVICE_ACCOUNT_KEY` (для деплоя)

### 7. Настройка веток

Создайте ветку для разработки:

```bash
# Создаем ветку develop
git checkout -b develop
git push -u origin develop

# Настраиваем защиту main ветки на GitHub
# Settings → Branches → Add rule
# - Branch name pattern: main
# - Require pull request reviews before merging
# - Require status checks to pass before merging
```

### 8. Рабочий процесс разработки

```bash
# Создание новой функции
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# Разработка...
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# Создание Pull Request на GitHub
# develop ← feature/new-feature

# После ревью и мержа в develop
git checkout develop
git pull origin develop

# Релиз в main
git checkout main
git pull origin main
git merge develop
git push origin main
```

### 9. Автоматическое обновление зависимостей

Создайте файл `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

### 10. Шаблоны Issues и PR

Создайте файлы:

`.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment:**
- OS: [e.g. Windows 10]
- Python version: [e.g. 3.11]
- Bot version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### 11. Коммиты и теги

Используйте семантическое версионирование:

```bash
# Создание тега релиза
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Формат коммитов
git commit -m "feat: add job search functionality"
git commit -m "fix: resolve database connection issue"
git commit -m "docs: update README with deployment instructions"
```

### 12. Мониторинг репозитория

Настройте уведомления:
1. **Watch** репозиторий для получения уведомлений
2. Настройте **GitHub Desktop** или **VS Code** для удобной работы
3. Используйте **GitHub CLI** для автоматизации:

```bash
# Установка GitHub CLI
# Windows: winget install GitHub.cli
# Mac: brew install gh

# Аутентификация
gh auth login

# Создание PR из командной строки
gh pr create --title "New feature" --body "Description"
```

## ✅ Проверка настройки

После выполнения всех шагов проверьте:

- [ ] Репозиторий создан на GitHub
- [ ] Локальный код синхронизирован
- [ ] SSH ключи настроены
- [ ] .env.example создан
- [ ] GitHub Actions настроены
- [ ] Секреты добавлены
- [ ] Ветки защищены
- [ ] Dependabot настроен
- [ ] Шаблоны созданы

## 🔄 Ежедневная работа

```bash
# Начало рабочего дня
git checkout develop
git pull origin develop

# Создание новой задачи
git checkout -b feature/task-name

# Работа...
git add .
git commit -m "feat: implement task"
git push origin feature/task-name

# Создание PR через веб-интерфейс или CLI
gh pr create --base develop
```

Теперь ваш проект готов к совместной разработке и автоматическому деплою! 🚀

