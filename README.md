# Dexcom-to-EInk Display on Raspberry Pi Zero 2W

Fetch Dexcom G7 (or other Dexcom sensors) glucose readings from DexcomShare and display them on a [Waveshare 7.5" E-Ink Display](https://www.waveshare.com/product/displays/e-paper/7.5inch-e-paper.htm).
This setup helps Type 1 Diabetes (T1D) families quickly view glucose data at a glance.

---

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Hardware Requirements](#hardware-requirements)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Configuration](#configuration)
8. [License](#license)
9. [Disclaimer](#disclaimer)

---

## Overview

- **Platform**: Raspberry Pi Zero 2W (should also work on other Raspberry Pi models).
- **Data Source**: [DexcomShare](https://www.dexcom.com). Requires a valid Dexcom account and Dexcom Follow setup so that sensor readings are uploaded.
- **Display**: [Waveshare 7.5" E-Ink Display](https://www.waveshare.com/product/displays/e-paper/7.5inch-e-paper.htm).
- **Purpose**: Continuously show the latest glucose reading to assist T1D families in managing blood glucose levels.

---

## Features

- **Real-Time**: Fetch current Dexcom sensor values at regular intervals (e.g., every 5 minutes).
- **E-Ink Display**: Utilizes the low-power nature of e-paper for always-on or scheduled updates without burning significant battery.
- **Portable**: The small form factor of the Raspberry Pi Zero 2W makes it easy to place anywhere in your home.

---

## Hardware Requirements

1. **Raspberry Pi Zero 2W** (or another model if desired).
2. **Waveshare 7.5" E-Ink Display** (plus any required cables/adapters).
3. **MicroSD Card** (with Raspberry Pi OS installed).
4. **Power Supply** for the Pi.
5. (Optional) **Case** or mount to house the Pi and display.

> **Note**: A full Bill of Materials (BOM) will be published soon.

---

## Prerequisites

- **Dexcom Account**
  - Must have a valid Dexcom account (for Dexcom G7 or compatible sensor).
  - Make sure Dexcom Follow is active and that your sensor data is uploaded to DexcomShare.
- **Python 3.10+** recommended.
- **pyenv/virtualenv** (optional, but helps keep dependencies isolated).

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/YourGitHubUsername/YourRepoName.git
   cd YourRepoName
