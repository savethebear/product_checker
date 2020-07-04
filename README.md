# Product Checker
Purpose of this project is to accept a list of products in certain websites and notifies the user when the product is no longer out of stock by sending them an email.

Additional products are added in the src/products.json

Running the src/checker.py will check the products listed in the JSON file once. To have it run continually a scheduler utility is used (ie. Crontab).

Current sites supported are "Superdrug" and "Boots"
