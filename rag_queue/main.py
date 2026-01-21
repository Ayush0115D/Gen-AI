from .server import app
from dotenv import load_dotenv
import uvicorn
load_dotenv()
def main():
    uvicorn.run(app,port=8000,host="0.0.0.0")
    main()
    
if __name__ == "__main__":
    main()