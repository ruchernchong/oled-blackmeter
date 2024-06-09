# True Black Calculator

## Installation

```bash
# Install the necessary packages
pip install -r requirements.txt
```

## Usage

### Run in local development
```bash
# Setup ngrok
ngrok http 5000 # Flask uses port 5000 by default. You can change this accordingly to your preference

# Copy the .env.example file and replace the values accordingly
cp .env.example .env

# Update your NGROK_STATIC_DOMAIN in .env with the ngrok "Forwarding" URL
NGROK_STATIC_DOMAIN=2655-158-140-141-125.ngrok-free.app # Example

# Update your Telegram Bot Token in your .env
TELEGRAM_BOT_TOKEN=

# Run the server.py
python server.py
```

Once the above is completed, head over to your Telegram Bot that was setup with Telegram BotFather and you are done.

## True Black Calculator Telegram Bot

![True Black Calculator Telegram Bot](screenshots/iFrameScreenshot1.PNG)
![True Black Calculator Telegram Bot](screenshots/iFrameScreenshot2.PNG)
