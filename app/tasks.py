import atexit
from datetime import datetime, timedelta
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError
from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from .models import Offer, Product
import logging

access_token = None
token_expiration = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_access_token(app):
    global access_token, token_expiration
    with app.app_context():
        if access_token and token_expiration and datetime.now() < token_expiration:
            return access_token

        auth_url = f"{current_app.config['OFFERS_SERVICE_URL']}/auth"
        refresh_token = current_app.config["REFRESH_TOKEN"]

        logger.info(f"Authenticating with URL: {auth_url}")
        logger.info(f"Using refresh token: {refresh_token}")

        try:
            response = requests.post(auth_url, headers={"Bearer": refresh_token})
            response.raise_for_status()

            data = response.json()
            access_token = data["access_token"]
            token_expiration = datetime.now() + timedelta(minutes=5)

            logger.info(f"Obtained new access token: {access_token}")
            save_access_token(access_token)

            return access_token
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            logger.error(
                f"Response content: {response.content if 'response' in locals() else 'No response'}"
            )
            access_token = retrieve_stored_token()
            if access_token:
                return access_token
            raise
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            raise


def save_access_token(token):
    try:
        with open("access_token.txt", "w") as f:
            f.write(token)
    except Exception as e:
        logger.error(f"Error saving access token to file: {e}")


def retrieve_stored_token():
    try:
        with open("access_token.txt") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error reading access token from file: {e}")
        return None


def register_product_and_create_offer(app, product):
    with app.app_context():
        logger.info(f"Attempting to register product: {product.id}")
        # url = 'https://python.exercise.applifting.cz/api/v1/products/register'
        url = f"{current_app.config['OFFERS_SERVICE_URL']}/products/register"
        headers = {"Bearer": get_access_token(app)}

        payload = {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
        }
        logger.info(f"Payload: {payload}")

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Product registered successfully: {response.json()}")
            create_offer(app, product.id)
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 409:
                logger.info(
                    f"Product already exists: {product.id}. Proceeding to create offers."
                )
                create_offer(app, product.id)
            else:
                logger.error(f"HTTP error occurred: {http_err}")
                logger.error(f"Response content: {response.content}")
                raise
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            raise


def create_offer(app, product_id):
    with app.app_context():
        offer_url = (
            f"{current_app.config['OFFERS_SERVICE_URL']}/products/{product_id}/offers"
        )
        headers = {"Bearer": get_access_token(app)}
        logger.info(
            f"Fetching offers for product {product_id} with URL: {offer_url} and headers: {headers}"
        )

        try:
            offer_response = requests.get(offer_url, headers=headers)
            offer_response.raise_for_status()
            offers_data = offer_response.json()
            logger.info(f"Offers fetched successfully for product {product_id}")
            save_offer_to_db(app, product_id, offers_data)
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            logger.error(f"Response content: {offer_response.content}")
            raise
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            raise


def save_offer_to_db(app, product_id, offers_data):
    with app.app_context():
        engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()

        try:
            for offer_data in offers_data:
                existing_offer = (
                    session.query(Offer).filter_by(id=offer_data["id"]).first()
                )
                if existing_offer:
                    if offer_data["items_in_stock"] == 0:
                        logger.info(
                            f"Deleting offer with zero stock: {offer_data['id']}"
                        )
                        session.delete(existing_offer)
                    else:
                        logger.info(f"Updating existing offer: {offer_data['id']}")
                        existing_offer.price = offer_data["price"]
                        existing_offer.items_in_stock = offer_data["items_in_stock"]
                else:
                    if offer_data["items_in_stock"] != 0:
                        logger.info(f"Adding new offer: {offer_data['id']}")
                        offer = Offer(
                            id=offer_data["id"],
                            price=offer_data["price"],
                            items_in_stock=offer_data["items_in_stock"],
                            product_id=product_id,
                        )
                        session.add(offer)
            session.commit()
            logger.info(f"Offers saved to database for product {product_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving offers to the database: {e}")
            raise e
        finally:
            session.close()


def fetch_offers(app):
    with app.app_context():
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()

        try:
            products = session.query(Product).all()
            for product in products:
                create_offer(app, product.id)
        except Exception as e:
            logger.error(f"Error fetching offers: {e}")
            raise e
        finally:
            session.close()


scheduler = BackgroundScheduler()


def start_scheduler(app):
    with app.app_context():
        scheduler.add_job(
            func=fetch_offers,
            args=[app],
            trigger="interval",
            minutes=30,
            id="update_offers_job",
        )
    scheduler.start()
    logger.info("Scheduler started.")


def stop_scheduler():
    """Stops the scheduler."""
    try:
        scheduler.shutdown()
    except SchedulerNotRunningError:
        pass


atexit.register(stop_scheduler)
