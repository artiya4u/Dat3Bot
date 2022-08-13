# AutoRight - Auto swipe right for Tinder Chrome Extension

Chrome extension for Tinder automatic swipe right now working with `Dat3Bot` model via a REST API.

## Features

- Can use on your default browser with any login type.
- Can browse all profiles photos and choose the hot one.
- Reliable and fast to interact with Tinder web UI.
- Handles all annoyed popup or modal windows.

## Getting Start

- Run the API on port 8000 using command `python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000`
  or build a docker image as `docker build --tag dat3bot:latest .` and run it
  as `docker run -d -it -p 8000:8000 dat3bot:latest`. First request will take a while to load the model weights.
  Can try the API with curl:

```shell
curl --location --request POST 'http://127.0.0.1:8000/check' \
--header 'Content-Type: application/json' \
--data-raw '{
    "url": "https://pbs.twimg.com/media/FZ9sI_-aMAA8Srt?format=webp&name=medium"
}'
```

- Change the `BASE_API_URL` constant to suit your needs. it could run on cloud.
- Buy the 'Tinder Plus' package to allow unlimited swipe right.
- Go to the Google Chrome extension page or type: `chrome://extensions/` on the address bar.
- Enable 'Developer mode' in the top right corner.
- Click 'Load unpacked' and browse the `chrome_extension` folder.
- Open https://tinder.com/app/recs and login into your Tinder account.
- It will start swipe automatically based on the trained model.
- Remove or disable on extension page to stop using it.