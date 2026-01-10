"""Quick test script to verify Ollama connectivity and setup."""
import httpx
import asyncio
import sys


async def test_ollama():
    """Test Ollama connection."""
    print("Testing Ollama connectivity...")
    
    ollama_urls = [
        "http://localhost:11434",
        "http://host.docker.internal:11434",
    ]
    
    for url in ollama_urls:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    print(f"✓ Ollama accessible at: {url}")
                    print(f"  Available models: {[m['name'] for m in models]}")
                    return True
        except Exception as e:
            print(f"✗ Failed to connect to {url}: {e}")
    
    print("\n⚠ Ollama is not running or not accessible.")
    print("  Please start Ollama:")
    print("    ollama serve")
    print("  Or if using Docker:")
    print("    docker run -d -p 11434:11434 ollama/ollama")
    return False


async def main():
    """Main test function."""
    print("=== Autonomous Agent Setup Test ===\n")
    
    ollama_ok = await test_ollama()
    
    print("\n=== Test Results ===")
    if ollama_ok:
        print("✓ All tests passed!")
        print("\nNext steps:")
        print("  1. Pull a lightweight model: ollama pull llama3.2:3b")
        print("  2. Build Docker images: docker-compose build")
        print("  3. Start services: docker-compose up -d")
        print("  4. Check health: curl http://localhost:8000/health")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
