import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("LORA_PATH"))
print(type(os.getenv("LORA_PATH")))