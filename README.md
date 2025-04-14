# Pizza Restaurant

Pizza Restaurant is a Django-based web application for online food ordering, featuring a shopping cart, order placement, and real-time order tracking. Users can add items to their cart, select delivery and payment methods, confirm orders, and track their order status (Preparation, Delivery, Ready) via an always-accessible tracking page. The admin panel allows managing orders, updating statuses, and overseeing menu items.

## Features

- **User Authentication**: Secure login/registration for customers.
- **Shopping Cart**: Add, update, or remove items with real-time total calculation.
- **Order Placement**: Choose delivery (home delivery or pickup) and payment methods (Wave, Orange Money).
- **Order Tracking**: Accessible via "Suivi de Commande" button on the cart page, showing the latest order’s status or "No orders" message.
- **Admin Panel**: Manage orders (`Commande`), update `statut` (Preparation, Delivery, Ready), and handle menu items (`Plat`, `Categorie`).
- **Responsive Design**: Built with Bootstrap, FTCO templates, and Font Awesome for a modern, mobile-friendly UI.

## Tech Stack

- **Backend**: Django 5.2, Python 3.x
- **Frontend**: Bootstrap, FTCO templates, Font Awesome
- **Database**: SQLite (default; configurable for PostgreSQL/MySQL)
- **Environment**: python-dotenv for secure configuration

## Prerequisites

- Python 3.8+
- Git
- Virtualenv (recommended)
- A GitHub account

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/TrapHustle/pizza-restaurant.git
   cd pizza-restaurant
