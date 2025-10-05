# Docker CI Build System

Minimal Docker setup for CI builds of macOS packages using Linux runners.

## Directory Structure

```
linux-native/
├── README.md                 # This documentation
├── Dockerfile                # Single Docker image for builds
├── docker-compose.yml        # Development/testing stack
└── build.sh                  # Build orchestration script
```

## Purpose

- **Docker Builds**: Use Docker for consistent build environments
- **Fast Builds**: Single optimized Docker image with all dependencies  
- **Local Development**: Same build process locally and in containers
- **Multiple Formats**: Build DMG and native packages

## Build Targets

1. **macOS DMG**: Native macOS application bundle
2. **macOS Native**: PyWebView-based native macOS app (non-Electron)

## Integration

```bash
# Local build
./linux-native/build.sh --build-dmg
./linux-native/build.sh --build-native

# Docker build
docker-compose -f linux-native/docker-compose.yml up apex-build

# Build all packages
./linux-native/build.sh --all
```
