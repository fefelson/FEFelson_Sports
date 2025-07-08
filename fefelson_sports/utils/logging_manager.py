import logging
import os

# Ensure logs directory exists
log_dir = os.path.expanduser("~/FEFelson/FEFelson_Sports/logs")  # Expand ~ to full path
os.makedirs(log_dir, exist_ok=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter for colorized log output in the console."""
    
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",   # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "CRITICAL": "\033[41m", # Red background
        "RESET": "\033[0m"    # Reset color
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        message = super().format(record)
        return f"{log_color}{message}{self.COLORS['RESET']}"

# Create a logger
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

# Console Handler (GUI)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = ColoredFormatter("%(levelname)s - %(message)s")  # Colorized output
console_handler.setFormatter(console_formatter)

# File Handler (Background)
file_path = os.path.join(log_dir, "app.log")
file_handler = logging.FileHandler(file_path)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def get_logger():
    return logger
