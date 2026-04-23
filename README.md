# Cloudflare Tunnel Extension for Stable Diffusion WebUI

This extension provides an alternative to ngrok for creating public tunnels to your local Stable Diffusion WebUI instance using Cloudflare.

## Features

- **Automatic Binary Management:** Automatically downloads the correct `cloudflared` binary for your OS (Windows, Linux, macOS).
- **Quick Tunneling:** Automatically generates a `https://<random>.trycloudflare.com` URL on startup without requiring an account.
- **Persistent Tunnels:** Supports custom Cloudflare tunnel tokens for using your own domain/persistent tunnels.
- **UI Settings:** Toggle the tunnel on/off from the WebUI settings tab.

## Installation

Clone this repository into your `extensions` folder:

```bash
cd extensions
git clone https://github.com/KanzakiRui/sd-webui-cflr-tunneling
```

## Usage

### Quick Tunnel (No Account Required)
Simply launch the WebUI. If enabled in settings, the tunnel will start automatically.

### Using a Tunnel Token
If you have a persistent tunnel configured in your Cloudflare dashboard, you can use it by adding the `--cloudflared` argument to your startup command:

```bash
python webui.py --cloudflared YOUR_TOKEN_HERE
```

## Arguments

- `--cloudflared <TOKEN>`: Start a tunnel using the specified token. If no token is provided, a "quick tunnel" is used.
