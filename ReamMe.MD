# RideBuddy

RideBuddy is a Django-based web application designed to help users track their carbon footprint from various rides. It calculates CO2 emissions and savings based on the type of vehicle, distance traveled, and other factors.

## Features

- User authentication (signup, login, logout)
- Profile management
- Ride recording and CO2 savings calculation
- Detailed eco impact statistics

## Requirements

- Python 3.x
- Django
- asgiref
- sqlparse

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/ridebuddy.git
    cd ridebuddy
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Apply migrations:
    ```sh
    python manage.py migrate
    ```

5. Create a superuser:
    ```sh
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```sh
    python manage.py runserver
    ```

7. Open your browser and navigate to `http://127.0.0.1:8000/` to access the application.

## Usage

- **Sign Up**: Create a new account.
- **Login**: Access your account.
- **Profile**: View your profile and eco impact statistics.
- **Record Ride**: Log a new ride and calculate CO2 savings.
- **View Results**: See the detailed results of your ride and overall savings.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries, please contact [ramachandraudupa2004@gmail.com].
