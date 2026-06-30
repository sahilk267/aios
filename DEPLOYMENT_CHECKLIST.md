# AIOS Deployment Checklist

## Pre-Deployment
- [ ] Docker and Docker Compose installed
- [ ] Python 3.11+ installed
- [ ] Git configured
- [ ] Environment variables set (.env file)
- [ ] Data directories created

## Deployment Steps
1. Run `./scripts/setup.sh` for initial setup
2. Run `./scripts/deploy.sh` to start all services
3. Verify health: `curl http://localhost:8000/api/v1/health`
4. Access API docs: http://localhost:8000/docs
5. Access Grafana: http://localhost:3000

## Services
| Service | URL | Description |
|---------|-----|-------------|
| Backend | http://localhost:8000 | FastAPI application |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Grafana | http://localhost:3000 | Monitoring dashboards |
| Prometheus | http://localhost:9090 | Metrics collection |
| n8n | http://localhost:5678 | Workflow automation |
| Gitea | http://localhost:3001 | Self-hosted Git |

## Rollback
- Run `./scripts/rollback.sh` to rollback deployment
