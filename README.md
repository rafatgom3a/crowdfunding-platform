# Crowdfunding Web Application

## Overview

Crowdfunding is the practice of funding a project or venture by raising small amounts of money from a large number of people, typically via the Internet. It is a form of crowdsourcing and alternative finance. In 2015, over US\$34 billion was raised worldwide by crowdfunding ([source: Wikipedia](https://en.wikipedia.org/wiki/Crowdfunding)).

This project aims to create a **Crowdfunding Web Platform** specifically targeting users in **Egypt**. The platform allows users to create fundraising campaigns, donate to projects, comment, and interact with the community.

---

## Features

### 1. Authentication System

* **User Registration:**

  * Fields: First name, Last name, Email, Password, Confirm password, Mobile phone (validated for Egyptian numbers), Profile picture.
  * Email activation with a link that expires after 24 hours.
  * Users cannot log in before activating their account.

* **Login:**

  * Login using email and password after activation.
  * **Bonus:** Login with Facebook or Google accounts.

* **Password Management:**

  * Forgot Password feature with email reset link.

* **User Profile:**

  * View and edit profile details (except email).
  * Optional fields: Birthdate, Facebook profile, Country.
  * View user's projects and donations.
  * Delete account with confirmation prompt.
  * **Bonus:** Require password input to delete account.

---

### 2. Projects

* Users can create fundraising campaigns with:

  * Title, Details, Category (chosen from admin-added categories), Multiple pictures, Total target amount (e.g., 250,000 EGP), Multiple tags, Start and end time for the campaign.
* Users can:

  * View any project and donate to its target.
  * Add comments on projects.
  * **Bonus:** Comments can have replies.
  * Report inappropriate projects or comments.
  * Rate projects.
* Project creator can cancel campaigns if donations are less than 25% of the target.
* Project page displays:

  * Average rating.
  * Image slider for project pictures.
  * Four similar projects based on tags.

---

### 3. Homepage

* Slider showing the top 5 highest-rated running projects.
* List of latest 5 projects.
* List of latest 5 featured projects (selected by admins).
* Categories list allowing users to filter projects.
* Search bar to search projects by title or tag.

---

## Technology Stack

* **Backend & Frontend:** Django (Python web framework) — handles both server logic and template rendering.
* Database: (e.g., SQLite/PostgreSQL/MySQL depending on deployment)
* Email system for activation and password reset.
* Optional OAuth integrations for social login (Facebook, Google).

---

## Installation and Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/rafatgom3a/crowdfunding-platform.git
   cd crowdfunding-platform
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   Create a `.env` file or set variables for:

   * `SECRET_KEY`
   * Email SMTP credentials
   * OAuth client IDs/secrets (if using social login)

5. **Apply migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create superuser (admin):**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

8. **Access the app:**
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Usage

* Register a new account and activate it via the email link.
* Log in to create projects or donate.
* Admins can add categories and feature projects.
* Users can browse projects by category, search, comment, rate, and donate.
* Profile page allows users to manage their information and projects.

---

## References / Inspiration

* [GoFundMe](https://www.gofundme.com)
* [Kickstarter](https://www.kickstarter.com)
* [Crowdfunding.com](https://www.crowdfunding.com)

---

## Future Enhancements (Bonus Ideas)

* Social login with Facebook and Google.
* Comments replies threading.
* User verification via phone SMS.
* Payment gateway integration for real-time donations.
* Mobile app version or PWA support.
* Analytics dashboard for admins.
