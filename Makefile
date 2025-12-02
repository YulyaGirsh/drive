.PHONY: build up down restart logs shell clean

# Сборка образа
build:
	docker-compose build

# Запуск контейнера
up:
	docker-compose up -d

# Остановка контейнера
down:
	docker-compose down

# Перезапуск
restart:
	docker-compose restart

# Просмотр логов
logs:
	docker-compose logs -f

# Вход в контейнер
shell:
	docker-compose exec easydrive-server bash

# Очистка (остановка и удаление контейнеров, образов, volumes)
clean:
	docker-compose down -v
	docker rmi easydrive-server_easydrive-server 2>/dev/null || true

# Полная пересборка
rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Статус
status:
	docker-compose ps

