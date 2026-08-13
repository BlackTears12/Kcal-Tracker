import reflex as rx

config = rx.Config(
    app_name="kcal_tracker",
    api_url="https://rpi.taila35c8c.ts.net",
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                has_background=True,
                accent_color="orange",
                gray_color="slate",
                radius="medium",
            )
        ),
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    vite_allowed_hosts=[
        "rpi.taila35c8c.ts.net",
        "localhost",
        "127.0.0.1",
    ],
)