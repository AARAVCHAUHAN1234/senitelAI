.PHONY: up seed reset test e2e dev-backend dev-voyagesim dev-frontend

up:
	docker-compose up --build

seed:
	python -m backend.voyagesim.seed
	python -m backend.seed

reset:
	python -c "import os; os.remove('sentinel.db') if os.path.exists('sentinel.db') else None; os.remove('voyagesim.db') if os.path.exists('voyagesim.db') else None"
	$(MAKE) seed

test:
	python -m pytest backend/tests -v

e2e:
	$(MAKE) test

dev-backend:
	python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

dev-voyagesim:
	python -m uvicorn backend.voyagesim.app:app --host 0.0.0.0 --port 8001 --reload

dev-frontend:
	cd frontend && npm run dev
