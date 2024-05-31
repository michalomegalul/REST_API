REST API - Products

This is a REST API built with Flask and SQLAlchemy. It includes endpoints for managing products and offers. The project uses Poetry for dependency management and is containerized with Docker.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Docker
- Docker Compose

### Installing

1. Clone the repository
    ```
    git clone [<repository_url>](https://github.com/michalomegalul/applifting-trainee)
    ```

2. Build the Docker images
    ```
    docker compose build
    ```

3. Run the application
    ```
    docker compose up
    ```

## API Endpoints

- `POST /api/products` - Create a new product
- `PUT /api/products/<uuid:product_id>` - Update a product
- `DELETE /api/products/<uuid:product_id>` - Delete a product
- `GET /api/products/<uuid:product_id>/offers` - Get offers for a product
- `GET /api/update_offers` - Update offers
- `GET /api/products` - Get all products

## API Access Point
  ```
  http://143.198.124.185:5000
  ```
