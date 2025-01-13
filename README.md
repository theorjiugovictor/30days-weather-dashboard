# Weather Dashboard Project

A DevOps solution for BTL, a small business that organizes events and requires real-time weather information for operational decision-making. This project creates an automated system that fetches weather data and displays it on a public dashboard using AWS S3 static website hosting.

## Problem Statement

BTL needs a real-time weather dashboard integrated into their event booking page to help customers make informed decisions. As a small business without technical expertise, they require a low-maintenance, cost-effective solution that:
- Fetches weather data from a reliable source
- Processes it into a visually appealing format
- Hosts it on a scalable platform
- Provides easy public access

## Solution Architecture

The project implements two main components:
1. JSON data storage pipeline for analytics
2. Dynamic HTML dashboard for public display

### Tech Stack

- **Data Source**: OpenWeatherMap API
- **Programming Language**: Python
- **Cloud Platform**: AWS S3
- **Development Environment**: 
  - Vagrant (VM)
  - VS Code
- **Key Libraries**:
  - Requests: API integration
  - Boto3: AWS S3 interaction
  - Jinja2: HTML templating
  - python-dotenv: Environment management

## Prerequisites

- Vagrant and VirtualBox (Optional)
- Visual Studio Code
- AWS Account
- Python 3
- AWS CLI

## Project Setup

### 1. Virtual Machine Setup (Optional)

```bash
# Initialize Vagrant
vagrant init hashicorp/bionic64
vagrant up
```

### 2. Project Structure

```bash
mkdir -p weather_dashboard/{src,data,tests,templates}
cd weather_dashboard
```

### 3. Dependencies Installation

```bash
# Update system and install Python
sudo apt update && sudo apt install -y python3-pip python3-venv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. AWS CLI Configuration

```bash
# Install AWS CLI
sudo apt install -y awscli

# Configure AWS credentials
aws configure
```

### 5. Environment Setup

Create a `.env` file with the following parameters:
```
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
JSON_BUCKET_NAME=your_s3_bucket_for_json
HTML_BUCKET_NAME=your_s3_bucket_for_html
```

Add `.env` to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

## Running the Application

### JSON Weather Data Pipeline

```bash
python3 src/json_weather_dashboard.py
```

### HTML Weather Dashboard

```bash
python3 src/web_weather_dashboard.py
```

## Deployment

1. Configure S3 Bucket for Static Website Hosting:
   - Navigate to your S3 bucket in AWS Console
   - Enable Static website hosting under Properties
   - Uncheck "Block all public access"
   - Add bucket policy for public read access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

2. Access the dashboard at: `http://your_html_bucket.s3-website-us-east-1.amazonaws.com`

## Challenges and Solutions

1. **S3 Bucket Creation Error**: Fixed by implementing proper bucket name validation
2. **API Authorization**: Resolved unauthorized access issues by validating API key presence
3. **Missing Dependencies**: Addressed by properly managing virtual environment and requirements
4. **PATH Issues**: Fixed pip-related PATH problems by updating environment variables

## Live Demo

Access the live weather dashboard: [http://web-jarvis-weather.s3-website.us-east-2.amazonaws.com/](http://web-jarvis-weather.s3-website.us-east-2.amazonaws.com/)

## Contributing

Feel free to fork this repository and submit pull requests with improvements.

## License

This project is open source and available under the [MIT License](LICENSE).