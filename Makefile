setup:
	@bash scripts/setup.sh

install:
	@bash scripts/install.sh

pip:
	.venv/bin/pip install -r backend/requirements.txt

npm:
	cd frontend && npm install && cd ..

dev:
	make dev-rabbitmq
	make dev-supertokens
	make backend &
	make celery-worker &
	make frontend

compose:
	docker compose -f 'compose.yaml' up -d --build

down:
	docker compose -f 'compose.yaml' down

backend:
	cd backend && ../.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8123 --reload

frontend:
	cd frontend && npm run dev

dev-rabbitmq:
	docker run -d --name rabbitmq-dev -p 5672:5672 -p 15672:15672 rabbitmq:3-management || docker start rabbitmq-dev

dev-supertokens:
	@set -a; source backend/.env; set +a; \
	docker run -d --name supertokens-dev -p 3567:3567 -e POSTGRESQL_CONNECTION_URI="$$SUPERTOKENS_DATABASE_URL" registry.supertokens.io/supertokens/supertokens-postgresql:latest || docker start supertokens-dev

celery-worker:
	cd backend && ../.venv/bin/celery -A src.services.email_impl.celery_app:app worker -l INFO --concurrency=1

stop-rabbitmq:
	docker stop rabbitmq-dev || true

stop-supertokens:
	docker stop supertokens-dev || true

clean-rabbitmq:
	docker stop rabbitmq-dev || true
	docker rm rabbitmq-dev || true

clean-supertokens:
	docker stop supertokens-dev || true
	docker rm supertokens-dev || true

test:
	echo "Test test 1 2 3..."

create-db:
	@echo "Creating database tables in Docker..."
	docker compose exec backend python -m backend.src.db_manager create

reset-db:
	@echo "Resetting database in Docker..."
	docker compose exec backend python -m backend.src.db_manager reset

reset-db-force:
	@echo "Force resetting database in Docker..."
	docker compose exec backend python -m backend.src.db_manager reset --force

drop-db:
	@echo "Dropping database tables in Docker..."
	docker compose exec backend python -m backend.src.db_manager drop

kill:
	@echo "Stopping Docker containers..."
	@docker stop rabbitmq-dev 2>/dev/null && echo "Stopped rabbitmq-dev container" || echo "No rabbitmq-dev container running"
	@docker stop supertokens-dev 2>/dev/null && echo "Stopped supertokens-dev container" || echo "No supertokens-dev container running"
	@docker compose -f 'compose.yaml' down 2>/dev/null && echo "Stopped docker-compose services" || echo "No docker-compose services running"
	@echo "Killing processes on app ports..."
	@for port in 8123 5672 15672 5173 3567; do \
		pid=$$(lsof -ti :$$port 2>/dev/null); \
		if [ -n "$$pid" ]; then \
			echo "Killing process $$pid on port $$port"; \
			kill -9 $$pid 2>/dev/null || true; \
		else \
			echo "No process found on port $$port"; \
		fi; \
	done
	@echo "Done!"

.PHONY: setup install pip npm dev backend frontend compose down dev-rabbitmq dev-supertokens celery-worker stop-rabbitmq stop-supertokens clean-rabbitmq clean-supertokens test create-db reset-db reset-db-force drop-db kill
