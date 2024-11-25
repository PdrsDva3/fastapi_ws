import uvicorn

import db.migrations
from handlers.app import app

if __name__ == "__main__":
    db.migrations.migration_up()
    uvicorn.run(app, host="0.0.0.0", port=8000)