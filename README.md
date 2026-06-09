# UI/UX Designer Portfolio & Admin Workspace

A premium, state-of-the-art digital portfolio and creative control workspace designed for UI/UX & Graphic Designers. Built with a responsive dark-themed grid, modern typography, glassmorphism, dynamic micro-animations, and a robust admin dashboard.

## Features

*   **Responsive Portfolio Showcase**: Modern layout with interactive category filtering (All, UI/UX Design, Mobile Apps, Branding, Web Design).
*   **Case Studies**: Dedicated detailed views with sections for design challenges, solutions, and key metrics.
*   **Creative Admin Workspace**: 
    *   **Drag-and-Drop Reordering**: Rearrange project display order on the home page via SortableJS.
    *   **Secure Authentication**: Secure PBKDF2 password hashing and verification.
    *   **Timed Password Resets**: Email-based forgot password flow valid for 15 minutes.
    *   **Media Gallery Support**: Multiple file uploads and cover page crop tooling.
*   **Client Services**: Discovery call booking, hiring inquires, and contact message notifications.
*   **Supabase Integration**: PostgreSQL cloud database and storage bucket integration.

## Tech Stack

*   **Backend**: Flask (Python)
*   **Database**: Supabase PostgreSQL
*   **Storage**: Supabase Storage
*   **Frontend**: HTML5, CSS3, TailwindCSS, SortableJS, Iconify
*   **Security**: PBKDF2 Password Hashing, Cryptographic timed tokens (`itsdangerous`)

## Setup & Run

1. Clone the repository.
2. Setup your Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env` file (copy from `.env.example`).
4. Run the development server:
   ```bash
   python app.py
   ```
