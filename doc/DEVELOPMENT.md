# DEVELOPMENT.md

This document describes how to set up a **development environment** for this Python project using a Raspberry Pi Zero 2W.
If you are looking for end-user instructions, please see **README.md**.

---

## 1. Overview and Requirements

### 1.1. Assumption
- You are using an **Ubuntu** PC for development.

### 1.2. Hardware Required
- **Raspberry Pi Zero 2W** (with header pins)
  [Example on Amazon](https://www.amazon.com/Pi-Zero-WH-Quad-Core-Bluetooth/dp/B0DKKXS4RV/)
- **Micro SD card (UHS-I, Class 10)**
  [Example on Amazon](https://www.amazon.com/dp/B08J4HJ98L)
- **Micro USB cable** (one end micro USB for Pi Zero 2W, the other end matching your PC)
  [Example on Amazon](https://www.amazon.com/dp/B0BFWSP4PP)
- **Waveshare 7.5-inch E-Ink Display**
  [Example on Amazon](https://www.amazon.com/waveshare-7-5inch-HAT-Raspberry-Consumption/dp/B075R4QY3L/)
- **Micro SD card reader** (optional, if your PC has no built-in reader)
  [Example on Amazon](https://www.amazon.com/dp/B07NW8RPYN)

---

## 2. Install Raspberry Pi OS on Micro SD Card

1. **Install Raspberry Pi Imager on Ubuntu**:
```
$ sudo apt update
$ sudo apt install snapd
$ sudo snap install rpi-imager
```


2. **Run Raspberry Pi Imager**:
- Select **Raspberry Pi OS (32-bit)** (avoid the 64-bit version).
- Click the gear icon (**Advanced settings**) and set:
  - **Hostname**: `raspberrypi.local`
  - **Enable SSH**: Use password authentication
  - **Username / Password**: Choose your own (note it down!)
  - **Configure Wireless LAN**:
    - SSID: `<Your Wi-Fi SSID>`
    - Password: `<Your Wi-Fi Password>`
    - Wireless LAN country: `GB` (or your country code)
  - **Set locale**:
    - Timezone: `America/Los_Angeles` (or your timezone)
    - Keyboard layout: `us`
  - Other options (if available):
    - Uncheck "Play sound when finished"
    - Check "Eject media when finished"
    - Check "Enable telemetry" (optional)

3. **Flash the micro SD card** using Raspberry Pi Imager.

4. **Insert the micro SD card** into the Raspberry Pi Zero 2W.

---

## 3. Initial Raspberry Pi Zero 2W Setup

1. **Connect Pi to your computer** with a micro USB cable (the Pi powers on immediately).

2. **SSH into the Pi** (your PC and Pi must be on the same network):
```
$ ssh <your_chosen_username>@raspberrypi.local
```
- When prompted, enter the password you set in the Raspberry Pi Imager.

---

## 4. Install System Dependencies on Raspberry Pi

Once logged in via SSH:
```
$ sudo apt update $ sudo apt install -y\
  git curl wget make build-essential libssl-dev zlib1g-dev\
  libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev\
  libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev\
  python3-dev vim libopenjp2-7 libtiff5-dev libjpeg-dev libfreetype6-dev\
  sqlite3
```

### 4.1. Enable SPI (required for Waveshare e-ink display)

You can do this in one of the following ways:

1. **Through `raspi-config` (interactive)**:
```
$ sudo raspi-config
```
- Go to `Interface Options` → `SPI` → enable.

2. **Edit `/boot/config.txt`**:
```
$ sudo nano /boot/config.txt
```
Add or ensure:
```
dtparam=spi=on
```
Then:
```
$ sudo reboot
```

3. **Non-interactive**:
```
$ sudo raspi-config nonint do_spi 0
$ sudo reboot
```

---

## 5. Increase Swap Size (Optional but Recommended)

Installing some Python versions via pyenv can be memory-intensive. Increase swap size:
```
$ sudo nano /etc/dphys-swapfile
```
Change or add:
```
CONF_SWAPSIZE=2048
```
Then:
```
$ sudo systemctl stop dphys-swapfile
$ sudo systemctl start dphys-swapfile
$ free -h
```
Confirm the swap size is updated.

---

## 6. SSH Configuration (Prevent Timeouts)

On **client side (Ubuntu PC)**, edit `~/.ssh/config`:
```
Host raspberrypi.local
  HostName raspberrypi.local
  User <your_chosen_username>
  ServerAliveInterval 60
  ServerAliveCountMax 5
```
Then:
```
$ chmod 600 ~/.ssh/config
```

### 6.1. Disable Wi-Fi Power Save on Raspberry Pi

Still on the Pi side, check current power save:
```
$ iw dev wlan0 get power_save
```

If it is on, create a config to disable:
```
$ sudo nano /etc/NetworkManager/conf.d/disable-wifi-powersave.conf
```
Add:
```
[connection]
wifi.powersave = 2
```
Then restart:
```
$ sudo systemctl restart NetworkManager
$ iw dev wlan0 get power_save
```
Confirm it is now off.

---

## 7. Set Up Python Environment (pyenv + virtualenv)

1. **Install pyenv**:
```
$ cd ~
$ git clone https://github.com/pyenv/pyenv.git ~/.pyenv
$ git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
```

2. **Update `~/.bashrc`**:
```
$ sudo vim ~/.bashrc
```
Add at the end:
```
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
Then:
```
$ source ~/.bashrc
```

3. **Create a working directory**:
```
$ mkdir ~/current
$ cd ~/current
```

4. **Install Python 3.10.2 with pyenv**:
```
$ pyenv install -v 3.10.2
```
(Note: Installing Python 3.11.x may fail on Pi Zero 2W as of Mar. 15, 2025.)

5. **Create and activate a virtual environment**:
```
$ pyenv virtualenv 3.10.2 py3102env
$ pyenv local py3102env
```

---

## 8. Clone the Project and Configure

1. **Clone repository** (example name: `dexcreen`):
```
$ cd ~/current
$ git clone https://github.com/daichi-yoshikawa/dexcreen.git
$ cd dexcreen
```

2. **Copy and configure `.env`**:
```
$ cp dot.env.default .env
```
- Update the `.env` file as needed (for example, database path, etc.).

3. **Run database migrations** (if applicable):
```
$ alembic upgrade head
```
- Adjust paths if needed. For instance, if you set `SQLITE=../sqlite.db` in `.env`, the database might be generated in `~/current/` directory, so plan accordingly.

---

## 9. Git Configuration (Optional)

You might want to set up your global Git config on the Pi:
```
$ git config --global user.email "you@example.com"
$ git config --global user.name "Your Name"
```

---

## 10. Other Optional Packages or Settings

- **Install `lynx`** (text-based browser):
```
$ sudo apt install lynx
```
Can be useful for signing in to Wi-Fi networks that require a browser-based login.

- **Enable remote desktop**:
```
$ sudo raspi-config
```
Go to `Interface Options` → enable VNC (or another remote desktop option).

---

## Conclusion

You should now have a fully configured development environment on your Raspberry Pi Zero 2W, ready to run and develop this Python project. If you run into any issues, double-check the steps above, especially SSH settings, Wi-Fi power saving, and pyenv installation steps.

