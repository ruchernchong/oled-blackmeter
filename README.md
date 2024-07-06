# OLED BlackMeter

Link to the Telegram Bot: https://t.me/OLEDBlackMeterBot

## Installation

```bash
# Install the necessary packages
pip install -r requirements.txt
```

## Run in Local Development

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

Once the above is completed, head over to your Telegram Bot that was setup with [@BotFather](https://t.me/BotFather) and
you are done.

## Deploy to Google Cloud Functions

By default, this Telegram bot is already properly setup and you may follow the commands below to deploy to Google Cloud
Functions.

```bash
# Setup a Pulumi Stack (You will need a Pulumi account first)
pulumi stack init

# Update the stack
pulumi up
```

However, if you have intention to use other methods of deployment, you are feel free to do so.

*Do note that the current setup is running in webhook mode rather than polling mode.

## Screenshots

![OLED BlackMeter Telegram Bot](screenshots/iFrameScreenshot1.PNG)
![OLED BlackMeter Telegram Bot](screenshots/iFrameScreenshot2.PNG)
