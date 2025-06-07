# Docker Quick Commands

## App-Only Mode (Current Setup)
*Uses external Railway PostgreSQL database*

### Start Application
```bash
docker-compose -f docker-compose.app-only.yml up -d
```

### View Logs
```bash
docker-compose -f docker-compose.app-only.yml logs -f
```

### Stop Application
```bash
docker-compose -f docker-compose.app-only.yml down
```

### Check Status
```bash
docker-compose -f docker-compose.app-only.yml ps
curl http://localhost:8000/health
```

### Rebuild (After Code Changes)
```bash
docker-compose -f docker-compose.app-only.yml build
docker-compose -f docker-compose.app-only.yml up -d
```

### Open Shell in Container
```bash
docker-compose -f docker-compose.app-only.yml exec api bash
```

## Full Development Mode (Local Database)
*If you want to use local PostgreSQL + Redis*

### Start Full Stack
```bash
docker-compose up -d
```

### Stop Full Stack
```bash
docker-compose down
```

## Useful URLs
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
