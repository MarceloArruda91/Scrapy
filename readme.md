<div align="center">
<h1 align="center">

<br>Zyte Challenge
</h1>
<h3>◦ Developed with the software and tools listed below.</h3>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style&logo=Python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/JSON-000000.svg?style&logo=JSON&logoColor=white" alt="JSON" />
</p>
<img src="https://scrapy.org/img/scrapylogo.png"/>
</div>

---

## 📒 Table of Contents
- [📒 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [⚙️ Features](#-features)
- [📂 Project Structure](#project-structure)
- [🚀 Getting Started](#-getting-started)
- [🗺 Roadmap](#-roadmap)
---


## 📍 Overview

This project is a Scrapy spider developed as part of a hiring process challenge. The spider's main task is to scrape information about artistic works from the "In Sunsh" and "Summertime" categories on the Scrapinghub Maybe Modern Art Collection website.

---

## ⚙️ Features


Category-Based Scraping: The spider is capable of scraping artworks from specific categories, by navigating through the browse tree structure of the website. It can parse artworks at the lowest level of the tree.


**Data Fields Extracted**: The spider extracts various fields for each artwork, including:
   - `url`: The URL of the work being scraped.
   - `artist`: A list of artists associated with the work.
   - `title`: The title of the work.
   - `image`: The URL of the artwork's image.
   - `height` and `width`: Physical dimensions in centimeters, if available.
   - `description`: A description of the work.
   - `categories`: The path of categories visited to reach the item via the browse tree.


PEP8-Compliant Code: The spider's code adheres to PEP8 standards, ensuring clean and readable code.

Customizable Categories: You can easily customize the categories you want to scrape by modifying the spider's configuration.

Structured Output: The scraped data is structured and saved in a JSON file named "items_artworks.json.

---


## 📂 Project Structure
```
│───items_artworks.json
│───log.txt
│───requirements.txt
│───scrapy.cfg
└───artworks
    │───items.py
    │───middlewares.py
    │───pipelines.py
    │───settings.py
    │───__init__.py
    │
    ├───enum
    │   └───options.py
    │
    ├───spiders
    │   ├───__init__.py
    │   └───artworks_spider.py 
    │
    └───util
        └───Extract.py
```

## 🚀 Getting Started

### ✔️ Prerequisites

Before you begin, ensure that you have the following prerequisites installed:
> - `Python 3.11`
> - `Scrapy 2.9.0`


### 📦 Installation


1. Change to the project directory:
```sh
cd artworks
```

2. Install the dependencies:
```sh
pip install -r requirements.txt
```

### 🎮 Running the spider

```sh
scrapy crawl artworks
```

