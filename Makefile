test:
	-coverage run --source=hotel_business_module -m unittest discover
	-coverage report --fail-under=50
