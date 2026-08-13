import reflex as rx

config = rx.Config(
    app_name="kcal_tracker",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    vite_allowed_hosts=[
        "rpi.taila35c8c.ts.net",
        "localhost",
        "127.0.0.1",
    ],
)