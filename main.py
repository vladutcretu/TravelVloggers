from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def main():
    return {"Test dependencies": "FastAPI"}

if __name__ == "__main__":
    main()
