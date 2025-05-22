# ElectroEgy API Documentation

## Table of Contents
- [Authentication](#authentication)
- [Accounts](#accounts)
- [Products](#products)
- [Cart](#cart)
- [Orders](#orders)
- [Wishlist](#wishlist)

## Authentication
The API uses token-based authentication. Protected endpoints require a valid authentication token in the request header.

Some endpoints also require 2FA verification for additional security.

### Protected Routes
The following paths require 2FA verification:
- `/api/orders/*`
- `/api/cart/*`
- `/api/wishlist/*`

## Accounts
Base URL: `/api/accounts/`

### Endpoints

#### Register
- **URL**: `/register/`
- **Method**: POST
- **Description**: Register a new user account
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "confirm_password": "string"
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "id": "integer",
    "username": "string",
    "email": "string",
    "token": "string"
  }
  ```

#### Login
- **URL**: `/login/`
- **Method**: POST
- **Description**: Authenticate user and get access token
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: 200 OK
  ```json
  {
    "token": "string",
    "user": {
      "id": "integer",
      "username": "string",
      "email": "string"
    }
  }
  ```

## Products
Base URL: `/api/products/`

### Endpoints

#### List Products
- **URL**: `/`
- **Method**: GET
- **Description**: Get list of all products
- **Response**: 200 OK
  ```json
  {
    "data": [
      {
        "id": "integer",
        "name": "string",
        "image": "string",
        "description": "string",
        "price": "decimal",
        "brand": "string",
        "category": "string",
        "rating": "decimal",
        "stock": "integer",
        "created_at": "datetime",
        "publisher": "string",
        "reviews": []
      }
    ]
  }
  ```

#### Product Detail
- **URL**: `/product/<pk>/`
- **Method**: GET
- **Description**: Get detailed information about a specific product
- **Response**: 200 OK
  ```json
  {
    "data": {
      "id": "integer",
      "name": "string",
      "image": "string",
      "description": "string",
      "price": "decimal",
      "brand": "string",
      "category": "string",
      "rating": "decimal",
      "stock": "integer",
      "created_at": "datetime",
      "publisher": "string",
      "reviews": [
        {
          "user": "string",
          "rating": "integer",
          "comment": "string",
          "created_at": "datetime"
        }
      ]
    }
  }
  ```

#### Create Product Review
- **URL**: `/review/<pk>/`
- **Method**: POST
- **Auth Required**: Yes
- **Description**: Create a review for a product
- **Request Body**:
  ```json
  {
    "rating": "integer(1-5)",
    "comment": "string"
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "message": "Review added successfully"
  }
  ```

## Cart
Base URL: `/api/cart/`

### Endpoints

#### View Cart
- **URL**: `/show-cart/`
- **Method**: GET
- **Auth Required**: Yes
- **Description**: View current cart contents
- **Response**: 200 OK
  ```json
  {
    "id": "integer",
    "items": [
      {
        "product": {
          "id": "integer",
          "name": "string",
          "image": "string",
          "price": "decimal",
          "stock": "integer"
        },
        "quantity": "integer",
        "total_price": "decimal"
      }
    ],
    "total_amount": "decimal"
  }
  ```

#### Add to Cart
- **URL**: `/cart/items/`
- **Method**: POST
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "product_id": "integer",
    "quantity": "integer"
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "message": "Item added to cart",
    "cart": {...} // Updated cart object
  }
  ```

## Orders
Base URL: `/api/orders/`

### Endpoints

#### Create Order
- **URL**: `/orders/create/`
- **Method**: POST
- **Auth Required**: Yes
- **Description**: Create a new order from cart items
- **Request Body**:
  ```json
  {
    "payment_method": "string",
    "shipping_address": "string",
    "city": "string",
    "country": "string",
    "zip_code": "string",
    "phone_no": "string"
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "id": "integer",
    "items": [
      {
        "product": {...},
        "quantity": "integer",
        "price": "decimal"
      }
    ],
    "total_amount": "decimal",
    "status": "string",
    "created_at": "datetime"
  }
  ```

## Wishlist
Base URL: `/api/wishlist/`

### Endpoints

#### View Wishlist
- **URL**: `/wishlist/`
- **Method**: GET
- **Auth Required**: Yes
- **Response**: 200 OK
  ```json
  {
    "wishlist": [
      {
        "id": "integer",
        "name": "string",
        "price": "decimal",
        "category": "string"
      }
    ]
  }
  ```

#### Add to Wishlist
- **URL**: `/wishlist/`
- **Method**: POST
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "product_id": "integer"
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "message": "Product added to wishlist."
  }
  ```

#### Remove from Wishlist
- **URL**: `/wishlist/`
- **Method**: DELETE
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "product_id": "integer"
  }
  ```
- **Response**: 200 OK
  ```json
  {
    "message": "Product removed from wishlist."
  }
  ```

## Error Handling
The API returns standard HTTP status codes and JSON responses for errors:
- 404: Resource not found
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 500: Internal server error

Error responses include a message field describing the error:
```json
{
  "error": "Error message description"
}
```