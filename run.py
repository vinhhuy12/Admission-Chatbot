"""
Production-ready server runner with multi-worker support
Run this file from project root to start the FastAPI server

Usage:
    python run.py                    # Auto-detect mode from .env
    python run.py --mode dev         # Development mode with auto-reload
    python run.py --mode prod        # Production mode with multi-workers
    python run.py --mode single      # Single worker mode
    python run.py --workers 4        # Custom worker count
"""

import os
import sys
import multiprocessing
from pathlib import Path

# Add backend directory to Python path
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

import uvicorn
from app.config import settings


def get_optimal_workers() -> int:
    """
    Calculate optimal number of workers based on CPU cores
    Formula: (2 x CPU cores) + 1
    
    Returns:
        Number of workers
    """
    cpu_count = multiprocessing.cpu_count()
    optimal_workers = (2 * cpu_count) + 1
    
    # Limit to reasonable maximum
    max_workers = 8
    return min(optimal_workers, max_workers)


def run_development():
    """
    Run server in development mode with auto-reload
    Single worker for easier debugging
    """
    print("="*80)
    print("🚀 STARTING DEVELOPMENT SERVER")
    print("="*80)
    print(f"📝 Mode: Development")
    print(f"🔄 Auto-reload: Enabled")
    print(f"👷 Workers: 1 (single worker for debugging)")
    print(f"🌐 Host: {settings.BACKEND_HOST}")
    print(f"🔌 Port: {settings.BACKEND_PORT}")
    print(f"📚 API Docs: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/docs")
    print(f"📖 ReDoc: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/redoc")
    print()
    print("💡 Tips:")
    print("  - Code changes will auto-reload the server")
    print("  - Use Ctrl+C to stop the server")
    print("="*80)
    print()
    
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
        reload_dirs=[str(backend_dir / "app")],
        log_level="info",
        access_log=True
    )


def run_production(workers: int = None):
    """
    Run server in production mode with multiple workers
    Optimized for performance and concurrent requests
    
    Args:
        workers: Number of workers (None = auto-calculate)
    """
    workers = workers or get_optimal_workers()
    
    print("="*80)
    print("🚀 STARTING PRODUCTION SERVER")
    print("="*80)
    print(f"📝 Mode: Production")
    print(f"🔄 Auto-reload: Disabled")
    print(f"👷 Workers: {workers} (multi-process)")
    print(f"💻 CPU Cores: {multiprocessing.cpu_count()}")
    print(f"🌐 Host: {settings.BACKEND_HOST}")
    print(f"🔌 Port: {settings.BACKEND_PORT}")
    print(f"📚 API Docs: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/docs")
    print(f"📖 ReDoc: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/redoc")
    print()
    print("⚡ Features:")
    print("  ✅ Multi-worker support for concurrent requests")
    print("  ✅ Models loaded once per worker (singleton pattern)")
    print("  ✅ Thread-safe database connections")
    print("  ✅ Automatic request queuing and load balancing")
    print("  ✅ Worker auto-restart after 10,000 requests")
    print()
    print("💡 Tips:")
    print("  - Each worker loads models independently")
    print("  - First request per worker may be slower (model loading)")
    print("  - Subsequent requests are fast (models cached)")
    print("  - Use Ctrl+C to stop the server")
    print("="*80)
    print()
    
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        workers=workers,
        log_level="info",
        access_log=True,
        # Production optimizations
        limit_concurrency=1000,  # Max concurrent connections
        limit_max_requests=10000,  # Restart worker after N requests (prevent memory leaks)
        timeout_keep_alive=5  # Keep-alive timeout
    )


def run_single_worker():
    """
    Run server with single worker (for testing or low-resource environments)
    """
    print("="*80)
    print("🚀 STARTING SINGLE-WORKER SERVER")
    print("="*80)
    print(f"📝 Mode: Single Worker")
    print(f"🔄 Auto-reload: Disabled")
    print(f"👷 Workers: 1")
    print(f"🌐 Host: {settings.BACKEND_HOST}")
    print(f"🔌 Port: {settings.BACKEND_PORT}")
    print(f"📚 API Docs: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/docs")
    print(f"📖 ReDoc: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/redoc")
    print()
    print("💡 Tips:")
    print("  - Models loaded once at startup")
    print("  - All requests handled by single process")
    print("  - Good for testing and low-resource environments")
    print("  - Use Ctrl+C to stop the server")
    print("="*80)
    print()
    
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        workers=1,
        log_level="info",
        access_log=True
    )


def main():
    """
    Main entry point - choose mode based on environment or command line argument
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run FastAPI server with optimal configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Auto-detect mode from .env
  python run.py --mode dev         # Development mode with auto-reload
  python run.py --mode prod        # Production mode with multi-workers
  python run.py --mode single      # Single worker mode
  python run.py --workers 4        # Production with 4 workers
  python run.py --host 0.0.0.0 --port 8080  # Custom host and port
        """
    )
    parser.add_argument(
        "--mode",
        choices=["dev", "prod", "single"],
        default=None,
        help="Server mode: dev (development with reload), prod (production with multi-workers), single (single worker)"
    )
    parser.add_argument(
        "--host",
        default=None,
        help=f"Host to bind (default: {settings.BACKEND_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=f"Port to bind (default: {settings.BACKEND_PORT})"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of workers (only for prod mode, default: auto-calculated)"
    )
    
    args = parser.parse_args()
    
    # Override settings if provided
    if args.host:
        settings.BACKEND_HOST = args.host
    if args.port:
        settings.BACKEND_PORT = args.port
    
    # Determine mode
    mode = args.mode or settings.ENVIRONMENT
    
    # Print banner
    print()
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "ADMISSIONS COUNSELING CHATBOT API" + " "*25 + "║")
    print("║" + " "*30 + "FastAPI Server" + " "*34 + "║")
    print("╚" + "═"*78 + "╝")
    print()
    
    # Run server based on mode
    if mode == "dev" or mode == "development":
        run_development()
    elif mode == "single":
        run_single_worker()
    else:
        # Production mode
        run_production(workers=args.workers)


if __name__ == "__main__":
    # Change to backend directory for imports
    os.chdir(backend_dir)
    main()

