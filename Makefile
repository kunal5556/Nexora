.PHONY: up down logs

up:
	docker compose up --build -d
	@echo Frontend: http://localhost:3000
	@echo Backend: http://localhost:8000

down:
	docker compose down

logs:
	docker compose logs -f
