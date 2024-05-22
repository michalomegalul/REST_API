import requests
import atexit
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError
from flask import current_app
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from .models import Offer, Product

# Globals to store the access token and its expiration
access_token = None
token_expiration = None


def get_access_token():
    """Fetches a new access token using the refresh token if the current one is expired or not set."""
    global access_token, token_expiration

    if access_token and token_expiration and datetime.now() < token_expiration:
        return access_token

    response = requests.post(
        current_app.config["AUTH_ENDPOINT"],
        json={"refresh_token": current_app.config["REFRESH_TOKEN"]},
    )
    response.raise_for_status()

    data = response.json()
    access_token = data["access_token"]
    expires_in = data["expires_in"]
    token_expiration = datetime.now() + timedelta(seconds=expires_in)

    return access_token


def fetch_offers():
    """Fetches offers for all products and updates the database."""
    engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    try:
        products = session.query(Product).all()
        for product in products:
            url = f"{current_app.config['OFFERS_SERVICE_URL']}/products/{product.id}/offers"
            headers = {"Authorization": f"Bearer {get_access_token()}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            offers_data = response.json()
            session.query(Offer).filter_by(product_id=product.id).delete()
            for offer_data in offers_data:
                offer = Offer(
                    id=offer_data["id"],
                    price=offer_data["price"],
                    items_in_stock=offer_data["items_in_stock"],
                    product_id=product.id,
                )
                session.add(offer)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Initialize the scheduler
scheduler = BackgroundScheduler()


def start_scheduler():
    """Starts the scheduler to fetch offers periodically."""
    scheduler.add_job(
        fetch_offers, "interval", minutes=30
    )  # Adjust the interval as needed
    scheduler.start()


def stop_scheduler():
    """Stops the scheduler."""
    try:
        scheduler.shutdown()
    except SchedulerNotRunningError:
        pass


# Ensure the scheduler is stopped when the application exits
atexit.register(stop_scheduler)
