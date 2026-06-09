-- Supabase PostgreSQL Setup Script for UI/UX Designer Portfolio

-- 1. Drop existing tables if they conflict (Warning: This will clear existing data)
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS hires CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS projects CASCADE;

-- 2. Create Bookings Table
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    booking_date TEXT NOT NULL,
    booking_time TEXT NOT NULL,
    date_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create Hires Table
CREATE TABLE hires (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    company TEXT,
    website TEXT,
    services TEXT,
    description TEXT NOT NULL,
    budget TEXT NOT NULL,
    timeline TEXT,
    date_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create Messages Table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    date_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Create Projects Table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    image_url TEXT,
    original_image_url TEXT,
    media_gallery TEXT,
    description TEXT,
    details TEXT,
    live_url TEXT,
    github_url TEXT,
    video_url TEXT,
    challenge TEXT,
    solution TEXT,
    metric1_value TEXT,
    metric1_label TEXT,
    metric2_value TEXT,
    metric2_label TEXT,
    is_featured_case_study BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    date_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Seed Initial Projects Data
INSERT INTO projects (id, title, category, image_url, description, details, live_url, github_url, challenge, solution, metric1_value, metric1_label, metric2_value, metric2_label, is_featured_case_study, date_created) VALUES
(1, 'Furniture E-commerce', 'UI/UX Design', 'https://uxmagic.blob.core.windows.net/public/agent-images/proj-furniture-1780871778267-2o9tcaq0whz.png', 'A premium shopping experience for modern furniture.', 'A clean and modern e-commerce mobile experience focusing on seamless checkout, interactive augmented reality preview for furniture pieces, and elegant product layout.', '#', '#', 'High cart abandonment due to complex checkout.', 'Frictionless 1-page checkout and immersive product 3D views.', '+65%', 'Conversion Rate', '-45%', 'Cart Abandonment', true, '2026-06-08 14:46:26+00'),
(2, 'SocialEat Recipe App', 'Mobile Apps', 'https://uxmagic.blob.core.windows.net/public/agent-images/proj-socialeat-1780871785724-ubnuea97lzs.png', 'Connecting food lovers through shared recipes.', 'An immersive culinary social platform. Users can create, share, and dynamically scale recipe portions, with voice-guided cooking assist features.', '#', '#', 'Low user retention and confusing navigation paths.', 'Streamlined onboarding and gamified community features.', '+40%', 'User Engagement', '+30%', 'Retention Growth', true, '2026-06-08 14:46:26+00'),
(3, 'Home Healthcare App', 'UI/UX Design', 'https://uxmagic.blob.core.windows.net/public/agent-images/proj-healthcare-1780871791868-1h75gszvihm.png', 'Seamless booking for at-home medical services.', 'Designed a dual-app ecosystem for patients and nurses. Features include calendar scheduling, medication alerts, and video consultations.', '#', '#', NULL, NULL, NULL, NULL, NULL, NULL, false, '2026-06-08 14:46:26+00'),
(4, 'Cyber Infomine', 'Branding', 'https://images.unsplash.com/photo-1600132806370-bf17e65e942f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80', 'Modern tech branding and visual system.', 'A complete brand overhaul for a cybersecurity analytics firm, including logo design, color typography guides, and marketing assets.', '#', '#', NULL, NULL, NULL, NULL, NULL, NULL, false, '2026-06-08 14:46:26+00'),
(5, 'Finance Dashboard', 'Web Design', 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80', 'Data visualization and analytics platform.', 'An intuitive desktop interface for analyzing complex cryptocurrency transactions, wallet logs, and yield statistics.', '#', '#', NULL, NULL, NULL, NULL, NULL, NULL, false, '2026-06-08 14:46:26+00'),
(6, 'Restaurant Mobile App', 'Mobile Apps', 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80', 'Table booking and digital menu experience.', 'A local dining companion application supporting contactless table ordering, custom ingredient requests, and live order status notifications.', '#', '#', NULL, NULL, NULL, NULL, NULL, NULL, false, '2026-06-08 14:46:26+00');

-- 7. Reset the SERIAL sequence to start after the seeded IDs
SELECT setval('projects_id_seq', (SELECT MAX(id) FROM projects));

-- 8. Enable Row Level Security (RLS) and define public access policies (recommended by Supabase)
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read" ON projects;
CREATE POLICY "Allow public read" ON projects FOR SELECT USING (true);
DROP POLICY IF EXISTS "Allow public insert" ON projects;
CREATE POLICY "Allow public insert" ON projects FOR INSERT WITH CHECK (true);
DROP POLICY IF EXISTS "Allow public update" ON projects;
CREATE POLICY "Allow public update" ON projects FOR UPDATE USING (true);
DROP POLICY IF EXISTS "Allow public delete" ON projects;
CREATE POLICY "Allow public delete" ON projects FOR DELETE USING (true);

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public insert" ON messages;
CREATE POLICY "Allow public insert" ON messages FOR INSERT WITH CHECK (true);
DROP POLICY IF EXISTS "Allow public read" ON messages;
CREATE POLICY "Allow public read" ON messages FOR SELECT USING (true);

ALTER TABLE hires ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public insert" ON hires;
CREATE POLICY "Allow public insert" ON hires FOR INSERT WITH CHECK (true);
DROP POLICY IF EXISTS "Allow public read" ON hires;
CREATE POLICY "Allow public read" ON hires FOR SELECT USING (true);

ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public insert" ON bookings;
CREATE POLICY "Allow public insert" ON bookings FOR INSERT WITH CHECK (true);
DROP POLICY IF EXISTS "Allow public read" ON bookings;
CREATE POLICY "Allow public read" ON bookings FOR SELECT USING (true);

-- 9. Create Settings Table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Seed initial settings
INSERT INTO settings (key, value) VALUES
('designer_name', 'Alok Sharma'),
('designer_role', 'UI/UX & Graphic Designer'),
('hero_headline', 'Designing Experiences. Creating Impact.'),
('hero_description', 'I create intuitive digital experiences, meaningful brands, and visually compelling designs that help businesses grow.'),
('hero_image_url', 'https://uxmagic.blob.core.windows.net/user/6a25a369277cb05ad3d0b425/project-assets/6a25f802dabb320111e4b8ed/work_pfpwide-1780873234357-bq8w5hzew.jpg'),
('about_heading', 'Hi, I''m Alok Sharma.'),
('about_bio_p1', 'I''m a passionate UI/UX and Graphic Designer based in Delhi, India, with over 5 years of experience crafting digital products that people love to use.'),
('about_bio_p2', 'My journey in design started with a fascination for how visual elements communicate stories. Over the years, I''ve transitioned from purely graphic design to focusing deeply on user experience, realizing that the best designs are those that solve real problems seamlessly.'),
('about_bio_p3', 'I believe in a research-driven approach where aesthetics meet functionality. Whether I''m designing a complex SaaS dashboard or a vibrant brand identity, my goal is always to create an emotional connection between the product and the user.'),
('about_quote', 'Good design is not just what it looks like, it''s how it works and how it makes people feel.'),
('about_image_url', 'https://uxmagic.blob.core.windows.net/user/6a25a369277cb05ad3d0b425/project-assets/6a25f802dabb320111e4b8ed/work_pfpwide-1780873234357-bq8w5hzew.jpg'),
('stats_experience', '1+'),
('stats_projects', '10+'),
('stats_clients', '6+'),
('cta_heading', 'Have a Project in Mind?'),
('contact_email', 'aloksharma.creative@gmail.com'),
('contact_location', 'Delhi, India'),
('social_linkedin', '#'),
('social_dribbble', '#'),
('social_instagram', '#'),
('social_twitter', '#')
ON CONFLICT (key) DO NOTHING;

-- Enable public RLS policies for settings table
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read on settings" ON settings;
CREATE POLICY "Allow public read on settings" ON settings FOR SELECT USING (true);
DROP POLICY IF EXISTS "Allow public insert on settings" ON settings;
CREATE POLICY "Allow public insert on settings" ON settings FOR INSERT WITH CHECK (true);
DROP POLICY IF EXISTS "Allow public update on settings" ON settings;
CREATE POLICY "Allow public update on settings" ON settings FOR UPDATE USING (true);
DROP POLICY IF EXISTS "Allow public delete on settings" ON settings;
CREATE POLICY "Allow public delete on settings" ON settings FOR DELETE USING (true);

-- 10. Create Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    role_or_company TEXT,
    content TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    date_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial reviews
INSERT INTO reviews (name, role_or_company, content, rating) VALUES
('Sarah Jenkins', 'CEO at Brandly', 'Alok is an exceptional designer. He transformed our complex SaaS tool into an incredibly clean and intuitive interface. Highly recommended!', 5),
('Marcus Chen', 'Product Owner at SocialEat', 'Working with Alok was a breeze. He met all timelines and brought a premium, state-of-the-art aesthetic to our mobile app.', 5),
('Emma Watson', 'Marketing Lead at DecoSpace', 'Alok has a deep understanding of typography, spacing, and user psychology. Our conversions increased by 40% after the redesign.', 5)
ON CONFLICT DO NOTHING;

-- Enable Row Level Security for reviews table
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read on reviews" ON reviews;
CREATE POLICY "Allow public read on reviews" ON reviews FOR SELECT USING (true);
DROP POLICY IF EXISTS "Allow public insert on reviews" ON reviews;
CREATE POLICY "Allow public insert on reviews" ON reviews FOR INSERT WITH CHECK (true);
DROP POLICY IF EXISTS "Allow public update on reviews" ON reviews;
CREATE POLICY "Allow public update on reviews" ON reviews FOR UPDATE USING (true);
DROP POLICY IF EXISTS "Allow public delete on reviews" ON reviews;
CREATE POLICY "Allow public delete on reviews" ON reviews FOR DELETE USING (true);

-- 11. Storage Setup for portfolio bucket
-- Create the bucket if it does not exist and ensure it is public
INSERT INTO storage.buckets (id, name, public)
VALUES ('portfolio', 'portfolio', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Enable public access policies for storage objects inside the 'portfolio' bucket
DROP POLICY IF EXISTS "Public Read Access" ON storage.objects;
CREATE POLICY "Public Read Access" ON storage.objects FOR SELECT USING (bucket_id = 'portfolio');

DROP POLICY IF EXISTS "Public Insert Access" ON storage.objects;
CREATE POLICY "Public Insert Access" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'portfolio');

DROP POLICY IF EXISTS "Public Update Access" ON storage.objects;
CREATE POLICY "Public Update Access" ON storage.objects FOR UPDATE USING (bucket_id = 'portfolio');

DROP POLICY IF EXISTS "Public Delete Access" ON storage.objects;
CREATE POLICY "Public Delete Access" ON storage.objects FOR DELETE USING (bucket_id = 'portfolio');

