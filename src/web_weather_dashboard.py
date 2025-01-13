import os
import json
import boto3
import requests
from datetime import datetime
from dotenv import load_dotenv
from jinja2 import Template

# Load environment variables
load_dotenv()

class WeatherDashboard:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        self.bucket_name = os.getenv('NEW_AWS_BUCKET_NAME')
        self.s3_client = boto3.client('s3')
        
        # HTML template for the weather dashboard
        self.html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-center mb-8 text-gray-800">Weather Dashboard</h1>
        <p class="text-center text-gray-600 mb-8">Last updated: {{ timestamp }}</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for city in cities %}
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-semibold mb-4 text-gray-800">{{ city.name }}</h2>
                <div class="space-y-3">
                    <div class="flex items-center">
                        <span class="text-4xl font-bold text-blue-600">{{ city.temp }}°F</span>
                        <img src="http://openweathermap.org/img/wn/{{ city.icon }}@2x.png" 
                             alt="{{ city.description }}"
                             class="ml-4 w-16 h-16">
                    </div>
                    <p class="text-gray-600">Feels like: {{ city.feels_like }}°F</p>
                    <p class="text-gray-600">Humidity: {{ city.humidity }}%</p>
                    <p class="text-gray-600 capitalize">{{ city.description }}</p>
                    <div class="mt-4 pt-4 border-t">
                        <p class="text-gray-600">Wind: {{ city.wind_speed }} mph</p>
                        <p class="text-gray-600">Pressure: {{ city.pressure }} hPa</p>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

    def create_bucket_if_not_exists(self):
        """Create S3 bucket if it doesn't exist and configure it for static website hosting"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} exists")
        except:
            print(f"Creating bucket {self.bucket_name}")
            try:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
                )
                
                # Configure bucket for static website hosting
                self.s3_client.put_bucket_website(
                    Bucket=self.bucket_name,
                    WebsiteConfiguration={
                        'IndexDocument': {'Suffix': 'index.html'},
                        'ErrorDocument': {'Key': 'error.html'}
                    }
                )
                
                # Make bucket public
                bucket_policy = {
                    'Version': '2012-10-17',
                    'Statement': [{
                        'Sid': 'PublicReadGetObject',
                        'Effect': 'Allow',
                        'Principal': '*',
                        'Action': ['s3:GetObject'],
                        'Resource': f'arn:aws:s3:::{self.bucket_name}/*'
                    }]
                }
                
                # Convert the policy to JSON and apply it
                self.s3_client.put_bucket_policy(
                    Bucket=self.bucket_name,
                    Policy=json.dumps(bucket_policy)
                )
                
                print(f"Successfully created and configured bucket {self.bucket_name}")
            except Exception as e:
                print(f"Error creating/configuring bucket: {e}")

    def fetch_weather(self, city):
        """Fetch weather data from OpenWeather API"""
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

    def generate_html(self, weather_data_list):
        """Generate HTML content from weather data"""
        cities = []
        for data in weather_data_list:
            if data:
                cities.append({
                    'name': data['name'],
                    'temp': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'wind_speed': round(data['wind']['speed']),
                    'pressure': data['main']['pressure']
                })
        
        template = Template(self.html_template)
        return template.render(
            cities=cities,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def upload_to_s3(self, html_content):
        """Upload HTML content to S3 bucket"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key='index.html',
                Body=html_content,
                ContentType='text/html',
            )
            print("Successfully uploaded weather dashboard to S3")
            
            # Get the website URL
            region = self.s3_client.meta.region_name
            website_url = f"http://{self.bucket_name}.s3-website.{region}.amazonaws.com"
            print(f"Website is available at: {website_url}")
            
            return True
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return False

def main():
    dashboard = WeatherDashboard()
    
    # Create and configure bucket
    dashboard.create_bucket_if_not_exists()
    
    # List of cities to fetch weather for
    cities = ["Philadelphia", "Seattle", "New York", "Miami", "San Francisco", "Chicago"]
    
    # Fetch weather data for all cities
    weather_data_list = []
    for city in cities:
        print(f"Fetching weather for {city}...")
        weather_data = dashboard.fetch_weather(city)
        if weather_data:
            weather_data_list.append(weather_data)
            print(f"Successfully fetched weather data for {city}")
        else:
            print(f"Failed to fetch weather data for {city}")
    
    if weather_data_list:
        # Generate HTML content
        html_content = dashboard.generate_html(weather_data_list)
        
        # Upload to S3
        dashboard.upload_to_s3(html_content)
    else:
        print("No weather data was fetched. Please check your API key and internet connection.")

if __name__ == "__main__":
    main()