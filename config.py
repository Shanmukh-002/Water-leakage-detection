class Config:
    SECRET_KEY = "<provide your key>"
    INGEST_API_KEY = "<provide your key>"

    SQLALCHEMY_DATABASE_URI = "sqlite:////app/data/leak.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    NODES = [
        {"id": "node1", "name": "Borewell (0 km)", "km": 0},
        {"id": "node2", "name": "1 km Point", "km": 1},
        {"id": "node3", "name": "2 km Point", "km": 2},
        {"id": "node4", "name": "Field End (3 km)", "km": 3},
    ]

    LEAK_THRESHOLD_LPM = 50
    FRESH_SECONDS = 600
