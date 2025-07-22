import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
