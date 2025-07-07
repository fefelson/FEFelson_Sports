.PHONY: setup clean

setup:
	@echo "🔧 Creating project directory structure..."
	mkdir -p data/raw
	mkdir -p data/processed
	mkdir -p data/models
	mkdir -p logs
	mkdir -p bin
	mkdir -p config
	mkdir -p templates

	@echo "📄 Checking for default config..."
	test -f config/default_config.toml || cp templates/default_config.toml config/

	@echo "✅ Project structure initialized. Run './setup.sh' to finish setup."

clean:
	@echo "🧹 Cleaning up generated directories and files..."
	rm -rf data logs bin venv __pycache__
