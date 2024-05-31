import os
import requests
from faker import Faker
from dotenv import load_dotenv

fake = Faker()
load_dotenv()
# API_BASE_URL = "http://143.198.124.185:5000/api"
API_BASE_URL = os.getenv("API_BASE_URL")

num_words = 10

for _ in range(num_words):
    random_word = fake.word()
    random_word2 = fake.text(max_nb_chars=200)

    if API_BASE_URL:
        create = requests.post(
            API_BASE_URL + "/products",
            json={"name": random_word, "description": random_word2},
        )
        print(random_word, random_word2, create.status_code)
    else:
        raise ValueError("API_BASE_URL is not defined in the environment variables")
