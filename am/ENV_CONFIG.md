# Environment Variables Configuration

## Quick Setup

Docker-compose now uses environment variables for flexible configuration.

### Key Variables

**`AM_REPO_PATH`** - Base path to AM-Portfolio directory

Current: `A:\InfraCode\AM-Portfolio`

### How to Use

#### Option 1: Auto-load from .env.local (Recommended)
```bash
cd am
docker-compose up -d --build
```

Docker automatically loads `.env.local` and uses `${AM_REPO_PATH}` in docker-compose.yml

#### Option 2: Set via environment variable
```bash
# Windows PowerShell
$env:AM_REPO_PATH = "A:\InfraCode\AM-Portfolio"
docker-compose up -d --build

# Windows CMD
set AM_REPO_PATH=A:\InfraCode\AM-Portfolio
docker-compose up -d --build

# Linux/Mac
export AM_REPO_PATH=/path/to/AM-Portfolio
docker-compose up -d --build
```

#### Option 3: Override specific service
```bash
docker-compose build --build-arg AM_REPO_PATH=A:\InfraCode\AM-Portfolio am-document-processor
```

### Affected Services

Services using dynamic path:
- `am-document-processor` → `${AM_REPO_PATH}/am-document-processor`
- `am-portfolio` → `${AM_REPO_PATH}/am-portfolio`
- `am-trade-api` → `${AM_REPO_PATH}/am-trade-management`
- `am-market-data` → `${AM_REPO_PATH}/am-market-data`

### Switching Directories

To change the repo path:

```bash
# 1. Edit .env.local
nano am/.env.local  # or use your editor

# 2. Change AM_REPO_PATH to new location
AM_REPO_PATH=/path/to/new/location

# 3. Rebuild services
docker-compose up -d --build
```

### Verify Configuration

```bash
# Check loaded environment variables
docker-compose config | grep -A 5 "am-document-processor"

# Or see the full config
docker-compose config
```

### Troubleshooting

**Error: "build context does not exist"**
- Check `AM_REPO_PATH` is correct and exists
- Verify files are at `${AM_REPO_PATH}/am-document-processor/Dockerfile`, etc.

**Variable not being replaced**
- Ensure `.env.local` is in the same directory as `docker-compose.yml`
- Try explicitly setting: `export AM_REPO_PATH=...`

