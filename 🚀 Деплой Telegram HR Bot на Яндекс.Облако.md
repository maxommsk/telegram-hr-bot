# 🚀 Деплой Telegram HR Bot на Яндекс.Облако

## 📋 Обзор стратегий деплоя

### 1. Compute Cloud (Виртуальные машины) ⭐ Рекомендуется
**Преимущества:**
- Полный контроль над окружением
- Простота настройки и отладки
- Предсказуемая стоимость
- Возможность использования Docker

**Недостатки:**
- Требует управления инфраструктурой
- Необходимо настраивать автомасштабирование вручную

### 2. Serverless Containers
**Преимущества:**
- Автоматическое масштабирование
- Оплата только за использование
- Не требует управления серверами

**Недостатки:**
- Ограничения по времени выполнения
- Холодный старт
- Сложности с долгоживущими соединениями (Telegram polling)

### 3. Managed Kubernetes
**Преимущества:**
- Высокая отказоустойчивость
- Автоматическое масштабирование
- Продвинутые возможности оркестрации

**Недостатки:**
- Сложность настройки
- Высокая стоимость для небольших проектов

## 🎯 Выбранная стратегия: Compute Cloud + Managed PostgreSQL

Для нашего проекта оптимальным решением является:
- **Compute Cloud VM** для приложения
- **Managed Service for PostgreSQL** для базы данных
- **Container Registry** для хранения Docker образов
- **Application Load Balancer** для балансировки нагрузки

## 🛠 Пошаговая инструкция деплоя

### Шаг 1: Подготовка Яндекс.Облако

#### 1.1 Создание аккаунта и настройка CLI
```bash
# Установка Yandex Cloud CLI (Windows)
# Скачайте с https://cloud.yandex.ru/docs/cli/quickstart
# Или через PowerShell:
iex (New-Object System.Net.WebClient).DownloadString('https://storage.yandexcloud.net/yandexcloud-yc/install.ps1')

# Инициализация CLI
yc init

# Проверка конфигурации
yc config list
```

#### 1.2 Создание каталога и настройка сети
```bash
# Создание каталога
yc resource-manager folder create --name telegram-hr-bot

# Получение ID каталога
yc resource-manager folder list

# Установка каталога по умолчанию
yc config set folder-id <FOLDER_ID>

# Создание VPC сети
yc vpc network create --name hr-bot-network --description "Network for HR Bot"

# Создание подсети
yc vpc subnet create \
  --name hr-bot-subnet \
  --network-name hr-bot-network \
  --zone ru-central1-a \
  --range 10.1.0.0/24
```

#### 1.3 Создание сервисного аккаунта
```bash
# Создание сервисного аккаунта
yc iam service-account create --name hr-bot-sa --description "Service account for HR Bot"

# Назначение ролей
yc resource-manager folder add-access-binding <FOLDER_ID> \
  --role container-registry.images.puller \
  --subject serviceAccount:<SERVICE_ACCOUNT_ID>

yc resource-manager folder add-access-binding <FOLDER_ID> \
  --role compute.editor \
  --subject serviceAccount:<SERVICE_ACCOUNT_ID>

# Создание ключа для сервисного аккаунта
yc iam key create --service-account-name hr-bot-sa --output key.json
```

### Шаг 2: Настройка Container Registry

```bash
# Создание реестра
yc container registry create --name hr-bot-registry

# Настройка Docker для работы с реестром
yc container registry configure-docker

# Получение ID реестра
yc container registry list
```

### Шаг 3: Создание Managed PostgreSQL

```bash
# Создание кластера PostgreSQL
yc managed-postgresql cluster create \
  --name hr-bot-postgres \
  --environment production \
  --network-name hr-bot-network \
  --host zone-id=ru-central1-a,subnet-name=hr-bot-subnet \
  --postgresql-version 15 \
  --resource-preset s2.micro \
  --disk-type network-ssd \
  --disk-size 20 \
  --user name=hr_bot_user,password=<STRONG_PASSWORD> \
  --database name=telegram_hr_bot,owner=hr_bot_user

# Получение информации о кластере
yc managed-postgresql cluster list
yc managed-postgresql cluster get hr-bot-postgres

# Настройка доступа (добавление IP адресов)
yc managed-postgresql cluster update hr-bot-postgres \
  --security-group-ids <SECURITY_GROUP_ID>
```

### Шаг 4: Сборка и загрузка Docker образа

```bash
# Сборка образа
docker build -t hr-bot:latest .

# Тегирование для реестра
docker tag hr-bot:latest cr.yandex/<REGISTRY_ID>/hr-bot:latest

# Загрузка в реестр
docker push cr.yandex/<REGISTRY_ID>/hr-bot:latest
```

### Шаг 5: Создание виртуальной машины

#### 5.1 Создание группы безопасности
```bash
# Создание группы безопасности
yc vpc security-group create \
  --name hr-bot-sg \
  --network-name hr-bot-network \
  --rule "direction=ingress,port=22,protocol=tcp,v4-cidrs=[0.0.0.0/0]" \
  --rule "direction=ingress,port=80,protocol=tcp,v4-cidrs=[0.0.0.0/0]" \
  --rule "direction=ingress,port=443,protocol=tcp,v4-cidrs=[0.0.0.0/0]" \
  --rule "direction=ingress,port=5000,protocol=tcp,v4-cidrs=[0.0.0.0/0]" \
  --rule "direction=egress,protocol=any,v4-cidrs=[0.0.0.0/0]"
```

#### 5.2 Создание cloud-init скрипта
Создайте файл `cloud-init.yaml`:

```yaml
#cloud-config
users:
  - name: hr-bot
    groups: sudo
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    ssh_authorized_keys:
      - ssh-rsa YOUR_PUBLIC_SSH_KEY

packages:
  - docker.io
  - docker-compose
  - nginx
  - certbot
  - python3-certbot-nginx

runcmd:
  # Настройка Docker
  - systemctl start docker
  - systemctl enable docker
  - usermod -aG docker hr-bot
  
  # Создание директорий
  - mkdir -p /opt/hr-bot
  - chown hr-bot:hr-bot /opt/hr-bot
  
  # Настройка автозапуска
  - systemctl enable docker
  
write_files:
  - path: /opt/hr-bot/.env
    content: |
      TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
      POSTGRES_HOST=YOUR_POSTGRES_HOST
      POSTGRES_PORT=6432
      POSTGRES_DB=telegram_hr_bot
      POSTGRES_USER=hr_bot_user
      POSTGRES_PASSWORD=YOUR_PASSWORD
      FLASK_SECRET_KEY=YOUR_SECRET_KEY
      FLASK_ENV=production
      FLASK_DEBUG=False
      NOTIFICATION_ENABLED=true
    owner: hr-bot:hr-bot
    permissions: '0600'
  
  - path: /opt/hr-bot/docker-compose.prod.yml
    content: |
      version: '3.8'
      services:
        app:
          image: cr.yandex/YOUR_REGISTRY_ID/hr-bot:latest
          container_name: hr_bot_app
          env_file: .env
          ports:
            - "5000:5000"
          volumes:
            - ./logs:/app/logs
            - ./uploads:/app/uploads
          restart: unless-stopped
          healthcheck:
            test: ["CMD", "curl", "-f", "http://localhost:5000/api/stats"]
            interval: 30s
            timeout: 10s
            retries: 3
    owner: hr-bot:hr-bot
    permissions: '0644'

  - path: /etc/nginx/sites-available/hr-bot
    content: |
      server {
          listen 80;
          server_name YOUR_DOMAIN.com;
          
          location / {
              proxy_pass http://localhost:5000;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
          }
          
          location /health {
              access_log off;
              return 200 "healthy\n";
              add_header Content-Type text/plain;
          }
      }
    permissions: '0644'
```

#### 5.3 Создание VM
```bash
# Создание виртуальной машины
yc compute instance create \
  --name hr-bot-vm \
  --zone ru-central1-a \
  --network-interface subnet-name=hr-bot-subnet,nat-ip-version=ipv4,security-group-ids=<SECURITY_GROUP_ID> \
  --create-boot-disk image-folder-id=standard-images,image-family=ubuntu-2004-lts,size=20,type=network-ssd \
  --memory 2 \
  --cores 2 \
  --core-fraction 100 \
  --service-account-name hr-bot-sa \
  --ssh-key ~/.ssh/id_rsa.pub \
  --metadata-from-file user-data=cloud-init.yaml
```

### Шаг 6: Настройка домена и SSL

#### 6.1 Настройка DNS
```bash
# Получение внешнего IP адреса VM
yc compute instance get hr-bot-vm --format json | jq -r '.network_interfaces[0].primary_v4_address.one_to_one_nat.address'

# Настройте A-запись в вашем DNS провайдере:
# your-domain.com -> EXTERNAL_IP
```

#### 6.2 Подключение к VM и настройка SSL
```bash
# Подключение к VM
ssh hr-bot@<EXTERNAL_IP>

# Активация сайта Nginx
sudo ln -s /etc/nginx/sites-available/hr-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com

# Настройка автообновления сертификата
sudo crontab -e
# Добавьте строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### Шаг 7: Запуск приложения

```bash
# Переход в директорию приложения
cd /opt/hr-bot

# Аутентификация в Container Registry
sudo docker login cr.yandex

# Запуск приложения
sudo docker-compose -f docker-compose.prod.yml up -d

# Проверка статуса
sudo docker-compose -f docker-compose.prod.yml ps
sudo docker-compose -f docker-compose.prod.yml logs -f
```

### Шаг 8: Настройка мониторинга

#### 8.1 Создание скрипта мониторинга
```bash
# Создание скрипта проверки здоровья
cat > /opt/hr-bot/health-check.sh << 'EOF'
#!/bin/bash
HEALTH_URL="http://localhost:5000/api/stats"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
TELEGRAM_BOT_TOKEN="YOUR_MONITORING_BOT_TOKEN"

if ! curl -f -s $HEALTH_URL > /dev/null; then
    MESSAGE="🚨 HR Bot is DOWN! Server: $(hostname)"
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
         -d chat_id=$TELEGRAM_CHAT_ID \
         -d text="$MESSAGE"
    
    # Попытка перезапуска
    cd /opt/hr-bot
    sudo docker-compose -f docker-compose.prod.yml restart
fi
EOF

chmod +x /opt/hr-bot/health-check.sh

# Добавление в crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/hr-bot/health-check.sh") | crontab -
```

#### 8.2 Настройка логирования
```bash
# Настройка ротации логов
sudo tee /etc/logrotate.d/hr-bot << 'EOF'
/opt/hr-bot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 hr-bot hr-bot
    postrotate
        docker-compose -f /opt/hr-bot/docker-compose.prod.yml restart app
    endscript
}
EOF
```

### Шаг 9: Настройка автоматического деплоя

#### 9.1 GitHub Actions для автодеплоя
Создайте файл `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Yandex Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Yandex Container Registry
      uses: docker/login-action@v2
      with:
        registry: cr.yandex
        username: json_key
        password: ${{ secrets.YC_SERVICE_ACCOUNT_KEY }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: cr.yandex/${{ secrets.YC_REGISTRY_ID }}/hr-bot:latest
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: hr-bot
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /opt/hr-bot
          sudo docker-compose -f docker-compose.prod.yml pull
          sudo docker-compose -f docker-compose.prod.yml up -d
          sudo docker system prune -f
```

#### 9.2 Настройка секретов в GitHub
В настройках репозитория добавьте секреты:
- `YC_SERVICE_ACCOUNT_KEY` - содержимое key.json
- `YC_REGISTRY_ID` - ID Container Registry
- `SERVER_HOST` - внешний IP адрес VM
- `SSH_PRIVATE_KEY` - приватный SSH ключ

### Шаг 10: Настройка резервного копирования

```bash
# Создание скрипта резервного копирования
cat > /opt/hr-bot/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/hr-bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
POSTGRES_HOST="YOUR_POSTGRES_HOST"
POSTGRES_DB="telegram_hr_bot"
POSTGRES_USER="hr_bot_user"

mkdir -p $BACKUP_DIR

# Резервная копия базы данных
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
  -h $POSTGRES_HOST \
  -U $POSTGRES_USER \
  -d $POSTGRES_DB \
  --no-password \
  | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Резервная копия файлов
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz \
  /opt/hr-bot/uploads \
  /opt/hr-bot/logs \
  /opt/hr-bot/.env

# Удаление старых резервных копий (старше 30 дней)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/hr-bot/backup.sh

# Добавление в crontab (ежедневно в 3:00)
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/hr-bot/backup.sh") | crontab -
```

## 📊 Мониторинг и метрики

### Основные метрики для отслеживания:
- Доступность приложения (uptime)
- Время отклика API
- Количество активных пользователей
- Количество обработанных сообщений
- Использование ресурсов (CPU, RAM, диск)
- Статус подключения к базе данных

### Настройка алертов:
- Недоступность приложения > 5 минут
- Время отклика > 5 секунд
- Использование CPU > 80%
- Использование RAM > 90%
- Свободное место на диске < 10%

## 💰 Примерная стоимость

### Минимальная конфигурация:
- **Compute Cloud VM** (2 vCPU, 2 GB RAM): ~1,500₽/месяц
- **Managed PostgreSQL** (s2.micro): ~2,000₽/месяц
- **Container Registry**: ~100₽/месяц
- **Трафик**: ~500₽/месяц
- **Итого**: ~4,100₽/месяц

### Рекомендуемая конфигурация:
- **Compute Cloud VM** (4 vCPU, 4 GB RAM): ~3,000₽/месяц
- **Managed PostgreSQL** (s2.small): ~4,000₽/месяц
- **Application Load Balancer**: ~1,000₽/месяц
- **Container Registry**: ~200₽/месяц
- **Трафик**: ~1,000₽/месяц
- **Итого**: ~9,200₽/месяц

## 🔧 Оптимизация производительности

### 1. Кэширование
- Используйте Redis для кэширования частых запросов
- Кэшируйте результаты поиска вакансий
- Кэшируйте пользовательские сессии

### 2. Оптимизация базы данных
- Создайте индексы для часто используемых полей
- Используйте connection pooling
- Настройте автовакуум PostgreSQL

### 3. Масштабирование
- Используйте несколько инстансов приложения
- Настройте Application Load Balancer
- Рассмотрите использование CDN для статических файлов

## 🚨 Безопасность

### 1. Сетевая безопасность
- Настройте группы безопасности
- Используйте VPN для административного доступа
- Ограничьте доступ к базе данных

### 2. Безопасность приложения
- Регулярно обновляйте зависимости
- Используйте HTTPS для всех соединений
- Настройте rate limiting

### 3. Мониторинг безопасности
- Отслеживайте подозрительную активность
- Настройте алерты на неудачные попытки входа
- Регулярно проверяйте логи

---

**Готово! Ваш Telegram HR Bot успешно развернут на Яндекс.Облако! 🎉**

