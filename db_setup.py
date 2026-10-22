from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "food_delivery_da3"

def get_database():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def seed_database():
    db = get_database()
    
    # Drop all collections to clear previous orders and test users
    for col in ["customers", "restaurants", "orders", "delivery_riders"]:
        db[col].drop()

    # 1. NO hardcoded customers (Starts completely empty)
    # Users will be created dynamically via the Customer Registration/Order form

    # 2. Hardcoded 3 Restaurants, each with 3 items (Unique Cuisines)
    restaurants = [
        {
            "restaurant_id": 201,
            "name": "Spice Hub",
            "cuisine": "North Indian & Mughlai",
            "email": "spicehub@chennai.com",
            "phone_num": "04440010001",
            "address": {"street": "Anna Nagar 2nd Avenue", "city": "Chennai", "state": "Tamil Nadu", "pin": "600040"},
            "avg_rating": 4.6,
            "menu": [
                {"item_id": 301, "item_name": "Butter Chicken", "description": "Tender chicken cooked in rich buttery tomato gravy", "price": 280.0, "is_available": True},
                {"item_id": 302, "item_name": "Paneer Tikka Masala", "description": "Char-grilled cottage cheese in spiced makhani gravy", "price": 240.0, "is_available": True},
                {"item_id": 303, "item_name": "Garlic Butter Naan Basket", "description": "3 freshly baked tandoori naans brushed with roasted garlic butter", "price": 120.0, "is_available": True}
            ]
        },
        {
            "restaurant_id": 202,
            "name": "Chennai Biryani House",
            "cuisine": "Authentic Chettinad & Dum Biryani",
            "email": "contact@chennaibiryanihouse.com",
            "phone_num": "04440010002",
            "address": {"street": "Usman Road, T Nagar", "city": "Chennai", "state": "Tamil Nadu", "pin": "600017"},
            "avg_rating": 4.8,
            "menu": [
                {"item_id": 304, "item_name": "Seeraga Samba Chicken Biryani", "description": "Fragrant traditional short-grain chicken biryani with boiled egg", "price": 310.0, "is_available": True},
                {"item_id": 305, "item_name": "Special Mutton Dum Biryani", "description": "Slow-cooked tender goat meat with seasoned basmati and salna", "price": 380.0, "is_available": True},
                {"item_id": 306, "item_name": "Chicken 65", "description": "Crispy fried South-Indian spiced marinated chicken bites", "price": 190.0, "is_available": True}
            ]
        },
        {
            "restaurant_id": 203,
            "name": "Bella Napoli",
            "cuisine": "Italian Wood-Fired & Pasta",
            "email": "order@bellanapoli.in",
            "phone_num": "04440010003",
            "address": {"street": "Besant Avenue, Adyar", "city": "Chennai", "state": "Tamil Nadu", "pin": "600020"},
            "avg_rating": 4.7,
            "menu": [
                {"item_id": 307, "item_name": "Wood-Fired Margherita Pizza", "description": "San Marzano tomato sauce, fresh buffalo mozzarella, fresh basil", "price": 360.0, "is_available": True},
                {"item_id": 308, "item_name": "Truffle Mushroom Fettuccine", "description": "Handmade pasta in rich garlic cream sauce and black truffle oil", "price": 420.0, "is_available": True},
                {"item_id": 309, "item_name": "Classic Tiramisu", "description": "Savoiardi soaked in espresso with mascarpone cream & cocoa", "price": 220.0, "is_available": True}
            ]
        }
    ]
    db.restaurants.insert_many(restaurants)

    # 3. Exactly 3 Hardcoded Initial Riders
    riders = [
        {
            "rider_id": 401,
            "name": "Suresh Kumar",
            "email": "suresh.k@delivery.com",
            "license_num": "TN09-20220001234",
            "avg_rating": 4.8,
            "phone_numbers": ["9840112233"]
        },
        {
            "rider_id": 402,
            "name": "Karthik S",
            "email": "karthik.s@delivery.com",
            "license_num": "TN07-20210005678",
            "avg_rating": 4.9,
            "phone_numbers": ["9840223344"]
        },
        {
            "rider_id": 403,
            "name": "Manoj Raj",
            "email": "manoj.r@delivery.com",
            "license_num": "TN02-20230009012",
            "avg_rating": 4.7,
            "phone_numbers": ["9840334455"]
        }
    ]
    db.delivery_riders.insert_many(riders)

    print("Success: Database reset. 3 Restaurants (3 items each), 3 Riders, 0 Customers, and 0 Orders.")

if __name__ == "__main__":
    seed_database()